# BASS_CR C9/R5: 보존형 광자 압축의 2차 곡률 상계, 고정 source 시험 및 병렬 경량화

**2026-10-15 KST.** 부모 `cosmosapjw-quantum/bass_cr` PR #67 head `5c6ea6ceb1cffb05f482bc0437b4e5eb2b2a13d9`. 연구 선택: 열린 `C9_DIRECTED_RATE_AND_CURVATURE`의 실제 코드 구현·과학 검산과 이론 R5 국소 유도. 이전 PR64/62의 Landau continuum 인증과 CR 원자/finite-rate 순간 편입을 변경하지 않는다. Native subagents NOT_RUN; Codex는 이번 연구에 사용하지 않음. 사용자 Ubuntu 워크스테이션과 ChatGPT 격리된 컨테이너에서 직접 실행했다.

## 핵심 판정

기존 PR67의 first-derivative Verner frozen-neutral BE event/heat upper bounds를 유지하면서, **같은-ray/같은-owner two-cohort mean-energy merge의 선형항이 정확히 상쇄한다**는 사실을 이용해 더 작은 second-order 충분 상계를 새로 구현했다. `src/curvature_bounds.py`는 float 계산 경로, `src/directed_curvature.py`는 원본 IEEE754 binary64 입력을 정확한 이진 유리값으로 받아 Decimal85의 방향성 반올림 및 최종 binary64 상향 nextafter를 수행하는 검산 경로다. 후자는 각 정수/양의 유리 연산을 ceiling/floor로 묶고 Python Decimal의 올바르게 반올림되는 exp/ln/sqrt 결과를 추가 next_plus/minus로 에워싼다. 수학적 충분 상계의 유한 정밀 평가를 지향하지만, 측정된 원자 물리계수의 불확실도, 전체 비선형 gas/RT, 실제 q-ray source/Jacobian을 포괄하는 global certificate는 아니다.

**소스 스코프**: 기존 50,000K truncated MD14 source `frozen_source(16)` (48 source energy centroids, total number=1/H, E initially 13.6..100eV), proper `dt=10^9 s`, `rho(HI/HeI/HeII)=(10^-3,8×10^-5,2×10^-5) cm^-3`, all-ray multiplicative redshift `r∈[.995,1]`, per-species BE events budget `.01 count/H`, photoelectron direct heat budget `1 eV/H`. Atomic fit cutoffs H I13.60/He I24.59/He II54.42 eV; physical binding energies `13.598434599702/24.587389011/54.41776 eV` are separate and selectable, *not* numericalized away. Units eV, proper seconds, photon count/H, cm^-3, c=29979245800 cm/s, signature(-,+,+,+). These densities and dt are a declared controlled fixture and **not extracted from an actual accepted rei_bianchi gas state**.

| Source n16 goal | PR67 first-order bound | New curvature Decimal85 (same budgets) |
|:--:|:--:|:--:|
| 32 cohorts | PASS | PASS |
| 26 cohorts | PASS | PASS |
| 24 cohorts | HOLD | PASS |
| 22 cohorts | HOLD | **PASS** |
| 20 cohorts | HOLD | HOLD |

The `22` case reduces original stored cohort count by **54.17%**, and by **15.38%** versus the best admitted `26` with identical budgets. This is a **source-cohort memory count comparison**, not a production q-grid speed/physics accuracy result. The first-order and second-order upper bounds are **different sufficient bounding strategies**; do not interpret their ratio as measured physical error.

## 1. Exact source-bound mathematics

For a pair `(E1,n1),(E2,n2)` of positive photons in *one identical physical ray/source-age/clock owner lane*, define `N=n1+n2`, `Ebar=(n1E1+n2E2)/N`. Fit cross-section sigma_k(E) is Verner et al. outer-shell fit with a species-dependent *zero to positive jump* at a fit cutoff E_fit,k. For a fixed proper neutral density n_neutral,k and time h define

