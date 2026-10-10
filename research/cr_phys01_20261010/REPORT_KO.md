# 실제 cosmic-ray 입력을 연결한 IGM 재이온화 연구 결과

작성: 2026-10-10. 적용 대상: non-tilted axisymmetric Bianchi I의 H/He IGM. 기준 구현은 이 패키지의 `src/provider.py`와 원천 파일을 고정한 `evidence/SOURCE_MANIFEST.json`이다.

**이번 결과로 입력 상태를 `NO_PHYSICAL_PROVIDER`에서 `CONDITIONAL_PHYSICAL_COMPONENT_AVAILABLE`로 바꿀 수 있다.** 초신성 양성자 주입, massive-particle 비등방 수송, 원자 H/He 충돌, 실제 전자 cascade 표, REI native receiver를 연결했다. H I·He I·He II 이온화 사건과 가열·여기 에너지가 모두 0이 아닌 값으로 계산된다. 따라서 물리적 source 없이 receiver 형식만 준비된 단계는 넘어섰다.

승격 범위는 **고정된 가스 상태에서 1–4 MeV 양성자의 이온화 손실 성분을 평가하는 국소 계산**이다. 전자 침적의 시간 지연, 변화하는 가스와의 되먹임, 전체 CR 손실, 우주론적 재이온화 역사는 아직 닫히지 않았다. 이 제한은 최종 수치와 함께 보존한다. 실행 모델 자체의 식별은 `UNKNOWN`이며 특정 GPT 모델에서 실행되었다는 주장으로 대체하지 않는다.

## 1. 무엇이 실제로 바뀌었는가

이번 작업은 사용 가능한 문헌을 목록화하는 데서 끝나지 않았다. 물리적 입력을 선택하고 출처와 단위를 고정한 뒤 실제 함수와 packet을 만들었다. 원문식과 공개 코드 사이의 적분 불일치를 고쳤고, 표의 원자료 잔차를 드러낸 상태에서 작은 수치 보정만 허용했다. 마지막으로 REI의 기존 보존 검사를 통과할 수 있는 species·electron·thermal source로 변환했다.

| 단계 | 실제 구현과 증거 | 판정 범위 |
|---|---|---|
| 초신성 CR source | [injection.py](src/injection.py), [source 연구](research/INJECTION_MODEL_KO.md) | 전체 10 keV–1 PeV 정규화 완료 |
| Bianchi 수송 | 같은 파일의 `transport_population` | 일정 H와 shear의 정확한 무충돌 characteristic |
| proton-impact ionization | [rudd.py](src/rudd.py), [kernel 검사](research/RUDD_KERNEL_CHECK.json) | neutral H/He, underlying adapter 1–10 MeV |
| 전자 에너지 분배 | [fs10.py](src/fs10.py), [독립 검토](research/FS10_INDEPENDENT_REVIEW.json) | 지정된 ionization fraction의 FS10 terminal response |
| 결합 provider | [provider.py](src/provider.py), [CR_PACKET](evidence/CR_PACKET.json) | 공통 proton 구간 1–4 MeV의 순간 rate |
| REI receiver | `rei_bianchi/rust/rei_microphysics/src/axisym_cr_deposition.rs` | 고정 source·gas·geometry에 결속된 국소 derivative |
| 실제 수치와 그림 | [검증 결과](evidence/PROVIDER_VERIFICATION.json), [그림 PDF](evidence/CR_DEPOSITION_COMPONENT.pdf) | 제한된 성분의 수치 결과; 전체 재이온화 곡선 아님 |

처음 검토한 DarkHistory/MEDEA 자료도 조사 기록으로 남겼지만, 현재 실행 provider의 전자 성분은 **Furlanetto–Stoever 2010, 이하 FS10**이다. 공식 공개 archive와 21cmFAST 배포본을 비교하여 표의 일치를 확인했다. 두 후보를 섞어 사용하거나 미실행 DarkHistory 분기를 실행된 provider로 표시하지 않았다. 관련 선택 근거는 [DEPOSITION_PROVIDER_SELECTION_KO.md](research/DEPOSITION_PROVIDER_SELECTION_KO.md), 출처는 [PROVIDER_SOURCES.json](research/PROVIDER_SOURCES.json)에 있다.

## 2. 초신성 양성자 source와 선택한 국소 상태

