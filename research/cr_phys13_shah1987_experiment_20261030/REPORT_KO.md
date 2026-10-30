# BASS-CR PHYS13 보고서 | 2026-10-30

## Outcome

실측 26점의 원본 Shah1987 H(1s) 전자충돌 자료를 원래 PHYS12/PHYS11 계보의 광자 source 6400원자에 source-qualified 상태로 연결했다. **신규 source-derived 데이터 6599행** (원본 실험점26 + 광자 원자6400 + 시간×source 54 + 시간 총계27 + 에너지 원본 bin92). 계산은 가속·stopping·공통 시간 진화·실험 측정 수율 없이 고정 원자 H/He gas와 실측 단면적 구간보간을 사용한 조건부 노출 모델이다.

## Primary results, T=1e10s

- Parent PHYS11 energy-only H capacity earliest: 1.28863125860899684e-28 m^-3.
- Shah measured-supported kinematic fraction earliest: 0.700377952.
- Shah central measured-supported finite-time H-second upper earliest: 1.23437461610498315e-31 m^-3.
- Shah lower / upper simultaneous error-plus-normalization scenarios: 1.11744008417127528e-31 / 1.35610902897027718e-31 m^-3. **Not probabilistic interval or strict bound.**
- Kim original published fit evaluated on **identical measured domain**: 1.25356210324239099e-31 m^-3; Shah/Kim=0.984693629. Measured 14.6 eV knot fit discrepancy +7.8214%.
- Unmeasured (<14.6 eV) kinematic upper capacity: 3.86102336573753815e-29 m^-3 (not observed impact rate). It exceeds the measured-domain collision envelope; source-wide secondary rate therefore remains unresolved.
- Latest scenario measured-supported central: 3.67227227111694134e-32m^-3, first source count 6.53655992483617193e-27m^-3.

## Verification

Finite-horizon integral Gauss–Legendre24, independent SciPy QUADPACK at 3 real source atom energies, Wolfram symbolic first-absorption/second-event and dlnσ identities (both residual 0), Python unit normal and -O 20/20 each, 27/27 original PHYS11 first/capacity parity, manifest/CRC/source SHA, deterministic 6 files outputs compared by SHA256 in clean extraction. All statuses bound to actual execution logs. Same-author adversarial checking does not fill distinct author R06/C09.

## Verdict

Scopable physical-data advance. CENTRAL_DAG=28/88 DELTA0. EXTENSION_DAG=0/3 DELTA0. PHYS13 auxiliary 1/1 REVIEW_HOLD, research R/C count 18/20 due distinct author. No actual K, stopping/transport or He global exclusive kernel; common evolving neutral+photon+clock+geometry absent. Next physical supplier may be source-common electron stopping/transport with 100K relative target velocities and source-compatible closure. No merge/force push or production.
