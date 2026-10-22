# C22B prescribed Compton-bath pilot

Conditional scientific result: PASS_SCOPED. Full thermochemical/radiative closure OPEN.
Runtime identity: `e4e5ce42693d473939e72ac3cd2ade32cd4a342993524df94ccf121eb6afbd52` (31 files).

Read `REPORT_KO.md`, `CONTRACT.json`, `SCIENCE_ACCEPTANCE.json`, and `STAGE_RECORDS.json` first.
Final numerical artifacts: `analysis_v2`. The rejected v1 reference time-axis image is preserved.
New runs: BDF3 + Radau1,72segments. Completed C21O/NCP/C22A runs were not rerun.

## Review stored evidence without ODE execution

The delivery ZIP verifier hashes and opens the same in-memory ZIP bytes. Use its recorded delivery SHA.
`analyze.py` reads completed nominal/reference histories and the preserved C22A baseline, validates the
registered methods/tolerances/cases and source hashes, then derives accepted summaries. It makes no ODE call.
Choose a new output directory when deriving analysis again; all outputs are create-only.

```bash
python3 analyze.py --nominal runs/c22b_compton_bdf_20261022_v1 --reference runs/c22b_compton_radau_20261022_v1 --baseline ../cr_c22a_thermochemical_20261022/runs/c22a_finite_uv_bdf_20261022_v1 --out review_new_unique
```

Do not start `run_pilot.py` merely to reconstruct completed results. Future scientific extensions require
new inputs, a new source freeze/run ID, actual resource and lease checks, CPU55/coordinator separation,
and one numerical thread per worker.

GitHub and Drive publication/preservation status is independently tracked. Read the final authority sidecar
for actual commit, bundle, upload ACK and byte readback evidence. No triple-backup claim is made.
