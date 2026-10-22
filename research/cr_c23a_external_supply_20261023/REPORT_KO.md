# C23A — 실제 원자료에 결속한 UVB·전자·핵 β 공급 연구

작성일: 2026-10-23 KST. 운영 규약 physmath-research-loop 1.0.0 / 승인 설계 v0.2.

## 1. 이번에 확보한 결과

이번 단위는 **실제 외부 입력을 읽는 공급 연산자와, 그 연산자를 안전하게 단순화하는 계산식**을 만들었다. Puchwein fiducial UVB를 읽는 H/He 광이온화 component, Furlanetto–Stoever 전자 침적표의 spectrum 사전 적분, ENDF β 자료를 이용한 finite-energy coverage가 각각 별도 source identity를 갖는다. 완료된 C21O–C22D/NCP 과학 계산의 복원 목적 재실행은 0이며, 새로운 cosmological ODE도 0이다. 실제 새 계산은 아래의 source response·고정밀 검사·quadrature다.

| 새 단위 | 실제 수행 | 확인한 결과 |
|---|---|---|
| P19 source adapter | 원본 59 redshift, 3개 PI와 3개 heat rate; node·중간값·오류 처리 | 18개 검사 PASS_SCOPED. plateau에서 exp(log(x))가 경계를 벗어난 최초 실패와 수정 보존 |
| H/He source subflow | 59 z × 2 inventory × 7 exposure = **826개**; 추가 1,652개 half-step 합성 | 핵종 최대 잔차 1.1102e-16, 전자–event 최대 2.2204e-16, 에너지 상대 잔차 9.5736e-17 |
| Subflow 독립 oracle | 283 rate cases / 1,915 calls, mpmath 80자리 8×8 augmented exponential, 28 invalid-input cases | v1 실패 1개 → 양의 해석식 v2에서 0개. v2 population abs/inventory 최대 2.1926e-16 |
| FS finite-table response | 3,612 source nodes, 3,341 cells, 70자리 적분과 독립 Gauss 비교 | 수치 표 연산 PASS_SCOPED; 일반 21종 gas coupling은 별도 입력 의무 |
| 고정 spectrum 사전 적분 | 3 spectra × 64 queries × 3 paired repetitions | 준비+64조회 포함 시간비 median **4.91144**; direct/prepared 최대 상대차 **4.35066e-16** |
| 핵 β source coverage | neutron/T ENDF8 실제 원자료, shape-free bound 및 별도 F=1 phase-space 진단 | neutron 중앙값 조건에서 FS 구간 밖 β 운동에너지 **≥97.9467539824%** |

위 잔차는 정의한 이산·연산자 모델의 검사다. 원자료의 정확성, 전체 IGM 진화 또는 전역 오차 인증의 수치가 아니다. **global_error_bound=null**을 유지한다. 이 보고서는 배송 전 scientific snapshot이며, 실제 Git ref·provider ACK·readback 수준은 최종 authority와 transport receipt가 소유한다.

## 2. 최신 자료를 어떻게 종합했는가

7개 알려진 저장소의 GitHub REST `matching-refs/heads` 결과 **1,278개**를 모두 비교했다. 복구 C22D의 1,271개 대비 **+7 added / 6 changed / 0 removed**다. 이는 해당 7개 저장소의 반환된 head 집합에 대한 전수 조사다. 모든 조직·미노출 저장소나 모든 과거 raw 결과의 전수 감사는 아니다. 선택 text **74개 / 830,327 bytes**는 Git tree의 크기·blob SHA1 및 로컬 SHA256가 일치했다. PR96/REI219/220/221/222/HE85/BASS180도 실제 현재 head를 읽었다. 세부 근거는 `intake/INTAKE_REPORT_KO.md` 및 binding 목록이다.

PR96 관측 parent는 `ba39fc75521aa18705ec832d789e50dd5c6565bc`다. 48,727,596-byte C22D 배송본 SHA256 `a64bda4bd0f3527a1ae526d84a3ac709f73777ed76d1e55f259f54c77ece5ed9`를 실제 다시 받아 CRC와 **285개 payload**를 모두 검증하고 create-only 복원했다. 과거 결과를 다시 적분하여 복원한 것이 아니다.

현재 실행 중인 외부 host의 process/lease는 **UNOBSERVED**다. Owner의 완료 보고를 읽은 것을 live queue 확인으로 바꾸지 않았다. 전체 타 대화 transcript는 connector의 unavailable 응답에 따라 **UNAVAILABLE**, 최초 핵반응 PNG는 **NOT_RECOVERED_NOT_READ**다.

