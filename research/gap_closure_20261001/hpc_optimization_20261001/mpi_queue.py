"""Whole-task MPI scheduling with one authoritative raw-attempt budget.

Only the synthetic CLI is executable here. A future physical adapter must carry
fresh exact source/native/input/admission pins. This module grants no authority.
All ranks call run_queue; only rank zero supplies tasks and receives results.
worker(task, reserve) calls reserve(level_index) BEFORE each raw attempt, in
prefix order of task['levels']. It may stop at any passing prefix. The worker is
responsible for the actual scientific qualification and unchanged tolerances.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import time


_COMMAND, _EVENT, _REPLY = 27101, 27102, 27103


class QueueExecutionError(RuntimeError):
    def __init__(self, failure):
        self.failure = failure
        super().__init__(f"{failure['type']}: {failure['message']}")


class ReservationDenied(RuntimeError):
    pass


def _json(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def _write_new(path, value):
    path = Path(path)
    with path.open('x') as stream:
        stream.write(_json(value) + '\n')
        stream.flush()
        os.fsync(stream.fileno())
    descriptor = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


class _Authority:
    """Used on root only; it never delegates or multiplies the global cap."""
    def __init__(self, tasks, maximum, output_dir):
        if type(maximum) is not int or maximum < 0:
            raise ValueError('max_attempts must be a nonnegative integer')
        if not isinstance(tasks, list):
            raise ValueError('rank zero must supply a list of tasks')
        for task in tasks:
            if not isinstance(task, dict) or not isinstance(task.get('levels'), list) or not task['levels']:
                raise ValueError('every task must declare a nonempty ordered levels list')
        # JSON copying fixes a portable plan identity and isolates caller data.
        payload = _json(tasks)
        self.tasks = json.loads(payload)
        self.maximum = maximum
        self.used = 0
        self.next_level = [0] * len(tasks)
        self.failure = None
        self.out = None if output_dir is None else Path(output_dir).resolve()
        self.ordered_results = []
        if self.out is not None:
            self.out.mkdir(exist_ok=False)
            descriptor = os.open(self.out.parent, os.O_RDONLY)
            try:
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
            (self.out / 'tasks').mkdir()
            (self.out / 'results').mkdir()
            _write_new(self.out / 'PLAN.json', {
                'schema': 'BASS_R4S_MPI_PLAN_V1',
                'task_plan_sha256': hashlib.sha256(payload.encode()).hexdigest(),
                'tasks': self.tasks, 'max_attempts': maximum,
                'physical_admission': False,
            })
            with (self.out / 'RESERVATIONS.jsonl').open('x') as stream:
                stream.flush(); os.fsync(stream.fileno())
            descriptor = os.open(self.out, os.O_RDONLY)
            try:
                os.fsync(descriptor)
            finally:
                os.close(descriptor)

    def fail(self, kind, message, index=None, rank=0):
        if self.failure is None:
            self.failure = {'type': kind, 'message': str(message),
                            'task_index': index, 'rank': rank,
                            'raw_attempts_reserved': self.used}
            if self.out is not None:
                _write_new(self.out / 'FIRST_FAILURE.json', self.failure)
        return self.failure

    def reserve(self, index, level, rank):
        if self.failure is not None:
            return {'ok': False, 'failure': self.failure}
        if (type(level) is not int or level != self.next_level[index]
                or level >= len(self.tasks[index]['levels'])):
            failure = self.fail('InvalidLevelSequence',
                                'reservation must be the next declared level index', index, rank)
            return {'ok': False, 'failure': failure}
        if self.used >= self.maximum:
            failure = self.fail('BudgetExceeded', 'global raw-attempt budget exhausted', index, rank)
            return {'ok': False, 'failure': failure}
        number = self.used + 1
        row = {'global_attempt': number, 'task_index': index,
               'level_index': level, 'level': self.tasks[index]['levels'][level],
               'rank': rank}
        # The successful reply is sent only AFTER the reservation is durable.
        # A crash between fsync and reply consumes this attempt; never retry it.
        if self.out is not None:
            with (self.out / 'RESERVATIONS.jsonl').open('a') as stream:
                stream.write(_json(row) + '\n')
                stream.flush(); os.fsync(stream.fileno())
        self.used = number
        self.next_level[index] += 1
        return {'ok': True, 'global_attempt': number}

    def envelope(self, index):
        task_dir = None
        if self.out is not None:
            path = self.out / 'tasks' / f'{index:08d}'
            path.mkdir(exist_ok=False)
            task_dir = str(path)
        return {'kind': 'task', 'index': index,
                'task': copy.deepcopy(self.tasks[index]), 'task_dir': task_dir}

    def publish(self, index, result):
        if index != len(self.ordered_results):
            raise ValueError('canonical publication order mismatch')
        # Results must be finite JSON data; task-local bulk payloads may be
        # referenced by path/hash in this record instead of sent through MPI.
        value = json.loads(_json(result))
        if self.out is not None:
            _write_new(self.out / 'results' / f'{index:08d}.json', value)
        self.ordered_results.append(value)

    def finish(self):
        if self.out is not None:
            _write_new(self.out / 'QUEUE_RECEIPT.json', {
                'schema': 'BASS_R4S_MPI_QUEUE_RECEIPT_V1',
                'status': 'FAILED' if self.failure else 'COMPLETE',
                'raw_attempts_reserved': self.used,
                'max_attempts': self.maximum,
                'canonical_prefix_count': len(self.ordered_results),
                'task_count': len(self.tasks),
                'failure': self.failure,
                'floating_point_MPI_reductions': 0,
            })


class _Reserve:
    def __init__(self, invoke, task_dir):
        self._invoke = invoke
        self.task_dir = task_dir

    def __call__(self, level_index):
        reply = self._invoke(level_index)
        if not reply['ok']:
            failure = reply['failure']
            raise ReservationDenied(f"{failure['type']}: {failure['message']}")
        return reply['global_attempt']


def _sequential(authority, worker, timeout_seconds):
    deadline = time.monotonic() + timeout_seconds
    for index in range(len(authority.tasks)):
        if authority.failure:
            break
        try:
            envelope = authority.envelope(index)
            def invoke(level):
                if time.monotonic() >= deadline:
                    authority.fail('QueueTimeout', 'sequential cooperative deadline reached', index)
                return authority.reserve(index, level, 0)
            reserve = _Reserve(invoke, envelope['task_dir'])
            value = worker(envelope['task'], reserve)
            if time.monotonic() >= deadline:
                authority.fail('QueueTimeout', 'sequential cooperative deadline reached', index)
            if authority.next_level[index] == 0:
                authority.fail('UnreservedTask', 'worker returned without reserving an attempt', index)
            if not authority.failure:
                authority.publish(index, value)
        except Exception as exc:
            authority.fail(type(exc).__name__, str(exc), index)
    authority.finish()
    if authority.failure:
        raise QueueExecutionError(authority.failure)
    return authority.ordered_results


def _workers(comm, worker):
    while True:
        envelope = comm.recv(source=0, tag=_COMMAND)
        if envelope['kind'] == 'stop':
            return
        index = envelope['index']

        def request(level):
            comm.send({'kind': 'reserve', 'index': index, 'level': level}, dest=0, tag=_EVENT)
            return comm.recv(source=0, tag=_REPLY)

        try:
            result = worker(envelope['task'], _Reserve(request, envelope['task_dir']))
            # Serialize locally so a bad result is a cooperative task failure,
            # rather than an MPI pickling error before root can drain workers.
            result = json.loads(_json(result))
            comm.send({'kind': 'done', 'index': index, 'result': result}, dest=0, tag=_EVENT)
        except Exception as exc:
            comm.send({'kind': 'failed', 'index': index,
                       'type': type(exc).__name__, 'message': str(exc)}, dest=0, tag=_EVENT)


def _root(comm, authority, timeout_seconds, MPI):
    count = len(authority.tasks)
    slots = comm.Get_size() - 1
    idle = list(range(1, comm.Get_size()))
    active = {}
    pending = {}
    next_task = 0
    started = time.monotonic()

    def stop_idle():
        while idle:
            comm.send({'kind': 'stop'}, dest=idle.pop(), tag=_COMMAND)

    while True:
        # Include completed-but-unpublished tasks in the window. A slow early
        # task cannot cause an unbounded result buffer or speculative dispatch.
        while (not authority.failure and idle and next_task < count
               and len(active) + len(pending) < slots):
            rank = idle.pop(0)
            comm.send(authority.envelope(next_task), dest=rank, tag=_COMMAND)
            active[rank] = next_task
            next_task += 1
        if authority.failure:
            stop_idle()
            if not active:
                break
        elif len(authority.ordered_results) == count:
            stop_idle()
            break
        if time.monotonic() - started >= timeout_seconds:
            authority.fail('QueueTimeout', 'worker did not cooperatively finish before timeout')
            authority.finish()
            comm.Abort(70)
            raise QueueExecutionError(authority.failure)  # for MPI substitutes
        status = MPI.Status()
        if not comm.Iprobe(source=MPI.ANY_SOURCE, tag=_EVENT, status=status):
            time.sleep(0.001)
            continue
        rank = status.Get_source()
        event = comm.recv(source=rank, tag=_EVENT)
        index = active.get(rank)
        if index is None or event.get('index') != index:
            authority.fail('ProtocolError', 'event does not belong to the active rank/task', index, rank)
            authority.finish()
            comm.Abort(71)
            raise QueueExecutionError(authority.failure)
        kind = event.get('kind')
        if kind == 'reserve':
            reply = authority.reserve(index, event.get('level'), rank)
            comm.send(reply, dest=rank, tag=_REPLY)
            continue
        if kind not in ('done', 'failed'):
            authority.fail('ProtocolError', 'unknown MPI worker event', index, rank)
            authority.finish()
            comm.Abort(71)
            raise QueueExecutionError(authority.failure)
        del active[rank]
        idle.append(rank)
        if kind == 'failed':
            authority.fail(event['type'], event['message'], index, rank)
        elif not authority.failure:
            if authority.next_level[index] == 0:
                authority.fail('UnreservedTask', 'worker returned without reserving an attempt', index, rank)
            else:
                pending[index] = event['result']
                while len(authority.ordered_results) in pending:
                    head = len(authority.ordered_results)
                    try:
                        authority.publish(head, pending.pop(head))
                    except Exception as exc:
                        authority.fail(type(exc).__name__, str(exc), head, 0)
                        break
    authority.finish()


def run_queue(comm, tasks, worker, *, max_attempts, output_dir=None, timeout_seconds=300.0):
    """Execute whole tasks, keeping ordered results and a single raw-attempt cap.

    The communicator must be dedicated to this queue. It is not shared with
    caller traffic. MPI size one has the same budget/order semantics without MPI imports.
    With size > 1 rank zero coordinates, size-1 ranks compute. output_dir, when
    supplied, must not exist and its parent must exist. It is root-owned; each reserve.task_dir belongs to
    exactly one task. Persistence is create-only and there is no automatic retry.

    Cooperative errors drain active tasks while refusing all future reservations;
    every rank raises QueueExecutionError. Hard timeout/protocol errors abort
    nonzero, avoiding an indefinitely blocked MPI shutdown. Physical admission,
    native source checks, host resource limits, and qualification are external.
    Size one checks its deadline cooperatively at reservations and task return;
    a stuck size-one callback requires an external process supervisor.
    """
    rank = comm.Get_rank()
    authority = None
    admission = None
    if rank == 0:
        try:
            if (isinstance(timeout_seconds, bool) or not isinstance(timeout_seconds, (int, float))
                    or not 0 < timeout_seconds < float('inf')):
                raise ValueError('positive finite timeout_seconds required')
            authority = _Authority(tasks, max_attempts, output_dir)
            admission = {'ok': True}
        except Exception as exc:
            admission = {'ok': False, 'failure': {'type': type(exc).__name__, 'message': str(exc)}}
    admission = comm.bcast(admission, root=0)
    if not admission['ok']:
        raise QueueExecutionError(admission['failure'])
    if comm.Get_size() == 1:
        return _sequential(authority, worker, timeout_seconds)
    from mpi4py import MPI
    try:
        if rank == 0:
            _root(comm, authority, timeout_seconds, MPI)
        else:
            _workers(comm, worker)
        failure = comm.bcast(authority.failure if rank == 0 else None, root=0)
    except BaseException as exc:
        # An unexpected MPI/I/O/programming failure cannot safely enter another
        # collective. Persist root's first failure if possible, then terminate.
        if rank == 0 and authority is not None:
            try:
                authority.fail(type(exc).__name__, str(exc))
            except Exception:
                pass
        comm.Abort(72)
        raise
    if failure:
        raise QueueExecutionError(failure)
    return authority.ordered_results if rank == 0 else None


def _self_test(case, output_dir):
    from mpi4py import MPI
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    tasks = [{'levels': [4, 8, 16], 'value': i} for i in range(17)] if rank == 0 else None
    maximum = 7 if case == 'budget' else 34

    def synthetic(task, reserve):
        # Integer-only synthetic work. No B0 inputs, native kernels or dynamics.
        if case == 'level' and task['value'] == 0:
            reserve(1)
        first = reserve(0)
        if case == 'timeout' and task['value'] == 0:
            time.sleep(2)
        if case == 'worker_failure' and task['value'] == 0:
            raise ArithmeticError('intentional synthetic worker failure')
        time.sleep(0.06 if task['value'] == 0 else 0.001)
        second = reserve(1)
        value = task['value']
        if reserve.task_dir:
            _write_new(Path(reserve.task_dir) / 'SYNTHETIC_PAYLOAD.json', {'value': value})
        task['value'] = -99
        return {'value': value, 'square': value * value,
                'reservations': [first, second]}

    failed = None
    try:
        result = run_queue(comm, tasks, synthetic, max_attempts=maximum,
                           output_dir=output_dir, timeout_seconds=0.2 if case == 'timeout' else 10)
    except QueueExecutionError as exc:
        failed = exc.failure
        result = None
    if rank == 0:
        if case == 'ordered':
            assert failed is None and [r['value'] for r in result] == list(range(17))
            assert [r['square'] for r in result] == [i*i for i in range(17)]
            assert sorted(n for r in result for n in r['reservations']) == list(range(1, 35))
            assert [t['value'] for t in tasks] == list(range(17))
        else:
            expected = {'budget': 'BudgetExceeded', 'level': 'InvalidLevelSequence',
                        'worker_failure': 'ArithmeticError'}[case]
            assert failed and failed['type'] == expected, failed
        if output_dir:
            out = Path(output_dir)
            receipt = json.loads((out / 'QUEUE_RECEIPT.json').read_text())
            assert receipt['raw_attempts_reserved'] <= maximum
            rows = [json.loads(line) for line in (out / 'RESERVATIONS.jsonl').read_text().splitlines()]
            assert [r['global_attempt'] for r in rows] == list(range(1, len(rows)+1))
            assert len(rows) == receipt['raw_attempts_reserved']
            if case == 'budget': assert len(rows) == 7
            if failed:
                assert len(rows) == failed['raw_attempts_reserved']
            for index in range(17):
                levels = [r['level_index'] for r in rows if r['task_index'] == index]
                assert levels == list(range(len(levels)))
        print(_json({'status': 'PASS', 'case': case, 'ranks': comm.Get_size(),
                     'physical_queries': 0, 'max_attempts': maximum}), flush=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument('--self-test', action='store_true', required=True)
    parser.add_argument('--case', choices=('ordered', 'budget', 'level', 'worker_failure', 'timeout'), default='ordered')
    parser.add_argument('--output-dir')
    args = parser.parse_args(argv)
    _self_test(args.case, args.output_dir)


if __name__ == '__main__':
    main()
