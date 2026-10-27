# C3 — 저장된 사슬의 새 채널 수치 설계

## 실제 계산식

새 basis나 source quadrature를 만들지 않는다. 각 case의 저장 lower/diagonal/upper와 physical16 RHS를 읽어 새 lambda와 lambda*E 두 열을 삽입한다. 한 shared tridiagonal K1로 physical18을 풀고, 그 확률 열의 conditional5를 푼다. 별도의 stable4 RHS는 −lambda*stored_HeI_column이다. 마지막 w1만 이전 K0를 사용한다. 이 diagnostic은 새 RHS이므로 과거 reward solve의 재실행이 아니다.

Production은 FP64 `scipy.linalg.solve_banded((1,1),...)`를 사용한다. 실행 전에 유한 Z-matrix 부호와 Thomas elimination의 모든 pivot>0를 검사한다. Tridiagonal 구조에서 이 부호·pivot 조건은 비음성 inverse의 LU 표현과 대응한다. Solver가 사용한 rounding을 포함해 각 RHS의 componentwise scaled residual

`abs(K*x-b)/(abs(K)*abs(x)+abs(b))`

최댓값을 계산한다. 분모가0이면 잔차도0이어야 한다. 허용 기준은2e-12이며 서로 다른 단위의 열을 하나의 큰 time/energy norm으로 정규화하지 않는다. Fast-math, dtype 축소, parallel reduction 변경은 적용하지 않는다.

## 작고 다른 오차의 분리

| 오차·가정 | 이번 처리와 판정 |
|---|---|
| 기존 PR106 diagonal·solution rounding | exact stored K0를 baseline으로 채택하고 과거 근거를 유지한다. 이전 intended-real-sum 복원은 하지 않는다. |
| 새 lambda diagonal addition loss | `(longdouble(K1diag)-longdouble(K0diag))-longdouble(lambda)`와 사용 mantissa bits를 기록한다. 이는 독립 Decimal70의 대체물이 아니다. |
| 새 선형 solve roundoff |각28 RHS에 componentwise backward residual2e-12, 독립 finest2의 own-column relative5e-10 |
| 작은 old-observable 변화의 cancellation |두 큰 해를 빼지 않고 stable4를 직접 푼다. 이것은 stored-column response이며 THEORY §4의 baseline residual 항을 유지한다. |
| 이산 grid 비교 |각 chi,z,R의1024→2048 비교. Ordinary observable.005, stable paired response.01. |
| 유한 upper-domain 비교 |각 chi,z,N2048에서R40→80, 모든 선택 observable1e-5. |
| 저장 source projection |동일 mask, p[0], 원384 atoms, count/first-energy moment identity만 확인한다. 새로운 projection이나 quadrature를 수행하지 않는다. |
| source physics와 모델 truncation |ground spontaneous/conditional isotope/zero recoil/frozen bath 가정 그대로. Finite-grid 성공을 global physical error bound로 바꾸지 않는다. |

M-matrix와 한 추가 hazard에 대한 `w/(1+max(w))<=p_HeII<=w`는 independent scale의 rare-bound 검사다. 기존 비음성 terminal reward의 stable response는0 이하이어야 한다. Conditional energy/time 비의 단조성은 검사 기준이 아니다.

## 보존·반환

확률 sum은 entry+CE_s+CE_p+H1+HeI+HeII다. Physical18의 bath slice는12:18이다. 새 최종 energy sum은 retained photon+internal을 사용하며 fast-removal diagnostic을 다시 더하지 않는다. Source 전체에는 처음부터 inactive인 kinetic energy와 p[0]의 cutoff entry를 포함한다. Event energy5e-13, total energy2e-8, integrated external energy2e-13을 각 scale에 적용한다.

24개 case/z export는 각기 다른 grid/source 대안이며 하나의 전체 source history로 합산하지 않는다. Canonical event ID와 frame/case/z binding, SI conversion, null rate/exposure, native retained photon port가 admission 대상이다. Actual nb가 없으므로 native25는 null이며 density delta는 유효하다. Explicit-nb control이 native25를 별도 검증한다.

## 독립 수치 기준

Decimal70 checker는 production module을 import하지 않는다. 새 intended diagonal은 `Decimal.from_float(stored_HeI_diag)+Decimal.from_float(lambda_new)`다. Old physical RHS는 저장 binary64 operand 그대로, 새 lambda*E와 stable 곱은 exact Decimal 곱으로 구성하고 conditional RHS는 독립 확률 해로 만든다. 두 finest case의 전체56 columns를 자기 infinity norm 기준5e-10으로 비교한다. Native HeII coefficient는 사전 고정 10 points를 별도 식으로 계산해5e-13으로 대조한다.

현재 단계는 수치 설계·정적 코드 대조다. 실행 결과나 실제 수렴 PASS는 C6–C9 evidence로만 판정한다. 실패하면 실제 원인·시도 비용을 보존하고 고정 acceptance를 완화하지 않는다.
