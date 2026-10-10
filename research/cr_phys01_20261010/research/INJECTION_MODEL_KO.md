> 후속 선택 반영: 이 문서는 원자료/후보 단계의 기록이다. 최종 provider는 `DEPOSITION_PROVIDER_SELECTION_KO.md`와 `src/fs10.py`의 FS10 xi=.01, E≤9937.21 eV를 채택했다. MEDEA 3000 eV 제한은 채택 모델이 아니며, raw-data 무보정 감사와 최종 명시적 bounded numerical heat-closure projection을 구별한다.

# 실제 proton cosmic-ray 입력: 주입–수송–이온화–전자 cascade 연결

작성 2026-10-10. 대상은 non-tilted axisymmetric Bianchi I의 후기 IGM H/He이다. `CRP_L17_MD14_v1`을 실제 물리적 주입 시나리오로 선택한다. Leite et al. (2017)의 초신성 양성자 momentum power law를 전체 10 keV–1 PeV에서 정규화하고, Madau–Dickinson (2014)의 comoving SFRD에 일관된 Salpeter IMF 초신성 변환율을 적용한다. 실제 양성자 충돌이 만든 전자를 별도로 확보한 MEDEA 전자 cascade에 넣는다. 이는 X-ray photoelectron 또는 임의의 단색 전자 주입으로 CR 입력을 대체한 모형이 아니다.

**현재 승격 범위:** 입력 모델 선택, 출처가 고정된 H/He proton-impact ionization kernel 구현, 보존적 secondary source 유도, kernel의 제한된 수치 검증. 전체 cosmic-ray transport 또는 IGM 재이온화 예측의 검증 완료를 뜻하지 않는다. 모델별 하네스의 claim-state 구분을 따른다. 실제 실행 모델 식별은 `UNKNOWN`; GPT-6 Astra로 실제 실행되었다고 단정하지 않는다.

## 1. 선택한 source와 초기조건

### 1.1 정규화에 고정한 물리적 가정

| 항목 | 선택 | 성격 |
|---|---:|---|
| source | core-collapse SN proton cosmic rays | Leite 2017의 물리적 시나리오 |
| 양성자 kinetic support | 10 keV–1 PeV | 주입 전체 영역, 손실 provider 영역과 다름 |
| momentum index | α=2.2 | 출판된 매개변수 선택 |
| 기준 kinetic energy | K0=1 GeV | spectrum의 무차원 pivot |
| SN 에너지 | 10^51 erg = 10^44 J | 출판된 표준 시나리오 |
| proton acceleration efficiency | εp=0.1 | 시나리오, 관측으로 확정한 값 아님 |
| IGM escape fraction | fesc,p=1 | full-escape 기준 시나리오; 실측값 아님 |
| SFRD | MD14 Eq15 | 역사적 경험식, 최신 관측 best fit 주장 없음 |
| IMF와 SN 변환 | Salpeter, kCC=0.0068/Msun | MD14 Eq16, progenitor 8–40 Msun |
| 방향분포 | 순간 주입은 normal observer frame에서 등방적 | 유한 shear에서 이후 분포 등방성은 보장되지 않음 |

Leite의 대략 0.01/Msun은 Larson IMF에서 나온 값이다. MD14의 Salpeter SFRD에 그대로 곱하지 않는다. 에너지 효율과 탈출률은 각각 source model의 명시적 매개변수로 남긴다. SFR 관측 적합은 대략 z≲8까지의 자료를 사용하므로 더 높은 z 적용은 명시적인 외삽 시나리오이다. 이 모델은 source 선택을 구체화하지만 비등방 우주에서 은하 형성과 SFR 자체를 계산하지 않는다.

### 1.2 kinetic-energy source

질량에너지 M=mp c², kinetic energy K, β=√[K(K+2M)]/(K+M)를 사용한다. Leite Eq23–24에 따라

\[
g(K)=\beta(K)^{-1}
\left[\frac{K(K+2M)}{K_0(K_0+2M)}\right]^{-\alpha/2},\qquad
q_p(K,t)=C(t)g(K)\,\mathbf1_{[K_{\min},K_{\max}]}.
\]

MD14 Eq15의 comoving source는

\[
\psi(z_v)=0.015\frac{(1+z_v)^{2.7}}
 {1+[(1+z_v)/2.9]^{5.6}}
\ \mathrm{M_\odot\,yr^{-1}\,Mpc^{-3}},\quad z_v=a^{-1}-1.
\]

