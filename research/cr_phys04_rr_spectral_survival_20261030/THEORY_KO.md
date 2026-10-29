# CR_PHYS04: H/He source-locked photon spectral survival and first-absorption envelope

## Source/physical state

Original PR125 contains 4 proper-time bins [0,2.5,5.0,7.5,10.0]×10^9 s, 3200 original electron-energy atoms per each ground-state H and He radiative recombination channel, photon energy E_e+I_a and nonnegative photon number weights w_{jic} [m^-3]. The SOURCE archive and atomwise NPZ are byte-locked. Ground-state neutral densities are inherited from the original PR110 fixed state at 100 K, n_HI=138.6 m^-3, n_HeI=11.427127659574467 m^-3. The original PR127 implementation of Verner et al. (1996) Table 1 supplies sigma_a(E), H I / He I ground photoionization cross sections. This is not an astrophysical background photon field or an expanding-universe solution.

The medium is homogeneous, stationary, source-independent, without scattering, redshift, re-emission, gas feedback or photoelectron secondary processes. Photons travel at physical c. Their individual emission times are *unknown* within source birth bins. We use no distribution or midpoint interpolation. Total opacities in the original source energy range are positive.

## Absorber-resolved event measure

For photon E, alpha_a(E)=n_a sigma_a(E) [m^-1], alpha=sum_a alpha_a, kappa=c alpha [s^-1]. The conditional event probabilities by observer proper time T for source birth s are

 U(s,T) = 1_{s>T} (unborn);
 S(s,T) = 1_{s<=T} exp[-kappa (T-s)] (surviving photon);
 A_a(s,T) = 1_{s<=T} (alpha_a/alpha) {1-exp[-kappa(T-s)]} (first absorption by a).

For all admissible source times, U+S+A_HI+A_HeI=1. At alpha=0 define S=1 if born, A_a=0. The present locked source has alpha>0, verified before evaluation. Multiply every probability by w for photon number density and by E*(1.602176634e-19 J/eV) for total primary photon energy.

## Theorem: sharp *pointwise* spectral envelopes

Fix one source weight w>=0 of energy E and a birth interval [l,r] (inclusive), T>=0. For each T independently, the extremal **surviving photon** probabilities are:

- T<l: S_min=S_max=0;
- l<=T<r: S_min=0 and S_max=1;
- T>=r: S_min=exp[-kappa(T-l)], S_max=exp[-kappa(T-r)].

For absorption target a, at all T:
 A_a,min = P_a(r,T), A_a,max = P_a(l,T), where P_a(s,T)=0 when s>T, otherwise (alpha_a/alpha)[1-exp(-kappa(T-s))].

For unborn photons:
 U_min=1 when T<l and 0 otherwise; U_max=1 when T<r and 0 otherwise.

**Proof:** For s<=T, S(s,T)=exp[-kappa(T-s)] increases with s, while each A_a decreases with s. At T in [l,r), an emission after T makes S=0, but an emission exactly at T makes S=1. Thus the survivor maximum in a partially covered source bin occurs at the *interior observation time* s=T, not necessarily at bin endpoint. The absorber max/min are at l/r respectively. Endpoints and interior times are allowed by the source bin-only birth contract. Since individual original atom times are independent unconstrained degrees of freedom under this reduced contract and all w>=0, multiplying by w and summing arbitrary subsets (including fixed 1 eV photon-energy bins) yields sharp pointwise bounds. The relation is a statement **conditional** on the declared unresolved within-bin birth-time freedoms, not that the underlying RR ODE permits arbitrary histories. QED.

**Important joint warning:** Spectral S_min/S_max, A_min/A_max and U_min/U_max are separately optimized; their endpoints must not be arbitrarily combined in a joint photon/energy conservation statement. For T>=r, earliest versus latest birth provides the exact complementary pair S_min+A_max=w and S_max+A_min=w for each atom. For interior T, some extremizers are mutually incompatible and pointwise survivor maxima at different T need not arise from one global emission history. To test genuine joint consistency we evaluate **three explicit witnesses** per source and epoch: earliest s=l, latest s=r, and observation-specific just-in-time s=clip(T,l,r). Each witness independently enforces U+S+sum A=1 and energy conservation. The witness catalog does not purport to sample the genuine birth-time distribution.

## Computational form

Original photon source channel c in {H,He}, source bin j, atom i, energy E_ci, weight w_cji, energy bin B_k=[e_k,e_{k+1}), e_k=13+k eV, k=0..22, and T in {0,1.25,...,10} Gs. Define

 N^\pm_{\gamma,c,k}(T) = sum_{j,i:E_ci in B_k} w_cji S^\pm(E_ci,[l_j,r_j],T),
 N^\pm_{a,c,k}(T) = sum_{j,i:E_ci in B_k} w_cji A^\pm_a(E_ci,[l_j,r_j],T).

The corresponding surviving/absorbed primary photon energy bins are obtained by inserting E_ci*(J/eV). Target threshold and primary electron excess components use I_a and E_ci-I_a, respectively; no thermal deposition is claimed.

## Literature and scope

1. Verner, Ferland, Korista & Yakovlev, ApJ 465, 487 (1996), doi:10.1086/177435; author-hosted numerical photoionization Table 1, https://www.pa.uky.edu/~verner/photo.html. The revised 1996 Eq.(1) includes (x-1)^2+yw^2; prior source code/Table preserved exactly.
2. Switzer & Hirata, PRD 77, 083006 (2008), doi:10.1103/PhysRevD.77.083006: real cosmological helium-line transfer needs continuum opacity, scattering and evolving neutral fractions, unlike this deliberately frozen, local conditional source.
3. Chluba, Fung & Switzer (2012), doi:10.1111/j.1365-2966.2012.21110.x: further time-dependent transfer effects; *not implemented here*.

These source citations do not establish this as a cosmological optical-depth solution, CMB spectral distortion, true in-situ photoionization rate, gas heat, physical K, exclusive He event kernel, or general transport benchmark.

## Evidence

- Direct constructive piecewise proof above: `derived` under original source freedoms.
- Source ZIP byte lock + nested PR125/127 bytes: `implementation-verified` on current run.
- Python normal 13/13, `-O` 13/13 and source mutation negative test: `implementation-verified`.
- Independent same-author mpmath at 80 dps: `numerically-checked`, 64 original atom/bin combos, worst relative differences <3e-15.
- Wolfram: derivatives dS/ds=+kappa exp[-kappa(T-s)], dP_a/ds=-c alpha_a exp[-kappa(T-s)], S+sum A=1 for born photon: `symbolically checked`.
- Different-author review R6/C9: **NOT_RUN**; user must obtain genuine independent checks before acceptance.
