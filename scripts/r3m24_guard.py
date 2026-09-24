"""CPU-only, same-descriptor intake and create-only evidence publication.

Assumes a local POSIX filesystem and no concurrent authorized writer. Detects
ordinary replacement/in-place writes by inode/size/mtime/ctime before and after
consumption; not a defence against a hostile filesystem or privileged attacker.
"""
from __future__ import annotations

from contextlib import ExitStack, contextmanager
from dataclasses import dataclass, field
import hashlib
import json
import math
import os
from pathlib import Path
import stat
from typing import Any, Iterator

import numpy as np


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode('utf-8')


def object_sha(value: Any) -> str:
    return hashlib.sha256(json_bytes(value)).hexdigest()


def safe_path(path: Path | str) -> Path:
    path = Path(os.path.abspath(path))
    for part in reversed((path, *path.parents)):
        if part.is_symlink():
            raise ValueError(f'symlink forbidden: {part}')
    return path


def signature(s: os.stat_result) -> tuple:
    return (s.st_dev, s.st_ino, s.st_mode, s.st_size, s.st_mtime_ns, s.st_ctime_ns)


def open_regular(path: Path | str):
    path = safe_path(path)
    fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0))
    stream = os.fdopen(fd, 'rb')
    if not stat.S_ISREG(os.fstat(fd).st_mode):
        stream.close()
        raise ValueError(f'not a regular file: {path}')
    return stream


def stream_sha(stream) -> str:
    stream.seek(0)
    h = hashlib.sha256()
    for block in iter(lambda: stream.read(4 * 1024**2), b''):
        h.update(block)
    stream.seek(0)
    return h.hexdigest()


def file_sha(path: Path | str) -> str:
    with open_regular(path) as stream:
        before = signature(os.fstat(stream.fileno()))
        value = stream_sha(stream)
        if signature(os.fstat(stream.fileno())) != before:
            raise ValueError(f'file changed while hashing: {path}')
        return value


