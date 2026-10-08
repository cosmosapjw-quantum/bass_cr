# R3M26 모델의 수학적 정의와 production 완료 경로

2026-09-24. 조사 기준: R3M25 `90d6cbad25e4bc49e9563f8721fdc408761b31c7`의 `docs/CLAIM_POLICY.md`, `docs/LITERATURE_AND_METHOD_LOCK.md`, `docs/r3m25/REPORT_KO.md`, `cr_repro/{tdl,r3m11,hydrogen,grid,observables,constants}.py`, B2 config. 원전의 관련 절/식과 공식 상수표를 확인했다. 이 문서는 이론·코드 조사와 직접 유도를 제시한다. Numerical source 변경·collision 실행 결과를 제시하지 않는다.

## 결론

현재 구현은 **비상대론적 단일 전자, 무한질량 수소 원자, 지정된 고전 직선 핵 궤적**이라는 내부적으로 정의 가능한 atomic model의 독립 구현이다. 핵 궤적을 지정하는 것은 모델 선택이며, 그 뒤 atomic-unit 변환·전자 Schrödinger equation·Galilean ETF·정사영·impact-parameter 적분은 연결해서 유도할 수 있다. 특정 논문의 raw data 또는 private code를 정확히 재현할 필요는 없다.

사용자가 재정의한 model-based production은 (1) 모델의 모든 가정과 출력이 명시되고, (2) 구현이 그 정의를 충실히 계산하며, (3) 사용 범위의 수치오차가 선언한 기준으로 충분히 작다는 뜻으로 운영할 수 있다. 이를 위해 외부 데이터 exact match나 AOCC 전체 lane을 무조건 요구할 이유는 없다. 다만 현재 h/시간/초기·최종 시간/CAP/상자/high-n/b-integral 미해결 항목은 **수치적 faithful implementation에 직접 필요한 항목**이다. 새로운 production 정의가 이 오차들을 물리 모델 가정으로 바꾸거나 없애지는 않는다.

원래의 50/100/225 keV/u all-bound capture 및 cross-section 최종 목표를 유지한다. n≤3는 빠르게 닫을 수 있는 중간 수치 milestone이며 최종 목표의 대체물이 아니다. 마지막 산출물은 model-based total observable와 수치 정확도 주장, 현실 검증 상태를 구분하여 한 번에 종합한다.

## 1. 차원 있는 출발점과 정확히 선택하는 근사

`κ=e²/(4πε₀)`로 놓으면 전자와 두 proton의 비상대론적 Coulomb Hamiltonian은

`H3 = p²/(2me) + PT²/(2mp) + PP²/(2mp) −κ/|r−RT| −κ/|r−RP| +κ/|RP−RT|`.

이는 시작 모형이며 spin-dependent, relativistic, radiation, nuclear finite-size correction은 포함하지 않는다. 이어 `RT(t)=0`, `RP(t)=b ex+vt ez`, `b·v=0`를 **처방**하고 전자 파동함수만 전파한다. 이 단계는 3-body quantum dynamics의 정확한 항등변환이 아니다. recoil/backreaction, nuclear deflection, nuclear quantum interference를 무시하는 semiclassical model choice다. 전자 mass를 reduced mass로 바꾸지 않으므로 현재 수소 에너지는 infinite-nuclear-mass 값이다.

처방된 궤적의 전자 Hamiltonian은

`He(t)=−ħ²∇²/(2me)−κ/r−κ/|r−RP(t)|`.

핵–핵 항 `C(t)=κ/R(t)`는 전자좌표 독립이다. 유한한 시간구간과 b>0에서 `ψplus(t)=exp[−(i/ħ)∫C(s)ds]ψe(t)`이면 `iħ∂tψplus=[He+C]ψplus`. 따라서 같은 b의 모든 전자 정사영 확률은 같다. 코드가 +κ/R를 생략한 것은 현 observable에 대한 gauge choice이며 missing electronic force가 아니다. 이 명제는 핵 궤적의 물리적 정확성 또는 서로 다른 b의 진폭을 coherently 간섭시키는 differential scattering 계산에 대한 증명이 아니다. b=0에서 C가 특이하므로 그 보조 gauge를 억지로 적분할 필요 없이 He 자체를 사용한다.

