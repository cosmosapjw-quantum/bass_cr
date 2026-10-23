# N4 수신 대응 독립 검토

## 판정

**PASS_SCOPED_NEW_ADMISSION_MAPPING — blocking finding 0.**

`CR_N4_C23B_CUTOFF_BINDING`의 원 입력·정리 가정·에너지 소유권을 완료된 C23C에 연결하는 이번 수신 대응은 유효하다. 중앙 wrapper의 `COMPLETE_SCOPED`와 claim gate의 `CONSUMER_ADMITTED`를 승인한다. 승인 대상은 **`C23C_FROZEN_FIVE_LABEL_CALORIC_V1` 및 저장된 18개 요청**이다. 향후 N6 RHS, IGM thermal history, full21 atomic provider와 physical stopping은 이 판정에 포함되지 않는다.

검토자 `/root/n4_admission_review`는 구현자의 자기 판정과 분리된 읽기 전용 독립 agent다. 고정 handoff, 실제 C23C code/theory/CONTRACT, 저장 결과와 기존 C9를 읽고 새 수신 문서 및 중앙 diff를 검토했다. 기존 18-case sweep, KC solver/suite, C9 audit, source quadrature 또는 ODE를 실행하지 않았다. 이번 검토는 새 수신 대응에 대한 한 번의 제한된 검토이며 기존 과학 결과 전체에 대한 새 blind proof audit가 아니다.

## 물리 대응

| 항목 | 검토 결과 |
| --- | --- |
| 공급자·단위 | 저장 C23B atoms의 byte identity, absorbing target당 proper-second weight, bath-frame energy를 유지한다. `Qe`는 부피·시간당 전자수 측도이고 소비자의 `mu_s`는 `V * duration * Qe`의 기대 전자수 측도다. V와 노출시간을 한 번씩 적용한다. |
| 정규화 | HI/HII/HeI/HeII/HeIII 다섯 초기 fit label을 모두 선언한다. Density 또는 reference abundance 중 하나를 사용하며 두 표현을 동시에 허용하지 않는다. 누락 species를 자동으로 0으로 채우지 않는다. |
| KC4 가정 | 비음수 population과 양의 총 핵수에서 `Ne0 >= 0`, `NB = Nnuc + Ne0 >= Nnuc > 0`이다. `T0 > 0`이므로 `UB > 0`; 유한 source와 비음수 노출은 유한 비음수 atoms를 만든다. `chi >= 3/2` 및 fresh-inventory construction이 실제 code와 일치한다. |
| 노출·초기 조건 | 초기 electron은 명시된 charge-neutral thermal reservoir이고 초기 resolved nonthermal measure는 0이다. 처음 존재한 target만 source를 만들며 daughter를 같은 노출에서 재처리하지 않는다. 점유 target의 depletion 검사는 시간오차 상계가 아니다. |
| Cutoff endpoint | 원 적분의 endpoint를 `thermal=[0,Kc]`, `active=(Kc,infinity)`로 구체화했다. 기존 B12와 실제 solver의 equality-thermal 규칙에 일치한다. |
| 에너지·EOS | `Uall,kin`은 병진 kinetic inventory이며 binding/radiation/escape를 섞지 않는다. 원 미분 EOS는 smooth variation 항등식으로 보존하고 실제 atomic 소비자의 B15 유한 온도 갱신과 구별한다. 분할만으로 physical deposition을 주장하지 않는다. |
| 정리 범위 | KC4를 재사용한다. 연속 KC3 C_eff certificate, KC6 contraction/uniqueness, 변경 source에 대한 고정-spectrum branch continuation은 승인 근거가 아니다. 새 cutoff 정리의 novelty를 주장하지 않는다. |
| 실제 승인 입력 | 새 `N4_ADMISSION.json.saved_numeric_approval.input_contract`는 복원 C23C `CONTRACT.json`과 정확히 일치한다. 세 z × 세 T0 × 두 chi의 18개 명시 요청과 조건부 API 정의역을 구별한다. |

## 재사용한 검증 근거

Science C `54c2ff11e8308d45c545679301059bc1fcf268eb`, documents D `6c760dc1f0ce5820263b276fa7263e87c1285bd2`, terminal E `910a9a92e4bf5a9d77b6ff60365d94559f54cbbd`를 구별해 사용했다. 기존 main 실행 identity는 `c6174a7a78247a1ee89dfeb152444ba49e2094004926bfe0597eb613e30b7faf`다.

기존 main18 SUMMARY/CASES, guarded-source targeted5 SUMMARY, 독립 Decimal80 C9 RESULT 및 C9 review status를 실제로 읽었다. 저장 main의 case당 13개 exact rational residual, 독립 검토 977개 비교와 기준 `1e-40`, 최대 상대차 약 `1.2507493130458459e-78`, C9-F1의 closed 상태를 재사용한다. 이 수치들을 이번에 재계산한 것으로 기록하지 않는다. 현재 guarded binding과 실행 v1의 차이는 요청 object/unknown-field 거절 guard이고, 유효 saved18 scientific path가 변하지 않았다는 기존 근거와 실제 code diff가 대응한다.

