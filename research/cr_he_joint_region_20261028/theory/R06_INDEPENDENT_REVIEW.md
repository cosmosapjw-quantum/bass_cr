# R06 — 독립 수학 검토

**판정: 선언된 finite divisible event model에서 정리 PASS. 수학적 blocker 0.** `THEOREM.md` 전체, `R03_CLAIMS.md`, `R04_EXPLORATION.md`를 읽고 필요조건·공통 최적점·모든 보간 분기를 정적으로 역대입했다. 기준 출판은 R5 `dc0661e91f8562f566ba4227b4054f681733d876`이며, 검토 중 발견한 R03 방향 표현의 교정도 다시 읽어 확인했다. 과학 코드·solver·source 배열·native 계산은 실행하지 않았다. 이 문서 외 파일 수정과 원격 게시도 하지 않았다.

검토자는 앞선 물리 mapping을 검토한 동일 팀의 별도 agent다. 작성자의 증명을 읽은 독립 검토이며 blinded replication으로 주장하지 않는다. 별도 하위 검토자는 Lemmas 4–5의 경계·퇴화·정량화만 중복 대조했고 같은 결론을 보고했다. 계산 검증 및 성능 검증은 이 PASS에 포함되지 않는다.

## 1. 지적, 영향, 교정 상태

| ID / 대상 | 근거와 영향 | 최소 교정 | 상태 |
|---|---|---|---|
| R6-01: R03 inventory의 `horizontal half-space` | 식은 `d>=d_min`이다. 통상 `(d,C)` 좌표에서 경계는 `d=const`이므로 방향 표현이 이후 도식을 오도할 수 있었다. 정리의 식에는 영향이 없다. | 방향 단어를 삭제하고 `intersect with d>=d_min`으로 명시 | **CLOSED.** 작성자가 교정했고 실제 R03 문장을 다시 읽어 확인했다. |
| R6-02: `finite rational event model`의 해석 | 전체 실수 polygon과 compactness는 실수 비음수 event coefficients의 polytope에 관한 것이다. R03은 coefficients를 nonnegative로 정의하고 rational target의 rational witness를 별도 주장하므로 현재 모순은 없다. 다만 모든 변수가 유리수만이라고 읽으면 그 집합 자체는 compact하지 않다. | 선택적으로 “event variables are real; rational targets admit rational witnesses; restricting event variables to rationals gives P intersect Q^2” 한 문장을 추가 | **NONBLOCKING CLARIFICATION.** 현재 명제의 수학적 오류가 아니며 본 검토에서 원문을 변경하지 않았다. |

아래 공격적 대조에서 새로운 반례나 미해결 증명 공백을 발견하지 못했다. 정리의 가정을 실제 native atom graph가 만족한다는 계산 결과로 이를 확대하지 않는다.

## 2. 정량화와 기본 상한

핵심 가정은 모든 **positive-mass** 허용 HL edge가 cross라는 것이다. Zero-mass atom은 marginal equation 때문에 incident event mass가 모두 0이며 삭제·복원이 무해하다. 허용 low diagonal은 coefficient `p_ii`가 두 marginal legs를 소모한다. Singles와 divisibility가 모두 필요하다. 정수 입자 수 또는 diagonal 금지를 추가한 모델은 검토 대상이 아니다.

유한 개 비음수 event 변수는 각 atom mass로 유계이고, all-singles가 존재하므로 실수 feasible polytope는 비어 있지 않고 compact하다. Rational data의 linear constraints와 rational objectives에서 rational optimizing vertex를 고를 수 있다. 첫 objective의 optimum X도 rational이므로 그 optimal face 위의 secondary objective m에 같은 논리를 적용할 수 있다. 유리수 optimum을 먼저 가정한 순환 논증이 아니다.

`m=HL mass`, `r=LL mass`라 두면 `d=m+r`, low-leg use는 `m+2r=2d-m<=L`다. `m<=M`으로 `d<=D=(L+M)/2`를 얻고, maximum HL matching의 residual low legs를 diagonals로 채우면 equality를 달성한다. 또한 `M<=min(L,H)`, `H=N-L`이므로 `D<=L`뿐 아니라 `D<=N/2`도 성립한다. 따라서 full-selected 식 `s=N-2d`는 선언된 영역에서 음수가 되지 않는다.

Maximum HL matching은 전부 cross이므로 `M<=X`; cross maximum에서 same-bin doubles를 singles로 풀면 `d=C=X`인 measure가 있어 `X<=D`다. 마지막 facet의 부등호 방향도 맞다:

\[
m\le C\quad\Longrightarrow\quad 2d-C\le 2d-m\le L.
\]

