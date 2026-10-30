# BASS-CR PHYS10 | 새 물리 데이터 생성 및 검증 보고서

2026-10-30 KST, source-locked primary photoelectron energy causal susceptibility. **원본 소스 물리량의 조건부 결과이며 신규 관측 자료가 아니다.**

## 연구 범위 및 출처

- `cosmosapjw-quantum/bass_cr` immutable parent PR134 HEAD `9a79c8b618fae288aee3a6bebdb2b8a5afba9c67`; original PHYS09 archive 6,671,808 B, SHA256 `e77bb3b9f7a91f608841b39e0b9679703c7d1f4d50f929c7fb7f030dac175243`. Nested PR133 original source SHA `16d0b7c9e2540777ea0e360511e502303e6ea887ae0ecd658282d14d79923ae4` and further nested PR132 source protected.
- Source: original 100K 3200 H+3200 He RR photon atoms, 4 birth intervals, 9 physical observation epochs (proper seconds), neutral densities original (138.6,11.427127659574467) m^-3; unchanged original Verner (1996) fits. No BASS21/REI source splicing.
- Derived source-weighted energy `Q_a=Σw(E-I_a)P_a`, `F_a=B_a+Q_a` and causal energy response `∂Q_a/∂ln n_b` from original first absorption and its exact PHYS09 window derivative. For full definitions see `THEORY_KO.md`.

## New physical numbers (unit J/m^3 unless specified)

At original final T=10^10 proper seconds, **earliest-source-birth witness**:

- Initial primary electron total energy: **6.236750696526702e-45** J/m^3.
- Target atomic binding energy increment: **3.781160219198057e-44** J/m^3.
- Total absorbed photon energy: **4.404835288850727e-44** J/m^3; sum of above terms to floating-point accuracy.
- HI first event: 1.6996986246313596e-26 /m^3; HeI first event: 1.9692741973494655e-28 /m^3. Sum agrees with original PHYS09 first absorption 1.719391366604854e-26 /m^3.
- HI first-photoelectron mean 2.258448795769167 eV; HeI 2.741684974878306 eV.
- At original baseline, d<eps_HI>/dln(n_HI)=+0.03197396074378495 eV and d<eps_HI>/dln(n_HeI)=-0.001226174311043836 eV. HI energy susceptibility dQ_HI/dln(n_HI)=5.956468059454388e-45 J/m^3, dQ_HI/dln(n_HeI)=-4.028444095771501e-48 J/m^3.

At final T, **latest-source-birth witness**:

- Initial primary electron total energy **2.3286751165159967e-45** J/m^3, atomic binding **1.437321399001462e-44** J/m^3, absorbed photon **1.6701889106530614e-44** J/m^3.
- HI first-photoelectron mean 2.218061098077124 eV; HeI 2.703932270410766 eV.

These are two *admissible witness schedules*, not proved global extrema of a ratio.

## New dataset and validation

- `results/TIME_CHANNEL_ENERGY.csv` 108 original-source physical event/energy rows.
- `results/CAUSAL_ELECTRON_ENERGY.csv` 1,728 causal number/initial-electron/binding/photon energy response rows.
- `results/TIME_ENERGY_LEDGER.csv` 27 common birth-policy/epoch energy budget and conditional-mean derivatives.
- `results/FINAL_ENERGY_RESPONSE.csv` 368 original photon-energy bin electron-energy susceptibility rows.
- Total *new* source-derived records: **2,231**, excluding machine results and test receipts.
- Tested in this session `python -m unittest test_phys10 -v`: **20/20 PASS**, `python -O -m unittest test_phys10 -v`: **20/20 PASS**, `python -m compileall`: PASS. Clean full `bash REPRODUCE.sh` (with exactly original nested source): exit0, **6/6 result-file SHA-256 byte replay**.
- Source-owner parity using independently preserved PHYS09 CSV: **1,728/1,728 causal number-response values exactly equal (max relative difference 0)** and 27/27 time baselines agree.
- Same-author alternate MP70 direct 3-segment competing-hazard finite differences compare 96 scalar cases over source energy atoms, both absorber and neutral owner choices; program test gate `<1e-6` relative on nonzero cases (observed PASS). This is **NOT** distinct-author R06/C09.
- Wolfram symbolic integral exact identities, conservation and conditional average derivative verified. Physical ledger maximal pointwise absolute `4.598021441129071e-61` J/m^3, response ledger `9.196042882258143e-61` J/m^3 (float roundoff, not error estimates of atomic cross sections).

## Parent and other-repository survey

- BASS-CR: PR134 at HEAD given above; PR133 remains Draft, 11/43 partial Git, original physical SOURCE externally preserved, no repair or merge.
- `rei_bianchi` PR284 2E1 Li II BASS193 source: genuinely source-common *inside that owner*, distinct photon spectra and frozen ionic history relative to BASS-CR H/He.
- `bass` PR274 finite-beta polarized Bianchi photons; `vigilode` PR131 and PR130 original BASS21 memory/geometry; `BASS_HE` PR124 DD measured capture; `rec_bianchi` PR168 HD line transfer; `WU088_HH` PR172 HD chemistry competition. All distinct physics owner/grain. **No** source-common radiative/clock/neutral transport substitution is licensed.

## DAG and claim gate

**CENTRAL 28/88 (+0); EXTENSION 0/3 (+0); PHYS10 AUXILIARY 1/1 SCOPED_REVIEW_HOLD.** Theory 9/10 + code 9/10 at same-author scoped execution; distinct-author R06/C09 NOT_RUN, native subagent NOT_RUN. `PHYSICAL_K=UNBOUND`, original He exclusive double-event kernel and two ejected electron correlation `UNBOUND`, no evolving shared H/He neutral/radiation/geometry history, native25/L4/production HOLD. No unlicensed physical claim of heat or full coupled chemistry. No merger, force push, parent PR/head mutation or auto-next.
