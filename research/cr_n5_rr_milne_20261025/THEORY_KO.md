# N5 H1 RR–PI source intake and differential-consumer theory

Observed 2026-10-25 UTC. This is source/theory intake for the root authority; no numerical solver, quadrature, ODE, source reconstruction, or publication was run by this agent.

## Decision and reuse boundary

The dependency-ready next unit is a **consumer binding of the existing H I ground-channel Milne provider to the saved PR104 finite chain**. The Milne relation, thermal rates, Verner photoionization fit, and C23D source atoms are prior results. The new computation is the ground-capture hazard/reward on the actual saved nonthermal electron process.

Existing provider: REI PR151, HEAD `8a4f5df46f6e3058f5e685b85cc1cf3c20926368`, unit `research/microphysics_r9_20261015/unit8_remaining_bridges_20261016`. Actual code `code/li_thermal_rates.py` Git blob `815a3f9ca3d8ecad995c80814948632907390762`; theory blob `93f6ab5903dbc1d33864d990c37d25c9c7560046`; contract blob `7fb86947fe81496b84e32008c477d3fde52916b2`. Census agent saved the exact files under `current_intake_20261025/provider_survey/reused_milne/`. Six H/He/Li ground-photo/Milne channels already exist. Eighteen independent detailed-balance quadratures reportedly agree to 4.55e-13; use the exact owner review/returned values, not a new thermal integration. The separate Li kinetics BDF failure remains HOLD and does not invalidate the separately tested rate block.

The module allocates Legendre64/128 nodes at import. Reading the module is safe; importing it would execute old quadrature-node setup. For the new adapter reuse the smaller pinned C23B `Verner96.sigma_cm2` implementation and source row, or extract only the existing provider's scalar photo function with explicit provenance. Do not repeat the old thermal quadratures.

C23B primary source is a **Verner1996 fitted cross section**, not an exact Coulomb 1s cross section. Its native H threshold is13.60eV. Preserve it with the source fit; do not substitute13.598...eV or a reduced-mass threshold into the same fitted input. Conditional H1 interpretation is explicit, as the element provider itself has isotope resolution OPEN.

## Exact scalar source identity

C23B module at PR104 D `257007cc708d0db403ec2ff0c741e4a10b6207ab`:
`research/cr_c23b_source_frame_20261023/source_providers/spectral_photo_source.py`, Git blob `e7d474d5145cb264102206e0403b0aa5916c3140`.

Its `photo.dat` is17760bytes, SHA256 `a53e73b0af4cc6b801aef67b84bd964e3ed8c9c4992f214e4a69dc7e4443f389`; H row Z=1,N=1:
threshold13.60, maximum50000, E0=.4298eV, sigma0=54750Mb, ya32.88, P2.963, yw=y0=y1=0.
The function returns cm²;1Mb=1e-18cm²=1e-22m².
For photon epsilon,
x=epsilon/E0-y0, y=sqrt(x²+y1²),
sigma=sigma0*1e-18*((x-1)²+yw²)*y^(P/2-5.5)*(1+sqrt(y/ya))^(-P).
It rejects above50000eV; below threshold its physical channel is zero. Unknown other species never become zero.

REI151 PH2 matches the exact same H row. Its constants are eV=1.602176634e-19J, kB=1.380649e-23J/K, h=6.62607015e-34J s,c=299792458m/s,me=9.1093837139e-31kg. Its d=2*g_ion/g_bound=1 for H I. Where parent-chain constants differ, freeze the convention and report the difference rather than silently changing stored arrays.

## Microscopic inversion and units

Let E>0 be kinetic electron energy in the heavy stationary target frame, epsilon=E+I, I=13.60eV. Under the same nonrelativistic, zero-recoil dipole convention as C23B,

sigma_RR(E) = (g_bound/g_ion) * epsilon²/(2*me*c²*E) * sigma_PI(epsilon)
            = (2/d) * epsilon²/(2*me*c²*E) * sigma_PI(epsilon).

