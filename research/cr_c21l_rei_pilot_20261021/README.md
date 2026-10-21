# C21L: preliminary REI initial shear–stress pilot

## Actual delivered result

The current runner includes the parent-authorized R1/R2 operational repair. The
exact original executed code and source closure are preserved in
`archived_execution_v1/`; the81-case raw data and old manifest remain unchanged.
The original pilot identity is `0090e1549b21b07e46001de2bf9cb2eab9bf0cba87ffe3d4d824ba117fecb44a`.
The repaired runner has a new source/runtime identity and intentionally rejects
resume against that old manifest. These repairs change execution provenance and
queued-case recovery, with no change to physical equations or pilot results.

The requested **81 distinct physical cases completed**, with four persistent
Python worker processes and one coordinator. Each case independently called the
unchanged PR147 `CanonicalFVSpecies.integrate(n=101, rtol=3e-11, atol=3e-13)`.
All worker exit codes were zero. This is an **EXPLORATORY / PRELIMINARY sandbox
pilot**, accepted by the independent review and parent within the scoped LRS collisionless preliminary claim; see `SCIENCE_ADMISSION.json` and `review/PARENT_CLOSURE.json`.

The imported source revision is REI PR147 commit
`3b85dedce84d37b3e165da00685a8a984950aafe`. All nine imported source files are
preserved unchanged with their relative directory structure under `vendor/rei/`;
`SOURCE_MANIFEST.json` records repository, revision, path, size and SHA256.

| Actual observation | Value |
|---|---:|
| Completed cases | 81 / 81 |
| Failed / incomplete cases | 0 / 0 |
| Full FP64 state shape per case | 40 × 101 |
| Final Frobenius shear range | 1.700222440078772e-20 to 0.00481987955610218 |
| Final Frobenius stress range | 5.712792465989438e-20 to 0.00029587955662661403 |
| Largest initial S/P mapping discrepancy | 1.3877787807814457e-17 |
| Largest algebraic Einstein H² constraint relative residual | 2.220446049250313e-16 |
| Largest radiation number monopole deviation | 0 |
| Smallest massive canonical cell population | 1.491026203638869e-30 |
| Largest massive comoving-number relative residual | 4.440892098500626e-16 |
| RHS evaluations per case | 92 to 224 |
| Common initial angular multiplier k range | -0.33501982430636024 to 0.3350198243063604 |

The constraint residual checks the saved algebraic constraint; it is not an
independent global solution error estimate. `global_error_bound` remains null.
No new resolution-convergence campaign or performance benchmark was performed.
The observed campaign wall time, 3.5771041970001534 s, is execution telemetry
only and supports no speedup, scaling, or NCP claim.

## Physics and conventions

The source is collisionless, non-tilted LRS Bianchi I with photon and massless
neutrino energy/number multipoles through ell=8 and canonical positive massive
Vlasov cells. `source_lock()` fixes a_ref=1/21 and a_end=.2 (z=20 to 4).
Tcmb0=2.7255 K, nonbaryonic massive fraction=.1, mass/Tref=30, massive A=0,
24 radial × 12 angular cells, Gauss order3, and no electron donor are fixed.
The common initial radiation multiplier is k_gamma=k_nu=k.

For sigma=diag(-s,-s,2s), pi=diag(-p,-p,2p), and H in s^-1,

- signed S = sqrt(6) s/H;
- signed P = (8 pi G/c²) sqrt(6) p/H²;
- p is the **signed sum** of Pi_gamma_J_m3, Pi_nu_J_m3 and Pi_matter_J_m3;
- Frobenius norms Sigma_F=abs(S), Pi_F=abs(P);
- half-norm convention Sigma_half=Sigma_F/sqrt(2), Pi_half=Pi_F/sqrt(2).

The adapter calls the original initial_state unchanged. For each target S0 it
sets Sigma_ref=abs(S0)/sqrt(2) and orientation=sign(S0), then evaluates the actual
initial physical fields at k=0 and k=.5. The affine map determines k including
the tiny massive quadrature stress residual and the actual H0. Saved axes are
actual mapped inputs; solver values are never snapped to requested values.
The 9×9 signed grid is defined explicitly in `adapter.py`.

