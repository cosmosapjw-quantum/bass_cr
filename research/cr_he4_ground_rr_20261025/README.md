# Conditional He4 ground RR consumer

Start with `FROZEN_CONTRACT.md`, `CONTRACT.json`, `THEORY_KO.md`, and
`RESULTS_KO.md`. `CLAIM_GATE.json` states the exact adopted scope.

The new consumer adds one He+ground -> neutral-ground spontaneous channel to
the saved PR105 H1 chain. All old generators, source projections and completed
science remain unchanged. C23E's all-level closure is not added to ground RR.

## Actual completed commands

Commands below are historical reproduction specifications. Their output IDs
are create-only and consumed; do not rerun a completed identity. A necessary
future changed-context execution requires a new root-bound run ID and budget.
The commands were run with `--unit` set to this directory's absolute path:

```bash
python3 -B implementation/dispatch.py --unit "$PWD" --mode controls --run-id cr_he4_rr_controls_20261025_v2
python3 -B implementation/dispatch.py --unit "$PWD" --mode primary --run-id cr_he4_rr_primary_20261025_v1
python3 -B implementation/dispatch.py --unit "$PWD" --mode review --run-id cr_he4_rr_c9_20261025_v1
python3 -B implementation/dispatch.py --unit "$PWD" --mode plot --run-id cr_he4_rr_plot_20261025_v1
```

The v1 control attempt failed before a child started. Its actual resource
refusal and source are retained. The v2 operational correction is documented
in `evidence/RESOURCE_ADMISSION_REVISION.json`; scientific input/criteria did
not change.

## Inputs and portability

Python3, NumPy, SciPy and matplotlib were used with native threads=1. The exact
input manifest contains eight PR104 saved NPZs, eight PR105 saved NPZs, three
C23D384-atom CSVs, C23B scalar provider and its native table. Dense arrays and
native table bytes are private backup inputs and are intentionally omitted
from public Git. They are present in the canonical source ZIP, where every
file is pinned by SHA256 and size. The ancestral canonical source is identified
in `inputs/INPUT_MANIFEST.json`; restore bytes rather than regenerating science.

`implementation/prepare_inputs.py` verifies all164 ancestral canonical payloads
and copies the21 input files. It writes create-only inputs. A normal resume
does not need to re-run it when these exact bytes and manifest remain present.

## Evidence

- R6: `review/R6_THEORY.json`.
- Controls: `runs/cr_he4_rr_controls_20261025_v2/RESULT.json` (31 checks).
- Primary: `runs/cr_he4_rr_primary_20261025_v1/RESULT.json` and
  `SOURCE_WEIGHTED_RESULTS.json` (192 RHS,24 rows,216 comparisons).
- Independent: `runs/cr_he4_rr_c9_20261025_v1/RESULT.json`
  (Decimal70,48 RHS,72 coefficient nodes,6 source rows).
- Plot: `runs/cr_he4_rr_plot_20261025_v1/HE4_RR_SAVED_RESULTS.png`
  with separate CSV/JSON values.
- Budget: `evidence/BUDGET_FINAL.json`.

N4/N5 remain partial/open; N6/N7 remain predecessor-gated. Physical completion,
global error, missing photon occupation and unprovided physical channels remain
explicitly unresolved. Publication and backup authority is the root delivery.