기존 C9의 10개 input/output pin을 복원한 실제 bytes에서 모두 확인했다. 새 274-object manifest는 path 중복이 없고 그중 source/contract/code/solver/CASES/C9 RESULT 6개 핵심 항목을 새 manifest와 직접 대조했다. 전체 274개에 대한 구현자의 구조 검사는 재사용하며 이 검토를 새 독립 전수 재해시 감사로 확대하지 않는다. 해시 검사는 위 물리 가정 대응이나 기존 수치 검증의 대체 근거가 아니다.

## 중앙 변경과 예산

원 중앙 baseline은 `0f9d9df825be1dac9ca9bdf73cdc2e8908bcba17`이다. 독립 JSON diff에서 변경 경로는 다음 두 개뿐이다.

- `/nodes/6/plan_status`
- `/nodes/6/observed_completion`

원 저자 계약 40개, 나머지 wrapper 39개, authority 7개, integration edge 17개가 그대로다. 원 N4 계약의 OPEN/NOT_RUN과 null budget은 당시 snapshot으로 유지한다. 원 handoff bytes는 새 overlay의 suffix로 보존되고 PR plan에서는 N4 행 한 개만 바뀐다. 기존 HE-X1 완료 상태를 포함한 다른 wrapper와 stopping/N5/N6 선행 관계를 변경하지 않는다.

예산 ledger의 9개 distinct historical run은 각각 outcome hash, dispatch record, worker wall/CPU time field가 복원된 원 기록과 일치한다. Dispatch wall 합계 `27.228573164997215 s`, 알려진 worker wall subtotal `22.34583505801129 s`, 알려진 worker CPU subtotal `11.701636483 s`의 직렬화·합산도 일치한다. 세 수치를 서로 합쳐 전체 비용으로 해석하지 않는다. 전체 inherited_spend/remaining/currency는 계속 null이며 dispatch의 worker/coordinator CPU 번호를 시간으로 합산하지 않는다.

## 네 축과 종료 범위

| 축 | 이 검토 시점의 상태 |
| --- | --- |
| EXECUTION | 기존 C23C 과학·C9 근거 재사용, 이번 새 과학 실행/과거 science replay 모두 0 |
| PUBLICATION | 기존 C/D/E 재사용, 새 packet 실제 commit·push는 parent의 후속 게시 기록 대상 |
| BACKUP | 검증 복원 및 기존 provider 근거 재사용, 새 packet provider ACK는 후속 기록 대상; 기존 Drive `UNKNOWN_NO_ACK` 보존 |
| DAG | N4 wrapper의 scoped completion 승인; stopping과 actual N5 coverage 및 N6 coupling 승격 없음 |

후속 작업은 이 판정·reviewer를 pending 상태 필드와 관련 문서에 기록하고 실제 expected-SHA 게시 및 provider 응답을 영수증으로 남기는 것이다. 이는 이미 수행된 검토와 실제 배송을 기록하는 제한된 갱신이다. 물리 범위, 저장 입력 집합, source identity, endpoint 규칙, 다른 wrapper나 원 저자 계약 변경을 승인하는 것은 아니다. 또한 requested_model을 parent가 실제 요청한 `gpt-6.1-sol`로 기록하되 observed_model은 UNOBSERVED로 유지하고, 같은 CASES bytes의 canonical Git path/immutable URL 및 기존 C/D/중앙 0f9에 연결하는 EVIDENCE local-to-repository prefix map을 추가할 수 있다. 이러한 상태·locator·요청 metadata 확정은 JSON에 열거한 범위에 한하며 마지막 구조 비교로 물리 영향 diff가 없음을 확인하면 충분하다. 기존 계산 재실행이나 추가 독립 검토 루프는 요구하지 않는다.

Physical heating, stopping time, global_error_bound 및 전체 목표 완료율은 null이다. 다른 대화 전체는 UNAVAILABLE, 외부 runtime은 UNOBSERVED, 원 nuclear-network PNG는 NOT_RECOVERED_NOT_READ다. 다음 물리 노드는 별도 `CR_N4_STOPPING_KERNEL` 계약이며 실제 rate/isotope coverage 노드도 OPEN으로 유지한다.

검토한 후보 파일의 정확한 byte size/SHA256, 원 C9 10개 pin, 판단 항목과 한계는 동봉 `INDEPENDENT_ADMISSION_REVIEW.json`에 기록했다. 본 검토 산출물 이외의 파일·Git·백업 object를 변경하지 않았다.
