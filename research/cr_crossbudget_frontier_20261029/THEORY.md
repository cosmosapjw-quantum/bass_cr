# CR_HL_CROSS_BUDGET_FRONTIER_V1

**Authority / scope:** Conditional mathematics for cosmosapjw-quantum/bass_cr, separate from PR116–118. Native 3201-atom PHYS02 input is **not** used or rerun. No actual exclusive event kernel, physical cutoff, density evolution, deposition, or observational prediction follows.

## Definitions

A finite set of atoms has nonnegative rational marginals \(w_i\) in \(\mathrm{m^{-3}s^{-2}}\), energies \(E_i\) in eV, and birth-bin labels \(b_i\). Fix a conditional cap \(K\ge 0\) eV. Low atoms satisfy \(2E_l\le K\); high atoms satisfy \(2E_h>K\). Allowed unordered double events satisfy \(E_i+E_j\le K\). Every low diagonal loop \((l,l)\) is allowed and consumes **twice** its event mass from the same marginal. High-high pairs are impossible by energy. Singles keep unused marginal.

For high-low events \(x_{hl}\ge 0\), low-low events \(y_{ll'}\ge 0\), and cross-bin double-event coefficient \(C=\sum_{b_i\ne b_j} \mathrm{event}_{ij}\), define \(d=\sum x+\sum y\) and the budgeted upper frontier \(d_{\max}(c)=\max\{d:C\le c\}\). This is not a characterization of the joint region at exactly fixed C.

## Theorem (derived)

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
and for c≥2 the maximum is 2. At c=1, previous necessary outer bound permits d=2 whereas **exact optimum is 7/4**, a strict gap 1/4. Wolfram exact MaxValue verifies c=0,1/2,1,3/2,2 with dmax=3/2,13/8,7/4,15/8,2. The new Python small-instance LP verifies primal-dual gap zero, and 16 random finite independent full-event LP fixtures agree.

## Scientific interface, limits and reproducibility

Under only the historical conditional source history \(q_i(t)=t w_i\), proper 0≤t≤10^10 s, \(W=\int t\,dt=5\times10^{19}\,\mathrm{s^2}\); W times event coefficient has units m^-3. If the selected source bookkeeping \(\varepsilon_{\rm chem}=W[I_1N+(I_2-I_1)d]\) applies and \(I_2>I_1\), then replacing d with dmax(c) is a *conditional upper bound*. Retained photons, radiative redistribution, external partner/donor, stopping, electron thermalization, feedback and actual K remain unbound. No physical heating or native25 calculation is licensed.

Use Python 3.13.5 + SymPy 1.14, run python -m unittest -v test_frontier.py; pure rational small-LP backend limits 12 atoms and 48 edges, not a 3201-atom implementation. The prior PR118 resource failure ≥20.45/20 CPU seconds is unchanged; no old budget transferred. Different-author R6/C9 not performed. Source GitHub refs: PR116–118. Literature: classical fractional matching LP duality (Ahn & Guha 2013, arXiv:1307.4355); Switzer & Hirata, Phys Rev D 77, 083006 (2008); Chluba & Sunyaev, MNRAS 402, 1221 (2010). This is a concrete specialized frontier, not a novelty claim for LP duality.