This is a two-dimensional source family, not an exhaustive tensor/stress-history
parameterization. Full H/He feedback, UV/stars and general triaxial dynamics are
outside this calculation; all inherited science HOLDs remain unchanged.

## Implementation and reuse

`adapter.py` creates one source-bound immutable species template per worker.
Each case uses `copy.copy` and changes only Sigma_ref, orientation, k_gamma,
k_nu and _nfev. Operators, Thomson coefficients and canonical momentum arrays
are shared read-only; each original initial_state creates an independent state.
The optional moment subclass caches 1-mu² and the minimum immutable cell
population, and evaluates `(r*q)**2` once for both momentum components. Every
remaining elementwise expression and summation order is the source expression.
The RHS, full state width, quadrature and DOP853 settings remain unchanged.

`runner.py` uses independent persistent multiprocessing-spawn workers. Threads
are set to1 before scientific imports. Each worker has a fixed CPU affinity.
Each case directory is created once, with a reservation, compressed full history,
and terminal result or raw failure. Good outputs survive failures elsewhere.
Aggregation is sorted by case ID.

`resources.py` intersects actual process affinity with visible cgroup-v2 cpus,
all visible ancestor quotas and memory limits. Admission counts the coordinator,
excludes CPU55, reserves max(1 GiB, 12.5% of effective memory), budgets 256 MiB
for the coordinator and512 MiB per worker, and caps using live available memory.
A bounded /proc/stat sample selects cores with observed load at most35%.
The actual run used coordinatorCPU0 and workersCPU1,2,3,4, under an eight-CPU
quota and8 GiB effective memory limit. Every acquired cooperative lease was
released; unrelated jobs were observed and left alone.

The configurable shared lease directory defaults to `/tmp/bass_cpu_leases`;
filenames are `cpu_N.lock`, compatible with C21K. Cooperating sessions must use
the **same directory**. These locks do not reserve CPUs against unmanaged jobs.
The repaired runner records `--execution-site {unspecified,sandbox,ncp,other}`
as an **operator declaration**, with observed hostname and platform. It does
not automatically attest a machine as NCP. Default site is unspecified and
`NCP_execution=null`; an explicit site sets that metadata consistently in
resource plans, case runtime records and summaries.

Resource-only ephemeral lock files outside this research unit were authorized
by the parent; all code, scientific evidence and run outputs stay in this unit.

## Files

- `adapter.py`: exact source adapter, initial mapping and full diagnostic histories.
- `runner.py`: create-only campaign, resource admission, persistent workers and CSV aggregation.
- `resources.py`: cgroup/load observations, admission arithmetic and CPU leases.
- `plotter.py`: saved-output-only four-branch figures.
- `focused_checks.py`, `checks/CHECKS.json`, `focused_checks.log`: seven actual focused checks.
- `checks/baseline_pair_*.npz`: complete paired raw baseline/reuse histories.
- `runs/pilot81/MANIFEST.json`: source/settings/executed-code identity.
- `runs/pilot81/cases/*/RESERVATION.json`: create-only case inputs and no-auto-retry declaration.
- `runs/pilot81/cases/*/RESULT.json`: actual mapping, endpoint, diagnostics, source identity and runtime.
- `runs/pilot81/cases/*/history.npz`: eta, complete Y, proper elapsed time, H, signed fields, both norm conventions, and all radiation moment/source diagnostics.
- `runs/pilot81/endpoints_*.csv`: 81 sorted endpoint rows.
- `runs/pilot81/RESOURCES_*.json`, `RETURN_*.json`, `SUMMARY_*.json`: resource observation, worker exits and completion accounting.
- `runs/pilot81/plots/initial_norms_final_Sigma_F.{png,pdf}`: color is final shear norm.
- `runs/pilot81/plots/initial_norms_final_Pi_F.{png,pdf}`: color is final stress norm.

Both figures have four signed-source branches on actual initial norm axes.
Zero-axis cases are explicitly shared in panels. Both PNGs were visually
inspected after generation; headings, axis definitions, color bars and points
rendered legibly.

## Commands

Run from this directory. NumPy, SciPy and Matplotlib are the only scientific
runtime dependencies; the delivered runtime used NumPy2.3.5, SciPy1.17.0 and
Matplotlib3.10.8.

