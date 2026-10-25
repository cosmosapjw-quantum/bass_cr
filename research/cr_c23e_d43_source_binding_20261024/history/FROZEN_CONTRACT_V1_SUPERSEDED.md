# C23E: H/D charge exchange, source reproduction and conservative reduced candidate

Frozen by root / Astra scientific controller, 2026-10-24 UTC. Unit `CR_N5_HD_CX_BALANCED_PAIR`, a scoped child of `CR_N5_ATOMIC_ISOTOPE_COVERAGE`. The user selected both theory R1–R10 and coding C1–C10. New bounded sandbox research is authorized; completed suites are reused, never replayed for restoration.

## Authority, paths and role

Base science/document branch: `research/cr-c23d-finite-t-source-bridge-20261024`, observed HEAD `4a0bbc0ed618ab6eae1b7b2714e366d803186b86`, PR99. Central observed HEAD `8b6e741ceb305cb0a6fde244ee002eb5926559fe` at PR222. Read `intake/bass_AGENTS.md`, `intake/rei_AGENTS.md`, `intake/policy/PHYSMATH_MAIN.md`, `intake/policy/THEORY_LOOP.md`, `intake/policy/CODING_LOOP.md`. This workspace is not a Git checkout; connector/API additive publication is the existing route, no clone/worktree is required.

Root owns all scientific choices and final admission. Lower-tier coder implements exactly this contract, records new bounded runs, and stops on any physical ambiguity or meaningful acceptance failure. One fresh Astra review is required before scientific admission/publication; one coherent targeted repair may follow. Allowed coding paths: `implementation/`, `inputs/`, `runs/`, `figures/`, `IMPLEMENTATION_REPORT.md` under this directory. No old source/output modifications. No remote mutation by coder.

## R2 source and reuse

1. Savin, ApJ566,599–603 (2002), DOI10.1086/324218; author preprint `https://arxiv.org/pdf/astro-ph/0109356`, v1. Root read reaction1/2, section2 reduced-mass Maxwellian averaging, section3 equation6, Table1 and Table2. Calculation tabulates1–200000K; **fit domain2.7–200000K inclusive**, forward/reverse stated fit errors below6%/4% against the author's computed coefficients. This is not an empirical uncertainty enclosure.
2. Official Grackle commit `6d57fe2c3eb07c34dadb0b0e568cdc12f975146d`, `src/clib/rate_functions.c` k50/k51 and LICENSE are saved in `intake/grackle/`. Reuse the source-matched formula, retain attribution/license; do not adopt its high-T extrapolation. No need build/install Grackle or import its full network.
3. Reuse C23C `intake/c23c/atomic_contract.py`,11926bytes,SHA256 `6246cff6dcc1bac18dd6f8c47b9e9da11f4d14a8bd342c21d30eee19eee9ca69`, Gitblob `e308ceef315e9f40f96fa62c2667253a1283523e`. It supplies the exact21 labels, integer stoichiometry conservation and inventory requirement. Its155+6 old tests are NOT_RUN here. Copy these exact bytes into an implementation reuse directory if needed for standalone execution; record identity, do not edit that copy.
4. C22A actual code contains PI/Case-A RR and conditional VF RR kinetic closure; no H/D CX. Current selected WU PHYS84 concerns H I bound-bound excitation, PHYS85 nuclear ownership still has actual rates OPEN. N5 completed bookkeeping is not a completed empirical full21 network.

## Physical model and two distinct rate objects

Gas frame: common rest frame, nonrelativistic dilute ideal monatomic Maxwellian mixture, no drift, all H/D neutral partners in1s. Atomic stress isotropic. No photons/electrons are produced by this charge exchange. Use physical time seconds, densities cm^-3, coefficients cm^3 s^-1, energies eV, temperature K. `k_B=1.380649e-23/1.602176634e-19 eV/K`.

Forward: `D:0 + H1:1 -> D:1 + H1:0`; reverse opposite. The22-component stoichiometry has four nonzero entries(-1,+1,+1,-1) in order(D0,D+,H0,H+) and zero free-electron component. Eight separate nuclides, baryon number, charge and total particle count are conserved. All21 input keys are mandatory; explicit zeros are allowed, absent keys are errors. Nonparticipating species are declared spectators only, not physically zero rates for their omitted processes.

`raw_savin` is the literal reference fit pair:

`kf=2.00e-10*T**0.402*exp(-37.1/T)-3.31e-17*T**1.48`

`kr=2.06e-10*T**0.396*exp(-33.0/T)+2.03e-9*T**(-0.332)`.

Reject nonfinite T and T outside[2.7,200000]; never extrapolate or clamp to zero. This is the actual published fit, with independent directional fit errors. It is **not thermodynamically admitted as an exact reversible pair**.

