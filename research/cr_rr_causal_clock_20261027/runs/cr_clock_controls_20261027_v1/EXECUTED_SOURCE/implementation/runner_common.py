"""Pinned local orchestration helpers; never rebuild inherited physics."""
from __future__ import annotations
import argparse
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import time

import numpy as np
from clock_engine import ClockEngine


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write_new(path, value):
    with Path(path).open("x") as f:
        json.dump(value, f, indent=2, ensure_ascii=False, allow_nan=False)
        f.write("\n")


def args():
    p = argparse.ArgumentParser()
    for name in ("unit", "output", "config", "pins"):
        p.add_argument("--" + name, type=Path, required=True)
    p.add_argument("--run-id", required=True)
    return p.parse_args()


def outward(x, upper):
    y = float(x)
    require(math.isfinite(y), "FINITE_INTERVAL_ENDPOINT")
    exact = Fraction.from_float(y)
    if (upper and exact < x) or (not upper and exact > x):
        y = math.nextafter(y, math.inf if upper else -math.inf)
    require(math.isfinite(y), "FINITE_OUTWARD_ENDPOINT")
    return y


def photon(count, kinetic):
    ion = Fraction(2721, 50)
    return [outward(Fraction.from_float(kinetic[0]) + ion * Fraction.from_float(count[0]), False),
            outward(Fraction.from_float(kinetic[1]) + ion * Fraction.from_float(count[1]), True)]


def difference(second, first, cap):
    lo = max(Fraction(0), Fraction.from_float(second[0]) - Fraction.from_float(first[1]))
    hi = min(Fraction.from_float(cap[1]), Fraction.from_float(second[1]) - Fraction.from_float(first[0]))
    require(hi >= lo, "INCONSISTENT_TIME_BIN_INTERVAL")
    return [outward(lo, False), outward(hi, True)]


class Context:
    def __init__(self, arguments):
        self.args = arguments
        self.unit = arguments.unit.resolve()
        self.output = arguments.output / "payload"
        self.output.mkdir(parents=True, exist_ok=False)
        self.snapshot = Path(__file__).resolve().parent.parent
        self.config = read(arguments.config)
        self.pins = read(arguments.pins)
        self.pinmap = {x["path"]: x for x in self.pins["files"]}
        self.cap = float(os.environ["CR_CLOCK_WORKER_CPU_CAP_S"])
        self.guard = self.cap - max(.15, .02*self.cap)
        self.verify("inputs/INPUT_MANIFEST.json")
        self.manifest = read(self.unit / "inputs/INPUT_MANIFEST.json")
        self.verify("CODING_CONTRACT.json")
        self.contract = read(self.unit / "CODING_CONTRACT.json")
        self.library = self.snapshot / self.config["native_library"]
        nativepin = self.pinmap[self.config["native_library"]]
        require(sha(self.library) == nativepin["sha256"], "EXECUTED_NATIVE_BINARY_PIN")
        self.engine = ClockEngine(self.library)
        self.guard_cpu()

    def verify(self, rel):
        p = self.unit / rel
        require(rel in self.pinmap, "UNPINNED_INPUT:" + rel)
        pin = self.pinmap[rel]
        require(p.stat().st_size == pin["bytes"] and sha(p) == pin["sha256"], "INPUT_HASH:" + rel)
        return p

    def guard_cpu(self):
        require(time.process_time() < self.guard, "WORKER_CPU_GUARD")

    def load_case(self, case):
        hp = self.verify(case["operator_file"])
        sp = self.verify(case["source_file"])
        with np.load(hp, allow_pickle=False) as h, np.load(sp, allow_pickle=False) as s:
            d, l, up = (h[k].copy() for k in ("K_diag", "K_lower", "K_upper"))
            r = h["rhs_physical18"][:, 10:12].copy()
            x = h["solution_physical18"][:, 10:12].copy()
            witness = h["t"].copy()
            source_ids = self.contract["exact_problem"]["sources"]
            weights = np.asarray([s["source_"+z][1:] for z in source_ids], dtype=np.float64)
            boundary = [float(s["source_"+z][0]) for z in source_ids]
            require(np.array_equal(h["E_eV"], s["E_eV"]), "SOURCE_OPERATOR_ENERGY_GRID")
        problem = self.engine.prepare(d, l, up, r, weights, witness, x, source_ids)
        provenance = []
        for index, sid in enumerate(source_ids):
            atom = next(a for a in self.manifest["atom_files"] if Path(a["path"]).name == "ATOMS_"+sid+".csv")
            self.verify(atom["path"])
            provenance.append({
                "distribution_id": "C23D_z"+sid+"_absolute_pulse_cm3",
                "count_projection_sha256": hashlib.sha256(np.asarray(weights[index], dtype="<f8").tobytes()).hexdigest(),
                "projection_encoding": "active[1:] C-order little-endian binary64; no renormalization",
                "operator_sha256": sha(hp), "operator_identity_kind": "full saved HeIII NPZ bytes",
                "bath_sha256": self.manifest["bath_sha256"],
                "raw_atom_sha256": atom["sha256"],
                "boundary_entry_count_cm3": boundary[index],
                "boundary_entry_RR_reward": 0,
                "original_source_file_sha256": sha(sp),
            })
        return problem, provenance


def clock_metadata(raw):
    records = []
    for horizon in raw:
        if horizon["horizon_s"] == 0:
            continue
        record = {k: horizon[k] for k in ("horizon_s", "m", "delta_requested", "arithmetic_certificate")}
        record["clocks"] = {side: {key: horizon["clocks"][side][key] for key in
            ("gamma_s_inverse", "gamma_hex", "a_numerator", "a_denominator", "tail_upper")}
            for side in ("minus", "plus")}
        records.append(record)
    return {"time_units": "proper_s", "gamma_units": "s^-1", "records": records}


def tighten(raw, source_index, horizons):
    fields = ("count_cm3", "kinetic_eV_cm3")
    result = []
    for T in horizons:
        rows = [h["source_rows"][source_index] for h in raw if h["horizon_s"] == T]
        require(bool(rows), "MISSING_HORIZON")
        result.append({"T_s": T, **{f: [max(r[f][0] for r in rows), min(r[f][1] for r in rows)] for f in fields}})
    for f in fields:
        for i in range(1, len(result)):
            result[i][f][0] = max(result[i][f][0], result[i-1][f][0])
        for i in range(len(result)-2, -1, -1):
            result[i][f][1] = min(result[i][f][1], result[i+1][f][1])
        for row in result:
            require(0 <= row[f][0] <= row[f][1] and all(map(math.isfinite, row[f])), "EMPTY_MONOTONE_LEVEL_INTERSECTION")
    for row in result:
        row["photon_eV_cm3"] = photon(row["count_cm3"], row["kinetic_eV_cm3"])
    return result
