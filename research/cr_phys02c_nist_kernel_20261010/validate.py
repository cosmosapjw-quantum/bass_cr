"""One bounded campaign. JSON/log outputs are supplied to parent for patching."""
import hashlib
import json
import platform
from pathlib import Path
import time

import numpy as np
import scipy
from excitation_kernel import make_graph, rates, sparse_evolve, uniformize

ROOT = Path(__file__).resolve().parent


def campaign():
    started = time.monotonic()
    contract = json.loads((ROOT / "CONTRACT.json").read_text())
    rows = []
    for impulse in contract["impulses_eV"]:
        graph = make_graph(impulse)
        off = make_graph(impulse, enabled=False)
        for epoch in contract["epochs_s"]:
            if time.monotonic() - started > 120:
                raise RuntimeError("CAMPAIGN_WALL_BUDGET")
            state = sparse_evolve(graph, epoch)
            alternate, tail, terms = uniformize(graph, epoch)
            obs = graph.observables(state)
            alt = graph.observables(alternate)
            energy_ledger = obs[2] + obs[3] + 10.204 * obs[4] + 21.218 * obs[5]
            number_error = abs(obs[0] + obs[1] - 1)
            energy_error = abs(energy_ledger / impulse - 1)
            parity = float(np.max(np.abs(obs - alt)) / impulse)
            off_state = sparse_evolve(off, epoch)
            off_pass = bool(np.array_equal(off_state, np.ones(1)))
            t0_pass = epoch != 0 or bool(state[0] == 1 and np.count_nonzero(state) == 1)
            oracle_error = None
            if impulse == 1000.001:
                channel_rates = rates(impulse)
                total = float(channel_rates.sum())
                active = np.exp(-total * epoch)
                events = -np.expm1(-total * epoch) * channel_rates / total
                oracle = np.array([active, events.sum(), active * impulse,
                                   events @ (impulse - np.array([10.204, 21.218])),
                                   events[0], events[1]])
                oracle_error = float(np.max(np.abs(obs - oracle)) / impulse)
            passed = bool(state.min() >= 0 and number_error <= 2e-11 and energy_error <= 2e-11
                          and tail < 1e-13 and parity < 1e-10 and off_pass and t0_pass
                          and (oracle_error is None or oracle_error < 1e-10))
            rows.append({"impulse_eV": impulse, "epoch_s": epoch, "states": len(state),
                         "minimum_population": float(state.min()), "observables": obs.tolist(),
                         "number_ledger_relative": float(number_error),
                         "energy_ledger_relative": float(energy_error),
                         "uniformization_tail": tail, "uniformization_terms": terms,
                         "sparse_uniformization_error_over_E0": parity,
                         "analytic_oracle_error_over_E0": oracle_error,
                         "OFF": off_pass, "t0": t0_pass, "PASS": passed})
    return {"id": contract["id"], "status": "PASS_SCOPED_PENDING_REVIEW" if all(r["PASS"] for r in rows) else "FAIL",
            "contract_sha256": hashlib.sha256((ROOT / "CONTRACT.json").read_bytes()).hexdigest(),
            "environment": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
            "wall_s": time.monotonic() - started, "campaigns": 1, "targeted_repairs": 0,
            "observables_order": ["Nactive", "Ncrossing", "Uactive_eV", "Ucrossing_eV", "CH", "CHe"],
            "rows": rows, "model_errors": "UNKNOWN_NOT_MEASURED", "P02B_interface": "HOLD", "global_admission": "HOLD"}


if __name__ == "__main__":
    result = campaign()
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["status"] == "PASS_SCOPED_PENDING_REVIEW" else 1)