실제 종합에서 다음 중복·오채택을 피했다.

- BASS_CR의 massive Bianchi characteristic, 현재 에너지로 kernel 재결속, cutoff·source energy ledger는 이미 후속 연구에서 완료된 구성이었다. 새로운 propagator로 다시 만들거나 old suites를 반복하지 않았다. 과거 GPL notice와 관련 Rudd 수정 계보를 보존한다.
- REI221의 independent isotope state·전자 rank-one Jacobian·local event ledger는 재사용할 수 있는 기존 구성이다. donor `atomic.py`는 transitive 입력을 요구하므로 일부 파일만 import해 전체 provider로 취급하지 않았다. 이번 source-specific H/He 코드는 독립 작성한 알려진 positive semigroup 구현이다.
- HH81의 finite-window H1/He4/Li7 CI와 7→3 hazard 축약, HE36의 α/β/γ reactive-loss moment는 현재 계약/유도다. 후자의 resolved birth tensor가 채워졌다고 하지 않는다. 축약 차원을 측정 speedup으로 부르지 않았다.
- REI18-family nuclear는 all-bare, instant-thermalization, passive-reservoir 조건이다. thermal neutron 1/v anchor를 DD MeV 생성물 stopping으로 바꾸어 쓰지 않았다.
- REI220/BASS180의 mirror 관계, 최초127의 JSON 실패·재적분, 기존 representative raw4개 PASS_SCOPED, VigilODE P02 C6 FAIL, HE85/REI219의 역사적 미완료→후속 scoped 보고 이력을 함께 보존했다.

## 3. UVB source: 실제 moment 표와 양의 반응 subflow

### 3.1 채택한 자료와 inventory

