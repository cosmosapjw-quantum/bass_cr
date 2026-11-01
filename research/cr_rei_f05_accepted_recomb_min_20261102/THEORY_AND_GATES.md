# REI F05 historically accepted HII states imply a minimum Case-B recombination budget

2026-11-02 | PhysMath theory R1–R10, original BASS-CR science supplier. Immutable branch parent PR163 `b5001472fa96ec7ba511e989948d826df3d12ab3`. Original source and parent never mutated. Central REI **28/88**, working **33/88**, physical fast **4/7**, BASS-CR extension **0/3**, all delta zero.

## R1–R3 Original question, data, conventions
Can the ORIGINAL accepted 26-event REI F05 states at ticks 0,64,128,160 constrain the cumulative H Case-B recombination events, *without claiming a manufactured within-interval Ly-alpha line field*? This source-integrated constraint differs from the parent PR160 instantaneous Case-B rate and PR161–163 optional atomic cooling fits.

Exact source SHA locks:
- Original 26-event H/He/OTS RHS `reduced_interval_rhs.py`: `b1f3d6d6397ff727b756816165652a44eb373055256adf7af2e7ef6304ed9b36`.
- Original source TAR: `a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b`.
- Initial 46,080-cell NPZ `7855f8b5c072da7860e5b0404a5548114ef46a8713840d99e4efa1b009905d2d`.
- Primary original REIADP1 state tick64 `aae4607ec1f0eff6669f1c1cb716ec6d6a4af8b789bba14abcd17f1733f83425`, tick128 `bbb349102194c86fb39a720a6695d9cb5845782b154da3448a433959fcc7f6a6`, tick160 `74c7cbb784c3a6fe25e53307f678ef23ab87263f56b314fbaa3ef696433d05f6`. REI owner #365 all-lane first64 and REC #195 historical accepted 64→160 are sources of this exact physical record, not independent 3-sky realizations.
- Original microtick proper duration `dt=4.87184874916828e9 s`. `χ_H = 13.598434599702 eV`, `1 eV=1.602176634e-12 erg`. Extensive HII particle counts, not densities. Signature (-,+,+,+).

## R4–R5 Constructive mathematical bound
Original source `dN_HII,j/dt = I_j(t)-R_j(t)`, where `R_j=N_HII,j*(N_e,j/V_j)*α_B,H(T_j) >= 0` and nonnegative `I_j = r_hi + y r_he2g + P_EXC r_he2b + p_h54 r_he3g + r_he3n2 + A_H r_he3cas >=0` in the physically admissible source cone with nonnegative rates/branches. The original `P_EXC=0.96`. Integrating a **model-consistent continuous trajectory** gives `∫R_j dt = N_j(a)-N_j(b)+∫I_j dt`. With proper lower/upper endpoint enclosures `N_j(a)∈[L_ja,U_ja]`, `N_j(b)∈[L_jb,U_jb]`, define
`R_min,j(a,b)=max(0,L_ja-U_jb)`.
Then `∫_a^b R_j dt >= R_min,j(a,b)` conditional on the true model trajectory and valid endpoint bounds. A global weaker check uses `max(0,sum_j L_ja-sum_j U_jb)`. The source-supported minimum *gross recombination chemical binding release* is `E_min = χ_H * (1.602176634e-12 erg/eV) * sum_j R_min,j`, not thermal heat, observed photon radiation, or net change in total H/He chemical storage.

## R6–R7 Actual 46,080-cell source checks and counterexamples
Direct original SHA-locked source reader produced preliminary 3 accepted-interval **conditional lower bounds**:
| proper ticks | min recombinations events | corresponding min gross H binding release erg | cells with certified HII decline |
|--|--:|--:|--:|
| 0–64 | 8.879746299967944e61 | 1.9346386888413227e51 | 42474 |
| 64–128 | 8.835204102163904e61 | 1.9249342382583115e51 | 42534 |
| 128–160 | 4.381986121562682e61 | 9.547074430236262e50 | 42522 |

**Self-hostile checks:** H ionization includes He-derived OTS and must not be set zero; therefore the net decrement is only a *necessary lower bound*, not exact events. Given any allowed end-to-end history, an equal nonnegative cycle of ionization and recombination `I→I+k(t), R→R+k(t)` leaves endpoints fixed while increasing `∫R` arbitrarily. Consequently endpoints give NO finite upper bound on recombination or Ly-alpha output. This is a specific construction, not a global strong no-go about the original kinetic system. The original source's exact time evolution fixes rates, but this study does NOT re-integrate its 26-event stage histories.

More critically: accepted REIADP1 endpoint intervals enclose **discrete numerical states**, not necessarily exact continuum ODE states. Numerical model admission requires continuum error/source-clock transfer evidence before interpreting this as a certified physical reaction-count bound. Even with correct ODE integration, Ly-alpha branching P_B(T), time history of T, 2s vs 2p level populations, line trapping and escape are unowned. **Do NOT call the number E_min/(hν_Lya) emitted or escaped photons.** The output contributes a conditional chemical event-budget constraint to eventual RUX02/03, not accepted photon source, ray, CMB or CR-on injection.

## R8–R10 Scientific decision and exact code/repro contract
Develop one source-native, strictly scoped **model-conditional accepted-history event-budget lower certificate**, not another optional time-atlas, fit or simulated light curve. Verify original NPZ and 3 full REIADP1 state byte hashes, independent magic/header/shape and original H-nucleus consistency; compute per-cell and global lower envelopes for three actual accepted intervals; negative corruption tests; Decimal/Wolfram single-cell and total identity; stable deterministic output of **3 source-conditional physical interval rows only** to public Git and no private original populations/REIADP1 states. Separate data/provenance/reproduction, preserve the original source and per-cell evidence privately.

Stage R1–R10 theories/checks are represented in this one science checkpoint; C1–C10 implementation/test evidence will be in one following code checkpoint, not fabricated 20 independent commits. At each checkpoint record REI 28/88, working 33/88, fast 4/7, BASS-CR extension 0/3, all Δ0. CR-OFF baseline and original thermal/26-event/source/worker/14-ledger preserved, NO_REI_MUTATION, NO_MERGE, NO_FORCE_PUSH, PRODUCTION HOLD. Next central milestone remains versioned native original t160→161 worker acceptance and source/clock/14-ledger parity; no new optional atomic loops. Native subagent unavailable: NOT_RUN; only same-author hostile audit.
