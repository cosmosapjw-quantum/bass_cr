#!/usr/bin/env python3
"""Audit the preserved C20 raw ledger without rerunning its physics."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
raw = json.loads((root / "raw" / "sweep_pass.json").read_text())
binding = (13.598434599702, 24.587389011, 54.41776)

assert raw["schema"] == "C20_NCP64_SOURCE_CONDITIONAL_COHORT_SWEEP_V1"
assert len(raw["cases"]) == 20
assert raw["pass_count"] == 20
for case in raw["cases"]:
    assert case["status"] == "PASS_SCOPED"
    value = case["result"]
    absorb = value["species_events_per_h"]
    heat = value["species_heat_ev_h"]
    assert min(absorb) >= 0.0 and min(heat) >= 0.0
    assert value["photon_redshift_work_ev_h"] >= 0.0
    number = value["input_n"] + value["source_n"] - value["end_n"] - sum(absorb)
    energy = (value["input_u_ev_h"] + value["source_u_ev_h"] - value["end_u_ev_h"]
              - sum(heat) - sum(a * b for a, b in zip(absorb, binding))
              - value["photon_redshift_work_ev_h"])
    # Rust's ledger uses Kahan accumulation while this independent audit uses
    # Python's ordinary binary64 summation; these are representation-level,
    # not physics-gate, comparisons.  The measured cross-order maxima are
    # 6.94e-18 photons/H and 1.11e-16 eV/H, respectively.
    assert abs(number - value["number_residual"]) <= 8e-18
    assert abs(energy - value["energy_residual_ev_h"]) <= 1.2e-16
    assert value["time_gl4_s"] > 0.0 and value["time_owner_simpson_s"] > 0.0
