# C16 scientifically conditional intake for rei_bianchi SOURCE07

Source: bass_cr C16 independent q-ray numerical supplier.
Owner rei_bianchi HEAD 0fcb2dddf5de6b583c2e00f150abff0b2afb6315,
preserved read-only. The C16 source is not merged into Rust.

Input contract:
- Source rate Scenario.rate(a), photons per original H proper second.
- Species proper n_HI,n_HeI,n_HeII in cm^-3 and Verner sigma(E) cm^2.
- Physical E(a) from owner Bianchi-I tetrad direction mapping,
  q signed; source birth photon-N/H measure and external R*J
  to be mapped ONCE in the receiving canonical implementation.
- Nonnegative photon stock, source endpoint rates S0,S1,
  H/He opacity endpoint arrays lambda0_j,lambda1_j.
- Proper dt seconds and exact photon-source ledger.

Algorithm: use positive optical-quadrature for piecewise affine time
source/opacity, carefully split interval at sigma threshold roots:
13.60 eV HI, 24.59 eV HeI, 54.42 eV HeII, and one-sided values.
This provides 2nd-order photon survivor convergence vs Radau in
controlled fixed-ion-fraction real-owner Bianchi q model.

Do NOT assume the observed 2nd order transfers to:
dynamic gas H/He/T, OTS, current-frame flux J or source spectrum
that was modified by previous opacity, or actual source-age ray
intensity. The standalone q-channel prototype injects in fixed
birth-energy labels by DESIGN. Actual owner spectral advection must
be a separate, verified adapter.

When lambda_j(t) varies, allocation of TOTAL photoevents to species
is a positive *weighted approximation*. Its species-level
convergence is not yet independently certified, even though the
total photon-number ledger closes.

The fast endpoint approximation can lose high packet precision
near threshold; do not select by speed alone. Future tests:
full ray source spectra, partial opacity crossing and source
frequency-advection ledger, true ionization/recombination/thermal
system with rigorous independent stiff baseline. Hold current
SOURCE07 C8 / AX08 / AX11 / AX12 admission states.
