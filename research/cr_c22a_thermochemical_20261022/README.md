# C22A — finite-UV thermochemical energy pilot

This is a new initial-value problem following the completed C21O recovery.
It preserves the non-tilted LRS kinetic implementation, 21 explicitly declared
atomic populations, full Frobenius norms and signed stress addition. It adds a
dynamical common gas temperature, six depleted/redshifting photon cohorts,
photoelectron heating, and the kinetic recombination moment derived from the
frozen Verner–Ferland fit. The old 51 C21O trajectories are reused as historical
evidence and are not reexecuted.

## Scientific authority and scope

- Parent science C: `6b6db06e8148e6826a2d5bf7dbc53d362126ca62`.
- Historical document D: `f7ca6905729f7d8d36ca0605f7b1dd7ad5595819`.
- Parent recovery R: `a5e12c5f3e6d323e211d65fefad34060ec07eff0`.
- Parent execution identity: `c60d734b0ed8cc7d1a147e181da27c282e3f47be90f8b0eb1d65c030faabea0f`.
- Current publication target: existing draft PR96 on
  `research/cr-c21o-hheli-z2-sandbox-20261021`.
- Contract: `CONTRACT.json`; rate coverage: `RATE_COVERAGE.json`;
  derivations: `theory/THERMOCHEMICAL_ENERGY_CONTRACT.md`.

The new UV and gas stress closures are imposed isotropic. Nonbaryonic Vlasov
matter retains its separate anisotropic stress. Thermal, chemical and finite
UV energy are trace sectors: their ratio to the background Einstein source is
diagnosed, and they are not newly inserted into that source. Escaped RR energy
is cumulative boundary export; it is not a propagated spectrum. No external
stellar emissivity is supplied. Compton energy exchange, CI, excitation, DR,
free-free, charge exchange, molecules and nuclear reactions are not active.
The saved-history omission diagnostics do not change the computed trajectories.
`global_error_bound=null`; a complete astrophysical thermochemical/radiative
model remains OPEN.

## Reproduce only new work

The immutable C21O source dependencies must be present in their original
`research/` sibling paths. A source freeze records their exact SHA256 values.
Use a new run ID and a new output directory for every new attempt.

```bash
python3 test_model.py
python3 run_pilot.py --freeze-source evidence/SOURCE_FREEZE_new.json
python3 run_pilot.py --run-id new_case_run_id \
  --source-freeze evidence/SOURCE_FREEZE_new.json \
  --cases inputs/NOMINAL_CASES.json --method BDF --workers 2
python3 analyze.py runs/new_case_run_id
```

The runner checks affinity, cgroup quota/memory and bounded lease locations,
protects CPU55 and a distinct coordinator CPU, uses at most two workers with
one numerical thread each, and refuses output-name reuse. It saves both 201
registered times and the adaptive solver's accepted mesh. Neither sampling
scheme supplies a continuous global error bound.

## External and historical evidence

`evidence/intake_refs/` records the seven-repository survey; external ensembles
and source identities remain distinct. REI220/BASS180 are mirrors of one
compact33 study. Their prior four-file comparison is PASS_SCOPED, not a new
127-raw audit or measured algebraic speedup. HE85's new external reintegration
is not byte recovery of lost raw data. VigilODE P02 C6FAIL remains recorded.
`evidence/intake_backup/` records separate provider acknowledgments. Historical
Drive C21O preservation remains OPEN. Inaccessible conversations are UNAVAILABLE;
the original nuclear-network PNG has not been recovered or read.

## Results and acceptance

Read `REPORT_KO.md` and `SCIENCE_ACCEPTANCE.json`. Three new BDF cases pass the
registered finite-state tests. A fourth trajectory, the Radau comparison,
finished all 18 integration segments but failed the exact neutron-zero reporting
gate at 8.6741e-36/Href; its original failure is retained. Independent saved-only
comparison of six fields passes without another ODE execution. The original
reference accepted mesh was not preserved and is UNAVAILABLE.

Use **`analysis_v3/`** and **`analysis_omissions_v1/`** for final figures. Earlier
analysis_v1/v2 versions are rejected and retained only as failure history;
analysis_v1 additionally has an unresolved HISTORY/manifest byte mismatch.
The final 603-row HISTORY and all final artifact hashes were independently
checked. Compton and H-excitation diagnostics show material missing energy
exchange; the next physical unit must couple those processes under an actual
temperature-coverage contract. Full closure remains OPEN.
