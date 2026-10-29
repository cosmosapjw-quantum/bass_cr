# bass_cr: 2026-10-29 generic potentials 연구·코딩 사이클

## 결론

`CR_GENERIC_POTENTIALS_EXACT_V1`은 PR121의 기존 exact Fraction/Bellman–Ford small reference를 사용해 새로운 독립 C++20 exact scaled-integral potentials–Dijkstra SSP + Python Fraction certificate consumer를 구성했다. **원본 3,201개 He conditional marginal과 원래 admissible 102,831 edges를 사용해 c=0,R/2,R의 세 primal-dual optimum을 현재 세션에서 정확 유리수로 재현했다.** 앞선 K3 특화 native는 같은 3 budget을 합계 8.58초에 처리해 여전히 더 빠르므로 **속도 향상 주장은 하지 않는다**. 새로운 경로는 arbitrary-bin 수학을 K3 원본 크기까지 확장한 별도 구조적 구현이며, physical exclusive He event kernel 또는 full native25는 아니다.

## Source/authority

- PR121 HEAD `6c3c91f9fd6261b6d79383ef7c5c8de7b6004fb6` 최신 조회 및 root AGENTS.md 읽음. Parent branch와 main 불변.
- Parent original NPZ SHA256 `1c974c306b50f3deb86df712844f753b4402fb25e5dbc41c9a1de0254bf3ff47`. The recovered immutable SOURCE ZIP SHA256 `12c406744b9b33632ba2cdfaf0afa63da50d2f29bc452f939ddad3ad01a3a566`.
- Latest related refs inspected on 2026-10-29: BASS #243 CE1-G positive-ray cap audit; BASS_HE #106/#107 330/213 MeV photodisintegration/DD reciprocity (nuclear, not atomic He recombination); REC #156 HD radiative-frequency local energy ledger; REI #263 conditional UVB/τ source jet; WU088_HH #157/#158 HD chemistry nominal 105K with owner HOLD; vigilode #106 original-residual preconditioned GMRES. Neither supplies source-qualified CR exclusive atomic He event kernel or physical K.
- Previous reported R6 and C9 distinct author review remain `NOT_RUN`; this model's own proof/code inspection is not a separate author.

## Theory result

The two-tier exactness is intentional: all dyadic marginal masses are integer scaled, with path/cost/potential arithmetic exact in signed i128; a budget inside a marginal-cost segment is interpolated as an exact rational flow rather than rounded. In a residual circulation with return arc t→s of cost -k, global exact shortest-distance potentials produce original vertex prices p_h,p_l and λ=1/k; an independent consumer checks the LP dual against all original (including zero-mass) admissible edges. A saturated maxflow recovers λ=0 by a reachable mincut. Proof and assumptions in `THEORY_KO.md`.

## Actual coding evidence

- C++20 optimized `-Wall -Wextra -Werror`: PASS. Runtime environment `PYTHON_PASS` and available g++ 14.2.0.
- Scoped C++ UBSan one nondyadic case PASS; new 6/6 tests also PASS with `python -O`. A full 22-test optimized combined command hit the current tool execution timeout and is **not** claimed as PASS (new 6/6 separately verified, parent 16/16 original unoptimized current).
- New unit tests 6/6 methods, 75 random synthetic full-event exact LP comparisons and 8 multipoint 10-atom references PASS; parent existing native/generic 16/16 PASS on original source tree.
- Independent Wolfram exact 18-edge 10-atom LP seven budgets: `{5,6,13/2,27/4,7,43/6,15/2}` PASS.
- 3 original source budgets: all exact M,d,capacity,102831 edge dual constraints and gaps 0 PASS. Different valid matching patterns are not byte-identical to the special-case greedy witness.
- Wall time per generic budget 22.13/30.61/18.93 s (c0/R2/R), peak process RSS recorded 114476/114576/114580 KiB, path augmentations 797/1055/1819. Special native Python all three in one call 8.58 s, maxrss101012 KiB. Not an apples-to-apples generic speedup; grouped vs per-budget solve, actual source/path both pinned.
- First negative test: fractional path reported cost numerator C*k+r instead of C*k+k*r, producing `PRIMAL_SUM_MISMATCH` at c=2. Code corrected, 83 oracle cases rerun PASS, regression includes c=2 and c=3 in the three-slope fixture.
- Conservative i128 overflow guards; CLI rejects giant capacities; Python input Q lcm exact, never silent float.

## Research-loop stages

The next theory/coding subject was defined as **scalable exact primal-dual witness**, not a claim of solving the physical source. R1 accepted parent contract, R2 independent literature and cross-repo survey, R3 fixed-C vs budget inequality, R4 potentials vs cost scaling alternatives, R5 constructive dual proof, R7 symbolic exact seven-point control, R8 conditional claim decision, R9 computational form, R10 reproducible handoff: **9/10 scoped**; R6 distinct author NOT_RUN. C1 locked original source, C2 equation-code mapping, C3 i128+potentials design, C4 bounded execution, C5 actual code, C6 6 methods + 16 parent, C7 original 3201 exact science, C8 real wall/RSS/augmentations, C10 reproducible package: **9/10 scoped**; C9 distinct author NOT_RUN. The science/engineering deliverable is scoped, but publication/backup stage receipts are separate states and do not become 20 contemporaneous checkpoint claims.

## Figure adversarial read

The plotted 10-atom `M(c)` is concave with slopes 1, 1/2, 1/3 and 0, exact corners c=0,3/2,5/2,4; no negative segment or mismatch. The plot is a source-independent synthetic mathematical counterexample, not an observed He rate. A fixed-C feasible region can contain low-low mixed events not described by upper-budget high-low graph alone.

## Risks and stop

Current CPU aggregate across distinct runs includes unmetered setup/CAS/provider work; **NO aggregate hard-cap PASS** claimed and previous PR118 CPU resource failure is preserved. New current bounded runtime and benchmark evidence do not borrow closed-unit unused budgets. Algorithm still augmentation-sensitive and may be slower than specialized K3, full generic source fixtures at other K/bin labels and cost-scaling not performed at 3201 scale. No heuristic physics source mapping, no donor/partner energy ownership or stopping, no physical native25/L4/production; no main/other-owner mutation.

Canonical **28/88**, extension **0/3**, inherited auxiliary **1/1 scoped**, new scoped engineering **1/1 with independent-review HOLD**, new R/C workflow **18/20**. No central count promotion.