The root's actual Wolfram evaluation found kf/kr=1.009893756250886 at10000K, while the author's Table1 ratio is8.04/8.07<1. This is permitted by separate6%/4% fit errors but cannot represent the small isotope ratio accurately. Preserve this finding; do not silently replace either published fit.

`balanced_candidate` is a separately identified construction. Define `Delta=0.0037 eV` exactly as the selected approximate defect from Savin section2 (quoted43K is rounded); this is not a metrological ionization-energy difference. Use a **declared translational/internal partition prefactor Lambda=1**, a ground-state statistical-weight/heavy-nuclear-mass approximation. Electron-mass corrections, hyperfine populations and exact isotope masses remain OPEN for physical precision. Do not pretend the full microscopic detailed-balance factor was determined.

Set `logR=-Delta/(k_B*T)` and `m=(log(kf)+log(kr))/2`; candidate `kf_B=exp(m+logR/2)`, `kr_B=exp(m-logR/2)`. This is the unique least-squares change in the two log coefficients subject to the stated model ratio. It preserves their geometric mean and retains positivity. The candidate is conditional, not a new measured rate or the published Savin pair; accuracy improvement against real scattering is unclaimed. Its numerical T domain equals the fit domain, but all application temperatures below remain10–30000K. No automatic isotope transfer to T,He3,He4,Li6,Li7.

## Constructive reduction and energy ownership

For initial(D0,D+,H0,H+)=(d0,dp,h0,hp), define forward extent x in cm^-3. State=(d0-x,dp+x,h0+x,hp-x), physical interval `L=max(-dp,-h0)`, `U=min(d0,hp)`. With fixed T and a positive pair:

`x'=A*x*x-B*x+C`, `A=kf-kr`, `B=kf*(d0+hp)+kr*(dp+h0)`, `C=kf*d0*hp-kr*dp*h0`.

`s=sqrt(B*B-4*A*C)`. For s>0 and u=-expm1(-s*t),

`x(t)=2*C*u / (B*u+s*(2-u))`.

Use equivalent stable formulas as necessary, without population clipping. Handle t=0, no reactions/all-zero, ND=0, C=0, A=0 and s=0 analytically. For s=0, x=C*t/(1+B*t/2). All input times finite and>=0. The physical interval is invariant: forward flux is inward at L and reverse at U. The finite-H result is not a trace-D approximation. This is an algebraic reduction, not measured speedup.

At fixed temperature the chemical heat `Delta_Uth=-Delta*x` has an opposite external thermostat contribution to keep T fixed; report thermostat ownership explicitly. For an isolated fixed-volume **candidate-only** H/D reaction with thermal spectator particles, let `N_th=sum(21 nuclei/atoms/ions)+n_e,total`, with neutral charge determining a fixed all-thermal n_e for this microbox. No fast electrons are admitted. Then `C_V=1.5*k_B*N_th` is constant and **T(x)=T0-Delta*x/C_V** exactly. Internal chemical energy change is+Delta*x; radiation source0 and total energy conserved. The microscopic candidate is an isolated-channel model, not a complete IGM/cosmological thermal network.

Implement the scalar fraction y=nD+/ND when ND>0: x=ND*(y-y0), H+=hp-x,H0=h0+x; dy/dt=kf_B(T)*(1-y)*(hp-x)-kr_B(T)*y*(h0+x). ND=0 is a stationary face. The domain must retain nonnegative population and T within the source interval; an actual excursion is a STOP with raw evidence, not clipping. Thermal balance is exact by reconstruction, while numerical y evolution still needs solver comparison.

Entropy in this Lambda1 model has dS/dx=k_B*log(exp(-Delta/(k_B*T))*D0*H+/(D+*H0)). Candidate J times this derivative is>=0 since it is k_B*(rf-rr)*log(rf/rr). At zero flux endpoints use an explicit limiting status rather than invalid log/JSON infinity. Raw independent fits need not obey this entropy statement. At T10000 and all four densities0.5, raw J>0 but this affinity<0 is a concrete model-consistency counterexample, not a general no-go theorem.

The total elemental neutral count and total elemental ion count are invariant for this **bilinear exchange channel**, so a trivial elemental number quotient exists. It cannot reconstruct isotope fractions or binding heat. Do not misapply C23C's common-generator theorem, which assumed independently linear isotope blocks. The four-state to one-extent reduction retains isotope identity. A useful bound is `abs(T-T0)<=Delta*min(ND,NH)/C_V`; no claim about the isotope-fraction error follows from this temperature bound alone.

## New inputs and bounded execution

