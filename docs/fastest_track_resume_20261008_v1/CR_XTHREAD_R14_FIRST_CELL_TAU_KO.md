# CR-XTHREAD-R14: first-cell continuous Thomson-depth goal enclosure

2026-10-08 KST. **CONDITIONAL_FIRST_CELL_CONTINUOUS_TAU_GOAL_ENCLOSED__GLOBAL_TAU_AND_PHYSICS_HOLD**

## Actual new research, not a repeated root/IVP test

Inherited REI BRIDGE12 `9e1bad4daacbe9e313d34b1b645391b90b32b606` actual first cohort-cell `[0,46757316.98818144] proper seconds`, the **64 full-interval scaled RHS residual slices**, whole-prefix solution-error majorant, Picard invariant tube and Duhamel Jacobian coupling. Sealed donor ZIP SHA256 `526214a43badb06535f6f72d66503e5a7b6ea02fe7e1ec0952dcff4819d4ac05`, certificate SHA256 `ebbfc634a3d76def3d48acc860bdf85ee02e328c6171f0a0f5d545394c4fcec7`. Donor certification was not reissued. No birth or cutoff in this one cell.

R14 defines a *specific* optical surrogate: interpolate **native point gas fractions linearly in proper s=t/L**, while using exactly the same continuous density `nH=nH0 exp(-3Ht)` as the REI target. This is not the solver's dense output nor the discrete root-family interpolation. BASS/SYNC03 constants retained from R7: `C_T=c_SI*sigmaT_SI*1e6` for nH[cm^-3] and proper dt[s], D=1, `Xe=h+fHe*(y+2z)`, hence
```
tau=C_T*nH0*L*int_0^1 exp(-alpha*s)*Xe(s) ds, alpha=3HL.
e=z_true-z_hat; r=z_hat'-F(s,z_hat).
e(s)=-int_0^s r(u)du+int_0^s (F(z_true)-F(z_hat))(u)du.
W(u)=int_u^1 exp(-alpha*s)ds.
delta_tau=-C_T*nH0*L*int_0^1 W(u)*ce.r(u)du
          +C_T*nH0*L*int_0^1 W(u)*ce.[F(z_true)-F(z_hat)]du.
ce=(1,fHe,2*fHe,0,0).
```
Each 64-slice signed forcing is enclosed by exact-rational alternating fifth/sixth exp Taylor bounds; nonlinear contribution is bounded by the donor's full-tube `N*whole_prefix_error`. These have distinct provenance and are **not** the endpoint state error multiplied by an invented half-step factor.

The exact fraction `num/den` results, tests, 100-digit point check and SHA manifest are in the sealed ZIP. Safely loose displayed bounds:
- `tau_hat ~ 9.55355741648836e-11`, declared native-linear/dynamic-density surrogate;
- `1.8414e-20 < tau_cont-tau_hat < 1.8879e-20`, **positive**;
- `9.5535574183298e-11 < tau_cont < 9.5535574183763e-11`;
- nonlinear coupling remainder `<3.71256e-24`.
These are **conditional on the REI donor interval arithmetic and tube proof**, not a complete independently re-certified interval solver. The numerical comparison to a constant endpoint electron value differs by `~1.50173e-16` and is not the same target.

## Three other research threads kept separate

- HE E7 `a075c2513c18d5877d6d3596c81035128d38f9cb`: 1155 immutable rate/inventory endpoint records exported and opt-in consumer checked, but true Gamma/Ecal/continuous flow uncertainty absent. **Different Grackle low-T model**, not combined with this FT03 result or R13 native full point.
- HH Library ENERGY04: projected OFF/LCS endpoint families scoped, **two-source ON−OFF HII interval includes zero**; the correlated ENERGY05 tangent and actual global history are open. Git HH head unchanged does not imply Library work stalled.
- REI BRIDGE12 first-cell result is valid only for the declared 5D source target; BRIDGE13 must propagate **nonzero state error and accumulated tau error** across later cells and six birth jumps.

## Verification, files and preservation

New focused Python tests **8 PASS** (one initial missing-API ImportError recorded as expected RED, not assertion RED; seven later tests); 64 independent 100-digit kernel comparisons and sampled independent surrogate/forcing integral inside enclosures; four Python syntax checks; exact-rational proof sign. New native/IVP/root/old tests/atomic provider/receiver mutation: **0**. No independent proof assistant or external scientific reviewer. `CR_OFF_FASTEST`, precision atomic `PARKED`, HH research `ACTIVE`, physical production `HOLD`, G02 `UNRESOLVED`, all_bound `OPEN`, b_grid `NO_GO`, capture=false, owner ACK/global CR counter/observer tail=null.

Source core actually added:
`research/fastest_rejoin_20261008/optical_goal/optical_goal.py`
Git blob `a4e281f4b01cddd56bdfa9884c2a99b536ea9d46`, local SHA256 `9160019f39846e91a124c57042cf6352cbb5123dfb2209e7b932d376ab857321`. Full tests, donor selection, reports, exact results and `reproduce.py` live only in immutable ZIP `BASS_CR_XTHREAD_R14_20261008_v1.zip`, **196226 bytes, SHA256 afac64fea33ac53dd4aac537a80cfc4e7917bb1447057aef67803afcca9d0f36**. Google Drive object `1BbBKSkC2ObFzieIpb3qqoRh4pfJ9APdS`, Dropbox object `id:BSpOijBcT10AAAAAAD3c3Q`, R1 UPLOAD_VERIFIED by ACK+name+size+path, NOT RESTORE_VERIFIED. Extra Drive text source object `1RmFfsgBejy1vUPKv7bPdrCIuMz3X5sOx` was used only to publish exact core bytes.

Next: consume REI BRIDGE13 same-family birth-aware continuation, do NOT propagate this first-cell scalar by resetting error or invent time-jump data.