#!/usr/bin/env python3
"""One charged preparation of the admitted low-birth recipient coefficients."""
import argparse
import hashlib
import json
import os
from pathlib import Path

import numpy as np

from model import (CONTRACT_SHA256, FITS, PROVIDER_SHA256, SOURCE_PATH,
                   TABLE_SHA256, T_END, UNIT_ID, array_identity, checked_file,
                   coefficient_arrays, constants_record, inventory, need,
                   source_arrays, write_json, write_npz)
from ports import context_record
from uniformization import choose_cutoff, ramp_occupancy_weights, uniformization_rate


def require_runner(unit, out):
    need(os.environ.get("CR_BOUNDED_UNIT") == UNIT_ID, "FROZEN_C4_BOUNDED_RUNNER_REQUIRED")
    need(os.environ.get("CR_BOUNDED_OUTDIR") == str(out.resolve()), "OWNED_RUN_DIRECTORY_REQUIRED")
    reservation = json.loads((out / "RESERVATION.json").read_bytes())
    need(reservation.get("unit") == UNIT_ID
         and reservation.get("attempt_id") == os.environ.get("CR_BOUNDED_ATTEMPT_ID"),
         "EXACT_RUNNER_RESERVATION_REQUIRED")
    checked_file(unit / "CONTRACT.md", CONTRACT_SHA256)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--source-records", type=Path)
    args = parser.parse_args()
    unit = Path(__file__).resolve().parents[1]
    out = args.out.resolve()
    require_runner(unit, out)
    source_path = args.source_records or unit.parents[1] / SOURCE_PATH
    provider = unit / "inputs/reused/c23b/spectral_photo_source.py"
    table = unit / "inputs/reused/c23b/data/verner_photo.dat"
    checked_file(provider, PROVIDER_SHA256, 10712)
    checked_file(table, TABLE_SHA256, 17760)
    energy, amplitude, acut, identity, _source = source_arrays(source_path)
    gas = inventory()
    arrays = coefficient_arrays(energy, gas)
    arrays["A_m3_s2"] = amplitude
    arrays["A_cutoff_m3_s2"] = np.asarray(acut)
    times = np.asarray([T_END / 4, T_END / 2, 3 * T_END / 4, T_END])
    arrays["times_s"] = times
    nu = uniformization_rate(arrays["drift_s_inv"], arrays["lambda_H_s_inv"], arrays["lambda_He_s_inv"])
    cutoff, choice = choose_cutoff(nu, T_END)
    wn, wo, tails = ramp_occupancy_weights(nu, times, cutoff)
    arrays["weights_n"] = wn
    arrays["weights_o"] = wo
    arrays["nu_s_inv"] = np.asarray(nu)
    hashes = {key: array_identity(value) for key, value in arrays.items()}
    write_npz(out / "PREPARED.npz", arrays)
    npz_raw = (out / "PREPARED.npz").read_bytes()
    record = {
        "schema": "CR_LOW_BIRTH_PREPARATION_V1", "unit": UNIT_ID,
        "status": "PREPARED_CHANGED_OPERATOR", "contract_sha256": CONTRACT_SHA256,
        "input": identity, "inventory": gas, "context": context_record(gas),
        "constants": constants_record(),
        "provider": {"helper_sha256": PROVIDER_SHA256, "table_sha256": TABLE_SHA256,
                     "imported": False, "fit_tuples": FITS,
                     "source_residual_state_resolution": "CONDITIONAL_SMOOTH_GROUND_CHANNEL_MODEL"},
        "array_identities": hashes, "uniformization_rate_s_inv": nu,
        "uniformization_rate_hex": nu.hex(), "cutoff_choice": choice,
        "weights": tails, "new_coefficient_evaluation": True,
        "source_regenerated": False, "old_science_replay": 0,
        "old_full9600_G_recovered": False,
        "PREPARED_npz": {"bytes": len(npz_raw), "sha256": hashlib.sha256(npz_raw).hexdigest()},
        "global_physical_error": None, "global_physical_completion": None,
    }
    write_json(out / "PREPARATION.json", record)
    print(json.dumps({"status": record["status"], "unit": UNIT_ID,
                      "active_states": len(energy), "cutoff_M": cutoff,
                      "nu_T": choice["x_max"], "coefficient_arrays": len(arrays)}, allow_nan=False))


if __name__ == "__main__":
    main()
