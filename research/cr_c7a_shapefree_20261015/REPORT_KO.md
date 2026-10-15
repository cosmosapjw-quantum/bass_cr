# BASS_CR: SOURCE07 C7의 분포형태 불확실성에 대한 shape-free 이온화·가열 범위

**2026-10-15 KST.** 선택 연구 단위: PR #69의 `REI_SOURCE07_C6_HARDENED_SPECTRAL_HISTORY`에 대한 건설적인 후속 이론 R5와 source-scoped C5–C8 구현·검증. 현재 기계에서 실제로 완료한 계산을 기반으로 작성했다. 기존 bb50k 새 source의 C10 source subcell 오차를 재실행하여 같은 결과를 꾸미는 것이 아니라, **임의의 양의 현재 photon spectrum의 알려진 첫 두 모멘트 및 q-bin energy support만으로 허용되는 종별 event·heat 범위를 산출**한다.

## 1. 최신 원본과 모델

- `bass_cr` 부모 draft PR69 head `669cbebe5e0a4383d7999aa354a3f320eff39fd2`, BB source `MD14_Z002_FESC_BB50K_13P6_100_V1_NATIVE48`; 기존 threshold/source code를 수정하지 않는다.
- 읽은 실제 `rei_bianchi` SOURCE07 C6 head `450bad5712d6bc3c58598ea8421232128411b573`: q-grid마다 `(N,U_ref)`를 저장하고, 양의 bounded exponential 최대엔트로피형 closure 후 Verner fit 문턱을 분할한 Rust 알고리즘. nE256, z20, gas frozen에서 HeI source 상대차 `+1.787547478926399e-7`, heat 상대차 `-6.394362817019328e-9`. 그러나 두 모멘트는 source-age별 hardened spectral shape를 결정하지 못한다. Owner C7 A(source support/age), B(time-varying opacity)는 미완료이며 AX08 signed family/AX11/AX12의 과학 상태는 바꾸지 않는다.
- 정상 proper seconds, E_physical=R E_ref (eV), signature `(-,+,+,+)`, C=29979245800 cm/s, proper neutral absorber cm^-3; fit cutoff `(13.60,24.59,54.42)` eV, chemical binding `(13.598434599702,24.587389011,54.41776)` eV. Current input mass and first reference-energy moment는 원/source J/R를 **이미 한 번 적용한 owner**가 제공한다. 이 모델은 가스고정 한 시간 step으로 한정되며, Bianchi photon q-label/angle은 이 계산에서 변경하지 않는다.

## 2. Exact-real sharp extremum lemma

각 q energy bin의 **실제 support**를 `a≤E≤b`, 현재 광자분포를 양의 Borel measure `dμ`, `N=∫dμ>0`, `m=∫E dμ/N∈[a,b]`라고 하자. 임의의 bounded measurable response `g(E)`에 대해 (단절점 one-sided limit에서 극값의 infimum/supremum을 허용):

```
N * conv_[a,b] g(m) <= ∫ g(E) dμ(E) <= N * conc_[a,b] g(m).
```

`conv g`는 g의 최대 convex minorant, `conc g`는 최소 concave majorant다. 일반화 moment 집합이 확률·평균이라는 2개의 affine constraint를 가진 양의 측도 집합이므로, 극단값은 최대 2개의 에너지에 지지된 분포로 접근할 수 있다. 2점 분포는 특정 source shape 가정이 아니다. 비열평형 hardening, age mix에도 현재 `N,U`와 참된 support만 충분하다. 이 오래 알려진 moment extremum 원리의 새로운 수학적 최초성을 주장하지 않는다. 비교 문헌: Winkler 1988 `doi:10.1287/MOOR.13.4.581`, Pinelis 2016 `doi:10.1007/s00186-015-0530-0`.

특히 photo fit cutoff `χ∈(a,b)`의 active fraction을 g=1_(E≥χ)로 쓰면, 불연속점에서 inf/sup 형식으로

```
max(0,(m-χ)/(b-χ)) <= P(E≥χ) <= min(1,(m-a)/(χ-a)).
```