여기서 z_v는 평균 부피 scale factor로 정의한 source clock이며 방향별 관측 redshift와 같다고 두지 않는다. proper energy injection density는

\[
\dot{u}_{\mathrm{inj}}=a^{-3}\epsilon_p f_{\mathrm{esc},p}E_{\rm SN}
 \frac{k_{\rm CC}\psi(z_v)}{({\rm yr\ in\ s})({\rm Mpc\ in\ m})^3},\qquad
C=\frac{\dot{u}_{\mathrm{inj}}}{\int_{K_{\min}}^{K_{\max}}K g(K)\,dK}.
\]

이 식에서 K를 J로 적분하면 q의 단위는 m⁻³ s⁻¹ J⁻¹이다. eV grid에서는 분자 J를 eV로 변환하고 q를 m⁻³ s⁻¹ eV⁻¹로 유지한다. eV↔J Jacobian을 spectrum와 energy integral 양쪽에 중복 적용하지 않는다. 전체 10 keV–1 PeV에서 먼저 정규화한 후 active deposition band만 적분한다. band에 재정규화하면 실제 초신성 에너지 예산을 바꾸므로 금지한다.

초기 `Np(K,μ,t0)=0`은 특정 시작 시간부터 SN source를 켜는 통제된 실험이다. 그 이전 우주에서 CR이 없었다는 우주론적 주장이 아니다. 누적 history 예측을 하려면 source 시작점, z(t), 이전 CR 분포, gas ionization/temperature IC를 함께 지정해야 한다. 국소 frozen-background benchmark에서는 실제 선택한 t0 또는 z_v, 일정 H와 shear, interval, gas IC를 출력물에 반드시 포함한다. gas IC는 연결 대상 IGM branch의 원소 보존 및 전하 중성 IC를 사용하며 별도로 임의 생성하지 않는다.

## 2. massive-particle Bianchi 수송

`H_perp=H−s`, `H_parallel=H+2s`를 사용한다. normal observer의 정규직교 tetrad에서 μ=p_parallel/p이고 자유 massive particle은 \(\dot p_i=-H_i p_i\)를 만족한다. 따라서

\[
\dot p=-p[H+s(3\mu^2-1)],\quad
\dot\mu=-3s\mu(1-\mu^2),\quad
\dot K_{\rm geom}=-\frac{K(K+2M)}{K+M}[H+s(3\mu^2-1)].
\]

이는 nonrelativistic limit에서 \(\dot K=-2K H_{\rm ray}\), ultrarelativistic limit에서 \(-K H_{\rm ray}\)이다. 저에너지 proton에 photon의 \(-HK\)를 대입하지 않는다. 기하학적 에너지 교환은 열 생성이 아니다.

proper differential number \(\mathcal N_p(K,\mu,t)=dN/(dV_{\rm proper}dK d\Omega)\)에 대한 conservative 식은

\[
\partial_t\mathcal N_p+3H\mathcal N_p+
\partial_K[(\dot K_{\rm geom}-b_{p,\rm coll})\mathcal N_p]
+\partial_\mu(\dot\mu\mathcal N_p)
=q_p/(4\pi)+\mathcal C_{\rm scat}+\mathcal S_{\rm other}.
\]

comoving 분포 `a³ Np`를 쓰면 3H 항을 없애고 source에 a³을 곱한다. axisymmetric 적분은 \(d\Omega=2\pi d\mu\)이다. 분포를 이미 azimuth-integrated로 정의한 구현이라면 source는 q/2이며 다시 2π를 곱하지 않는다. 등방적 주입과 scalar gas target은 energy-dependent total rate를 각도 적분으로 계산할 수 있게 하지만, 입자 분포가 shear 하에서도 등방적이라고 결론내리지는 않는다. source/scattering closure와 local kernel을 분리한다.

에너지 모멘트의 별도 대조식은

\[
\dot u_{\rm CR}+3H(u_{\rm CR}+P_{\rm CR})
+\sigma_{ij}P^{ij}_{\rm CR}
=\dot u_{\rm inj}-\dot u_{\rm coll}+\hbox{boundary/source terms},
\]

\(u_{\rm CR}=\int K\mathcal N_p\,dK d\Omega\), \(P^{ij}=\int pv\hat p_i\hat p_j\mathcal N_p\,dK d\Omega\), \(P=P^i_i/3\). kinetic energy를 사용한 식이므로 입자 수가 바뀌는 경계/source의 rest mass 처리는 별도 number ledger와 일치해야 한다.

