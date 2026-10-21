# C21O: 원시 핵종 전하상태와 LRS photon hierarchy의 조건부 결합

2026-10-21. 이 문서는 새 코드 실행 전의 독립 이론·원전 수용 검토다. 저장 위치는 intake scratch이며 기존 C21L/M/N source·raw를 수정하지 않았다. 실제 SciSpace 검색과 Exa 검색/원문 조회를 수행했고, 수치 ODE 실행은 0회다.

## 1. 지금 구현할 수 있는 정확한 연구 대상

현재 선택은 **H, D, T, ³He, ⁴He, ⁶Li, ⁷Li의 20개 원자 전하상태와 자유 중성자 1개를 추적하고, 그 상태로부터 자유전자 밀도를 계산하여 기존 비편극 elastic Thomson photon hierarchy에 연결하는 non-tilted LRS Bianchi I trace-gas pilot**이다. 자유전자는 전하 중성 조건으로 계산하며 별도의 독립 ODE를 추가하지 않는다. 기존 40개 상태에 21개 원자/핵종 population과 광학깊이 1개를 더하면 62개 상태다. “21개 ion”이라는 표현은 사용하지 않는다.

복사 입력은 정의된 5–150 eV UV cohorts, 가스 온도는 지정한 T(z), 원자 반응은 photoionization와 Case-A 총 radiative recombination으로 고정한다. 각 isotope에 같은 원소의 전자 반응 계수를 적용하는 근사는 입력에 명시한다. n과 T의 초기 abundance 0은 late-primordial IC의 명시적 선택이며, 데이터 부재를 0으로 해석한 것이 아니다. beta decay가 구현되면 초기값이 주어진 별도 검산에서 작동 경로를 확인한다.

이 구성에서 chemistry→n_e→Thomson→photon anisotropic stress→geometry의 동역학 경로가 존재한다. **Prescribed UV·T, 등방 trace gas, 비바리온 massive Vlasov와 dust gravitational closure 아래의 결합 pilot**로 보고한다. 전체 thermochemical/nuclear/stars radiation–Einstein 예측의 완성 상태와는 구분하여 현재 구현의 정확한 경계를 기록한다.

## 2. 첨부 도식과 species coverage

첨부 PNG `원시 광핵반응 및 재이온화 네트워크(3).png`를 직접 읽었다. 도식의 Li 열은 I–III에서 끝나므로 fully stripped Li IV를 보완해야 한다. ⁶Li, ⁷Be, 자유전자, molecular lane은 그림에 없다. 행은 전하상태, 열은 isotope라는 의미를 유지하되, 핵반응 화살표는 원자 ionization graph와 별도 stoichiometry로 구현해야 한다.

| 추적 대상 | 핵전하 Z | 실제 전하상태 | 상태 수 | 이번 closure |
|---|---:|---|---:|---|
| H, D, T | 1 | q=0,1; I,II | 6 | 원자 PI/RR, isotope 전자계수 동일 근사 |
| ³He, ⁴He | 2 | q=0,1,2; I–III | 6 | 원자 PI/RR |
| ⁶Li, ⁷Li | 3 | q=0,1,2,3; I–IV | 8 | 원자 PI/RR; Li I의 채택 valence-shell PI와 omitted core PI를 명시 |
| 자유 n | 0 | 핵종 n | 1 | beta decay; 초기 late-primordial 값 명시 |
| e⁻ | −1 | 자유전자 | algebraic | 전하합으로 계산, Thomson opacity에 사용 |
| ⁷Be | 4 | q=0…4; I–V | 이번 상태에는 없음 | BBN 및 후속 hard-photon 핵반응 확장의 intermediate; absent 기록 |
| H⁻, Li⁻ 및 분자 | 별도 | H₂/H₂⁺, HD/HD⁺, HeH⁺, LiH/LiH⁺ 등 | 이번 상태에는 없음 | chemistry 확장 목록으로 보존, 0 population 측정으로 표현하지 않음 |

Galli–Palla (1998)의 primordial chemistry는 H/D/He/Li와 분자·음이온의 유용한 원전이지만 Li의 모든 양전하 상태를 제공하는 네트워크는 아니다. GRACKLE도 H/D/He 및 분자 경로의 재사용 후보이며 Li 전체 전하상태 source로 삼지 않는다. [S4,S5]

## 3. 실제 확보한 원자 계수와 적용 범위

