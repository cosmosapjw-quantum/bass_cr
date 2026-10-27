# Frozen theory → code contract

Unit `CR_PHYS02_LOW_BIRTH_CAUSAL_RR_V1`; R1 `CONTRACT.md` SHA256 `0766fa66e643de2b50d797fa94838cb989e69c8d3aaa47fe8c31673764757210`가 권위다. 작성자 `/root/theory_review`는 theory 및 independent reference 작성자이고 production 비작성자다. 수치 실행은 C4의 실제 host/code/budget admission 이후 root가 수행한다.

## 1. 변경 입력과 representation

Actual input은 `research/cr_proper_injection_20261027/runs/actual_v1/ACTUAL_SOURCE_RECORDS.json`, 4394309bytes, SHA256 `8fca44c378844029a72253179e557dfa97f6cca8e0f9d6e677d67919ca3797cf`다. Root JSON list에서 `tag=direct_0p1_10`을 유일하게 선택한다. Source history는 `[0,1e10]` proper seconds, atomic bins의 `number_coefficients=[0,A_j]`다. 앞3200개 `stored_node_index=0..3199`는 active E이고 마지막 `cutoff_boundary` atom은 직접 cutoff source다.

Exact stored E_j/A_j를 사용한다. Total-source E≤10 필터, E-grid 재생성, source 재정규화, source quadrature/projection은 하지 않는다. Active coefficient와 direct-cutoff coefficient를 구분한다. Input의 source moments는 원자들의 sum consistency를 확인하는 근거이며 그 moments에서 spectrum을 만들지 않는다. Source 밖 history와 proper volume 크기는 unknown/null이다.

새 inventory는 binary64 recipe `nH=140.; nHe=nH*.248/(4*(1-.248)); ne=.01*(nH+nHe); nb=nH+4*nHe`다. Rational semantics `1085/94,2849/1880,8750/47`도 기록한다. 원 PR109 nb-null을 변경하지 않는다. Source neutrality/parent-ion chemistry는 미제공으로 유지한다.

Constants는 CODATA2022/SciPy1.17.0에 pin한 me,eps0,e,h,c와 `hbar=h/(2*pi)` 한 세트다. PHYS02B Coulomb prescription의 classical/quantum log minimum을 사용한다. Verner native fit literals, `IH=13.60`, `IHe=24.59`, Milne dH=1/dHe=4 및 conditional ground-channel interpretation은 `intake/RR_SOURCE_BINDINGS.json`을 따른다. RR target density는 `.01*nH`와 `.01*nHe`다. Source neutral target factor는 원 A 내부, recipient ion target factor는 λ 내부에 각각 한 번 존재한다.

## 2. 새 active count operator

Cutoff E0=.1; `d_j=b_j/(E_j−E_(j−1))`; `lambda_Hj=nHII*v_j*sigma_RRH_j`, He도 같다. Active generator L의 diagonal은 `−(d+lambda_H+lambda_He)`, upper diagonal `(row=j−1,col=j)`은 `d_j`다. Source는 `t*A`, initial active state0이다. 저장 source는 원래 energy-coordinate construction에서 나왔지만 현재 input의 A_j는 이미 count coefficient이므로 E로 다시 나누지 않는다.

`n(t)=t²phi2(tL)A`, `O(t)=t³phi3(tL)A`이며 O는 actual finite occupation density-time이다. Endpoint rate는 `lambda·n`, cumulative capture는 `lambda·O`다. C_H를 λ로 나누는 방식은 per-state C_H,j와 λ_H,j>0일 때만 동일하다. 집계 C_H/λ_j는 사용하지 않는다.

Production은 active-only positive P sweep을 사용할 수 있다. `nu>=max departure`, `P_a=I+L/nu`는 substochastic이며, absorber counts를 더한 conceptual P가 stochastic이다. P_a에서 active vector만 갱신해 n/O를 얻고 absorber/reward를 O에서 만든다. This avoids carrying thousands of unnecessary probability states. Actual ν and floating positivity are recorded.

## 3. Positive Poisson weights와 termination

`x=nu*t`, actual unnormalized `p_n=exp(−x)x^n/n!`. Finite-n truncation n≤M을 사용한다.

`w_k=x^(−2) sum_(n=k+2)^M (n−k−1)p_n`, k0..M−2.

`v_k=x^(−3) sum_(n=k+3)^M binom(n−k−1,2)p_n`, k0..M−3.

`n_hat=t² sum w_k P_a^k A`; `O_hat=t³ sum v_k P_a^k A`.

추가 backward cumulative sum으로 `sum_(k=l+1)^(M−2)w_k=x*v_l`를 사용할 수 있다. 같은 M이면 `n_hat−L O_hat=(t²/2)A*Pr(Pois(x)≤M−2)`가 exact arithmetic에서 성립한다. 따라서 O에서 계산한 capture/cutoff/caloric ledgers는 n_hat과 동일한 truncated source mass를 보존한다. Direct-cutoff injection은 exact analytic `Acut*t²/2`, `Ecut*Acut*t²/2`로 별도 더할 수 있다.

Tail은 전체 injection count/energy의1e−13, 각 positive channel capture의1e−12 이하로 할당한다. Tiny RR에는

