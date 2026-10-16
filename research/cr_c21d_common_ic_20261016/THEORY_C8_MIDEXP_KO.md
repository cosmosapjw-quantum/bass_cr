# C21D C8 theory: positivity-preserving midpoint absorber exposure

## New controlled construction

In a step with no source impulse or abrupt threshold inside, let `k_rj(t) >= 0` denote photo hazard per *per-total-H absorber* for packet r and species j, in s^-1. Let `A_j^0,A_j^1>=0` be physical populations/H. Define `bar A_j=(A_j^0+A_j^1)/2`, `bar k_rj=k_rj(t_mid)`, and `Theta_r=dt Σ_j bar k_rj bar A_j`. Then

- `N_r^1=N_r^0 exp(-Theta_r)`, nonnegative;
- `L_rj=N_r^0*(-expm1(-Theta_r))*(bar k_rj bar A_j)/(Σ_l bar k_rl bar A_l)` when denominator >0, zero otherwise;
- `A_j^1` is solved with **exact H/He event stoichiometry**, including HeI→HeII source and HeII→HeIII loss;
- binding increments `Σ_j chi_j L_j`, thermal photoheat increments `Σ_rj (E_r(t_mid)-chi_j)L_rj`;
- geometry redshift and gas adiabatic work occur outside the chemistry transaction in two half-maps.

A bounded nonlinear solve parameterizes all converted fractions in `[0,1]`, then accepts only physical residuals below the predeclared bound. Structurally impossible absorption channels are exactly zero; no epsilon neutral fraction floor, no false endpoint Γ injection. Positive EXP does not force second order; midpoint exposure changes the leading truncation term.

## Smooth-interval local consistency

For scalar smooth `A(t)=a0+a1 t + a2 t²/2` and `k(t)=k0+k1 t+k2 t²/2`, analytic integration shows

`dt*k(dt/2)*(A(0)+A(dt))/2 - ∫_0^dt k(s)A(s)ds`
`= dt³*(k0*a2/12-k1*a1/12-k2*a0/24)+O(dt^4)`.

Wolfram Language independently returned `[0,0,0,0,cc*kk/12-bb*ll/12-aa*mm/24]` for the coefficients through order three after subtracting the claimed formula. This gives O(dt^3) local hazard error for smooth coefficients and a resolved/non-stiff accepted midpoint root. With GL2 source impulses split exactly at births, threshold crossing split exactly at q20/Efit, and physical-time clock midpoint, the positive photon/exposure subsystem is **formally second order on smooth subintervals**. This is not a blanket stability/uniqueness proof for full non-equilibrium H/He/Grackle, nor a full cosmological accuracy theorem.

## Why no source-on native second-order claim follows

Latest user NCP PR78 and rei_bianchi PR171/172 show that native source-age spectral convergence and owner source-on chemical accuracy are still HOLD. C21D MIDEXP is a standalone photo-only toy with original 3 Verner fits and the original MD14 **total rate**, but prescribed three spectral energies and opacity scale. It has no Case-A recombination photons, CI/RR/DR, Compton/CMB or Grackle thermal RHS, and its frozen-end EXP baseline is not bit-equivalent to the native PR150 PreparedAbsorption. A native port must perform the full event-owner transfer and accepted-step rollback, then compare matched source/IC/time/spectral/angle against an independent native Radau reference.