관련 원전 [P1] §II.A Eqs. (1)–(5)는 같은 semiclassical 구조와 +1/R를 사용한다. [P2] §2.1은 straight-line approximation의 물리적 조건을 설명한다. 두 원전은 model choice를 지지하며 현재 수치의 정확도를 보증하지 않는다.

**상태:** Hamiltonian과 gauge 관계 `derived`; prescribed trajectory와 생략된 corrections `modelling choice, literature-supported`; 실제 p+H의 오차 크기 `not established here`.

## 2. Atomic units: 변수와 코드의 대응

`a0=ħ²/(me κ)`, `Eh=me κ²/ħ²=κ/a0`, `ta=ħ/Eh`, `va=a0/ta=κ/ħ=αc`.

`r=a0 r̃`, `t=ta t̃`, `Ψ=a0^(−3/2) ψ̃`를 대입하면 norm이 보존되고

`i ∂t̃ ψ̃ = [−(1/2)∇̃² −1/r̃ −1/|r̃−R̃P(t̃)|]ψ̃`.

`tdl.py:23,42`의 potential, `tdl.py:20,27`의 k²/2, `hydrogen.py`의 orbital, `grid.py`의 dv=h³가 이 convention에 대응한다. Energy가 시간 의존하므로 collision 중 전자 에너지 보존을 invariant로 요구하면 틀린다. CAP가 없을 때의 norm 보존과 `d<He>/dt=<∂tHe/∂t>`가 맞는 관계다.

입력 `E_u=energy_keV_per_u`는 특정 projectile의 총 에너지가 아니라 **질량 1 u당 kinetic energy**다. `v_au=sqrt[2(1000 E_u/Eh[eV])/(u/me)]`는 `observables.py:5`와 일치한다. 실제 proton의 total kinetic energy는 `(mp/u) E_u`다. NIST 2022 CODATA [P3]의 mp/u=1.0072764665789에 따르면 100 keV/u는 약 100.7276467 keV의 proton energy다. 논문의 ‘100 keV proton’와 비교할 때 이 convention을 정합화한다. 현재 constants를 조용히 바꾸거나 이 차이를 수렴 실패의 원인으로 추정하지 않는다.

단면적 code unit은 a0²이고 cm²로 변환할 때 `A0_CM²`를 곱한다. Rate coefficient를 최종 산출물에 포함한다면 추가로 relative-speed distribution f(v)의 normalization/units를 정의한 뒤 `<σv>=∫σ(v)v f(v)d³v`를 계산해야 한다. σ와 rate를 혼용하지 않는다.

**상태:** 단위변환 `derived, code-inspected`; 원자상수 [P3] `official-source verified`; production execution의 unit test 결과는 이 문서에서 새로 만들지 않았다.

## 3. Target 초기상태와 incoming Coulomb phase

무한질량 isolated target에서 `φ1s(r)=exp(−r/a0)/sqrt(πa0³)`, `E1=−Eh/2`. `∇²exp(−r/a0)=[1/a0²−2/(a0 r)]exp(−r/a0)`를 대입하면 exact eigenstate임을 확인할 수 있다. Dimensionless `one_s`는 이 식이다.

현재 `relaxed_initial`은 sampled analytic φ를 시작점으로 **discrete target Hamiltonian**에 imaginary-time split propagation/normalization을 적용한다. 이는 discrete stationary preparation이며 finite imaginary step, finite relaxation time, h, box의 근사다. `stationary_residual_Eh`가 작아도 곧바로 continuum initial-state error bound는 아니다. Isolated atom analytic identity, fixed-grid residual/convergence, h에 따른 접근을 각각 검사하면 된다. Finite-start 문제를 두 중심 instantaneous ground state로 바꾸는 것도 무조건 개선은 아니다. 원하는 incoming channel은 isolated target 1s이기 때문이다.

먼 projectile의 potential을 target 근처에서 전개하면

`−κ/|R−r|=−κ/R−κ(r·R)/R³+O(κr²/R³)`.

첫 항의 time integral은 asymptotically log phase를 만들지만 spatially constant이므로 initial ket 전체에 붙은 phase는 모든 확률에서 상쇄된다. +κ/R nuclear scalar gauge를 사용하면 이 monopole을 제거할 수 있다. 나머지는 target 근방에서 R⁻² 이상으로 감소하는 tidal interaction이며 실제 polarization/transition을 만들 수 있다. 코드가 finite ti에서 phase 없는 φ1s를 넣는 것에서 **전역 incoming phase의 누락은 probability bug가 아니지만, ti 이전의 tidal dynamics 누락은 finite-start approximation**이다. 이 expansion은 r≪R에서의 식이며 전공간 rigorous norm bound가 아니다.

