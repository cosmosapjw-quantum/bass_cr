"""One bounded independent exact check of recorded source-response arithmetic.

This script imports only the standard library and never imports the producer.
It reads original JSON numeric tokens as Fraction, expands polynomial histories
against the truncated raw moments, and compares the stored rational packets.
It neither evaluates nor reconstructs a CR kernel.
"""

import csv
import hashlib
import json
from decimal import Decimal, localcontext
from fractions import Fraction as F
from pathlib import Path


UNIT = Path(__file__).resolve().parents[1]
SOURCE_SHA256 = "dfdca59ca0b4131c6143fe3cf0e402a7b18efb113a9af9bcc82a66696f5ec6f5"
fields = ("H0", "p", "R", "S", "mu_s", "m2_s2")
onsets = ("constant", "linear", "quadratic")
packet_checks = 0


def display(value):
    with localcontext() as context:
        context.prec = 50
        return str(Decimal(value.numerator) / Decimal(value.denominator))


def check(packet, expected, label):
    global packet_checks
    actual = F(int(packet["numerator"]), int(packet["denominator"]))
    assert actual == expected, (label, actual, expected)
    assert int(packet["numerator"]) == actual.numerator, (label, "noncanonical numerator")
    assert int(packet["denominator"]) == actual.denominator, (label, "noncanonical denominator")
    assert packet["decimal50"] == display(expected), (label, "decimal display")
    packet_checks += 1


raw_bytes = (UNIT / "inputs/F_CACHED_NUMERICAL_ARTIFACT.json").read_bytes()
assert hashlib.sha256(raw_bytes).hexdigest() == SOURCE_SHA256
source = json.loads(raw_bytes, parse_float=F)
stored = json.loads((UNIT / "results/CACHED_RESPONSE.json").read_bytes())
T = F(source["T_s"])
check(stored["T_s"], T, "T_s")
check(stored["T_years"], T / F(source["year_s"]), "T_years")
assert stored["source_sha256"] == SOURCE_SHA256

references = {}
for model, record in source["models"].items():
    selected = {key: F(record["selected"][key]) for key in fields}
    births = record["birth_columns"]
    H = sum((F(birth["H0"]) for birth in births), F(0))
    pooled = {"H0": H}
    for key in fields[1:]:
        pooled[key] = sum((F(birth["H0"]) * F(birth[key]) for birth in births), F(0)) / H
    for representation, moments in (("selected_record", selected), ("birth_defined", pooled)):
        p, r, s = (moments[key] for key in ("p", "R", "S"))
        m0 = p
        m1 = T * (p - r)
        m2 = T * T * (p - 2 * r + s)
        # Integrate 1, (T-tau)/T and (T-tau)^2/T^2 using raw moments.
        response = (m0, (T * m0 - m1) / T,
                    (T * T * m0 - 2 * T * m1 + m2) / (T * T))
        # Integrate each source history over [0,T-tau] before the kernel.
        cumulative_constant = T * m0 - m1
        cumulative_linear = (T * T * m0 - 2 * T * m1 + m2) / (2 * T)
        assert moments["H0"] > 0 and 0 <= s <= r <= p <= 1
        assert m1 >= 0 and m2 >= 0
        references[model, representation] = {
            "moments": moments, "response": dict(zip(onsets, response)),
            "m1": m1, "m2": m2,
            "cumulative_constant": cumulative_constant,
            "cumulative_linear": cumulative_linear,
        }

rows = {(row["model"], row["representation"]): row for row in stored["rows"]}
assert len(stored["rows"]) == len(rows) == len(references) == 4
assert set(rows) == set(references)
for identity, expected in references.items():
    row = rows[identity]
    H = expected["moments"]["H0"]
    for key, value in expected["moments"].items():
        check(row["moments"][key], value, str((identity, "moment", key)))
    for onset, value in expected["response"].items():
        check(row["response_over_H0_q0"][onset], value, str((identity, onset)))
        check(row["instantaneous_normalized_deficit"][onset], 1 - value, str((identity, "deficit", onset)))
        check(row["heating_coefficient_per_q0_in_original_normalization"][onset], H * value,
              str((identity, "heating", onset)))
    check(row["truncated_m1_s"], expected["m1"], str((identity, "m1")))
    check(row["truncated_m2_s2"], expected["m2"], str((identity, "m2")))
    check(row["source_curvature_bound_coefficient_s2"], expected["m2"] / 2, str((identity, "Taylor")))
    check(row["constant_source_cumulative_heat_over_H0_q0_T"], expected["cumulative_constant"] / T,
          str((identity, "cumulative_constant")))
    check(row["linear_source_cumulative_heat_over_H0_q0_T_over2"], expected["cumulative_linear"] / (T / 2),
          str((identity, "cumulative_linear")))

for representation in ("selected_record", "birth_defined"):
    a = references["fullBED", representation]
    b = references["legacy", representation]
    H_a, H_b = a["moments"]["H0"], b["moments"]["H0"]
    delta = stored["model_differences"][representation]
    check(delta["H0_fullBED_over_legacy_minus1"], (H_a - H_b) / H_b,
          representation + " H0 difference")
    for onset in onsets:
        x, y = a["response"][onset], b["response"][onset]
        check(delta["normalized_response_fullBED_over_legacy_minus1"][onset], (x - y) / y,
              representation + " normalized " + onset)
        check(delta["heating_coefficient_fullBED_over_legacy_minus1"][onset],
              (H_a * x - H_b * y) / (H_b * y), representation + " heating " + onset)

tsv_checks = 0
with (UNIT / "results/CACHED_RESPONSE.tsv").open(newline="") as stream:
    table = list(csv.DictReader(stream, delimiter="\t"))
assert len(table) == 4
assert {(row["model"], row["representation"]) for row in table} == set(references)
for row in table:
    expected = references[row["model"], row["representation"]]
    values = {key: expected["moments"][key] for key in ("H0", "p", "R", "S")}
    values.update({"H0_p": values["H0"] * expected["response"]["constant"],
                   "H0_R": values["H0"] * expected["response"]["linear"],
                   "H0_S": values["H0"] * expected["response"]["quadratic"],
                   "m1_truncated_s": expected["m1"], "m2_truncated_s2": expected["m2"]})
    for key, value in values.items():
        assert row[key] == display(value), (row["model"], row["representation"], key)
        tsv_checks += 1

for model in source["models"]:
    assert references[model, "selected_record"]["moments"] != references[model, "birth_defined"]["moments"]

print(json.dumps({
    "status": "PASS_SCOPED",
    "input_sha256": SOURCE_SHA256,
    "rows": len(rows),
    "onset_functionals": 12,
    "rational_packets_checked": packet_checks,
    "tsv_numeric_cells_checked": tsv_checks,
    "selected_and_birth_remain_distinct": True,
    "method": "Exact original numeric tokens; independently expanded polynomial and cumulative functionals",
    "producer_imports": 0,
    "producer_reruns": 0,
    "old_suite_runs": 0,
    "G": 0, "pulse": 0, "expm": 0, "resolvent": 0,
    "linear_solve": 0, "NCP": 0, "F_retry": 0,
}, indent=2))