`H_HE_LI_ATOMIC_COEFFICIENTS.json`은 공식 저자 표에서 추출한 H/He/Li PI 6행, RR 7행(He I의 두 fit 포함), CI 6행, DR 3행을 보존한다. 현재 채택은 PI+RR이며 CI/DR은 수용 가능한 미래 source의 위치를 기록하기 위해 포함했다. `ATOMIC_EXTRACTED_RECEIPT.json`은 로컬 추출 텍스트의 SHA와 URL을 갖는다. Exa clean text는 whitespace가 변환되므로 원 서버 파일과의 byte identity는 검증하지 않았다. Sandbox 직접 HTTP 다운로드 실패는 별도 receipt에 보존했다.

### Photoionization

Verner et al. (1996), v2의 ground-state fit을 사용한다. 광자에너지 E와 fit 에너지 매개변수의 단위는 eV, 단면적의 단위 Mb는 10⁻¹⁸ cm²=10⁻²² m²이다. [S1]

\[
x=E/E_0-y_0,\quad y=(x^2+y_1^2)^{1/2},\qquad
\sigma(E)=\sigma_0[(x-1)^2+y_w^2]
y^{P/2-5.5}(1+\sqrt{y/y_a})^{-P}.
\]

E<E_th에서는 원 반응의 단면적 0이다. Li I/II/III thresholds는 표의 정밀도로 5.392, 75.64, 122.5 eV이다. Li I의 이 식은 inner-shell edge 64.39 eV에서 전환되므로 150 eV까지 단순 연장하지 않는다. 공식 `phfit2.f`, version2(1996-03-25)는 outer/inner-shell 분기를 제공한다. Li I의 high-energy outer-shell PH1은 [5.392,3.466,47.74,20.35,4.423,0], inner 1s PH1은 [64.39,27.40,156.4,33.82,1.490,0]이다. PH1 인수 순서는 threshold,E0,sigma0,ya,P,yw이다. External_results의 현재 구현 선택은 **valence-shell PI**이며 64.39eV 이상은 outer PH1을 사용한다. Core-shell PI는 omitted channel로 기록한다. 전체 shell cross section은 공식 source를 통해 확장할 수 있고, 이때 charge-state yield 및 emitted/deposited energy의 처리도 별도로 결속한다. Valence-only rate를 total atomic photoabsorption rate라고 부르지 않는다. [S1]

### Radiative recombination

Verner–Ferland 표의 ion label은 **재결합 후 생성 ion**이다. 예를 들어 LiIII 행은 Li IV+e⁻→Li III 계수다. [S2]

\[
\alpha(T)=\frac{a}{\sqrt{T/T_0}
(1+\sqrt{T/T_0})^{1-b}(1+\sqrt{T/T_1})^{1+b}}.
\]

식의 분모 위 표기에서 줄바꿈은 곱을 뜻한다: 분모는 `sqrt(T/T0) * (1+sqrt(T/T0))**(1-b) * (1+sqrt(T/T1))**(1+b)`이다. 모든 온도는 K이고 a는 cm³ s⁻¹다. 총 bound-level RR를 사용하므로 escaping recombination photons의 Case-A closure에 대응한다. 재결합 radiation을 다시 chemistry에 넣는 Case-B/on-the-spot 방법과 자동 혼용하지 않는다. 저자의 fit 적용 범위는 3 K부터이며, He I의 a fit은 3 K<T<10⁶ K, b fit은 3 K<T<10¹⁰ K로 별도 제공된다. 선택한 온도 history가 해당 범위에 드는지 실제 기록한다. [S2]

| 생성 ion | a [cm³ s⁻¹] | b | T₀ [K] | T₁ [K] |
|---|---:|---:|---:|---:|
| Li I | 1.036×10⁻¹¹ | 0.3880 | 1.077×10² | 1.177×10⁷ |
| Li II | 1.112×10⁻¹⁰ | 0.6926 | 2.437×10¹ | 8.323×10⁶ |
| Li III | 3.039×10⁻¹⁰ | 0.7539 | 1.871×10¹ | 6.209×10⁶ |

CI/DR/CX를 이번 source에 포함하지 않는 결정은 명시된 반응 집합의 선택이다. cold-T에서 CI fit의 적용 범위를 임의로 확장해서 전체 atomic kinetics라고 부르지 않는다. 원 Voronov 표의 Li CI Tmin은 각각 1,4,5 eV이며, 원 `cfit.f`에는 U>80이면 0을 반환하는 수치 절단이 있다. Badnell 공식 DR fit도 확보했으므로 이 반응을 자료가 존재하지 않는다고 표현하지 않는다. CX의 경우 조사한 구형 Arnaud–Rothenflug ct1/ct3 표에는 Li 행이 없고, 모든 Li charge의 H/He CX를 검증하여 포함한 상태는 아니다. [S3,S6]

