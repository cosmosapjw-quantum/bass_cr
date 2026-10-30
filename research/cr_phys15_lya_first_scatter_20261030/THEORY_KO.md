# PHYS15: 2p 자발방출 및 최초 Lyα 공명 산란 (조건부 국소 물리)

## 정의와 출처

서명 (-,+,+,+), proper time t in s. 원래 H/He RR 광자 6,400개와 4개 birth bin, 불변 PHYS14 source. 100 K의 정지 균질 HI 밀도 138.6 m^-3, 원래 H 첫 광이온화 hazard k_H(E)와 전체 hazard k(E). 최초 H photoelectron E_e = E-I_H. **실측 Shah 이온화와 NIST 모델 2p 여기 양쪽 모두 유효한 공통 영역**에서만 ν_I=n_H σ_I(E_e)√(2E_e eV_J/m_e), ν_2=n_H σ_2(E_e)√(2E_e eV_J/m_e), ν=ν_I+ν_2.

원 광자 출생 s 뒤 u≥s에 발생하는 첫 2p 전자충돌의 밀도:

 r_2(u|s,E) = k_H ν_2 ∫_0^(u-s) exp(-k x) exp[-ν((u-s)-x)] dx
 = k_H ν_2 (u-s) exp[-k(u-s)] exprel[(k-ν)(u-s)].

eV 단위 에너지 장부: E_e = E_21+(E_e-E_21), E_21=10.1988 eV (원 모델 컨벤션). 여기 사건 자체는 Lyα 방출이 아니며 먼저 2p 상태가 생성됨.

## 복사 방출

NIST Wiese-Fuhr 전이율 A_21=6.2649e8 s^-1 (선택된 2p fine-structure rate). 자연 수명 τ=1/A=1.59619 ns. 비복사 소멸 또는 비탄성 외부 강제감쇠가 없는 **조건부 spontaneous-only model**에서 실제 방출 지연 PDF는 A exp(-AΔ). 따라서 P_emit(T)=∫_s^T r_2(u)[1-exp(-A(T-u))]du; N_exc-N_emit = ∫ r_2(u)exp[-A(T-u)]du. 양의 source에 대해 각 birth bin마다 0 ≤ (N_exc-N_emit) ≤ W k_H ν_2 (T-s)/A, 전체 상한은 합산. 수치에서 아주 작은 ns 간격을 subtractive cancellation하지 않도록 upper/lower로 기록함.

## 정지 균질 100 K HI 첫 공명산란

조건부 Lyα 주파수 offset x=(ν_γ-ν_α)/Δν_D, Δν_D=ν_α√(2k_B T/m_H)/c, a=A/(4πΔν_D). 전자기 oscillator strength f=0.41641와 Voigt H(a,x)=Re[w(x+ia)]로

 σ_Lyα(x) = [e²/(4 ε₀ m_e c)] f H(a,x)/(√π Δν_D) [m²],
 q(x)=c n_H σ_Lyα(x) [s^-1].

선택된 주파수의 첫 산란 사건만 계산하며, 산란 후 주파수/방향 재분배·다중산란·탈출은 추적하지 않는다. 2p 붕괴 즉시 방출 근사에서

 P_sc^prompt(T|s,E,x)=∫_s^T r_2(u|s,E)[1-exp(-q(x)(T-u))] du.

유한 A 방출 지연을 포함한 정확 첫 산란 확률은 2개의 양의 지수 대기시간(방출, 산란)의 합 CDF를 r_2와 convolution하여 얻을 수 있다. A>q>0이면 prompt–finite 차이는 각 여기 시점 u에 대해 정확히

 Δ(w)=q[exp(-qw)-exp(-Aw)]/(A-q) (w=T-u),
 0≤Δ(w)≤q/(A-q).

따라서 전체 첫 산란 사건수는 [P_sc^prompt-q/(A-q) P_exc, P_sc^prompt]에 놓이며 이 범위는 자체 조건부 모델에서 rigorously derived. source마다 출생위치·에너지를 보존하며 횟수와 결합에너지 전환을 섞지 않는다.

## 생략 영역/경계

이것은 Lyα *escaped flux*나 CMB reionization radiation solution이 아니다. x는 방출 source에서 유도된 광자 주파수 PDF가 아닌 **조건부 입력 변수**. 여기된 수소 recoil, 공간 boundary, 원자 속도분포 비등방성, Bianchi geometry, redistribution R_II, full electron K/energy stopping, 다른 excitation (2s, 3p), multi-inelastic cascades 및 He double 사건은 모두 unresolved. 중앙 DAG 승격 불허. `R06_DISTINCT_AUTHOR=C09_DISTINCT_AUTHOR=NOT_RUN`.
