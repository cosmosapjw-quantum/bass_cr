# z=-2 후보 적분 오차: 연구 결과와 적용 범위

## 입력과 재현

사용자 실행 3499e9f73527dfb5e76299205b9e864e89ebf248에서 z=-4는 q48 reference로 통과했다. z=-2에서는 q56/q64가 reference qualification을 통과했고, phase24 후보는 connection 4.9986895e-7로 1e-6 screen을 통과했지만 raw cross 차이 1.2094522e-8이 1e-9 기준을 위반했다. 이 NUMERICAL_SCREEN_FAILED는 보존한다.

이번 연구는 이전 보존된 BASIS.npz 계수(SHA256 172303585e254e6ad3ea7543fe0c1e695bd9364dc60040fad49c99b06ee84abe)를 재사용했다. 최신 사용자 행렬 원본을 받은 것이 아니므로 별도 호스트의 동일 모형 재현과 사용자 bytes 검증을 구별한다. scientific dependency 14개는 원격 기준과 연결된 SHA pins로 복원했다. 새 물리 full operator 15개와 반사실적 cross operator 2개를 계산했다. 기존 TP1, GPU, 성능 benchmark는 반복하지 않았다.

## 직접 유도

차원 있는 k = m_e (v_P-v_T)/hbar, 중심 간 단위벡터 e_R, k_parallel=k.e_R,
 k_perp=|k-k_parallel e_R|라 두자. 두 중심 거리 좌표에서
 a=(r_T^2-r_P^2+R^2)/(2R), rho^2=r_T^2-a^2다.

방위각을 해석적으로 적분한 원소에는 exp(i k_parallel a) J_m(k_perp rho)가 남는다. 이는 Fourier-Bessel integral identity를 이용한 것으로, Bessel 처리가 남은 거리 적분까지 정확하게 만드는 것은 아니다. 기존 24-rad 정책은 |k_parallel| Delta(r^2)/(2R)만 제한한다. k_perp*rho의 변화나 Bessel-진폭 곱의 고차 미분은 제한하지 않는다.

고정 r_T에서 d rho/d r_P = a*r_P/(R*rho)이므로 축 근처에서는 이 위상변수의 변화율이 커질 수 있다. 이 관찰은 물리적 특이점이나 J_m 자체의 발산을 뜻하지 않는다. 완전한 적분 오차상한으로 사용하는 것도 아니다.

b=2a0, z=-2a0, v=2.00798106651023 a0/ta에서 R=sqrt(8)a0,
 k_parallel=-1.4198570286/a0, k_perp=1.4198570286/a0다. 지지 영역의 최대 Bessel 인자는 약 90.84866이다. 원래 바깥 FEM 구간 [60.84,64]a0의 종방향 위상 변화는 약 99.01716rad이며 기존 정책은 이를 나눴지만 횡방향 의존성을 직접 제어하지 않았다.

## 통제 실험

같은 18 channels, 물리적 FEM degree4/40 elements, same-center order20, epsilon_z=1e-4a0, direct D와 weak H를 유지했다. 아래 q는 FEM degree가 아니라 적분 차수다.

| 규칙 | connection 상대잔차 | plain64 대비 3-stencil raw cross 최대 상대차 |
|---|---:|---:|
| plain56 | 7.1016583e-9 | 2.1291505e-10 |
| plain64 | 1.5619507e-9 | 0 |
| phase24, budget24 | 4.9986883e-7 | 1.2094522e-8 |
| phase32, budget24 | 1.5655020e-9 | 5.1249131e-15 |
| phase24, budget12 | 1.5635994e-9 | 4.7894722e-15 |

별도 반사실적 대조에서는 고정 중심과 동일 radial basis를 유지하고 상대속도를 중심축 방향으로 투영해 횡방향 성분만 제거했다. 이때 기존 phase24와 plain64의 S 차이는 2.08e-15 이하, 여섯 cross 원소의 최대 상대차는 5.10e-15였다. 특히 S의 진폭은 속도에 무관하므로 이 대조는 잔여 횡방향 ETF/Bessel 의존성이 현재 quadrature error에 결정적임을 지지한다. 투영 궤적을 실제 100keV/u 충돌의 물리 결과로 해석하지 않는다.

R_q=delta_h S_q-(D_q+D_q^dagger)에 대해
 R_24=delta_h(S_24-S_64)-[(D_24-D_64)+(D_24-D_64)^dagger]+R_64.
첫 항 norm은 1.02847e-7/ta, direct-D 차이 norm은 2.51561e-9/ta, R64 norm은 3.25400e-10/ta다. 재구성 오차는 1.494e-17/ta였다. 두 norm을 더해 기여율이라고 하지 않는다. 잔차는 사실상 TP/PT에 있으며 TT/PP의 제곱 norm 기여는 각각 약 6.9e-10이다.

## 코드 정책

후보도 이름만으로 충분하다고 간주하지 않는다. 새 계약은 reference [32,40,48,56,64]를 먼저 검증한 뒤, 동일 phase budget24에서 후보 [24,32,40,48,56,64]를 사전 고정된 순서로 검사한다. 두 기준(own connection/operator, qualified reference 대비 raw cross)이 모두 통과한 최초 후보만 채택한다. 실패했던 q24 수치는 candidate_attempts에 남는다. 허용오차, epsilon, basis, D 정의, native 소스는 변경하지 않는다.

이번 q32 결과만으로 모든 geometry의 q32 정확도를 선언하지 않는다. 유한 후보 budget 소진은 CANDIDATE_CONVERGENCE_UNRESOLVED이며 reference 소진과 구별한다. 이 사전 고정 refinement는 이전 실행의 재시도나 결과 재표기가 아니라 별도 V2 계약이다. 기존 user run은 source archive/report/hash를 확인한 명시적 bridge에서 원시 task만 재사용한다.

## 문헌과 근거 구분

NIST DLMF 10.9.2 (Bessel integral representation), https://dlmf.nist.gov/10.9.E2
NIST DLMF 3.5 (Gaussian quadrature), https://dlmf.nist.gov/3.5
문헌은 항등식과 일반 적분 이론의 근거다. 위 수치 및 원인 판정은 이 연구의 저장된 원시 행렬과 대조 계산에 근거한다. refinement 차이는 엄밀한 enclosure가 아니다.

전체 9 geometry, 연속 궤적 오차, basis completeness, capture, 기존 GPU 3% 차이는 이번 결과로 닫히지 않는다. Production HOLD / all_bound OPEN / b_grid NO_GO.