따라서 필요한 검증은 z_start를 더 멀리 옮긴 common-physical-horizon probability 비교다. Phase를 맞추는 작업으로 이를 대신하지 않는다. 추가 global Coulomb phase 때문에 raw wavefunction이 일치하지 않더라도 projector probability/ray distance가 일치할 수 있음을 비교 정의에 반영한다.

**상태:** 1s, scalar-phase invariance `derived`; far-field expansion `derived, local asymptotic`; 실제 ti 오차 `unresolved until checked`.

## 4. Moving projectile ETF: 부호와 projection의 유도

Projectile rest-frame orbital이 `H_H φ_nlm=E_n φ_nlm`, `E_n=−Eh/(2n²)`를 만족한다. 현재 target-rest convention에서

`χ_nlm(r,t)=exp{i[me v·r−me v²t/2]/ħ} exp(−iE_n t/ħ) φ_nlm(r−b−vt)`.

직접 미분하면 iħ∂t의 `−iħ v·∇φ`와 kinetic term의 같은 cross term이 일치하여 χ는 **움직이는 단일 Coulomb center**의 TDSE를 정확히 만족한다. 이 식은 full two-center collision의 정확한 eigenstate라는 뜻이 아니라 asymptotic outgoing channel의 정의다. Atomic units에서는 코드 `_state_slab`의 `exp(ivz−iv²t/2) exp(+it/(2n²))`가 된다. [P2] Eq. (11)이 같은 Galilean transformation을 제시한다. 문헌의 좌표/boost convention을 확인하지 않고 phase 부호를 복사하면 안 된다.

Spatial ETF exp(ivz)는 electron momentum을 mv만큼 옮기므로 생략할 수 없다. 반면 각 channel에 붙은 pure-time phase는 개별 probability와 전체 span projector를 바꾸지 않는다. 이 invariance는 아래 Gram form에서도 정확히 성립한다. Finite FFT lattice는 Galilean covariance를 정확히 보존하지 않으므로 isolated moving atom test는 ETF algebra와 grid dispersion/Coulomb sampling의 영향을 구분하는 좋은 독립 판별 문제다.

## 5. Finite-grid observable가 정확히 의미하는 것

Discrete weighted inner product는 `<x,y>h=h³Σx* y`. Sampled channel columns를 Φ, `G=Φ†h Φ`, `c=Φ†h ψ`라 하면 full-rank finite span의 orthogonal projector는

`Πh,N=Φ G^(−1) Φ†h`, `Qh,N=c†G^(−1)c`.

`Π²=Π`, `Π†h=Π`, `0≤Q≤||ψ||h²`는 직접 유도된다. Φ→ΦD, D invertible인 basis change에서 Π가 불변이므로 diagonal channel phases 역시 결과를 바꾸지 않는다. `r3m11.py:61,83,91`이 해당 algebra를 구현한다. Gram rank/conditioning 검사는 이 representation이 수치적으로 의미 있는지를 확인한다.

R3M18의 P1/P2/P3는 authoritative nested finite spans **n≤1 / n≤2 / n≤3**다. Shell 증가분은 QN−Q(N−1)≥0. Nonorthogonal finite-grid channel별 raw overlap magnitude를 합하는 legacy `tdl.py:58`과 Gram projector를 혼용하면 안 된다. Finite-grid에서 개별 nlm population을 정의하려면 orthogonalization/채널 convention까지 명시해야 하며 arbitrary 분배를 유일한 physical state probability라 부를 수 없다.

여기서 `Bv(t)f(r)=exp{i[me v·r−me v²t/2]/ħ}f(r−b−vt)`는 boost와 translation의 unitary operator다. Continuum asymptotic projector `ΠP,bound(t)=Bv(t) 1_{(−∞,0)}(H_H) Bv(t)†`는 모든 hydrogen bound states를 포함한다. Finite sampled Πh,N은 이것과 같지 않다. 따라서 norm−QN에는 target bound, omitted projectile high-n, continuum 및 finite-time channel overlap 효과가 함께 들어갈 수 있다. 이를 ionization 또는 continuum probability로 명명하지 않는다.

