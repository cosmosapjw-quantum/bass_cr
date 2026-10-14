# BASS_CR: 2048-cell weak cut residual and rei_bianchi Verner threshold projection

2026-10-14 KST. Selected `SHARP_SAVED_KINETIC_WEAK_RESIDUAL_AND_BOUNDARY_TRACE` (R5 continuation) from parent PR62 head `aa2705dc3e35a03920e2cd5e7efc32ef9fe43c77`, plus nonblocking actual-source support for `rei_bianchi`. This is **not** a new continuum microkelvin Landau certificate or full REI history calculation. No parent source, completed kinetic IVP, live REI process, owner checkout, permission or admission gate was changed.

## New finite-grid kinetic weak defect

Reused the saved labelled C/P/S/A 2048-cell radial Landau path, 21 immutable binary64 states on `0..100000` proper seconds. No new kinetic solver run. All four reciprocal and tail-tail collision terms remain. Fix `q=20 theta_C0=0.17424655306669512 eV`, which lies between energy **centres** 850/851; the corresponding finite-volume face is 850.

For `n_i'=J_(i-1)-J_i`, each label has exact discrete weak identity

```
d/dt sum_{i<851} n_ai = -J_a,850 / t_unit,
t_unit=theta_C0^(3/2)/K.
r_cut,a(t) = [N_a,<851^(k+1)-N_a,<851^k]/5000s
             + J_a,850(n_hat(t))/t_unit
n_hat=(1-v)n^k+v n^(k+1), 0<=v<=1.
```

The symmetric positive logarithmic-mean mobility and the positive, piecewise-separable Landau interaction kernel give a **whole-slab** flux enclosure from interval bounds on every saved endpoint component. All 20 time slabs were enclosed using `mpmath.iv` 55 dps on the finite-grid exact-real model with saved dyadic inputs. Summed `int_0^100000 |r_cut,a|dt` upper bounds:

| label | absolute residual bound, count |
|---|---:|
| C | 9.174024299756161e-12 |
| P | 3.181179868937600e-9 |
| S | 4.130436276729609e-7 |
| A | 1.765483713798265e-9 |

These bound the **saved piecewise-linear reconstruction defect versus its finite-volume ODE**. They are not forward errors of the finite-grid IVP and do not close a continuum PDE spatial, boundary or adjoint estimate. Prior PR62 source-specific coarse continuum `T_C(1e5s) in [101.30796502966,101.40851150782] K` remains valid within its assumptions; the ~-7.69 microK shape correction is still unresolved in a sharp continuum interval.

## Reproduced REI source-stage threshold leakage

Read the actual remote Rust files `axbi_sources.rs`, `axbi_driver.rs` and `atomic_provider.rs`, pinned by SHA256 in the immutable archive CONTRACT. The sources use 50,000 K truncated stellar blackbody, 16 log-cells per `[13.60,24.59,54.42,100]` segment, 49 receiver energy nodes, a two-neighbor positive count/first-energy conservative deposit, and Verner opacity that is **zero below** each species fit threshold and **positive at** that threshold.

If `E_-<E_src<chi` is below threshold but is deposited between `E_-` and `chi`, the receiver sees

```
sigma_eff(E_src)=(E_src-E_-)/(chi-E_-) * sigma(chi)>0,
sigma_true(E_src)=0.
```

Independent source-formula port and SciPy continuum source integral give relative **source-weighted cross-section** biases, *not history abundance or optical-depth errors*:

| n per source segment | H I | He I | He II |
|---:|---:|---:|---:|
| 16 | +0.119254% | +10.408540% | +38.594120% |
| 32 | +0.029825% | +5.117104% | +17.829887% |
| 64 | +0.007457% | +2.536692% | +8.572902% |

At n16, below-threshold false absorber weighting contributes respectively 0, 10.334253 and 38.477011 **percentage points relative to the corresponding continuous source-weighted result**. These are non-native Python component diagnostics; the full Rust history and physical chemistry errors remain UNKNOWN.

