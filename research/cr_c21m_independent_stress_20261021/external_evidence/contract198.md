# Matter/radiation 응력 분리: 유한 preliminary 확장 계약

## 사용자 변경과 기존 증거

2026-10-21 사용자가 “π_ab는 matter와 radiation을 별도로 고려하고 싶어”라고 지시했다. 완료된 625조건 pilot과 source/results `03d12c64d266a43f209b5f21408210186464ca5d`, delivery `53eb52f57e5de2f2f850bde97daf3a1f5235c039`를 그대로 보존한다. 이 디렉터리는 요청된 성분 분리와 독립 초기 matter 응력의 유한 확장이다. 기존 numerical gate를 다시 열어 같은 검증을 의무 반복하지 않는다.

## 물리적 계약

동일한 comoving orthonormal normal frame에서

\[
\pi^{(m)}_{\hat a\hat b}=\mathrm{diag}(-p_m,-p_m,2p_m),\quad
\pi^{(r)}_{\hat a\hat b}=\mathrm{diag}(-p_r,-p_r,2p_r),\quad
\pi^{(tot)}=\pi^{(m)}+\pi^{(r)}.
\]

여기 matter는 기존 fm=.1의 massive collisionless canonical component 및 나머지 pressureless dust이며 dust의 비등방 응력은 0이다. radiation은 photons+exactly massless neutrinos다. 공통 초기 brightness와 충돌 없는 동일 evolution 때문에 두 radiation energy vector를 공유한다. Native baryonic H/He 응력·Thomson·stellar feedback를 새로 넣었다고 주장하지 않는다.

기존 half-contraction norm과 실제 순간 H를 모든 성분에 공통 적용한다. p는 J/m³이며 K=8πG/c²다.

\[
\widetilde\Pi_m=\sqrt3Kp_m/H^2,\quad
\widetilde\Pi_r=\sqrt3Kp_r/H^2,\quad
\Pi_m=|\widetilde\Pi_m|,\quad\Pi_r=|\widetilde\Pi_r|,\quad
\Pi_{tot}=|\widetilde\Pi_m+\widetilde\Pi_r|.
\]

총 magnitude를 성분 magnitude의 합으로 대체하지 않는다. 일반 텐서에서는 교차 contraction도 필요하며, 이 pilot은 공축 LRS slice로 고정한다. 각 성분의 signed scalar와 magnitude를 모두 내보낸다. 실제 압력 scalar를 저장할 때 J/m³ 및 orthonormal frame을 명시한다. shear source는 계속 K(p_m+p_r)이며 두 별도 trajectory를 선형 합성하여 mixed trajectory로 만들지 않는다.

기존 source moment의 재사용식은 rho_crit,0=3H0²/K일 때

\[
p_m=\rho_{crit,0}(f_m\Omega_m/a_{ref}^3)M_{\pi_s}(x,b),\quad
p_r=\rho_{crit,0}(\Omega_r/a^4)E_2/3.
\]

각 충돌 없는 성분의 에너지식은
\(d\rho_m/dx=-3(\rho_m+\bar p_m)-6(s/H)p_m\),
\(d\rho_r/dx=-4\rho_r-6(s/H)p_r\)다. dust와 Λ를 기존 방식으로 합치면 Hamiltonian constraint 전파는 이전과 같다. Wolfram에서 half-norm squares `3pm²,3pr²,3(pm+pr)²`, cross contraction `6pm pr`, anisotropic work `6s(pm+pr)`, constraint derivative 0을 실제 확인했다.

## 허용 초기 영역과 실제 할 일

1. 기존 625개 history를 추가 ODE 없이 분해한다. 원본 NPZ의 `massive_pi_s_norm`, `E2`, `H_per_s`, `x`를 사용하고 원본 파일을 바꾸지 않는다. signed component 합이 원래 `signed_Pi`를 재현하는지 전 sample에서 검사한다.
2. 초기 matter 응력의 companion slice: Σ0∈[0,.004]의 기존 13 magnitude/비영 ±sign과 Π_m0∈(0,.0004]의 12 magnitude/±sign을 조합하여 **600개 새 조건**을 실행한다. 새 조건의 radiation 초기 k=0이다.
3. matter slice의 zero axis 25조건은 기존 625 중 neutral control을 **기존 자료 참조**로 사용한다. actual realized component axes, old k, old source/case identity를 유지한다. `REFERENCE_REUSE`로 표시하며 새 source/config의 resume나 새 실행으로 바꾸지 않는다. 기존 tiny offset은 물리축 허용오차1e-12 안에 있지만 exact zero/bitwise equivalence라고 부르지 않는다.
4. mixed 초기 cancellation **6조건**: signed S0=√3 s/H∈{0,+.004,-.004}, signed Π_m0=±.0004, signed Π_r0=−signed Π_m0. 두 성분 초기 타깃을 각각 실현하고 실제 coupled ODE를 계산한다.