For H1(1s), electronic g_bound=2,g_ion=1,d=1. Free-electron spin2 and photon polarization2 cancel in reciprocal-channel counting. A consistently included common nuclear-spin factor cancels. No extra factor2 may be added. This agrees with the original REI151 rate formula:
alpha_sp=(C/D) integral sigma_PI(epsilon)*epsilon²*exp[-E/theta] d epsilon,
C=8*pi/(h³c²), D=d*(2*pi*me*theta/h²)^(3/2).

The differential Maxwell factor is
f_E(E)=2/sqrt(pi)*sqrt(E)/theta^(3/2)*exp(-E/theta).
Multiplying v=sqrt(2E/me) by f_E and the microscopic sigma_RR gives the C/D integrand. This algebraic equivalence justifies reusing the existing rate validation without redoing its integration.

For a **tagged electron**, lambda_RR(E)=n_p*v(E)*sigma_RR(E), in s^-1.
The target is n_p=.1cm^-3, not electron-bath density .14cm^-3. A bulk thermal reaction would have density n_e*n_p*alpha; that bulk chemistry is outside this tagged-impulse computation.

sigma_RR diverges like E^-1 and lambda like E^-1/2 toward E0. The stored active chains start at q=chi*theta>0, so no zero-energy evaluation or arbitrary cutoff is needed. The initial selection0<W<10eV is not a path ceiling; evaluate active-grid E through the existing reflecting U. All E+I remain below the source maximum. Below q the stopped model does not evolve captures; do not call their omitted rates zero.

## Photon occupation and scope

The microscopic sigma above is spontaneous RR. For isotropic unpolarized radiation with photon occupation n_gamma(epsilon), total RR has factor1+n_gamma. Ground PI and stimulated RR cancel pointwise only for the appropriate thermal populations and Planck occupation.

Existing PW19 fields are not a Planck spectrum. If the root elects to bind the initial prescribed PW19 radiation, its exact C23B spectral normalization is S=4*pi*nu*Jnu; the occupation is
n_gamma = c²*S/(8*pi*h*nu^4)
        = h³*c²*S/(8*pi*epsilon^4),
with coherent cgs units for S [erg s^-1 cm^-2] and epsilon [erg]. That would introduce three different frozen hazards. It does not evolve the accumulating closed-box radiation field.

A simpler admissible scoped quantity is the **spontaneous ground-RR component and first-RR endpoint**. Its rate is determined without a radiation-state assumption; stimulated contribution and total RR remain null/unbound when no photon occupation is adopted. Photons produced by capture remain in a bookkeeping reservoir in this closed box. Their subsequent absorption/re-emission is an N6 coupling dependency. The stopping boundary at firstRR is an observation endpoint, not irreversible permanent neutralization.

At LTE, n_e*n_p/n_H = d*(2*pi*me*theta/h²)^(3/2)*exp(-I/theta), and
exp(-E/theta)*(1+n_Planck)=exp(I/theta)*n_Planck.
This explains the old detailed-balance check. It does not assign LTE to the present fixed densities.

## Event conservation and unique energy owners

RR event stoichiometry:
Delta N_e_free=-1, Delta N_p=-1, Delta N_H1(1s)=+1, Delta N_photon=+1.
Nuclear H1 count is unchanged. Ionic charge falls by1 and free electron count falls by1, preserving net charge.

For each capture at E:
Delta electron kinetic = -E;
Delta atomic internal = -I (reference continuum p+e at0);
Delta photon reservoir = +(E+I);
sum=0.
The inverse PI event reverses all signs, as in the reused C23B source ledger.
Photon energy includes the binding release; it is not all thermal electron cooling. The kinetic-cooling reward is E, the photon reward E+I, and internal reward-I. No escape loss is inserted.

This is a frozen-reservoir linear calculation. Event counters can record the changes while the prescribed densities remain fixed. Evolving density changes, momentum/recoil, generated radiation and feedback belong to a subsequent conservative-coupling unit.

Finite proton temperature is already used in old EI bath coefficients, while this new RR channel shares C23B's heavy-target zero-recoil cross-section convention. For a finite-mass extension one needs a consistent relative-frame cross section, reduced-mass threshold, moving-proton average and photon recoil energy. Replacing me with mu in only the prefactor is inconsistent. The new unit can retain an explicit leading-heavy-target RR approximation; it does not certify the omitted finite-M correction.