\[
\beta_k(E)=h c n_{k}\sigma_k(E),\quad D(E)=1+\sum_j\beta_j(E),\quad P_k(E)=\frac{\beta_k(E)}{D(E)},\qquad Q_k(E)=(E-\chi_{k,\rm bind})P_k(E).
\]

These are the species photon events and direct photoelectron heat per incident photon for the **backward-Euler frozen-neutral one-step** comparison. Only readout source; no gas coupling or propagation time quadrature.

Given any `r in [rmin,1]`, if `rmin*E1>=13.6eV` and no species fit threshold belongs to `(rmin E1,E2]`, every active `P_k,Q_k` is `C²` on the relevant full energy tube (zero for inactive species). Positivity of n1,n2 gives exact cancellation of first derivatives at r Ebar:

\[
\sum_{i=1}^2 n_i(rE_i-r\bar E)=0,\qquad
\sum_i n_i(rE_i-r\bar E)^2=r^2\frac{n_1n_2}{N}(E_2-E_1)^2.
\]

Taylor with integral remainder and `r²<=1` then establishes

\[
\left|\sum_i n_i g(rE_i)-Ng(r\bar E)\right|
\le\frac12\frac{n_1n_2}{N}(E_2-E_1)^2\sup_{E\in[r_{min}E_1,E_2]}|g''(E)|,
\quad g=P_k\ \text{or}\ Q_k.
\tag{C9.1}
\]

Threshold-crossing *full tube* causes explicit `CompressionHold`; no attempt to apply `C²` across a Verner jump. This remains true even if a currently absent neutral species has density0, since future conditions can activate it.

## 2. Verner curvature and BE quotient bounds

With `x=E/e0-y0`, `y=sqrt(x²+y1²)`, `a=(x-1)²+yw²`, `z=sqrt(y/ya)`, `v=p/2-11/2`,

\[
\sigma(E)=10^{-18}\sigma_0 a y^v(1+z)^{-p}\;\mathrm{cm}^2,
\qquad \ell_1=\frac{d\ln\sigma}{dE}=\frac1{e_0}\left[\frac{2(x-1)}a+v\frac{x}{y^2}-\frac p2\frac{xz}{y^2(1+z)}\right].
\]

Then

\[
\ell_2=\frac{d^2\ln\sigma}{dE^2}
=\frac1{e_0^2}\left[\frac2a-\frac{4(x-1)^2}{a^2}+v\frac{y_1^2-x^2}{y^4}
-\frac p2\left(\frac{(y_1^2-x^2)z}{y^4(1+z)}+\frac{x^2z}{2y^4(1+z)^2}\right)\right],
\quad \sigma''=\sigma(\ell_1^2+\ell_2).
\tag{C9.2}
\]

The verified code constructs *supremum upper bounds* `S0,S1,S2` across a smooth full tube using the endpoint max |x|, min distance to x=0 and x=1, positive y_min and a_min, plus `z/(1+z)<=1`, `z/(1+z)^2<=1/4`. It uses sigma<=sigma0*a_max*y^v and `S1<=S0 L1, S2<=S0(L1²+L2)` with separate sign-aware negative exponent. The formulas are source fit, not fitted from a few samples. Actual independent mpmath70 derivative checks sampled interior points on 6 regimes and Wolfram15 symbolic checks differentiated C9.2.

Set `B_j,k=h c n_k S_j,k`, `T_j=sum_k B_j,k` for j=0,1,2. The `D>=1`, `β_k>=0` inequalities imply

\[
\sup |P'_k|\le B_{1,k}+B_{0,k}T_1=M_{1,k},\qquad
\sup|P''_k|\le B_{2,k}+2B_{1,k}T_1+B_{0,k}T_2+2B_{0,k}T_1^2=M_{2,k}.
\]

The separate binding energy matters for direct heat:

\[
\sup|Q_k''|\le 2M_{1,k}+(E_{max}-\chi_{k,\rm bind})M_{2,k}.
\tag{C9.3}
\]

The fit cutoff and binding constants are **not** interchangeable; original `frozen_be_readout` fixture used fit cutoffs for its direct heat readout, while `frozen_be_readout_binding` and the physical-binding test use the proper IGM source bookkeeping constants. Fit sigma and binding energy remain separately source-locked.

