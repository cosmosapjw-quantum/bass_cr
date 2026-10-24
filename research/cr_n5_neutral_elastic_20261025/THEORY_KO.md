# Constructive derivation and scientific scope
## Distribution transformation
Let F0(E) be the isotropic electron energy-distribution function normalized by ∫sqrt(E)F0(E)dE=1 and p=sqrt(E)F0. For a fixed neutral species the standard elastic term has flux proportional to E² sigma_m(E)[F0+theta F0']. Substituting F0=p/sqrt(E) gives
J_N=-D_N[p'-(1/(2E)-1/theta)p], D_N=2(me/M)theta E nu_m.
Thus ∂t p=-∂E(mu_N p)+∂E²(D_N p), with mu_N=D_N'+D_N(1/(2E)-1/theta).
Expanding nu_m∝sqrt(E)sigma_m gives mu_N=2(me/M)nu_m[theta(2+E sigma_m'/sigma_m)-E]. Each term has eV/s, D has eV²/s. Maxwell p∝sqrt(E)e^{-E/theta} has identically zero flux. With common theta all EE/EI/neutral generators share the same invariant weight; their conductances can be added without modifying the stored pi.

## Cold recoil and physical order
At theta_N→0 the leading drift is -2(me/M)E nu_m. For one stationary finite-mass target, exact angle-averaged recoil is -[2 me M/(me+M)²]E nu_m under the same relative-speed cross section. The leading coefficient is the O(me/M) expansion; it is not the exact finite-mass coefficient. Thermal motion is retained to the same leading order. Active-domain theta/(r E) controls the small target-speed expansion, while resonant/source interpolation structure is an additional dependence. A small mass ratio alone is not a certified data/model error.

## Exact first moment identity (not a full diffusion closure)
For electron velocity v, Maxwell target velocity u, relative g=v-u, V=(me v+M u)/(me+M), and reduced mass mr, angular integration gives a_E=-n mr <g sigma_m(g) V·g>_u. This follows from ΔE=mr V·(g'-g) and the definition sigma_m=∫(1-cosχ)dσ. Set beta=me/(me+M), s²=kBTn/M and f(g)=g sigma_m(g). Gaussian integration by parts gives
a_E=n mr[s²<3 f+g f'>-beta<g² f>].
At fixed v with target thermal speed small, expanding the averages yields the preceding leading drift (after the energy-unit conversion). This identity concerns only the first energy moment. Higher angular moments enter the exact finite-mass variance; the supplied MTCS is sufficient for the adopted leading operator, not an exact finite-mass Boltzmann kernel.

## Piecewise-linear data and finite chains
The target-speed parameter theta/(r E) is not the only physical truncation parameter. Define sigma_2=∫(1-cosχ)^2 dσ, for which 0<=sigma_2<=2 sigma_m. The cold recoil contribution omitted from the leading thermal diffusion is D_recoil≈2(me/M)^2 E^2 n v sigma_2, so D_recoil/D_thermal≈[E/(r theta)] sigma_2/sigma_m<=2E/(r theta) at this order. Its upper-grid diagnostic reaches 2R/r; report it separately from theta/(r q). This elementary angular inequality is not a full physical-error bound, and actual sigma_2 is not supplied. The simulation solves the declared leading operator over the finite grid; it does not certify exact finite-mass diffusion at its top boundary.

The adopted sigma_m interpolation is continuous and piecewise C1. Consequently D_N is continuous and positive; mu_N has finite one-sided values at native knots. The weak flux equation is well defined across these knots. The implementation constructs conductance directly from D_N; no delta term or smoothing of raw data is introduced. Exact database support is enforced.
On an inherited grid, each new edge c>0 gives Q_{j+1,j}=c/pi_j and Q_{j,j+1}=c/pi_{j+1}. Column sum zero and Q pi=0 follow edge by edge. All fixed-bath energy gains are computed by -Q^T E, so adding two neutral generators preserves the stopped-process energy ledger when the same killed operator solves every reward.
For the un-killed first-entry problem, T_i=Σ_{k<i}(Σ_{j>k}pi_j)/c_k. Since c_old<=c_new<=(1+delta)c_old, Told/(1+delta)<=Tnew<=Told. CE killing is retained in a separate resolvent and is not asserted to obey that MFPT comparison.

## Isotope quotient and nuclei
Elastic electron-H1 or electron-He4 changes kinetic energy only: electron and target counts, target internal ground state, charge and nucleus identity are fixed. The prescribed neutral bath absorbs exactly the opposite electron kinetic reward; no chemistry integration or bath-temperature feedback is performed.
An isotope aggregation is exact only when the projected kinetics and energy ownership descend through the quotient (for a linear operator, S K=L S), or when a stated conditional closure supplies the unresolved isotope fractions and resulting mass-weighted coefficients. Even identical electronic MTCS does not remove the explicit inverse-mass factor. Unknown D/T/He3/Li6/Li7 densities remain null. H1/He4 is a conditional assignment, not inferred isotope completeness.

## Evidence and decisions
- Standard operator: Hagelaar & Pitchford, Plasma Sources Sci. Technol.14(2005)722–733, DOI10.1088/0963-0252/14/4/011, Eq27 (F0 convention), official BOLSIG+ data manual.
- Atomic scattering method: Bray & Stelbovics1992, DOI10.1103/PhysRevA.46.6995; Fursa & Bray1995, DOI10.1103/PhysRevA.52.1279. Actual adopted MTCS are separately identified CCC/LXCat process records.
- Wolfram actual symbolic evaluation returned zero for drift identity, Maxwell zero flux and power-law reduction, and the leading cold limit. Its preceding context search returned no relevant atomic source; that search is not source validation.
- This work adds a data-bound neutral consumer on existing completed finite grids. Ground-H RR/Milne remains an alternative dependency and is not implemented in parallel with an active matching provider.
- No new strong no-go is proposed; NG1–NG7 not applicable. Source support/licensing or absent angular information are scoped input limitations, not no-go results.
