# CR PHYS16: 원본 2p 여기 사건에서 조건부 Lyα 방출 스펙트럼과 첫 공명산란

## 1. 물리적 범위와 분리된 주장

- 계량 부호 `(-,+,+,+)`; 본 실험은 국소 정지 100 K 중성수소 균질계의 비상대론적 전자·원자 운동학이다. 시공간의 Bianchi IVP나 공통 진화 기체·복사·기하를 풀지 않는다.
- 원본 source는 PHYS15 ZIP SHA-256 `48cda47e966bb0e9309753d4cbb089977218d6f1a364f67a8331fec0f19ba316`과 그 안의 PHYS14 및 원래 6,400 H/He RR 광자, 4 birth bins이다. H의 첫 광흡수 이후, 최초 전자 비탄성 충돌이 H(1s→2p)인 원본 measured/model 공통 영역 2,066개에만 적용한다. 그 2,066개 광자는 전부 He 재결합 기원이다. H photoionization의 소유권과 Shah measured H ionization, NIST BE-scaled 2p의 두 경쟁 rate는 그대로 유지한다.
- `established`: 전자충돌에서 에너지·운동량 보존, Doppler 변환, 단일선 Voigt 자연폭, 원본 시간순 source event.
- `derived`: 고정 표적 두 물체 비탄성 반동의 해와 원자 반동을 포함한 방출 주파수 연산자.
- `conjectural model closure`: 1s→2p 첫 Born 미분 각도분포(PWBA)를 원본 BE 적분 충돌률의 조건부 각도 weight로 정규화; 여기된 2p 정렬축을 momentum transfer에 평행하다고 가정; E1 분극 합산 각도 분포 사용. 진짜 14.6–21 eV DCS 측정이나 CCC angular rate가 아니다.
- `numerically checked`: 원본 source와 결합한 6개의 조건부 시간순 첫 산란 스펙트럼, 세 closure별 재분배 atlas. `unresolved`: 물리적 source-owned 실제 emission PDF, 정확한 resonance scattering detailed balance 및 다중산란, global radiation owner.

## 2. 충돌 반동: 운동학적으로 정확한 비상대론적 식

정지 H(1s) 표적의 질량 M_H, 입사 전자 p_i, 산란각 μ=cosθ, 출사 p_f로 놓고 E_e=p_i²/(2m_e), 전자 전달 여기 에너지 ΔE=10.1988 eV (부모의 에너지 장부 컨벤션)로 고정한다.

```
E_e = ΔE + p_f²/(2m_e) + |p_i-p_f|²/(2M_H)
q⃗ = p⃗_i-p⃗_f,     v⃗_exc = q⃗/M_H.
(1/m_e+1/M_H)p_f² - (2p_i μ/M_H)p_f
  + 2ΔE + p_i²/M_H-p_i²/m_e = 0.
```

양의 해 p_f는 입사 운동학에만 의존한다. 각 (E_e, μ)에서 recoil energy q²/(2M_H)의 계산된 상대 에너지 잔차는 최대 6.102×10^-16. 이 조건은 총 cross section으로부터 각도 분포가 유일하게 정해진다는 주장이 아니다.

수소 수소양자계 1s→2p form factor의 momentum-transfer z=qa_0/ħ에 대한 각도 합은 `|F(z)|²=72 z²/(z²+9/4)^6` (hydrogenic PWBA construction). 고에너지 first-Born 모델의 상대 각도분포를

```
w_B(μ|E_e) ∝ (p_f/p_i) |F(z)|²/z⁴,     ∫[-1,1] w_B dμ = 1
```

로 잡고, **정규화 이후** 원본 BE-scaled total collision rate를 재사용한다. 따라서 원본 충돌 계수나 사건수는 변하지 않는다. 근접 문턱에서는 첫 Born이 통제된 정확한 산란해라는 보장이 없고, 본 결과는 불확실한 closure 의존성을 별도로 노출한다.

추가 가정: 첫 Born에서 전이 dipole이 q 방향으로 정렬되고, 2p의 E1 방출은 상대 방향 w=cosχ에 대해 `p_E1(w)=3(1-w²)/4`, `-1≤w≤1`이며 `E[w]=0`, `E[w²]=1/5`이다. 이 angular polarization의 원자 세부 구조 및 CCC 보정은 미포함이다.

## 3. 조건부 Lyα 방출선

`ν0=ΔE/h`, `v_th=√(2 k_B T_K/M_H)`, `Δν_D=ν0 v_th/c`, `a=A21/(4πΔν_D)`로 놓는다. `x=(ν-ν0)/Δν_D`; `φ_V(y)=Re[w(y+ia)]/√π`는 x에서 적분해 1. 자발 방출 photon momentum recoil에 의한 무차원 중심 이동은 `η_em=hν0/(2M_H c v_th)`, 각도에 따라 충돌 반동에 의한 이동은 `(q/M_H v_th)w`이다. 100 K 초기 H 열속도는 Maxwellian이며, 열축 방향 확률은 `Gaussian(0, variance=1/2)`.