## Finite-chain binding and positive rare-event diagnostics

Use the saved PR104 active backward killing matrix K, with previous q-entry and CE stopping. Let Lambda=diag(lambda_RR), and K_R=K+Lambda. Preserve the old generator/grid/pi/source array identities. All off-diagonal kinetic transitions remain unchanged.

For any nonnegative previous reward b:
x0=K^-1 b (saved),
xR=K_R^-1 b,
Delta=x0-xR=K_R^-1 Lambda x0 >=0.
Compute paired changes with the rightmost positive formula. Direct subtraction of two old/new near-equal probabilities loses relative accuracy of the rare RR effect.

Direct RR probability is r=K_R^-1 lambda_RR. RR electron-kinetic reward is eR=K_R^-1(lambda_RR*E). Photon reward is pR=eR+I*r; internal reward is uR=-I*r. These equations also specify independent reference quantities.

The previous endpoint RHS vectors b_q,b_CE obey K*1=b_q+b_CE. Therefore
p_q,R+p_CE,R+r=1
within the active chain. The selected source is integrated using the saved projection, including its pre-existing inactive component exactly as prior units.

A useful non-asymptotic bound comes from a=K^-1 lambda_RR, A=max_i a_i:
a-r=K_R^-1 Lambda a, hence
a/(1+A) <= r <= a.
This provides a finite-chain first-order hazard approximation with a quantified relative remainder <=A, using no unknown physical error bound. It follows from positivity, not an expansion assuming numerical smallness.

Also,
0 <= p_CE,0-p_CE,R=K_R^-1 Lambda p_CE,0 <= r
and similarly for q probability. Their sum equals r.
For old expected stopping time t0=K^-1*1,
t0-tR=K_R^-1 Lambda t0 >=0.
These are independent identities to distinguish a physically tiny effect from subtraction error.

Joint first-event time for RR is vR=K_R^-1 r, and conditional mean vR/r where r>0. This is a new scoped observable only if selected by the root contract.

Let b_s be the six old signed bath-gain reward rates and b_q*q the entry energy reward. The old CE endpoint contains projectile E-Delta_CE and atomic+Delta_CE=E. For new RR, total endpoint E=(E+I)+(-I). Thus:
E_initial =
sum_s bath_gain_s
+ q_entry_energy
+ CE_projectile_energy + CE_atomic_internal
+ RR_photon_energy + RR_atomic_internal
+ pre-existing inactive_initial_energy.
The RR photon and internal terms must both appear; their sum is the lost electron kinetic energy. An additional RR electron-energy column is a diagnostic, not a third deposited-energy contribution.

## What this contribution does and does not replace

- Reuses original C23B photo source and original REI151 Milne physics/thermal validation.
- Reuses C23E shared H/D total-RR constitutive moments as earlier conditional evidence.
- Does not add total RR to its own ground component; excited-state RR remains a missing separate coverage obligation.
- DR has no autoionizing core for bare proton capture in this H1 ground channel, but the global network still has other ionic species and processes to cover.
- CI/CX/excited states/isotope-resolved kinetic kernels remain their explicit existing statuses.
- No new strong no-go is proposed. This is a known microscopic relation plus a new nonthermal finite-chain consumer and resolved energy ledger.

## Primary literature actually read

1. Verner et al.1996, ApJ465,487 official author collection https://www.pa.uky.edu/~verner/photo.html and actual photo.dat: exact fit identity and ground-state scope.
2. AtomDB technical memo https://www.atomdb.org/Physics/rrc-v2.pdf, Eq6–14: cross-section reciprocity, Saha electronic weights, stimulated contribution; Eq15–17 photon emission.
3. Mao,Kaastra,Badnell2016 https://arxiv.org/html/1612.01017v1, Sections2.1–2.2: nonresonant level-resolved PI inversion, distinction between count and electron energy-loss moments.
4. Nahar2021 Atoms9,73 https://www.mdpi.com/2218-2004/9/4/73, Eq28/31 and surrounding definitions: exact hydrogenic Coulomb alternative and Milne form. The fetched Eq30 momentum placement is algebraically inconsistent with Eq31. Adopt Eq31 only as corroboration with AtomDB and own spin/Saha derivation; do not copy Eq30. Exact-Coulomb formula is a comparison model, not the adopted C23B fit.