새 scientific sweep은 합계 **606 trajectory solves**다. 기존625를 다시 세거나 replay하지 않는다. radiation-only 원래 slice도 “초기에 matter-isotropic”이라고 표현한다. 진화 중 반대 성분 응력이 유도될 수 있다.

fm=.1, mass/Tref=30, zbar20→4, cosmology lock, 24×12 Gauss3 cells, L8 even block, rtol3e-11/atol3e-13,65 samples를 고정한다. 초기 massive 분포 W_m=1+A_m P2의 source positivity 범위는 −1≤A_m≤2다. 실제 원본 helper 평가에서 Σ0=.004의 attainable signed Π_m0는 약[−.0004833821888780,+.0009667643777560]이다. 따라서 symmetric ±.001 matter sweep은 이 고정 모델에서 불가능하다. 선택한 ±.0004는 |A_m|max≈.827502563이며 양의 분포를 유지한다. 실제 helper 기반 inversion과 실현 오차≤1e-12로 매 초기 타깃을 확인한다. 실패 시 모델의 mass/fraction/tolerance를 바꾸지 않고 반환한다.

## 구현·검증·자원 계약

원본 parent pilot.py와 vendor4개는 변경하지 않는다. 이 additive 디렉터리의 adapter가 기존 immutable source helper, radiation even matrix, bounded moment_batch, resource observer를 재사용한다. worker당 하나의 모델/행렬/기본 quadrature를 유지하며 bounded memory로 성분 diagnostics를 벡터화한다. 상태는 여전히8개다. 전체606개를 하나의 거대한 vectorized solve_ivp state로 결합하지 않는다.

새 model/config/source/case identity와 stdout/stderr/command/exit receipt, NPZ/JSON checkpoint를 남긴다. 실제 local max8, NCP max64, BLAS/OpenMP1, nice10, 관측 affinity/cgroup/spare CPU/memory, 명목256MiB/worker 및 reserve를 유지한다. 새 확장에 유한 wall900초/aggregate child3600초를 적용하고 실패·미완료는 자동 retry하지 않는다. 다른 작업을 종료하거나 다른 세션의 존재만으로 작업을 중지하지 않는다. 기존 V12 cap/debit에 합치거나 그 debit을 환불하지 않는다.

필요한 새 검증은 다음으로 한정한다.

- **4개 새 원본40-state 대 reduced8-state 비교**,65시점: signed(Sigma0,Pi_m0,Pi_r0)=(+.004,+.0004,0),(-.004,-.0004,0),(0,+.0004,-.0004),(+.004,-.0004,+.0004). b,s/H,E0,E2, signed Pi_m/Pi_r/total 최대절대차≤1e-8, 원본H² constraint≤2e-13.
- A_m 양/음에서 **2개 massive directional energy identity** 검사, 상대잔차≤1e-7.
- 기존625의 모든 저장 시점에서 component-sum reconstruction, 새606의 초기 타깃 실현/finite positive energy/H/cell populations 및 저장 angular brightness 진단.
- 새 inversion과 reference-provenance의 필요한 작은 표적 검사만 수행한다. 과거6source comparisons/L8-L12/tolerance campaign을 다시 의무 반복하지 않는다. material discrepancy가 있을 때만 한 가지 원인을 표적으로 조사한다.

성분별 CSV/NPZ, 새 matter Σ heatmap, 기존 history의 성분 분해 그림, mixed cancellation의 signed component/Σ 진화를 제공한다. 600새+25참조 matter table의 provenance를 명확히 한다. NCP에서는 새606실행 및 그림만 수행할 수 있도록 실행 파일을 준비한다. 기존 derivative benchmark나 detailed performance campaign은 하지 않는다. 상태 수/재사용/벡터화 구현과 실제 실행 시간은 기록하되 speedup/RSS 감소를 주장하지 않는다.

## 과학적 판정과 게시

Astra root가 이 계약/이론을 고정하고 lower-tier agent가 구현·실행하며, 구현하지 않은 Astra가 새 source와 raw 성분 분석을 독립 검토한다. 새 결과의 판정 전에는 `PENDING_INDEPENDENT_REVIEW`다. 기존 preliminary625 PASS는 유지한다. production은 계속 NOT_ISSUED이고 일반 Bianchi I, full native H/He, source-on order/positivity/continuous certificate 등의 HOLD를 승격하지 않는다.

기존 PR198 branch에 expected-head fast-forward로 additive 게시한다. 계약 단계와 완료 단계의 Drive/Dropbox 백업 및 DAG 상태를 기록한다. 기존 archive를 덮어쓰지 않으며 새 패키지의 source/data/command/exit/hash를 실제 evidence에 묶는다. Codex 및 다음 대화 handoff는 이 성분 분리를 최신 목표로 반영한다.
