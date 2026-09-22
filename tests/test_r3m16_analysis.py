"""Decision-table regressions for the registered R3M16 2x2 analysis."""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("r3m16_analysis", ROOT / "scripts/r3m16_analyze.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def test_decomposition_uses_preregistered_denominators():
    out = MOD.decompose(1.0, 1.2, 0.9, 1.15)
    assert out["Delta_h_dt05"]["value"] == pytest.approx(0.2)
    assert out["Delta_h_dt05"]["relative"] == pytest.approx(0.2 / 1.2)
    assert out["Delta_h_dt025"]["value"] == pytest.approx(0.25)
    assert out["Delta_h_dt025"]["relative"] == pytest.approx(0.25 / 1.15)
    assert out["Delta_t_h025"]["value"] == pytest.approx(-0.1)
    assert out["Delta_t_h020"]["value"] == pytest.approx(-0.05)
    assert out["I_ht"]["value"] == pytest.approx(0.05)


@pytest.mark.parametrize(
    "time_rel,gap_rel,clean,expected",
    [
        (0.0008, 0.004, False, "POINT_COULOMB_FFT_SPATIAL_REPRESENTATION_BLOCKER"),
        (0.002, 0.002, False, "CURRENT_REPRESENTATION_RETAINED__COUPLED_H_DT_PROTOCOL_REQUIRED"),
        (0.002, 0.006, False, "COUPLED_H_DT_PROMISING_BUT_BUDGET_OPEN"),
        (0.002, 0.012, True, "POINT_COULOMB_FFT_REPRESENTATION_CHANGE_REQUIRED"),
        (0.002, 0.012, False, "TIME_REFINEMENT_STILL_OPEN"),
    ],
)
def test_exact_registered_decision_branches(time_rel, gap_rel, clean, expected):
    assert MOD.decide(time_rel, gap_rel, clean) == expected


def test_zero_denominator_does_not_auto_pass():
    with pytest.raises(ValueError, match="denominator"):
        MOD.decompose(0.0, 0.0, 0.0, 0.0)
