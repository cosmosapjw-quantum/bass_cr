# R4X 공유 경계 radial 표현의 독립 설계 검토

작성일: 2026-10-02 KST. 역할: 독립 과학 설계 검토. 기존 소스와 R4W 증거를 읽고 수행한 정적 검토이며, 이 문서 작성자는 후보 평가기나 연산자 비교 구현을 작성하지 않았다. 이 문서 자체는 새 물리 호출, 실행 결과 또는 production 승인 증거가 아니다.

## 권고와 적용 범위

이번 단계는 R4W에서 확인한 FP64 monomial 표현의 경계 결함을, 명시적인 공유 endpoint 표현으로 제거하고 기존 저장 bank와의 변화를 정량화하는 데 한정한다. `u=(1-s)L+sR+s(1-s)q(s)`의 endpoint-factored 표현은 적합하다. 여기서 각 셀의 L,R은 하나의 공유 endpoint 배열을 참조하고 q는 2차 polynomial이다. 끝점 값을 그때그때 monomial 합으로 복원하지 않는다.

원본 `BASIS.npz`에는 원래 eigensolve의 전역 nodal vector가 없고 셀별 monomial coefficient만 있다. 따라서 이 후보를 **원래 nodal FEM의 원자료 보존·복구**로 부르면 안 된다. 원본 각 셀의 c0를 공유 endpoint로 선택하고 마지막 endpoint를 0으로 정하는 규칙은 R4W의 정확한 affine lift와 연결되지만, q를 FP64로 저장하면 그 반올림 효과를 별도로 측정해야 한다. 후보 이름, 입력 SHA, 평가기 SHA 및 연산자 문맥을 모두 새로 부여한다.

명시된 실제 원본 spec은 radius=64a0, elements=40, degree=4, grading=2, radial quadrature=12, lmax=1, bound_nmax=2, positive_per_l=1, positive_emax=2Eh다. 자유 nodal DOF는 40×4−1=159개이며 radial mode 5개, angular channel 9개/중심, 총18개다. H,M은 기존 `radial_fem`의 Coulomb weak form을 그대로 쓴다. 새 eigensolve·기저 크기 변경·에너지 재선택은 이번 비교에 필요하지 않다.

## 정확한 연속성과 미분의 의미

저장된 L,R,q의 binary64 값을 각각 정확한 이진 유리수로 해석하면, 후보 polynomial은 s=0에서 L, s=1에서 R을 정확히 가진다. 인접 셀이 같은 endpoint 값을 공유하고 첫/마지막 endpoint가 0이면 모든 내부 value jump와 양 끝 trace가 정확히0이다. 이 성질은 셀 내부 FP64 evaluation error가0이라는 주장이 아니다. 평가기는 정확한 endpoint 입력에서 공유 값을 직접 반환할 수 있고, `nextafter`로 양옆을 평가하는 점 검사는 해당 실행 경로의 구현 검증이다.

연속 piecewise polynomial의 1차 미분은 셀 경계에서 jump해도 된다. C1이나 전역 H2를 요구할 이유는 없다. 유한 mesh와 0인 끝점에서 radial 후보는 H0^1(0,L)에 속한다. 3차원 각운동량 채널의 Coulomb weak form에 필요한 centrifugal integral도 별도로 유한해야 하며, u(0)=0인 이 유한 polynomial 표현에서는 그 근방을 정확식으로 확인할 수 있다. p-mode의 정확한 수소형 cusp 차수를 새로 강제하는 것은 기존 FEM 공간을 바꾸는 별도 작업이다.

원래 monomial bank는 미세하게 불연속이므로 후보−원본의 derivative 차이를 전역 H1 또는 weak-derivative L2 norm으로 표기하면 안 된다. 셀 내부 polynomial derivative에 대한 **broken L2 norm**만 적분할 수 있다. 후보 자체의 weak derivative는 정상적인 L2 함수이지만, 불연속 원본과의 차이는 interface distribution을 포함한다.

