# C20 원본 회수: source-age FLRW photon oracle

이 패키지는 C19 (`e91ffe368c4e6db64c4b6c5962566302a33402b6`) 위에서 회수한 C20의 실제 Rust source와 NCP 원시 결과를 보존한다. `src/c20_native.rs`는 재구성 fallback이 아니며, SHA-256 `13b6bc6fd3279d6b90f95baccf7bae20bbca838ee1eb83583c22071411c64de0`인 원본 바이트이다. `raw/sweep_pass.json`도 원본 바이트(SHA-256 `7c1a39fd02294623f93c4c95da15827edae4644cb455cf114c85f9ed0cc3dc19`)이다.

## 회수 및 검산 결과

- 원본 경로: `/root/BASS_CR_C20_20261015_003`; create-only 사본은 그 아래 `recovery_create_only_20261016T0813Z`에 있다.
- `rustc 1.99.0`; raw sweep은 20/20 `PASS_SCOPED`이다. 18개는 source+absorption He II refinement, 2개는 switch control이다.
- 원시 ledger 재계산에서 최대 `|number_residual| = 6.94e-18` photons/H, 최대 `|energy_residual| = 1.39e-16` eV/H이다. 사건·열·적색편이 work는 비음수이다.
- binding energy `[13.598434599702, 24.587389011, 54.41776]` eV와 Verner fit crossing cutoff `[13.60, 24.59, 54.42]` eV는 의도적으로 구별된다.
- GL4 proper-time 과 owner Simpson 시계의 refinement 상대 차는 최대 `8.45e-14`이다. crossing은 source-age packet의 cutoff cell split으로 기록된다.

## 판정 범위

이 결과는 fixed gas fraction, FLRW-only (`q_ref=0`) photon transport oracle의 photon/binding/heat/redshift-work ledger만 검증한다. `a_end=0.0914`와 `0.095`에서 He II refinement 인접 차이가 비단조적이므로 전역 convergence order는 **HOLD**이다. 동적 H/He chemistry·thermal evolution, Bianchi geometry 및 전체 EoR production은 이 패키지에서 검증되지 않았으며 PASS가 아니다.

## 재현 가능한 비물리 검산

`python3 tests/test_raw_audit.py`는 보존 JSON의 ledger 방정식과 positivity만 검사한다. NCP sweep을 재실행하지 않는다. 원본 crate와 input의 immutable hash는 raw provenance에 기록돼 있다.