## 4. Population ODE, 보존량, 양성성

물리적 baryon number density를 n_b, isotope X와 전하 q의 abundance를 Y_Xq=n_Xq/n_b로 정의한다. LRS 평균 scale factor의 부피는 a³이므로 n_b∝a⁻³이고, η=ln(a/a_i)에서 d/dη=H_t⁻¹d/dt이다. 핵반응이 없는 isotope는 Σ_qY_Xq=Y_X가 보존된다.

\[
\dot Y_{Xq}=\Gamma_{X,q-1}Y_{X,q-1}
+n_e\alpha_{X,q+1}Y_{X,q+1}
-(\Gamma_{Xq}+n_e\alpha_{Xq})Y_{Xq},
\qquad n_e=n_b\sum_{X,q}qY_{Xq}.
\]

경계 q=0,Z에서 존재하지 않는 채널은 물리적인 boundary zero다. 모든 rate가 음이 아니면 각 abundance simplex의 경계에서 벡터장은 바깥쪽으로 향하지 않는다. 따라서 연속 ODE는 비음수성과 isotope 총량을 보존한다. 유한 tolerance의 실제 solver에서도 이 성질이 유지되는지는 별도로 출력 residual을 검사해야 하며 clipping으로 conservation failure를 숨기지 않는다.

자유 neutron decay는 n→H⁺+e⁻+anti-ν_e다. 전자 spectator를 유지한 tritium decay는 T(q=0)→³He(q=1)+e⁻+anti-ν_e 및 T(q=1)→³He(q=2)+e⁻+anti-ν_e로 매핑한다. 이때 baryon number ΣAY는 보존되고, 증가한 nuclear charge가 자유전자 증가와 함께 neutrality를 유지한다. 원 도식의 neutral→neutral 화살표를 그대로 사용하면 이 전하 accounting이 맞지 않는다.

## 5. UV, Thomson, stress의 실제 연결

원자 ground-state 단면적이 입사방향에 무관한 경우

\[
\Gamma_{Xq}=\int d\Omega\int_{\nu_{th}}^\infty
\frac{I_\nu(\hat n)}{h\nu}\sigma_{Xq}(\nu)d\nu
=4\pi\int_{\nu_{th}}^\infty\frac{J_\nu\sigma_{Xq}}{h\nu}d\nu.
\]

따라서 number density로 정의된 discrete photon cohorts라면 Γ=c Σ_g n_γg〈σ〉_g이다. energy density로 정의했으면 반드시 photon energy로 나누어 number density로 변환한다. integrated radiation energy와 quadrupole만으로 threshold별 photoionization rate를 결정할 수 없으므로, 채택한 cohort spectrum/width/normalization을 별도 입력으로 결속한다. H-recombination UV가 Li ionization에 영향을 주는 원전은 spectrum 의존성의 직접 사례이며, 그 논문의 z≈400 결과를 z20→2 결과로 대체하지 않는다. [S7]

비편극 elastic Thomson kernel의 Legendre eigenvalue는 monopole 1, quadrupole 1/10, 나머지 nonzero ℓ에서 0이다. 따라서 optical-time derivative τ′=c σ_T n_e/H_t에 대해 collision loss는 ℓ=0에서0, ℓ=2에서−(9/10)τ′E₂, 나머지 ℓ>0에서−τ′E_ℓ이다. 이 항은 local electron rest frame의 monopole energy/number를 보존한다. Polarization·Compton recoil·photoheating을 이 elastic block으로부터 계산했다고 해석하지 않는다.

기존 massive Vlasov fm=0.1 성분은 비바리온 sector, dust에는 baryons가 포함된다는 source 대응을 유지한다. 새로운 gas의 rest mass를 gravitational density에 다시 더하지 않는다. 등방 gas closure에서는 π_gas=0이며, 이 값은 가정의 결과다. 기존 matter stress는 massive Vlasov에서, radiation stress는 photon과 존재하는 neutrino에서 추출한다. Neutrino는 Thomson opacity를 적용하지 않는다.

\[
\sigma_{\hat i\hat j}=\operatorname{diag}(-S,-S,2S),\qquad
\pi^X_{\hat i\hat j}=\operatorname{diag}(-p^X_s,-p^X_s,2p^X_s),\quad
p^X_s=(p_\parallel^X-p_\perp^X)/3.
\]

\[
\Sigma=\frac{\sqrt6|S|}{H_t},\qquad
\Pi_X=\frac{\sqrt6(8\pi G/c^2)|p_s^X|}{H_t^2},\qquad
P_X=\frac{\sqrt6(8\pi G/c^2)p_s^X}{H_t^2}.
\]

