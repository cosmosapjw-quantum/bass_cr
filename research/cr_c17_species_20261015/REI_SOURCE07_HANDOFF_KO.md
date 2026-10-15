# C17 receiver contract: precise H/He temporal photoevents

The existing canonical owner rei_bianchi/source07 Rust state remains
untouched at commit 0fcb2dddf5de6b583c2e00f150abff0b2afb6315.
C17 is an independently reproducible bass_cr Python supplier.

The input and output, all per original H except proper rates:
- Input: photon stock N_k>=0, proper source S0,S1 photons/(H s),
  species HI/HeI/HeII proper absorption rates lambda_kj,0 and
  lambda_kj,1 in s^-1, proper dt>0 s, prepartitioned ionization
  threshold events and owner source/clock/geometry identity.
- Output: survivor N_k and positive species event A_kj, with
  per-packet identity Nstart+dt(S0+S1)/2=Nend+sum_j A_kj.
- Optional: M_kj=integral_0^dt(t/dt)lambda_j(t)N(t)dt to compute
  affine photon-energy photoelectron heat with physical I_j:
  Q_kj=(E0-I_j)A_kj+(E1-E0)M_kj. Reject active in-step
  threshold crossing instead of inventing a heat sign correction.
- H and helium gas fraction updates per original hydrogen count:
  dxHI=-A_HI; dxHeI=-A_HeI/y;
  dxHeII=(A_HeI-A_HeII)/y; dxHeIII=A_HeII/y;
  dx_e=A_HI+A_HeI+A_HeII.

The C16 effective branching fraction is not acceptable as a
generic per-species time-dependent photoionization source: it can
assign the same conserved total photon losses to the wrong species
by nearly a full photon/H in an explicit affine-rate counterexample.
C17 integrates species rates over the actual time-ordered photon
stock and validates against independent Radau species ODE.

Global limitations:
1. The owner SOURCE07 true transported age/ray photon measure,
   R J_Omega and photon time/temperature clocks are not attached.
   Current q benchmark assigns sources to five manufactured
   fixed energy channels with real owner Verner/Scenario inputs.
2. Species/photoheat integrals are numerically positive and
   constrained by an independent quadrature-fidelity test;
   not formally interval-certified for all stiff opacities.
3. Ionization fractions, n_e, recombination and T do NOT evolve
   during a local affine-opacity step. Full igm_rates/igm_thermal,
   secondary ionization and OTS need actual owner coupling.
4. C16 photon-survivor temporal threshold partition remains a
   prerequisite; never interpolate across H/He spectral jumps.
5. Global SOURCE07 C8/AX08/AX11/AX12 scientific gates remain HOLD.

Next: enable owner Rust source-age ray packet import with exact
frame/normalization tests and add coupled H/He gas-state and
photoheating with independent fully stiff short-step reference.