주입 모형은 Leite et al. (2017)의 momentum power law에 Madau–Dickinson (2014, MD14)의 comoving SFRD를 결합한 `CRP_L17_MD14_v1`이다. K는 proton kinetic energy, M=mpc², K0=1 GeV로 놓는다.

\[
q_p(K,t)=C(t)\beta(K)^{-1}
\left[\frac{K(K+2M)}{K_0(K_0+2M)}\right]^{-\alpha/2},
\quad\beta=\frac{\sqrt{K(K+2M)}}{K+M},\quad\alpha=2.2.
\]

지원 구간은 10 keV≤K≤1 PeV이다. 정규화는 이 **전체 구간**의 \(\int Kq_p\,dK\)가 초신성 CR 주입 power와 같도록 잡는다. 실제 충돌을 계산하는 1–4 MeV 구간에 source를 다시 정규화하지 않는다.

\[
\psi(z)=0.015\frac{(1+z)^{2.7}}{1+[(1+z)/2.9]^{5.6}}
\ \mathrm{M_\odot\,yr^{-1}\,Mpc^{-3}},
\]
\[
\dot u_{\rm inj,proper}=a^{-3}\epsilon_p f_{\rm esc}E_{\rm SN}
\frac{k_{\rm CC}\psi(z)}{({\rm yr\ in\ s})({\rm Mpc\ in\ m})^3}.
\]

