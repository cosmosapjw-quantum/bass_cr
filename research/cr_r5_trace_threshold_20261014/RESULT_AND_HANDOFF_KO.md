# BASS_CR R5: continuum signed tail trace, flux lift and native AXBI threshold experiment

2026-10-14 KST. Actual parent PR63 head `6da1d99643660974a48da3677658a4a37b6f5392`. Selected next construction under `NT_CONTINUOUS_RADIAL_ADJOINT_BOUNDARY`, plus scoped source support for separate `rei_bianchi`. User's completed historical Coulomb source and its valid coarse continuum certificate are unchanged.

## 1. True continuum signed time-weak boundary flux (new derived result)

Under parent's SAME homogeneous isotropic full nonlinear electron-electron Coulomb Landau problem with nonnegative four-labelled C/P/S/A classical solution, natural infinity flux and exponential tail bound, let `N_R(t)=sum_a int_R^infinity F_a(W,t)dW`. The continuity law gives `N_R'(t)=j(R,t)`. For every C1 time test `phi`:

```
int_0^T phi(t) j(R,t) dt
  = phi(T) N_R(T) - phi(0) N_R(0) - int_0^T phi'(t) N_R(t) dt.
```

At `phi=1`, positivity and parent's `0<=N_R(t)<=B_R` yield the rigorous signed count interval `[-N_R(0), B_R-N_R(0)]`. Input exact Gaussian-tail initial count was outward enclosed via 90-digit interval arithmetic and an alternating erfc integration-by-parts enclosure, not just old Maxwell extrapolation.

| R | signed integrated continuum boundary flux, count, outward displayed |
|---|---|
| `40 theta_P0 = 798.661651... eV` | `[-3.069278e-17, 2.841405e-15]` |
| `60 theta_P0 = 1197.992477... eV` | `[-7.716791e-26, 1.601468e-23]` |

**Important distinction:** this is a weak signed boundary trace, NOT `int |j|dt` or the reflecting finite-grid true-error estimate. A positive oscillating tail count `B(1+sin(2pi*m*t/T))/2` has arbitrarily large absolute variation while `N<=B`, showing that tail mass alone cannot control absolute flux without an additional regularity/dissipation bound. It is a general logical counterexample, not a constructed Landau solution. The previous coarse true continuum cold-origin temperature interval remains `[101.30796502966,101.40851150782]K`; the physical microkelvin shape correction is still unresolved.

## 2. Continuous affine finite-volume face-flux lift

For the unchanged saved 2048-cell four-labelled nonlinear Landau path, evaluate the ORIGINAL positive logmean semidiscrete face flux `J_i(n_hat(t))` using each saved dyadic path. On every spatial energy cell, interpolate *fluxes* linearly between its actual left/right face values. This reconstructed spatial flux is continuous at faces and obeys

```
dt F_hat + d_W(j_hat/t_unit)
  = [dn_i/dt + (J_right-J_left)/t_unit]/width_i,
  t_unit=theta_C0^(3/2)/K.
