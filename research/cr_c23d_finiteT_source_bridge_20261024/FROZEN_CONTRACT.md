# C23D: C23B source to the existing finite-temperature EE operator

Frozen by the root physics controller, 2026-10-23 UTC. Unit `CR_N4_STOPPING_C23B_EE_BRIDGE`, a scoped child of the still-open `CR_N4_STOPPING_KERNEL`. Workflow: physmath research R1-R10 and coding C1-C10; the user selected both complete loops. This is an additive consumer/application of completed theory and code, not a new Coulomb theorem or a rerun of an old campaign.

## Authority and reuse

- Base bass_cr branch `research/cr-c23c-cutoff-binding-20261023`, actual F `ec0c2cb8cc9feae64fe028ca2a4ea0eb7d79c8f8`; root AGENTS unchanged. No local checkout is present; use additive task files and Git data API publication, no fresh clone.
- Existing provider in that base: `research/cr_coulomb_partition_20261014/coulomb_partition.py`, 3984 bytes, Git blob `27923abcaef06527011eb916acf7a414dd43c128`. Reuse its `MaxwellianCoulomb`, `reversible_generator`, `bath_energy_rate`, and `moving_interface` without changing it. The adjacent result report already derives the EE coefficients, common-current moving interface, reversible generator, and MFPT formula. PR59 and PR60-64 remain their own evidence.
- C23B atom CSV at `research/cr_c23c_stopping_coverage_20261023/inputs/photoelectron_atoms.csv`: 1681578 bytes, SHA256 `f5bcfe477b8a073341a7496c079e6eb2737f6ca578b884376887b04989e57fc3`. Existing local bytes under n4_resume_transport_20261024/verified_restore/main/repository/. Source quadrature, old18 binding cases, KC theorem suite, old2048 Landau runs: REUSED, zero replay.
- Current central base M `68420637a9ab54ada92afd786c5733bc0764b8c9`. Preserve original40 contracts and all other owner wrappers; append this scoped return without marking the full stopping node complete.

## Fixed new inputs and physical scope

Use all three supplied redshifts 2.316, 2.479, 2.649. Source weights per volume and proper second are `n_target * q_atom`; do not insert a Lorentz factor or a particle lifetime. Explicit five labels in cm^-3: HI=0.9, HII=0.1, HeI=0.07, HeII=0.02, HeIII=0.01. The initial bath is declared charge-neutral with no initially resolved nonthermal electrons: n_e,total_initial=n_e,thermal=0.14 cm^-3. Retain these as distinct named fields. Frozen bath temperature 10000 K; constant prescribed leading Coulomb logarithm 20. Frame bath_frame_rest_target; time proper seconds. Do not claim this prescribed logarithm is a self-consistent screening calculation.

Define an impulsive test population by the saved source rates times a declared exposure 10000 s. This sets an initial population, not an integration of ongoing photoionization/chemistry. Select atoms with 0 < kinetic_energy_eV < 10 eV for this low-energy EE channel. Preserve all excluded count and energy source totals explicitly, including any exact endpoint atoms. Do not replace missing species/rates with zero. Use source multiplicities exactly as saved.

Dilute frozen-bath acceptance for the selected pulse: N_test/n_e,thermal <= 1e-3 and U_test/(1.5 n_e,thermal k_B T) <= 1e-3. Also report each occupied parent depletion `exposure * Gamma_parent` from ALL saved atoms, not only the low-energy selection. This is a perturbation-size applicability screen, not a quantitative global approximation error bound. If it fails, return the measurements without changing exposure or accepting the frozen-bath model. Full finite-bath alternatives already exist in PR60-64.

Nonrelativistic, classical, nondegenerate, weakly coupled Maxwell electrons, homogeneous bath, tagged dilute test population. Compute and report E_max/(m_e c^2), thermal theta/(m_e c^2), Debye electron-sphere occupancy, classical plasma coupling, and degeneracy n_e lambda_th^3. These characterize this prescribed bath; no neutral or electron-ion suppression estimate is invented. Neutral elastic, excitation/ionization, electron-ion energy exchange, self-consistent screening, radiative/chemical evolution and spatial escape are open separate contributions. The scoped diagnostic uses an explicitly closed box, no escape. Global error bound and full physical stopping/heating remain null.

## Mapping and outputs

Let theta=k_B T/epsilon_eV in eV, v(W)=sqrt(2 epsilon_eV W/m_e), Gamma=4*pi*n_e,thermal*(e^2/(4*pi*epsilon0))^2*lnLambda/m_e^2. Use anchor W*=theta and `loss_anchor=m_e*Gamma/(epsilon_eV*v(W*))`, `log_anchor=20`, `running_log=False`. This maps to the existing eV/second provider. Its convention is Var(dW)=2D dt and count density per eV. Track bath energy gain as minus the SAME test-population collisional energy moment; no second stopping heat.

Analytic dimensionless reduction y=W/theta and tau=(Gamma/v(theta)^3)t makes one coefficient shape reusable for the fixed bath. Any computational simplification is algebraic until a same-input benchmark measures speedup. Save signed per-atom drift and diffusion, source-weighted initial EE energy exchange, source fractions with upward/downward drift and selected count/energy coverage. Distinguish a source-weighted drift coefficient (source units per second squared) from the selected initial-pulse heat rate (energy per volume per second).

