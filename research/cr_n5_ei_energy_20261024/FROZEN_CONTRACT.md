# N5: selected electron–ion energy exchange

Frozen scientific contract, 2026-10-24. Unit `CR_N5_EI_MAXWELLIAN_ENERGY_EXCHANGE`, consumer `N5_C23D_H1_HE4_EI_ENERGY_V1`. User requested one next complete theory R1–R10 and coding C1–C10 loop plus current accessible survey, publication, backup, and handoff. User-supplied physmath protocol 1.0.0 governs this invocation; the installed plugin's observed 1.3.0 is not silently substituted.

## Baseline and allowed change

Base PR102 D `3acb6beca5de4f82fccff1673dbcac010c53cf24`, science S `896800b4511f323ad3f0b5372b4912fb4770ea98`. Prior unit `research/cr_n5_ce_resolvent_20261024/` is immutable. Its canonical ZIP is 13750538 bytes, SHA256 `541c8132278cda76c8ca73aadaa99aff316efe6cc3f5135bba8d98fe34438c1b`, with retained actual-byte Library/Dropbox R3. Current local bytes match. Prior failed v1/v2 runs, lost-v1 raw status and their charged costs remain unchanged.

Reuse its eight native-knot v3 NPZ cases, source CSVs, pi/conductances/EE generator arrays, CE hazards, source projections, and baseline solutions. Do not call the old EE generator, CE source quadrature, old source projection campaign, old ODE, or old primary runner. No new native provider duplication: PHYS84, PHYS87 and HE-ANG retain their owner boundaries. The new operation is the mass-resolved EI coefficient and its combined-generator consumer. Standard Landau coefficients, Maxwell reversibility, MFPT and resolvent identities are reused mathematics, not new theorems.

Only this new unit may be written. Use additive branch `research/cr-n5-ei-energy-20261024`, stacked on PR102, expected-SHA/non-force publication, draft PR, no merge. No checkout/clone is created: existing API-materialized workspace is used. Central updates are additive observations/returns on the latest actual parent and must preserve all parallel work and original contracts.

## Physical input and conventions

Same C23D elemental source and densities from science `d04b2a56adb4a5d55b901420aa544332b41f6dbb`, `research/cr_c23d_finiteT_source_bridge_20261024/FROZEN_CONTRACT.md`, Git blob `5cd596b8ddd3e0878bd612d300673c522311eebb`:

| Label | Density cm^-3 | Selected charge |
|---|---:|---:|
| HI | 0.9 | 0 |
| HII | 0.1 | 1 |
| HeI | 0.07 | 0 |
| HeII | 0.02 | 1 |
| HeIII | 0.01 | 2 |
| thermal e | 0.14 | -1 |

The source supplies elemental labels, not isotope abundances. New conditional mass resolution: HII is H1+, HeII/HeIII are He4+/He4++. This supplies no D/T/He3/Li6/Li7 density; their actual contributions remain null. New explicit ion-bath assumption is Ti=Te=10000 K, stationary isotropic Maxwellians in the same bath frame. Retain theta=0.8617333262145178 eV and C23D b(theta)=2.3306698113646996e-5 eV/s unchanged. All lnLambda_eb=lnLambda_ee=20 are prescribed leading logarithms.

Selected inertia mass ratios to m_e: H1+ 1836.152673426; He4++ 7294.29954171; He4+ 7295.29954171 (nucleus plus one bound electron, binding mass defect neglected in inertia). Proton/alpha ratios use NIST 2022 CODATA, https://physics.nist.gov/cuu/Constants/Table/allascii.txt . The He+ inertia approximation is declared, not an assertion of exact atomic mass or a change to any binding-energy ledger. The inherited EE normalization is not recomputed with updated constants.

