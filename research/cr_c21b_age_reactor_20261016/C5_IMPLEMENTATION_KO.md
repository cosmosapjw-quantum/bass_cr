# C21B C5 implementation checkpoint (2026-10-16 KST)

**Implemented** `src/c21b_age_reactor.py` (336 lines) and `tests/test_c21b_reactor.py` (~190 lines) as an isolated runnable **positive source-age FLRW photo-only H/He reference**. Source and test files are not native production replacements.

- Original-form original-code Verner outer-shell three rows and H/He native distinct fit/binding thresholds, original MD14 redshift source rate, flat cosmology H(a) and HE23 native-total-H normalization.
- Independent canonical `q20=a E`, `q_ref=q20/a*` conversion; individual birth tags `x_birth`, q and original physical emission energy per packet.
- Stable exact two-stock pair map with `expm1` and a positive min/max reconstruction, applied as a palindromic sequence to all photon/species pairs.
- Source birth at separate positive GL2 epochs in each time cell, BB50K GL_n positive spectral nodes in each of 3 native fit bands, crossing-aware evolution, per-H photon/ionization/binding/heat/thermal work.
- External gas geometry map `w∝a^-2` with its own work ledger; no duplicate H cooling inside reaction.
- Strict gas nuclei simplex and finite domain gate. Explicit source support zbar ∈[4,20]. Native C21 RHS not invoked in this stage.

**Executed actual Python sandbox validation at close of C5:** `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m pytest -q tests/test_c21b_reactor.py`: `20 passed in 0.57s`, exit 0. Scope covers original parameter consistency, exact pair-vs-Radau, source GL2-vs-QUAD, real Verner threshold source-free Radau, finite source-on gas evolution and number/energy ledgers. C6/C7 robustness+refinement still selected next for a full result study and audit.
