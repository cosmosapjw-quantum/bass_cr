# BASS_CR → rei_bianchi SOURCE07 C8: HeII-resolved positive age quadrature

## Question and protected scope

Investigate whether SOURCE07 C8 positive compression of 36 photon-source ages
remains accurate for hydrogen and nonzero HeII as receiving proper H/He gas
changes. Hold fixed the owner's 50,000 K blackbody source, emitted energy
13.6–100 eV, Bianchi-I directional energy ratios, Verner HI/HeI/HeII
cross sections, physical binding energies and original 12-angle/16-energy
threshold-split Gauss quadratures. No owner chemistry, radiation Jacobian,
full source history, AX08 or Rust runtime is modified.

## Definition → derivation → computational form

At source age a and angular direction mu, received physical energy is
E = R(a,q,mu) E_emitted. Gas density n_j is in proper cm^-3, sigma_j(E)
is in cm^2, and dt is in proper seconds. Set

    tau_j(E) = c dt n_j sigma_j(E)
    tau = sum_j tau_j
    g(tau) = (1-exp(-tau))/tau, with g(0)=1
    P_j(E) = tau_j g(tau).

This is photon absorption/photoionization, NOT resonant H+H charge exchange.
The photoelectron heat per absorbed species is P_j(E) (E-I_j), with I_j
the physical species binding energy, and sigma_j nonzero only above
the fit's corresponding threshold.

Each age/gas has eight source-weighted moments: number, received photon
energy, three species absorption counts and three species photoelectron
heat terms. The owner 5 moments (number, energy, HI/HeI counts and summed
heat) are recovered by projecting the new 8-vector.

Conservation lemma (derived and CAS checked): for nonnegative tau_j,
P_j>=0, sum_j P_j = 1-exp(-tau) <= 1. Any nonnegative, normalized age
weights preserve the photon ledger. For each packet, the absorbed energy
splits into binding and photoelectron heat:

    sum_j [Q_j + I_j N_abs,j] <= total photon energy.

No full cosmological energy conservation (including gravitational
redshift, expansion or time-variable radiation) is claimed.

The response depends nonlinearly on gas composition. At fixed E,

    dP_j/dn_l = c dt sigma_j delta_jl g(tau)
                 + tau_j g'(tau) c dt sigma_l

    g'(tau) = ((1+tau)exp(-tau)-1)/tau^2,  g'(0)=-1/2.

Wolfram Language returned tau*g(tau)-(1-exp(-tau)) = 0 and
g(tau) = 1 - tau/2 + tau^2/6 - tau^3/24 + ... .
Thus equality at one gas state does not imply equality after opacity
changes. This is established directly by the numerical holdout
counterexample.

For source-age response vector F(a;n) in R^8 and original weights
w0_a=1/36, choose compressed w_a>=0 with sum w_a=1 that solve

    sum_a w_a F(a;n_k) = sum_a w0_a F(a;n_k)

at finite training states n_k. The original positive weights ensure
feasibility; LP gives a sparse positive approximation subject to
floating solver tolerances. Replacing a continuous source-age history
by these manufactured equal weights is NOT physically validated.
Finite gas samples do not give a uniform error certificate.

## Application boundary and claim status

- q=(-.01,0,+.01) is a prescribed Bianchi source-geometry parameter,
  not measured anisotropy.
- The owner radiation R*J angular Jacobian is EXTERNAL and must not be
  applied again in this per-age reference. Source ratio/clock are
  preserved from its exact user-owned Python input.
- All results compare the same fixed quadrature and fixed gas for 1e10
  proper seconds. The scalar/fast agreement does not certify the
  quadrature against a continuous exact integral.
- HeII now has independent nonzero gas support. No electron temperature,
  collisional rates, helium feedback, evolving gas/IGM thermal history,
  cosmological radiative work or species coupling are solved.
- H+H resonant charge exchange by itself preserves global HI/HII number.
  If needed later, it belongs in ion-neutral multifluid momentum/heat
  coupling, not an extra ionization source for the abundance solver.
- This source-conditioned experiment cannot supersede SOURCE07 C8
  scientific gates or the AX08/AX11/AX12 program.

## Literature (motivation, not novelty assignment)

Vikas et al. (2013), Radiation transport modeling using extended
quadrature method of moments:
https://cfd.ku.edu/papers/2013-jcp-radiation.pdf

Baumschlager, Shen and Wadsley (2024), Spectral reconstruction for
radiation hydrodynamic simulations of galaxy evolution:
https://www.aanda.org/articles/aa/full_html/2024/11/aa48164-23/aa48164-23.html

DeStefano & Heerikhuisen (2020), doi:10.1063/1.5142868, is
relevant to the separate ion-neutral charge exchange kinetic lane.
