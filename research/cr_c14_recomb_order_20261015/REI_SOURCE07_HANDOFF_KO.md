# SOURCE07 C8 numerical-method supplier from bass_cr C14

Pinned owner: rei_bianchi commit 0fcb2dddf5de6b583c2e00f150abff0b2afb6315.
Parent C13: eef456cd3f72b4d8c699e6454e04ed405099b436.
Physics units: proper electron density cm^-3, photon counts per original
H, emitted source photons/H/s, local proper time seconds, E in eV.

Receiver-side useful contracts:
- H/He Case-A pure recombination exact Markov exponential can be
  evaluated at a scalar nonnegative self-consistent midpoint n_e.
  This restores 2nd order in the pure-recombination limited subproblem
  while preserving positive H/He fractions, nuclei/charge and energy.
- At a constant-gas, constant-source short proper interval, a positive
  exponential Duhamel photon update gives exact in-step source retention
  and species photoevents. It does not synthesize unknown hardened
  spectral shape from parent N,U.
- Do not allocate 0-mass source packet lists when emission is zero.

Blocking distinctions:
- Real owner photon age/ray geometry and R*J must be bound to the
  source-intensity frame before any production import.
- Coupled gas opacity varies in time, and true initial photon stocks
  are not necessarily zero: exact constant-coefficient formula does
  not imply full time-dependent RT exactness.
- Full Grackle thermal, H/He recombination emissivity and OTS are
  not represented by C13 toy free electron escape closure.
- Full C13 gas response remains numerically first-order-like in
  active source experiments; retain the production HOLD and
  independent referent. AX08/AX11/AX12 unchanged.
