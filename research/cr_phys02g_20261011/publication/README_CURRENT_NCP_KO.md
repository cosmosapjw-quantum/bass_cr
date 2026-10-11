# PHYS02G 현재 전달본: 저장 모멘트 분석 + 실제 F 실패 통합

이 ZIP 하나로 다음 NCP 읽기 전용 진단을 시작할 수 있다. 현재 상태는 **G 저장 분석 PASS_SCOPED, F HOLD_OPERATOR_BINDING_UNRESOLVED, G actual frontier BLOCKED_BY_F_OPERATOR_BINDING_HOLD**다.

## 먼저 읽을 파일

1. `late_f/CURRENT_NEXT_ACTION.json`: 실제 독립 준비 판정과 연결한 현재 행동.
2. `late_f/LATE_F_INTEGRATION_KO.md`: 게시 중 도착한 F 실제 실패, 수치·물리 의미와 상태 우선순위.
3. `late_f/NCP_READONLY_DIAGNOSTIC_CONTRACT.json` 및 `late_f/FINAL_READONLY_HANDOFF_DECISION.json`: 새 읽기 전용 과제의 입력·범위·예산·판정.
4. `late_f/INDEPENDENT_LATE_RETURN_ASSESSMENT.json`: 실제 F 보존 파일에 대한 별도 독립 평가.
5. `late_f/R3_RESTORE_RECEIPT.json` 및 `late_f/SOURCE_SNAPSHOT_RECONCILIATION.json`: 원본 backup과 뒤에 게시된 Git snapshot의 구분.

G core 내부의 “F actual not observed”와 “WAITING”은 2026-10-11 07:01 UTC 후보 고정 시점의 기록이다. 실제 F 반환 PR37은 07:02:57 UTC에 생성됐다. 이를 지우거나 core 해시를 바꾸지 않고 현재 HOLD를 위의 후속 기록으로 명시했다. 이 반환에 대해 과거 START의 “F 미예약일 때 최초 실행” 분기를 적용하지 않는다.

## 정확한 복구

외부 시작 파일의 전체 ZIP 크기·SHA256을 확인한다. 이 파일의 outer manifest는 `BUNDLE_MANIFEST.json`, schema는 `cr-phys02g-late-f-hold-envelope.v1`이다. payload entry와 manifest 자신 하나가 정확한 전체 entry 집합이어야 한다. 절대경로·parent traversal·중복·symlink·비정규 ZIP member를 거부하고, 각 크기·SHA256을 검증한 뒤 새 빈 root에 복구한다. 기존 작업 위에 덮어쓰지 않는다.

| 내장 원본 | 용도 |
| --- | --- |
| `payload/CR_PHYS02G_20261011_0ad3be0f_HANDOFF.zip` | 동결 G core, 독립 판정, 수학 유도, 실제 저장 분석·그림, 준비 코드 및 기존 완전 F/E/canonical 의존 자료 |
| `payload/CR_PHYS02F_LOCAL_OPERATOR_BINDING_HOLD_REMOTE_20261011T0700Z.tar.gz` | 새로 도착한 실제 F 실패 원본: numerical ZIP, 원본 return family와 종료 sidecar·로그 |
| `late_f/git_publication_snapshot/research/cr_phys02f_local_operator_return_20261011/` | PR37 head a490ab7af8e7b1b4db9a604293867df8e6d035dd의 정확한 47-file 게시 snapshot |

두 archive는 원본 바이트 그대로다. 각 원본을 별도의 빈 root에 복구한다. G inner manifest는 `cr-phys02g-self-contained-bundle.v1`이다. F tar는 일반 파일·디렉터리만 허용하며 절대경로·parent traversal·중복·symlink·hardlink를 거부한다. F tar의 원본 `F/return/RETURN_FAMILY_MANIFEST.json`과 내부 numerical ZIP의 RETURN_MANIFEST를 검증한다. ZIP 안에 없는 publication metadata가 나중 Git snapshot에 있다고 해서 원래 tar를 고쳐 쓰지 않는다.

G core는 141 entry의 새 복원과 stdlib missing-F plan을 한 번 통과했다. 이 로컬 준비 검증은 실제 NCP 런타임이나 성공한 F/G 수치 결과의 승인이 아니다. 수신 호스트의 source 복구 검증은 해당 호스트가 실제로 수행하고 별도로 기록한다.

## 다음 NCP 단위

`CR-PHYS02G-NCP-OPERATOR-PROVENANCE-INTAKE`만 진행한다. F는 이미 G 생성 1회 뒤 exact operator binding에 실패했고 execute/collect/wrapper exit은 1/0/1이다. G/solve/pulse/expm을 새로 실행하거나 nominal F allowance를 재사용하지 않는다.

현재 실패 반환에는 양쪽 CSC 원시 값이 없다. 실제 NCP의 기록된 cache/run 위치에서 이미 보존된 reference/current 값을 확인한다. 정확한 원래 identity와 연결된 두 값이 모두 있을 때만 계약 안의 한 번짜리 저장 배열 비교를 한다. 없으면 MISSING_PERSISTED_OPERATOR_VALUES와 실제 검색 범위를 기록한다. Hash 차이만으로 오차 크기, roundoff-only, 원인 또는 물리적 비동등성을 추론하지 않는다.

진단 명령 구간은 180초, 조건부 저장 배열 비교는 최대 1회·90초다. 모든 G/linear solve/pulse/expm/F retry/G frontier 호출은 0이다. source 복구와 파일 전송 시간은 따로 기록한다. BLAS dispatch 강제, 환경·라이브러리 변경, reference SHA 교체와 tolerance 완화는 없다. 기존 G frontier 1회·90초 준비 예산은 미소모·비활성 상태다.

새 물리 실행은 독립 심사를 통과한 별도 유한 계약과 실제 입력·누적 예산이 마련된 뒤에만 다룬다. 현재 단위는 그 물리 실행을 승인하지 않는다.

## 원본 보존과 반환

원본 F 실패 family 전체, 현재 G 원본, 이번 읽기 전용 진단의 실제 command·UTC·wall·exit·raw logs·code/source identity와 새 독립 평가를 완전한 새 outer return에 함께 담는다. 기존 archive, 실패, core 계약을 변경하지 않는다. G 게시 branch `research/cr-phys02g-moment-frontier-20261011`의 실제 최신 head가 science commit `0ad3be0fec018fbd638063ffd4bf4d0cf2ef8525`의 descendant이고 후속 변경이 publication 범위인지 확인한 뒤, 새 additive return branch와 draft PR을 만든다. merge·force push·history overwrite는 없다.

기존 Drive 폴더 1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI 및 Dropbox /BASS_DERIVATION_DOSSIERS_20260912에 고유 이름으로 완전한 반환을 저장한다. 통상 게시 R1과 실제 source 복구 R3를 구분한다.

G-R01의 FP64 끝점 한계와 모든 상속 gate를 유지한다. 저장 구간 8/10의 exact decimal-token 부등호 차이를 인증된 exact-input 포함구간이나 물리 오차로 바꾸어 표현하지 않는다.
