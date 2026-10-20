# VigilODE PR71의 후속 비교 실행: C21H 추가 intake

확인일: 2026-10-19 UTC. GitHub publication head: `9f80e38dd6c7e5cf002d2436f6cf5fb2cc372858`.

**새 실행 결과가 게시되어 있음을 확인했다.** `strict_solver_comparison_20261019/runs/39257390707`의 작은 보고서·영수증 6개와 이전 run의 `BLOCKER.json`을 GitHub에서 새로 읽었다. 이 7개 UTF-8 payload, 총 14,953 bytes의 SHA256과 Git blob SHA를 직접 계산했고 GitHub가 반환한 blob 7개와 모두 일치했다. 원문과 계산값은 `VIGILODE_LATE_DELTA.json`에 함께 보존했다. 정확도 CSV, 큰 reference/model 파일, 실제 solver raw 전체는 이번 제한된 intake에서 읽거나 재실행하지 않았다.

## 1. Source와 실행 상태

Root가 이미 새 GitHub compare로 확인한 `ac1cd2a4738c2441c92e5fdae5f70aba35e53544 → 9f80e38dd6c7e5cf002d2436f6cf5fb2cc372858`의 5개 commit delta를 재사용했다. 변경은 모두 `research/strict_solver_comparison_20261019/` 아래이며 production crate 변경은 0개라는 기존 확인을 다시 수행하지 않았다.

새 run의 `EXEC_SOURCE_COMMIT.txt`는 `87df9b071c3a3a7828e999e553a088af5860d274`를 기록한다. 동시에 `SOURCE_REPAIR_RECEIPT.json`은 campaign의 `scripts/campaign.py`와 `src/main.rs`에 두 변경을 `APPLIED`로 기록한다. 따라서 실행 identity는 **기록된 commit과 두 campaign repair의 조합**으로 표현해야 한다. 변경 후 source SHA256은 각각 `6da98c3baf586aeabc14ad18afa06b5e1d371f1d9a4551a8269212a7d022977c`, `4308cd33647953f76a6dc50a09c192e975219763b73abc9fc7b0661f9c623eb2`다. 이는 검증한 영수증에 적힌 값이며 이번 intake에서 해당 두 source 파일이나 compiler 입력 전체를 독립 복원했다는 뜻은 아니다. [실행 commit][exec] · [repair 영수증][repair]

| 구분 | 실제 읽은 기록 | 판정 범위 |
|---|---|---|
| 이전 run `39255702592` | BLOCKED, `TypeError: Object of type int32 is not JSON serializable` | 해당 실행의 직렬화 blocker를 역사 기록으로 유지한다. |
| 새 run `39257390707` | `EXIT_STATUS`: exit 0, stage complete | 게시된 실행 완료 영수증이다. |
| 새 SUMMARY | `COMPLETED_BOUNDED_CAMPAIGN`, 계획·보존 756 cells, `ok=756`, structurally admitted 756 | 보고서상의 실행 및 구조적 admission이며 정확도 목표 통과와 구분한다. |

[이전 blocker][blocker] · [새 종료 상태][exit] · [새 summary][summary]

## 2. 정확도: 보고된 통과 수와 그 의미

| Solver arm | 보존/구조적 admission | 보고된 `R_up<=1` |
|---|---:|---:|
| VigilODE fast | 252/252 | 207/252 |
| Diffsol BDF | 252/252 | 39/252 |
| Netlib DVODE | 252/252 | 16/252 |
| 전체 | 756/756 | 262/756 |

전체 `R_up<=10`은 543개로 보고된다. Accuracy 선택 단계는 32개 READY, 4개 `HOLD_MISSING_ACCURACY_ARM`이다. 모든 실행이 완료됐다는 사실과 모든 arm이 모든 목표 정확도를 달성했다는 주장은 서로 다르다. 위 수치는 **게시 summary의 reported 값**이며 756행 accuracy CSV로 재계산한 값으로 승격하지 않는다. [Summary][summary]

보고서는 reference radius를 Radau ladder와 독립 LSODA 사이의 경험적 차이로 정의하며 엄밀한 전방오차 인증으로 보지 않는다. `R_up>1`도 관측 격자의 global target miss이고, local error를 제어하는 solver의 명세 위반으로 자동 분류하지 않는다. 따라서 이 수치만으로 C21H의 특정 연속방정식·물리 수지·global 오차를 인증할 수 없다. [보고서 제한][report]

`PARITY.json`의 6개 benchmark, 각 2개 sample에서 직접 읽은 필드의 최대값은 `rhs=2.0770189841780673e-16`, `jac=0`, `complex_step_jvp=7.384999274592463e-14`다. 이는 12개 게시 기록에서 다시 집계한 값이다. 새 parity 실행이나 C21H native 화학의 RHS/Jacobian 검증으로 취급하지 않는다. [Parity 원기록][parity]

## 3. Timing: 제한된 동일 호스트 비교

보고서에는 유효 timing process 1,152개와 완성된 paired comparison 96개가 있다. 읽은 Markdown 표의 96행을 직접 집계하면 **`matched_achieved_factor2` 12행, `same_target_only` 84행**이다. 후자는 동일한 요청 목표에 도달하려 한 비교이며 달성 오차가 맞았다고 주장하지 않는다. 95% 구간은 pointwise이고 다중비교 보정이 없다. Timing authority도 `diagnostic_shared_runner`로 명시되어 있다. [Summary][summary] · [시간비와 제한][report]