SciSpace and Exa were actually called for discovery; search outputs are preserved. The first parallel call's local result serialization failed before two search outputs were saved; they were repeated once, with the failure retained. No numerical run was involved. No Wolfram call was made by this agent; root may use it for the new finite-chain algebra without repeating old thermal computations.

## Admission and next action

Root authority should freeze ground/spontaneous or explicitoccupation choice; targetdensity; source-native threshold/statistical weights; oldchain identity; direct/paired RHS; relative tolerances that resolve the rareRRsignal; lineage budget. Lower-tier implementation should then bind only the differentialhazard/reward, run bounded controls/newcases, and return actualresults to independent review. No source quadrature, oldthermalquadrature, oldEE/EI/neutralgenerator replay, or cosmologicalODE is needed.



# Root-selected RR consumer conventions

Root froze the choice during the 2026-10-25 source intake:

- Spontaneous H1(1s) RR component only.
- Actual stimulated RR and total RR hazard remain null/unbound.
- Endpoint is first RR before the existing q-entry/CE stopping event.
- Produced photons remain in a closed-box ledger reservoir; no photon transport or feedback is executed.
- N6 coupling is not activated.
- Conditional H1 assignment, native fitted threshold13.60eV, C23B Verner96 function/table reused.
- Electron mass in the consumer equals saved PR104:9.1093837015e-31kg.
- REI151 provider electron mass9.1093837139e-31kg is retained as the original provider convention.

## Algebraic transfer of an existing thermal coefficient

With the same E,theta,threshold,cross-section,eV conversion,statistical factor,and c, the microscopic sigma_RR is proportional to m_e^-1 and v to m_e^-1/2. The normalized energy Maxwell distribution has no mass factor. Therefore both the spontaneous thermal count and kinetic-energy coefficients scale as m_e^-3/2:

alpha_104 = alpha_151*(m_151/m_104)^(3/2).

This is an exact numerical-convention mapping within the fixed fitted model. It is not a recomputed thermal integral, a changed physical cross-section fit, or evidence about the finite-target-mass correction. Other constants in REI151 are eV1.602176634e-19J,kB1.380649e-23J/K,h6.62607015e-34J s,c299792458m/s; compare them against the root frozen contract before adopting a stored reference.

## Immutable local inputs for coding

- `reuse_c23b/spectral_photo_source.py`: SHA256 `71b7e3a6b6f1c68ec15bcb19b98014bc025ef595f53df29703f11e25f36f4a8d`; exact public Gitblob `e7d474d5145cb264102206e0403b0aa5916c3140`.
- `reuse_c23b/data/verner_photo.dat`:17760B; SHA256 `a53e73b0af4cc6b801aef67b84bd964e3ed8c9c4992f214e4a69dc7e4443f389`; Gitblob `754b5ce11cbe662f96394430beeafe3f102f339c`.
- `reuse_c23b/CONTRACT.json`: SHA256 `d589523758493c1f2f2aedec29d09a6a2c2cb8548cdba1a0f8996cd4ab221fe1`; Gitblob `e40e4093ea56c2427cf3a79bd5d29ed6d2edad2e`.

All paths are relative to `current_intake_20261025/source_theory/`. These are restored original bytes, not a new provider implementation. The module's plain import has no top-level quadrature generation. Instantiate only `Verner96.from_table("HI",data_dir=...)` and call `sigma_cm2(E+13.60)`. Do not invoke its source generation/PW19 integration methods. Root designated raw photo table private for the new archive; public code refers to the immutable source identity.

## Review scope

The previous source note's explicit-occupation branch is an unselected alternative. Root selected the spontaneous component. No unsupported radiation occupation is set to zero; spontaneous emission is a separately defined positive channel. The eventual first-event calculation may compare counts and energy rewards to all separately bound old channels; it must not label the spontaneous component a complete physical recombination network.

Execution by this source/theory agent: numeric0,source quadrature0,thermal quadrature0,ODE0,old science replay0.

