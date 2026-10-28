# CR_NATIVE_BUDGET_K3_FRONTIER_V1: exact source-bound frontier

**Authority and scope.** This theorem concerns the immutable PR116 PHYS02 He marginal, `ATTRIBUTION_ARRAYS.npz`, SHA-256 `1c974c306b50f3deb86df712844f753b4402fb25e5dbc41c9a1de0254bf3ff47`, with exact IEEE-754 binary64 values lifted to rational numbers, unchanged birth-bin assignments, and conditional **K=3 eV**. It is not a physical cutoff measurement, an exclusive-event kernel, or a recombination/transport calculation. Source owner is `cosmosapjw-quantum/bass_cr`; upstream PR116, PR117, PR118, PR119 remain unmodified.

## Finite event definitions and units

Each atom i has mass `w_i >= 0` in m^-3 s^-2, energy `E_i >= 0` in eV and bin `b_i`. A low atom has `2 E_i <= K`; high has `2 E_i > K`. Permitted unordered double events obey `E_i + E_j <= K`; low diagonals are permitted and consume two units of that low marginal per unit event. High-high double events are impossible under this cap. The source's finite proper history is `q_i(t)=t w_i` for `0<=t<=10^10 s`; `W=int t dt=5*10^19 s^2`. The mathematical cross budget `c>=0` and all event coefficients have units m^-3 s^-2.

Let L=sum of low marginal masses. For high-low matching x_{hl}, define total `m=sum x`, cross-bin coefficient `C=sum_{b_h!=b_l} x`. Let S=max m with all high-low edges constrained to same bin; M=max m with all admissible high-low edges. Let M(c)=max m with C<=c. By the exact full-event reduction from PR119, the maximum total double-event mass is `dmax(c)=(L+M(c))/2` when every low diagonal is allowed. This is a **budget inequality** C<=c, not a fixed-equality C=c joint polygon.

## General upper bound and source-specific attainment

For any feasible high-low x, split m=m_same+m_cross. Since m_same<=S and m_cross<=C<=c, while m<=M, we have `M(c)<=min(S+c,M)`. This upper bound need not be sharp for arbitrary finite sources (the four-atom counterexample in PR119 shows the distinction).

For this exact native K3 source, a *constructive simultaneous primal* exists:

1. For each bin, sort high atoms by descending E and same-bin lows by ascending E; greedily match admissible pairs with exact rational capacities. This yields 315 positive same-bin pairs with sum S and saturates the independent same-bin weighted-Hall min-cut bound.
2. Keep the residual high marginal. Greedily match it against cross-bin lows in ascending E. At K3 all eligible high atoms are in bin 2; all cross lows lie in bins 0 or 1. This yields 526 positive cross-bin pairs of mass R.
3. Exact rational source verification gives `S+R=M`, where M independently equals the unrestricted weighted-Hall min-cut. All 3,201 original atom capacities and all 841 pair-support conditions are satisfied. Thus the combined witness is simultaneously optimal for S and M.
4. For any 0<=c<=R, retain all same-bin pairs and scale every cross-bin pair by theta=c/R. Unused low mass is allocated to allowed low diagonal events `r_l/2`; unused high mass stays single. This preserves all original marginals and realizes `M(c)=S+c` with C=c. For c>=R, retain the full combined witness with C=R<=c and M(c)=M.

Therefore, **for this immutable source and K3 only**,

`M_K3(c)=min(S+c,M)` and `dmax_K3(c)=(L+min(S+c,M))/2` for all c>=0.

## Exact dual certificates for all c

For any high-low graph, the LP dual is

`min sum_h w_h p_h + sum_l w_l p_l + c lambda`, subject to
`p_h,p_l,lambda>=0`, and `p_h+p_l+lambda 1[b_h!=b_l]>=1` for every admissible high-low edge.

Let `(p^S_h,p^S_l)` be the exact 0/1 weighted-Hall vertex-cover dual for the same-bin graph. For `c<R`, choosing lambda=1 covers all cross-bin edges, and the dual objective is S+c, matching the scaled primal. For `c>=R`, choose the unrestricted 0/1 Hall cover `(p^M_h,p^M_l)` and lambda=0; its objective is M, matching the full primal. Thus primal-dual gap is identically zero at every budget, not merely at selected grid points. At c=R both choices are optimal. Zero-mass atoms must be assigned free dual prices if needed to cover original-graph edges; the Python reference handles this explicitly.

The native exact Hall thresholds are:

- same-bin active bin2 high threshold `2254790485312799/1125899906842624` eV, cover counts 162 high and 0 low;
- unrestricted high threshold `6529867615966331/2251799813685248` eV, cover counts 452 high and 1 low.

These cuts are source-specific certificates, not universal constants.

## Exact values and conditional bookkeeping

```
N = 77906149556394634457/49039857307708443467467104868809893875799651909875269632
L = 999870389230360121/3064991081731777716716694054300618367237478244367204352
S = 323478918562118325/3064991081731777716716694054300618367237478244367204352
M = 3456415883490050789/12259964326927110866866776217202473468949912977468817408
R = M-S = 2162500209241577489/12259964326927110866866776217202473468949912977468817408
R/N = 0.11103104037640514
(dmax(0))/N = 0.1358916404240498
(dmax(R))/N = 0.19140716061225238
```

All N,L,S,M,R are coefficients in m^-3 s^-2. Multiplying by W gives finite-window event densities in m^-3. The PR116 conditional chemical energy bookkeeping `W [ (24.59 eV) N + (29.83 eV) d ]` admits this dmax(c) as an upper bound, but it does **not** identify heat, retained photons, RR, stopping, donor work or actual He recombination rates. Actual physical K, exclusive kernel, EOS/T, full native25 and production/L4 remain unknown or held.

## Evidence and scope of verification

A fresh Wolfram remote kernel read the pinned public GitHub NPZ (HTTP 200), verified original file SHA-256, decoded the two `.npy` float64 arrays **bit-exactly** as rationals, reconstructed 3,201 atoms and bin labels, recomputed S and M with independent greedy/Hall routines, and checked all 3,201 marginal capacities and all 841 pair supports. Exact primal-dual equalities and source SHA passed. This is a second engine, **not a distinct-author blind review**.

A separate Python 3.13.5/SymPy 1.14.0 source-locked reference implements the same construction with explicit 0/1 Hall duals and all original-atom witnesses; ten local tests, including 48 independent full-event LP comparisons and a synthetic 3,201-atom topology, pass. The original NPZ is **not locally mounted**, so the Python implementation has not been run against its native bytes. No numerical comparison between the two implementations on identical native bytes is claimed.

Relevant literature: classical weighted Hall/max-flow duality; S. Kapoor and M. Sarwat, *The Budgeted Transportation Problem* (arXiv:1302.5871), related but not identical optimization; Switzer & Hirata, Phys. Rev. D 77, 083006 (2008); Chluba, Fung & Switzer, MNRAS 423, 3227 (2012). These sources support optimization and physical context, not novelty of the present specialized identity.