시간비는 baseline/candidate다. 다음 값은 표에서 읽은 reported 사례이며 solver와 문제·격자·backend 구성에 따라 방향이 달라진다.

| 문제·격자·목표 | Baseline / candidate | 보고된 시간비 | 보고된 달성 오차 조건 |
|---|---|---:|---|
| Robertson endpoint, `1e-8` | DVODE / VigilODE | 2.354 | factor 2 이내 |
| Robertson endpoint, `1e-8` | Diffsol / VigilODE | 1.535 | factor 2 이내 |
| Brusselator 200 endpoint, `1e-4` | DVODE / VigilODE | 0.149 | factor 2 이내 |
| Brusselator 200 endpoint, `1e-4` | Diffsol / VigilODE | 7.838 | factor 2 이내 |

VigilODE fast는 요청 출력 시각에 step을 맞추고 Diffsol/DVODE는 dense output을 사용할 수 있다고 보고서가 설명한다. Brusselator에서 Diffsol은 FaerLU dense, DVODE는 banded 경로다. 이 구성 차이를 포함한 측정이므로 방법론 전체의 보편적 순위나 C21H의 속도비로 옮기지 않는다. 새 allocation/Callgrind 측정도 이 campaign에는 없다. 보고서와 summary의 `production_promotion=false`, `global_error_guarantee=false`를 그대로 유지한다. [보고서][report]

## 4. C21H 결정에 미치는 영향

새 bounded campaign은 세 arm 모두 완료된 결과를 보고하므로, 이전의 특정 실패 기록만으로 Diffsol 경로가 전혀 실행될 수 없다고 일반화해서는 안 된다. C21H가 VigilODE Rodas5P를 고정 후보로 유지하고 Diffsol BDF를 독립 비교 후보로 구현한 선택은 유지한다. 이 판단은 새 benchmark를 C21H 화학 결과로 대체한다는 의미가 아니다.

C21H의 VigilODE 실행 pin은 `8a8bd409b1d96c7b7421f496d229e119fd3d284e`로 유지한다. 미시물리 native owner도 기존 `rei_bianchi@6ea2b1b4b3875c9163cafc45efe720afded43fc4`로 유지한다. 새 campaign repair를 적용하거나 PR71 중간본을 C21H에 merge하지 않았다. C21G reference ladder와 C21H native/실제 NCP 판정은 해당 독립 실행 증거로 결정하며, 이 intake로 변경하지 않는다. Full48, source-age/spectral/angular, Case B, signed Bianchi, full EoR, standalone Grackle driver parity는 기존 HOLD를 유지한다. C21H 전역 오차 상계는 `null`이다.

## 5. 게시·백업·DAG 상태

| 단계 | 게시 | 백업/보존 | DAG |
|---|---|---|---|
| VigilODE 새 작은 기록 7개 읽기 | 고정 GitHub head에서 확인 | 원문 7개와 SHA/Git blob을 새 JSON에 보존; 외부 저장소 사본은 이번 제한 intake의 확인 범위 밖 | LATE_RESULT_INTAKE_DONE |
| C21H late intake 2파일 | root의 새 게시 단계 PENDING | root의 create-only 백업 단계 PENDING | 기존 source/구현/닫힌 검토 재개 없음 |
| C21H native/정확도/성능 채택 | 이번 intake의 실행 증거 없음 | 별도 실제 영수증 필요 | native 또는 과학 단계 승격 없음 |

[summary]: https://github.com/cosmosapjw-quantum/vigilode/blob/9f80e38dd6c7e5cf002d2436f6cf5fb2cc372858/research/strict_solver_comparison_20261019/runs/39257390707/SUMMARY.json
[report]: https://github.com/cosmosapjw-quantum/vigilode/blob/9f80e38dd6c7e5cf002d2436f6cf5fb2cc372858/research/strict_solver_comparison_20261019/runs/39257390707/REPORT_KO.md
[parity]: https://github.com/cosmosapjw-quantum/vigilode/blob/9f80e38dd6c7e5cf002d2436f6cf5fb2cc372858/research/strict_solver_comparison_20261019/runs/39257390707/PARITY.json
[exec]: https://github.com/cosmosapjw-quantum/vigilode/blob/9f80e38dd6c7e5cf002d2436f6cf5fb2cc372858/research/strict_solver_comparison_20261019/runs/39257390707/EXEC_SOURCE_COMMIT.txt
[repair]: https://github.com/cosmosapjw-quantum/vigilode/blob/9f80e38dd6c7e5cf002d2436f6cf5fb2cc372858/research/strict_solver_comparison_20261019/runs/39257390707/SOURCE_REPAIR_RECEIPT.json
[exit]: https://github.com/cosmosapjw-quantum/vigilode/blob/9f80e38dd6c7e5cf002d2436f6cf5fb2cc372858/research/strict_solver_comparison_20261019/runs/39257390707/EXIT_STATUS.json
[blocker]: https://github.com/cosmosapjw-quantum/vigilode/blob/9f80e38dd6c7e5cf002d2436f6cf5fb2cc372858/research/strict_solver_comparison_20261019/runs/39255702592/BLOCKER.json
