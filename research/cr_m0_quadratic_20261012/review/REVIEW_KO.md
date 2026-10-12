# 독립 결정 검토 — M0 이차 주입 응답

## 판정

**PASS_SCOPED.** 동결된 `CR-M0-QUADRATIC-RESPONSE-20261012` 후보의 새 수학, exact 수치 후처리, 해석과 실제 실패·복구 기록을 이 범위 안에서 승인한다. 필수 후보 수정은 없다. 완료된 원 M0의 기록을 재사용한 **유효한 bounded interpretation continuation**으로 인정한다.

이 판정은 production 또는 cosmological PROMOTE, 물리적 진실에 대한 오차 인증, 원 F binding 해소, NCP 실행 승인이 아니다. 최초 producer의 exit 1도 그대로 유지된다. 기계 판정은 [DECISION.json](DECISION.json), 실제 독립 실행 기록은 [ACTUAL_EXECUTION.json](ACTUAL_EXECUTION.json)에 있다.

## 검토자, 입력 동결과 적용 절차

검토자는 `/root/m0_independent_decision`이다. 후보 생성, 후보 유도 설계, producer 수치 구현에 참여하지 않은 별도 decision reviewer로 동결된 후보를 받았다. 이번 검토에서 후보는 수정하지 않았으며 `review/`의 독립 참고 계산과 판정만 작성했다. 검토의 재귀 위임은 하지 않았다.

기준 commit은 `ae2d246d7e9037e000b00cd89991beb6f837f2ee`다. [REVIEW_INPUT_MANIFEST.json](../REVIEW_INPUT_MANIFEST.json)에 나열된 31개 파일의 크기와 SHA256을 모두 확인했다. manifest 자체의 SHA256은 `e1dd63ee9b46614afa5808f68e6887c345b29e3241a309b1fd0225834da3bbf6`다. 31개라는 수에는 manifest 자신, 이번 review 결과와 이후 게시 자료를 포함하지 않는다.

`CONTRACT.json`, `README_KO.md`, `DERIVATION_KO.md`, 입력·결과 JSON, TSV, 실행·완료·실패·복구 영수증과 stderr, 최초 및 최종 producer source, renderer, root 시작문, 현재 state와 HANDOFF/NEXT_DAG를 읽었다. PNG를 직접 보았다. PDF는 동결된 bytes/hash를 확인했으며 별도 PDF 렌더 검토를 했다고 주장하지 않는다.

현재 호스트가 제공한 `GPT-6 Astra Pro` / `GPT-6 Astra` 표시에 따라 canonical research harness v4.0.0을 적용했다. ZIP의 실제 SHA256은 `dae76c90f2e5d691bcdd595dadbe470bacacba3bb2a036ff9788ffe7d3bfabb7`와 일치했다. 실제로 읽은 항목은 `START_HERE.md`, `PROJECT_INSTRUCTIONS.md`, `docs/MODEL_ROUTING.md`, `state/RESEARCH_STATE.md`, `prompts/phases/05_independent_adversarial_review.md`와 후보의 현재 state다. ZIP state는 미실행 템플릿이다. 전체 과거 하네스나 과학 suite는 실행하지 않았다. 이 routing은 호스트 모델의 성능 또는 backend identity에 대한 별도 증명이 아니다.

## 1. 수학적 범위와 달성가능성 — DEFENDED

고정 비음수 causal kernel, \(H_m>0\), zero prehistory와 명시된 source amplitude \(q_*>0\) 아래에서

\[
\mathcal P_m(T)=H_mq_*\int_{[0,T]}f(1-\tau/T)\,dF_m(\tau)
\]

이며 \(f(x)=\alpha+\beta x+\gamma x^2\)를 대입하면 \(H_mq_*(\alpha p_m+\beta R_m+\gamma S_m)\)가 정확히 나온다. 상수항에 전체 확률 1 대신 창 질량 \(p_m=F_m([0,T])\)가 들어가는 점이 맞다. 이 결론은 `derived`이고, 저장된 exact packet에 대한 평가는 `numerically checked`다.