여기서 p_s는 SI energy-density/pressure 단위다. κ=8πG/c⁴, H_geom=H_t/c를 쓰면 κ|π|/H_geom²와 같다. Signed P_tot=P_m+P_γ+P_ν이며 norm Π_tot=|P_tot|이다. Π_m+Π_r와 Π_tot의 차이를 cancellation로 보존한다.

## 6. Trace energy의 계산 가능한 상계

가스 온도를 prescribed T(z)로 둘 때 내부에너지 equation을 풀었다고 기록하지 않는다. 누락한 thermal/binding source의 크기는 출력에서 다음으로 진단할 수 있다. Y_e=n_e/n_b, N_nuc=Σ_XqY_Xq+Y_n, ξ=N_nuc+Y_e로 둔다. 모든 charged states의 최대 ionization energy 합을 I_X,tot이라 쓰면

\[
u_{th}=\frac32 n_b\xi k_BT,\qquad
0\le u_{ion}\le n_b\sum_XY_X I_{X,tot}.
\]

UV cohorts의 실제 u_UV를 포함한 양의 source 상계를 δu_bound=u_th+u_ion,bound+u_UV로 두고,

\[
\epsilon_{H^2}=\frac{8\pi G\,\delta u_{bound}}{3c^2H_t^2}
\]

를 저장하면, **다른 instantaneous state를 고정하고 이 양의 에너지만 Hamiltonian에 추가했을 때** δH/H≤ε_H²/2를 얻는다. 이는 √(1+x)−1≤x/2에서 나온 algebraic bound다. 장시간 trajectory의 global error bound가 아니며 `global_error_bound=null`을 유지한다. T, abundances, UV normalization이 아직 고정되지 않았을 때 작은 수치를 미리 주장하지 않는다. 초기 n/T=0이고 nuclear production을 사용하지 않는 branch에서는 beta-decay heating도 발생하지 않지만, populated decay test의 에너지 방출은 별도 diagnostic으로 남긴다.

향후 thermal closure는 u_th balance 또는

\[
\dot T=-2H_tT-\frac{T}{\xi}\dot\xi
+\frac{2(\mathcal H-\Lambda)}{3k_B n_b\xi}
\]

를 사용한다. 자유전자 생성에 따른 particle-number term −T ξ̇/ξ를 포함하고, photoheating·recombination·collisional excitation/ionization·free-free·Compton·분자 cooling 및 재방출 photon ledger를 선택한 반응 집합과 맞춘다. 이 식은 지금의 prescribed-T 경로와 별도 후속 구현이다.

## 7. 첨부 19반응의 이번 처리와 다음 source

| 도식 번호 | 채널 집합 | 이번 상태 | 근거/남은 입력 |
|---|---|---|---|
| 1–3 | H,He atomic PI/RR | 선택 closure에서 구현 가능 | Verner PI와 총 RR, cohort intensity |
| 4,5,6 | ⁴He→³He+n,T+p,D+D | UV≤150eV에서 photonuclear rate=0 도출 | thresholds20.58,19.81,23.84MeV |
| 7,8 | ³He→D+p, D→p+n | 같은 spectral-support 결과 | thresholds5.49,2.22MeV |
| 9,10 | T,n beta decay | source에 별도 구현/검사 | atomic charge mapping, lifetime, emitted energy |
| 11 | ⁷Li→⁴He+T | UV≤150eV에서 photonuclear rate=0 도출 | threshold2.47MeV |
| 12–19 | np capture, D/p/D/T/³He fusion, T+α capture | 이번 atomic closure의 미채택 nuclear block | temperature/density와 valid nuclear rate source 필요 |

ACROPOLIS의 원논문 Table1은 위 six channels 및 ⁶Li/⁷Be channels를 포함한 17 photonuclear thresholds/rates의 공개 provenance를 제공한다. UV의 최대 photon energy 150eV와 nuclear threshold 사이의 비교만으로 이번 photonuclear rate zero를 도출하므로 GPL 코드 vendor가 필요 없다. 이는 nuclear fusion·decay rate까지 모두0이라는 결론이 아니다. 더 높은 에너지 spectrum을 추가하면 해당 결론을 다시 검토하고, 실제 cross sections 및 electromagnetic cascade·nuclear charge/energy ledger를 연결한다. [S8]

⁷Be는 BBN의 ⁷Li precursor이며 electron capture가 전하상태에 의존한다. 이번 late-time atomic block에서 absent로 기록하되, 향후 nuclear-generation branch에는 q=0…4와 electron-capture kinetics를 넣는다. T·n·⁷Be의 후기 decay를 ACROPOLIS 기본 출력이 자동 완료한다고 가정하지 않는다. [S8,S9]