def fsync_dir(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def publish_json(path: Path | str, value: Any) -> None:
    """fsync complete temporary bytes, link without replacement, fsync directory.

    An interrupted .pending or existing destination is never removed/overwritten.
    A manifest is published last by the caller to commit a multi-file bundle.
    """
    path = safe_path(path)
    payload = json_bytes(value)  # Reject NaN before creating any output.
    if os.path.lexists(path):
        raise FileExistsError(path)
    pending = path.with_name(path.name + '.pending')
    with pending.open('xb') as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    os.link(pending, path, follow_symlinks=False)
    fsync_dir(path.parent)
    pending.unlink()
    fsync_dir(path.parent)


def read_json(path: Path | str, expected_sha: str | None = None) -> dict:
    with open_regular(path) as stream:
        if os.fstat(stream.fileno()).st_size > 32 * 1024**2:
            raise ValueError('small JSON evidence exceeds 32 MiB limit')
        raw = stream.read()
    if expected_sha is not None and hashlib.sha256(raw).hexdigest() != expected_sha:
        raise ValueError(f'JSON identity mismatch: {path}')
    value = json.loads(raw, parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
    if not isinstance(value, dict):
        raise ValueError('JSON object required')
    return value


@dataclass
class PinnedGeneration:
    array: np.memmap = field(repr=False)
    receipt: dict
    _identities: list = field(repr=False)

    def assert_current(self) -> None:
        """Use before upload and after its synchronization, before propagation."""
        for path, stream, initial in self._identities:
            try:
                safe_path(path)
                actual = signature(path.stat())
                opened = signature(os.fstat(stream.fileno()))
            except OSError as exc:
                raise ValueError(f'input disappeared: {path}') from exc
            if actual != initial or opened != initial:
                raise ValueError(f'input changed at consumption boundary: {path}')


@contextmanager
def bind_generation(spec: dict) -> Iterator[PinnedGeneration]:
    """Verify one trusted generation manifest and map the SAME opened state fd.

    The selected manifest hash is the authority, not a mutable old guard's PASS.
    Each large state is hashed once. Subsequent boundary checks use the retained
    object identity, so no repeated 1-GB hash/download is needed in one attempt.
    """
    root = safe_path(spec['generation_directory'])
    if type(spec['done']) is not int or root.name != f"g{spec['done']:06d}":
        raise ValueError('generation/done mismatch')
    with ExitStack() as stack:
        identities = []

        def acquire(name, expected_sha, size=None):
            if Path(name).name != name or name in ('', '.', '..'):
                raise ValueError('manifest must contain direct file names')
            path = root / name
            stream = stack.enter_context(open_regular(path))
            sig = signature(os.fstat(stream.fileno()))
            if size is not None and sig[3] != size:
                raise ValueError(f'file size mismatch: {name}')
            if stream_sha(stream) != expected_sha:
                raise ValueError(f'file hash mismatch: {name}')
            if signature(os.fstat(stream.fileno())) != sig or signature(path.stat()) != sig:
                raise ValueError(f'file changed during intake: {name}')
            identities.append((path, stream, sig))
            return stream

        stream = acquire('r3m17_generation_manifest.json', spec['manifest_sha256'])
        manifest = json.load(stream)
        if (manifest.get('schema') != 'BASS_CR_R3M17_CHECKPOINT_GENERATION_V1'
                or manifest.get('status') != 'PUBLISHED_VERIFIED_LOCAL'):
            raise ValueError('unpublished generation')
        for key in ('done', 'nstep', 'config_hash', 'source_digest'):
            if manifest.get(key) != spec[key]:
                raise ValueError(f'manifest mismatch: {key}')
        required = {'state.npy', 'state.json', 'r3m11_checkpoint_seal.json',
                    'r3m14_initial_binding.json', 'r3m14_witness_run_receipt.json'}
        files = manifest.get('files', {})
        if not required <= files.keys():
            raise ValueError('generation lacks seal/witness/receipt')
        streams = {name: acquire(name, record['sha256'], record['size'])
                   for name, record in files.items()}
        state_record = files['state.npy']
        if (state_record['sha256'] != spec['expected_state_npy_sha256'] or
                state_record['size'] != spec['expected_state_npy_bytes']):
            raise ValueError('selected state identity differs from manifest')
        metadata = json.load(streams['state.json'])
        for key in ('config_hash', 'done', 'nstep', 'backend'):
            if metadata.get(key) != spec[key]:
                raise ValueError(f'state metadata mismatch: {key}')
        if type(metadata['done']) is not int or type(metadata['nstep']) is not int:
            raise ValueError('integer done/nstep required')
        norm = metadata.get('norm')
        if isinstance(norm, bool) or not isinstance(norm, (int, float)) or not math.isfinite(norm) or norm <= 0:
            raise ValueError('positive finite checkpoint norm required')
        seal = json.load(streams['r3m11_checkpoint_seal.json'])
        if (seal.get('schema') != 'R3M11_CHECKPOINT_SEAL_V1' or
                seal.get('source_digest') != spec['source_digest'] or
                seal.get('files') != {k: files[k]['sha256'] for k in ('state.npy','state.json')}):
            raise ValueError('seal metadata mismatch')
        dt, t0, start, horizon = [float(spec[k]) for k in
                                ('actual_dt_au','initial_time_au','actual_start_time_au','horizon_au')]
        if (not all(math.isfinite(x) for x in (dt,t0,start,horizon)) or dt <= 0 or
                horizon <= 0 or horizon > 4*dt*(1+1e-14) or
                not 0 <= spec['done'] <= spec['nstep']-4 or
                abs(start-(t0+spec['done']*dt)) > 64*np.finfo(float).eps*max(1.,abs(start),abs(t0))):
            raise ValueError('checkpoint time/horizon mismatch')
        state = streams['state.npy']
        version = np.lib.format.read_magic(state)
        if version == (1,0):
            shape, fortran, dtype = np.lib.format.read_array_header_1_0(state)
        elif version == (2,0):
            shape, fortran, dtype = np.lib.format.read_array_header_2_0(state)
        else:
            raise ValueError('only NPY 1.0/2.0 checkpoint headers supported')
        offset = state.tell()
        if (list(shape) != spec['shape'] or dtype != np.dtype('complex128') or
                dtype.str != spec['dtype'] or fortran or
                offset + math.prod(shape)*dtype.itemsize != state_record['size']):
            raise ValueError('checkpoint shape/dtype/order/extent mismatch')
        array = np.memmap(state, dtype=dtype, mode='r', offset=offset, shape=shape, order='C')
        # Never manually close array._mmap: ndarray views and exception frames
        # may still reference it. NumPy releases the mapping when the final
        # array/view is collected; the verification descriptors still close
        # with this context. Manual unmapping creates dangling readable views.
        bound = PinnedGeneration(array, dict(label=spec['label'], done=spec['done'],
            state_sha256=state_record['sha256'], manifest_sha256=spec['manifest_sha256'],
            state_bytes=state_record['size'], shape=list(shape), dtype=dtype.str,
            intake='SAME_FD_HASH_AND_READONLY_MMAP', metadata=metadata,
            source_path=str(root)), identities)
        bound.assert_current()
        yield bound