R4W와 같은 s–p_z endpoint trace 합은 후보에서 정확히0이어야 한다. 이것은 integration-by-parts representation defect의 제거를 검증한다. 실제 FP64 D의 합까지 비트 단위0이 되어야 한다는 조건은 아니며, raw D를 반대칭화하거나 S의 같은 중심 미분을 강제로0으로 만드는 구현은 제외한다.

## 정규화·변화량·고유문제 검증

다음 값은 원본/후보 각각에 대해 모드별로 남기는 것이 적절하다.

| 검증량 | 계산 및 해석 |
|---|---|
| exact trace | Fraction으로 origin,outer,39개 internal interface를 계산. 후보는 모두 정확히0이어야 함 |
| radial norm | 각 셀 exact polynomial product를 적분해 ∫u²dr 및 원래1과의 차이 기록. 후보를 자동 재정규화하지 않음 |
| mode overlap | 같은 l의 모든 radial pair를 정확 적분. 다른 l은 angular orthogonality로 분리 |
| representation change | exact ∫(u_new−u_old)²dr, 상대 norm, 최대 endpoint 변화, 셀 내부 derivative 차이 norm |
| roundoff from affine lift | R4W exact affine candidate와 새 endpoint-factored 후보 사이의 exact polynomial norm 차이. reconstruction과 q 저장 반올림을 구분 |
| weak eigen residual | 기존 spec의 H,M으로 r=Hc−ε_old Mc, 기존 absolute residual, relative backward residual을 함께 기록 |
| mass condition | λmin(M), λmax(M), κ2(M), nodal Gram CᵀMC. radial norm과의 일치도 관측 |
| radial energy | 기존 ε를 유지한 Rayleigh quotient 및 차이. 에너지를 갱신해 residual을 감추지 않음 |

후보의 exact polynomial을 local nodes 0,1/4,1/2,3/4,1에서 계산하면 연속 전역 nodal vector를 구성할 수 있다. 이를 binary64 c로 반올림하여 기존 H,M에 넣는 residual은 **후보의 nodal projection/rounding을 포함한 수치 weak residual**이다. 원래 nodal eigenvector를 복구했다는 증거가 아니다. exact nodal 값과 반올림 c로 만든 polynomial의 차이 또는 그 반올림 크기를 함께 보고하면 적용 범위가 분명해진다.

기존 `atomic_bank`의 gate인 absolute residual≤2e−8 및 |ε|>100×residual을 완화하지 않는다. 추가 relative backward residual은 원인 분리용이며 기존 gate를 대체하지 않는다. radial eigen residual은 유한 FEM 행렬에 대한 것이며, 전공간 Schrödinger 연산자 residual이나 continuum 오차 증명으로 승격하지 않는다.

## 같은 입력의 전체 S/H/D 비교

z=−32와 z=0, radial cross orders32,40에서 original/candidate를 비교하는8개 static calls는 분리된 이 표현 변경을 검토할 수 있는 제한된 실험이다. B0의 trajectory, ETF, charges, bank mode 수, angular convention, 같은 중심 order20, cross batch 및 native accumulation 순서를 고정한다. 같은 geometry/order/backend의 두 표현을 한 쌍으로 비교한다. 32→40 차이는 후보와 원본 각각 기록한다.

full_operator의 같은 중심 경로는 각 radial의 evaluate를 호출한다. exact_cross의 `_radials` 역시 evaluate를 호출하고, native moment kernel에는 실제 u,du 값이 들어간다. 따라서 native C++/Fortran kernel의 변경 없이 새 표현을 평가할 수 있다. 그러나 두 경로의 guard에는 `isinstance(FEMRadial)` 및 `polynomial_coefficients` fingerprint가 있으므로, 기존 class인 것처럼 가장하거나 stale monomial bytes를 입력 identity로 쓰는 것은 부적절하다.

