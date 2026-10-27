# R8: 현재 단위의 이론 채택 판정

**판정은 `ADOPT_SCOPED_THEORY_FOR_BOUNDED_IMPLEMENTATION`이다.** 고정 PHYS02 모델의 H/He 전자 성분 식별식, He 부모 사건의 부분적 affine family, 같은 100 K 조건부 상태의 native25 소비자와 유한 proper-time 장부를 구현에 채택한다. 아직 새 수치 fit·projector·consumer를 실행하지 않았으므로 수치 채택은 C5–C9 결과를 기다린다.

## 주장별 근거와 채택 범위

| 결과 | 현재 근거 | 판정 |
|---|---|---|
| 세 기저와 세 저장 에너지 모멘트의 3×3 식별 | THEORY 식 1–12의 직접 유도, 원 source 코드·저장 모멘트·문헌의 정의 대조, R6 독립 심사 | 모형 내 식별 절차 채택. 실제 계수·conditioning·holdout PASS는 미실행이다. |
| 원 Q8 및 선형 barycentric 사상의 기저별 분해 | 고정 원 source projector의 선형성, THEORY 식 13–16 | 원 total atom을 바꾸지 않는 별도 H/He attribution 채택. 실제 atom별 잔차는 고정 허용치로 확인해야 한다. |
| He 선택 전자 수와 부모 사건 family | s+p+2d=N_eHe, 명시적 비음성 조건과 종·전하 장부 | affine family 채택. 선택 support의 필요 조건이며 실제 joint kernel의 충분조건으로 쓰지 않는다. 실제 s,p,d·파트너 에너지/시계/응답은 null이다. |
| 동일 상태의 RR 결합·native25 사상 | 명시적 nb=8750/47 m^-3, 원 저장 RR와 새 source 부모의 서로 다른 label, R6 | baseline+delta+독립 RR 항 및 p,d 계수 채택. 실제 full native25와 donor work는 null이다. |
| proper-time prefix와 observation-bin 사상 | q(t)=tA, J(a,b)=(b−a)(b+a)A/2, 원 저장 response bin | prefix는 비가산 진단이다. disjoint observation bin은 이전 cohort의 생존 반응을 포함하며 bin 시작에서 clock을 재설정하지 않는다. |
| 원자 결합에너지 convention sidecar | source H 13.605693122994 eV와 native/RR H 13.6 eV의 차이, unresolved He partner/branch lift 분리 | literal residual과 실제 미정 work를 따로 보존한다. retained photon은 원 atom port 그대로 보존한다. |
| 조건부 caloric 계산 | p=d=0과 명시적 EOS 조건에서 prefix·bin의 정확한 비율 및 log1p 표현 | 두 named fixture만 채택. frozen 100 K response에 feedback하지 않으며 physical heating 완료가 아니다. |

## 독립 검토와 판별 계산

R6는 물리·수학적 검토 12개 주제에서 `PASS_SCOPED_THEORY`, 열린 blocker 0을 반환했다. 수식 기호와 계약 변수의 alias, 문서 경로, z=0의 나머지 하한 표기 세 건을 교정했다. 원 R5 문서와 교정 기록은 보존한다.

R7 Wolfram evaluator의 실제 한 번의 평가에서 상·하한 모멘트 도함수 8개, 영폭 모멘트 4개, 핵종·baryon·전하 4개, 에너지 sidecar 1개, EOS 2개, proper-clock 2개, 양의 급수 도함수 1개가 모두 0으로 나왔다. 합계 **22/22**다. 이는 ii>0, 0≤a≤b, 양의 EOS 분모에서의 대수 검산이다. 앞선 Wolfram context 조회의 내부 오류는 원 응답으로 보존했으며 evaluator 실패나 수치 물리 결과로 바꾸지 않았다. 원격 CPU는 측정 불가로 null이다.

## 후속 실행의 정확한 의무

고정 세 recovery band에서 실제 계수를 한 번 식별하고, 세 unused holdout·원 3201개 atom·target별 N/E·독립 reference를 고정 허용치로 확인한다. 실패하면 해당 결과를 `UNRESOLVED`로 남기며 기저 수, support, 허용치 또는 원 source를 자동으로 바꾸지 않는다. 실제 C4 예산·입력·소스·host 승인이 있어야 실행한다. 새 단위 CPU40 s는 이전 잔여와 분리한다.

새 strong no-go는 제시하지 않는다. 제공된 inclusive marginal만으로 실제 exclusive branch가 아직 특정되지 않았다는 현재 입력 판정과, 향후 joint source가 주어지면 적용할 수 있는 구성적 family를 함께 보존한다.

## 상태

R8 사전 확인에서 actual AGENTS·local/remote HEAD·17 source pin·직전 source/backup receipt가 일치했다. 중앙 qualified HEAD는 b99a9468abd53de77ddae36d93180e60072885bc이며 **28/88**, 88 nodes/17 edges, 이번 CR 효과 0이다. N4/N5 PARTIAL_OPEN, N6/N7 PREDECESSOR_GATED, L4false와 global completion/error/budget/currency null은 유지한다. 현재 단위만 마치고 후속 과학 노드는 시작하지 않는다.

근거: [THEORY_KO.md](../THEORY_KO.md), [R6 독립 심사](../review/R6_INDEPENDENT.json), [실제 CAS 결과](../symbolic/RESULT_V1.json), [고정 계약](../CONTRACT.json). 실제 이 단계 게시·백업 identity는 생성 후 publication/R08_RECEIPT.json에 결속한다.
