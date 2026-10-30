# BASS_CR PHYS17 — 정식 물리 정의와 새로운 원전 기반 도출

**계약**: metric `(-,+,+,+)`; 비상대론적 국소 정지 중성수소 `T=100 K`, `n_HI=138.6 m^-3`이고 광자/기체 공통 진화 IVP가 아니다. 부모의 H/He RR 광자 6,400개, 네 proper-time birth bins 및 2,066개 measured+model common-support H(1s→2p) first-inelastic 원자 사건을 보존한다. 광자의 기원은 모두 He-RR, 광흡수는 H.  `PHYS16` (PR #141) source archive, HEAD `30020355677b66930856a385cf5cd4e9c3c3a24c`는 byte immutable.

## 원전과 식별자의 구분

- Kingston, Fon & Burke (1976), *J Phys B* **9** 605–618, DOI `10.1088/0022-3700/9/4/010`. PDF printed p.613 **Table 5**는 pure 1s→2p **unitarized Born** differential cross section `a0² sr^-1`, theta=0..180°, `k²=1,1.44,2.25` (원문 printed energies 13.6,19.6,30.6 eV). **Close-coupling Table 5가 아니다**. 같은 논문 printed p.612 Table 4는 `2s` UB DCS; printed p.616 Tables 6/7은 `2s`, `2p` CC 및 UB **total** cross sections (`pi a0²`). p.615 Fig.8의 2p CC 그래프는 정량 표로 둔갑시키지 않았다.
- Williams (1976), *J Phys B* **9**,1519–1527, DOI `10.1088/0022-3700/9/9/017`, printed p.1526 **Table 1**은 13.87,16.46,19.58 eV, θ=15..150°에서 measured `n=2=2s+2p` **unresolved** DCS 및 괄호 안의 마지막 자릿수 오차. Photon prompt/delayed로 total 2P와 2S는 구분했지만 본 각도별 Table 1은 2p-resolved가 아니다. 실험의 0..15° 및 150..180°는 직접 측정되지 않았다.

두 원본 PDF의 정확한 SHA-256: Kingston `d7767365440f840e5638eec38a46223bfbbf3a27a4c0296ecc1d35b6ec1b1c78`, Williams `09d3cb9c950f74624e7cd35d75d6d8a154d22102f19d75ee42493ff9d4c586ed`. PDF 원문은 공개 ZIP/Git에 재배포하지 않는다. 해당 표는 시각적 대조로 수치 전사한다.

## Differential source PDF 구성

각 E는 세 개의 출판 energy anchor `{13.6,19.6,30.6} eV` 내부에서만 사용한다(인용된 원전의 반올림된 eV 표기 그대로 사용). 2p UB 원표 `D_j(θ)=dσ_{2p}^{UB}(E_j,θ)/dΩ [a0²/sr]`에서 각 측정 θ별 `log D(E,θ)`를 에너지에 대해 조각별 선형보간하고, 동일 E에서 μ=cosθ에 대해 shape-preserving log-PCHIP 보간한다. 이는 논문에서 제시한 미분단면적 자체가 아니라 원본 표의 양수 보간 closure이다. 양수이고 표본 energy/angle 점을 재현한다.

실제 angular probability는

\[
 P_{2p}(\mu\mid E)=\frac{D(E,\arccos\mu)}{\int_{-1}^1D(E,\arccos\xi)\,d\xi},\qquad -1\leq\mu\leq1,
\]

로 정의한다. `2π`는 azimuth 평균 분자·분모에서 약분된다. 원본 **NIST BE-scaled total** 2p 충돌률과 Shah measured 이온화 경쟁률은 그대로 유지한다. Kingston UB의 별개 total 2p cross section을 이벤트율에 대입하지 않는다. Williams measured n=2 DCS 또한 2p 이벤트율에 삽입하지 않는다.

원래 운동학은 보존된다.

\[
 \frac{p_i^2}{2m_e}=E_{21}+\frac{p_f^2}{2m_e}+\frac{|\mathbf p_i-\mathbf p_f|^2}{2M_H},
 \qquad E_{21}=10.1988\,\mathrm{eV},\quad
 \mathbf q=\mathbf p_i-\mathbf p_f.
\]

Lyα E1 photon emission alignment는 Kingston Table5에서 **결정할 수 없다**. 앞선 PHYS16의 `p(w)=3(1-w²)/4` with w=cosχ relative to momentum transfer `q`와 대체 isotropic `1/2`를 **별도 명시 가정**으로 유지한다. `A21`, `f`, natural Voigt physics와 100 K Maxwellian도 이전 그대로:

\[
 p_{\mathrm{em}}(x\mid E)=\int_{-1}^{1}\!d\mu\,P_{2p}(\mu\mid E)
 \int_{-1}^{1}\!dw\, p_{E1}(w)\,\frac{\mathrm{Re}\,w_\mathrm{Faddeeva}(x-v_\mathrm{rec}(E,\mu)w/v_\mathrm{th}+\eta_\mathrm{em}+ia)}{\sqrt\pi}.
\]

이 값의 full-real-line normalization은 1이고 `|x|≤16` 격자 밖 Voigt 꼬리 질량은 별도 bounded; 오차 상계는 기존 PHYS16 numeric non-interval 제한을 상속한다. `N_{2p,i}`마다 다시 고정된 동일 proper-time source `r_{2p,i}(u)`를 사용해

\[
 N_1(T) =\sum_i\int dx\,p_{\mathrm{em},i}(x)
 \int_{s_i}^{T}du\,r_{2p,i}(u)\big[1-e^{-cn_{HI}\sigma_{Ly\alpha}(x)(T-u)}\big].
\]

여기서 첫 산란만 계수한다. 재분배/다중산란/탈출/열 피드백/전체 K/He exclusive/reionization IVP가 아니다.

## 독립 source consistency checks와 불확실성

표 4/5 각도 보간을 적분한 `σ/(π a0²)` 값은 같은 논문의 Table 6/7 **UB total**과 상대 0.0132 이내 (2p만 0.00532 이내). 이는 표 수치 전사의 source consistency이지 별도 실험과의 일치를 증명하지 않는다.

Williams 실제 n=2 측정값과 Kingston `2s(UB)+2p(UB)` 모델을 일치 에너지/각도에서 대조한다. 48개 각도 점의 signed `(model−measured)/quoted_error`는 **diagnostic**이지 알려지지 않은 각도 상관·계통 covariance를 포함한 χ²가 아니다. 19.58eV에서 UB pure-2p model > experimental total-n=2 central values가 6개 (of which 5 exceed quoted 1σ). 측정이 2p-resolved가 아니기 때문에 이것을 교정 인자로 source 2p 충돌률에 곱하지 않는다. 오히려 near-threshold model angular-shape uncertainty를 노출한다.

## 물리 판정

`literature-supported`: source DCS printed original table and measured inclusive n=2. `derived`: normalized DCS angular map, recoil-energy PDF form, source-clock convolution. `numerically checked`: 2,066 parent source events, 35 focused tests and byte-check replay (결과/로그 참조). `conjectural`: 2p sublevel alignment, interpolation between printed anchors and uniqueness of emitted photon PDF. `unresolved`: full 2p density matrix / CCC or 2p-resolved measured DCS at 14.6..21 eV, exact detailed-balance redistribution, shared evolving gas radiation clock geometry, physical K and global He exclusive kernel.

CENTRAL 28/88 (+0), EXTENSION 0/3 (+0), PHYS17 auxiliary source-intake/scoped science 1/1 conditional review HOLD, no global promotion; NATIVE25/L4/PRODUCTION HOLD, no merge/force-push; distinct-author R06/C09 NOT_RUN.
