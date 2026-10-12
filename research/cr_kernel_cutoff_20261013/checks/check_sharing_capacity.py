"""KA.29 only: actual mesh bound and three sharing extents with one denominator."""
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
import platform
from pathlib import Path
import sys
import time

import numpy as np
import scipy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from kernel_event_adapter import BoundKernel


def stamp():
    return datetime.now(timezone.utc).isoformat()


def file_record(path):
    raw = path.read_bytes()
    return {"path": str(path.relative_to(ROOT)), "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest()}


def main():
    started = stamp()
    timer = time.monotonic()
    k = BoundKernel()
    path = ROOT/"inputs/prior/event_capacity_step.py"
    spec = importlib.util.spec_from_file_location("ka29_accepted_capacity", path)
    accepted = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = accepted
    spec.loader.exec_module(accepted)
    inventory = json.loads((ROOT/"inputs/kernel_sources/research/cr_phys02b_20261010/"
                            "inputs/CCC_USED_CHANNELS.json").read_text())
    max_gap = float(np.max(np.diff(np.r_[float(k.cut), k.E])))
    min_binding = min(ion.B_eV for ion in k.ions.values())
    min_cost = min(c["adopted_effective_cost_eV"] for c in inventory["channels"])
    assert 0 < max_gap < min(min_binding, min_cost)
    j = int(np.searchsorted(k.E, 30.))
    slow, _, _ = k.sharing(j, "HI")
    q_ghost = int(np.argmin(np.abs(slow-.5*(float(k.cut)+k.E[0]))))
    selected = sorted({0, q_ghost, len(slow)-1})
    assert len(selected) == 3
    events = [k.ion_event(j, "HI", index) for index in selected]
    base = {f"A:{j}": Q(1), "HI": Q(1)}
    rates = {ev.name: k.proposal(ev, base, Q(1)) for ev in events}
    result = accepted.capacity_step(base, {ev.name: ev.column for ev in events},
                                    rates, Q("1e20"))
    donors = [{key: str(-value) for key, value in ev.column.items() if value < 0}
              for ev in events]
    assert all(donor == {f"A:{j}": "1", "HI": "1"} for donor in donors)
    ratios = [result.extents[ev.name]/ev.probability for ev in events]
    assert all(value == ratios[0] for value in ratios)
    denominators = [result.denominators[ev.name] for ev in events]
    assert len(set(denominators)) == 1
    out = {
        "schema": "bass-cr-sharing-capacity-checks.v1",
        "unit_id": "CR-THEORY-KERNEL-CUTOFF-20261013", "claim": "KA.29",
        "status": "pass", "started_utc": started, "finished_utc": stamp(),
        "elapsed_seconds": time.monotonic()-timer,
        "runtime": {"python": sys.version, "executable": sys.executable,
                    "numpy": np.__version__, "scipy": scipy.__version__,
                    "platform": platform.platform()},
        "source_files": [file_record(ROOT/rel) for rel in
            ("checks/check_sharing_capacity.py", "kernel_event_adapter.py",
             "inputs/prior/event_capacity_step.py", "inputs/KERNEL_SOURCE_BINDING.json")],
        "saved_grid_raw_sha256": k.binding["grid"]["raw_sha256"],
        "largest_gap_eV": max_gap, "min_binding_eV": min_binding,
        "min_of_27_effective_costs_eV": min_cost,
        "no_ion_or_excitation_parent_reprojection": True,
        "parent_index": j, "parent_energy_eV": float(k.E[j]),
        "species": "HI", "source_sharing_points_in_family": len(slow),
        "targeted_sharing_indices": selected,
        "negative_donor_columns": donors,
        "common_capacity_denominator_exact": str(denominators[0]),
        "extent_over_probability_exact": [str(value) for value in ratios],
        "all_three_ratios_equal": True,
        "full_generator_built": False, "ODE_or_NCP_run": False,
        "scope": "mesh inequality plus three same-family exact extents; proof extends to all quadrature points",
    }
    path = ROOT/"results/SHARING_CAPACITY_CHECKS.json"
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False)+"\n")
    print(json.dumps({key: out[key] for key in ("status", "started_utc", "finished_utc",
          "largest_gap_eV", "min_binding_eV", "targeted_sharing_indices", "all_three_ratios_equal")}, indent=2))


if __name__ == "__main__":
    main()
