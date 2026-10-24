# N5 channel-resolved first-CE event consumer — frozen contract v1

## R1/C1 authority and purpose

Date 2026-10-24 UTC. Root Astra frames and admits; mechanical executor requested gpt-6.1-sol, observed model UNOBSERVED. Base bass_cr Documents D `b65befa5187d3e1e11574a98dcadd2032831de72` (PR101). New additive unit `CR_N5_CE_KILLED_GENERATOR_FIRST_EVENT`, consumer `N5_C23D_HI_CE_RESOLVENT_V1`, branch `research/cr-n5-ce-resolvent-20261024`. Scope is a conditional finite-state diagnostic inside partial N5, not N6/N7 activation. The current user explicitly authorizes next theory/code loops and publication/backups.

The new result is the source-weighted probability that a tagged electron undergoes its first H1 1s→2s or 1s→2p excitation before its first entry into E≤q. PR101 supplied only a maximum-hazard/mean-time upper estimate. Reuse the standard Feynman–Kac/killed-chain result and existing scientific providers; the contribution is their source-pinned consumer connection and new channel-resolved numerical values. No new general theorem or no-go claim.

## R2 evidence and nonduplication

Seven-repo metadata survey 04:41:26–04:43:17 UTC: 1321 branches,856 open PRs,29 pages,14 collections exhausted. Actual new owner returns HE95/WU143/BASS186/REC132/VigilODE85/central222 inspected separately. No new admitted stopping provider. PHYS84 numerical WAIT; PHYS85/86 active owner reference/moment work must not be duplicated; HE-ANG full joint law remains pending. Full other conversation transcripts are unavailable; personal-context excerpts are separately labeled. Survey files live at `continuation_survey/` until packaged into intake.

PR59 `reversible_generator` and Maxwell coefficients are already completed. C23D source atoms and anchor are saved results. Its saved finite population grids were R40, N256/512, z2.479. This unit assembles NEW R40/R80 matrices using the unchanged provider; it does not claim a saved R80 matrix. PR101 `theory/THEORY_REVIEW.md` section4 already derives the backward survival equation; that derivation is reused. New work is its actual channel-resolved/source-conditioned finite-chain realization, with event-energy/time rewards. Existing PR60–64 nonlinear work and historical9600 fullBED heat-delay resolvents are different scopes and are not replayed.

## R3/C2 fixed physical input

- T=10000 K; thermal ne=0.14 cm^-3; prescribed lnLambda=20; proper seconds; stationary heavy, unpolarized H1 target; closed box/no escape.
- theta=0.8617333262145178 eV and EE physical rate/loss anchor are read from saved C23D `APPLICABILITY.json`, without recomputing old source/MFPT work.
- Ground H1 density n1s=0.9 cm^-3, exactly the additional PR101 conditional closure. n2s/n2p and all unselected/missing providers remain null, not zero. No D/T/He/Li isotope transfer.
- Reuse all three saved `ATOMS_2.316.csv`, `ATOMS_2.479.csv`, `ATOMS_2.649.csv`. Their `pulse_count_cm3` is an impulsive population defined by 10000 proper seconds exposure, not a chemistry integral. Initial selection 0<W<10 eV is not a path-energy ceiling.
- q=chi*theta, chi∈{1.5,3}. Upper reflecting energies U=R*theta, R∈{40,80}; R80 is primary, R40 is a finite-boundary comparison.
- H1 CE gap and source interpolation are exactly PHYS83: Delta=10.20435 eV, W(E)=E sigma(E) piecewise linear on native knots, threshold zero at/below Delta, native upper968.6058 eV. Physical constants for this hazard are the pinned PHYS83 EV_J/ME_KG, not substituted constants.
- h_c(E)=n1s*100*sqrt(2 EV_J/ME_KG)*W_c(E)/sqrt(E), units s^-1. Only constructor arrays are consumed; no `moments`, `evaluate`, rate quadrature or PHYS84 source callback.
- Original nuclear PNG NOT_RECOVERED_NOT_READ; global_error_bound=null, global_completion_percent=null. Non-tilted LRS/full Frobenius and signed amplitude/norm/cancellation scope unchanged. No new anisotropic stress or nonbaryonic Vlasov equivalence.

