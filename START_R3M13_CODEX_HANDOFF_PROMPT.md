# R3M13 Codex start handoff

Base: branch `cr/r3m11-fixed-cap-gram-20260921` at
`02546302a3d6958ea9fa97488a670672e07be178`.

Continue the R3M12 b-grid NO_GO lane without repeating completed collision runs.

Mandatory preparation comparison at dx=.25 a0, physical dt=.05, fixed CAP:
- reference: imag_dt=.025, imag_steps=1200
- candidate: imag_dt=.0125, imag_steps=2400
- total imaginary time 30 t_a in both

1. Verify HEAD and existing R3M12 evidence. Do not touch main.
2. Run relevant existing tests and the new R3M13 tests.
3. Run `python -m cr_repro.r3m13_cli prepare-only` for both supplied configs.
   This must stop after preparation and must not launch collision propagation.
4. Compare the normalized initial states with `python -m cr_repro.r3m13_cli compare`.
   Use P_ref=0.00775827737938 and screen=.01.
5. Frozen sufficient threshold: `d_crit=4.3930987793802824e-4`.

If d<=d_crit, record a theorem-certified PASS for the existing 1% preparation
pair screen and do not run the candidate collision solely for that question.
If d>d_crit, the bound is inconclusive; run exactly one candidate collision and
compare the n<=3 Gram span. Do not infer failure from d alone.

Always record initial energy and stationary residual. If practical, add a
target-only one-step stationarity defect under the same real-time Strang
discretization, clearly separated from physical capture convergence.

Return `R3M13_LOCAL_PREPARATION_RETURN` with environment/tests, both state
SHA256/size, preparation diagnostics, theorem certificate, failure ledger, and
an explicit PASS or INCONCLUSIVE. b-grid remains NO_GO unless a later CR node
explicitly changes it. Push only to a dedicated R3M13 branch; do not merge main.