`M<=X<=D<=L`은 따로 추측한 숫자 제약이 아니라 정의된 graph의 feasible measures에서 도출된다.

## 3. Lemma 3: residual augmentation을 통한 공통 달성

### 경로의 존재와 occupancy

현재 cross-only optimum의 HL 부분은 source→high→low→sink capacity network의 feasible flow다. 그 값이 `m<M`이면 residual source–sink path가 존재한다. `N`이라는 HL edge capacity는 충분하다. `N=0`이면 이미 `M=0`이므로 augmentation 분기에 들어가지 않는다. Simple path는 HL forward/reverse를 교대로 지나며, 처음 high와 마지막 low를 제외한 각 vertex의 전체 HL occupancy를 그대로 유지한다.

처음 high의 unused source capacity는 정확히 그 high의 single mass다. HH event가 없고 cross-only 상태에서 high가 참여할 다른 double 유형도 없기 때문이다. 마지막 low의 `a_l-HL_occupancy`는 single mass와 LL-cross incidences의 합이다. 이것이 양수이면 적어도 한 summand가 양수다. Residual path가 실제로 이용하는 positive-capacity vertices는 positive input mass를 가지므로 domain의 positive-mass 정량화만으로 모든 수정 HL edge가 cross임을 보장할 수 있다.

### 두 endpoint 경우

마지막 low에 single이 있으면 모든 path residual과 두 endpoint singles 이하의 epsilon을 고른다. Endpoint single을 각각 epsilon 줄이고 HL path를 증대하면 각 marginal은 보존된다. Forward HL edges의 수가 reverse보다 하나 많으므로 `Delta m=Delta C=epsilon`; 이는 X의 최적성에 모순이다.

Single 대신 LL-cross edge `(l,q)`를 epsilon 줄이는 경우의 순변화는 다음과 같다.

| atom / event total | HL 사용량 변화 | LL 사용량 변화 | single 변화 |
|---|---:|---:|---:|
| 처음 high | +epsilon | 0 | -epsilon |
| 마지막 low l | +epsilon | -epsilon | 0 |
| LL edge의 다른 끝 q | 0 | -epsilon | +epsilon |
| 그 밖의 내부 path vertex | 0 | 0 | 0 |

`q!=l`은 LL **cross** edge이기 때문에 보장된다. **q가 내부 path low인 경우에도** 표의 HL 변화는 0이다. 각 path edge coefficient는 변할 수 있지만 해당 vertex의 합은 상쇄되므로 q의 freed LL leg를 single로 돌리는 것과 충돌하지 않는다. LL edge는 HL path edge와 동일할 수도 없다. Epsilon을 path residual, source-high single 및 선택한 LL coefficient 이하로 고르면 모든 coefficient가 nonnegative다.

따라서 이 경우 `Delta C=epsilon-epsilon=0`, `Delta m=epsilon`이다. 고정 C=X face에서 m을 최대화했다는 선택에 모순된다. Lemma 3의 lexicographic argument에 빠진 endpoint/internal-vertex 경우를 발견하지 못했다.

### F의 completion과 유한 유리수 구성

얻어진 cross-only measure는 HL mass M, LL-cross mass X-M이고 low-leg use는 `2X-M`다. 각 atom의 **실제 residual marginal**은 nonnegative다. 각각을 절반의 diagonal coefficient로 채우므로, 총량만 맞추고 개별 marginal을 놓치는 구성이 아니다. 추가 diagonal mass는

\[
[L-(2X-M)]/2=D-X,
\]

따라서 정확히 F=(D,X)를 얻는다.

유한성 주장도 성립한다. Rational cross optimum의 모든 event coefficients와 input capacities의 공통분모를 제거하면 초기 single·LL·HL coefficients, edge capacities, 모든 residual이 정수다. 허용된 최소 양수량으로 augment하면 정수성이 보존되고 m은 매 단계 최소 한 scaled unit 증가한다. `m<=M<infinity`이므로 과정은 유한하게 끝난다. X를 유지하는 동안 single-ending 경로가 생길 수 없고, `m<M`에서 residual path가 사라질 수도 없다. 따라서 종료점은 M이다. 마지막 diagonal completion에서 분모 2가 추가될 수 있으나 rationality는 유지된다. 이 유한성은 polynomial runtime이나 native 예산 충족을 뜻하지 않는다.

## 4. 모든 vertex, 단면과 퇴화

