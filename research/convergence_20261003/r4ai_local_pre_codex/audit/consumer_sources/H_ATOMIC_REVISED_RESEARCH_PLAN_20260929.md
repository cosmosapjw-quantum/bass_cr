# Revised Unified Hydrogen Atomic Microphysics Plan — post-H0 snapshot

## Why the previous serial plan changes

The previous H0→H1→…→H12 serial plan was too coarse. Current evidence shows that the program contains several scientifically independent frontiers with different maturity and blockers. In particular, H-H has moved to an interpolation/model-reduction validation problem (R31AA), H2+ has already advanced to C18 NA/scalar/E2 work, while atomic recombination and H+H charge exchange retain older gated states. Therefore no branch should hold the others hostage.

The revised structure uses a common authority layer followed by four parallel lanes and explicit merge gates.

## H0 — Current authority reconstruction

Status: COMPLETE_CURRENT_AUTHORITY_RECONSTRUCTION.

Outputs:
- current authority registry;
- supersession graph and role firewall;
- dual-backup integrity ledger;
- revised execution DAG.

The H0 naming prefix is `H_ATOMIC_H0_` to avoid collision with historical `WU088_UNIFIED_U0` and the R31T “H0 authority bundle”.

## H0.5 — Supersession and role firewall

Freeze these distinctions before new theory:
1. C17 is an immutable H2+ predecessor; C18 is the extended scoped authority.
2. H-H model foundation is distinct from R31AA interpolation/full-cell admission.
3. KGT/Feshbach certification cannot automatically amend the canonical recombination source.
4. HOST4/C102 COUNT_MODEL is not a physical CX-rate certificate.
5. Reionization receiver equations and atomic rate authority are separate objects.
6. Legacy CR3C9/P0-R2/WP1 are consumer/semantic evidence, not replacement microphysics authority.

Exit: `H_ATOMIC_ROLE_FIREWALL_CLOSED`.

## Lane A — Common radiative H microphysics, can start now

A1. Unified H state/process/source registry:
- bound states, bound-bound, bound-free, 2γ;
- e-H excitation/ionization;
- reverse-process identities;
- source DOI/version/hash/domain/normalization/interpolation/UQ.

A2. Microreversibility:
- Einstein identities;
- Milne photoionization↔radiative-recombination relation;
- collisional detailed balance;
- LTE/Saha recovery;
- explicit threshold/degeneracy/frame conventions.

A3. Unified radiative operator:
`C_H^γ = C_bf + C_bb + C_2γ`.

A4. H-only reionization receiver:
instantiate R1 as `R2-N-H` with `{x_HII,u_th,fγ}` before helium or tilt.
Use P0-R2/WP1 as conservation/charge-semantic fixtures, not physical history.

A5. Recombination adapter:
connect the same atomic authority to the recombination source/transport contract.

Merge gate A:
`CROSS_ENVIRONMENT_LOCAL_ATOMIC_PARITY_PASS`.

This lane does not wait for H-H R31AA or H+H physical-rate closure.

## Lane B — Atomic continuum / KGT-Feshbach certification

B1. Canonically admit or reject the pending S4 full suite. Do not use archive filenames as admission.
B2. If and only if S4 passes, execute/admit S5 bridge decomposition.
B3. G10 raw continuum blocks and frozen whitening.
B4. G11 Schur/rank/property certification.
B5. G12 only if G11 permits it.
B6. G13 pole-free Feshbach/root certification only if authorized.

Any proposed source change goes through `SOURCE_AMENDMENT_REVIEW`.
D86_TABLE_V_LENGTH_LINEAR_B remains canonical until that review passes.

## Lane C — Collision and molecular physics

### C-HH: H-H
C-HH1. Execute the already authorized cheap/read-only R31AA follow-up:
- existing z=3 local-vs-global post-hoc comparison;
- fixed-Q model-definition review;
- fixed-Q physical-invariance review.

C-HH2. Decision gate on the preregistered z=1 mixed-only node.
Do not execute z=1 merely because it is preregistered.

C-HH3. If z=1 is authorized and useful, compare global vs local models using preregistered E_K/E_Dmax rule.

C-HH4. Only after interpolation choice:
- z4 neutral47 generation if separately authorized;
- full-cell O/D/dotO/H authority;
- source/roundoff interval enclosure;
- BR01/BR02;
- independent review;
- trajectory and transition observables.

### C-CX: H+ + H
C-CX1. Recover exact H19 promotion-trigger identities.
C-CX2. Complete remaining trigger.
C-CX3. Close source-native blind/replay/actual-consumer ledgers.
C-CX4. Tail + continuous-source UQ.
C-CX5. Only then promote thermal `k_CX(T)` or physical consumer rates.

### C-H2+: H2+
C18 is the baseline and is not repeated.
Future work is limited to:
- continuum energy/flux normalization;
- long-range and near-threshold matching;
- RA/PD detailed balance;
- full coupled-channel NA;
- NA transition operator;
- rigorous global UQ and higher-order physics when scientifically needed.

## Lane D — Consumer semantics and cosmological bookkeeping

D1. Normalize charge/nuclei/electron-count semantics across recombination, reionization and CR consumers.
D2. Preserve the key CX fact: charge exchange redistributes charge; it does not create a free electron.
D3. Build photon-number, nuclei, charge and thermal-energy ledger interfaces.
D4. Map atomic source IDs/hashes into every downstream consumer.

Legacy CR3C9/P0-R2/WP1 results are regression fixtures here.

## Merge M1 — Common H microphysics freeze

Required:
- H0.5 role firewall closed;
- Lane A microreversibility and local atomic parity closed;
- Lane B has an explicit certified ceiling, even if negative/blocked;
- Lane C statuses are explicit and no consumer silently assumes a higher claim;
- Lane D bookkeeping interfaces fixed.

Output:
`H_ATOMIC_MODEL_SPEC`,
`H_ATOMIC_PROCESS_REGISTRY`,
`H_ATOMIC_SOURCE_LEDGER`,
`H_ATOMIC_CLAIM_MATRIX`.

## M2 — Process relevance atlas

Only after M1:
compare process timescales across `(z,T,x_e,Eγ,Ep)` and classify each as
`CORE`, `CONDITIONAL`, `NEGLIGIBLE_IN_REGISTERED_DOMAIN`, or `UNKNOWN`.

Negligibility requires a bound, not intuition.

## M3 — Theory freeze and implementation contract

Freeze:
- units and conventions;
- state IDs;
- reverse-process identities;
- source amendment rules;
- environment adapters;
- error/claim gates.

Then hand off bounded heavy numerical work to local Codex.

## Immediate next research node

Recommended next node:
`H_ATOMIC_H05_SUPERSESSION_ROLE_FIREWALL_AND_COMMON_SOURCE_CROSSWALK`

In parallel, H-H may proceed only with the R31AA read-only/post-hoc + fixed-Q review already authorized by its handoff. The new z=1 scientific node remains a separate explicit decision.
