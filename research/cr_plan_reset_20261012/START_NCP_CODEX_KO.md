# 현재 NCP handoff — 과학 산출물 우선 계획, 2026-10-12

`cosmosapjw-quantum/bass_cr`의 `research/cr-scientific-fast-track-reset-20261012` branch를 현재 계획으로 읽어라. 이전 H 게시 기준은 `8d80abde76f6c259cac031353d1928fccb5f191c`다. 실제 branch head와 commit을 읽고 이 기준의 descendant임을 확인하라. 기존 사용자 작업을 reset/clean/stash하지 마라.

이번 요청은 감사에 따른 계획 변경이다. **현재 새 NCP 과학 실행은0이며, 아직 시작하지 않은 H 전체9600 qualification은 보류한다.** 이전 H START의 `--execute` 안내는 현재 자동 실행 지시가 아니다. 이전 NCP_READY의 준비 PASS는 보존되지만 실행 우선순위를 뜻하지 않는다.

## 지금 할 일

1. root AGENTS와 `research/cr_plan_reset_20261012/{PLAN_AND_RESULTS_KO.md,HANDOFF.json,NEXT_DAG.json}`를 읽어라.
2. 같은 H unit의 실제 기존 reservation/run/return을 한 번 확인하라. 새 폴더로 실행 예산을 초기화하지 마라.
3. 진행 중인 원래 wrapper가 있으면 중복 실행하지 말고 실제 상태를 보존하라. 완료된 원래 run의 수집이 빠졌을 때만 그 source에 결속된 기존 `--collect` 절차를 사용하라. 이미 수집된 run은 그 결과를 읽고 반환하라. 모호한 PID/소유권으로 무관한 프로세스를 종료하지 마라.
4. 기존 run이 없으면 `NO_EXISTING_RUN_NEW_DISPATCH_DEFERRED`로 한 번 반환하고 종료하라. 같은 부재 확인을 반복하는 작업을 만들지 마라. NCP에서 새 runner, mock, scalar 재검산, 파일럿, benchmark를 시작하지 마라.
5. 반환할 실제 결과가 있으면 원래 값·오류·reservation/completion·실제 exit를 보존한다. 새 결과의 독립 검토는 그 값의 범위에 한정한다. 원래 F/G gate는 유지한다.

가벼운 구현·분석·테스트와 다음 연구 설계는 이 ChatGPT 연구 스레드가 맡는다. NCP에 미완성 개발을 다시 구현하게 하지 않는다. 현재 완료된 `evaluate_cached_response.py`를 검증 목적으로 반복 실행하지 마라. `results/CACHED_RESPONSE.json`과 actual execution receipt를 읽으면 충분하다.

## 앞으로 NCP를 재활성화할 때

구체적인 CR 과학 질문 또는 사용자가 선택한 독립 성능 연구 목적, 필요한 출력, 기존 값·경량 방법의 부족, 예상 비용과 실제 병렬 독립성, source 및 누적 예산을 하나의 activation 기록에 먼저 묶는다. 기존 승인의 범위에서 이 조건이 충족되는 다음 실제 작업을 정하되 준비됐다는 이유만으로 자동 dispatch하지 마라.

원래 H qualification을 선택한다면 그8논리생성/76800열/전체900초/자동retry0 및 정확한 runtime/resource/원시 값 비교 계약을 그대로 적용한다. 다른 과학 workload를 선택한다면 H의29×2 배치나 예산을 임의로 재사용하지 말고 그 workload의 계약을 사용한다. F retry·pulse·expm·solve·G frontier로 이어지는 자동 edge는 없다.

## 추가 첨부 없는 복구

이 수정본의 완전 전달 ZIP에는 위 새 계획과 분석, 사용자 감사 원문, 기존 H 완전 ZIP이 원본 bytes 그대로 들어 있다. 새 ZIP의 최상위 START와 이 문서를 먼저 읽어라. 내부에 보존된 H START는 역사적 원문이며 현재 일정 지시를 덮어쓰지 않는다.

기존 H의 정확한 baseline은 다음과 같다.

- `CR_PHYS02H_20261011_7907a2f5_HANDOFF.zip`,68158856B
- SHA256 `fbc505a9515d483c84c984eaf7a9666ddf1a55e3d94c57f43e013ab34d557adf`
- Drive ID `1KChWc0w0EFcuArlpEEoDCSja67p4yKGE`
- Dropbox ID `id:BSpOijBcT10AAAAAAD4MiA`

이미 같은 bytes가 있으면 재사용한다. 계정·rclone remote를 추측하지 않는다. 새 source 복구는 안전한 entry 집합과 정확한 manifest를 확인하며 기존 파일을 덮어쓰지 않는다. 자료가 필요하지 않은 상태 보고만을 위해 전체 H를 복원하거나 옛 wrapper plan을 재실행하지 마라.

필요한 반환은 새 additive branch/draft PR과 하나의 결과 묶음으로 작성한다. 원래 history를 덮어쓰거나 merge/force push하지 않는다. 실제 새 반환이 있을 때 create-only Drive/Dropbox 백업과 START를 함께 올리고 provider 성공·ID·size·제공 checksum으로 R1을 닫는다. 선택 checksum이 없다는 이유로 재다운로드하지 않는다.

CR-off의 source0/provider-calls0는 해당 receiver에서 확인할 계약이며 이 문서만으로 구현 완료를 주장하지 않는다. CR-on의 미지원 입력은 typed unavailable로 반환하고0으로 숨기지 않는다. 고정 CR kernel의 응답을 Bianchi 방향 수송 또는 전체 우주론 이력으로 승격하지 마라.
