# Exact finite model: proof details and implementation contract

All w_i>=0 are atom marginal coefficients, not particle rest masses. Finite energies E_i>=0 and K>=0 use eV; w_i,c,d,C use m^-3 s^-2. A low loop consumes2 units of atom marginal per unit of event mass. Singles consume1. Total marginal N counts occupied marginals, while d counts double events. Metric signature(-,+,+,+) is inherited but does not enter this finite gas-rest combinatorial optimization. No natural-unit conversion is made.

Lows satisfy2E_i<=K; highs satisfy2E_i>K. Two highs cannot pair. Every pair of lows is energetically allowed, including low diagonals. For any full event measure write m=HL and q=LL mass. Its cross HL contribution is <= total C<=c. Therefore m<=M(c), m+2q<=L, and d=m+q<=(L+M(c))/2.

Take an optimal HL flow. At each low atom l let r_l=w_l-sum_h x_hl. Add diagonal mass r_l/2. At each high let singleton mass w_h-sum_l x_hl; zero-weight atoms get zero. All original marginals are now equalities. Diagonal bin cost is0, hence total C equals HL cross_used<=c. This proves attainment and supplies the complete certificate, also when there are no HL edges. For empty/zero inputs all totals are0.

With vertex-capacity dual prices p_i>=0 and budget multiplier lambda>=0, the edge inequalities are p_h+p_l+lambda k_hl>=1, k_hl=1[b_h!=b_l]. Finite LP duality gives M(c)=min(sum_i w_i p_i+c lambda). Weak duality can be independently checked by multiplying and summing these edge inequalities. Exact feasible primal and dual with equal objective prove the returned optimum. No solver status string substitutes for these checks.

The feasible sets grow with c, so M is nondecreasing. Mixing optimizers at c1,c2 gives a feasible flow at theta c1+(1-theta)c2 with objective theta M(c1)+(1-theta)M(c2), proving concavity. Finite parametric LP yields a piecewise affine value. Partition any HL flow into same-bin and different-bin edges. The same-bin subflow is feasible at c0, so m<=S+c, S=M(0); also m<=M_infinity. The old inequality2d-C<=L+S follows, but need not attain this new frontier.

At fixed prescribed C=c the diagonal completion construction may use a smaller C, so the theorem describes the upper frontier of C<=c rather than every vertical section C=c. The four-atom example separates the old necessary bound from the exact frontier.

Conditional history q_i(t)=t w_i on proper t in[0,1e10]s gives W=integral t dt=5e19 s^2. Its integrated double-event density is W d. With the separate specified source bookkeeping U_chem=W[I1 N+(I2-I1)d], I2>I1, substituting dmax gives an upper bound in eV m^-3. Multiplication by the eV-to-J conversion gives SI energy density. Temperature/heating require the actual kernel, donor/partner work and thermodynamic state and are not computed here.

Acceptance map: theorem+R06 review -> exact equations; guarded solve -> complete primal witness and dual_prices/budget_multiplier; verify_certificate -> independent algebraic inequalities and exact zero gap; full-event formulation -> small model cross-check; CAS -> four-atom independent optimization. No native3201 source or production solver is called.
