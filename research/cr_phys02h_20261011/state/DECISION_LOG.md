# PHYS02H decision log

## 입력과 현재 의무

사용자의 2026-10-11T17:38:49+09:00 요청을 적용했다. 경량 계산을 ChatGPT 환경에서 완료하고, NCP에는 길고 무겁고 병렬화 가능한 계산만 넘긴다. 이전에 허용한 additive Git draft PR 및 새 이름의 Drive/Dropbox 완전 백업을 유지한다. 별도 사용자 첨부를 요구하지 않는다.

G publication f5ac634e67ab17e8820eed8f53d625b6c230a252를 기준으로 PR39/PR40 sibling 반환을 개별 namespace에 보존했다. 완료된 read-only intake는 재실행하지 않는다. 원래 F 실패·소모된 G 예약과 G frontier HOLD는 유지한다. 새 source implementation을 과거 F 재시도 예산으로 해석하지 않는다.

## 후보 선택과 동결

Root는 두 개의 구체적 의무를 선택하고 SCIENTIFIC_CONTRACT.json을 구현 전에 고정했다.

1. G-R01의 FP64 끝점 인증 한계를 처리하기 위해 저장 십진 토큰의 정확 Fraction 인증을 계산한다. Selected 합계와 birth 정의가 정확히 다른 경우 별도 확률 표현으로 유지하며, 각각 비어 있지 않은 모멘트 분포군에 대해 strict lower/closed upper를 인증한다.
2. 새로운 대형 과학 계산의 병목인 원본 생성행렬 구성을 열별로 분리한다. 원래 열 내부 계산과 물리 입력은 고정하고, 새로운 source identity로 실제 직렬/병렬 배열을 비교한다.

여기서는 전체9600 생성0, 작은240 전체16개와 저장grid의 선택16열8개, 정확 분석1회만 허용했다. 작업별 초 단위 예산과 한 번의 구현 한정 repair 규칙을 동결했다. 후보 구현은 ASTRA_TIER_ROUTING_POLICY에 따른 lower worker가 맡고, 독립 판정자는 후보·허용조건·구현에 참여하지 않았다.

## 실제 결과와 범위

Exact 생산 검사8개 및 실제 분석1회가 첫 실행에 통과했다. 20개 인증을 별도 Fraction 참조 프로그램이 확인했다. 비공집합 증인8개와240개의 정수 증명을 포함한 독립 검토는 PASS_SCOPED다. 인증은 각각의 기록이 정의하는 모멘트 분포군에 조건부다. 실제 원자·bath·격자 오차는 인증하지 않는다. 과거 G-R01 결과를 삭제하거나 고치지 않았다.

병렬 표적 검사4개와 실제 파일럿1회가 첫 실행에 통과했다. 작은 전체16개와 선택 열8개, generator 실제52회(부분 worker44회 포함)이며 전체9600 생성은0회다. 작은 작업에서는 spawn 비용 때문에 병렬 실행이 더 느렸다. 이 사실을 NCP 성능으로 외삽하지 않는다. 보관한24 payload를 독립적으로 읽는 검증은 생산 물리를 재실행하지 않는다.

## NCP 과제와 자원 보완

원본 전체9600 paired serial lanes에는 합계24GiB 작업 여유와 최소16GiB reserve를 요구한다. 현재 실제8GiB 호스트에서는 시작하지 않는다. NCP의 유한 새 과제는 두 모델×직렬/병렬×두 반복, 총8논리 생성과76800열 평가, whole-command900초다. Pulse/expm/solve/F retry/G frontier는0이다.

완료된 local spawn 파일럿에서 resource_tracker가 worker/coordinator lifetime RSS 밖이라는 점이 확인됐다. NCP_RESOURCE_AMENDMENT.json으로 지원 프로세스2개, CPU 고정5슬롯, 지원 메모리64MiB를 추가로 계산했다. 초기 계약은 보존했다. 최종 wrapper source를 통합할 때 감시 프로세스1개가 더 있음을 발견해 NCP_WRAPPER_ACCOUNTING_AMENDMENT.json을 추가했다. 처음 검사한 소스와 input manifest는 보존하고 영향받은 accounting만 고쳤다. 최종 실제64CPU에서는 모델당29workers와 고정6슬롯으로 총64슬롯이며 wrapper 메모리64MiB도 추가한다. 실제 cgroup/affinity/메모리가 작으면 줄이거나 typed HOLD한다.128GB와128GiB를 동일시하지 않는다.

