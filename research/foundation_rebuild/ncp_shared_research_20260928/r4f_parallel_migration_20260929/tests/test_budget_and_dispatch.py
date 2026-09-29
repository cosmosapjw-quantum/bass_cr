from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing
from pathlib import Path
import sys
import threading
import time

import pytest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from parallel_bridge import BudgetExceeded, GlobalBudget, MigrationCancelled, dispatch_bounded


def _reserve_process(root):
    budget=GlobalBudget(Path(root))
    count=0
    for _ in range(5):
        try:
            budget.reserve('q',32,1)
            count+=1
        except BudgetExceeded:
            pass
    return count


def test_shared_reservation_never_overshoots(tmp_path):
    budget = GlobalBudget.create(tmp_path/'budget', parent_attempts=4, maximum=11, deadline_unix=time.time()+60)
    succeeded = []
    def reserve(i):
        try:
            return budget.reserve('q', 32, 1)
        except BudgetExceeded:
            return None
    with ThreadPoolExecutor(max_workers=8) as pool:
        succeeded = list(pool.map(reserve, range(32)))
    assert sum(x is not None for x in succeeded) == 7
    assert budget.used() == 11
    assert budget.reservations() == 7


def test_spawned_processes_share_one_durable_cap(tmp_path):
    budget=GlobalBudget.create(tmp_path/'budget',parent_attempts=4,maximum=11,
                               deadline_unix=time.time()+60)
    with ProcessPoolExecutor(max_workers=4,mp_context=multiprocessing.get_context('spawn')) as pool:
        counts=list(pool.map(_reserve_process,[str(budget.root)]*4))
    assert sum(counts)==7
    assert budget.used()==11


def test_dispatch_bounds_inflight_and_keeps_plan_order(tmp_path):
    running = 0
    peak = 0
    lock = threading.Lock()
    def work(item):
        nonlocal running, peak
        with lock:
            running += 1
            peak = max(peak, running)
        time.sleep((7-item)*0.002)
        with lock:
            running -= 1
        return item * 2
    published = {}
    with ThreadPoolExecutor(max_workers=3) as pool:
        dispatch_bounded(list(range(7)), pool, work, lambda item, result: published.__setitem__(item, result),
                         max_inflight=3, deadline_unix=time.time()+60)
    assert peak <= 3
    assert [published[i] for i in range(7)] == [i*2 for i in range(7)]


def test_failure_stops_new_dispatch(tmp_path):
    started = []
    def work(item):
        started.append(item)
        if item == 1:
            raise RuntimeError('synthetic worker failure')
        time.sleep(0.01)
        return item
    with ThreadPoolExecutor(max_workers=2) as pool:
        with pytest.raises(RuntimeError, match='synthetic worker failure'):
            dispatch_bounded(list(range(10)), pool, work, lambda *_: None,
                             max_inflight=2, deadline_unix=time.time()+60)
    assert max(started) <= 2


def test_deadline_and_cancel_refuse_new_reservation(tmp_path):
    budget = GlobalBudget.create(tmp_path/'expired', parent_attempts=0, maximum=2, deadline_unix=time.time()-1)
    with pytest.raises(MigrationCancelled):
        budget.reserve('q', 32, 1)
    budget = GlobalBudget.create(tmp_path/'other', parent_attempts=0, maximum=2, deadline_unix=time.time()+60)
    budget.cancel('synthetic')
    with pytest.raises(MigrationCancelled):
        budget.reserve('q', 32, 1)