## 3. Directed arithmetic and numerical admission

`src/directed_curvature.py` encloses each positive analytical expression using `Decimal.from_float` input **binary64 dyadic identity**. For every critical addition, multiplication, denominator and subtraction, use 85-digit ROUND_CEILING/FLOOR; use `next_plus/next_minus` around decimal transcendental rounding; round each final positive bound up to adjacent binary64. The zero branch remains zero. The heap overrides cumulative bound arithmetic to add upwards after each merge, including pre-admission budget tests. The Verner `(species, E_low, E_high)` envelope is cached in bounded `lru_cache(maxsize=4096)` independent of density, allowing reuse across ray lanes. The independent physical binding vector is preserved in `inject_and_compress` and never reset to fit cutoffs by a new object constructor.

The actual `22` certificate with owner physical binding (`H/HeI/HeII`) and high-precision upper evaluation is in `results/CURVATURE_BENCHMARK.json`; the earlier fit-cutoff comparison is separate. One-step rate and heat errors against direct `frozen_be_readout` are sampled at r=1,.999,.997,.995 and tested under every bound. This is **an exact-real sufficient local bound evaluated to directed numerical accuracy**, not a posteriori interval enclosure of a coupled cosmological IVP. No uncertainty envelope for Verner atomic fit coefficients/approximations has been applied. The output `HOLD` at target 20 remains genuine; the code does not silently increase user-specified error budget.

## 4. Optimization and real scientific run

The original heap algorithm uses O(N log N) local candidate updates, preserving original deterministic tie ranking and transaction rollback. The new curvature kernel adds more expensive scalar bounds but saves stored packets at *the same* local error budget. On the same system, float curvature is faster than Decimal85; Decimal caching makes many same-grid rays feasible. Standalone `src/curvature_scaling.py` runs independent physical ray lanes using ProcessPoolExecutor (not subagents). At 32 independent frozen-neutral lanes, it measured a speedup from multiple processes when task duration was sufficient, with **bitwise-identical per-ray outputs**. These independent lanes are not the SOURCE07 owner q-ray geometry; they do not import a source Jacobian or fuse angular/source-age lanes. Exact measured timings are in `results/PARALLEL_SCALING.json`.

Latest owner source inspected by remote Desktop from actual `rei_bianchi` head `129627969dae18958ceef520c197bfa8b20b8888` (2026-10-15 KST). SOURCE07 C4 has already selected *fixed reference q-energy×angle grid* primary and a directional cohort cap diagnostic. It explicitly demonstrates a cross-epoch q-direction energy deficit when naively compressing different emission epochs. Therefore this `bass_cr` scalar response compressor **is a supplier for same-ray local rate-error control**, not a new owner primary representation, full directional momentum certificate or reason to defer CR-OFF abundance history. BASS_HE PR59 warm P01 third interval and WU088_HH PR74 screened atom work are different physics and not transplanted as source inputs.

## 5. Scope and next

No original `rei_bianchi` executable, source, state, DAG, accepted history, scheduler, or running Codex session was changed; the user requested work here with no Codex use. Native subagents `NOT_RUN` (not exposed by current chat runtime). Future scoped tasks are: (i) same-ray/source-age real SOURCE07 packet producer input test under *owner-approved source identity* and proper neutral histories; (ii) source interval/dyadic error audit of Verner high-energy thresholds; (iii) controlled q-grid/one-step native comparison, then actual coupling errors if separately authorized; (iv) separate `bass_cr` Landau fine continuum adjoint. The existing PR62 coarse kinetic C-temperature interval and PR64 signed tail traces remain untouched.

**Literature comparator**: Mirocha et al. (2012), DOI10.1088/0004-637X/756/1/94, https://arxiv.org/abs/1204.1944, and Baumschlager et al. (2024), A&A DOI10.1051/0004-6361/202348164, on reaction-sensitive spectral discretization. No published numerical error constants were transferred into the local result.