**전하·입자 수 계약:** 초신성에서 나오는 proton을 외부 source로 실제 가스에 추가하면 전하와 baryon source가 생긴다. 이를 thermal IGM proton의 가속으로 해석할 경우 같은 개수를 thermal H+ reservoir에서 빼고, 정지 또는 탈출 때 돌려줘야 한다. 은하에서 IGM으로 유입되는 새 baryon으로 해석할 경우 source reservoir와 동반 전자 또는 return-current closure가 필요하다. tracer approximation은 nCR/nB의 작음을 정량 보고한 경우에만 적용하고, 정확한 baryon/charge conservation 구현 완료라고 표시하지 않는다. 방향이 등방적이라 current가 0인 것은 net charge가 0이라는 뜻이 아니다.

## 3. 직접 채택한 proton→electron 물리 provider

primary methodological source는 Krumholz, Crocker & Sampson (2022), CRIPTIC §2.3.3, Eq23–25이다. 공개 author code commit `e169dc2e906cf51d5c6a1bba47c10bf3d61c3d92`의 `Src/Losses/Ionization.H`를 실제 읽고 계수와 구현을 고정했다. upstream license는 GPL v3이며 Python port `src/rudd.py`와 license notice를 별도로 제공했다.

표적 s∈{H I,He I}, binding energy Is, W는 ejected electron kinetic energy이다. \(w=W/I_s\), \(t=(m_e/m_p)K/I_s\), \(A_s=4\pi a_0^2N_s(R/I_s)^2\)라 놓으면

\[
\frac{d\sigma_{p,s}}{dW}=\frac{A_s}{I_s}
 \frac{F_{1,s}(t)+F_{2,s}(t)w}{(1+w)^3},\qquad
0\le W\le W_{\max}=4(m_e/m_p)K-I_s.
\]

이 endpoint는 선택한 upstream의 nonrelativistic prescription이다. 정확한 relativistic endpoint라고 부르지 않는다. differential kernel은 전자 방출 각도를 이미 적분한 값이므로 directional secondary electron spectrum은 제공하지 않는다.

H I의 source code 선택은 \(F_1=7/(3t),F_2=1/t\), Ns=1, Is=R이다. **H2의 경험 계수를 H 원자에 가져오지 않았다.** He I은 Ns=2, Is=24.59 eV이며

\[
F_1=\frac{A_1\ln(1+t)}{t+B_1/t}
+\frac{C_1t^{D_1/2}}{1+E_1t^{D_1/2+2}},\qquad
F_2=\left[\frac{1}{C_2t^{D_2/2}}
+\frac{1}{A_2/t+B_2/t^2}\right]^{-1}.
\]

He의 `(A1,B1,C1,D1,E1)=(1.02,2.4,0.70,1.15,0.70)`, `(A2,B2,C2,D2)=(0.84,6.0,0.70,0.50)`이다. 코드의 상수 R=13.605693122994 eV와 a0, me/mp를 명시적으로 고정했다. 이는 원래 GSL 빌드 버전의 마지막 자릿수를 byte-identical하게 복원한다는 뜻이 아니다. network의 binding-energy convention과 작은 수치 차이가 있으면 하나의 convention으로 energy ledger를 일치시키거나 차이를 별도 기록한다.

### 3.1 선택한 유효 실행 영역

adapter는 **1–10 MeV proton kinetic energy**만 허용한다. 실제 benchmark가 1–4 MeV처럼 더 좁은 부분구간을 쓰는 것은 허용된다. 이 범위 선택은 저속 charge exchange와 relativistic endpoint 외삽을 피하려는 연구 설계이며, 외부 논문이 해당 구간에서 특정 오차율을 보증했다는 주장이 아니다. H의 Williams-limit 근사 및 He fit의 모형 오차는 남는다. `active_proton_mask` 밖의 전체 주입 입자는 transported/unresolved CR reservoir에 남긴다. kernel 호출 자체는 밖의 K를 거부하여 무음 외삽을 차단한다.

포함된 물리 채널은 neutral-target proton-impact **single ionization**이다. 다음은 전체 CR 예측에 필요한 후속 확장이지 이 포팅의 완료 항목이 아니다: direct proton excitation, free-electron Coulomb stopping, charge exchange/neutral CR transport, He+ ionization, hadronic collisions/π channels, magnetic confinement 및 self-generated turbulence. 따라서 이 결과는 `selected_ionization_channel_scenario`로 해석한다. 누락 채널의 에너지를 이미 계산된 것으로 가장하여 heat로 처리하지 않는다. 낮은/높은 proton sector와 미지원 secondary sector를 보존적으로 남기는 것은 energy accounting을 해결하지만, 누락된 실제 물리 작용의 정확도까지 해결하지는 않는다.