`eps_c <= min[Ninj,active*Pr(Pois(x)>=M−1), Aactive*lambda_c,max*t³/6*Pr(Pois(x)>=M−2)]`

를 적용한다. Kcapture bound는 Emax*eps_c, photon-energy bound는 (Emax+Ic)*eps_c다. Endpoint rate tail은 λmax에 active count-tail bound를 곱한다. Source direct-cutoff atom은 RR error bound의 active source 합에 포함하지 않는다.

Absolute p_n normalization을 유지한다. Centered/scaled weights의 truncated sum을1로 맞추면 다른 algorithm이므로 normalization error를 따로 다루어야 한다. These are analytic exact-arithmetic bounds evaluated numerically; ordinary FP summation/Poisson arithmetic is separately checked and is not an outward interval certificate.

## 4. 네 prefix와 네 emission bin

Actual prefixes는 T/4,T/2,3T/4,T이고 source absolute clock은 항상0에서 시작한다. Four-time one-sweep reuse가 가능하다. Prefixes는 diagnostics이며 서로 합하지 않는다. Bin outputs는 `[0,T/4],(T/4,T/2],(T/2,3T/4],(3T/4,T]`의 disjoint returns다.

`O_bin=O(t1)−O(t0)`이며 prior source survivors를 유지한다. 직접 formula는 `h phi1(hL)n(t0)+t0*h²phi2(hL)A+h³phi3(hL)A`다. Endpoint prefix tails에서 bin error에는 두 endpoint bounds를 전파한다. Positive partial-prefix differences가 자동 lower bound는 아니다. T에서의 endpoint rate는 known-history left limit이다.

Native birth family/partition과 observation bin을 별도 fields로 보존한다. Capture current E가 native birth E를 대신하지 않는다. Same-event family/channel/birth partition/observation overlap은 거절하고, four disjoint emission bins는 같은 input history를 참조할 수 있다.

## 5. 출력 ledgers와 native25

Prefix active N/E: `sum n_j`, `sum E_j*n_j`.

Drift cutoff N/E: `d_1*O_1`, `.1*d_1*O_1`; direct cutoff는 원 source atom에서 별도 계산한다.

Coulomb caloric energy: `sum b_j*O_j` eV/m³.

Per-channel captures: `C_cj=lambda_cj*O_j`, N=`sum C`, K=`sum E*C`, photon count=N, photon energy=`sum(E+Ic)*C`. Discrete photon atoms는 그 실제 capture measures에서 만들며 transport/escape/heating을 계산한 것으로 표시하지 않는다.

Count closure: Ninj=Nactive+Ncut+CH+CHe.

Kinetic closure: Uinj=Uactive+Qc+Ucut+KH+KHe.

Photon+binding closure: Uinj=Uactive+Qc+Ucut+UγH+UγHe−IH*CH−IHe*CHe.

RR-only native25 delta는 H1I/H1II indices1/2, He4I/He4II indices10/11에 ±capture/nb, ζ(index21)=−(CH+CHe)/nb, w_nt(index22)=−(KH+KHe)*eV_J/nb, w_ext(index23)=0, logT(index24)=0(frozen diagnostic)이다. `q·DeltaY−Deltaζ=0`을 확인한다. Source parent-ion chemistry가 없으므로 **full_source_native25=null**이다. Net active N/nb·E/nb는 독립적인 diagnostics다. Cutoff thermal join은 명시적 closure하의 별도 candidate이며 physical heating/global completion은 승격하지 않는다.

## 6. 독립 reference와 고정 acceptance

Reference는 source input을 독립적으로 읽고 constants/density/Verner/Milne/Coulomb 식을 직접 구현한다. Production modules, primary arrays를 coefficient input으로 import하지 않는다. Number-active state와 occupancy, polynomial forcing을 sparse augmented matrix에 넣고 `expm_multiply`로 네 times를 얻는다. Dimensionless time u=t/T와 normalized source shape를 사용하여 tiny physical source와 unit-valued clock의 scaling을 분리한다.

Reference comparison은 actual prefix/bin의 positive H/He capture N/K/photon quantities를 각 quantity 자체의 scale로1e−9 이내에서 검사한다. Total-source scale로 tiny RR discrepancy를 가리지 않는다. Count/energy closure 및 source/photon/native stoichiometry는1e−11 기준이다. Array coefficient comparison과 occupancy/state values는 independent method의 직접 근거로 저장한다. Exact-zero values는 별도 zero rule로 처리한다.

Agreed primary artifact는 `runs/primary_v1/ARRAYS.npz`, `RESULT.json`이다. Arrays include E,A,b,drift,lambda_H,lambda_He,times; four n_prefix/O_prefix/O_bins; four per-energy H/He capture prefix/bin arrays. RESULT has four prefixes and four observation_bins, scalar source/cutoff/caloric/channel/native ledgers and reported tail bounds. Exact schema is frozen by implementation before C4.

`review/independent_reference.py`는 소스만 준비하고 root C4 전에는 import/compile/test/run하지 않는다. Nominal10CPU reference reservation과 coordinator cost를 새40CPU 단위 안에서 root가 배정한다. Old20/30/parallel budgets는 이월하지 않는다. 모든 실패·UNKNOWN_NO_ACK·과거 accepted science identity는 유지한다.
