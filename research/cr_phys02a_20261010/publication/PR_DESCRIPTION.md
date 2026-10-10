## Why this follows PHYS01

PHYS01 binds a real proton source and a local terminal-yield receiver, but terminal electron yields do not determine deposition during the 317-year source turn-on. This work completes the first bounded physical component of CR-PHYS02-DELAY.

## What changes

Adds `research/cr_phys02a_20261010/` with the causal response of **directly born 0.1–10 eV electrons** in the fixed PHYS01 gas. The inherited 10 keV–1 PeV proton normalization and 1–4 MeV impact window remain source-pinned. The new local response uses the actual leading source ramp `Q_e(W,t)=t A(W)`, an analytic Ei Coulomb stopping clock, and a birth-time convolution. Active electron energy and the unresolved 0.1 eV cutoff residual are kept in separate ledgers.

At `t=1e10 s`, selected stopping power is `2.4153106338e-44 J m^-3 s^-1`, or `0.220764561` of that band's instantaneous terminal proxy. Of cumulative selected injection, 15.5763% has reached the prescribed bath, 83.8894% remains active kinetic energy, and 0.5343% is cutoff residual.

## Validation and decision

Nine new scoped checks pass with an actual exit-0 receipt: independent adaptive clock integration and forward ODE, source SDCS integration, 64/96 quadrature, energy closure, Bianchi source samples, unsupported-input rejection, OFF/zero behavior and source partition. Unchanged PHYS01 suites were not rerun.

A reviewer independent of candidate generation, implementation and verification design issued **PROMOTE_SCOPED** with zero blocking findings. Review/source hashes, raw logs, the derivation, complete report, state, DAG and executable follow-up instructions are included.

## Scope and next work

This is a **conditional classical superthermal Coulomb-only fixed-bath component**. It does not include higher-energy cascade feed, photon delay or near-thermal matching, and has no physical-accuracy certificate. PHYS02-DELAY remains OPEN; receiver/history and original atomic production gates remain HOLD/unchanged. The next work unit fixes absolute rates and branching for the 10–1000 eV electron input.

Base: `research/cr-physical-provider-20261010` at `e41e18873af438ef989ff44f505fe2665118fdec`. Scientific payload: `a6717cddf830b8195bc629b37d824009e1fc15c5`. Publication and dual-backup receipts will be added separately.
