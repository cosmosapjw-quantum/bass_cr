# 독립 검토의 범위와 중간 판정

검토자: `/root/independent_review` (별도 agent). GPT-6 Astra v4.0.0 연구·코딩 하네스와 Phase 8 독립 decision gate를 적용했다. 후보 유도·구현 및 owner의 검증 설계에는 참여하지 않았다. 검토를 위해 별도 기준 계산을 설계했다. 같은 기록 입력을 사용하므로 이 검토는 원 입력의 물리적 정확성에 독립적인 인증을 제공하지 않는다.

**중간 판정:** 신규 finite-age 수학, 코드, 저장된 입력의 새 산술 비교에 범위를 한정하면 치명적인 문제를 발견하지 않았다. 최종 판정은 owner가 고정한 통합 계획·주장 manifest를 읽은 뒤 별도 `DECISION.json`에 기록한다.

## 수학과 정규화

고정된 비음의 열 가중 지연 확률측도, 양의 유한 `H0`, `T>0`, `[0,T]`의 source 이력, 0인 prehistory와 별도 초기 비열적 stock 부재라는 전제가 명시되어 있다. `p,R,S`는 확률질량과 절단 모멘트이며 source 평가점은 `T*R/p`이다. `T*(1-R/p)`는 지연이므로 두 값을 서로 바꾸어 쓰면 안 된다. 새 코드와 기록은 이를 올바르게 구분한다.

`P+ = H0*p*q(T*R/p)`의 일차 Taylor 항은 제한 측도의 중심에서 소거된다. 따라서 절대오차는 `H0*M*T^2/2*(S-R^2/p)`로 제어된다. 끝점의 일차 보정과 오차계수 차이는 `(p-R)^2/(2p)`이므로 비음이다. 이는 동일한 곡률 정보에 대한 상계 비교이며 개별 source의 실제 오차 순위를 증명하지 않는다.

`q(0)`는 적분구간의 실제 끝점값이다. `q(t<0)=0`으로 정했다고 `q(0)`까지 삭제하지 않는다. 마찬가지로 현재 `q(T)=0`이라는 이유로 지연 가열을 0으로 만들지 않는다. `qstar>0`는 명시한 이력 진폭이고, `H0*qstar/P_ref`는 선택한 reference에 대한 비율이다. 실제 CR 가열분율, gas ionization knot, 초신성 CR efficiency와 서로 대체할 수 없다.

미분 가능성은 닫힌 구간 내부 이력에 대한 `C2` 전제다. 불연속 shutoff를 가진 이력에 이 곡률 상계를 그대로 적용하지 않는다. 코드의 `closure_budget`은 제공된 곡률 상계와 reference 비율을 곱하는 함수이며 그 입력의 물리적 타당성을 스스로 검증하지 않는다.

`p=0`이면 source callback을 평가하지 않고 0을 반환한다. `p>0`의 분산 0, 순간 kernel, `tau=T` 끝점 원자측도도 식과 코드가 일치한다. `H0=0`은 확률측도 정규화 전의 별도 무가열 경우이며 현재 cache의 적용범위 밖이다.

## 실제 독립 실행

`independent_reference.py`는 stdlib `Fraction`만으로 기준 수학을 계산하고, 새 `finite_age_closure.py`만 검사 대상 모듈로 읽는다. 기존 evaluator와 owner test suite를 import하거나 실행하지 않았다. 기준 경로는 직접 이산 지연측도 합과 별도의 닫힌형 산술이다.

`run_independent_reference.py`로 한 번 실행했다. 실제 종료 코드는 0, wall time은 `INDEPENDENT_REFERENCE_ACTUAL_EXECUTION.json`에 기록된 약 0.0453초다. `INDEPENDENT_REFERENCE_RESULT.json`에 결과를 보존했다. 1004개의 세부 단정은 아래 제한된 위험을 검사한 packet 필드 비교까지 포함한 수이며, 독립 과학 실행 1004회를 뜻하지 않는다.

