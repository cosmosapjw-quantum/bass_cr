# BASS-CR → REI F05: original excitation-cooling partition, scientific result

2026-11-01 KST. One source-native, nonproduction IGM physics unit stacked on immutable BASS-CR PR161 head `a555eeb75eae79a5b05ee9054323c3ce06e3075d`. Original REI owner PR356 `cc1929982948265f6d0b0f699353b3170ccd1792`. Official REI accepted source tick is **160/131072**; 161 is **NONAUTHORITATIVE PREVIEW**. Main/owner/worker/production paths are not mutated. REI central 28/88, working 33/88 and BASS-CR extension 0/3 all unchanged.

## Physical error averted

The original REI F05 `reduced_interval_rhs.py` SHA256 `b1f3d6d6397ff727b756816165652a44eb373055256adf7af2e7ef6304ed9b36` includes H I excitation cooling `n_e*n_HI*7.5e-19*exp(-118348/T)/(1+sqrt(T/1e5))`, with coefficient in erg cm^3 s^-1. The published electron-H I(1s→2p) rate in parent PR161 is therefore **not an additive new thermal sink**. Moreover substituting only 2p for the whole original multi-channel phenomenological coefficient would erase a positive residual channel. The physically justified result is a source-matched **decomposition/diagnostic**, no source patch.

## Actual original source physical calculation

Private original source: original F05 46,080×27 record `ORIGINAL_REI_F05_TICK161_HHE_T_ELECTRON_PREVIEW_46080.csv.gz` SHA256 `713b46a0da8931cc6f5a355912cdd2efa790945c2539ad049c086fd995f3441d`. Uses accepted tick160 H/He/e/T fields, and the original READ-ONLY owner SHA-locked module to obtain proper native cell volumes and exact microtick `dt=4871848749.16828` s. Input parent PR161 12,528-node derived original source SHA256 `09c564df9400b171617ce5006b2c7eee94085f8d321f8d41648fc9456cbd1628`. Supported temperature 5000–20000 K, excluded 14,832 cold and 18,720 hot original cells; no extrapolation and NO full 46k total.

At fixed original source cell, with `n_e=N_e/V`, `N_HI=N_H(1-x_HII)`, `K=N_HI*n_e`:
- `P_old=K*Lambda_H_legacy(T)`
- `P_2p=K*E12*q12(T)`, where `q12(T)` uses original parent Scholz/Pradhan effective collision strength four knots with piecewise linear interpolation, `Te=Tgas`, `f1s=1` saturation
- `P_residual=P_old-P_2p>0` on supported nodes. THIS IS A PHENOMENOLOGICAL REMAINDER, not measured 2s/higher excitation, verified multilevel kinetics or detected escaped Ly-alpha.

| One original-support-domain physical quantity | Actual computed result |
|---|---:|
| Supported source cells | 12528/46080 |
| Original H excitation cooling, erg/s | 1.4642738832064828e38 |
| Corresponding conditional 1s→2p energy sink, erg/s | 8.216438058687765e37 |
| Unassigned original H excitation-model residual, erg/s | 6.426300773377064e37 |
| Integrated 2p / original excitation-model ratio | 0.5611271329032599 |
| Nodewise 2p/legacy ratio min, median, max | 0.56068794320782; 0.5890122444516253; 0.675990262443924 |
| Native 2p original PR161 rate crosswalk max relative error | 4.440892098500626e-16 |
| Source supported ideal bath U, erg | 2.7486360671295096e55 |
| Frozen 2p first-order response ε_j max | 1.0799605733753442e-5 |
| Robust ε2p_low > maximum absolute original t160→161 preview delta_lnT | 120 nodes |
| Robust ε2p_low > 0.1 * maximum absolute original preview delta_lnT | 1776 nodes |
| Midpoint ε2p_mid > absolute original preview midpoint delta_lnT | 180 nodes |

The last screening is an **already-in-model** channel's materiality, not a missing energy term. It compares a one-freeze instantaneous first-order estimate with the original **unaccepted** tick161 preview. Source intervals are NOT atomic-model uncertainty bounds. No true time-dependent integration, local radiation escape, 2p population, actual optical depth, CMB signal, CR-ON or original solver change is claimed.

New output: `ORIGINAL_REI_F05_2P_LEGACY_COOLING_PARTITION_12528.csv.gz`; source-origin, thermal interval, legacy power, 2p power, residual and robust materiality flags, one row for each original cell. Separate `RESULT.json` carries numerical and preservation identities.

## R/C research-loop completion evidence and adversarial audit

R1–R3 direct original source/thermal operator audit; R4–R5 analytical decomposition and energy identity; R6–R7 reject naive double counting and full-legacy substitution; R8–R10 checked Wolfram four-knot ratios and published immutable theory checkpoint `31feb2c1cae932a335aae93d2d4a628cf76b9182`, local source-free archive SHA `7a2568799c7111f7e58b2685543f944b06413c3ab20ddfb4a3fc12f9e6e53d00`.

C1–C5 source-bound original input and 12528-node implementation; C6–C9 direct source conservation, root/interval checks, identity crosswalk, numerical checks and **16/16 standard + 16/16 -O unittest PASS** on local host (after original source was loaded). C10: final archive and GitHub Draft receipts must be checked from actual terminal/GitHub output, not inferred. No separate native subagent or distinct-author blind referee: NOT_RUN. Same-author hostile math/source review FOUND AND REPAIRED initial naive-addition conceptual defect by choosing partition-only science.

Runtime warning: import of existing original source `pandas` can print NumPy1-compiled `numexpr`/`bottleneck` ABI compatibility messages under installed NumPy2.4.2; actual command and 16/16 tests still exited 0. Does not certify the original owner solver/runtime, and no runtime packages were changed.

Mission watchdog: this study identified a real overlap that prevents inaccurate new physics, and produced a reproducible original-source 12,528-node partition. **STOP** neighboring optional fit/opacity/atlas iteration. Central next action: original REI F05 owner source clock/14-ledger parity and versioned tick161 admission; independently RUX02/RUX03 photon/geometry source identity. Any practical replacement of legacy excited-state closure requires source-owner validation for ALL contributing channels and atomic uncertainty. No auto-next, REI main merge, force-push, production change or canonical DAG promotion.

Primary atomic references: Scholz et al. (1990), MNRAS 242,692 DOI 10.1093/mnras/242.4.692, published Pradhan effective-collision-strength table four knots. The empirical legacy coefficient is original REI code, SHA given above, not assumed identical to a particular 2p channel.
