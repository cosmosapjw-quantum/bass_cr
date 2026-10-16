# C21D R5: Common-IC event ownership and competing-risk native interface

2026-10-16 KST. Immutable parent: bass_cr PR #78, commit `12eba7754df154dbd9e8b2947bb2b94199126e51`. Relative physical scope: source-age photons (3 old, GL2 births each at 3 positive energies) and H I, He I, He II photo-only gas. No native Rust compile or Case-A RR/CI/DR/CMB claim.

## Distinct current physics lanes

On **identical** initial photon stock, GL2 impulse birth locations and q20=a_birth E, proper H(a), total-H nuclei (not neutral-H) density, original Verner fit and physical binding constants, and one common time grid, compare:

1. Exact continuous photo-only evolution and actual physical absorber exposure `I_j=∫_t0^t1 A_j(t) dt`, independently integrated by SciPy Radau as a reference.
2. Coupled *endpoint backward Euler* photo reaction: `N_r^1=N_r^0/[1+dt Σ_j k_rj A_j^1]`, `L_rj=dt k_rj A_j^1 N_r^1` and `A^1=A^0+S*Σ_r L_rj` with H/He stoichiometric matrix. This is a mathematical frozen-midpoint BE **photo-only** lane, not compiled owner C21 or PR150.
3. Coupled *endpoint-frozen positive exponential* photo reaction: `N_r^1=N_r^0 exp(-dt Σ_j k_rj A_j^1)`, `L_rj=(N_r^0-N_r^1) k_rj A_j^1/(Σ_j k_rj A_j^1)` with same gas stoichiometry. This is an independent frozen-end opacity proxy, **not** a claim of native `PreparedAbsorption` byte/numerical identity.
4. PR #76's original positive exact-pair Strang reactor can be retained as separate source-conditional control, but does **not** directly define physical-time absorber exposure.

The source-age birth clock belongs to the photon impulse, not an artificially spread constant source across all intervals. All four lanes must retain the **same** old stock and exact GL2 birth quadrature. Native `Γ_exposure=Σ_r L_rj/I_j` and `Γ_BE=Σ_r L_rj/(dt A_j^1)` are distinct: one is physically time averaged, one enforces native BE endpoint event count. Never silently substitute them. Even in a mixed HeI→HeII→HeIII network, the central photo events `L` rather than instantaneous Γ alone are the conserved shared contract.

## Constructive one-species monotone well-posedness

With constant positive `α=k dt`, starting photon stock `P0>=0` and absorber `A0>=0`, the frozen-end BE step asks for a root of
`F(a)=A0-a-P0 α a/(1+αa)=0, 0<=a<=A0`.
Since `F(0)=A0>=0`, `F(A0)=-P0 α A0/(1+α A0)<=0` and `F'(a)=-1-P0 α/(1+αa)^2<0`, a unique physical root exists (with the degenerate A0=0 branch trivial). The frozen-end exponential replaces the rational fraction by `1-exp(-αa)` and has `F'(a)=-1-P0 α exp(-αa)<0`; it also has a unique nonnegative physical root. This result is **not** uniqueness of the coupled H/He three-species nonlinear system. For the latter, a bounded residual and all nonnegative populations must be independently checked; otherwise return HOLD without clipping.

## Exact multi-species photon, nuclei, electron and binding event identities

Let `(h,i,j)` denote absorbed photons/H by H I, He I, He II, respectively (photo-only). Changes in the five physical per-total-H stocks `(H I,H II,He I,He II,He III)` are `(-h,+h,-i,+i-j,+j)`. The sum of H nuclei and He nuclei separately vanishes, the electron abundance increases by `h+i+j`, the photon count drops by `h+i+j`, and physical binding increases by
`χ_H h + χ_HeI i + χ_HeII j`.

At each photo event with physical energy E, photoheat is `L_j(E-χ_j)` and binding is `L_j χ_j`. For a photon energy and gas work split around the same chemical midpoint, the exact discrete global photo-only identity is
`(Uγ0+Usrc) - Uγ1 = Σ_j(Qheat_j + χ_j L_j) + Wγ`;
`Uth1-Uth0 = Σ_j Qheat_j - Wgas`;
`ΔB=Σ_j χ_j L_j`;
therefore `(Uγ0+Usrc)-Uγ1-(Uth1-Uth0)-ΔB-Wγ-Wgas=0`.
No recombination escape/CMB term is present in this **manufactured photo-only** identity. Real original Grackle paths must own these additional terms exactly once.

Wolfram Language independently returned six exact zero residuals: nuclei H, nuclei He, electron census, binding, photon number, thermal photo decomposition. Tool output includes undefined-symbol warnings from symbolic parameters but all six expressions were verified as zero.

## Research positioning

This finite same-IC photo-only comparison is not a full Grackle comparison, not native PR150 `PreparedAbsorption` equivalence, and not a source-matched cosmological continuous reference at age16/32 or signed Bianchi. Related current checkpoints: bass_cr PR #77/#78; rei_bianchi PR #170/#171/#172; BASS_HE PR #74. Complement original Mellema et al., *C2-Ray* (2006) and Friedrich et al., helium C2-Ray (2012) photon-conserving rate allocations and Norman et al. (2015) implicit radiation-chemistry coupling. The next native owner action is to replace the exponential proxy with actual pinned native PR150 prepared operator and integrate CI/RR/DR/thermal/CMB on the identical physical/source clock.
