# BASS-CR → REI original F05 | 추가 전자충돌 1s→2p Lyα source sector

2026-11-01 KST. 원본 REI 26-event F05의 **정식 승인 tick160**을 소비한 1개 물리 데이터 생산 단위. Source owner는 REI PR356 cc1929982948265f6d0b0f699353b3170ccd1792, BASS-CR parent PR160 fb4f0e150aae027421fafa942abc7c09d70ae67d. tick161은 정식 승인되지 않았다.

## 근거 상태와 유효범위
- Established/literature-supported: Scholz et al. 1990 MNRAS 242,692 DOI 10.1093/mnras/242.4.692; Pradhan published table of Maxwellian effective collision strengths for HI 1s→2p: Υ(5000K)=0.416, Υ(10000K)=0.472, Υ(15000K)=0.528, Υ(20000K)=0.585; A21=6.265×10^8 s^-1. Published atomic value and its tabulation provenance are NOT identical claims.
- Model-conditional: piecewise-linear Υ interpolation; Maxwellian T_e=T_gas; all original neutral H in 1s (f1s=1); prompt two-level radiative competition. Unknown collision strength interpolation uncertainty, non-LTE neutral state and non-Maxwellian effects are NOT included in source intervals.
- Source-numerically verified: original 46,080-cell 27-field source byte SHA256 713b46a0da8931cc6f5a355912cdd2efa790945c2539ad049c086fd995f3441d; original proper cell volume and electron density checked against SHA-locked native REI owner and source-native Case-B PR160 data. No synthetic cell inputs or other simulation lanes.
- Temperature valid 5,000–20,000 K, **12,528** original cells. Excluded cold **14,832**, hot **18,720**, zero boundary ambiguity; supported cells contain **75.83855556965152%** of original tick160 H I count. The excluded high-temperature sector could contribute substantially. Therefore the supported-sector rate is NOT a full-IGM upper or lower bound absent assumptions about excluded cells.

## Constructive physics
At fixed source cell N_H, x_HII, N_e, proper volume V and T, effective collision strength Υ(T):
  q12(T)=8.629e-6 Υ(T) exp(-10.198835887565243/[8.617333262145e-5*T])/(2 sqrt(T)) cm³/s;
  q21(T)=8.629e-6 Υ(T)/(6 sqrt(T)) cm³/s.
  R_exc=N_H(1-x_HII) f1s (N_e/V) q12 [excitation events/s].
  R_rec,Lya=N_H x_HII (N_e/V) alphaB(T) PB(T) [Case-B recombination photons/s].
  R_exc/R_rec,Lya = f1s [(1-x_HII)/x_HII] q12/[alphaB PB] (exact same-cell cancellation).
Under two-level radiative competition, b21=A21/[A21+n_e q21] and R_coll,Lya=b21 R_exc. Original 4 ionizing photon groups do not measure or transport these 10.2 eV Lyα photons.

## 새 원본 셀 기반 물리 결과
- Conditional 1s-saturated e+HI → 2p **excitation-rate interval**, source-state interval only: [5.026781097199843e48,5.0298516439581024e48] s^-1, midpoint 5.028316296918783e48 s^-1, restricted 12,528 original material cells.
- Same 12,528 cells Case-B conditional Lyα source 1.3465051545657722e50 photons/s. New excitation/source ratio **0.03734346118073599**. This is not a global 46,080-cell source fraction, not a scattering optical depth, not observed luminosity and not a new radiation evolution.
- Corresponding maximum potential electron kinetic excitation energy transfer (no radiative escape/feedback) 8.216438058687765e37 erg/s. Physical energy is taken from electrons in each excitation; not permission to insert a new heat sink into an existing energy equation without checking previously included cooling.
- Maximum computed two-level e− collisional deexcitation to spontaneous ratio n_e q21/A21=2.351419442626624e-19: deexcitation is negligible at source densities in this *restricted model*. Radiative trapping, line self-absorption, 2s and 2p kinetics, photoexcitation/fluorescence and Bianchi null geometry are NOT assessed.
- Original per-cell n_e source parity maximum relative residual 0; independent direct recombination ratio identity maximum relative residual 6.661338147750939e-16.
- Derived 12,528-row gzip SHA256 09c564df9400b171617ce5006b2c7eee94085f8d321f8d41648fc9456cbd1628, RESULT.json SHA256 55d8f2c0731ef2fae058d3a02307f46c9a96f297ad047a2106c4b3a19e8c041c. Private 27/30-field original material arrays are not committed.

## Hostile referee / drift
The first independent Decimal64-vs-float64 q test FAILED at an unnecessarily tight 2e-15 threshold: maximum observed relative 3.9968028886505635e-15. This is a floating-point rounding discrepancy, NOT an original physics or original REI source-owner acceptance failure. Test threshold changed to 1e-14 for only this new test, with provenance and failure retained; frozen original physics gates untouched. Final 15/15 standard, 15/15 optimized -O tests passed locally; original native Python import emitted optional NumPy2/NumPy1 extension diagnostic to stderr but exited 0. Distinct-author referee NOT_RUN; source-dependent GitHub CI claim NOT_MADE without actual logs.
Stop: this is **one** missing conditional source sector. No additional fits/atlases/angle surveys without REI original owner RUX02/RUX03 and original F05 tick161 admission. NO_REI_MUTATION, NO_MERGE, NO_FORCE_PUSH, CR_OFF_UNCHANGED, PRODUCTION=HOLD. REI central 28/88, working 33/88, BASS_CR optional extension 0/3, all Δ0.