```bash
python runner.py --plan-only --workers 4 --execution-site sandbox
python runner.py --out runs/new_sandbox_pilot --workers 4 --execution-site sandbox --timeout-seconds 600
python plotter.py runs/new_sandbox_pilot
```

The delivered `checks/`, `runs/pilot81/` and `plots/` already exist. The creation
commands intentionally refuse to overwrite them. Use a fresh output directory
for a separately authorized new campaign. Do not repeat a full campaign merely
for a plot or metadata update. The plotter consumes saved results only.

To continue a newly created v2 campaign with the same code, settings and declared site:

```bash
python runner.py --out runs/new_sandbox_pilot --workers 4 --execution-site sandbox --timeout-seconds 600 --resume
```

Resume requires the identical source, settings and executed adapter/runner/resource
manifest. Completed histories require their saved SHA256 and are reused.
New-format reservations explicitly record QUEUED. The worker durably writes a
STARTED marker before entering its physical solve. Missing cases and known
QUEUED/NOT_STARTED cases can resume; STARTED/INCOMPLETE and FAILED attempts
are preserved and **are not retried**. Old v1 reservations without the new queued
format remain INCOMPLETE if they have no terminal receipt.

The delivered old81-case campaign is read-only evidence under its archived v1
identity. Use the saved CSV, NPZ and figures to inspect it. If a v1 reaggregation
is specifically needed, the complete archived v1 tree can resume the old manifest:

```bash
python archived_execution_v1/runner.py --out runs/pilot81 --resume
```

That command would add only a new aggregation/return under the old identity
without solving a case; it was not run during the repair. The current v2 runner
intentionally cannot resume the old v1 manifest.
`--cpu-list` can further restrict admitted CPUs; it cannot enlarge actual limits.
`--workers 1` requests a single worker plus coordinator under the same admission
rules; execution-site metadata follows the explicit declaration. No remote availability is required.

For a future owner-authorized NCP run, request `--workers 63 --execution-site ncp`
with an explicitly selected fresh output directory. Admission still caps this
request to actual affinity, cgroups, quota, observed idle/leased CPUs and memory,
and includes the coordinator and CPU55 exclusion. A nominal64-CPU allowed set
including CPU55 can admit at most62 workers plus one coordinator. The default
remains4 requested workers; the NCP label alone does not increase parallelism.
New v2 filenames use actual UTC conversion and a Z suffix; archived v1 filenames
retain the original local timestamps. Teardown uses bounded global grace periods
in addition to the campaign computation deadline, so that deadline is not a
hard total wall-time debit cap.

## Verification actually performed

`python focused_checks.py` exited0 with all seven checks PASS:

1. All nine immutable source files matched size and SHA256.
2. Frobenius/half normalization and signed stress cancellation, including c² units.
3. Immutable template sharing and independent full state arrays.
4. Baseline-versus-reuse moment values were bitwise identical at four eta/b points.
5. All full history arrays were bitwise identical for three complete paired solves:
   (-.04,+.001), (0,0), and (+.02,-.00075), at the same frozen solver settings.
6. CPU55 exclusion, quota/coordinator and memory arithmetic, held-lease skip/release.
7. Missing/incomplete/completed/failed resume states, manifest mismatch rejection,
   and completed-history corruption detection.

`python runner.py --workers 4 --timeout-seconds 600` exited0 with81 complete cases.
`python plotter.py runs/pilot81` exited0 and plotted81 saved completed cases.
No old suite, remote mutation, Git mutation, global chemistry admission,
performance benchmark or NCP campaign was executed.

## Parent-authorized operational repair verification

`python repair_checks.py --out repair_checks_final` checks site metadata/manifest
separation and CPU planning, legacy/failed attempt preservation, and the actual
worker start/queued/restart path using an explicitly labeled solver test double.
It performs **zero physical ODE solves**. The control terminates one started
worker, preserves that attempt as INCOMPLETE, then starts a fresh real process
which completes only the known-unstarted queued case. Raw test receipts and
resource observations are in `repair_checks_final/`; the initial repair-check
pass is also retained in `repair_checks/`. No81-case rerun was made.