두 반복의 정확성·build-and-persist wall·부분 worker 시간·메모리를 따로 기록한다. 후보가 느리면 PERFORMANCE_NOT_IMPROVED로 보고하고 반복 최적화 sweep을 자동 시작하지 않는다. 새 source의 same-runtime qualification과 원래 F의 미해결 identity는 구별한다. 새 행렬을 옛 CSC 복구나 옛 pulse 자동 승인으로 해석하지 않는다.

## 모델 및 판정 출처

Root host label은 GPT-6 Astra Pro이나 router의 exact alias는 MODEL_UNRESOLVED다. 프로젝트의 source-bound canonical Astra v4.0.0 흐름을 이어 사용하며 요청 모델 이름으로 backend를 인증하지 않는다. 처음 요청한 reviewer 모델/effort 조합은 실행 전에 서비스에서 거부됐고, 그 사건을 REVIEWER_ROUTING_EVENT.json에 보존했다. 실제 independent reviewer는 상속된 root 모델로 별도 검토했고 구현 역할에 참여하지 않았다.

각 독립 판정은 검토한 파일과 해시를 별도로 고정한다. 최종 실행 source manifest를 검토한 NCP preparation decision만 NCP_READY.json을 생성할 수 있다. 실제 NCP 결과의 독립 판정은 아직 수행되지 않았으며 준비 승인이 미래 실행 결과를 승인하지 않는다.

## 독립 HOLD와 제한된 실행기 교정

첫 NCP 준비 심사는 이미 죽은 qualifier 뒤에 남은 group, 손상된 control/event records, comparator session 기록 및 deadline 직후 취소의 다섯 결함을 확인했다. 최초 manifest `0a0281dccbbae4f53a167bdb0af421c2cf760f0ca0926c9be08f716887aab280`와 최초 HOLD를 보존했다. Root가 원래 실패 수집 계약을 충족하는 한정 수정을 승인했다. 그 첫 영향 batch는6PASS+1FAIL+1ERROR였으며 전체를 보존했다.

그 두 실패는 current PID namespace와 ancestor procfs view의 불일치로 설명됐다. `/proc/self`와 namespace identity를 기준으로 syscall PID/PGID/SID와 procfs 경로를 구별하도록 최소 수정을 승인했다. 새 매핑은 소유권 확인·parent route·session·cleanup·메모리 관측에 일관되게 적용한다. 무관한 namespace나 미확인 group은 kill 대상이 아니다.

마지막 영향 batch는6PASS, exit0, wall1.725660511초였다. 실제 관측은 orphan 두 개 LIVE→GONE, watchdog 자식 LIVE→ZOMBIE이며 최초 실패 순간은 NOT_OBSERVED다. 과거 scalar/pilot/물리 호출은 재실행하지 않았다. 최종 source manifest는 v2 `14f9ad1319146c72d13b1e30583dc27d3b9272c8d23913e63467782fa57b35ec`로 새로 고정했다. Root의 최초 manifest-writing helper는 receipt field 이름을 잘못 읽어 쓰기 전에 KeyError로 종료했고, 실제 schema를 읽은 후 metadata만 교정했다. 이 사건도 EXECUTION_MANIFEST_REVISION_RECEIPT.json에 남겼다.

후속 독립 심사는 최초 다섯 결함과 namespace 직접 영향의 diff·저장 증거만 읽는다. 독립 fixture·생산 물리·과거 검사를 반복하지 않는다. 최종 NCP_READY는 이 후속 심사가 새 manifest에 대해 PASS_SCOPED를 준 경우에만 생성한다.

## 전달과 후속 실행

완전한 H outer에는 새 source·모든 local evidence·handoff·기존 G 완전 ZIP의 동일 바이트를 포함한다. 새 source 복구 확인과 stdlib plan1회는 R3의 게시 범위로 구분한다. 원격 업로드는 기존 R1 규칙을 따른다. Provider 성공·정확ID·size·제공되는 checksum만 확인하며 없는 SHA 때문에 다운로드를 반복하지 않는다.

새 Git science commit/tree와 outer의 실제 SHA/크기/Drive/Dropbox ID는 게시 이후의 별도 receipt와 외부 START에 추가한다. 자기참조 manifest를 만들지 않으며 승인된 core와 과거 기록을 덮어쓰지 않는다. 원래 F/G 과제의 예산을 초기화하거나 이미 완료한 경량 실행을 NCP에서 되풀이하지 않는다.