- 양 끝점과 구간 밖 late mass를 포함하는 새 비대칭 원자측도에서 직접 가열합, 평균지연 근사, 일차 보정 및 오차계수를 비교했다.
- 상수·선형 이력의 정확성, 이차 이력의 날카로운 상계, cubic·quartic의 곡률 상계, source-off와 현재 source shutoff를 구분했다.
- 같은 `p,R,S`를 가지는 두 명시적 측도가 서로 다른 cubic 응답 `7/32`와 `25/128`을 갖는 예로 kernel 비유일성의 해석 한계를 확인했다.
- 저장된 네 model/representation 행을 섞지 않고, 기존 이차 정확값을 읽어 24개의 새로운 근사 비교와 180개의 조건부 budget 기록을 대조했다. 원래 이차 evaluator나 cone certification은 재실행하지 않았다.
- missing input, 부정확한 budget 입력 형식, 음의 reference ratio, 0인 tolerance의 거절과 budget 등호 경계를 점검했다.

owner의 M2 실행과 7개 targeted test에 대해서는 저장된 실행 receipt·raw stdout/stderr를 읽고 현재 코드 SHA와 로그 SHA가 각각 일치함을 확인했다. 해당 실행을 반복하지 않았다. 신규 `G`, propagation, NCP 실행은 없다.

## 통합 계획에 대한 현재 검토

제공된 원 RUX DAG와 새 local DAG/overlay, 소비자 요청, 원자 owner matrix와 domain map을 읽었다. CR의 국소 완료 상태를 전체 RUX 물리 gate의 완료로 바꾸지 않는다. CR relevance를 scenario freeze 전에 판정하고, CR ON일 때 native source/domain binding을 먼저 요구하며, 선택한 물리 주장에 필요한 확장만 release 의존성으로 둔다.

기존 native terminal proton packet과 M0의 causal electron kernel은 동일 응답량으로 승인되어 있지 않다. 공통 source digest는 lineage의 근거이며 terminal heating에 `p`를 곱하는 근거가 아니다. M1의 실제 full-history binding과 관측량 budget은 열린 상태다.

CR OFF의 제한된 함수 및 negative control의 동일성과 과거 실제 실행 근거는 현재 전체 binary 또는 선택된 우주론 이력의 실행 완료와 구분된다. 그러므로 별도 local OFF wrapper를 새로 만드는 근거는 없고, 후속 실제 receiver history에서 필요한 receipt를 남기는 계획이 적절하다.

## 문장 정밀화 요청

`DERIVATION_KO.md`의 이차식 상계 등호 문장은 `M=|q''|`를 택할 때라는 조건을 붙이면 일반 전제 `M>=sup|q''|`와 정확히 일치한다. 현재 산술은 실제로 `kappa=2|c|`를 사용하므로 코드나 계산을 바꿀 필요는 없다. owner에게 이 문장 정밀화를 전달했다.

## 유지하는 한계

이 결과의 근거 상태는 `derived`, `numerically checked`, 범위를 한정한 `implementation-verified`다. 논문의 신규 물리 결과나 문헌상 최초성을 주장하지 않는다. 원 기록의 forward/discretization error, 물리적 source/bath 오차, 시간 의존 환경, source-normalization transfer, 실제 EoR observable, production, F/H gate, NCP scaling은 승인 대상 밖이다. 이 한계를 없애는 추가 검산을 지금 반복하지 않는다.

## 최종 범위 판정

최종 통합 보고서·계획·주장 ledger·handoff·상태 문서와 루트 진입 포인터를 읽었다. 후보 manifest `ffe92537a2de923d2180540587c91ab2a4faac56d752089de19a3e6c58fe98ba`의 120개 파일은 크기와 SHA256이 모두 일치했다. 이는 byte identity 확인이며 120개 파일의 과학을 모두 새로 검증했다는 뜻은 아니다.

이차 상계의 등호 문장은 요청한 `M=|q''|` 조건을 포함하도록 정밀화되었다. 독립 reference 실행 후 바뀐 것은 이 비코드 유도 문서와 판정 포인터를 기록한 계약 문서뿐이다. 실행 당시 두 문서의 원문은 `executed_documents/`에 보존했고, 계산 코드와 입력·출력 identity는 유지되었다. 과학 계산은 다시 실행하지 않았다.

최종 결정은 `DECISION.json`의 **PROMOTE — BOUNDED_REUSE_DIAGNOSTIC_AND_NEXT_SOURCE_BINDING**이다. 신규 수학·코드·기록 산술 진단과 한정된 재사용 계획을 후속 source binding에 사용할 수 있다. 실제 source 정규화, EoR 이력, current whole binary, production과 과거 F/H gate는 이 결정으로 승격하지 않는다. 막는 finding은 없고 추가 과학 검증은 종료한다.
