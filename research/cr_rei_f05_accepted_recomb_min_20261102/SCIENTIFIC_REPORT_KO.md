# BASS-CR → original REI F05 accepted-history gross Case-B H recombination lower budget

Date 2026-11-02 KST. One **original scientific source-derived, 3-interval**, nonproduction result in BASS-CR stacked on immutable parent PR163 HEAD `b5001472fa96ec7ba511e989948d826df3d12ab3`. Main, original REI 26-event 46,080-cell owner, original [0,64,128,160] states, 14 ledgers, original worker and CR-OFF unchanged. **Official original accepted tick160/131072**. Tick161 remains nonauthoritative, NOT_ACCEPTED.

## Real primary source and identity

Original REI source HII RHS `reduced_interval_rhs.py` SHA256 `b1f3d6d6397ff727b756816165652a44eb373055256adf7af2e7ef6304ed9b36` has `dN_HII/dt = ion_h - r_hb`, `r_hb=N_HII*(N_e/V)*alpha_B(T)`, `ion_h` a sum of source-native nonnegative H photoionization, collisional ionization and He-OTS H-ionizing contributions (physical cone). Initial source NPZ SHA256 `7855f8b5c072da7860e5b0404a5548114ef46a8713840d99e4efa1b009905d2d`. Exact historical primary REIADP1 state SHA256 at tick64 `aae4607ec1f0eff6669f1c1cb716ec6d6a4af8b789bba14abcd17f1733f83425`, at tick128 `bbb349102194c86fb39a720a6695d9cb5845782b154da3448a433959fcc7f6a6`, at tick160 `74c7cbb784c3a6fe25e53307f678ef23ab87263f56b314fbaa3ef696433d05f6`. REC #195 accepted trajectory summary SHA256 `f015ff77dfdc2afc022360880030aa29f06c234cac146105edbbf291fce39429`; REI #365 verified all three first64 source lanes, but these represent the SAME physical material state, not independent simulations.

## Proof and physical result

If the true model-consistent continuous trajectory is enclosed by the historical accepted-state endpoint intervals, integrating `dN_HII,j/dt=I_j-R_j` with `I_j,R_j≥0` yields the **conditional necessary bound**:
`R_min,j(a,b)=max(0,N_HII,j(a)_lower-N_HII,j(b)_upper) ≤ ∫_a^b R_j(t) dt.`
This is independent of unknown intermediate rate fluctuations and not a staged original reaction integral. Using `χ_H=13.598434599702 eV`, `1eV=1.602176634e-12 erg`, the minimum gross H recombination *chemical binding* energy released is `χ_H ΣR_min` (after unit conversion). No identity with escaped Lyα photons, gas heat or total He/H net binding. Original proper microtick `4871848749.16828 s`.

| Original accepted proper ticks | Minimum conditional H Case-B recombinations | Gross H binding-energy release lower, erg | Source cells with certified HII decrease |
|---|---:|---:|---:|
| 0→64 | 8.879746299967941e61 | 1.934638688841322e51 | 42474 |
| 64→128 | 8.835204102163902e61 | 1.9249342382583105e51 | 42534 |
| 128→160 | 4.3819861215626807e61 | 9.547074430236255e50 | 42522 |
| TOTAL 0→160 source-conditional | **2.209693652369452e62** | **4.814280370123257e51** | *Do not add row counts* |

Cellwise minima are stronger than the globally aggregated signed HII decline bound because individual increases/decreases may cancel. The source output records 3 aggregate physical records, **not** a duplicated 138,240-row source atlas. Mathematica independently confirms the linear positivity constraint `R ≥ max(0,N_a-N_b)` and H binding-energy arithmetic.

**Specific scientific use:** Any future original source-clock-consistent cumulative `r_hb` reaction balance must satisfy this lower constraint if the original continuous source endpoint enclosure is valid. It is a necessary, not sufficient, native photon/chemistry budget for later RUX03; original accepting t161 requires separately the full versioned 26-event worker/source-clock/14-ledger tests.

## Blind-referee attack and nonclaims

1. **Continuum qualification:** REIADP1 accepted endpoint state boxes are **discrete method output**. They do not themselves certify exact continuous-ODE enclosure. Thus these numerical bounds are strictly SOURCE_CONDITIONAL_MODEL_BOUNDS, **not** source-confirmed exact actual event totals nor publication-grade continuum certificates.
2. **No photon count:** Case-B recombination need not emit a surviving Lyα photon. Cascade and level population, 2s two-photon transitions, resonant scattering/escape and spectral/angular transport are unowned. No nonzero lower bound on observed/intrinsic Lyα photons is admitted from these HII endpoints.
3. **No finite upper from endpoints alone:** The formal transformation `I→I+k(t)`, `R→R+k(t)` with nonnegative `k` leaves HII endpoints unchanged while gross reaction counts increase. The ORIGINAL fixed kinetic model would restrict `k`; this example proves only the **information limitation of endpoints**, not a strong no-go theorem on the full physical model.
4. **No invalid scalar cancellation:** Helium OTS can create HII, so `−ΔN_HII` is only a minimum recombination number. Net HII change and electron-number change are distinct.
5. **Numerical identity precision:** Source states are exact SHA bytes, NumPy and stdlib binary readers, conservative one-ULP binary64 subtraction/summation corrections; no global MPFR proof or continuous error calibration claimed.

## Tests and status

Actual original-source normal `python3 -m unittest -q test_accepted_recomb_min`: **12/12 PASS**, optimized `python3 -O -m unittest -q test_accepted_recomb_min`: **12/12 PASS**. Includes independent 46,080-cell state-body decoder readback, original hashes/clock, negative malformed state/tamper, energy dimension, positivity, deterministic output and provenance. Initial changes were a Python shape guard error in the new source consumer and two new-test input errors, corrected without changing original physics or tolerances. No native subagent, different-author independent referee, large solver run, or original IVP claimed. GitHub CI status must be independently checked.

BASS-CR remains science supplier-only. Central REI **28/88 (+0)**, working **33/88 (+0)**, physical fast **4/7 (+0)**, BASS-CR extension **0/3 (+0)**. NO_REI_MUTATION, NO_MERGE, NO_FORCE_PUSH, NO_CR_ON, PRODUCTION_HOLD. **Do not continue with another optional fit/opacity atlas**. Next central action is original F05 owner versioned [160,161] accepted state map and proper source/clock/14-ledger admission, then owner-controlled line-photon source and Bianchi geometry.