[Puchwein et al., arXiv:1801.04931v1](https://arxiv.org/html/1801.04931v1)의 D1 fiducial ancillary table을 채택했다. 원본은 [rates_fiducial.txt](https://arxiv.org/src/1801.04931v1/anc/rates_fiducial.txt), 4,381 bytes, SHA256 `5b4cca58fcc46e821970c0a5a8cbb188cf2b5e6c00f56d6942588c86806662fe`다. v1은 2018년 버전이며 2019년 저널판과 bytes가 같다고 주장하지 않는다. D2 equivalent-equilibrium table과 구별한다.

범위는 **0≤z≤15.1**이다. Γ_i는 s^-1/target, H_i는 eV s^-1/target의 excess heating이다. 원자료 node는 그대로 반환하고, 사이에서는 log(1+z)에 대해 양의 rate의 log를 선형 보간한다. z20로 외삽하지 않는다. 원본 Compton 열은 convention이 확정되지 않아 사용하지 않는다. 미지원 열을 0으로 치환한 것은 아니다.

새 API의 inventory는 명시적 `(HI,HII,HeI,HeII,HeIII)`다. 두 diagnostic inventory는 H=1, He=0.083이며 각각 중성/부분 이온화, T0=100/10000 K다. 이는 전체 21종을 quotient하거나 D/T/He3/Li를 없앤 상태가 아니다. Source component의 제한된 입력이며 추가 종이 들어오면 거절한다. 원래 n/T=0 선언과 absent species의 구별은 유지한다.

### 3.2 연속식과 event count

고정 proper volume·고정 z에서 외부 rate를 일정하게 두고,

\[
\dot X_{\rm HI}=-\Gamma_HX_{\rm HI},\qquad
\frac{d}{dt}\begin{pmatrix}X_0\\X_1\\X_2\end{pmatrix}
=\begin{pmatrix}-\Gamma_1&0&0\\\Gamma_1&-\Gamma_2&0\\0&\Gamma_2&0\end{pmatrix}
\begin{pmatrix}X_0\\X_1\\X_2\end{pmatrix}.
\]

He의 각 성분은 HeI/HeII/HeIII다. 누적 event count C_H,C_1,C_2를 함께 계산하면

\[
\Delta N_e=C_H+C_1+C_2,\quad
\Delta U=\sum_i \frac{H_i}{\Gamma_i}C_i,\quad
\Delta B=\sum_i\chi_i^{\rm model}C_i,\quad
E_{\rm imported}=\Delta U+\Delta B.
\]

Γ=H=0은 명시한 inactive control로 처리하고, Γ=0인데 H>0이면 다른 heating process이므로 거절한다. H/He nuclei는 generator의 column sum으로 보존된다. 전하 neutrality와 생성 전자 수를 event ledger 및 최종 state에서 각각 확인했다. χ_model=(13.6058,24.59,54.42)eV는 C22D에서 계승한 **명시적 회계 registry**다. P19의 수치 threshold convention은 별도로 확정되지 않았으므로 E_imported는 선언한 moment 모델의 장부이지, 실제 입사 photon spectrum을 유일하게 복원한 값이 아니다.

온도는

\[
N=\sum_iX_i+N_e,\qquad T=\frac{2U}{3k_BN}
\]

로 복원한다. 따라서 dT/dt에는 thermal energy뿐 아니라 새 전자의 heat capacity도 들어간다. 이번 저장 격자에서 N을 초기값으로 고정하면 온도를 최대 **2.063691배** 크게 계산한다. 이 비교는 같은 source-only 입력에 대한 것이다.

### 3.3 관측된 실패가 이끈 안정한 계산식

첫 구현은 positive uniformization과 scaling/squaring을 사용했다. P19 z=5.81, dt=1e17 s, 순수 HeI 조건에서 HeIII 오차가 2.0463038e-12로 사전 population 기준 2e-12를 넘었다. 작은 exact-arithmetic series tail은 누적 floating-point rounding을 통제하지 못했다. 실패 원본과 결과는 `review/photo_subflow_v1`에 보존했다.

a=Γ1 dt, b=Γ2 dt, m=min(a,b), d=|a-b|를 쓰면 두 전이 확률은

\[
K_{20}=F(m)+m e^{-m}G(d),\quad
F(x)=1-(1+x)e^{-x},\quad
G(d)=1-\frac{1-e^{-d}}d,\quad G(0)=0.
\]

작은 인자는

\[
F(x)=e^{-x}\sum_{n=2}^{\infty}\frac{x^n}{n!},\qquad
G(d)=e^{-d}\sum_{n=1}^{\infty}\frac{n d^n}{(n+1)!}
\]

라는 양의 급수로 계산한다. 큰 인자는 `expm1`을 쓴다. 매우 다른 rate, 거의 같은 rate, 작은 노출량에서 큰 항끼리 빼거나 거의 항등인 행렬을 반복 제곱할 필요가 없어졌다. 알려진 birth-chain 확률을 안정하게 평가하는 구현이며 새로운 semigroup 이론의 최초 발견을 주장하지 않는다.

수정 후 동일 **283 cases/1,915 calls와 28 fail-closed 기준**을 유지했다. 독립 80자리 oracle은 production 수식을 사용하지 않은 8×8 population/event augmented matrix exponential이다. 최대 population abs/inventory=2.1926e-16, event=9.2141e-17이며 원 실패 case는 5.1772e-17로 교정됐다. `series_tail_upper`는 K20 exact-arithmetic 절단항만의 값이다. floating-point/global/physical error bound가 아니다.

### 3.4 실제 새 source-response 계산

새 run은 `c23a_p19_subflow_20261023_v1`, source identity는 `5d7a4a41d7a10fccf12458807d31630cf1bed65c2a38fdfb9b9dbb1c9fa674f7`다. θ=max_iΓ_i dt를 0,1e-6,1e-3,0.1,1,10,100으로 지정했다. 각 row는 독립된 고정 배경 노출이며 z에 따라 이어지는 cosmological trajectory가 아니다. 일부 frozen duration은 cosmic time보다 길어질 수 있으며, 해당 값을 IGM 예측으로 해석하지 않는다.

| 중성 초기조건 | 최종 T 범위 | 생성 전자/Href 범위 |
|---|---:|---:|
| θ=1 | 10,967.879–17,818.764 K | 0.580113–0.667160 |
| θ=10 | 14,693.485–25,405.087 K | 1.082073–1.093586 |
| θ=100 | 14,865.036–28,587.827 K | 1.083132–1.151978 |

826개 본체 response와 1,652개 half-step comparison은 약 wall/CPU 1.204/1.203 s에 실행됐다. 보존과 semigroup 잔차는 표1에 기록했다. Recombination, collisions, expansion, Compton, finite photon reservoir를 포함한 온도 이력은 다음 coupling의 별도 의무다. 최종 그림은 `analysis_v3`이며 source-only 문구를 그림과 caption에 넣었다.

## 4. CR/전자 공급: spectrum을 보존하면서 반복 계산을 줄인다

### 4.1 실제 FS2010 입력과 채택 경계

[Furlanetto–Stoever](https://arxiv.org/abs/0910.4410)와 [원저자 코드 페이지](https://cosmicdawn.astro.ucla.edu/codes_and_tools.html)의 실제 archive를 읽었다. 310,272-byte archive SHA256는 `e9760d637b5bd97fe981cb459a7e2d733692a9f9f8deb9a757224b14be632101`다. 원표는 **10–9937.21 eV**, 14×258 nodes다. 첫 열의 에너지는 post-primary 전자의 운동에너지로 해석해야 한다.

현재 package에는 C 좌표와 header 충돌, 논문 Table1과 archive의 차이, 최대 **3.9e-5**의 f_ion+f_heat+f_exc closure defect가 있다. 이를 clipping·renormalization으로 숨기지 않았다. 원 C reader의 buffer 문제 때문에 그 C는 실행하지 않았다. 새 parser와 적분기는 독립 작성했다.

배경은 xHII=xHeII, HeIII=0의 제한된 source family다. 수치 He/H도 별도로 확정해야 한다. 따라서 원 21종 상태를 임의의 단일 xe로 투영하여 physical response로 사용하지 않는다. 원 C의 좌표를 사용하는 14-row diagnostic과 header가 일치하는 ξ=(0.1,0.5,0.9,0.99,0.999) 5-row slice를 분리했다. 성능 측정은 후자다.

실제 [21cmFAST@72d8a2d](https://github.com/21cmfast/21cmFAST/tree/72d8a2d23702f1b69fbc85abd25d4592a7bcd3f5)의 MIT table mirror 14개를 취득하고 모든 numeric token이 원저자 표와 같음을 확인했다. 마지막 newline 차이로 byte-identical은 아니다. Public payload는 MIT notice와 mirror, 새 코드·결과를 포함하고 원저자 C 전체를 재배포하지 않는다. DarkHistory의 작은 MIT 코드·표는 read-only 후보로 조사했으며 새 물리 provider로 승인하지 않았다.

### 4.2 정확한 사전 적분의 의미

명시적 PL electron source q(E)와 유한 표의 채널 response r_k(E,ξ)를 두고

\[
D_k(\xi)=\int q(E)r_k(E,\xi)\,dE
\]

를 계산한다. Energy channel에는 E를 추가로 곱한다. 표와 q의 node 합집합에서 count integrand는 2차, energy integrand는 3차 다항식이다. 양의 Bernstein 가중치로 해당 보간모델의 적분을 정확하게 계산할 수 있다. ξ의 선형 보간과 적분은 교환되므로 고정 q에 대해서는 각 ξ node의 D_k를 한 번 준비하고 후속 query에서 채널별 선형 결합만 수행한다. 원자료의 물리 오차나 보간 오차까지 사라지는 것은 아니다.

실제 9개 paired timing에서 construction+64 queries를 포함한 direct/prepared 시간비는 **1.86383–5.91058**, median **4.91144**다. Query-only median 1008.21은 준비 비용을 제외한 값이므로 대표 결과로 사용하지 않는다. 상각 조회수 median은 약12.9844이며 timing 변동을 모두 보존했다. Cosmological ODE 또는 NCP speedup을 측정한 결과는 아니다.

### 4.3 두 moment만으로 충분하지 않은 실제 예

ξ=0.1의 동일 동결 source gas에서 `1 electron at100eV`와 `0.5 at10eV +0.5 at190eV`는 전자 수와 총 운동에너지가 각각 1과100eV로 같다. 그런데 표를 실제 적분한 heat는 **86.49070834 vs81.91488963eV**, 차이는 **−4.57581871eV**다. 이 한정된 response에서 count와 첫 energy moment만으로 채널값을 정할 수 없다는 구성적 반례다. 일반 transport 전체에 대한 새 strong no-go를 주장하지 않는다.

따라서 P19의 Γ와 H로 평균 전자 에너지 H/Γ를 만든 뒤 FS를 그 한 점에서 평가하는 shortcut은 현재 계약에 채택하지 않는다. 실제 q(E) 또는 별도로 검증된 spectrum family가 필요하다. 최초 photon ionization의 binding energy는 primary 사건이, 남은 electron kinetic energy는 cascade가 소유한다. 기존 즉시 photoheating에 FS heat를 더하는 이중 계상, Lyα energy를 excitation energy에 다시 더하는 계상, 이미 source model이 처리한 helium photon 재흡수의 중복도 피해야 한다.

## 5. 핵 β 공급과 유한 전자 침적표의 실제 coverage

기존 REI `EVALUATED_DECAY_INPUTS.json`에는 수명이 있지만 Q와 평균 β 에너지는 없었다. 별도로 [IAEA의 ENDF/B-VIII.0 decay 배포본](https://www-nds.iaea.org/public/download-endf/ENDF-B-VIII.0/decay/)에서 neutron/T ZIP을 받아 CRC와 payload SHA를 확인했다. 이 historical energy 입력을 현재 lifetime이나 최신 정밀 평가로 바꾸어 쓰지 않는다. 평가일/변환일/배포일을 분리한다.

| 평가자료 중앙값 | Q 또는 ER | 평균 β 전자 운동에너지 |
|---|---:|---:|
| neutron | 782,347 eV | 301,370 eV |
| T | 18,590 eV | 5,690 eV; 입력 uncertainty40eV |

ENDF의 ER/Q는 정밀 recoil-corrected electron endpoint와 동일하지 않다. 여기서는 energy support의 보수적 ceiling Q 및 별도 illustrative spectrum parameter로 쓴다. neutron 평균의 저장 uncertainty0을 물리 uncertainty0으로 승격하지 않았다. 실제 continuous spectrum이 제공되지 않았다는 상태도 보존한다.

전자 수를 1로 정규화한 양의 measure가 **동일한 에너지 frame**에서 [0,Q]에 있고 평균이 m이라고 하자. 평가 Q와 평균은 parent rest frame에 결속하며, 움직이는 n/T 또는 CR parent의 bath-frame 전자에는 boost 없이 Q ceiling을 적용하지 않는다. FS 상한 U=9937.21eV보다 m이 크면, 구간 내부의 number fraction p는

\[
m\le pU+(1-p)Q\quad\Rightarrow\quad
p\le\frac{Q-m}{Q-U}.
\]

구간 안 운동에너지는 pU 이하이므로, 전체 β 전자 운동에너지 대비 coverage는

\[
f_E([10,U])\le\frac{U(Q-m)}{m(Q-U)}.
\]

위 **평가 중앙값과 support 가정**을 neutron에 넣으면 coverage≤**2.0532460176%**, outside≥**97.9467539824%**다. 이는 electron spectrum shape를 채워 넣지 않고도 얻는 조건부 coverage 경계이며 물리적 heating fraction 또는 통계적 confidence bound가 아니다. T는 평균/Q만으로 유의한 outside-energy 하한을 만들 수 없다.

별도 진단으로 Fermi function을1로 둔 allowed phase-space weight

\[
w(T_e)\propto\sqrt{T_e(T_e+2m_ec^2)}(T_e+m_ec^2)(Q-T_e)^2
\]

를 사용했다. 이 곡선은 **평가된 β spectrum이 아니다**. 실제 Coulomb, recoil, radiative, atomic/molecular final-state correction과 precise endpoint 의무를 남긴다. 이 예시에서 FS구간 안 number/energy fraction은 neutron **0.3659666% /0.00720573%**, T **81.97985% /64.66412%**다. T의 상부 tail에 놓인 energy35.33588%를 0으로 버리지 않는다.

24개 moment/구간의 scipy quadrature와 80자리 기준은 최대 상대차3.878e-16, 독립 antiderivative와 80자리 값은2.970e-60이었다. 코드는 neutron/proton/triton 등의 kinetic input을 electron-only FS provider에 바로 넣지 않는다. 핵 reaction rate, prompt neutron stopping, daughter charge, escaped photon/neutrino, thermal feedback를 이 계산이 제공하는 것은 아니다.

## 6. 전체 목표로 연결하는 coverage 계약

Non-tilted LRS와 metric signature(-,+,+,+), full Frobenius norm을 유지한다. Signed Pγ/Pν/Pm/Pr, scalar norm, cancellation을 구별하고 Πr=|Pγ+Pν|, Πtot=|Pm+Pr|를 계승한다. 이번 source component는 atomic gas의 isotropic stress closure를 쓰며 별도 nonbaryonic Vlasov anisotropic stress를 변경하지 않는다.

| 결합 의무 | 현재 실제 확보 | 다음에 필요한 입력/작업 |
|---|---|---|
| UVB primary source | 3개 H/He Γ,H 및 positive subflow | source threshold convention, spectrum 또는 검증된 moment-only 모델 채택, z>15.1 공급 |
| Atomic rate coverage | C22D의 기존 제한된 provider 및 이번 H/He source | isotope별 CI/RR/DR/CX/line/molecular 범위·최종상태·에너지 계약 |
| Nonthermal electrons | FS finite-table operator, 양의 PL contraction, 실제 자료 결함 기록 | gas composition/He normalization, source spectrum, high-energy 및 <10eV continuation, loss-time/locality |
| Nuclear sources | 기존 passive18-family와 이번 β moment/coverage | 실제 β spectra, finite stopping, recoil·fragment·neutrino ledger, photo/nuclear feedback |
| Stellar/CR/IGM 공급 | 기존 MD14 fit와 source/geometry 코드의 정확한 계보 | 선택 source normalization, proper/comoving units, injection time·species·angular distribution |
| Global energy closure | 각 component의 명시적 event/energy ownership | expansion work, dynamic radiation/Einstein coupling, double-count 방지와 전체 독립 검증 |

새 반응은 전하·핵종·에너지 보존뿐 아니라 유효 T/E, dominant omitted processes, isotope quotient의 동일 generator/동일 source 조건을 확인해야 한다. 공급자가 없는 항을0으로 채우지 않는다. Full nuclear high-energy 및 general triaxial/tilted/polarized CMB는 HOLD다.

## 7. 실행·검토·배송과 다음 순서

실제 sandbox는 affinity0–8, quota8 cores, memory limit8GiB였다. CPU55는 이 host에 없으며 사용하지 않았다. Coordinator0, 각 새 worker1/3/4/5, native thread1, 실제 cooperative lease 및 create-only run directory를 썼다. 기존51 NCP rerun0, 새NCP dispatch0이다. 자세한 headroom·timing·lease 반환은 각 run의 receipt다.

원본 실패는 삭제하지 않는다: P19 plateau rounding, photo-subflow v1 squaring drift, launcher의 비정규 lease CPU encoding 및 unknown-memory 처리, figure legend overlap, 접근 실패한 원문/도구 응답을 각각 수치·구현·환경·입력으로 분류했다. Source 원자료의 차이를 소프트웨어 성공으로 덮지 않았다.

R1–R10과 C1–C10의 단계·네 축은 `STAGES.json`과 `NEXT_DAG.json`이 소유한다. 과학 단위는 공급 component 범위로 COMPLETE_SCOPED다. 전체 물리 목표의 고정 가중 분모는 없으므로 overall percentage는 null이다. 전체 목표를100%라고 표현하지 않는다.

다음 순서는 실제 source composition/threshold/energy-range 조건을 닫고 → source별 열화·방출 spectra를 결속하고 → 기존 열·원자 solver에 admitted component를 합성하고 → 새 입력·새 run ID로 영향받는 작은 검증 및 실행 → 분석 → 게시/백업이다. 완료된826 response와 기존 cosmological 계산은 복원용으로 반복하지 않는다. 새로운 물리적 input이 생기면 그 변경된 의존성부터 재개한다.

배송은 GitHub source/results commit, 별도 release ZIP과 SHA/size manifest, provider별 실제 ACK/R3 readback, 최종 authority, 복사 가능한 handoff 순서로 결속한다. Drive의 과거 C21O 보존 확인은 OPEN이며 이번 새 파일의 상태와 구별한다. Library·Dropbox 성공만으로 삼중 백업이라고 쓰지 않는다.

### 7.1 최종 독립 검토와 공개 묶음 소비

핵 공급 C9는 실제 source manifest29개/233,841B와 실행 pin7개를 확인하고 PASS_SCOPED로 판정했다. Same-frame/initial-state 조건은 문서 의무를 닫았으며 물리 adoption은 OPEN이다. 별도 공개 묶음 smoke는 새3-node PL 입력 한 개만 실행했다. 실제 workspace 의존성17개 모두 공개 `deposition/` 안에 있었고 원 archive/upstream 읽기는0이었다. CPU3/native1,wall0.106712s,leaseRELEASED,consumer1call이다. 기존 audit/benchmark/ODE 재실행은0이다. 이전 `NOT_RUN` 문서는 그대로 두고 새 receipt를 추가했다.