For chi=1.5 and3, reuse the old MFPT formula to first entry at q=chi*theta with reflecting upper boundary W_R=40*theta:

    T(W)=integral_q^W dz/[D(z)*p_theta(z)] * integral_z^W_R p_theta(u)du.

Evaluate for selected atoms W>q; initial atoms W<=q have first-entry time0 under that explicitly declared observable. Save weighted means among active atoms and all selected atoms, min/max, and ratio to prescribed evolution time1e10s. Repeat only the MFPT endpoint at W_R=80*theta as a truncation diagnostic. Report first-entry times, never permanent assimilation/Maxwellization times. Diffusive recrossing is retained by the evolution model.

New source evolution at z=2.479: use the old reversible generator with positive ordered geometric centres, lower centre min(1e-6*theta, half minimum selected atom energy), upper centre40*theta, N=256 and512. Project each selected atom to its two neighboring centres with positive linear weights preserving count and kinetic energy. Use reflecting endpoints exactly as the inherited generator specifies; report the finite-band and midpoint equilibrium interpretation. Evolve with backward Euler and tridiagonal solves in dimensionless tau, sample tau=0,0.1,1,5,20. Main step delta_tau=0.01; compare512 at0.005 for temporal sensitivity and256 at0.005 for spatial sensitivity. No historical case is rerun. Record energy, count, nonnegativity, relative entropy to the inherited discrete equilibrium, low/high partition at chi, and opposite bath-energy ledger. Do not replace the source core with a Maxwellian or add the tagged population to bath density.

At each fixed numerical cut choose an explicit inter-centre face q_h nearest requested q and report q_h. Positive edge current J_i=c_i*(N_i/pi_i-N_(i+1)/pi_(i+1)). Tail kinetic moment is q_h*J_edge+I_h with I_h=(E_first_tail-q_h)*J_edge+sum_internal_tail((E_(i+1)-E_i)*J_i). Reuse `moving_interface` for this SAME-current ledger; its complementary reservoir contains background bath plus low-energy tagged particles. Distinguish that reservoir from the background-only heat ledger `-E dot rhs`. New verification checks this source-dependent mapping, not an old theorem suite.

## Frozen numerical acceptance and bounded execution

- Immutable source/provider identities and declared required fields must match before evaluation. Wrong unit/frame, missing bath fields, unknown redshift and invalid densities/temperature/log/domain are explicit errors.
- Count and energy projection relative residual <=1e-12; all weights >=0. Count drift in the evolution <=1e-9 relative; negative populations cannot be clipped. Opposite energy and common-face algebra residual <=1e-11 relative to the corresponding noncancelling moment scale.
- Entropy nonincrease tolerance1e-11 relative to max(1,initial absolute entropy). The inherited discrete Maxwell equilibrium is the target; no new historical equilibrium fixture campaign.
- Compare mean test energy at nonzero output times: spatial256->512 relative difference <=5e-3, temporal0.01->0.005 <=3e-3. MFPT quadrature at epsabs=1e-10 dimensionless, epsrel=1e-9; doubling upper boundary changes source-weighted active means <=1e-8 relative. These are measured scoped convergence criteria, not certified continuum bounds.
- One independent 80-digit arithmetic check of NEW density-anchor mapping and a few NEW source-weighted quantities; no imports of production numerical provider for that reference. Source-derived means can use raw CSV independently. Reviewer owns exact targets and reports its scope.
- If a concrete failure appears, preserve raw evidence and ask root for one targeted repair episode. Never relax a tolerance or change the physical model silently.
- Actual sandbox:9visibleCPUs, affinity0-8, quota8CPUs, memory8GiB. Use one worker pinnedCPU0, coordinator reserveCPU8; CPU55 absent on this host and untouched. Check live affinity/resources/process/lease before each run. Create an exclusive local lease for this new task; external/NCP leases remain UNOBSERVED. Native/BLAS/OMP threads1. No NCP launch.
- New bounded worker ceiling CPU120s, wall180s, RSS512MiB; create-only run directories. Historical budget separately carried from N4, currency/inherited global spend/remaining=null. CPU indices are not CPU seconds.

## Deliverable and gate

New repo path `research/cr_c23d_finiteT_source_bridge_20261024/` contains adapter, runner, input JSON, exact provider/input reuse pins, raw outputs, one useful source/time/energy figure PNG/PDF, R/C ledger, results, independent review, DAG and handoff. Keep code publication separate from large binary delivery as needed. No new scientific claim on full stopping, full thermal closure, atomic coverage or nuclear network.

Gate on passing: `NUMERICALLY_CHECKED_SCOPED` for named `C23D_FROZEN_MAXWELL_EE_LOW10_V1`. The full CR_N4_STOPPING_KERNEL stays PARTIAL/OPEN for channel competition, reciprocal finite bath, escape and coupling. N5 actual-rate coverage and N6 coupling remain separate. Strong no-go NG1-NG7: NOT_APPLICABLE, no new impossibility claim. Publish additive draft with expected-SHA protection, no merge/force; preserve Library/Dropbox/Drive states per artifact. Each stage records EXECUTION | PUBLICATION | BACKUP | DAG.
