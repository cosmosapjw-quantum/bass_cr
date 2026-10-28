# CR_HL_CROSS_BUDGET_FRONTIER_V1

**Authority / scope:** Conditional mathematics for cosmosapjw-quantum/bass_cr, separate from PR116–118. Native 3201-atom PHYS02 input is **not** used or rerun. No actual exclusive event kernel, physical cutoff, density evolution, deposition, or observational prediction follows.

## Definitions

A finite set of atoms has nonnegative rational marginals \(w_i\) in \(\mathrm{m^{-3}s^{-2}}\), energies \(E_i\) in eV, and birth-bin labels \(b_i\). Fix a conditional cap \(K\ge 0\) eV. Low atoms satisfy \(2E_l\le K\); high atoms satisfy \(2E_h>K\). Allowed unordered double events satisfy \(E_i+E_j\le K\). Every low diagonal loop \((l,l)\) is allowed and consumes **twice** its event mass from the same marginal. High-high pairs are impossible by energy. Singles keep unused marginal.

For high-low events \(x_{hl}\ge 0\), low-low events \(y_{ll'}\ge 0\), and cross-bin double-event coefficient \(C=\sum_{b_i\ne b_j} \mathrm{event}_{ij}\), define \(d=\sum x+\sum y\) and the budgeted upper frontier \(d_{\max}(c)=\max\{d:C\le c\}\). This is not a characterization of the joint region at exactly fixed C.

## Theorem (derived; independently reviewed on 2026-10-29)

Assume c>=0. The value theorem also holds for nonnegative real marginals and budgets; the exact API and rational certificate assertions below restrict w_i, E_i, K and c to rationals. The finite HL polytope is nonempty (zero flow) and compact, so its optimum exists. No extra regularity or continuum closure is used.

Let \(L=\sum_l w_l\) and let
\[
M(c)=\max_{x\ge0}\sum_{h,l}x_{hl},
\quad\sum_lx_{hl}\le w_h,\quad\sum_hx_{hl}\le w_l,\quad
\sum_{b_h\ne b_l}x_{hl}\le c,
\]
where HL edges exist iff \(E_h+E_l\le K\). Then
\[
\boxed{d_{\max}(c)=\frac{L+M(c)}{2}.}
\]
**Proof.** Write \(m=\sum x\), \(q=\sum y\). The low marginal consumption is \(m+2q\le L\), hence \(d=m+q\le(L+m)/2\le(L+M(c))/2\). Conversely choose an optimizing HL flow \(x^*\); let \(r_l=w_l-\sum_hx^*_{hl}\ge0\) and assign a low diagonal event \(y_{ll}=r_l/2\) for each low atom. All marginals are respected, diagonal events cost zero cross-bin budget, and \(d=M+(L-M)/2\), so equality is attained. QED.

## Exact primal-dual certificate

By finite LP duality,
\[
M(c)=\min_{\substack{p_h,p_l,\lambda\ge0\\p_h+p_l+\lambda\mathbf1[b_h\ne b_l]\ge1\ \text{on every allowed HL edge}}}
\left(\sum_h w_hp_h+\sum_lw_lp_l+c\lambda\right).
\]
Equal rational primal and dual objectives certify the value. Therefore \(M(c)\) is nondecreasing, concave, piecewise linear. With \(S=M(0)\), \(M_\infty=\lim_{c\to\infty}M(c)\), \(M(c)\le\min(M_\infty,S+c)\), reproducing PR118's necessary outer bound. That earlier bound may be strictly loose.

## Small exact counterexample and independent CAS

Fix K=4 eV, all four marginals 1: L0 (bin0,E0), L1 (bin1,E1), H0 (bin0,E5/2), H1 (bin1,E19/5). Exactly three HL edges survive: x=H0-L0 (same), y=H0-L1 (cross), z=H1-L0 (cross). Constraints \(x+y\le1\), \(x+z\le1\), \(y+z\le c\) imply \(x+y+z\le1+\min(y,z)\le1+c/2\). For 0≤c≤2 the rational primal \(x=1-c/2,\ y=z=c/2\) attains the bound. The dual \(p_{H0}=p_{L0}=\lambda=1/2\), all others zero, certifies its optimality. Thus
\[
M(c)=1+c/2,\quad d_{\max}(c)=3/2+c/4\quad(0\le c\le2),
\]
and for c≥2 the maximum is 2. At c=1, previous necessary outer bound permits d=2 whereas **exact optimum is 7/4**, a strict gap 1/4. This is an explicit counterexample to sufficiency of the old outer facets, not a new universal no-go theorem. Current CAS and implementation results are recorded in evidence/ and RESULTS.json only after actual execution. The predecessor's unlogged numerical claims are not used as execution evidence.

## Scientific interface, limits and reproducibility

Under only the historical conditional source history \(q_i(t)=t w_i\), proper 0≤t≤10^10 s, \(W=\int t\,dt=5\times10^{19}\,\mathrm{s^2}\); W times event coefficient has units m^-3. If the selected source bookkeeping \(\varepsilon_{\rm chem}=W[I_1N+(I_2-I_1)d]\) applies and \(I_2>I_1\), then replacing d with dmax(c) is a *conditional upper bound*. Retained photons, radiative redistribution, external partner/donor, stopping, electron thermalization, feedback and actual K remain unbound. No physical heating or native25 calculation is licensed.

Current runtime is Python3.12.14 with pinned SymPy1.14.0/mpmath1.3.0 installed after an observed PACKAGE_MISSING probe. The exact command and actual environment are in evidence/. The API is limited to12 atoms/48 HL edges. The prior PR118 resource failure ≥20.45/20 CPU seconds is unchanged; no old budget is transferred. Separate theory/code agent reviews are in review/. Source GitHub refs: PR116–118 and the unfinished parent bdc7bf6. LITERATURE.md records primary-source comparisons. The contribution is a specialized constructive frontier and corrected certificate implementation, without a claim of novelty for LP duality.