현재 구현 계획처럼 **명시적으로 이름 붙인 연구용 source copy에서 guard만 수정**하고, 모든 upstream source SHA와 exact diff를 기록하는 경로가 타당하다. guard는 원본 FEM 또는 새 후보 schema만 허용하고, 후보의 실제 공유 endpoint/bubble payload 및 evaluator SHA를 fingerprint에 포함해야 한다. assembly의 산술·quadrature·basis gradient·native call 순서를 바꾸지 않는다. 원본 입력을 새 adapter로 처리한 결과가 기존 경로와 같은지 bounded 확인하면 guard-only 변경 주장을 뒷받침한다. candidate의 genuine payload를 복원하지 못하는 기존 monomial serializer는 명시적으로 거부해야 한다.

| 기록할 양 | 목적 |
|---|---|
| 각 full/block ΔS,ΔH,ΔD의 Frobenius/spectral norm, max entry | representation 변경이 어느 블록과 원소에 들어가는지 측정 |
| 원본/후보별 S,H raw Hermiticity | 기존1e−11 screen 유지. exact-moment S/H reverse는 conjugacy로 유도되므로 독립 Hermiticity 검산으로 부르지 않음 |
| λmin/max(S), λmin/λmax | 기존 metric ratio≥1e−8 유지. 새 positive-definite projection 금지 |
| same-center raw D+D†, A+A† | exact trace 소거 뒤 남는 arithmetic/quadrature 잔차 측정 |
| 같은 중심 H−iD−H0−Vother | boost cancellation 진단. raw arrays 보존 |
| order32→40 차이 | 두 표현 각각의 공간 적분 수치 민감도. 인증 상계로 부르지 않음 |
| source/native/payload SHA, query order, resources, wall time | 재현성과 실제 제한 범위의 성능 설명 |

Δoperator의 물리 단위는 S가 무차원,H가Eh,D가ta⁻¹이다. 작은 성분의 상대비는 0 근처에서 커질 수 있으므로 max entry absolute와 block norm을 함께 제시한다. 새로운 representation-local screen을 사전 명시할 수는 있지만, 그 screen의 PASS를 원래 G02 raw derivative gate의 PASS로 대체해서는 안 된다.

## 판정 한계와 다음 단계

이 단계의 성공은 **공유 endpoint 표현을 실제 구현했고 정확한 continuity와 bounded S/H/D 비교를 검증했다**는 국소 결론이다. 두 z의 static 비교는 교차 블록 시간 미분의 검증이 아니다. R4V의 raw FD 절단오차, 전체 collision window, 연속 error bound, capture, all-bound 또는 b-grid 상태는 그대로 열린다.

상태는 production=HOLD,capture=false,all_bound=OPEN,b_grid=NO_GO를 유지한다. 독립 geometric derivative 또는 별도 고차 FD 설계가 다음 G02 단계다. ballistic midpoint 좌표에서 공통 carrier가 이미 상쇄되므로 lab ETF의 −v²t/2만 제거하는 단순 phase demodulation은 해법으로 추가하지 않는다.

모든 FP64 payload·quadratue·native accumulation은 보존된 계약하에 평가한다. 이 작은 실험에서는 현재 host의 실제 자원 안에서 query 병렬화를 사용할 수 있지만, NCP64 scaling이나 실제 OpenMPI 실행으로 보고하지 않는다. 검증되지 않은 새 SIMD reduction 또는 기저 오차를 감추는 fast-math는 이번 representation 작업에 섞지 않는다.

## 읽은 근거

- R4W `DERIVATION_KO.md`, `REPORT_KO.md`, `exact_trace_oracle.py`.
- `bass_foundations/radial_basis.py`, `kernels.py::radial_fem`, `two_center.py`.
- `full_operator_20260926/full_operator.py`.
- `reaudit_20260925/repair/aligned_cross.py`.
- `tp2a_perf_20260926/fast_cross.py`.
- `tp2a_analytic_pruning_20260926/code/exact_cross.py`.
- 실제 `runtime_inputs/BASIS.json`, `SCIENCE_CONTEXT.json` 및 프로젝트 HPC 정책.

위 근거는 현재 복구된 source의 읽기 결과다. 이 문서가 외부 문헌 검색, 새 native 실행 또는 결과에 대한 독립 재계산을 대신하지 않는다.