**예:** support [24,25.1]eV, mean24.55eV, χ_HeI24.59eV면 `P_HeI,active∈[0,0.93220338983051]`. 같은 평균에너지를 갖는 전자기복사 분포에 실제 HeI-active photon의 비율이 크게 다를 수 있다. `δ_24.55`의 HeI event는 0, `0.5δ_24+0.5δ_25.1`의 HeI event는 양이다. 원 C6의 국소 source 정확도와 *무조건적* spectral-hardening 오차증명은 다르다.

## 3. 실제 구현: threshold-split piecewise envelopes

종별 one-step fixed-neutral response는 `q_i(E)=Δt*c*n_i σ_i(E)`, `Q=Σq_i≥0`, `h(Q)=∫_0^1 exp(-uQ)du`, `p_i=q_i h(Q)`, `g_heat,i=(E-χ_i,binding)p_i`다. 따라서 정확히 `p_i''=q_i''h+2q_i'h'Q'+q_i(h''Q'^2+h'Q'')`이고, 모든 Q≥0에 대해 `|h|≤1`, `|h'|≤1/2`, `|h''|≤1/3`. 기존 C9 `second_sigma_up`에서 **85자리 Decimal 방향성 상계** `(σ_i^#,|σ_i'|^#,|σ_i''|^#)`를 가져와

```
B0_i=dt*c*n_i σ_i^#, B1_i=dt*c*n_i |σ_i'|^#,
B2_i=dt*c*n_i |σ_i''|^#,  T1=Σ B1_i, T2=Σ B2_i,
|p_i'| <= B1_i+B0_i*T1/2,
|p_i''| <= B2_i+B1_i*T1+B0_i*(T1²/3+T2/2),
|g_heat,i''| <=2|p_i'|+(b-χ_i,binding)|p_i''|.
```

각 smooth cutoff-free subinterval 길이 δ에서의 linear-interpolant error는 `M δ²/8` 이하. `24.59-`, `24.59+` 등 **같은 x인 별도 노드**를 넣어 cutoff jump를 절대로 연속 PL로 잇지 않는다. mpmath.iv 55dps의 실제 f64 dyadic input interval response를 outward binary64로 보낸 뒤, 각 segment error로 upper/lower nodal polyline을 만든다. **Float로 hull slope를 판정하지 않고** Fraction으로 정확한 lower-convex/upper-concave hull을 구성하고, 현재 `U/N`, 실물 R, 전체 q bin 합산도 Fraction을 사용한 뒤 float endpoint만 다시 바깥으로 반올림한다.

이 방식은 actual source shape를 복원한 것이 아니다. 모델-조건부 exact-real sharp theorem의 보수적인 수치 outer enclosure다. `ShapeFreeTemplate.vector_preview`는 미분계수 계산·정확한 합산 없이 NumPy로 여러 moment를 읽는 **빠른 비인증 preview**이며, 생산 판정은 Fraction 경로만 이용한다.

## 4. 실제 source/numeric 결과

초기 source consistency fixture는 실제 C10의 positive split GL8 native48 source fractions로 `N,U`를 만든다. Original owner C5 z20 proper gas `(0.0017575700008892194,0.0001429214010766023,0) cm^-3`, `dt=1e10s`, total source count `4.298036114764196e-8/H`, qmax433eV. 각 현재 q-bin의 `N,U`와 support만 쓰고 **그 내부의 BB50K shape를 잊은 상태**의 envelope 결과:

| nE | HeI event lower | actual initial-source event | upper | half-width / actual |
|---:|---:|---:|---:|---:|
|64|2.43783364e-10|1.4281834584e-9|2.84901161e-9|91.21%|
|128|1.12627292e-9|1.4281834584e-9|1.79955404e-9|23.57%|
|256|1.34250533e-9|1.4281834584e-9|1.53671179e-9|6.80%|
|512|1.39411458e-9|1.4281834584e-9|1.46479508e-9|2.47%|
|1024|1.41437031e-9|1.4281834584e-9|1.43821341e-9|0.835%|

단위 photons per original H. nE256에서 진짜 HeI direct heat `6.87374780362e-9 eV/H`, shape-free 허용구간 `[6.53850321737e-9,7.21119198480e-9] eV/H`다. Actual source 관측값은 모든 H/He event 및 species heat envelope에 포함된다. 상계는 2-moment 보존만 사용하므로 owner C6의 현재 source-conditioned relative error `1.8e-7`이 **추후 스펙트럼에 적용할 수 있는 무조건적 보장값은 아님**을 명확히 나타낸다.

