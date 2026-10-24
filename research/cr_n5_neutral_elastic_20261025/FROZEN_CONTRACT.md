# N5 neutral elastic finite-temperature energy exchange — frozen contract
Version 1, frozen 2026-10-25 KST (UTC 2026-10-24).
Unit: CR_N5_NEUTRAL_ELASTIC_FINITE_T
Consumer: N5_C23D_H1_HE4_NEUTRAL_ELASTIC_V1

## Question and baseline
Measure the conditional change in the existing C23D-source EE+EI+H(1S→2S/2P) first-stop finite chain when leading heavy-neutral elastic energy exchange is added. Baseline science is PR103 S d3d9b0de8796de6e988c0d95540b1dbbe1d1cff3, documents D bdcb576f4202be81b7436726eca6b588029de840. Reuse saved eight grids, invariant weights, EE and EI conductances/generators, CE hazards/RHS, source projections, and all baseline results. Do not call the old generator, project the source again, or rerun PR103.

## Physical input and scope
Stationary isotropic prescribed Maxwell baths: Te=Ti=Tn=10000 K, theta=0.8617333262145178 eV, ne=0.14 cm^-3, prescribed lnLambda=20. HI=0.9, HII=0.1, HeI=0.07, HeII=0.02, HeIII=0.01 cm^-3. Assign neutral HI to H1(1S), HeI to He4(1S) conditionally. Neutral mass ratios M/me are 1837.152673426 and 7296.29954171, obtained by adding bound-electron masses to the PR103 inertia convention; binding mass defects are neglected explicitly. Do not use the coarsely rounded LXCat header mass ratios as the calculation masses.
Closed box, no escape, initial selected source 0<W<10 eV from three saved z=2.316,2.479,2.649 atom arrays. Exposure10000 proper seconds defines the impulsive population, not continuous photoionization chemistry.
Active first-entry thresholds q=chi*theta for chi=1.5,3; reflecting U=R*theta for R=40,80; reuse both nominal N=1024,2048 grids. Only E>=q is the physical neutral consumer domain; the initial 10 eV selection is not a path ceiling. Below-q particles retain their own initial energy and immediate first-entry convention. Neutral coefficients below active q are null/out of scope, including energies below database support.
D/T/He3/Li6/Li7 densities and missing CI/RR/DR/CX/other channels remain null. Current atomic ground-state chemistry and isotropic energy closure do not close a thermal/UV/stars/nuclear network or nonbaryonic Vlasov stress.

## Source contract
CCC via LXCat H(1S) ELASTIC/MTCS process25646: 91 rows, [0.01,1000]eV, m²; sha256 98ed242085006cc5f73057a7013c9fcd93b973349e9d2235fbbe5fb807f4bff0,8954bytes.
CCC via LXCat He(s1S) ELASTIC/MTCS process25758:87 rows,[0.1361,1360.6]eV,m²; sha256 bcf1bae983ea0f2e75ef6cce184cc3b80d370e677f26409efdabe5c5f1e0f4b1,9224bytes.
Strictly increasing E and positive finite sigma; piecewise-linear sigma(E) on native support; no extrapolation. At knots use D directly for conductances; derivative diagnostics have a declared right-interval convention (last endpoint left). These are MTCS, not total elastic cross sections or total/effective momentum cross sections. Integrated CCC2026 ZIPs alone do not provide MTCS. He MTCS method/source is CCC(171),2013 database return; it is not relabelled as a newly published2026 calculation.
Raw database files remain private research inputs; public Git publishes source identities, retrieval procedure and derived consumer results. Do not publicly publish raw tables or dense coefficient plots that reconstruct them. Private canonical backup may retain user's research inputs. Public numerical outputs should be integrated source summaries and finite-matrix checks; full arrays belong in the private canonical package.

