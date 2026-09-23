import json

import pytest

from scripts import r3m23_cross_window as cross


def test_two_window_worst_required_work_fits_frozen_fft_cap():
    assert cross.REQUIRED_TOTAL_MAX == 3591
    assert cross.REQUIRED_TOTAL_MAX <= cross.MAX_FFT
    assert cross.REQUIRED_TOTAL_MAX + 2 * cross.OPTIONAL_SUBSTEP_MAX > cross.MAX_FFT


def test_budget_enforces_terminal_wall_and_reserves_next_window(monkeypatch):
    clock = [0.0]
    monkeypatch.setattr(cross.time, "perf_counter", lambda: clock[0])
    budget = cross.Budget(started=0.0, preflight_count=3)
    assert budget.reserve(2 * cross.REQUIRED_PER_WINDOW_MAX)
    budget.begin_window()
    clock[0] = 1799.0
    budget.tick()
    assert budget.count == 4
    clock[0] = 1800.01
    with pytest.raises(TimeoutError, match="short-window wall cap"):
        budget.end_window()
    assert budget.count == 4


def test_strang_scale_gate_fails_closed_without_full_substep_repeat():
    distances = dict(strang_4_vs_cf4_16=2e-7,
                     strang_8_vs_cf4_16=1e-8,
                     strang_16_vs_cf4_16=1e-9,
                     cf4_8_to_16=5e-12,
                     inner_16_repeat=4e-13,
                     substep_8_repeat=3e-12)
    scale, threshold, passed = cross.assess_window(distances, True)
    assert scale == 1e-9 and threshold == pytest.approx(1e-11) and passed
    assert not cross.assess_window(distances, False)[2]
    distances["inner_16_repeat"] = threshold
    assert not cross.assess_window(distances, True)[2]


def test_execution_contract_hashes_match_frozen_inputs_and_sources():
    contract = json.loads(cross.CONTRACT.read_text())
    assert contract["input_guard_sha256"] == cross._sha(cross.OUT / "INPUT_GUARD.json")
    assert contract["selection_sha256"] == cross._sha(cross.SELECTION)
    assert contract["strict_cpu_oracle_sha256"] == cross._sha(cross.STRICT_CPU)
    for name, digest in contract["source_sha256"].items():
        assert digest == cross._sha(cross.ROOT / name)