Nonrelativistic, dilute tagged electrons, classical weak-coupling leading-log, point ionic net charge for elastic Coulomb energy exchange; no ionic excitation/ionization or charge conversion. The original source atoms are all three z=2.316,2.479,2.649 with 384 selected atoms each and 0<W<10eV initially. Exposure10000 proper seconds defines the pulse, not a continuous chemistry integration. Closed box/no escape. Initial selection is not a path ceiling. General signature(-,+,+,+), c,hbar,kB are retained in interpretation; this local nonrelativistic operator is in eV/proper second.

## Coefficient and conservation contract

For an ion b define r_b=M_b/m_e, eta_b=(n_b Z_b^2/ne)*(lnLambda_eb/lnLambda_ee), x_b=r_b E/theta_b, b_b=b_ee(E) eta_b, and A(x)=P(3/2,x)=erf(sqrt(x))-2sqrt(x)exp(-x)/sqrt(pi), A'(x)=2sqrt(x)exp(-x)/sqrt(pi). Use a positive incomplete-gamma evaluation, not small-x subtractive cancellation.

    D_b = theta_b b_b A(x_b)/r_b
    mu_b = b_b [A'(x_b)-A(x_b)/r_b]
    Var(dE)=2D_b dt

D has eV^2/s and mu eV/s. These follow from the Rosenbluth velocity drift gamma_b(1+1/r)grad H and covariance gamma_b Hess g via Ito E=m_ev^2/(2epsilon_eV). The perpendicular diffusion contribution is retained; do not copy the velocity-friction mass factor into energy diffusion. Verify mu=D'+D(1/(2E)-1/theta_b). Same T implies common Maxwell weight p_theta proportional sqrt(E)exp(-E/theta).

The elastic channel has zero nucleus, ionic charge and free-electron-number incidence. Bath gain is the opposite of the same tagged electron kinetic moment; do not add another stopping heat. This is a frozen-bath diagnostic, not a finite-bath thermal evolution or N6 activation. A finite elastic-event count/hazard is not defined by this leading-log diffusion representation and must remain null, distinct from energy drift/diffusion and angular scattering.

Compute per-atom per-ion mu,D and total EI/EE diffusion ratio from saved source. Reuse saved per-atom EE values. Source-rate-weighted moments and exposure-scaled initial-pulse heat have different units and must be named separately. Save fractions with positive/negative/zero signed drift by count and by energy, without inferring a drift time from a cancellation zero.

Useful validation identity for a normalized Maxwell test population of theta_t and bath theta_b, with b_b(E)=C_b/sqrt(E):

    <mu_b> = 2 C_b (theta_b-theta_t) / [sqrt(pi) r_b (theta_t+theta_b/r_b)^(3/2)].

This is a standard thermal energy-exchange consequence; derive by Laplace transform of A. No new physical thermal-rate database or source quadrature is needed.

## New same-grid consumer

Use exactly the eight saved PR102 native-knot grids: chi=1.5,3; R=40,80; geometric N=1024,2048; primary R80. Read E,pi,c_ee,Q_ee,h_s,h_p,p_z and old CE solutions directly. Preserve each input file and its SHA256 in INPUT_MANIFEST.json. No old grid or provider rebuild.

At each edge midpoint E_m, c_b=c_ee*(eta_b/r_b)*A(r_b E_m/theta)/A(E_m/theta). This uses identical finite-volume geometry and the common equilibrium; it is the ratio of D_b/D_ee. New tridiagonal Q_b uses upward c_b/pi_left, downward c_b/pi_right and their negative outgoing sum. Combine Q_tot=Q_ee+sum Q_b; derive total diagonal from summed outgoing edges and record any floating rounding difference from literal diagonal addition. q is state0. Transient G=Q_tot[1:,1:].T and a_j=Q_tot[0,j+1]. q loss stays in G. Top remains reflecting.

K=diag(h_s+h_p)-G. Solve only the new combined system:

    K [u_s,u_p,u_entry,t,r_s,r_p] = [h_s,h_p,a,1,E*h_s,E*h_p]
    K [v_s,v_p] = [u_s,u_p]
    K H_b = -(Q_b.T @ E_full)[1:]  for EE,H1+,He4+,He4++

Twelve RHS per case, 8 cases, 96 primary RHS planned. Use tridiagonal linear algebra, FP64, no dense generator, no ODE. Signed energy RHS is permitted; negative drift/reward must not be clipped. The electron-energy drift must include transitions to q with energy q. Compute it from edge increments to avoid multiplying a full cancellation-heavy matrix.

Read old u_s/u_p/r/t/v directly for a same-grid comparison. Compute source-weighted P_CE, mean diagnostic stop time, conditional CE energy/time, and each bath reward. Normalize active values by original saved W>q population including any mass projected to q. Selected normalization uses all original selected atoms. Inactive W<=q atoms stop at their own original energy and have zero diagnostic reward.

Energy identity on each active initial state:

    sum_b H_b + q*u_entry + (r_s+r_p-Delta*(u_s+u_p))
       + Delta*(u_s+u_p) = E

At source level add initial p_q*q and the original inactive kinetic moment. CE internal energy is not final gas heat; no radiative decay or repeated CE after the first mark is modeled. Ending this diagnostic at CE is not physical destruction of an electron. First entry is not irreversible assimilation or Maxwellization.

For the no-CE first-entry comparison use the already established reversible-chain conductance formula directly on saved c_ee and new c_tot:

    T_i = sum_(k=0)^(i-1) [sum_(j=k+1)^m pi_j]/c_k

These are new paired algebraic diagnostics on stored arrays, not a rerun of the old EE/CE solver. They need no extra linear RHS. Same-T provides the analytic bound delta_max=(sum eta_b/r_b)/A(chi): T_ee/(1+delta_max)<=T_tot<=T_ee. Verify on the actual edges/source means. Do not transfer this monotonic claim to CE probabilities.

## Frozen validation and review

- Required fields/units/frame/log/densities/masses/T positive and finite; null is rejected as unavailable and is never coerced to0. Explicit n=0 and Z=0 controls are distinct exact-zero models. Different ion T is valid for a single coefficient but rejected by this common-weight consumer. Wrong source hash and run-ID reuse are errors.
- New coefficient controls: r=1 matches PR59 mu,D at relative5e-13 on a fixed positive-energy list; density and Z^2 scaling; small-x positivity/series; high-energy and heavy-mass limit; equilibrium identity and thermal exchange sign; exact charge sum to2e-15. Do not run the old PR59 test suite.
- Per-species and total Q column sum / absolute column scale <=2e-13, detailed-balance edge defect <=2e-13. Pi and source arrays are unchanged inputs.
- Each linear backward scaled residual <=2e-12, probability partition max abs<=2e-8, probabilities in[-2e-10,1+2e-10]. Energy ledger max residual / sum of absolute energy terms <=2e-8. This is a finite-chain numerical ledger, not a continuum/global error certificate.
- MFPT algebra/Poisson residual <=2e-12 and analytic comparison bound slack2e-10 relative. Report exact delta_max and actual maximum edge ratio. No arbitrary first-entry time screen.
- N1024→2048 at fixed chi,R,z: P_CE, ion heat per selected, no-CE MFPT, conditional CE energy/time relative change<=5e-3. Relative EI-induced CE change (P_new/P_old-1) must agree within1e-2 relative, with1e-10 absolute floor near zero. Preserve a failure and return to root for diagnosis; no silent tolerance/grid/model change.
- Finest N2048 R40→80: same five observables relative difference<=1e-5; EI-induced relative CE change absolute difference<=1e-7. Store all comparisons, not just maxima.
- Independent reviewer uses raw sources and new matrices, no production import. One targeted Decimal/mpmath80 check of coefficient values and selected finest-grid probability/energy reward solutions; acceptable relative difference<=5e-10. Signed near-zero quantities use a noncancelling absolute scale defined by their component magnitudes. Include a literal charge/energy algebra check. Verify the unchanged source identity only once, not repeated science.
- One useful figure from saved new outputs: signed drift and EI/EE diffusion versus energy; source-weighted heat/first-entry/CE effect with grid comparison. Root and independent reviewer inspect the actual image for semantic correctness and readability. Do not rerun science to plot.

## Resource and cumulative budget

Inherited known bounded worker lineage24.830244114 CPU seconds; original ODE4 retained and this unit newODE0. Global spend, remaining, currency and total unmeasured I/O/model/tool cost are null. Mechanical survey/packaging samples stay separate. Nothing resets the lineage or transfers another owner's allowance.

Observed host affinity0–8, quota8CPUs, memory8GiB. Reserve coordinatorCPU8; scientific workerCPU0, independent reviewerCPU1, native/BLAS/OMP threads1. CPU55 is absent and is not repurposed. Check actual host/process/task lease before launching; external NCP runtime/leaseUNOBSERVED. Exclusive local task lock, create-only run directories and immutable executed-source snapshots. No NCP/MPI/native build.

This requested new light unit has CPU60s aggregate scoped ceiling, with focused tests<=5CPU/20wall, primary<=10CPU/40wall, independent check<=10CPU/40wall, saved-output plotting<=5CPU/20wall. Leave unused allowance recorded; repairs require an observed finding and root-scoped authorization within the same cumulative allowance. Estimate is justified by prior eight-case tridiagonal run0.550025CPU and max2480nodes; no heavy campaign is authorized. Mechanical backup I/O and remote CAS are separate measured/unknown fields.

Before tests/primary execution: publish the root contract and prepared implementation in a new draft branch and preserve a checkpoint through actual provider acknowledgment. Root reviews the contract and independent R6 receipt, then tells the lower-tier executor to start. Stop at a substantive scientific/numerical failure and return all partial raw/cost without inventing a repair.

## Claim/DAG/closeout

Pass gate target `NUMERICALLY_CHECKED_SCOPED_CONDITIONAL_EI_FINITE_CHAIN`; claim only selected H1+/He4+/He4++ leading-log Maxwellian energy coefficients, source moments, and finite-chain EE+EI+first-CE consumer. Missing other rates/abundances/neutral elastic and dominant omitted-process ranking remain null. Original isotope quotient condition PQ=QbarP and c^T=cbar^TP is reused; no generic elemental quotient admission follows from this new mass choice.

CR_N4_STOPPING_KERNEL and CR_N5_ATOMIC_ISOTOPE_COVERAGE remain PARTIAL/OPEN. N6_CONSERVATIVE_COUPLING and N7_NEW_PARCEL remain predecessor-gated. Preserve original central40contracts, FS composition gate, non-tilted LRS/full Frobenius, signed amplitude/norm/cancellation, atomic isotropic gas versus nonbaryonic Vlasov stress. Full high-energy nuclear and general triaxial/tilted/polarized CMB HOLD, original nuclear PNG NOT_RECOVERED_NOT_READ, global_error_bound=null/global_completion_percent=null.

Every R/C stage records EXECUTION | PUBLICATION | BACKUP | DAG with actual evidence. S0 is preparation; scientific S follows independent C9; canonical ZIP carries binary raw; D/M2/terminal preserve publication and backup receipts. Previous Drive unknowns remain historical unknowns, and exact-name+folder reconciliation precedes any retry. New final release uses selected R3 actual-byte verification; routine Git fast-forward is R1. AGENTS references a machine readback config returning404, so the actually read docs/READBACK_POLICY.md governs the same tiers; no synthetic config is substituted.

Strong no-go NG1–NG7: not applicable, no new impossibility claim. Novelty scope is this previously missing selected EI consumer and numerical observations, not the standard Landau/MFPT/Markov identities.
