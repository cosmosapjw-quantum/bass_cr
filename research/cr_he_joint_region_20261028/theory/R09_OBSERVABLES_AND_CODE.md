# R9 — Formal source-observable corollaries and code boundary

## Source-parent and chemical region

For the unchanged full-selected single-window source contract let W=integral(t dt), nb=8750/47 m^-3, I1=24.59 eV and I2=54.42 eV. For any feasible (d,C),

\[
n_{\rm parent}=W(N-d),\quad
U_{\rm union}=W[I_1N+(I_2-I_1)d],\quad
\Delta U_{\rm partition}=-(I_1+I_2)WC.
\]

The source ion vector is W(-N+d,N-2d,d). Its sum is zero and its ionic charge is WN. The correction to duplicated partition returns is W(C,0,-C), with charge correction -2WC. It is a correction to bookkeeping, not a new electron loss. Dividing each density by nb once yields the source abundance vector. Kinetic energy W*sum(E_i*a_i) is independent of pairing. Partial-selection formulas and the per-call inventory limit are stated in R03; this corollary does not silently extend to them.

At fixed d, the exact range of the chemical partition correction is

\[
-79.01W\min(d,X)\le\Delta U_{\rm partition}
\le-79.01W\max(0,2d-L).
\]

The sign reverses the order of the C endpoints. Both endpoints are attained by complete event measures from THEOREM, so these are joint conditional bounds rather than independent extrema taken from different sources.

At fixed C define d_up=min(D,(L+C)/2). Then

\[
W(N-d_{\rm up})\le n_{\rm parent}\le W(N-C),
\]
\[
W[I_1N+(I_2-I_1)C]\le U_{\rm union}
\le W[I_1N+(I_2-I_1)d_{\rm up}].
\]

These orders use I2-I1=29.83 eV>0 and W>=0. If the inventory imposes d>=d_inv, replace the lower d endpoint C by max(C,d_inv), require it not to exceed d_up, and map the two endpoints through the same formulas. At W=0 every physical density in this corollary is zero and no inventory division is made.

## Required executable interfaces

1. Validate finite rational atoms, unique keys, nonnegative masses/energies and cap. Derive low/high membership exactly. Return a concrete same-bin allowed HL pair when the domain fails, ignoring only zero-mass endpoints. No region claim is returned outside the declared domain.
2. Obtain exact M,D,X and their provenance. Native D/max_events and X/dual certificates are the pinned saved PR114/115 evidence, never a fresh replay of their old optimization. Any new general solver result must have exact primal and dual/bound validation.
3. Produce O,A,B,F,G event measures. Native K2 may use saved B because X=M; native K20 may reuse saved cross G because M=0. Native K6 requires a new explicit cross primal; X=D makes that measure itself F=G once exact equality is checked. Degenerate caps are constructed directly.
4. Given a rational feasible target (d,C), use the theorem's piecewise interpolation with all zero denominators guarded. Mix the entire measure, including singles. Canonicalize unordered electron keys and create consistent event IDs across partition claims.
5. Independently verify pair support, every atom marginal, nonnegativity, exact d and C. Convert the verified measure into the original consumer's Event type, derive claims by its unchanged binding, and execute its once-only source union at the original proper-time window.
6. Export exact fractions in certificates and decimal values only for presentation. Save source hashes, method, actual commands, exit status and resource receipts. Plot from saved accepted results with no source refit or solver invocation.

## Acceptance obligations

The native cap set is 0, exact decimal1/5, twice the stored binary ghost,2,6,20. Verify every distinct vertex and at least one rational interior/edge point for each nontrivial region. Duplicate degenerate coordinates may reuse a named valid representative with identity recorded. K=1,3,10 must return a concrete domain rejection from actual atoms. Boundary equality Ei+Ej=K is allowed; the exact decimal0.2 differs from twice the stored binary64 ghost.

An independent exact small-graph oracle must form the full event marginal problem itself, rather than import the constructor's proposed polygon or tolerance. Cover a nondegenerate pentagon, the M=0/X=0/X=M/X=D degeneracies, a zero-mass atom, equality support and the equal-bin rejected fixture. The new integer backend must reject capacity overflow before narrowing and return verifiable integer flow/cut or event evidence. Tests must expose meaningful risks; no unchanged source solver replay is required.

The primitive source consumer remains untouched. All computations stay in this new additive unit. The new 40 CPU-s local accounting includes compilation, validation, failures and plotting; remote CAS CPU remains separately unknown. The whole scoped node is admissible only after these coding obligations and independent review close. Central count delta is zero and actual physical K/kernel/d/C remain open.