**분포가 실제로 바뀐 추가 시험:** 서로 다른 방출시각의 `R_birth=(.98,1)` 두 source family를 동일 q-bin에 더하고 오래된 photon만 `R_pre=.99,dt_pre=2e9s`·proper gas `(0.001,.00012,.00001)`에서 먼저 감쇠. `R_now=.97`에서 다른 proper gas `(.0008,.00009,.000005)`, `dt=4e9s`를 사용. 이제 원 stellar BB 분포는 참이 아니다. 직접 sparse packet oracle HeI event `4.10161823916e-10/H` vs shape-free `[3.94669559753e-10,4.13076740193e-10]/H`; HI, HeII event와 세 종별 heat도 모두 포함된다. 이는 원 owner 실제 two-epoch geometry가 아니라 **선언된 두-age manufactured source**이며, 적분 shape를 다시 BB로 강제하지 않았다.

## 5. 실제 코드·테스트·성능

- New implementation: `src/moment_envelopes.py`: directed smooth-piece curvature, jump duplication, exact-dyadic convex/concave hull, current N/U+q-support contract, bounded template LRU cache, vectorized preview. `src/parallel_moments.py`: independent q-bin processes with deterministic exact Fraction sum. CLI `src/moment_benchmark.py`, `src/cold_scaling.py`, `src/parallel_benchmark.py`.
- **31 targeted Pytest PASS**: cutoff active exact/edge, convex hull vs independent SciPy linprog, 40 random nonthermal spectra and heat inclusion, real source 64–512, source-age hardening, new gas/clock, invalid support, independent finite-difference derivative diagnostics, two-worker bit-identical output. Older source suites not bulk rerun.
- Actual kernel Wolfram Language15.0.1: 8 scalar exact-zero checks including response second derivative and energy moment. Actual hash-pinned xAct/xTensor1.3.0: 5 tensor zero checks for same ray photon 4-momentum/projectors.
- Local component benchmark nE512 cold process medians 1/2/4 workers `4.744/3.570/2.228 s`, corresponding 4/1 ≈ 2.13×. Each trial launches a clean Python interpreter and parallel outputs are byte-for-byte equal. nE256 medians `2.363/1.826/1.325 s`, 4/1≈1.78×. For 10,000 repeated *same support+neutrals+dt* states, numpy preview ~0.00154s vs exact Fraction readout ~1.1597s ≈752×, **but preview is not a scientific certificate**. Real CPU/OS details in final workstation receipt when rerun.
- Main proof and algorithms are existing generalized-moment convex-envelope/positive FV ideas specialized to C6 input. No first-ever or global Bianchi solver theorem is claimed; atomic experimental uncertainty and full source/gas/chemistry/geometry coupling are not included.

## 6. Owner integration and NEXT

This is a **read-only supplier** for `rei_bianchi` C7 A and B. Require actual per-ray current N/U/ref-q edges, proper now clock, physical ratio R and proper gas state; no new source Jacobian; apply envelope over *true* support and bind each q angular lane separately, never average unrelated rays or ages before geometric mapping. A second-age mix within the same genuine q-direction is permitted since first two moments remain additive, and false above-threshold responses are prohibited if true support lies below the fit cutoff. Only optional monitor/diagnostic until numerical variant/source identity is separately accepted.

Latest owner already has positive C6 entropy closure; **do not reimplement/overwrite** it or replay source histories. Next local research is to use measured per-cell width to construct adaptive q-bin refinement/error-budget triggers and only then assess SOURCE07 C7 multiple-epoch coupled gas/temperature feasibility. BASS_CR Landau fine constitutive/adjoint remains independent unfinished lane. native_subagent NOT_RUN (host does not expose it); standalone direct Python/CAS work, no local Codex.

Primary comparisons: Winkler, *Extreme points of moment sets* (1988, DOI `10.1287/MOOR.13.4.581`); Pinelis, *On the extreme points of moment sets* (2016, DOI `10.1007/s00186-015-0530-0`); Mirocha et al.(2012) arXiv:1204.1944; Baumschlager et al.(2024) arXiv:2310.16902. These are contextual references, no outside paper numerical constants were substituted.
