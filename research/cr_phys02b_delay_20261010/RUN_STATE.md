# Characteristic repair return state

- Base branch: `research/cr-phys03-fs10-xi01-20261010`.
- Base HEAD: `3189026c312318bfee4cac70ea3be45cc9cbfcae`.
- Base tree: `6548d1fb944b5567b643fe69a4383d4b7df63e02`.
- Python 3.12.3; NumPy 2.4.2; SciPy 1.17.0; single BLAS/OpenMP thread.
- Exact executed source identities and command: `evidence/REPAIR_VALIDATION.json`.
- One full repair-closeout: exit 0, PASS_SCOPED; 45 histories and all eight checks.
- Original validation FAIL remains unchanged. First repair test FAIL also retained.
- Software: PASS_9; numerical/scientific component checks: PASS_SCOPED.
- Independent review: PENDING_PARENT. Promotion: HOLD_PENDING_REVIEW.
- No production changes, commit, push, source convolution or extended domain.
- Next action: independent diff review; if approved, begin a separately bounded
  convolution/domain-extension unit. Do not rerun unchanged acceptance evidence.