일반 이차식을 \(f=a(1-x)^2+2bx(1-x)+cx^2\)로 썼을 때 비음 조건은 \(a,c\ge0\), \(b\ge-\sqrt{ac}\)다. 끝점에서 첫 두 조건을 얻고, 내부에서는 \(a/u+2b+cu\)의 inf로 마지막 조건을 얻는다. \(a=0\), \(c=0\), 양쪽이 모두 0인 경우에도 조건과 다음 분해가 성립한다.

\[
f=[\sqrt a(1-x)-\sqrt c\,x]^2+2(b+\sqrt{ac})x(1-x).
\]

따라서 모든 비음수 이차 source를 제곱 선형식과 비음 계수의 bubble \(x(1-x)\)로 표현할 수 있다. 중간 Bernstein 계수 \(b\)가 음수인 admissible square도 빠지지 않는다.

\(A_l\succ0\), \(B_l>0\)이면 모든 nonzero admissible source의 legacy 분모가 양수다. squared-linear source의 모델 비율은 generalized Rayleigh quotient이므로 두 실수 generalized eigenvalue 사이의 닫힌 구간을 정확히 이룬다. bubble을 더하면 그 비율은 squared-linear 비율과 \(B_f/B_l\)의 legacy 가열 가중평균이다. 그러므로

\[
\left[\min(\lambda_-,B_f/B_l),\;\max(\lambda_+,B_f/B_l)\right]
\]

가 정확한 전체 범위다. 각 경계는 해당 고유벡터의 square 또는 bubble로 달성된다. 두 경계 source를 각자의 legacy 가열로 정규화한 후 비음 조합하면 비율이 두 경계 사이에서 선형으로 변하므로 중간의 모든 값도 달성된다. 이 주장은 유한 표본으로 추정한 envelope가 아니다.

현재 두 표현에서는 bubble 비율이 eigenvalue 구간의 strict 내부에 있다. 따라서 두 정확한 경계는 algebraic squared-linear source에서 달성된다. JSON의 rational witness는 그 source의 근사이며, 유리수 외향 경계를 정확한 극값이라고 바꾸어 부르지 않는다.

## 2. 비감소 클래스, 종료 source와 단위 — DEFENDED

