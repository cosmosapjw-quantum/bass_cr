# BASS-CR CR_FERRERS_DUAL_ORACLE_V1 | 이론→코딩 연구 결과

## Scope / authority

Independent child of Draft PR124 frozen HEAD `a6b49b352fed31587955d55b1cad30c0b55a81eb`, original NPZ SHA256 `1c974c306b50f3deb86df712844f753b4402fb25e5dbc41c9a1de0254bf3ff47`. PR124 SOURCES and parent PR123 preserved byte-for-byte. BASS-CR mathematical HL allocation only; no physical event rate normalization. Existing central DAG 28/88 and extension 0/3 unchanged; PR124 auxiliary 1/1 remains HOLD.

## Observed actual bottleneck and remedy

PR124 `prefix_bridge.py` allocated a list of all admissible HL original edges (102831) and scanned all of them using Python `Fraction` once per requested budget, despite the exact prefix-compressed network. In each fixed low birth-bin, the high-admissible lows are an exact energy prefix and the dual cost coefficient is bin-constant. Theorem in `THEORY_DUAL_PREFIX_KO.md` shows exact equivalence to the minimum low-price in each nonempty prefix. The new `prefix_dual_oracle.py` precomputes original high/bin cutoff, exact logical original-edge count and grouped queries once, and checks prefix minima per budget. `prefix_bridge.py` integrates `dual_check='prefix_exact'` as an opt-in; default stays `dual_check='explicit'` pending genuine review. Primal certificates, C++20 binary and source parser are untouched.

## Tests actually executed in this research session

- C++20 original `prefix_ssp.cpp`: g++ 14.2.0, `-O2 -std=c++20 -Wall -Wextra -Werror` build success.
- Python `test_prefix` + new `test_prefix_dual`: **9/9 normal PASS** and **9/9 `python -O` PASS**, exit0; separate `compileall` PASS.
- New random dual predicate oracle 300 seeded exact-rational instances; failure case provides an original allowed `(h,l)` witness. Input modes invalid/duplicate-energy/zero-mass tested.
- Wolfram exact-rational predicate equivalence 1000 deterministic cases, 1000/1000 agreement; proof independent of testing.
- Locked original 3201 atom, K=3 eV, 3 budgets `c=0,R/2,R`, **three sequential paired comparisons with order explicit→prefix, prefix→explicit, explicit→prefix**. Each pair matched exact `M, C, dmax, lambda, price for every original atom, high-labelled positive flow, cpp_stats, logical edge count 102831, zero primal-dual gap`.

## Actual per-pair wall seconds, current host

| Trial | Literal original edges | Exact prefix | Order |
|---:|---:|---:|---|
|1|13.599408|0.256522|explicit→prefix|
|2|13.630405|0.285190|prefix→explicit|
|3|12.990086|0.234679|explicit→prefix|

Medians 13.599408 s and 0.256522 s; **ratio of medians 53.01452x**, **n=3**, same 3201-atom source and budget/objective/certification semantics but different exact logical verifier algorithm. 102831 original edges collapse to **1067** high-bin prefix inequalities per budget; this 96.3739x *constraint-count* reduction is not a physical rate or generic wall-time bound. In the first pair, isolated original-edge dual-only check was about 1.6s per budget versus about 2.4ms per budget in the prefix oracle (ratio of median of those three-budget checks ≈673.42x); original overall time also includes constructing a 102831-pair list and large exact Fraction checks. No significance test, untested memory ceiling, no production claim.

**Resource exception:** optional `tracemalloc` instrumentation covering the old 102831-edge generator timed out under the session 55-second execution bound; marked EXECUTION_FAILED for the diagnostic, not mathematical or code-test failure. It was not blindly repeated. Memory gain remains **theoretically expected**, not empirically validated. Historical PR118 CPU resource FAIL and full aggregate cap NOT_CERTIFIED remain.

## Hostile audit / precise gate

- **P0 future invalidation:** new edge support not representable as same `E_h+E_l<=K` prefix or per-bin constant chi; reject opt-in certification until model-specific theorem refreshed.
- **P1 pending:** genuinely independent R06 mathematical and C09 code-author audits; no distinct-author receipt. Source provenance of exclusive He kernel/physical K/clock/normalizer/energy ownership/stop remains missing.
- **P2:** dedicated process memory measurement, duplicate/missing malformed source fuzz and broader bins/scale stress may be useful, but not a production-blocking new physics claim.
- **P3:** plot and benchmark narrative polish.

The performance ratio is scoped to the current host and source; disable `prefix_exact` on uncertain new cost/edge semantics. Legacy `explicit` mode remains available as an independent reference. No main/PR124/PR123 mutation, no source NPZ modification, no physical native25/L4.

## Publication / recovery status

This report describes locally executed calculations. Exact Git/Drive/Dropbox publication receipts must be appended after actual provider readback; file names or planned backups are **not** upload verification. New staged R/C JSONs are retrospective records of this finished experiment unless a later provider truly receives an individual contemporaneous file. No fictitious independent R06 or C09 author.
