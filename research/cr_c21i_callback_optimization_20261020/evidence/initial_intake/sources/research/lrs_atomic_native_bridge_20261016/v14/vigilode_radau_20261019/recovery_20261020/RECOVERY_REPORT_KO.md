# 독립 LRS V14 / VigilODE 복원 보고 — 2026-10-20

## 완료한 일과 과학적 범위

2026-10-19의 C10 sandbox와 C11 NCP 완료 결과를 복원했다. 이번 host의 **native 실행 0, build 0, 의존성 설치 0**이다. 현재 원시 자료로 prepare-only와 저장 결과 readback을 완료하고, NCP가 미실행이라고 남아 있던 전달 문서를 정정했다. 새로운 과학 cycle은 시작하지 않았다.

[실제 NCP 실행 receipt](../ncp_20261019T171038Z/NCP_EXECUTION_RECEIPT.json), [NCP delivery/DAG](../stages/NCP_DELIVERY_20261019.json), [이번 복원 receipt](../stages/RECOVERY_20261020.json)가 현재 상태의 근거다. [C10 최종 receipt](../stages/FINAL_DELIVERY.json)는 실행 전 당시 기록으로 원문을 보존한다. Source publication은 [`d87ba9ca25acb8a2a032154fa23057b45acd6207`](https://github.com/cosmosapjw-quantum/rei_bianchi/tree/d87ba9ca25acb8a2a032154fa23057b45acd6207/research/lrs_atomic_native_bridge_20261016/v14/vigilode_radau_20261019), NCP evidence는 `09bfe94bc270623b014bc6db78c59211152739aa`, C11 delivery는 `46a29285ad7095959bb0e5b5a10dab0fec97501f`다. 전달 문서의 최신 commit을 실행 scientific source로 바꾸어 부르지 않는다.

## 실제 NCP 결과와 launcher 실패 구분

NCP의 locked/offline release build와 focused 7시험, 같은 19개 설정의 matrix가 완료됐다. Matrix 전체 exit 0, 19완료, 실패·중단 0, native RHS 38,840회, native wall 15.824811033초, process wall 19.061708406108664초다. Sandbox는 같은 설정에 RHS 38,840회, native wall 9.146159986초다. 서로 다른 host의 단회 측정으로 속도 우월성을 주장하지 않는다. 두 host 결과는 38개 고유 설정이 아니다. 이전 84 NCP 이력·제조76·Python57·projection/SSPRK2 결과도 새로 세지 않는다.

첫 세 launcher는 single-branch fetch 때문에 `origin/BRANCH`가 stale하여 native 이전 exit 1이었다. 네 번째 launcher 전체 exit 1은 native 실패가 아니다. `prepare_and_run.py`는 exit 0으로 matrix를 끝냈고, 뒤의 system Python analyzer가 matplotlib 부재로 exit 1이었다. 분석 전용 venv의 analyzer 재실행 exit 0은 `NCP_EXECUTION_RECEIPT.json`의 보고값이다. 저장된 `analysis_r2` stdout 요약과 빈 stderr가 이를 뒷받침하며, 별도의 재실행 `EXIT_CODE` 파일은 관찰하지 못했다. Receipt는 CSV/JSON이 앞선 부분 분석과 동일하다고 기록한다. [실제 한 줄 refspec 수정](../ncp_20261019T171038Z/tools/launcher_r1_to_r4.diff)을 선택적 재현 가이드에 반영했다. Matplotlib 분석용 venv는 과거 실제 호환 수정의 기록이며 이번에는 설치하지 않았다.

Sandbox binary SHA256는 `358d254f88d196cd1ada4f71283fa3a69a068bbbf25ae28980af287575106905`, NCP binary는 `6f0a5382dd10f03850e78e83d91d7930b374c622895f5538316cc21f84e74d12`다. 서로 다른 compiler/host의 executable bytes가 같다고 요구하지 않는다. [Sandbox binary receipt](../stages/FINAL_DELIVERY.json)와 [NCP binary·toolchain receipt](../ncp_20261019T171038Z/NCP_EXECUTION_RECEIPT.json)를 따른다.

## 이번 host에서 수행한 유한 readback

저장된 정상 `prepare_and_run.py`에 C10 research input root와 VigilODE source root를 명시하고 `--offline --prepare-only`를 실행했다. Exit 0, 0.567초, 최대 child RSS 45,440 KB이며 baseline native 152파일·VigilODE 477파일·173-byte append가 검증됐다. Compile과 scientific cases는 NOT_RUN이다.

게시된 `host_compare.py`는 수정하지 않고 저장된 sandbox와 NCP payload 및 NCP C9 raw audit를 입력했다. Exit 0, 0.817초였고 결과 JSON은 보존된 [NCP_VS_SANDBOX.json](../ncp_20261019T171038Z/NCP_VS_SANDBOX.json)과 byte-identical이다. 별도 readback은 각 숫자의 유한 f64 여부와 `struct.pack('>d', value)`를 검사해 signed zero까지 확인했다.

| 비교 대상 | 수치 leaf | nonfinite | packed IEEE64 불일치 | 구조 불일치 |
|---|---:|---:|---:|---:|
| 19 raw 기록의 비시간 leaf | 316,540 | 0 | 0 | 0 |
| 19×11 endpoint 물리량 | 209 | 0 | 0 | 0 |
| refinement | 435 | 0 | 0 | 0 |
| empirical comparisons | 323 | 0 | 0 | 0 |

기존 walker와 같은 path substring `wall`, `elapsed`, `utc`, `seconds` 기준으로 raw 시간 leaf **38개만** 제외했다. Raw에는 서로 일치하는 +0 pair 63,476개, −0 pair 0개였다. 각 NCP case의 outcome은 모두 exit 0·truncated false이며 stdout/stderr SHA256를 실제 파일과 대조했다. C9 과학 유도를 새로 실행하거나 새 독립 심사를 했다는 뜻은 아니다. 이 결과의 승인은 **동일한 19개 이산 설정의 저장 결과 재현 확인**에 한정된다.

## 회수 및 보존 상태

- C10 `REI_LRS_V14_VIGILODE_C10_20261019T141050Z.tar.gz`: 59,621,285 bytes, SHA256 `7d709bcb82476fbfa11b8b68654319173740480686633b1e7d7e8b7f7e02812c`, 1,300파일 검증. 이번 전체 GET은 Dropbox였다.
- C11 `REI_LRS_V14_VIGILODE_NCP_C11_20261019T171038Z.tar.gz`: 50,236,168 bytes, SHA256 `bcb4526ccb14584161f479faeb4dcd8db3656f5dc7966693c75085419e958995`, 175 payload 검사. 이번 전체 GET은 Drive였다. Drive ID `1u4Wq5K1JjtoslPn-TNIMF60JA7q8fEbK`, Dropbox ID `id:BSpOijBcT10AAAAAAD_R2Q`.
- 과거 C11 양쪽 전체 readback은 유효한 과거 근거로 보존한다. 오늘 양쪽 provider 모두에서 다시 회수했다고 주장하지 않는다.
- C10/C11 source·raw·transcript, 원 C10 FINAL_DELIVERY, SOURCE_DELTA 및 runner는 변경하지 않았다. Git publication·새 recovery archive·Drive/Dropbox ACK 및 dual readback의 실제 완료 여부는 작은 최종 `stages/RECOVERY_REMOTE_ACK.json`에 기록한다. [복원 receipt](../stages/RECOVERY_20261020.json)는 그 기록을 가리키며, 이 pointer 자체로 성공을 예측하거나 주장하지 않는다. 최종 ACK 파일은 실제 확인 뒤 root가 작성하며 이번 overlay에는 아직 없다. 이 문서나 복원 receipt 자신의 final-commit hash를 기록해 자기참조하지 않는다.

## 실행·readback 근거와 문서 검토

이번에 실제 실행한 [유한 f64/packed IEEE64 readback 결과](evidence/RECOVERY_NUMERIC_READBACK.json), [prepare-only receipt](evidence/PREPARE_RECEIPT.json), [별도 Astra-agent 문서·근거 검토](evidence/REVIEW_20261020.json)를 함께 보존한다. 검토자는 R1 증거 표현과 R2 역사적 pointer 정정을 조건으로 수용했고, root가 정확한 수정본을 직접 확인해 두 지적의 해결을 수용했다. 두 번째 reviewer pass, 새 이론 심사나 다른 모델 계열의 과학적 합의를 주장하지 않는다.

[실제로 실행된 helper](executed/check_recovered_numbers.py)는 원래 local 경로를 포함한 원문 그대로다. 이 보존본을 이식 가능한 runner로 수정하거나 재실행하지 않았다.

## 최신 VigilODE upstream 후보의 관찰 범위

이번 intake에서 확인한 upstream PR 본문과 source pointer는 아래와 같다. 현재 LRS에 적용한 pin은 `8a8bd409b1d96c7b7421f496d229e119fd3d284e`, LU 의존성은 faer 0.24.4 그대로다. 아래 항목은 후속 후보이며 자동으로 pin을 바꾸거나 native를 재실행하지 않았다.

| PR | 관찰한 HEAD | 본문에 보고된 후보 범위 |
|---|---|---|
| [PR #73](https://github.com/cosmosapjw-quantum/vigilode/pull/73) | `3c0157910076ce552283c831c2be000c66671fab` | FixedWidth2 banded kernel과 bit-identical Jacobian/shift의 exact-factor cache; 수정한 benchmark adapter의 supplied JVP |
| [PR #74](https://github.com/cosmosapjw-quantum/vigilode/pull/74) | `15c43ce76734d0a560fcec5909ac49f1e6f2d347` | supplied JVP를 받는 opt-in native coupled companion step; 공유 basis/J0V, full-space residual 및 별도 embedded time-error 판정 |
| [PR #75](https://github.com/cosmosapjw-quantum/vigilode/pull/75) | `6c945b6c6e0e024d8f733c21da8d35fbcc3c5f2a` | 수렴한 iterate의 불필요한 JVP를 생략하는 residual-first coupled step과 JVP-budgeted fallback 후보 |

이는 PR 본문에서 관찰한 upstream supplied-JVP/coupled/residual-first 후보의 기록이다. 해당 본문의 시험·timing·readback 주장은 이번에 새로 독립 readback한 LRS-native 증거가 아니다. 같은 19개 LRS 설정의 재현 판정이나 일반 정확도·stiff·양수성 주장에 추가 근거로 합산하지 않는다.

## 판정과 다음 의무

일반 source-on 차수·HeIII endpoint 단일 차수·uniform stiff 정확도·일반 양수성·Case B·full EoR·signed Bianchi·positive CMB/비영 boundary는 HOLD이며 production admission은 NOT_ISSUED다. 같은 설정의 두 host 일치는 새 일반 정확도·stiff·양수성 정리를 입증하지 않는다. 같은 19개 NCP 실행을 미완료로 넘기지 않는다. 후속 연구는 사용자가 선택한 범위에서 시작하며, 이번 재개에서 과거 완료 작업을 새로 실행·집계하지 않는다.