### 3.2 공개 원문/코드의 total-cross-section 불일치 수정

Eq24의 kernel을 직접 적분하면, \(r=w/(1+w)\)에 대해

\[
\Sigma_s(w)=A_s\left[F_1(r-r^2/2)+F_2 r^2/2\right],
\quad
L_s(w)=A_s I_s\left[F_2\ln(1+w)+(F_1-F_2)r\right].
\]

Σ는 ionization number cross section, L은 binding+electron kinetic stopping moment이다. CRIPTIC Eq26 및 C++ total cross-section에는 F2 항의 numerator가 w로 기재되어 있지만, differential 식의 적분은 **w²**를 요구한다. stopping Eq25는 위 L과 일치한다. 포팅은 SDCS와 stopping을 함께 만족하도록 total cross section을 w²로 수정했다. 이 조정은 관측 재보정이나 임의 normalization이 아니라 differential 식 자체에 대한 algebraic consistency correction이다. upstream 식도 evidence-only 함수로 남겼다.

`research/RUDD_KERNEL_CHECK.json`: log(1+W/I) 변수의 128-point Gauss–Legendre 적분으로 H/He × 1,2,5,10 MeV를 확인했다. analytic moment와 numerical SDCS의 최대 상대 오차는 3.1×10⁻¹⁴, secondary-energy 분할의 합 일치는 2.2×10⁻¹⁶이다. upstream total/SDCS-integrated total 비는 이 표본에서 H 약0.700–0.704, He 약0.757–0.865로 차이가 작지 않다. 이는 kernel consistency check이며 full transport scientific runtime은 아니다.

## 4. 중복 없는 proton→secondary→gas 연결

gas target density는 proper ns이다. 정상원자 가스가 CR보다 훨씬 차갑다는 local stationary-target approximation에서

\[
R_{s,\rm prim}=n_s\int dK\,d\Omega\;\mathcal N_p(K,\Omega)v_p(K)\sigma_s(K),
\]
\[
Q_e(W)=\sum_s n_s\int dK\,d\Omega\;\mathcal N_p v_p
\frac{d\sigma_{p,s}}{dW},\quad
b_{p,\rm ion}(K)=\sum_s n_s v_p\int_0^{W_{\max,s}}(I_s+W)\frac{d\sigma_{p,s}}{dW}\,dW.
\]

q_e(W) 단위는 m⁻³ s⁻¹ eV⁻¹이다. target density를 CR source 정규화에도 넣지 않는다. 일차 H I→H II 또는 He I→He II event 수는 Rprim이며, 각 event의 Is는 binding-energy ledger로 간다. cascade에는 **W만** 넣는다. 동일 event의 Is를 전자 입력에도 더하면 primary ionization을 두 번 센다.

공통 gas state에서 검증한 전자 table response `fj(W,gas)`를 쓰면 각 secondary deposition은

\[
\dot u_j=\int_{\mathcal D_e} dW\;W Q_e(W) f_j(W,\mathrm{gas}).
\]

각 table channel의 정의가 에너지 fraction인지 rate/yield인지 먼저 확인한다. ionization-energy fraction을 ionization count로 바꾸려면 같은 table binding threshold로 나눈다. cascade excitation/continuum photon은 열로 재명명하지 않는다. MEDEA data의 실제 energy/ionization/abundance support는 다른 담당자가 확보한 audit manifest를 authoritative하게 사용한다.

현재 연결 대상으로 확인한 표의 energy range는 약10.2–3000 eV이다. kernel 전체 secondary support와 일치하지 않으므로 **모든 W를 보존적으로 분할**한다:

1. primary binding: \(\sum_s I_s R_{s,\rm prim}\);
2. supported secondary kinetic energy: 실제 MEDEA domain에만 deposition을 요청;
3. low-W secondary reservoir: W<10.2 eV. thermalization timescale/closure를 별도 채택한 경우만 heat로 이동;
4. high-W secondary reservoir: W>3000 eV. 추가 electron transport/provider가 생길 때 연결;
5. proton support 밖의 energy: 전체 CR transport/reservoir에 유지.

중간 cell을 한 점으로 대표시켜 table을 조회하더라도 analytic interval moment를 이용해 에너지의 정확한 가중치를 유지할 수 있다. 에너지 가중 평균 fraction의 grid convergence는 별도 runtime 확인 항목이다. kernel이 scalar SDCS만 주므로 빠른 local isotropization/deposition을 채택할 때에는 그 시간척도와 transport length가 background 변화 및 resolution보다 작다는 조건을 명시한다. 그렇지 않으면 ejected electron의 방향을 임의로 재구성하지 않고 angle-integrated reservoir로 남긴다.

