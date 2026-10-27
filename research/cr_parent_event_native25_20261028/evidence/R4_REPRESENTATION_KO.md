# R4 — 알려진 source 모형의 계수와 부분 사건을 연결하는 표현

## 선택한 구성

고정 revision `4ca5a90de79c8fb82a25fd9e83615bec0dfa870b`의 실제 Rudd port와 PHYS02 생성식을 사용한다. 원 proton quadrature나 source/G/RR 응답을 재실행하지 않는다. 공통 kinematic endpoint보다 작은 원 band support에서 source는 알려진 세 유리함수의 선형결합이다. 저장 moments를 이용하는 이유는 이 유한 차원 모형과 실제 입력 identity가 이미 고정되어 있기 때문이다. 임의의 moments에서 spectrum을 만들어 내는 방법을 주장하지 않는다. Retained-photon spectrum은 기존 저장 atom을 그대로 참조한다.

\[
f_1(I,W)=(1+W/I)^{-3},\quad f_2(I,W)=(W/I)(1+W/I)^{-3},
\]
\[
A(W)=\theta_H\{(7/3)f_1(I_H,W)+f_2(I_H,W)\}
+\theta_{He1}f_1(I_{He},W)+\theta_{He2}f_2(I_{He},W).
\]

H와 He의 pole이 다르고 H numerator는 그 pole에서 0이 아니므로 세 함수는 선형 독립이다. 다만 이것만으로 선택한 세 moment의 행렬이 잘 조건화되었다고 할 수 없다. 실제 matrix의 scaled inverse, rcond, component sensitivity, positivity와 미사용 moments를 별도로 확인한다.

## 계산 경로와 고정 입력

1. Recovery bands `[0,.1]`, `[3,10]`, `[100,1000] eV`의 저장 energy coefficient로 3×3 문제를 구성한다. `[.1,1]`, `[1,3]`, `[10,100]`은 식별에 사용하지 않고 검증한다. Identification support와 실제 low-birth support `[.1,10]`은 별개다.
2. 행·열 scaling을 고정하고 작은 matrix에 충분한 정밀도를 사용한다. 작은 구간의 로그·유리함수 차는 상쇄를 피하는 식으로 평가한다. R1의 모든 허용치는 유지한다.
3. 원 8-point cell quadrature와 number-linear barycentric projection을 각 basis에 적용한다. 새로운 H/He 귀속 계수의 합을 실제 canonical atom과 비교하며 기존 A/E bytes를 바꾸거나 재정규화하지 않는다.
4. 원 proper history `q=tA`를 유한 구간에서 적분한다. Source 안에 이미 들어 있는 neutral target density와 proper729를 다시 곱하지 않는다. Same-state `nb=8750/47 m^-3`는 native25 사상에서 한 번만 나눈다.
5. H parent extent, He selected-electron marginal, 저장 RR·cutoff·photon port를 결합한다. Source parent와 RR capture target의 개별 전자 lineage를 추정하지 않는다.

## 비교한 표현과 판정

| 표현 | 판정과 이유 |
|---|---|
| 알려진 3-basis 모형의 식별 + 원 projection | 채택 후보. 실제 source recipe·moments·atom을 각각 검증할 수 있다. |
| 원 proton quadrature 또는 전체 G/RR 재실행 | 현재 변경 의존성에 필요하지 않으며 이번 계약에서 실행하지 않는다. |
| Projected atom 위치에서 H/total의 pointwise ratio 적용 | 원 cell 평균과 projection을 보존하지 않으므로 채택하지 않는다. |
| 임의의 4계수 fit, normalization 조정, 허용치 확대 | R1의 식별 실패를 숨길 수 있으므로 자동 복구 경로에 넣지 않는다. |
| He 전자 수를 모두 HeI→HeII 사건으로 선언 | Inclusive marginal에는 single/double pairing 정보가 없으므로 실제 상태로 채택하지 않는다. |

## 반환 표현

He 사건은 `p>=0,d>=0,p+2d<=N_eHe`의 affine family와 unresolved partner port로 내보낸다. 실제 branch point는 null이다. 기본 cutoff는 보존된 reservoir이며, thermal assimilation은 명시적인 partner·EOS closure를 가진 조건부 fixture로만 계산한다. 실제 full physical native25는 null을 유지한다.

Native baseline과 increment는 별도 필드다. Source parent와 작은 RR 항도 별도 term ledger에 보존한다. 큰 두 수를 빼서 작은 RR 항을 복구하거나, 반올림된 endpoint 차이로 increment를 재구성하지 않는다. Retained photons, Coulomb transfer, cutoff retention, atomic convention residual, unresolved partner work는 각자 의미를 가진 port다.

이 단계는 표현 선택과 손 유도이다. 새 과학 실행·Wolfram·기존 science replay는 모두 아직 없다. 실제 수치 채택은 C4 이후의 새 예산 실행과 독립 검토에 달려 있다. 중앙 **28/88**, 이번 단위 효과 **0**.
