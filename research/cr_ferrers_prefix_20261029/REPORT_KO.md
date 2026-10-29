# BASS-CR exact Ferrers prefix network: 이론→코딩 실증 결과

**Unit:** `CR_FERRERS_PREFIX_EXACT_V1` · **Parent:** Draft PR123 `9f520c5e4042cb15bbd55da14ef946d6d9960d97` · **scope:** 조건부 유한 HL event allocation (physical rate 아님). Source-locked original 3,201-atom NPZ SHA256 `1c974c306b50f3deb86df712844f753b4402fb25e5dbc41c9a1de0254bf3ff47`.

## Executive scientific finding

에너지 제약 `E_h+E_l<=K`가 각 low birth-bin의 에너지 정렬 순서에서 high별 prefix를 형성함을 이용했다. prefix에 대한 canonical segment-tree covering으로 비용 0(same-bin)/1(cross-bin)의 exact min-cost-flow extended formulation을 구성했다. `m, C, dmax`와 원래 원자별 primal/dual 제약을 수학적으로 보존한다. C++20 signed-i128 potentials-Dijkstra SSP, energy/bin 정렬 Python Fraction 입력·출력 consumer 및 top-down high-label 유량분해를 실제 구현했다.

원본 K=3eV 조건부 source의 2,748 high 중 2,295는 양의 허용 low 이웃이 없어 exact pruning 가능하다. 453 active high, 453 low, 102,831 original HL admissible edges를 4,307 forward arcs/1,358 vertices로 표현했다(arc 23.8753배 압축). 이 arc 수치가 메모리나 wall-time의 23.9배 향상을 뜻하지는 않는다.

## Same-source, same-budget verification

- **Primal and dual:** c=0, R/2, R 세 budget에서 기존 PR123의 정확 rational `M(c)`/`dmax(c)`와 완전 일치. 세 budget 각각 3,201원자 marginal·positivity·cost·102,831 original original edge dual inequalities·objective gap=0. c=0 / R/2 / R의 positive pair 수는 새 경로에서 각각 308/485/797. 이는 같은 최적값을 주는 다른 primal witness를 허용한다.
- **Independent small oracle:** 75 seeded 2–6 atom random full-event LP, 10-atom multi-kink, off-bin/zero-mass/duplicate/fractional 1/3 budgets, 6 test methods normal/6 `python -O`/6 UBSan-backed. First red tests two findings: invalid float K의 예외 클래스 충돌 및 predecessor small SymPy dual가 일부 유효 instance에서 불필요하게 미인증됨. 새 경로는 float 예외를 명확히 하였고 다른 primal oracle + 자체 원본 그래프 dual 인증으로 경로를 분리했다. Old reference 증명서 취약성은 원 코드 수정 없이 기록.
- **Wolfram exact:** 독립 18-edge 10-atom LP의 c=0,1,3/2,2,5/2,3,4에서 M=5,6,13/2,27/4,7,43/6,15/2를 모두 확인.
- **Adversarial full-size bin recoloring:** 원래 E_i와 w_i 바이트는 그대로 두고 오직 bins를 `(7*i+int(10 E_i)) mod 5`로 바꾼 합성/비물리 대조군. 9,774 forward arcs/1,356 vertices, 세 budget 각각 102,831 원본 dual 검사와 gap=0; 값은 원래 물리 bin 해석이 아님.

## Actual 3 paired same-host performance readings

동일 Python3.13/C++20 -O2, 같은 원본 3,201 marginal, 동일 세 예산, 같은 original-edge 102,831 exact certificate 검증과 stdout witness decoding을 모두 포함한 end-to-end wall time. 순서 1 prefix-first, 순서 2 parent-first, 순서 3 prefix-first. **Measured, not analytically guaranteed:**

| paired run | original PR123 graph | prefix DAG |
|---:|---:|---:|
| 1 | 18.83913 s | 16.47199 s |
| 2 | 20.68954 s | 15.70707 s |
| 3 | 18.84499 s | 16.97601 s |

Medians: parent 18.84499 s, prefix 16.47199 s; ratio of medians **1.14406**. Parent final Dijkstra pop count 5,827,053, prefix 1,396,409; final augmentations 1,818 vs 1,027. Benefit from network compression is partly offset by segment-node overhead, exact witness decomposition and full original-edge validation. Median wall-time ratio is a **workload-specific observation with n=3**, no significance claim, no production rate prediction. 원래 PR123의 과거 16.338초와는 서로 다른 실행을 혼용하지 않는다. First paired benchmark wrapper was interrupted after parent trial2, which was preserved; the missing prefix trial was run separately, unmetered timeout not conflated with mathematical failure.

## Audit/admission

- **Derived**: exact prefix network equivalence with cost conservation, high-label disaggregation, original budget LP primal/dual mapping. Standard segment-tree range-edge idea/SSP is prior art, no generic algorithm novelty claim.
- **Implementation verified (scoped)**: C++ compile `-Werror`, 6/6 normal+6/6 optimized+6/6 UBSan small tests, original source 3 rational budget checks, 5-bin synthetic 3201 tests.
- **Blocked/held**: genuine distinct-author R6/C9 not run (native delegation unexposed); entire source original full physics, same-physics production benchmark, physical exclusive He event kernel, actual physical K/clock/energy partner/stop, L4/native25 remain HOLD. Historical PR118 CPU resource FAIL and current aggregate cap not certified. No main merge, no parent mutation.
- **DAG**: central 28/88 delta0, extension 0/3 first partial; new auxiliary compressed reference 1/1 scoped, reviewer HOLD; R/C 18/20. Per-stage Git/Drive records, when published, are post-computation retrospective checkpoints rather than contemporaneous scientific-execution captures.

## Literature references

Király & Kovács, *Efficient implementations of minimum-cost flow algorithms*, 2012 https://arxiv.org/abs/1207.6381 (algorithmic prior art). Ghiyasvand, *Solving the parametric bipartite maximum flow problem in unbalanced and closure bipartite graphs*, 2015 https://doi.org/10.1007/s10479-015-1807-7 (different objective/model). Switzer & Hirata, *Primordial helium recombination II: two-photon processes*, 2008 https://arxiv.org/abs/astro-ph/0702144 (physical candidate only, **not** source-qualified for this mathematical He pair event input).
