# REI F05 accepted history: exact discrete MPRK HII↔HI transfer budget

2026-11-02 KST. BASS-CR supplier-only, immutable parent PR165 exact `48fde990177fba08a09e70de20e3218e5303fb36`. Original REI owner #355 exact `70bb906fcfd6b7c5b0f4c356f44c03ad7164ff00`, sealed 26-event kernel `579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644`. Original accepted parent states ticks 0,64,128,160 read from REC195 SHA-locked archive `ed08c131cb61b8cb5c5a52a8dadeb4fc7350945eefc5c2e1c1bf12c1a2052657`. Original `[160,161]` V2 is still research-only and not official. No source/worker/main/history/CR-ON alteration. Central REI 28/88, working 33/88, Physical Fast 4/7, BASS-CR extension 0/3, all Δ0.

## R1–R3: physical purpose and original algorithm identity

BASS-CR PR165 ran 9 exact original MPRK22(1)+Alexander SDIRK2 maps and computed 0→160 total H Case-B *stage-flux quadrature* [2.5410387807979653e62,2.766237241157955e62]. This is **not equal by design** to the positivity-corrected discrete MPRK chemical transfer ledger. Source quadrature of HII ionization minus HII recombination disagreed with accepted HII state delta for 336/46,080 cells on [0,64], with local positive gap sum 9.640425779725532e54 particles (1.084858508048765e-7 of total abs HII change). The objective is to construct and numerically evaluate the *actual weighted MPRK transfers*, not to enlarge acceptance tolerances or produce a new H emission atlas.

Actual original file `stages/...CROSS_SITE_STATE_FEEDBACK_REMAINDER_AND_TABLE_EVENT_LOCK/analysis/interval_discrete_map.py` has original H/He transfer map:
- `pred=population_step(parent,e0.flux,parent,dt)` at original source t0;
- original predictor gas root `pr=thermal_root(thermal_context(pred,e0.photo_heat),U0,dt,0,1,...)`;
- `e1=event_box(pred,exp(pr.log_temperature),t1)`, positive offdiagonal 5×5 source flux;
- `fbar=average_flux(e0.flux,e1.flux)`;
- `corr=population_step(parent,fbar,pred,dt)`, with H/He nuclei invariants.
Do NOT substitute `StepResult.stage_event/final_event` into this chemical corrector. Those are *thermal SDIRK* source sites eg/ef, not e0/e1 used by the MPRK chemical step. This distinction is the source of the PR165 336-cell discrepancy.

Reference algorithms: Burchard, Deleersnijder & Meister (2003), `doi:10.1016/S0168-9274(03)00101-6`; Kopecz & Meister (2018) `doi:10.1016/j.apnum.2017.09.004`. Primary reference general positive conservative MPRK, but the **specific formulas below are directly derived from this REI source implementation**.

## R4–R5: constructive exact *discrete* chemistry identity

Let `F_{ij} = (F^0_{ij}+F^1_{ij})/2 ≥0`, `i=destination, j=source` with native extensive units s^-1, `D_j=y_j^pred>0` original predictor population, and `X_j=y_j^corr≥0` the positivity-corrected population. For each *source-native half step* of proper duration `h` original MPRK matrix satisfies

`(A X)_i = y_i^parent` with `A_{ij}=-h F_{ij}/D_j` for `i≠j` and `A_{jj}=1+h sum_{k≠j}F_{kj}/D_j`.

Define **numerical transfer counts**
`T_{i←j}^MPRK = h F_{ij} X_j / D_j` (nonnegative, dimensionless number of particles).
Then EXACT algebraic matrix identity:
`X_i−y_i^parent = sum_{j≠i}(T_{i←j}^MPRK−T_{j←i}^MPRK)`.
For H two species `HI=0,HII=1` original independent nuclear block:
`T_R = T_{0←1}`, `T_I=T_{1←0}`, `ΔN_HII=T_I−T_R` EXACT for the implicit matrix, not the source thermal stage quadrature.
Setting `u=h F_{1,0}/D_HI`, `v=h F_{0,1}/D_HII`, `H=N_HI+N_HII`, `Y=y_HII^parent`, the 2x2 closed-form HII solution is
`X_HII=(Y+u H)/(1+u+v)`; `T_R=v X_HII`; `T_I=u(H−X_HII)`.
Wolfram explicitly reduced `X_HII−Y−T_I+T_R` to **0**; this identity should be numerically checked independently on original 46,080 cells.

If source flux, predictor and corrector are intervals, positive interval products
`h × [Flo,Fhi] × ([Xlo,Xhi]/[Dlo,Dhi])`
give conservative **numerical interval enclosures** of transfer count. The x and denominator intervals are correlated: intervals may be wider than exact interval solution. The *two half* MPRK transfer is sum of two original half-step counts. H/He nuclear conservation in original positive cone and no different absolute flow ownership are preserved.

## R6–R9: expected adversarial discrimination

Direct target: source-state 46,080-cell `[0,64],[64,128],[128,160]` MPRK weighted transfer `T_R,T_I` with source input clocks/hashes and output original terminal REIADP1 byte parity, original 3-map/full/half/half certification, original 14/14 signed energy/nucleus/photon ledgers. Reconstruct e0, predictor populations+thermal pr, e1 and Fbar exactly from unchanged original owner module, reconstruct corrector, and compare to native `StepResult.population` and original accepted endpoint array (exact or sound numeric interval identity as required).

Compare the MPRK transfer `T_I−T_R` with original accepted `ΔN_HII` per cell, recording nonoverlaps **without** relaxing published original 2e-4 / 2e-3 gates. Conditional parent #164 endpoint H-recombination lower remains a separate *continuous-model-conditional* bound and is NOT a mathematically required lower bound for the numerical MPRK flow without a continuum enclosure theorem.

Unlike PR165 **thermal SDIRK stage-flux quadrature**, this is a discrete map's own transfer ledger. Both may give different nonnegative gross H Case-B counts. Physical interpretation: positivity-preserving discretization accounting, not exact continuum chemical reaction integral. `χ_H × T_R` is a numerical gross H binding-energy-channel equivalent, NOT new gas heat, 10.2-eV Lyα count, escaping photons or observational flux. He-OTS and preexisting H cooling unchanged. Assumptions: original source continuously H/He positive, source t and proper local input exact, original 46,080 cells and 3 accepted intervals only.

A failed comparison from original floating point outward enclosures should be classified separately as `DISCRETE_NUMERICAL_ENCLOSURE_LIMIT`; incorrect e0/e1 site `IMPLEMENTATION_ERROR`; source-head mismatch `PROVENANCE_BLOCKER`; genuine loss of source/chemistry identity `PHYSICS_OR_OPERATOR_ERROR`. If a material blocker persists, checkpoint negative evidence rather than guessing flux weights.

## R10: objective, evidence and next step

One R source derivation + one C original-data computation. At each R/C stage: preservation and physical DAG snapshot **REI 28/88, working 33/88, Fast 4/7, CR 0/3 (Δ0)**. Preserve source private arrays and original runtime. Source-free Git public 3-interval summary and exact code/test; source-inclusive private provenance only in preexisting authorized provider archives, not public Git. If output passes self-adversarial source review, push independent Draft/HOLD stacked on PR165; no merge, no force push, no original REI mutation. Native subagent NOT_RUN if no callable delegate. Next central path remains original REI source-clock/continuum error and official tick161 decision, then Bianchi photon transport RUX02/RUX03. STOP repeating optional atomic-data/cooling/opacity table PRs.