## R4–R5/C3 mathematics and representation

Full Q acts on column populations. On nodes E0=q<E1<...<Em=U, restrict transient A=Q[1:,1:] retaining loss to node0. Backward G=A.T; a=-G*1=Q[0,1:]. For h=h_2S+h_2P, K=diag(h)-G.

Solve K u_c=h_c, K u_abs=a, K t=1. The vector u_c is the joint first-event channel probability, u_abs first-entry-before-CE probability, t mean time until either outcome. Solve K r_c=E*h_c for event incoming-energy moment and K v_c=u_c for channel-weighted first-event time. Then conditional incident energy=(source·r_c)/(source·u_c), conditional event time=(source·v_c)/(source·u_c). A zero denominator produces null, not a fabricated mean.

For a useful new occupation comparison, solve (-G) w=h (expected integrated CE hazard on the unmarked path). This is a new RHS on this new grid, not an old MFPT calculation. Positivity gives 0≤u_2S+u_2P≤w. No continuum MFPT integral or ODE is executed. PR101 upper estimates are reused as descriptive prior comparators, not asserted as a certified inequality for a different discretization.

Probability partition u_2S+u_2P+u_abs=1 follows because K1=h+a and the finite chain reaches absorption. Standard M-matrix/positive semigroup reasoning establishes nonnegativity. Do not compute CE as 1-u_abs, which loses relative accuracy for rare events; solve positive channel RHS directly.

Grid: base geometric nodes `geomspace(q,80*theta,N+1)`, N∈{512,1024,2048}; add exact q,10eV,40theta,80theta,Delta when inside the band, deduplicate. The exact10eV source-support knot prevents any original W<10 atom from projecting above10eV or into an initially CE-active node. The exactDelta knot retains the physical zero threshold. R40 uses the common prefix ending at40theta; R80 uses full grid. This keeps below-R40 nodes identical between boundary comparisons. Use unchanged PR59 constructor and physical coefficients. Retain diagonals/source/hazard/raw solutions; dense Q may be discarded after extracting bands to bound memory.

For each original source, retain original active mask W>q and exact active/selected totals. Project only active atoms linearly to the q..U grid using count/energy-conserving nonnegative interpolation. Any projected mass on boundary node0 has probability0 and time0; include it in active normalization and report its fraction explicitly. Atoms originally≤q have time0 and no pre-entry mark. Require initial projected mass above10eV and on positive-CE-hazard nodes exactly0. Compute both original-active and whole-selected averages. This finite-grid interpretation must be explicit.

CE event bookkeeping: e(E)+H1(1s)→e(E-Delta)+H1(2l). Charge and H1 nuclei unchanged; tagged electron number unchanged; internal energy gains Delta and electron kinetic energy loses Delta. Killing terminates the diagnostic at the event; it is not physical electron removal or irreversible thermal assimilation. Expected first-event internal excitation energy is Delta*(P2S+P2P); subsequent evolution/radiation/heat is not solved.

## R6/C6–C9 acceptance and stopping rule

Before primary run, independent theory review of matrix orientation, source projection, probabilities/rewards, energy bookkeeping and scope. Wolfram two-transient-state check is complete with five true identities, saved raw response; it is a toy algebra witness, not production data. Primary literature search is background only; molecular/screened results are not adopted as neutral-H providers.

Targeted implementation controls: exact rational two-transient-state example with threshold-only high-state hazard; zero-hazard case uCE=0,uabs=1; single channel absent by explicit control gives exact0; small mark multiplier tends to (-G)^-1h; missing or negative physical rates rejected rather than silently zero; matrix orientation/column sums checked; no clipping of computed probabilities. Fix toy a=2,b=3,c=5,x=7,y=11 in consistent arbitrary inverse-time units. The common multiplier lambda scales BOTH CE channels; physical primary lambda=1 only. Toy controls lambda∈{0,1e-8,1} and one explicit absent-channel case are test work, charged within the test child and recorded separately from the12 physical matrix cases. Compare direct channel probabilities to the rational formula with abs tolerance1e-15 plus relative5e-13; exact-zero RHS requires exact-zero solution. At lambda=1e-8, u_total/lambda versus the limiting vector (x+y)(b,a+b)/(a c) must agree to relative1e-6. Monotonicity/concavity are claims about total CE, not generally individual competing channels. No production density scan is authorized by these controls.

