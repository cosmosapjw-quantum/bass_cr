# BASS193 IGM H+–H drift-energy reservoir | THEORY (2026-11-01)

## R1/R2/R3: question, source, assumptions
Question: On 192 source-frozen REI BASS193 time intervals, what *maximum* H-only internal heating can a pre-existing small ion-neutral relative drift supply without sustained external forcing? This is an energy-budget diagnostic, not a new evolving Bianchi IGM model. Scientific source lineage: immutable REI PR311 HEAD 63052797e382b438ef375e8389f539118a7e2a0c, private original ZIP SHA256 4f2682e5885040fa69f0fe05095505cb7724b2d84c4707af8e1a78c8db41cb52 (parent PR155 reported crosswalk; original ZIP not independently read here). Exact public derived CSV SHA256 f47f1379503dba93f1583a8cb2b2cdb61fa856f9e0e485140d62fce329600f03; Git blob 62290340fd338e1105e44739823d2ff267377f52 from PR155. Sources for context: Schultz et al. (2016) J. Phys. B 49 084004 DOI 10.1088/0953-4075/49/8/084004; Glassgold, Krstic & Schultz (2005) ApJ 621 808 DOI 10.1086/427686. No original full 2016/2023 quantum DCS retrieved (UGA TIMEOUT).

Assume nonrelativistic two-fluid H+ and H with positive masses mi and mn, nonnegative densities ni and nn, common source-saved T>0, no external forcing during a *fixed-density, fixed-volume, collision-only* substep, no internal excitation/binding energy change from resonant exchange, no cosmic expansion/shear, ionization, photoheating, electrons or helium heat capacity *inside this substep*. Initial velocities ui, un and no ongoing creation of relative kinetic energy. REI source T and densities are input snapshots, not solved variables. Epsilon=|ui-un|/a is a prescribed small perturbative ratio, NOT a recovered finite Bianchi tilt. Geometry, external forces and particle exchange outside the collision-only substep can replenish drift energy and invalidate a global bound.

## R4/R5: exact construction
Define M=mi+mn, mu=mi mn/M, rho_i=mi ni, rho_n=mn nn, rho_tot=rho_i+rho_n and rho_red=rho_i rho_n/rho_tot. Then
  (rho_i ui^2+rho_n un^2)/2 = rho_tot V^2/2 + rho_red |ui-un|^2/2,
  V=(rho_i ui+rho_n un)/rho_tot.
The *only* relative-mode kinetic reservoir at fixed total momentum is Edrift=rho_red U^2/2. The common-temperature relative Maxwell width is a^2=2 kB T (1/mi+1/mn)=2 kB T/mu. Write U=epsilon*a.
The H-only monatomic internal energy is EH=3/2(ni+nn) kB T. If collision dynamics exhausts initial Edrift into H-only internal heat, with no external work, the maximum fractional temperature rise is
  DeltaTmax/T = Edrift/EH
              = (2/3)*rho_red/(mu*(ni+nn))*epsilon^2
              = (2/3)*(mi+mn)*ni*nn/[(mi ni+mn nn)*(ni+nn)]*epsilon^2.
At equal masses, x=ni/(ni+nn), this is (4/3)*x*(1-x)*epsilon^2 <= epsilon^2/3. For epsilon=0.1 the universal H-only upper bound is 0.0033333333333333335.

## R6/R7: hostile analytic/CAS checks
Dimensions: rho_red U^2 is erg/cm^3; EH is erg/cm^3; ratio and epsilon dimensionless. Nonnegative, vanishes when either species density is zero, invariant on swapping ion and neutral including masses. No direct scalar HI/HII/electron source from resonant H charge exchange; no direct Thomson-opacity change. Mathematica/Wolfram FullSimplify: general coefficient 2 eps^2 (mi+mn) ni nn/[3(ni+nn)(mi ni+mn nn)]; equal-mass 4 eps^2 x(1-x)/3; MaxValue on 0<=x<=1 -> eps^2/3. Independent of any unverified low-energy angular scattering fit.
Careful counterexample to any *global* IGM heating bound: ionization, shear, pressure gradients, externally driven ion-neutral drift or evolving densities can inject new relative energy. Therefore this is a per-snapshot reservoir ceiling for collision-only conversion, not a bound on all future heating. Includes *no* CMB optical-depth, polarization or Bianchi transport claim.

## R8/R9/R10: decision and computational interface
Adopt this rigorous local algebraic bound as source-conditioned DIAGNOSTIC only. For each 192-row source snapshot compute x, rho_red, a, Edrift, EH, Edrift/EH, and Edrift/nH (eV/H); for a prescribed frozen-source linear A7 collision frequency nu, optionally compute collision-only single-bin transfer Edep/Edrift=-expm1(-2 nu dt). This kinetic coefficient is model-conditional and NEVER establishes the exact quantum joint elastic+CX operator. Never sum separately normalized per-bin energy reservoirs into a single IGM history.
Keep REI central 28/88, REI working 33/88, CR extension 0/3, delta=0. NO_REI_MUTATION, NO_MERGE, NO_FORCE_PUSH, CR-OFF unchanged, PRODUCTION HOLD. R stages record one coherent science result, not new central milestones.