## Leading heavy-neutral operator
For epsilon=me/M, nu_m(E)=n_N*sqrt(2*E*e_J/me)*sigma_m(E), with density in SI or consistently converted cm units:
D_N(E)=2*epsilon*theta_N*E*nu_m(E), Var(dE)=2*D_N dt.
mu_N=D_N' + D_N*(1/(2E)-1/theta_N)
=2*epsilon*nu_m*[theta_N*(2+E*sigma_m'/sigma_m)-E].
Probability density is p(E) per eV, equilibrium pi_cont ∝sqrt(E)exp(-E/theta_N).
This is the standard leading heavy-neutral recoil/thermal operator, transformed from the energy-distribution convention in Hagelaar & Pitchford2005 Eq27; the project contribution is its source/data/finite-chain binding, not a new collision theorem. Accuracy of the physical approximation is not globally certified. Exact finite-mass diffusion would require further angular information. No finite elastic event hazard/count is inferred from MTCS.
At active q the expansion control theta/(r*E) is small; quantify its maximum as a diagnostic, not a proved error bound. No extrapolation of this interpretation to all initial sub-q source energies.
Also quantify the separate omitted cold-recoil diffusion diagnostic 2*E/(r*theta), whose upper-grid maximum is 2R/r from sigma_2<=2 sigma_m. This is not a global physical-error bound. Native MTCS uses the nucleus-rest/heavy-target incident-energy convention; exact finite-mass frame corrections are outside the adopted leading operator.

## Discrete algorithm and energy ownership
For each inherited edge midpoint, c_N=c_EE*D_N/D_EE with analytic D_EE=theta*b_anchor*sqrt(theta/E)*P(3/2,E/theta), b_anchor=2.3306698113646996e-5 eV/s. This evaluates the new ratio without rerunning the old generator. Construct only the two new neutral detailed-balance generators. Add their off-diagonal rates to the stored PR103 total generator. Use the stored pi and native grid exactly.
K_new=K_old - Q_N,active^T. Preserve stored CE source RHS and update the first-entry RHS with the added q-edge rate. Solve six probability/time/incoming-energy RHS, two conditional-time RHS, and six bath-reward RHS (EE, three ion species, H1neutral, He4neutral):14 RHS per8 cases,112 total.
Bath gain reward is -Q_species^T E, including q-edge increments. Reuse four stored PR103 bath RHS; only two new neutral reward columns are generated. The energy identity is:
initial selected kinetic energy = all six bath gains + first-entry energy + inactive own energy + CE outgoing kinetic energy + CE internal energy.
CE internal gap10.20435eV is separate from bath heat. Electron/neutral species, charge and nuclei are conserved by elastic channels. First entry is diagnostic, not irreversible assimilation/Maxwellization.
No-CE MFPT uses the inherited birth-death flux formula with new total conductance. Let delta=max_edges(c_H+c_He)/c_old; then Told/(1+delta)<=Tnew<=Told on the identical finite chain. This finite-chain inequality is a reused comparison argument, not a global physical error bound.

## Acceptance and execution
Preserve inherited FP64 tolerances: generator2e-13; scaled linear residual2e-12; probability2e-10; partition2e-8; energy ledger2e-8; backward MFPT2e-12; finite-chain bound2e-10. Compare N1024→2048 relative changes<=0.005 for principal source observables including neutral heat; neutral-induced CE relative-change convergence1% with absolute floor1e-10. R40→80 relative changes<=1e-5, induced CE absolute change<=1e-7. If any fails, retain the failure, diagnose and change only affected calculations/new run IDs.
Controls must test source identity/parsing/units/support, rejection of missing species/outside support/unequal bath temperatures; constant/power-law coefficients and Maxwell zero flux; zero-density and infinite-mass limits; sign and cold recoil convention; positive detailed balance and finite-chain conservation. A bounded constant-cross-section exact Maxwell-target first-moment comparison is optional only if needed for the remaining approximation risk; any such new quadrature must be counted.
Independent reviewer must recompute selected new coefficients separately and solve selected finest matrices including all14 physical RHS at higher precision or an independent adequate method; report exact RHS types/counts. Do not repeat PR103's overbroad C9 time wording.
Runs: n5_neutral_controls_20261025_v1; n5_neutral_primary_20261025_v1; n5_neutral_saved_plot_20261025_v1; independent review gets its own run ID.
New ODE0, source quadrature0, old science replay0. Planned new neutral generators16, combined matrices8, primary RHS112, source rows24, finite comparisons18. Figures use saved integrated results, not database-reconstructing curves.
Inherited known science-worker CPU29.870022114s; never reset. New-unit ceiling60CPU s including failures, controls5/primary10/review10/plots5CPU s individual; wall20/40/40/20s, one worker at a time, native threads1, RLIMIT_AS512MiB. Actual affinity0–8/quota8/memory8GiB observed; admit again immediately before each child. WorkerCPU0, reviewerCPU1, coordinatorCPU8; CPU55 absent and must not be presumed. External NCP/lease UNOBSERVED. Use create-only outputs, own task lease, preserve all failed attempts. Mechanical packaging/IO/CAS costs are separate and unknown global spend/remaining/money null.

## Publication, backup and completion
Use separate science and documents commits on research/cr-n5-neutral-elastic-20261025, parent pinned PR103 D. Preserve active owners and refresh actual expected SHA for each ref update, including central DAG. Draft PR remains unmerged.
Maintain per-stage EXECUTION|PUBLICATION|BACKUP|DAG records. Freeze checkpoint before numerical execution, intermediate execution checkpoint, then final canonical ZIP and postcanonical terminal authority; use actual provider acknowledgement and requested canonical R3 verification. Reconcile prior exactname+folder DriveUNKNOWN before any resend; do not turn historical unknowns into success.
Scope gate is conditional numerical admission of this neutral FP finite chain after R6/C9. Parent CR_N5_ATOMIC_ISOTOPE_COVERAGE and N4 remain PARTIAL/OPEN; N6 conservative coupling and N7 new parcel remain gated. Missing omitted-process ranking, global_error_bound and global_completion_percent remain null.
