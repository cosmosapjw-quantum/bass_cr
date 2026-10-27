"""Create-only exact-byte preparation.  No NumPy import or scientific evaluation.

Run once after root has frozen FROZEN_CONTRACT, THEORY and R6/native25 authority
files.  All attempts receive a preparation receipt and consume local-misc CPU.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
import re
import time

THEORY_SHA = "3e5f31d271c32efcd1ee9a1eb23625c2ead0dc0b6c4a78732de34ef4a696ceae"
ARCHIVE_SHA = "7e39930b862a0af5f87e5d3e4dd9d9fa4b37694dda496221e6e311957a087aaa"


def writej(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def pin(path):
    raw = path.read_bytes()
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def prior_preparation_cost(preparations, current):
    total = 0.0
    for directory in sorted(preparations.iterdir()):
        if directory == current or not directory.is_dir():
            continue
        try:
            cost = json.loads((directory / "PREPARATION_RECEIPT.json").read_text())["process_cpu_s"]
            need(not isinstance(cost, bool) and isinstance(cost, (int, float))
                 and math.isfinite(cost) and cost >= 0, "invalid prior cost")
        except (OSError, ValueError, KeyError, TypeError):
            raise RuntimeError("UNKNOWN_PRIOR_ATTEMPT_BUDGET:" + directory.name)
        total += cost
    return total


def run(unit, old, config_template, input_pins, prep_run_id):
    need(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", prep_run_id), "SIMPLE_PREPARATION_ID_REQUIRED")
    out = unit / "preparations" / prep_run_id
    out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    status, error, copied, old_cost = "FAILED_RETAINED", None, [], None
    try:
        old_cost = prior_preparation_cost(out.parent, out)
        need(old_cost + time.process_time() < 2.0, "LOCAL_MISC_CPU_RESERVATION_EXHAUSTED")
        config = json.loads(config_template.read_text())
        pins = json.loads(input_pins.read_text())
        need(pins["source_archive_sha256"] == ARCHIVE_SHA and len(pins["files"]) == 21,
             "ADMITTED_INPUT_PIN_SET_REQUIRED")
        need(config["operator_baseline"] == "EXACT_STORED_PR106_HEI_K_DIAG"
             and config["native_nb_m3"] is None, "FROZEN_CONFIGURATION_REQUIRED")
        need(pin(unit / "THEORY_KO.md")["sha256"] == THEORY_SHA, "EXACT_REVIEWED_THEORY_REQUIRED")
        need((unit / "FROZEN_CONTRACT.md").is_file(), "ROOT_FROZEN_CONTRACT_REQUIRED")
        expected = set()
        for chi, radius, nominal in itertools.product(config["chi"], config["R"], config["grid_N"]):
            name = f"chi{chi:g}_R{radius}_N{nominal}.npz"
            expected.update(("inputs/reused/pr104/" + name, "inputs/reused/pr106/" + name))
        expected.update("inputs/reused/c23d/ATOMS_" + z + ".csv" for z in config["source_z"])
        expected.update(("inputs/reused/c23b/spectral_photo_source.py", "inputs/reused/c23b/data/verner_photo.dat"))
        need({row["path"] for row in pins["files"]} == expected, "EXACT_CASE_SOURCE_CLOSURE")
        for row in pins["files"]:
            source = (old / row["source_relative_to_old_unit"]).resolve()
            need(source.is_relative_to(old.resolve()), "INPUT_SOURCE_PATH_ESCAPE")
            need(pin(source) == {"bytes": row["bytes"], "sha256": row["sha256"]},
                 "ADMITTED_INPUT_CHANGED:" + row["source_relative_to_old_unit"])
        authorities = []
        for rel in ("review/R6_THEORY.json", "intake/HEIII_NATIVE25_MAP_R5.json"):
            authorities.append({"path": rel, **pin(unit / rel)})
        review = json.loads((unit / "review/R6_THEORY.json").read_text())
        need(review["decision"] == "PASS_SCOPED_AFTER_TARGETED_REPAIR"
             and review["identity"]["reviewed_final_THEORY_sha256"] == THEORY_SHA,
             "EXACT_R6_THEORY_PASS_REQUIRED")
        inp = unit / "inputs"
        inp.mkdir(exist_ok=False)
        with (inp / "CONFIG.json").open("xb") as stream:
            stream.write(config_template.read_bytes())
        for row in pins["files"]:
            target = unit / row["path"]
            need(target.resolve().is_relative_to(inp.resolve()), "INPUT_DESTINATION_ESCAPE")
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as stream:
                stream.write((old / row["source_relative_to_old_unit"]).read_bytes())
            need(pin(target) == {"bytes": row["bytes"], "sha256": row["sha256"]}, "COPIED_INPUT_IDENTITY")
            copied.append(dict(row))
        record = {
            "schema": "CR_HEIII_IMMUTABLE_INPUTS_V1", "files": copied,
            "authority_files": authorities,
            "canonical_archive_sha256": ARCHIVE_SHA,
            "source_science_commit": pins["source_science_commit"],
            "source_document_commit": pins["source_document_commit"],
            "frozen_contract_sha256": pin(unit / "FROZEN_CONTRACT.md")["sha256"],
            "theory_sha256": THEORY_SHA,
            "config_sha256": pin(inp / "CONFIG.json")["sha256"],
            "input_pins_sha256": pin(input_pins)["sha256"],
            "preparation_run_id": prep_run_id,
            "new_scientific_execution": False,
            "old_source_projection_calls": 0, "old_generator_calls": 0,
            "source_quadrature": 0, "old_primary_replay": 0, "new_ODE": 0,
        }
        writej(inp / "INPUT_MANIFEST.json", record)
        need(old_cost + time.process_time() <= 2.0, "LOCAL_MISC_CPU_RESERVATION_EXCEEDED")
        status = "PASS"
    except Exception as exc:
        error = {"type": type(exc).__name__, "message": str(exc)}
    receipt = {"schema": "CR_HEIII_PREPARATION_RECEIPT_V1", "status": status,
               "run_id": prep_run_id, "error": error, "files_copied": len(copied),
               "process_cpu_s": time.process_time(), "wall_s": time.monotonic() - started,
               "previous_preparation_cpu_s": old_cost, "scientific_evaluations": 0,
               "budget_owner": "new unit local_misc2 CPU seconds", "partial_inputs_retained": status != "PASS",
               "historical_allowance_reused": False}
    writej(out / "PREPARATION_RECEIPT.json", receipt)
    print(json.dumps(receipt))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--unit", type=Path, required=True)
    parser.add_argument("--old-unit", type=Path, required=True)
    parser.add_argument("--config-template", type=Path, default=Path(__file__).with_name("CONFIG_TEMPLATE.json"))
    parser.add_argument("--input-pins", type=Path, default=Path(__file__).with_name("INPUT_PINS_TEMPLATE.json"))
    parser.add_argument("--prep-run-id", required=True)
    args = parser.parse_args()
    raise SystemExit(run(args.unit.resolve(), args.old_unit.resolve(),
                         args.config_template.resolve(), args.input_pins.resolve(), args.prep_run_id))