## 8. 독립 수학 검토와 실행 전/후 최소 검사

현재 식 검토에서는 isotope 총량, baryon number, charge closure, nonnegative-rate simplex, Thomson monopole 보존, signed stress norm 및 SI 대응이 서로 일치한다. 새로운 source 구현의 실제 대조는 아직 수행 전이다. 아래 항목이 확인되면 조건부 pilot의 독립 검토를 마무리할 수 있다.

1. 모든 seven-isotope charge states가 실제 RHS에 있고, algebraic n_e가 같은 현재 state에서 계산된다.
2. 광자 단면적 threshold/inner-shell 전환, Mb→m², cm³→m³, H_t⁻¹ 변환이 source와 맞는다.
3. q 경계·FLRW·zeroUV·zeroelectron·populated n/T decay 사례에서 positivity와 conservation을 확인한다.
4. 기존 collisionless full40 path의 source/tolerance를 고정하고 n_e=0일 때 대응하는 RHS를 재사용한다.
5. 실제 z20→2 저장 trajectory에서 Hamiltonian 및 isotope/baryon/charge residual, signed/norm closure, 모든 물리 population 및 L8 reconstructed E/N의 원 angular nodes 비음수성을 검사한다. 유한 node 검사를 전 방향 양성성 정리로 확대하지 않는다.
6. prescribed-T·UV trace energy 진단을 실제 input에서 평가하고, 결과를 same-physics speedup나 full thermochemical accuracy로 바꾸어 서술하지 않는다.

새 대규모 benchmark는 필요하지 않으며, 현재 변경의 실제 위험을 가르는 최소 검사를 사용한다. 첨부 01의 all-family/CMB statistics 감사는 새 LRS atomic pilot을 전체11-family 또는 polarized CMB 문제로 자동 확장하지 않는다. 04/05의 source-first와 dual audit, 07/08의 plot semantics/residual 가독성 검토를 이번 실제 그림에 적용한다. 내장 physmath 1.0.0의 변경 의존성만 재검토하는 규칙을 적용하며 기존81/125/4 ODE는 반복하지 않는다.

## 원전

- [S1] Verner, Ferland, Korista & Yakovlev, 1996, ApJ465,487; arXiv v2: https://arxiv.org/abs/astro-ph/9601009 ; 공식 계수/코드 https://www.pa.uky.edu/~verner/photo.html .
- [S2] Verner & Ferland, 1996, ApJS103,467, DOI10.1086/192284; https://arxiv.org/abs/astro-ph/9509083 ; https://www.pa.uky.edu/~verner/rec.html .
- [S3] Voronov, 1997, ADNDT65,1; 공식 fit·Fortran https://www.pa.uky.edu/~verner/col.html .
- [S4] Galli & Palla, 1998, The chemistry of the early Universe; https://arxiv.org/abs/astro-ph/9803315 .
- [S5] Smith et al., 2017, GRACKLE: a chemistry and cooling library for astrophysics, DOI10.1093/mnras/stw3291; https://arxiv.org/abs/1610.09591 .
- [S6] Badnell et al. 저자 DR archive https://amdpp.phys.strath.ac.uk/tamoc/DR/ 및 clist_K; Li-specific tables를 실제 확인. 공식 CX collection https://www.pa.uky.edu/~verner/chtr.html .
- [S7] Switzer & Hirata, 2005, PhysRevD72,083002; https://arxiv.org/abs/astro-ph/0507106 .
- [S8] Depta, Hufnagel & Schmidt-Hoberg, 2021, JCAP03,061; 원논문 Table1/eq8 https://arxiv.org/html/2011.06518v1 ; 코드 발견 위치 https://github.com/hep-mh/acropolis/ (이번 구현에 vendor/execute하지 않음).
- [S9] Fuller & Smith, 2010, Nuclear weak interaction rates in primordial nucleosynthesis; https://arxiv.org/abs/1009.0277 . ⁷Be late conversion 원전 후보: Khatri & Sunyaev, DOI10.1134/S1063773711060041 (이번 bounded closure에는 계수 채택하지 않음).

**상태:** EXECUTION=문헌조회·계수추출·직접유도 완료, 새 ODE0 | PUBLICATION=루트 수용 대기 | BACKUP=루트 담당 | DAG=조건부 원자/Thomson closure의 source 구현 및 실제 pilot 검증으로 연결. 전체 thermochemical/nuclear extension은 구체적 별도 의무로 유지.
