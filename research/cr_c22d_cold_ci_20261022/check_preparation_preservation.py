"""Fault-injected runner test. The fake solver performs no physical integration."""
from pathlib import Path
from types import SimpleNamespace
import argparse
import io
import json
import numpy as np
import run_pilot as driver
from model import ThermochemicalFactory

parser = argparse.ArgumentParser()
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
case = json.loads(Path("inputs/NOMINAL_CASES.json").read_text())["cases"][1]
model = ThermochemicalFactory().build(case)
real_inset = driver.endpoint_inset
calls = {"inset": 0, "fake_solver": 0}


def inset(*values, **kwargs):
    calls["inset"] += 1
    if calls["inset"] == 3:
        raise ValueError("INJECTED_NEXT_SEGMENT_PREPARATION_FAILURE")
    return real_inset(*values, **kwargs)


def fake_solver(rhs, interval, initial, **kwargs):
    calls["fake_solver"] += 1
    initial = np.asarray(initial)
    return SimpleNamespace(success=True, message="TEST_STUB_NO_ODE", nfev=0, njev=0, nlu=0,
                           t=np.array(interval), y=np.repeat(initial[:, None], 2, axis=1),
                           sol=lambda times: np.repeat(initial[:, None], len(times), axis=1))


driver.endpoint_inset, driver.solve_ivp = inset, fake_solver
try:
    driver.integrate_segmented(model, "BDF", 3e-11, 3e-13, io.StringIO())
except Exception as exc:
    preserved = isinstance(exc, driver.IntegrationFailure)
    report = {"status": "GREEN_PRESERVES_PRIOR_POINTS" if preserved else "RED_LOSES_PRIOR_POINTS",
              "exception": repr(exc), "calls": calls, "physical_ODE": 0,
              "arrays_are_test_stubs_not_scientific_results": True,
              "driver_sha256": driver.sha256(Path(driver.__file__))}
    if preserved:
        report["preserved_accepted_points"] = int(len(exc.arrays["eta"]))
        report["preserved_segments"] = len(exc.segments)
        assert report["preserved_accepted_points"] == 2 and report["preserved_segments"] == 1
else:
    raise AssertionError("INJECTED_FAULT_NOT_REACHED")
driver.json_create(args.output, report)
print(json.dumps(report))