선택값은 εp=0.1, ESN=10⁵¹ erg, fesc=1이다. 마지막 값은 full-escape 시나리오이며 관측으로 확정된 값은 아니다. MD14의 Salpeter IMF에 맞춰 kCC=0.0068/Msun을 썼다. Leite의 다른 IMF에서 유래한 약0.01/Msun을 혼용하지 않았다. 현재 구현은 MD14 fit-use 범위를 z=0–8로 제한하고, z=8에서 source를 고정한다. 평균 부피 redshift를 사용하는 이 source 처방이 비등방 우주에서 은하 형성을 자체 계산한다는 의미는 없다. [Leite 원문](https://arxiv.org/abs/1703.09337v1), [MD14 원문](https://arxiv.org/abs/1403.0007v3).

| 국소 계산 조건 | 실제 선택 |
|---|---:|
| source snapshot | z=8 |
| 시작 CR 분포 | 0; 통제된 source turn-on |
| 분포를 준비한 시간 | 10¹⁰ s ≈316.881년 |
| 평균 팽창률 H | 3.3×10⁻¹⁷ s⁻¹ |
| shear 변수 s | 3.3×10⁻¹⁸ s⁻¹ |
| H⊥, H∥ | 2.97×10⁻¹⁷, 3.96×10⁻¹⁷ s⁻¹ |
| proper nH, nHe | 140, 11.5425532 m⁻³ |
| nominal helium 질량분율 | YHe=0.248 |
| 가스 온도 | 100 K |
| 이온 분율 | xHII=xHeII=0.01, xHeIII=0 |

이 IC는 관측에 맞춘 우주론적 해가 아니다. 원래 source가 없는 상태에서 일정 시간 동안 주입한 CR 분포를 정해 놓고 local operator를 검사하는 시나리오이다. source history를 바꾸거나 가스가 상태점에서 벗어나면 현재 고정 packet을 재사용할 수 없다.

## 3. massive-particle Bianchi 수송의 구현

normal observer의 정규직교 틀에서 H⊥=H−s, H∥=H+2s이다. μ=p∥/p라 하면

\[
\dot p=-p[H+s(3\mu^2-1)],\quad
\dot\mu=-3s\mu(1-\mu^2),\quad
\dot K=-\frac{K(K+2M)}{K+M}[H+s(3\mu^2-1)].
\]

nonrelativistic limit의 에너지 감소율은 −2KHray, ultrarelativistic limit은 −KHray이다. 따라서 저에너지 양성자에 photon의 redshift 식을 그대로 적용하지 않는다. 현재 코드는 일정 H,s에서 각 운동량 성분을 지수함수로 운반한다.

\[
p_\perp=p_{\perp,0}e^{-(H-s)\tau},\qquad
p_\parallel=p_{\parallel,0}e^{-(H+2s)\tau}.
\]

birth 좌표에서 적분하는 각 입자의 proper number-density 가중치는
\(e^{-3H\tau}q_p(K_0)dK_0d\tau d\mu_0/2\)이다. 이미 이 좌표에서 적분한 결과에 final energy/angle Jacobian을 다시 곱하지 않는다. 각 birth 방향·age에서 최종 1 MeV와 4 MeV 경계를 역으로 찾아 적분 구간을 나누므로, 불연속 mask를 드문 grid점에 적용하는 오류도 피했다. s=0에서는 방향에 무관한 FLRW momentum redshift를 복원한다.

이 분포는 충돌 손실의 되먹임을 넣기 전 무충돌 CR snapshot이다. 최종 population으로 계산한 loss/kinetic energy에 age를 곱한 진단값은 1.72857×10⁻⁶이다. 작은 값은 이번 국소 성분 평가를 지지하지만, 최종 quadrature node들의 표본 추정이며 전 궤적의 supremum 또는 증명된 error bound는 아니다. 누적 충돌 사건 수를 얻으려면 population을 시간에 대해 추가 적분해야 한다. endpoint rate에 10¹⁰ s를 곱한 것을 정확한 누적 history로 해석하지 않는다.

## 4. 실제 H/He 충돌과 전자 cascade의 연결

### 4.1 proton-impact kernel와 공개 코드의 수정

[CRIPTIC 원문](https://arxiv.org/abs/2207.13838v2) Eq23–25 및 실제 author code의 atomic coefficient를 채택했다. \(w=W/I_s\), \(t=(m_e/m_p)K/I_s\), \(A_s=4\pi a_0^2N_s(R/I_s)^2\)에 대해

\[
\frac{d\sigma_{p,s}}{dW}=\frac{A_s}{I_s}
\frac{F_{1,s}(t)+F_{2,s}(t)w}{(1+w)^3},
\qquad W_{\max}=4(m_e/m_p)K-I_s.
\]

H 원자는 upstream의 Williams-limit 선택 F1=7/(3t), F2=1/t를 쓴다. He 원자는 Rudd 계수를 사용한다. H2의 경험식을 H 원자로 바꾸어 쓴 것이 아니다. underlying adapter는 1–10 MeV를 허용하지만 전체 provider는 전자 표와 안전하게 겹치는 **1–4 MeV**로 더 좁혔다. Wmax는 upstream의 nonrelativistic prescription으로서 정확한 relativistic endpoint가 아니다. H 근사의 오차와 He fit의 물리적 불확실성을 수치 적분 오차와 구분한다.

원문 Eq26와 C++의 total cross section에는 F2 항의 numerator가 w로 적혀 있다. 그러나 미분 단면적의 적분은 w²를 준다.

\[
\int_0^w\frac{u}{(1+u)^3}du=\frac{w^2}{2(1+w)^2}.
\]

이에 따라 source SDCS와 stopping moment에 일관되도록 total cross section을 수정했다. [Wolfram 실제 반환](evidence/WOLFRAM_MOMENTS.json)도 이 적분을 확인한다. 독립 수치적분과 analytic moment의 최대 상대 차이는 약3.1×10⁻¹⁴였다. 수정 전 total/SDCS integral 비는 검사점에서 H 약0.700–0.704, He 약0.757–0.865여서 그대로 넘길 수 없는 차이였다. 원래 식은 비교용 함수에만 남겼다.

### 4.2 FS10 표와 적용 조건

현재 표는 [Furlanetto–Stoever 원문](https://arxiv.org/abs/0910.4410v1)의 공개 전자 degradation 결과이다. 21cmFAST의 특정 commit과 파일 hash를 고정했으며, 공식 archive와는 마지막 newline을 제외한 내용이 같다. 현재 사용하는 `log_xi_-2.0.dat`는 258개의 10–9937.21 eV energy node와 H I/He I/He II 이온화 횟수, 가열, 여기, Lyα 정보를 제공한다. [획득 증거](research/FS10_ACQUISITION.json).

코드는 xHII=xHeII=0.01, xHeIII=0만 받아들인다. 임의 이온 분율로 보간하지 않으며 table energy 상한도 잘라서 계속 진행하지 않는다. 1–4 MeV proton의 secondary endpoint는 상한 안에 들어간다. 10 eV 아래 전자의 에너지를 heat로 보내는 것은 FS10의 **terminal degradation** 처방을 채택한 결과이다. 이는 짧은 시간 안에 thermalization이 완료되었다는 시간해가 아니다.

표 header의 z=10, T=100 K를 실제 확인했다. 이를 z=8의 저밀도 가스에 사용하는 것은 terminal fraction의 약한 density 의존성을 이용한 명시적 근사이다. **원 Monte Carlo의 정확한 helium abundance는 복원하지 못했다.** 따라서 선택한 YHe=0.248을 원자료와 정확히 일치한 조성이라고 부르지 않는다. 이 두 불확실성이 있으므로 현재 결과는 조건부 물리 성분이다. 원천 metadata가 충돌하는 다른 분율 파일을 자동 수정하여 확대하지 않았다.

FS10의 final excitation은 gas 밖으로 보내는 저에너지 복사 에너지이다. Lyα는 그 일부여서 총 여기 에너지에 또 더하지 않는다. 원 모형 내부에서 재흡수한 helium excitation의 ionizing photons를 receiver에 다시 주입하면 이중 계산이 된다. 이번 receiver는 별도의 photon spectrum을 복원하지 않고 ionizing-photon number/energy source를 0으로 둔다.

### 4.3 primary binding과 secondary kinetic energy를 분리한 convolution

target density ns는 proper density이다. primary 사건 수와 생성 전자는

\[
R_{s,\rm prim}=n_s\int\mathcal N_pv_p\sigma_s\,dK d\Omega,
\qquad
Q_e(W)=\sum_s n_s\int\mathcal N_pv_p\frac{d\sigma_{p,s}}{dW}\,dK d\Omega.
\]

양성자가 잃은 에너지는 binding Is와 전자 kinetic W의 합이다. cascade에는 **W만** 넣고 Is는 primary ionization ledger에 한 번 기록한다. 최종 secondary channel j가 전자당 에너지 또는 사건 yield Yj(W)를 주면

\[
\dot{\mathcal R}_j=\int Q_e(W)Y_j(W)\,dW.
\]

현재 구현은 모든 table node와 atomic threshold에서 구간을 분할한다. 구간 안의 piecewise-linear yield를 Rudd의 analytic number/energy moment와 합성하므로 sampling만으로 희박한 He II 채널을 놓치는 일을 줄였다. 독립 adaptive quadrature와 비교한 30개의 target·energy·channel 조합의 최대 상대 차이는 2.05853×10⁻¹³이다.

## 5. 실제 비영 결과와 에너지 수지

아래 값은 [CR_PACKET.json](evidence/CR_PACKET.json)과 [PROVIDER_AUDIT.json](evidence/PROVIDER_AUDIT.json)의 현재 결과를 읽은 것이다. manifest 및 packet hash는 이 파일들과 [SOURCE_MANIFEST.json](evidence/SOURCE_MANIFEST.json)을 authoritative하게 사용한다. 보고서에 이전 hash를 복사해 고정하지 않는다.

| 이온화 사건 | primary rate | secondary rate | 단위 |
|---|---:|---:|---|
| H I→H II | 3.0408320×10⁻²⁵ | 2.4095904×10⁻²⁵ | m⁻³ s⁻¹ |
| He I→He II | 3.9395188×10⁻²⁶ | 1.3473438×10⁻²⁶ | m⁻³ s⁻¹ |
| He II→He III | 이번 primary kernel에 없음 | 1.8524261×10⁻²⁹ | m⁻³ s⁻¹ |

총 electron source는 5.97929394×10⁻²⁵ m⁻³ s⁻¹이다. He II 이온화가 0이 아닌 이유는 실제 전자 cascade가 기존 He II에 작용하기 때문이다. 양성자 kernel에 He II target을 구현했다는 뜻은 아니다.

| power 또는 수지 | 값, J m⁻³ s⁻¹ |
|---|---:|
| **전체 10 keV–1 PeV source 주입** | **5.31537175×10⁻³⁴** |
| **모델에 포함된 1–4 MeV 이온화 손실** | **3.26700196×10⁻⁴²** |
| 최종 heat | 1.20930446×10⁻⁴² |
| ionization event의 internal-energy 증가 | 1.39637507×10⁻⁴² |
| excitation escape | 6.61322430×10⁻⁴³ |
| 별도 continuum escape | 0; 추가 독립 채널로 분해하지 않음 |
| 보정 전 선택된 보간법의 energy defect | +1.64972939×10⁻⁴⁶ |
| heat closure correction | −1.64972939×10⁻⁴⁶ |
| 허용한 correction bound | 2.44893211×10⁻⁴⁶ |

두 굵은 power는 서로 다른 물리량이다. 모델 손실/전체 주입 비는 약6.14633×10⁻⁹이다. 이는 317년 동안의 특정 dilute snapshot에서 얻은 제한된 채널의 순간 비율이며, 전체 우주에서 CR의 최종 침적 효율이라고 해석할 수 없다. receiver의 `external_power`에는 전체 source가 아니라 모델 손실만 들어간다.

최종 CR kinetic storage는 5.31536806×10⁻²⁴ J m⁻³이다. 그중 active 구간은 4.53304390×10⁻²⁶ J m⁻³, 비율로 **0.85281844%**이다. 구간 밖 **99.14718156%**는 below/above CR 저장 에너지로 남겼다. 이를 heat로 옮기거나 삭제하지 않았다. 팽창 dilution과 signed adiabatic work도 별도 기록한다. 현재 CR 수밀도/nH≈2.88×10⁻¹⁴라는 작은 tracer 값도 확인되지만, 이 사실만으로 은하→IGM의 baryon source 또는 전하 보상 문제를 완전히 해결했다고 할 수는 없다.

![선택된 CR 이온화·침적 성분](evidence/CR_DEPOSITION_COMPONENT.png)

이 그림은 실제 물리적 입력을 가진 **성분 단위 scientific plot**이다. 채널과 원장의 재현성을 확인할 수 있으나 xHII(z), Tgas(z), filling factor, optical depth 또는 21 cm 예측 곡선은 아니다. 수치 원본은 [CSV](evidence/CR_DEPOSITION_COMPONENT.csv), 공유용은 [PDF](evidence/CR_DEPOSITION_COMPONENT.pdf)에 있다.

## 6. 작은 표 잔차와 receiver 보존 검사의 의미

secondary threshold는 13.6/24.6/54.4 eV를 **선언한 표준 근삿값**으로 사용했다. 원 Monte Carlo의 내부 상수를 완전히 복원한 값이라고 하지 않는다. primary threshold는 CRIPTIC convention의 13.605693122994/24.59 eV를 따로 보존했다. 두 경로의 energy accounting을 합치면서 차이를 감추지 않는다.

원자료의 energy-fraction 합과 사건 수×threshold는 유한한 차이가 있다. 선택한 표에서 event energy defect/E의 최대값은 9.52529×10⁻⁵이다. 구현은 미리 정한 10⁻⁴E bound 안에서 heat만 보정하고 원래 값·잔차·보정량을 모두 반환한다. atomic threshold에서 yield가 미리 생기지 않도록 적용한 보간 수정은 별도 항으로 기록한다. 이를 단순 출력 반올림 오차라고 단정하거나 물리적 불확실성의 상한으로 사용하지 않는다.

현재 packet의 aggregate correction은 secondary kinetic power의 약6.73653×10⁻⁵이며, 보정 후 channel energy 합의 residual은 저장된 수치에서 0이다. 기존 REI의 128×machine-epsilon 보존 검사를 느슨하게 만들어 통과시킨 것이 아니다. 그러나 **128ε 통과는 선택한 수치 모형의 에너지 보존**을 검증할 뿐 원자 단면적·threshold의 물리적 정확도를 128ε로 증명하지 않는다. `internal_power` 역시 provider가 정의한 근사 event-energy ledger이며, 모든 채널에서 유일하고 정확한 chemical state potential Uchem이 존재한다는 증명으로 승격하지 않는다.

Rust receiver는 H0→H+, He0→He+, He+→He++ 사건의 부호와 electron 생성을 실제 `AxisymLocalSources`로 전달한다. CR proton 자체를 ambient nucleus inventory에 더하지 않는다. 고정된 gas state, time, temperature, source identity와 실제 packet 숫자를 검사하고, OFF에서는 provider를 호출하지 않는다. 임의의 packet 또는 table 정의역 밖 gas를 같은 source label로 통과시키지 않는다.

구현 경로는 REI 저장소의 `rust/rei_microphysics/src/axisym_cr_deposition.rs`, `axisym_cr_deposition_pin.rs`, `examples/cr_deposition_probe.rs`이다. 독립 검토에서 ON 경로가 임의 geometry를 허용했던 점을 찾아, source manifest의 H/s와 snapshot a=exp(Ht), anisotropy=st까지 결속하도록 수정했다. 수정 후 신규 7개 test와 native 예제를 다시 실행해 통과했고, 별도로 확인한 기존 13개 regression의 PASS 증거도 보존했다. 최종 native 반환의 `matched_geometry=true`를 확인했다. 수정 전 증거와 [geometry 검토 기록](evidence/rei_native/GEOMETRY_REVIEW_FINDING.json)을 남기고, 최종 판정은 [NATIVE_OUTPUT.json](evidence/rei_native/NATIVE_OUTPUT.json), [NATIVE_EXECUTION.json](evidence/rei_native/NATIVE_EXECUTION.json)에 결속했다.

source-only temperature 변화는 반환된 source 원장으로부터

\[
\left.\dot T\right|_{\rm source}
=\frac{2Q_{\rm heat}}{3k_Bn_{\rm th}}
-\frac{T}{n_{\rm th}}\dot n_{\rm th,source}
=+3.81118655\times10^{-22}\ {\rm K\,s^{-1}}
\]

이다. 실제 background 팽창을 포함하면 약−6.59999962×10⁻¹⁵ K s⁻¹로서 −2HT 항이 지배한다. 두 값의 부호 차이는 오류가 아니라 계산 대상의 차이이다. source-only 값은 ledger에서 직접 계산하고, 큰 ON/OFF derivative를 빼는 계산은 상쇄 오차 진단으로만 남겼다. geometry 결속 후 다른 H=s=0 배경에서 같은 ON packet을 받아들이는 우회 경로는 허용하지 않는다. native 예제의 solver interval 수는 0이며, 장시간 적분을 완료한 결과가 아니다.

## 7. 실제 검증과 아직 계산하지 않은 시간 지연

검사는 서로 다른 계층을 구분했다. [주입·수송 검사](evidence/INJECTION_TRANSPORT_CHECK.json)는 14개 focused test를 통과했다. 전체 source normalization을 독립 adaptive 적분과 비교하고, proper/comoving factor, 상대론적 운동량 변환, FLRW 극한, 각도별 characteristic, tail 분할, OFF no-call을 확인했다. [FS10 독립 검토](research/FS10_INDEPENDENT_REVIEW.json)는 고정 상태에서 원자료, threshold, 양수성, 거부 조건과 10,274개 보간 probe를 확인했다.

결합 provider의 48×8×8에서 64×12×12로의 quadrature 비교에서 최대 상대 변화는 primary 약1.51×10⁻¹⁵, secondary 약1.44×10⁻⁶, heat 약1.37×10⁻⁹, excitation 약3.38×10⁻⁹였다. 선언한 2×10⁻⁶ 기준을 통과했다. 이것은 수치 적분의 독립 비교이며 새로운 Monte Carlo 또는 다른 물리 단면적을 이용한 독립 물리 oracle은 아니다. 최종 native 결과의 Decimal70 비교에서 electron source, source-only temperature, 전체 temperature의 상대 차이는 각각 약1.06×10⁻¹⁶, 1.16×10⁻¹⁶, 2.42×10⁻¹⁷였다. 같은 packet의 receiver 산술 검사이므로 provider physics의 독립 재계산으로 표시하지 않는다.

문헌 탐색에 **SciSpace를 실제 사용**했고, 발견한 논문은 primary PDF와 author code로 다시 확인했다. 도구가 반환한 연도 같은 metadata는 원문과 구분했다. **Wolfram도 실제 호출**하여 Rudd moment의 적분식을 검산했으며 반환값을 보존했다. 외부 도구가 논문을 추천했다는 사실과 우리가 해당 원문/코드를 읽고 검증했다는 사실을 각각 기록했다. 세부 원천과 접근 실패는 [INJECTION_SOURCES.json](research/INJECTION_SOURCES.json), [TOOL_USAGE.json](research/TOOL_USAGE.json)에 있다.

현재 가장 중요한 물리적 제한은 **terminal response가 인과적 시간 진화를 대신하지 못한다**는 점이다. 10¹⁰ s는 CR population을 준비한 약317년이다. FS10 table은 그 전자 에너지가 최종적으로 어디에 가는지를 주며, 그 기간 안에 전부 침적되었음을 주지 않는다. 가스가 고정되어 있고 충분히 오래 유지되는 quasistatic local response로 채택한 것이다. 따라서 결과의 `delay_admission=false`는 유지한다. 침적 시간을 따로 풀지 않은 채 이 순간 rate를 source turn-on 뒤의 실제 가열 history로 그리지 않는다.

## 8. 이어갈 연구를 병렬로 나누는 기준

이제 입력 파일 자체가 없는 blocker 대신 범위가 정해진 물리 과제가 남았다. 아래 작업은 현재 source와 event ledger를 공통 인터페이스로 사용할 수 있어 병렬 진행이 가능하다.

| 연구 lane | 필요한 확장 | 완료 판단에 필요한 결과 |
|---|---|---|
| 인과적 electron transport | finite degradation delay, 잔여 전자 에너지, 필요시 공간 이동 | 시간별 source→deposition kernel, 살아 있는 reservoir, terminal limit 회복 |
| 임의 가스 조성·상태 | 독립 xHII/xHeII/xHeIII, YHe, temperature·density 의존성 | 원자료의 조성 확인 또는 새 provider, 정의역 및 보간 검증 |
| warm gas·REI 결합 | 기존 warm atomic provider와 CR source를 매 상태에서 함께 평가 | 고정 packet을 벗어나는 state-dependent API, positivity·number·energy 보존 |
| 전체 CR 손실 | Coulomb, direct excitation, charge exchange, He II target, 고에너지 hadronic 성분 | 전체 주입 spectrum의 남은 에너지와 secondary 산물 연결 |
| 비등방 수송 확장 | H(t),s(t), angular scattering, magnetic propagation | 현재 constant-background/FLRW 해 회복과 transport convergence |
| 핵·isotope 확장 | D/T/³He 및 핵반응·spallation의 별도 rate provider | atomic ionization과 핵 abundance 변화의 구분, baryon/charge ledger |

full IGM run으로 넘어가기 전에는 source 초기 history, external baryon/charge 또는 acceleration-reservoir 해석, thermal/radiation closure가 함께 정해져야 한다. 일정이나 예상 완료일을 새로 만들어 넣지 않는다. 현재 자료는 위 lane의 출발 입력과 비교 기준을 제공하며, 기존 원자물리의 정밀 확장 연구를 폐기하지 않는다.

## 9. 재현·게시와 파일 경계

실행 provider의 authoritative 연결은 `src/provider.py` → `evidence/SOURCE_MANIFEST.json` → `evidence/CR_PACKET.json`이다. raw table, source pin, correction, verification과 native receiver 결과를 함께 제공한다. 코드·표가 바뀌면 manifest와 packet을 다시 생성하고 receiver의 고정 입력과 검사도 함께 갱신해야 한다. 숫자를 그대로 둔 채 source identity만 바꾸는 것은 새 계산이 아니다.

CRIPTIC에서 포팅한 Rudd 및 그것을 결합한 Python 프로그램은 **GPLv3 component**로 분리하여 [license](src/GPL-3.0.txt)와 [notice](src/RUDD_NOTICE.md)를 포함한다. FS10 표는 MIT로 배포된 21cmFAST snapshot에서 가져왔으며 그 license를 함께 보존한다. 공식 archive 자체에는 별도 license 파일을 찾지 못했다는 획득 기록도 남긴다. REI의 Rust receiver는 기존 저장소의 MIT 경계에서 event packet을 받도록 작성했다. 서로 다른 출처의 파일을 일괄 재표시하지 않았다.

원격 게시·backup 완료 여부는 연구 결과와 분리하여 [publication/PUBLICATION.json](publication/PUBLICATION.json)에 기록한다. 이 보고서는 영수증에 없는 push, PR, backup을 완료로 주장하지 않는다. 현재 제공할 수 있는 과학적 결론은 **실제 SN proton source에서 H/He 사건과 열로 이어지는 조건부 계산 성분을 확보했다**는 것이다. 전체 재이온화 history의 closed prediction은 위의 남은 물리·상태 결합 검증 이후에 판정한다.
