# Proper-time source injection and qualified returns

Unit `CR_PROPER_INJECTION_RETURN_V1`, physmath workflow1.0.0, 2026-10-27.

## Fixed objective

Qualify and consume at least one actual finite proper-time external source. The selected source is the stored PHYS02 secondary-electron history Qe(W,t)=t A(W),0≤t≤10^10 proper seconds, at100K in its own frozen physical bath. Source-native kinetic support0.1–900eV, two birth tags, original source vectors and original source code are reused. The source is model-derived and actually stored; it is not an observed time series. Its exact files and hashes are bound at R2. Its elemental H/He origin retains conditional H1/He4 assignment. Actual source isotope/level information is not extended.

Derive native measure→proper injection→finite N/E→qualified RR/native25 and retained-photon ports. Implement photon/electron/baryon normalization contracts and changed controls. One actual electron source is consumed; other particle inputs are explicitly synthetic contract controls until independently qualified. No previous source quadrature, projection, old generators, old RHS or ODE are rerun.

## Physical boundaries

Use metric(-,+,+,+); retain c,hbar,kB. The actual source has fixed proper volume but no absolute volume value; density outputs are allowed, worldtube totals remain null. The recorded history supports only[0,10^10]s; post-end continuation or shutoff is unspecified. Target density, angle integration and z8 proper-volume factor729 already occur in source A. No second target/clock/volume factor is applied.

PHYS02 hasT100K andHeIII0, while PR107 hasT10000K andnHeIII.01cm^-3. Their physical-state IDs differ. Actual RR consumption of this source remains gated unless a matching response is supplied. The independent PR108 finite-age response is retained as a parallel observation, not recomputed or adopted by changing this source. Frozen moments do not define a new spectrum or time history. An explicit input law does permit exact integration of that law.

Actual same-state donor/recipient nb is absent: nb and native25 remain null. General baryon-changing projection uses the exact quotient, not fixed-nb division. Retained photons have a separate number/energy port; missing retained output is null, with no transfer into w_ext or physical heating. Finite injection interval and finite return horizon are distinct.

## New execution envelope

New local science CPU cap20s includes preparation, actual adapter, controls, independent reference and all science coordinators/failures. One native thread; memory512MiB/worker and≥1GiB host reserve; each attempt wall≤60s, named create-only attempts. C4 records actual admission before scientific workers. The supplied Wolfram exact check used two remote calls with20s/5s timeConstraint and provider CPU unavailable; that unknown is separate from local measured CPU, not0. No previous budget is transferred, including HeIII6.988054525/30 and parallel PR10860s. Historical UNKNOWN_NO_ACK and old failed/owned-lease recovery remain unchanged.

Acceptance: exact hashes; actual source moment reproduction relative≤2e-12; finite-time integration/additivity relative≤2e-14; energy unit/event conservation scaled≤2e-14; independent reference≤2e-13; all specified invalid-state/clock/volume/isotope/support/duplicate-event guards refuse. No relaxed criteria after execution. Numeric checks qualify the stored source and adapter, not global physical uncertainty.

## Authority and completion

BaseS4e72c89b714431eb4c6ae07def777bbf72a5ae4c,D ec463db0c7e5c7fb5070796071c926caa4db6445,M5abe0d19df95db730e3e33bae0373c81ba37ce89. Work branch research/cr-proper-injection-20261027, no main merge. R1–R10/C1–C10 each have an actual preflight, stage result, expected-SHA non-force publication and dual checkpoint. Source and final authority have R3; ordinary stage checkpoints R2. Receipts bind actual prior publications without circular future hashes.

Original central27/88,88nodes/17edges, scoped count effect0. N4/N5 PARTIAL_OPEN,N6/N7 PREDECESSOR_GATED,L4false. Global physical completion/error/budget remaining/currency null. Unmerged PR23632/88 and itsT/nb remain separate. Full private conversation search unavailable and prior Drive inventory partial. A complete contract implementation is distinguished from the still-open actual source-to-RR physical join.