**상태:** finite-span algebra `derived, code-inspected`; continuum/all-bound approximation의 정확도 `numerical validation required`.

## 6. CAP는 물리적 openness 자체가 아니다

무한 공간의 전자 TDSE는 closed unitary dynamics이며 ionization은 continuum에 대한 단위적 population 이동이다. CAP는 finite periodic FFT box에서 outgoing amplitude의 wraparound/reflection을 줄이기 위한 **numerical boundary treatment**다. `Heff=Hh−iWh`, `Wh=−log(Mref)/dt_ref≥0`이면

`d||ψ||h²/dt=−2<ψ,Whψ>h`.

ControlledTDLRunner는 dt-dependent mask를 `Mref^(dt/dt_ref)`로 바꿔 같은 W를 유지하고 양쪽 half step으로 결합한다. 이것은 base historical runner의 fixed per-step post-mask와 다르다. 따라서 canonical controlled path를 정확히 지목해야 한다.

Lost norm을 물리적 ionization으로 동일시하거나, surviving state를 renormalize한 conditional capture를 incident-electron probability와 혼용하지 않는다. Bound-channel tail도 absorber에 닿을 수 있다. [P4] Eq. (6), §4는 CAP의 목적이 unabsorbed inner region의 정확도임을 명시하고 finite-grid reflection 한계를 설명한다. Box/CAP/finite-time biases를 ‘선택한 물리 모델’로 재분류하여 수렴 조건을 건너뛸 수 없다.

## 7. All-bound와 b-integral의 유한 종료 조건

최종 목표는 `Pcap(E,b)=lim_{tf→∞,ti→−∞}<ψ(tf),ΠP,bound(tf)ψ(tf)>` 및

`σcap(E)=2π∫₀∞b Pcap(E,b)db`.

이는 isotropic 1s target와 straight-line impact-parameter ensemble에 대한 model definition이다. [P1] §II.C Eq. (10), [P2] Eq. (5)가 이 구조를 사용한다. `capture_cross_section_a0sq`는 주어진 유한 b-grid의 trapezoid 적분만 계산하므로 small-b/large-b tail 또는 quadrature accuracy를 자동 제공하지 않는다.

All-bound를 닫는 방법은 둘 중 하나를 실제로 선택하여 완성하면 된다. 둘 다 전부 수행하거나 문헌 method 전부 구현할 필요는 없다.

1. **Explicit channels와 tail accounting:** h/box에 안정된 QN과 여러 shell increments를 확보한 뒤 omitted-tail treatment의 가정·수치 안정성·허용오차를 명시한다. 단지 마지막 shell이 작다거나 n⁻³ fit 하나가 맞는 것은 upper bound가 아니다. Empirical tail estimate를 쓰면 numerical evidence와 model assumption을 구분하여 기록하고, formal bound라 하지 않는다.
2. **Threshold-band spectral route (이론 후보, 미구현):** 같은 exact boosted hydrogen operator에 대해 `Qdeep=<1_{(−∞,−ε]}>`, `Mε=<1_{(−ε,+ε]}>`를 정의하면 `Qdeep≤Qall≤Qdeep+Mε`. 이는 spectral-set inclusion에 따른 직접 유도다. Finite box에서는 near-threshold spectral accuracy, box growth, ε reduction과 final-time stability가 추가로 필요하다. 이 불등식만으로 현재 array의 all-bound error가 인증되지는 않는다.

작은 impact parameter의 미계산 면적은 probability≤1로 `0≤σ[0,bmin]≤π bmin²`라는 보수적 bound를 얻을 수 있다. 큰 b에서는 P≤1만으로 tail bound를 얻을 수 없다. 따라서 bmax extension와 tail decay의 근거가 필요하다. All-bound completeness와 b tails를 처리한 뒤 선택한 E 범위에서 interpolation까지 검증하면 목표 범위의 total cross section을 model product로 종합할 수 있다.

## 8. 어떤 정확도를 무엇으로 주장할 것인가

