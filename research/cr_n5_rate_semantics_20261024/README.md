# CR N5 source-pinned rate semantics and CE envelope

Read [REPORT_KO.md](REPORT_KO.md), [FROZEN_CONTRACT.md](FROZEN_CONTRACT.md),
[theory/THEORY_REVIEW.md](theory/THEORY_REVIEW.md), and the independent C9 review.
The scope is a conditional H1 ground-state CE first-event diagnostic on the saved
C23D EE finite reflecting band. Full N5/N4 remain PARTIAL; N6/N7 remain gated.

Primary evidence: `implementation/runs/n5_ce_envelope_primary_20261024t031906828z_v1/`.
All 30 frozen input files are pinned in `inputs/INPUT_MANIFEST.json`. The exact
PHYS83 constructor is reused only for W-PL arrays. Its rate evaluators and the
PHYS84 source adapter are never called. Python 3.12, NumPy 2.3.5 and SciPy 1.17.0
were present; no dependency installation was required. Matplotlib 3.10.8 rendered
the saved data only.

An authorized new diagnostic after a relevant input change can be run from any
working directory with an unused lowercase run ID:

```bash
python3 -B /absolute/path/to/this/unit/implementation/dispatcher.py \
  --unit /absolute/path/to/this/unit --mode science \
  --run-id your_new_authorized_run_id
```

The dispatcher requires the observed local CPU0/8 topology and finite cgroup
memory limits, checks memory, reserves a local exclusive lease, and creates a
new output directory. Adapt the resource contract explicitly on another host.
Do not rerun a completed unchanged scientific identity for restoration. Use
saved raw outputs and manifests for recovery; repeated run IDs are rejected.

`implementation/EXECUTION_LEDGER_FINAL_V3.json` records implementation cost
only. Root `BUDGET_CONTINUITY.json` includes separate plotting/review and
inherited known costs. Global spend and remaining budget are unknown, not zero.
Publication, canonical recovery backup and central DAG identities are separate
from the scientific claim; final receipts live under `delivery/`.
