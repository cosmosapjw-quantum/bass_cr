# SOURCE07 C8 - C12 research supplier intake, NOT production admission

Source: bass_cr physical_age C12, independent Python model and numerical
validation derived from fixed actual rei_bianchi owner source read-only.
C11 parent identity 43db96b8457842c4bbc945f5b9e4c14f2f831d9f.
Owner branch reference 0fcb2dddf5de6b583c2e00f150abff0b2afb6315.

## Preserved interfaces

- Input q_ref and a_ref=.047619..., reception a=.2. Age weight is
  emitted_photons_per_original_H = Scenario.rate(a)/H(a,q)dln(a).
- Photon packet E_phys = R(a,q,mu)E_emit (eV), local photon number per
  original H; no owner transport Jacobian R*J applied a second time.
- Chemistry proper nH, nHe (cm^-3), xHI, xHeI,xHeII,xHeIII, electron
  fraction from exact charge neutrality. Proper dt (s).
- Photoionization (HI,HeI,HeII) and species-specific photoelectron
  heat (eV/H); Verner thresholds and physical binding distinct.
- LEDGER: delta photons = sum_j A_j and lost photon energy =
  sum_j heat_j + sum_j I_j A_j, nuclei and electrons conserved.
- Exact photon exponential plus midpoint gas predictor verified
  second order relative independent simultaneous DOP853.

## Numerical new supply and limits

- 48 original source-age nodes, positive 13 age-node 3-state
  compression. SVD-based nullspace pruning with source original
  full training moment residual gate 1e-10. Physically time-weighted
  SOURCE (model parametrization), not actual prior-ray opacity.
- Read actual outputs: SCIENTIFIC_VALIDATION.json,
  SOURCE_WEIGHTED_DOP853.json, PARALLEL_BENCHMARK.json,
  TIME_CONVERGENCE.png.
- Age/Spectrum integration cross-check with QUADPACK; 3-signed q.
  No event/temperature convergence admission for real EoR history.
- If an owner ray already has evolved true age-bucket photon
  populations, do NOT overwrite them with these free-streaming
  source-age weights; those spectra are materially different.
- Do not mistake 4.44659 emitted photons/H as the present neutral
  gas's local radiative inventory without transport and absorption.
- This is a candidate validation library for source-age reduction
  and local H/He photon-budget conservation in separate owner
  tests, not a new canonical runtime or changed SOURCE07 C8 gate.
- Resolved local C12 objective: initial source rate and dynamic gas
  short benchmark, positive compression, independent DOP853,
  vectorization and small OS-process scaling.

## Ready next constructive owner-side questions

1. Integrate authenticated actual emission epochs with true
   transported/binned radiation stocks, angular/source ray R*J,
   preexisting age-dependent opacity and HeII/HeIII foreground.
2. Couple H/He/electron/temperature to recombination/cooling/OTS,
   evolve together, and match independent full-physics reference.
3. Use physical photon/thermal ledgers, time/age/angular/energy
   refinement, error allocation and real CPU/memory before
   deciding Rust C8 integration. Preserve all C8 and AX08 holdouts.