| 주장 층 | 필요한 근거 | 불필요한 전제 |
|---|---|---|
| 모델 정의·수식의 일관성 | convention, modelling choices, 정확한 derivation, limiting cases | 특정 논문 raw data |
| 구현의 정확성 | analytic one-center/ETF, unit/invariance tests, 독립 full-H 또는 다른 algebraic 구현, observable algebra | 반드시 AOCC full collision 전체 lane |
| 범위 한정 numerical production | full-horizon dt/h/preparation/domain/CAP/time/high-n/b convergence와 목표 observable error budget | 모든 오차의 엄밀한 전역 proof certificate |
| Formal global error certificate | 엄밀 residual·stability·roundoff/representation bound | 경험적 p 또는 local window PASS로 대체 |
| 실제 실험 예측의 검증 | 조건이 맞는 외부 measurement/독립 theory, uncertainty/model discrepancy | 특정 외부 central에 exact equality |

R3M26은 사전 등록된 보수적 empirical error estimate를 미관측 refinement data로 점검하고 교차 효과를 확인하는 수치 검증 경로를 허용한다. 이는 formal certificate와 별개이며 certified bound라고 보고하지 않는다. 기존 real-time 0.10%, spatial 0.30%, total 1% 목표는 바꾸지 않는다.

외부 자료는 모델의 반증·현실 검증에 가치가 크며 알려진 모순을 무시할 수는 없다. 그러나 자료 확보나 private raw 복제 자체를 내부적으로 정의한 model-based numerical release의 무조건 gate로 삼지 않는다. 외부 검증을 하지 않았다면 `real_world_validation=NOT_EVALUATED`라고 정확히 표기한다.

현재 R3M25 결과는 full production grid의 실제 t=0 **4-step local window**에서 독립 CF4/reference action과 refinement를 검증했다. 이 증거는 구현 신뢰를 높이지만 global time error를 닫지 않는다. 같은 원리로 target atom residual, tests 통과, hash binding도 서로 다른 증거층을 대신하지 않는다.

참고로 finite-grid dissipative A에 대한 residual `r=y'−Ay`를 전체 구간에서 통제하면 Duhamel로 `||y(T)−ψ(T)||≤||y(ti)−ψ(ti)||+∫||r||dt`를 얻는다. Fixed orthogonal Π에 대해 `|Q(y)−Q(ψ)|≤(||y||+||ψ||)||y−ψ||`. 이는 formal certificate의 한 경로를 보여 주는 직접 유도다. 현재 local checkpoint 비교들이 이 적분을 계산한 것은 아니며, model production에 이 보수적인 formal bound만을 유일한 admission 경로로 강제할 필요도 없다.

## 9. 끝나는 연구 경로

1. **모델 계약 한 번 확정:** 위 Hamiltonian·frame·energy convention·incoming/outgoing definition·finite-channel 중간 milestone·all-bound/cross-section 최종 목표·정확도 기준을 한 문서로 연결한다. 새로운 외부 논문 추가를 계속 gate로 만들지 않는다.
2. **기존 시간수렴 경로 마무리:** 예정 B3를 같은 physical/numerical family에서 완료하고 B0–B3 global observables와 독립 reference evidence를 평가한다. R3M26 이후의 사전 등록 정책에서 `1.5≤p≤2.5`는 진단이며 universal hard veto가 아니다. 등록한 mixed-order model의 미관측 refinement 예측, 보수적인 empirical error estimate와 cross-effect 검증이 해당 기준을 충족하는지 판단한다. 기존 R3M18 등의 판정과 증거는 변경하지 않는다. p 하나를 physical failure 또는 전체 certification으로 해석하지 않는다. 결과가 허용 기준을 충족하면 같은 local audit를 반복하지 않는다.
3. **지배 오차만 해결:** 현재 h gap와 h–dt interaction이 크므로 시간검증 후 spatial refinement/representation 선택을 하나의 판별 실험으로 결정한다. h와 dt의 additive independence를 가정하지 않는다. 한 방법을 선택한 뒤 요구 accuracy를 만족하는 구현을 완성하고 동급 solver들을 모두 구현하지 않는다.
4. **경계·채널·적분 완성:** preparation, ti/tf, CAP/box, high-n, b quadrature/tails를 declared observable budget으로 묶어 검증한다. 고정된 완료기준을 만족하면 더 넓은 hypothesis sweep를 종료한다. 미해결인 항목은 원인/수치/허용오차를 특정하여 해결하며 외부 exact reproduction을 새 blocker로 추가하지 않는다.
5. **한 번의 독립 최종 판단과 종합:** model/derivation, implementation, numerical validation, total observable, limitations를 묶고 독립 decision reviewer가 정확히 이 자료와 criteria로 판정한다. 동일 증거에 대한 review-of-review loop를 만들지 않는다. R3M25의 국소 independent-method 증거는 재사용하며, 새로운 실패나 별도 필요가 없는 한 local oracle을 계속 추가하지 않는다. 최종 산출물은 model-based production의 해당 범위와 real-world validation 상태를 분리한다. Resource ceiling 때문에 충족하지 못하면 남은 정확도 한계를 수치로 밝힌 연구 종료 보고서를 만든다; 근거 없는 PASS로 바꾸지는 않는다.