**Convex-hull obstruction:** if all absorption-inactive nodes are `<=E_-<E_src`, no positive count-one measure on those nodes can reproduce mean `E_src`. An illustrative one-sided `chi^-` (inactive)/`chi^+` (eligible) tagged split restores count, energy and target-threshold ownership. It is **only a model construction**; before adoption each species threshold, repeated redshift projection, output cadence/budget, species rate and heat ledgers must be jointly considered.

Within the frozen signed shear family `|Sigma|<=0.01`, `dln(a)<=0.005`, photon energy monotonically redshifts and each step moves less than the smallest log-node gap `0.03701688`. Hence a generic plus/minus `|q|` grid-crossing cusp on each step is **not** established. Independent continuous `P_2` monopole cancellation holds in the differentiable isotropic limit, not as a claim about the fully adaptive nonlinear implementation.

## Actual REI development and nonblocking support

The separate Codex owner advanced well beyond prior public PR snapshots. The actual Desktop on 2026-10-14 22:38 KST was read: AX07 conditional ZERO full z=20→4 completed; AX08 signed family in progress; AX11 T1 and AX12 variants prepared but their result runs PENDING. `post_cap_epoch_recovery.py` and original `SHEAR_HALF_MINUS` solver were running. Live historical runs, binaries, tracked owner files and shared scheduler were not modified, killed, relaunched or marked admitted by this work.

**Suggested owner action:** one short, standalone *native source* regression to confirm the Python port, followed by a physics-aware decision whether to run a separate threshold-side/refined-source control. Do not silently modify accepted source lock, historical raw results, current solver or AX11/AX12 owner readiness. CR fine kinetic/physical tau are nonblocking for the existing CR-OFF goal.

The full owner handoff `integration/REI_OWNER_HANDOFF_KO.md` and 12 passing component tests are in the source ZIP. `R5` status: **weak semidiscrete cut defect done; full continuum fine temperature and boundary/adjoint remains OPEN**. REI supplier status: `READY_FOR_OWNER_REVIEW_AND_SCOPED_TEST`, not owner science PASS.

## Actual verification and backup

- Corrected Wolfram Language 15.0.1 call: 8 scalar zero identities and unsatisfiable convex-hull witness. Prior input precedence failure preserved as an input issue.
- Actual xAct/xTensor 1.3.0: 6 tensor zero residuals, direct official `.m` SHA pins matched.
- Python: 12 tests passed, nine independent source-sigma cells re-evaluated and matched stored source-sigma JSON. All 20 saved weak slabs already bounded at 55dps; final ZIP relocated verifier exit0 with all27 payloads and 12 tests.
- Native Rust source regression/old kinetic IVP/full REI history/HPC/external independent science review/native subagents: NOT_RUN.
- [Full report, code, test, saved parent kinetic evidence and CAS contracts ZIP](https://drive.google.com/file/d/1Ayfi_xx62RhXKMvWJF-HhNEiKzL5KTzZ/view?usp=drivesdk): **1,424,921 bytes**, 28 members/27 manifest payloads, SHA256 `6ff9634f6673741bcf8d9f59804de4a2200c217b4625fb4a39d4b43f6d437e62`.
- Dropbox: `/BASS_DERIVATION_DOSSIERS_20260912/BASS_CR_WEAK_FRONT_REI_SUPPORT_20261014_SOURCE.zip`, completed file ID `id:BSpOijBcT10AAAAAAD6bIQ`, same 1,424,921 bytes. Local CRC/relocated full payload verification; remote **R1 ACK/ID/name/size/parent**, not remote full restore. No overwrite.

Next within bass_cr: continuous C1 radial flux reconstruction and whole-band boundary/adjoint/stability estimate. Parallel external handoff: one owner-reviewed native source regression and optional separate-source scientific decision. Preserve original atomic/F/G/b-grid/global REI and CR/RCT/HH OFF scopes.