Primary numeric obligations: componentwise scaled linear residual≤2e-12, defined rowwise as |Kx-b|/(|K||x|+|b|); when the denominator is exactly0, residual must also be exactly0 and the ratio is recorded0 (otherwise fail); no arbitrary positive scale floor. Probability partition max absolute defect≤2e-8; probabilities in[-2e-10,1+2e-10] with actual deviations reported; uCE≤w with absolute2e-10 allowance; generator sign/column conservation scaled≤2e-13 with denominator sum_i |Q_ij| (the same exact-zero convention); count/energy projection relative errors≤2e-12; event kinetic/internal energy relative residual≤2e-14. Denominator-safe tests for tiny positive CE values use relative and absolute terms explicitly.

Grid consistency: for all six source/chi cases and both CE channels+sum, finest2048 vs1024 relative probability change≤5e-3; compare512 without requiring it to pass. Event mean energy/time changes≤1e-2. R40 vsR80 finest source probability relative difference≤1e-5. These are finite comparisons, not rigorous continuum/global error bounds. A failed comparison is retained; no auto-relaxation. Return concrete failure to root; at most one root-authorized changed-dependency refinement/repair. The scoped finite-discretization result can remain useful even if continuum comparison stays open, but must be labeled accordingly.

Independent C9 receives raw arrays and exact frozen inputs, not only implementation outputs. Reconstruct selected rows with an independent tridiagonal reference at high precision and compare direct/adjoint source-weighted probability; inspect physical gates and counts. Reuse unchanged providers/tests, no broad optional suites.

## C4 resources and budget

Actual host CPUs0–8, quota8, RAM8GiB; CPU55 unavailable. Coordinator CPU8, one science worker CPU0, native threads1. Local create-only exclusive lease and unique run directories; check current /proc workers and cgroup memory/events before launch. Much current memory is reclaimable file cache; record anon/file/dirty/kernel separately. Enforce512MiB address-space RLIMIT_AS and record actual peak RSS (do not claim RLIMIT_RSS enforces Linux memory limits); CPU cap30s, wall cap60s per bounded primary. One targeted-test child≤10CPU s/30wall, independent review≤10CPU s/30wall. No NCP or external lease assumed. Preserve every failed/prelaunch attempt and measured cost; request root diagnosis at actual limits.

Inherited known bounded worker subtotal19.209296114 s. Separate prior coordinator and mechanical costs remain separately labeled; global spend/remaining/currency/unmeasured costs stay null. New science counts: twelve new finite matrices (2chi×2R×3N); positive-channel/reward/occupation linear solves are new. New ODE0, source quadrature0, thermal-rate quadrature0, old science replay0. Record actual counts if an attempt stops early.

## C5 allowed paths and publication/backup

Executor may create only this unit's `implementation/`, `inputs/`, `runs/` and mechanically prepared `intake/` copies; do not edit old science or other owners. Root writes scientific conclusions/decisions. Exact input SHA manifest once; proportional integrity, no new security/governance layer.

After independent admission publish additive Draft PR using expected SHA, preserve current parallel central changes, update only named child observation/handoff. No merge. Canonical create-only ZIP and terminal authority: Library/Dropbox actual-byte R3; Drive truthful ACK/reconciliation, no blind retries. Reconcile previous exact names/folder before any retry. Every R1–R10/C1–C10 records EXECUTION | PUBLICATION | BACKUP | DAG. Full N4/N5 remain PARTIAL/OPEN; next provider admission remains gated; N6/N7 are not activated.