One fresh create-only run ID `c23e_hdx_20261024T<UTC>_v1`. Preserve any failed attempt; never overwrite a run. Before run: observe cpu affinity/cgroup limit/memory/process workload; take a local one-worker lease and set OMP,OPENBLAS,MKL,BLIS,NUMEXPR,VECLIB threads1 before imports. Select one available CPU other than55; reserve coordinator, no external/NCP use. Max new worker wall120s, cpu120s, RAM512MB excluding Python shared environment; no background jobs. Root Wolfram call1 already executed, its cost unknown/null; prior measured CPU subtotal13.331329114s is inherited, not reset.

Inputs: NH=0.1cm^-3; initial H+ fraction0.5; T0 in[43,300,10000]K; ND/NH in[0.000025,1]; initial D+ fraction in[0,1]. These12 cases are illustrative closed microboxes, not a new redshift/IGM history. All other17 species explicitly0. Candidate scalar thermal primary trajectories: DOP853, rtol2e-11,atol2e-13. Define B0 as above at initial T,candidate pair and physical densities; nondimensional tau=B0*t. Sample61points tau0..12. Maximum12 primary ODE trajectories. Four independent Radau comparisons use same equations/input and rtol2e-12,atol2e-14: T43,ND/NH1,both D+ IC; T10000,ND/NH0.000025,both D+ IC. No other ODE trajectories without a concrete failure and root authorization. New cosmological ODE0, source quadrature0, historical replay0.

Additional finite arithmetic controls: raw Table1 fidelity; candidate model detailed balance; integer stoichiometry; 21-key rejection; valid/bad T support; exact isothermal formula against80-digit independent 2x2 matrix exponential for selected states including trace D and degenerate faces; frozen-T vs thermal difference as observation; candidate entropy sign; one raw-fit negative entropy witness; quotient hidden-energy witness. Up to4097 sampled T values on a log grid may diagnose positivity/ratio/correction, explicitly sampled rather than continuous certification. Plot rates/ratios and selected thermal/isotope histories, PNG/PDF, no image-generation.

## Acceptance fixed before execution

1. Source literal fit at every published Table1 knot within numerical fit domain: |fit/table-1|<=0.065 forward,<=0.045 reverse. The extra0.005 accommodates printed-table rounding; this is reproduction, not physical uncertainty. Candidate table errors are reported, not assigned a new literature guarantee.
2. Isothermal closed-form fraction error<=1e-11 against80-digit independent matrix exponential on a finite declared control grid. Absolute abundance error normalized by its own nonzero nuclide total. No fake speedup.
3. Candidate |log(kf_B/kr_B)+Delta/(kBT)|<=3e-13 sampled. Stoichiometry residual exactly0. Report actual min/max rates and corrections, without calling the finite grid a global error bound.
4. Primary/Radau max absolute D fraction difference<=1e-9 and |T_DOP-T_Radau|/max(T0,1K)<=1e-10 at61samples. Returned fractions within physical interval to2e-11; no clipping. Conserved nucleus/charge relative residual<=3e-13, energy-change residual divided by max(CV*T0,Delta*ND,1e-30)<=3e-13. The latter tests reconstruction/accounting, not whole-network dynamics.
5. For positive interior fluxes candidate entropy production >=-1e-13 times kB*(rf+rr) (roundoff allowance). Explicit record for boundary limit. Nonpositive temperatures or actual coverage exit stop admission.
6. All tests and budgets retain actual counts. C9 reviewer evaluates physical appropriateness of claims, not just assertions. Full21 rates, empirical error confidence, full thermochemical/UV/stars/nuclear network, global cosmology and physical stopping remain OPEN; global_error_bound=null. Full nuclear high-energy and general triaxial/tilted/polarized CMB HOLD.

## Deliverables and positive transition

Standalone source provider + scalar/analytic microbox code, table-fact input with attribution, exact reused21-species helper and license, machine raw outputs, numerical/physics diagnostics and figures. Report commands, environment, resource and CPU/wall receipt, source hashes, all attempted trajectories. Root integrates theory, R/C ledger, claim gate and next DAG, obtains one fresh Astra review, then publishes additive science commit and draft PR with expected-SHA updates. Canonical release ZIP gets R3 Library/Dropbox readback once; Drive new unique artifact gets one bounded attempt and honest receipt status. Preserve unknown historical Drive states. Minimal copyable handoff records science S/document D/central M independently.

EXECUTION: CONTRACT_FROZEN; actual Wolfram symbolic/rate diagnostic1, new local ODE0 atfreeze. PUBLICATION: NEW_PENDING. BACKUP: C23D prior R3 reused; new checkpoint local. DAG: N5_HD_CX candidate child IN_PROGRESS; full N5 OPEN.
