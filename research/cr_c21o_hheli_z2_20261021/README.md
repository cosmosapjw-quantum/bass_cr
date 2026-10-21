# C21O: executable conditional H/He/Li–LRS pilot, z=20 to 2

**45 independent-stress trajectories and 6 additional comparison trajectories completed in the sandbox.** This is a new conditional photoionization/Case-A radiative-recombination–electron–Thomson LRS model. It is not a full nuclear, thermal, stellar or radiation-transfer reionization history. The original C21L 81 and C21M/N campaigns were not rerun or relabeled.

Read [REPORT_KO.md](REPORT_KO.md), [PHYSICAL_CONTRACT_KO.md](PHYSICAL_CONTRACT_KO.md), and [RESEARCH_DAG.json](RESEARCH_DAG.json) before interpretation. Current plots are in `analysis_v2/`; `analysis_v1/` and its analyzer snapshot are retained as historical artifacts. All 51 individual raw arrays and execution receipts are under `runs/`.

## Model and numerical identity

- 20 atomic charge populations: H1 I–II, D I–II, T I–II, He3 I–III, He4 I–III, Li6 I–IV and Li7 I–IV; plus free neutron. Free electrons are an algebraic charge sum.
- 40 inherited LRS states + 21 populations + optical depth = 62 states at L=8. L=12 comparisons have 78 states.
- Prescribed isotropic UV cohorts and prescribed temperature; photoionization and spontaneous Case-A RR. Other reaction families are explicitly UNMODELED, not silently zero-filled.
- Full Frobenius norms and signed coordinates, with separate massive matter, CMB photon, massless-neutrino, radiation-total and total tensors.
- FP64; BDF default, one independent Radau comparison; rtol=3e-11 and scaled-state atol=3e-13; 201 saved times.
- Frozen execution identity: `c60d734b0ed8cc7d1a147e181da27c282e3f47be90f8b0eb1d65c030faabea0f`.
- Original LRS science commit: `3b85dedce84d37b3e165da00685a8a984950aafe`.
- Parent document head: `8dc5031b3323d4be42a7444843294200aa8887f2`.
- `global_error_bound=null`.

The nested `initial_mapping` receipt describes inherited kinetic initialization only. Its original-RHS/UV-absent/40-state labels do not describe the new top-level C21O model. The top-level source manifest, 62/78 states, BDF/Radau and explicit external UV are authoritative for these runs.

## Use completed data without ODE replay

Run from the repository root. Python 3.12.14 was used; exact numerical package versions are in `requirements.txt`. This Python implementation requires no project-specific C/C++ compilation. A fresh environment can install the pinned dependencies with `python -m pip install -r "$C21O/requirements.txt"`.

```bash
C21O=research/cr_c21o_hheli_z2_20261021
C21O_OUT=$(mktemp -d /tmp/c21o-analysis-XXXXXXXX)
python "$C21O/analyze.py" \
  --grid-run "$C21O/runs/c21o_grid45_v1" \
  --control-run "$C21O/runs/c21o_controls6_v1" \
  --output "$C21O_OUT/analysis"
```

This only reads saved arrays, verifies their SHA/case bindings, and writes new CSV/NPZ/PNG/PDF. The destination must not exist. No ODE or RHS evaluation is performed by the analyzer.

For a new independent validation receipt, if needed for a concrete audit, use:

```bash
python "$C21O/validate_results.py" \
  --grid-run "$C21O/runs/c21o_grid45_v1" \
  --control-run "$C21O/runs/c21o_controls6_v1" \
  --output "$C21O_OUT/validation.json"
```

The committed validation is already complete; repeating it is optional and is not new science. An archive delivery contains the required inherited dependencies in the same repository layout.

## New science and resource-aware dispatch

The existing 51 cases are complete. Do not launch them again merely to show another host can run them. For a genuinely new, validated input manifest, use a new output directory:

```bash
python "$C21O/run_sandbox.py" run \
  --grid /absolute/path/to/new_validated_grid.json \
  --output /absolute/path/to/new_create_only_run \
  --workers 62 --lease-json /absolute/site/path/to/current_cpu_leases.json
```

`--workers 62` is an upper request, not a fixed allocation. The scheduler observes host affinity, cgroup CPU and memory limits, sampled load, available RAM and the supplied shared lease. CPU55 and a coordinator CPU are excluded from workers. It never launches more workers than pending cases, uses one numerical thread per worker, and bounds active submissions. It pauses new dispatch when resource headroom falls; completed results are retained. It does not kill or alter other owners' tasks/files. Observation is not a distributed atomic lease reservation; use the site's real scheduler/lease convention.

The memory admission allowances are 512 MiB/worker + 768 MiB coordinator + 1 GiB reserve, not measured peak RSS or enforced caps. On the observed 8-CPU/8-GiB sandbox, resource admission selected 4 and later 5 workers. No 64-core scaling or speedup has been measured.

`--resume` accepts only identical source/input/Python-build/NumPy/SciPy identities, verifies completed case receipts and bytes, and dispatches only never-started cases. Started/failed directories are held for inspection. Do not bypass a mismatch; create a new run for changed inputs or builds. Completed cross-host data can always be analyzed read-only without using resume.

## Main artifacts

| Artifact | Meaning |
|---|---|
| `analysis_v2/STRESS_EVOLUTION45.*` | Full Sigma, Pi_m, Pi_r and Pi_tot over z=20→2 |
| `analysis_v2/ION_EVOLUTION21.*` | Every tracked population and algebraic electron density |
| `analysis_v2/SIGNED_CANCELLATION.*` | Opposing stresses, generated shear, photon/neutrino split |
| `analysis_v2/COUPLING_AND_NUMERICS.*` | Optical depth, imposed T, omitted energy diagnostic, limited numerical comparisons |
| `analysis_v2/ENDPOINT_SLICES45.*` | Five signed-S0 slices across independent Pm0/Pr0 |
| `analysis_v2/ENDPOINTS45.csv` | Endpoint values with exact coordinate labels |
| `analysis_v2/ION_HISTORY45.csv` | All saved ionic abundances in physical Y/Href units |
| `analysis_v2/ENSEMBLE45.npz` | Aggregate arrays; full sector tensors remain in individual raw histories |
| `checks/TRAJECTORY_VALIDATION.json` | Hash-bound 51-case validation and limited comparisons |
| `checks/INDEPENDENT_*REVIEW.json` | Physics, operations and visual audit scopes |
| `CODEX_HANDOFF_KO.md`, `NEXT_THREAD_HANDOFF_KO.md` | Copyable continuation instructions |

See `vendor/atomic/ATTRIBUTION.md` for external code/data provenance and licensing boundaries. No long extracted literature text or private backup search payload is included.