동일 cell, 동일 time step의 필수 ledger는

\[
\Delta E_{p,\rm ion-loss}=
\Delta E_{\rm primary-binding}+
\Delta E_{e,<}+\Delta E_{e,\rm supported}+\Delta E_{e,>}.
\]

supported energy는 다시 table가 허용하는 heat/ionization/excitation/continuum/기타 명시적 channel의 합과 비교한다. cosmological geometry work, reservoir influx/outflux, 주입 에너지, particle-grid boundary의 잔여 에너지는 별도 항이다. 이 구분으로 domain 밖 에너지를 버리지 않고도 실제 양성자가 만든 ionization과 electron cascade를 연결할 수 있다.

## 5. 출판된 단순 closure를 그대로 채택하지 않은 이유

Leite Eq32–35는 W_H≈36.3 eV와 ξ(xe)=5/3−2xe/3를 이용해 primary/secondary H ionization과 heat를 표현한다. 그러나 이 논문은 excitation을 누락하여 heat가 과대평가될 수 있음을 명시한다. He neutral stopping을 합산한다고 species-resolved He ionization/excitation cascade가 자동으로 완성되지 않는다. 따라서 그 식은 source와 비교용 baseline에는 사용하지만 이번 full H/He channel provider로 채택하지 않는다.

Jasche et al. (2007)의 W-value 접근도 분자수소 측정값을 원자수소에 근사 적용하고 excitation을 무시한다. H용 ξ를 He에 기계적으로 복사하면 `40.3−(5/3)×24.6≈−0.7 eV`의 비물리적 heat까지 생긴다. 코드 분기가 없다는 이유로 그 식을 He에 그대로 확장하지 않는다. 원자/분자와 species별 secondary prescription을 구별하는 것이 이번 blocker 해소의 핵심이다.

## 6. handoff 및 claim 상태

| 산출물/주장 | 상태 |
|---|---|
| Leite source spectrum + MD14 Salpeter normalization 선택 | `SOURCE_VERIFIED / MODEL_SELECTED` |
| massive Bianchi Liouville, proton→electron source, ledger | `DERIVED` |
| CRIPTIC H/He atomic parameters와 GPL source pin | `CODE_READ / SOURCE_PINNED` |
| bounded differential provider와 analytic moments | `IMPLEMENTED / BOUNDED_CHECK_PASS` |
| upstream Eq26 missing-square discrepancy | `INDEPENDENT_INTEGRAL_CHECK_PASS`; root CAS 확인은 별도 evidence |
| IGM evolution, gas feedback, full energy/mass/charge closure | `PENDING_RUNTIME_INTEGRATION` |
| 전 영역 10 keV–1 PeV stopping/deposition | `NOT_CLAIMED`; 주입 에너지 전체는 반드시 보존 |
| 임의 isotope/nuclear reaction cascade | `NOT_IMPLEMENTED`; H/He atomic ionization 대상 |

바로 연결할 파일은 `src/rudd.py`, `src/GPL-3.0.txt`, `src/RUDD_NOTICE.md`, `research/RUDD_KERNEL_CHECK.json`, `research/INJECTION_SOURCES.json`이다. runtime은 첫째 whole-source 정규화, 둘째 active/inactive proton 분리, 셋째 proper/comoving/angular Jacobian, 넷째 primary/electron energy ledger, 다섯째 matched table domain을 검증한 뒤 scientific plot으로 승격한다. injection·kernel·cascade를 각각 검증하고 합성 단계에서 과도한 에너지 생성/소멸이 없는지 확인한다.

Primary references: [Leite et al. 2017](https://arxiv.org/abs/1703.09337), [Madau & Dickinson 2014](https://arxiv.org/abs/1403.0007), [CRIPTIC 2022](https://arxiv.org/abs/2207.13838), [source commit](https://bitbucket.org/krumholz/criptic/src/e169dc2e906cf51d5c6a1bba47c10bf3d61c3d92/Src/Losses/Ionization.H), [Rudd et al. 1992 DOI](https://doi.org/10.1103/RevModPhys.64.441), [Jasche et al. 2007](https://arxiv.org/abs/0705.4541). Rudd original author PDF retrieval failure and precise read scopes are preserved in the source JSON; original Eq43–44/Table V 전체를 직접 읽었다고 주장하지 않는다.
