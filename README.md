# BASS cosmic-ray charge exchange

H+ + H(1s) charge transfer의 단일 전자, 비상대론적, fixed-target/straight-line point-Coulomb 모형을 다루는 연구 저장소다. Nichols 비공개 코드나 raw data의 byte reproduction을 주장하지 않는다.

## 현재 통합: foundation rebuild + local test-only

`cr/r3m29-spatial-discretization-discriminator-20260924`의 `8e1d49e5ef6af70bb47d9238e64cda68ea0f5c4f`에서 CP3 연구 구성품과 bounded two-center S/H/D 모듈을 독립 sidecar로 통합했다. 기존 `cr_repro`, configs, R3M10-29 결과와 numerical source digest는 변경하지 않았다.

- [Local Codex 시작 프롬프트](START_CODEX_HANDOFF_PROMPT.md): 추가 코딩/연구 설계가 아니라 고정 테스트 실행과 결과 수집.
- [구현·테스트 패키지](research/foundation_rebuild/README.md), [실행 계약](research/foundation_rebuild/VALIDATION_CONTRACT.json), [R2 구현 범위](research/foundation_rebuild/docs/R2_IMPLEMENTATION_KO.md).
- [원 연구 보고서](research/foundation_rebuild/REPORT_KO.md), [재구축 설계](research/foundation_rebuild/docs/REBUILD_ARCHITECTURE_KO.md), [import provenance](research/foundation_rebuild/provenance/CP3_IMPORT.json).

Production **HOLD**, all-bound **OPEN**, b-grid **NO_GO**. R3M27의 고정-h 선택 span 시간 추정과 R3M28 A3/B3 공간 pair NO_GO는 유지한다. 신규 원자/연산자 시험의 PASS를 원래 3% capture 차이의 해결이나 continuum 공간오차 인증으로 해석하지 않는다.

## 역사적 authority

[모형 계약](docs/r3m26/MODEL_CONTRACT.json), [오차 예산](docs/roadmap/ERROR_BUDGET.json), [시간 검증](docs/r3m27/REPORT_KO.md), [공간 비교](docs/r3m28/REPORT_KO.md), [R3M29 국소 판별](docs/r3m29/REPORT_KO.md)을 보존한다. 기존 root MANIFEST.sha256 및 R3M10 문서는 해당 역사적 snapshot의 manifest이며 새 sidecar 전체를 검증하는 파일이 아니다. 신규 실행 코드/시험은 sidecar SOURCE_MANIFEST.json으로 검증한다.

이전 README와 START_CODEX_HANDOFF_PROMPT.md는 위 base commit의 동일 경로에 보존된다. 새 테스트 실행은 자동으로 fresh output과 RETURN ZIP을 만들며, 과거 결과를 덮어쓰지 않는다. GitHub 게시, 코드 시험, 수치적 모형 검증, 원격 복원은 서로 다른 주장이다.
