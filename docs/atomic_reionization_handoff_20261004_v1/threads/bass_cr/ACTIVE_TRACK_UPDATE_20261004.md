# 현재 연구 경로: CR-off fastest

2026-10-04 사용자의 fastest-track 전환 지시를 적용한다. 같은 packet의 TASKS.json과 CODEX_START_KO.md를 우선한다. 원자 계산 속도 최적화가 아니라 CR-free photon/H-He baseline에서 정밀 원자 lane의 필수 의존성을 제거하는 경로다. 실제 CR 효과가 무시 가능하다는 물리적 상계나 sigma=0이라는 주장은 아니다.

## 현재 실행 판정

- source bass_cr commit: `358ba9a76211321b1d048e4cc796ebaa4f3a7005`.
- 조회한 rei_bianchi receiver commit: `4af2912ce73fdb1240db74d420a0a48fe686af0b`.
- 활성 원자 측 task: `CR-F0`.
- 상태: `WAIT_FOR_REI_CONSUMER_TASK` (IMPLEMENTATION dependency).
- 지정된 `rust/rei_microphysics/src/`에는 fixed-input kernel 다섯 파일만 있으며 lib.rs는 thermochemistry solver가 아니라고 명시한다. 이 판정은 지정된 crate에 한정한다.
- 실제 CR dispatch/consumer callback 시험은 미실행이다. source와 loader/callback 관측값은 null로 유지하며 `CR_OFF_ACCEPTANCE.json`을 만들지 않았다.
- 기존 portable reference의 10개 시험은 기록으로 계승했고 반복하지 않았다. 새 원자 계산, native 호출, Bianchi 이력, 소비자 코드 변경은 모두 0이다.

다음 실행 가능한 owner 작업은 **rei_bianchi REI-F00**이다. 그 source/closure/parent lock 및 F01/F02/F03 consumer 구현을 진행한다. CR-F0 수락을 먼저 받아야 F00을 시작할 수 있다는 역방향 의존성을 만들지 않는다. 실제 source-dispatch가 생기면 CR-off에서 provider를 로드하기 전 분기하고 source=0, load=0, callback=0을 focused integration으로 확인한다. portable mock을 추가해 실제 receiver 검증으로 대신하지 않는다.

## 보존한 원자 lane

packet의 R4AO snapshot 이후 이 대화에서 R4AP의 완전 덮개·오차배분·cache/driver 구현은 완료됐다. 실제 전체 1s–1s entry는 미계산이다. R4AQ와 이후 precision lane은 보류하며, explicit process/domain/sensitivity 또는 사용자 재개 결정 때만 연다. R4AP를 다시 구현하지 않는다. 기존 S-only 인증, 실패, G02=UNRESOLVED, production=HOLD, capture=false, all_bound=OPEN, b_grid=NO_GO를 그대로 보존한다.

R4AP 원본 패키지 11,122,394 bytes, SHA256 `95fac399d7ffe6ed5a5dbe1717af32070145b79413fd60823470e0a9fd164242`를 바이트 변경 없이 백업했다. Dropbox ID `id:BSpOijBcT10AAAAAADx5RA`, Drive ID `1oGuBRp3FcITdV3WDV1DXfg5u-owg-Hjg`. R1 ACK/ID/이름/크기 검증이며 remote restore는 아니다. 옛 38파일 patch와 318파일 patch는 적용하지 않았다.

## 상세 상태·인계

`BASS_CR_FASTEST_TRACK_ADOPTION_20261004_v1.zip`
- bytes: `22741`
- SHA256: `c2e86d5d7f6fb5e9a359a0248358b45f69e19ccc24c760b0f92421aa315040ae`
- Dropbox ID: `id:BSpOijBcT10AAAAAADx5ZQ`
- Drive ID: `1l8SlU9e1eg9jDkan4JDKHsV2py-b_OCV`

한 인증된 mirror에서 직접 회수한다. ACTIVE_TRACK.json, CR_F0_RETURN.json, RECEIVER_READINESS.json, LEGACY_STATE_OVERLAY.json, NEXT_HANDOFF_KO.md와 정확한 source 근거를 포함한다. 사용자의 재업로드는 필요 없다. 원문 source는 수정하지 않았으며 이 문서는 additive routing overlay다. 과학적 완료나 실제 receiver binding 완료를 선언하지 않는다.

새 receiver 근거 없이 반복 continue 요청이 오면 원자 retry·전체 감사·새 인계 패키지를 반복 생성하지 않는다. CR-M1~M3는 별도 CR-on observable/domain 결정 전 시작하지 않는다. Bianchi 동역학은 계속 rei_bianchi 소유다.
