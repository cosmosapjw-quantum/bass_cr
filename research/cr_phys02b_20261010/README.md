# CR-PHYS02B: causal HI/HeI electron cascade

Read REPORT_KO.md for the physical result and limits, DERIVATION_KO.md for the equations,
and review/FINAL_DECISION.json for independent admission. This is an additive research
unit with fixed source, bath, energy bounds and a disclosed hybrid atomic representation.
It is not an admitted production REI or whole-history provider.

`src/causal_cascade.py` implements the operator. `tests/verify_cascade.py` is the actual
scientific runner. Keep `research/cr_phys02a_20261010` and the necessary PHYS01 parent
modules at their original sibling paths; inputs/PARENT_SOURCE_MANIFEST.json pins them.

From the repository root, with Python3.12 and requirements installed:

```bash
OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 OMP_NUM_THREADS=1 \
NUMEXPR_NUM_THREADS=1 OMP_MAX_ACTIVE_LEVELS=1 \
python3 research/cr_phys02b_20261010/tests/verify_cascade.py \
  --run-dir research/cr_phys02b_20261010/evidence/runs/LOCAL_NEW \
  --grids '800,1600;1600,3200'
```

Use a fresh run directory to preserve shipped evidence. R001 is a deliberate retained
first numerical failure; R002 is the fixed-criterion converged run. The report's13/13
count excludes unavailable external CGI comparison and does not measure atomic accuracy.
Scientific data and repository identities are distinct from operational publication
and backup receipts. See THIRD_PARTY_NOTICES.md for source attribution and license limits.