```
p_em(x|E_e, MODEL) = ∫_-1^1 dμ w_MODEL(μ|E_e)
                      ∫_-1^1 dw p_E1(w)
                      φ_V[x - (q(E_e,μ)/(M_H v_th)) w + η_em].
```

모든 모델은 `x∈ℝ`에서 양수·정규화이다. 옵션: `BORN_DIPOLE`(주요 가설), `ISOTROPIC_IMPACT_DIPOLE`(반동 각도 민감도), `BORN_ISOTROPIC_EMISSION`(방출 편광 민감도). 마지막 옵션에서는 `p_E1(w)=1/2`; 이는 대체 closure이지 물리적 실측이 아니다. 자연 Lorentz 꼬리로 인해 전체 스펙트럼의 두 번째 모멘트는 발산한다. CSV에 적힌 centre variance는 **자연폭 convolution 이전의 recoil+thermal centre**에 관한 양이다.

원본 excited 2p 출생 source `r_{2p,i}(u)`와 관측 clock `T`를 유지한다. 이전 PHYS15의 각 x에서 first HI scattering rate `q_s(x)=c n_HI σ_Lyα(x)` (`n_HI=138.6 m^-3`)와 원본 시간순 값을 결합한다.

```
N1_model(T) = Σ_i ∫_{-∞}^{∞} dx p_em(x|E_e,i)
                ∫_{s_i}^T du r_{2p,i}(u) [1-exp(-q_s(x)(T-u))].
```

원본 source 2,066개 각각에서 이전의 exact first-event formula와 GL160 / Laguerre64 endpoint integral을 사용한다. 이것은 2p decay delay를 빠른 감쇠 한계로 둔 prompt-scatter 모델이다. 실제 A21=6.2649e8 s^-1 유한 붕괴 지연 차이는 원본 PHYS15의 `q/A21` 상한으로 별도 표시한다. x∈[-16,16] 이외 꼬리는 모델에서 `P(|x|>16) <= P(|Voigt|>16-B)`라는 삼각부등식 기반 연속론 상계(B=최대 절댓값 중심 이동)로 제한한다. 꼬리 적분은 SciPy QUADPACK으로 계산하고 10^-10의 여유를 더했다. 따라서 **꼬리에 관한 수학적 상계의 수치평가는 정식 directed-rounding interval certification이 아니다.** 또한 x-grid 내 적분의 이산화 오차는 이 꼬리 상계에 포함되지 않는다.

## 4. 첫 HI 재분배: one-scatter conditional operator

입사 x_i를 이미 알고, 온도 100 K·정지 HI에서 resonant absorption을 일으킨 원자 열속도 u=v_parallel/v_th는 무조건 Maxwellian이 아니다.

```
P(u|x_i)= [ exp(-u²)/√π * a/(π((x_i-u)²+a²)) ] / φ_V(x_i).
```

원자 rest frame의 coherent scattering과 unpolarized Rayleigh phase `P(μ)=3(1+μ²)/8`를 적용한다. 단일 산란 후 입사 주파수를 쓰면

```
x_o = x_i + (μ-1)(u+η_sc) + √(1-μ²) v⊥/v_th,
η_sc=hν0/(M_H c v_th)=2η_em.
```

최종 transverse thermal component는 평균 0, 분산 1/2인 정규분포. 계산된 재분배 kernel은 conditional `R_model(x_o|x_i)`, `∫dx_o R_model=1`, 모든 bin은 gaussian CDF로 정확히 적분. 모델 내 평균은

```
E[x_o|x_i] = x_i - E[u|x_i] - η_sc.
```

이 간략 모델에는 재반동의 nonrel O(v/c) 항과 coherent assumption을 사용하지만, microscopic detailed balance를 보장하는 정확한 전이율 비율, Lyα 2P fine-structure interference, 21-cm spin-flip, stimulated terms, recoil correction higher orders, multi-scattering, spatial escape, common evolving gas/geometry는 미포함이다. 원본 Hummer R_II 형식의 **단일산란 유사 모델**이지 그 전체 물리적 연산자에 대한 수학적 동일성 주장이 아니다.

## 5. 판별 및 노드 판정

1. 수학적 반동 운동학 + total-rate-preserving closure의 source spectral integration은 국소 물리 탐색 산출물로 수용한다. 문헌/실측 DCS 또는 신뢰할 수 있는 CCC amplitude 없이는 고유 source-owned recoil PDF로 승격하지 않는다.
2. 최초 산란 spectrum은 PHYS15 x=0의 각 2,066 소스별 계산을 4e-16 수준에서 재현하며 주파수 적분은 새로운 조건부 물리량이다. 방출 photon escaping flux, 다중 scattering rate, global radiation field가 아니다.
3. one-scatter kernel은 각 fixed incoming frequency에서 normalization/first moment 검증만 인정한다. 물리적 R_II / full line-transfer 승인 불가.
4. 중앙 DAG 28/88 (+0), extension 0/3 (+0), PHYS16 보조 조건부 연구 단위 1/1; 기존 PHYS15 보조 단위 1/1은 변경하지 않는다. independent distinct-author R06/C09 NOT_RUN; real native subagent NOT_RUN; NATIVE25/L4/production HOLD. NO_MERGE, NO_FORCE_PUSH 유지.