\(f(1)=1\)인 이차식의 도함수는 \(2[(b-a)(1-x)+(1-b)x]\)다. 일차 도함수의 양 끝 부호와 \(f(0)=a\)를 확인하면 \(f\ge0\), \(f'\ge0\)의 필요충분조건이 \(0\le a\le b\le1\)임을 얻는다. 표현

\[
f=a\cdot1+(b-a)(2x-x^2)+(1-b)x^2
\]

의 계수는 비음이고 합이 1이다. 각 꼭짓점의 legacy 가열이 양수이므로 비율 극값은 꼭짓점에서 달성된다. 두 표현 모두 최소는 \(x^2\), 최대는 \(1\)이다. 이 클래스와 \(f(1)=0\)도 허용하는 일반 비음수 클래스가 분리되어 있다.

원점과 종료 시각의 source 값도 적절히 다룬다. 지연 원자 \(\tau=T\)는 \(q(0)\), \(\tau=0\)는 \(q(T)\)를 읽는다. zero prehistory는 \(q(0)=0\)을 강요하지 않는다. \((1-x)^2\)는 종료 시점에 \(p-2R+S\), \(4x(1-x)\)는 \(4(R-S)\)의 정규화된 가열을 남긴다. 후자는 포물선형 pulse이며 삼각형 pulse와 구별된다.

종료 source에서는 \(q(T)=0\)이므로 순간 예측으로 나눈 상대오차를 만들지 않았다. \(H_mq_*\)에 대한 정규화된 응답과 같은 source의 fullBED/legacy 비율을 보고한다. \(p,R,S,f\)는 무차원이며 \(H_mq_*\)는 원 기록의 가열률 단위다. 새로운 W 또는 eV/s를 부여하지 않았다. \(T=10^{10}\,\mathrm{s}\)와 약 316.88년의 표기도 입력 packet과 일치한다.

0 source의 \(0/0\), singular \(A_l\), \(B_l=0\), 순간 kernel 극한은 별도로 다뤘다. 현재 네 기록에서는 Bernstein Gram matrix가 양의 정부호이고 bubble이 양수여서 strict 가정이 실제로 성립한다.

누적 열량에 \(U_3\)가 추가로 필요한 유도도 맞다. 제시한 두 discrete measure는 같은 \((p,R,S)=(1,1/2,7/18)\)와 다른 \(U_3=19/54,17/54\)를 갖는다. 이를 단 한 번의 독립 실행 안에서 Fraction으로 확인했다. 이 반례는 실제 CR kernel을 대체하는 모델이 아니다.

## 3. 독립 exact 검산 — PASS

[REFERENCE_CHECK.py](REFERENCE_CHECK.py)는 producer를 import하거나 재실행하지 않는다. 입력 numerator/denominator만 재사용하여 다음의 다른 기저 행렬을 직접 구성했다.

\[
M_m=H_m\begin{pmatrix}p_m-2R_m+S_m&R_m-S_m\\R_m-S_m&S_m\end{pmatrix}.
\]

이는 \((1-x,x)\) 기저의 Gram matrix다. 저장된 \(L,U\)에서 \(M_f-LM_l\succeq0\), \(UM_l-M_f\succeq0\)와 두 bubble 부등식을 exact Fraction으로 확인했다. 저장된 원 기저 인증값과의 합동변환도 일치했다.

고유값 구간 검증은 producer의 isqrt 경로를 복제하지 않았다. 두 저장 구간의 끝점에서 \(\det(M_f-\lambda M_l)\)의 부호가 각각 \((+, -)\), \((-, +)\) 방향이며 구간이 분리되어 있음을 확인했다. determinant를 \(\lambda=0,1,-1\)에서 평가해 복원한 characteristic polynomial도 저장값과 일치했다. 네 rational witness 모두 정확한 square, \(\max f=1\), legacy 분모 양수이고 저장된 비율과 일치했으며 각자 해당 고유값 구간 안에 있었다.

| 클래스 | selected 기록의 실제 경계 근삿값, % | 두 표현 각각의 외향 표시, % |
|---|---|---|
| 모든 nonzero 비음수 이차식 | 0.01630328996864084 ~ 0.06539354557392767 | **[0.016303, 0.065394]** |
| 비음·비감소, \(f(1)=1\) | 0.01938958880244023 ~ 0.03914683073298701 | **[0.019389, 0.039147]** |

표의 퍼센트는 \(100(\mathcal P_f/\mathcal P_l-1)\)이다. 출력의 소수 경계는 외향 표시이며, 정확한 범위는 유리수 꼭짓점 비율 또는 algebraic eigenvalue다. birth-defined의 exact packet도 별도로 검산했으며 같은 여섯 자리 외향 표시를 얻었다. 두 표현의 일치를 한 kernel의 결합 근거로 쓰지 않는다.

새로운 세 이력을 포함한 24개 named response, 24개 TSV 행, 모델 비율과 표시 방향도 확인했다. 근거 전체는 [REFERENCE_RESULT.json](REFERENCE_RESULT.json)에 있다. 이 계산은 **1회, 실제 exit 0, 외부 wall 0.03784373699454591초, timeout=false**, 60초 한도 안에 끝났다. [REFERENCE_LAUNCHER.py](REFERENCE_LAUNCHER.py), 실제 stdout/stderr와 source hash를 보존했다. 이 독립 참고 실행은 원 과학 producer의 재실행으로 기록하지 않는다.

## 4. 최초 실패와 복구 — INFORMATIVE_FAILURE / DEFENDED

실제 producer 기록은 1회, **exit 1, wall 0.5617769189993851초**다. 보존된 attempt01 source의 255번째 줄이 최초 `savefig`이며, traceback의 해당 줄과 `mathcal P` 수식 문법 오류가 일치한다. JSON·TSV 기록문과 exact assertions는 그 앞에 있다. 실패 영수증에 기록한 두 산출물의 SHA256은 현재 JSON·TSV 및 완료 영수증과 일치한다. 빈 stdout도 보존됐다.

복구는 기존 JSON을 읽는 별도 renderer **1회, exit 0, wall 1.4970884500071406초**다. renderer receipt의 입력·결과·source hash와 PNG/PDF hash가 모두 동결 파일과 맞았다. 최종 evaluator에서 바뀐 것은 그림 경로의 분리이며, exact 수치 prefix와 마지막 receipt 부분은 최초 source와 동일했다.

최초 실패를 exit 0으로 다시 쓰지 않았고 exact 산술도 재실행하지 않았다. 실패 전에 저장하지 못한 산술 단독 wall은 `null`로 남아 있다. 이를 전체 실패 프로세스 wall에서 추정하지 않는다. 최종 evaluator를 처음부터 끝까지 새로 실행했다는 주장도 없다. 이번 `implementation-verified` 범위는 실제 실행한 renderer와 보존된 실패·복구 경로에 한정한다.

PNG를 직접 확인했으며 네 패널의 source, 가열 정규화, 모델 차이, 비감소 영역과 한계 문구를 읽을 수 있었다. 그림은 exact 인증의 설명용이며 plot sampling이 uniform bound의 근거라는 표시는 없다.

## 5. 과학적 한계와 다음 작업 — DEFENDED

고정 kernel·bath·스펙트럼·동일 T의 같은 source 비교라는 한계를 유지한다. 모델 차이를 물리적 진실에 대한 오차로 승격하지 않는다. 임의 이력의 오차 인증, 시간 변화 bath, cosmological/Bianchi 관측량, \(U_3\) 없는 이차 누적 열량과 T 이후 가열곡선은 아직 범위 밖이다. 일반 이력으로의 적용에는 실제 잔차와 consumer domain을 결속해야 한다.

HANDOFF/NEXT_DAG는 원 M0 COMPLETE, F operator binding HOLD와 G 차단을 보존한다. 원 H의 8build/76800열/900초/retry0을 초기화하지 않으며, 이번 M0의 NCP dispatch는 0이다. 아직 시작하지 않은 H qualification은 DEFERRED_OPTIONAL이고, 기존 미수집 run이 실제로 있을 때만 원 source-bound 수집을 이어받는다. 현지 NCP 상태는 UNKNOWN 또는 실제 영수증에 따르게 되어 있다.

다음 작업인 M1 소비자 이력·스펙트럼·bath/domain·관측량·오차 예산 결속, M2 controlled 또는 실제 이력의 응답 오차 평가, M3 CR-off receiver의 실제 증거 확인은 이 결과와 일치한다. 원 F closure나 H 전체 실행이 이 해석 산출물의 새 자동 의존성이 되지 않는다.

검토자는 원격 게시·PR·백업 성공과 현재 NCP 현지 run/reservation 상태를 검사하지 않았다. 이들 항목의 성공은 이 과학 판정에 포함되지 않는다. 새로운 CR G, CR linear solve, pulse propagation, expm, resolvent, F retry, 과거 suite 및 NCP 실행은 이번 독립 검토에서 각각 0이다.

## 종료

요청된 수학·수치·해석 및 실제 실패·복구 기록에 대한 필수 검토를 완료했다. 중대한 반례, 수치 경계 위반 또는 provenance 모순은 발견하지 않았다. 추가 재검산이나 검토의 검토 없이 종료한다. 이후 새 입력·source·scope가 바뀌면 해당 변경 부분이 새로운 검토 대상이다.