```

The original 20 whole-slab cut residuals remain valid and now have an explicit continuous spatial flux-lift representation. New four saved-state checks reproduce the exact parent compiled Numba RHS algebra, with face-cut telescoping residual<3e-24count/s, pair-energy cancellation ~1e-28eV/s. These are double-precision spot checks, not directed full PDE residual bounds. Since piecewise-constant `F_hat` jumps at faces, the continuous nonlinear Landau constitutive defect `j_L(F_hat)-j_hat` and the adjoint/boundary remainder are **OPEN**. The affine flux lift does not by itself certify a smooth positive physical-density reconstruction.

## 3. Independent actual native Rust source-control and candidate

The current `rei_bianchi` Rust source files were read and pinned: `axbi_driver.rs` SHA92bc6..., `axbi_sources.rs` SHA606e3..., `atomic_provider.rs` SHAb0b572... . An isolated `rustc` executable linked against the actual existing `librei_microphysics-2db3552c92b16edc.rlib` (SHA7c7a...) and called `AxbiSource::new` plus `AtomicProvider::reference().cross_section` over 16,32,64,128 spectral subdivisions. It did not launch any AXBI history.

The original number+energy-conserving two-node photon deposit maps below-threshold photons partly onto the HeI/HeII active threshold nodes, yielding the following relative errors **only for injected source-weighted cross-sections compared to continuous blackbody×Verner integration**:

| n/source segment | baseline HeI | candidate chi-side-tag HeI | baseline HeII | candidate chi-side-tag HeII |
|---:|---:|---:|---:|---:|
| 16 | +10.408540% | +0.074287% | +38.594120% | +0.117109% |
| 32 | +5.117104% | +0.018581% | +17.829887% | +0.029395% |
| 64 | +2.536692% | +0.004646% | +8.572902% | +0.007356% |

The proposed `chi^-`/ `chi^+` tagging preserves positive number and first-energy moment while separating absorber-inactive/active threshold sides. On n16 the candidate improvement factors are ~140.1(HeI) and ~329.6(HeII), **not** improvement factors in full abundance history. The actual native arithmetic and independent Python source port agree within max relative `1.825e-13`. This tagged adapter remains a PROPOSED separate-source model, not a production replacement.

The physical source-weighted direct **excess heating** `sigma(E)*(E-chi)_+` is different: the *original* n16 projection errors are HI -0.178912%, HeI -0.369935%, HeII -0.805740%. False species absorptions at exactly chi have zero direct excess heat, while their downstream chemistry/binding effects are unknown. Exact photon number/energy conservation therefore does not imply accurate absorption/species assignment.

## 4. Live separate-Codex execution and status

The actual authorized local `rei_bianchi` worktree, not just Git metadata, was read. The originally queued `SHEAR_HALF_MINUS` returned 2026-10-14 22:57:57 KST with `STOPPED_CHECKPOINTED`, accepted200000, RHS4200402, wall6300.257s, `AXBI_RUNTIME_CAP`. This is a resource stop, not a demonstrated physics failure. The existing epoch recovery receipt reports `COMPLETED_EPOCH_RECOVERY`. After an initial PLUS dispatch HOLD, the owner's distinct recovery launcher had an observed `SHEAR_PLUS` resource continuation running under its exact prior allocation. No duplicate start or process action by this supplier. Original ZERO z20→4 remains conditional scoped complete; AX08 signed family pending, AX11/12 runs pending; current STATE can lag actual RETURN and must be re-read by owner.

**Owner action:** one small source-specific native threshold side/energy/absorber and heating-ledger test before considering a new source ID and a separately reviewed matched history. No silent modifications to current source, original signed histories, accepted output/checkpoint identities or scheduler; no AX11/12 READY claim here. Physical CR/RCT/HH remain OFF in current REI plan.

## 5. Evidence and preserving the next step

Wolfram Language15.0.1: 8 corrected scalar zero residuals + unsatisfiable inactive-support convex-hull counterexample. Actual xAct/xTensor1.3.0: final 6 literal tensor zeros with exact upstream xCore/xPerm/xTensor SHA pins. First xTensor call did not algebraically normalize three scalar rational weights, fixed by exact `Together` in an explicit targeted recheck; original observation preserved. New finite-grid/trace/source/heat 15 targeted tests passed; relocated archive manifest checker and same15 tests passed. Native Rust source probe ran and produced recorded stdout; no full old scientific IVP, native REI history, external independent review or host subagents.

Entire proof, exact tail bounds, native stdout, source-only input and heat comparisons, tests, CAS scope, handoff and prior pinned kinetic NPZ are in the frozen archive. [Google Drive source archive](https://drive.google.com/file/d/1maOxNoiK3hSRRKsYNe7RU3Qb9DtmbcQe/view?usp=drivesdk), Dropbox file `id:BSpOijBcT10AAAAAAD7J7A`: same 1,350,111bytes, SHA256 `ed9aeae9615175abddf20f98042d99da1893f33014168f2fd851ed1732200c47`, 31 members/30 SHA payloads, local CRC/relocated tests PASS. Remote R1 provider ACK/name/ID/size/parent only, not remote byte restoration. No original overwrite or permissions change.

**Next node** `NT_CONTINUOUS_RADIAL_CONSTITUTIVE_ADJOINT`: use the positive count-energy moments, continuous affine face flux and existing signed boundary trace to construct a smooth physically admissible density, quantify `j_L(F_h)-j_lift`, control time/space/truncation and adjoint response, and then sharpen the currently coarse continuum temperature error. Separately `CR_REI_THRESHOLD_OWNER_REVIEW_AND_INDEPENDENT_LEDGER_TEST` is ready for a focused owner test, not automatically a change to the external DAG.