O, A, B는 직접 구성되며 F는 위 논증으로 구성된다. F에 추가했던 diagonals를 각각 두 singles로 풀면 G=(X,X)가 된다. 다섯 measure 모두 같은 전체 atom marginal을 갖기 때문에 convex combination은 scalar `(d,C)`뿐 아니라 모든 marginal과 allowed support를 보존한다. 중복되는 unordered event는 coefficient를 합치면 유한 event representation으로 남는다.

고정 d 단면의 nonemptiness도 확인했다. `d<=D<=L`이므로 `2d-L<=d`; 또한 `2d-L<=2D-L=M<=X`다. 따라서

\[
\max(0,2d-L)\le\min(d,X).
\]

고정 C에서는 `C<=X<=D<=L`이므로 `C<=min(D,(L+C)/2)`다. Result의 두 조건부 구간은 허용된 각 d와 C 모두에서 실제로 비어 있지 않다.

| 경우 | 역대입 및 분모 검사 |
|---|---|
| X=0 | M=0, D=L/2, C=0. D=0이면 O만; D>0일 때만 d/D를 사용한다. |
| L=0 또는 전체 zero mass | M=X=D=0. All-singles O로 끝나며 0으로 나누지 않는다. |
| M=0<X | A=B, D=L/2. U(C)의 첫 좌표는 항상 D다. C>M branch와 M=0 branch가 C>0에서 겹치지만 B=A이므로 두 공식이 동일하다. |
| X=M>0 | B=F. 모든 C<=X가 C<=M branch에 들어가므로 X-M으로 나누지 않는다. |
| X=D>0 | F=G. C=X에서는 d_U=C 분기가 theta의 영분모를 회피한다. |
| C=0, C=M, C=X | Upper witnesses는 각각 A, B, F에 일치한다. M=0 또는 X=M의 겹침도 위 분기로 처리된다. |
| d_U=C | 허용 d가 하나뿐이므로 Q를 사용하는 것이 정확하다. |
| 일반 내부점 | 0<=theta=(d-C)/(d_U-C)<=1. Q와 U의 완전한 measure를 섞으면 정확한 target을 얻는다. |

상단 경계는 C<=M에서 `(L+C)/2`, C>=M에서 D이며, 필요한 교차점은 `2D-L=M`다. 문서의 보간이 이 전 경계를 덮는다. Rational target에는 모든 혼합계수가 rational이다. Real target은 실수 혼합으로 같은 polygon을 채운다.

## 5. 별도 반례 시도와 scope

R04의 K=3, energies `(1/2,1,2)`, masses `(3,1,1)` 예를 손으로 대조했다. 두 low–high pairs는 모두 허용되고 HL maximum은 1이다. 각 cross edge가 B 또는 H의 적어도 한 leg를 쓰므로 X<=2이며 제시한 두 edges가 이를 달성한다. 다섯 표의 double/single coefficients를 각 atom에 합하면 모두 `(3,1,1)`로 돌아온다. 따라서 비퇴화 pentagon 예가 실제로 작동한다.

Outside-domain 예 K=2, energies `(2/5,7/5)`, 같은 bin과 masses `(1,1)`도 맞다. 허용 HL pair 하나의 mass 1은 `(d,C)=(1,0)`, L=1을 주어 `2d-C<=L`를 위반한다. 이는 **domain을 제거한 보편 명제의 반례**다. Predicate가 실패한 모든 데이터에서 polygon이 틀리거나 물리 모델이 불가능하다는 결론은 아니다. Strong scientific no-go로 승격하지 않은 처리가 적절하다.

Diagonal이 금지되거나 mass가 indivisible이라면 singleton low atom부터 A의 half-mass diagonal 구성이 실패한다. 문서는 그러한 가정을 명시적으로 제외하므로 이것은 현 정리의 반례가 아니다. 빈 effective support, zero masses, threshold equality에서 low로 분류되는 atom도 정의와 위 퇴화 분기에 포괄된다.

## 6. 수용 범위와 다음 검증 경계

실수 event polytope의 정확한 projection과 rational finite witnesses라는 **수학 명제**를 수용한다. Observable mapping은 full-selected·한 bound window·W와 nb 각 한 번이라는 R03 조건에서만 사용하며 inventory는 polygon과 `d>=d_min`을 교차시킨다. 실제 K, actual exclusive kernel, actual d/C, donor/outside response, EOS/T 및 full physical native25를 이 증명으로 결정하지 않는다.

Native support predicate, source atom identity, saved scalar optimum identity, 실제 atomwise primal construction, original consumer acceptance 및 실행 예산은 별도 coding obligations다. 본 R6는 그것을 실행 완료했다고 주장하지 않는다. 새 R7 계산이나 이후 stage를 선행하지 않았고, 현재 범위의 검토는 여기서 종료한다.
