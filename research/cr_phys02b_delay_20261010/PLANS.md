# CR-PHYS02B implementation contract

The selected design is a sparse linear continuous-time electron branching
generator at the frozen gas state. Alternatives were the upstream complete-
cooling matrix (cannot encode a physical delay) and a continuous-energy Monte
Carlo cascade (unnecessary sampling variance for this bounded deterministic
test). Only a sidecar is changed. The existing production FS10 provider and
receiver remain outside this implementation scope.

1. Preserve six exact upstream source files and their SHA-256 source manifest.
2. Translate the selected old-method rate formulas with explicit local densities.
3. Assemble absolute rates and paired conservative daughter transitions; keep
   excitation, binding, heat, and unresolved cutoff reservoirs separate.
4. Check raw formula parity, generator moments, impulse causality, positivity,
   OFF behavior, finite time evolution and frozen-grid/time refinements.
5. Preserve first failures, perform at most one repair round, return for an
   independent Astra review. Do not commit, push or change production in this unit.

Rollback consists of removing only this new sidecar after its evidence has been
preserved. No original tracked file is modified. NumPy/SciPy are already present;
no new runtime dependency or external database is introduced.

## One authorized characteristic repair — executed

The failed donor-cell transport was replaced by a moving characteristic grid.
The unchanged collision terms use its midpoint energies; exact characteristic
energy decreases enter heat. A static donor-cell matrix exponential cannot
serve as the new transport reference, so the additive repair contract records
same-stage dense/sparse collision parity and refined characteristic reference
without changing any acceptance tolerance, physical input, impulse or epoch.

- Targeted tests: 9 PASS after the two first implementation failures were saved.
- Single full repair-closeout: PASS_SCOPED, all original rows plus arrival oracle.
- Original failed validation: byte-identical, SHA recorded in REPAIR_CONTRACT.json.
- Remaining action: independent parent review; no implementation self-promotion.