이 경로는 실험 성공을 사전에 보증하지 않는다. 대신 생산 admission을 막는 항목을 유한한 scientific deliverables로 고정하며 끝없는 문헌 추가·보조 solver·반복 audit를 필수 목표로 만들지 않는다.

## 실제 코드에서 정리해야 할 concrete theory interface

- Canonical production entry는 historical TDLRunner가 아니라 fixed-rate symmetric CAP path라는 점을 contract와 output에서 명시.
- Authoritative output은 `gram_audit.P_span_by_nmax`와 `P_span_nmax`; legacy raw overlap sum과 cumulative/shell 의미를 혼용하지 않음.
- Energy label은 keV/u, paper total keV conversion 별도; c/ħ는 차원 있는 유도에서 유지한 뒤 au로 축약.
- ti/tf와 sampled-vs-discrete orbital 준비의 approximation을 명시; arbitrary global phase를 physical error로 세지 않음.
- Finite-N complement/absorbed norm을 continuum·all-bound·ionization으로 잘못 승격하지 않음.
- `production_admitted=False` 같은 역사적 runner 기본값과 향후 evidence-based release policy를 구분. 단순 flag 변경으로 admission을 만들지 않되, ‘언제나 False’ 자체를 새 production 정의의 영구 정책으로 해석하지 않음.

## 원전·locator·지지 관계

| ID / 원전 | 확인한 locator | 지지와 한계 | Primary URL |
|---|---|---|---|
| P1 — Avazbaev et al., PRA 93, 022710 (2016) | §II.A Eqs. (1)–(5); §II.C Eqs. (9)–(12); §III.A finite-Z setup | `supports/contextual`: semiclassical H+1/R, incoming conditions, σ. 해당 basis 정확도를 이식하지 않음 | https://link.aps.org/accepted/10.1103/PhysRevA.93.022710 |
| P2 — Tseliakhovich, Hirata, Heng (2012), arXiv:1201.4778v2 | §2.1 Eqs. (3)–(5); §2.2 Eq. (11); Table 1; §3 tests | `supports/limits`: straight-line model, ETF, impact-parameter formula. capped-core/hybrid grid 및 5–80 keV 결과는 현재 ground truth 아님 | https://arxiv.org/pdf/1201.4778v2 |
| P3 — NIST 2022 CODATA | Atomic unit of length/energy/time/velocity; proton mass in u; electron mass in u | `supports`: unit/energy conventions. Code constants는 검사했으며 변경하지 않음 | https://physics.nist.gov/cuu/Constants/Table/allascii.txt |
| P4 — Shemer, Brisker, Moiseyev, PRA 71, 032716 (2005) | Eq. (6); §4 Eqs. (20)–(21) | `supports/limits`: inner-region accuracy objective, finite-grid reflections. SES-CAP가 현재 mask를 인증하지 않음 | https://arxiv.org/pdf/quant-ph/0508084 ; DOI 10.1103/PhysRevA.71.032716 |
| P5 — Kołakowska et al., PRA 58, 2872 (1998) | Publisher abstract only | `contextual`: Cartesian TDSE/state projection at 10/40/100 keV proton energy. 이번 유도에서 full paper를 읽었다고 주장하지 않음, exact-reproduction gate 아님 | https://journals.aps.org/pra/abstract/10.1103/PhysRevA.58.2872 |

모델·ETF·Gram·spectral band·small-b bounds는 위에서 직접 유도한 결과다. 기존 R3M25 실행 결과는 저장 보고서를 읽은 것이며 이 문서에서 독립 재실행하지 않았다. 문헌 및 코드 읽기로 모델의 대수적 연결은 명시했지만, R3M25의 local pass를 global production pass로 승격하지 않는다.
