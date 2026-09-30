# R4K N1536 A1 부분 결과 보존 및 자원 센서스 수정

상태: `R4K_A2_RESUME_IMPLEMENTATION_READY__LIVE_CENSUS_AND_FRESH_AUTHORIZATION_PENDING`.
이 커밋은 A2 재개 준비만 한다. 새 native operator 계산, parity, pilot, 전파를 수행하지 않았다.

## A1에서 확인된 사실

- A1 실행 commit/tree: `830b2849741f70078ac7bc779ee40c3f249c3fab` / `922c976e5bb3aa8f6a87d96d482ea5b28e82eaf0`.
- A1 부분 ZIP SHA256: `82a8997ad57ad2a7dee70bce67bd0c5b2871df0ca4f23f04362bfb7f8e9b5b7e`, 크기 51269880 byte.
- 완료된 N768 선행 ZIP SHA256: `dd8b3b185ce7c31a16b85d929291ef38d3d8ad666992e5bc1a9e03789e4384f3`.
- A1 선행 pair 2047개와 완료된 stage8 midpoint pair 16개를 합쳐 canonical pair 2063개다. Stage8은 8 workers, 16/16 query, 193.6389812209818초, 0.08262799101251579 query/s, raw 54회, worker 실패 0건이다.
- Stage16은 dispatch 0으로 중단됐고 stage32와 fill은 시작되지 않았다. 당시 겹친 PID/PGID/cmdline/affinity가 보존되지 않았으므로 원인은 `RESOURCE_CENSUS_EVIDENCE_INSUFFICIENT`다. 외부 작업과 같은 실행의 종료 지연 중 어느 쪽인지 단정하지 않는다.
- A1 nonce는 소비됐다. A2는 새 승인 ID가 필요하다.

## 복구 경계

`a1_salvage.py`는 A1 ZIP SHA/크기/CRC와 manifest 전 항목, commit/tree/nonce, 최초 실패와 supervisor 종료, stage 기록, 2063개의 JSON+NPZ 쌍, 16개 query ID와 ordered qualification을 검사한다. 선행 2047개 pair는 선행 ZIP과 byte 단위로 비교한다. 승인된 A1 16개 pair만 create-only로 가져오고 stage8 receipt를 byte 그대로 보존한다. 무결하지 않은 pair, orphan, 예상 밖의 ID 또는 충돌은 거부한다.

재개 단계는 stage8을 재실행하지 않는다. A1의 측정치를 첫 건강한 stage로 사용하고 원래 pilot plan의 stage16 32개, stage32 64개를 계산한다. 성공한 pilot query는 모두 canonical cache에 남긴다. 남은 midpoint는 1520개다. 누적 raw budget은 `GlobalBudget(parent_attempts=54, maximum=16896)`으로 시작하며, 남은 엄격한 최대는 16720회, 생애 최대는 16774회, 여유는 122회다. Stage16/32가 자원 부족으로 시작 전 거부된 경우에만 낮은 건강한 stage로 넘어간다. 외부 BASS CPU 겹침, 이전 풀의 잔존 worker, worker/native/operator 실패는 중단 조건이다.

`resource_census.py`는 후보 PID/PPID/PGID/SID/state, 제한·마스킹된 cmdline, affinity, cgroup, 요청 CPU 교집합과 `SELF/ANCESTOR/SAME_RUN_PROCESS_GROUP/EXTERNAL` 소유 분류를 예외 전에 create-only receipt에 남긴다. 완료된 풀의 task receipt PID가 사라졌는지 짧게 확인하고 동일 실행 process group에 남은 spawn worker도 검사한다. 환경변수나 credential 값은 읽지 않는다.

N1536 required query 1538개, inherited exact hit 2개, 전체 새 midpoint 1536개, 최종 union 3583개, frozen operator ladder와 temporal screen은 그대로다. 필수 query가 모두 검증된 후에만 원래 initial state로 strict cache-only replay를 진행한다. replay native call은 0이어야 한다.

## 검증 및 다음 승인

준비 ZIP은 clean exact commit에서 선행/A1 ZIP, native source/library/BUILD, 고정 numerical dependency를 확인한 후 source pins, A1 salvage manifest, resume query plan, pilot continuation plan, 미래 승인 템플릿을 기계적으로 생성한다. 패키지는 선행과 A1 ZIP fixture를 포함하며 추출된 독립 트리에서 비 native focused suite를 다시 실행한다. 실제 검증 명령과 결과는 별도 검증 receipt에 기록한다.

패키지 생성과 read-only live census는 native 권한을 부여하지 않는다. A2에는 새 commit/tree, 새 authorization ID, 정확한 32 CPU 순서, 새 절대 deadline, 누적 raw 16896, A1+A2 합산 KRW 40000 비용 범위의 명시적 승인이 필요하다. 다른 BASS 작업과 CPU가 겹치거나 메모리가 부족하면 승인 요청 대신 자원 차단을 보고한다.

N3072, 자동 재시도, 새 nonce 우회, threshold 변경, reference 재실행, capture, all-bound, b-grid 및 VM 변경은 범위 밖이다. `capture=false`, `production=HOLD`, `all_bound=OPEN`, `b_grid=NO_GO`, `original_capture_gap_resolved=false`, `continuous_global_supremum_bound=false`, `continuous_trajectory_error_bound=false`를 유지한다.
