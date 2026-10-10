# RESEARCH_STATE

PROJECT: bass_cr / CR-PHYS02A-CAUSAL-SUBTHRESHOLD
HARNESS_VERSION: research4.0.0 / coding4.0.0
STATE_VERSION: 1.0
LAST_UPDATED: 2026-10-10 UTC
EXECUTION_STATUS: EXECUTED_PASS_SCOPED
MODEL_IDENTITY: GPT-6 Astra Pro
MODEL_IDENTITY_SOURCE: host developer metadata
HOST_CAPABILITY_PROFILE: local Python FP64, SciPy/NumPy; connectors and web; independent agent review
MODEL_PERFORMANCE_STATUS: NOT_EVALUATED
OWNER: /root
CURRENT_PHASE: bounded scientific closeout and publication
MODE: convergence

## Question and motivation

PRIMARY_RQ: In the fixed PHYS01 scenario, how much of the directly produced low-energy
electron input has actually reached the bath after finite source turn-on?
ORIGINAL_MOTIVATION: real charged-particle injection and transport to causal gas deposition.
NOVELTY_INTENT_NOT_ESTABLISHED: no new physical law or literature-priority claim.
SUBQUESTIONS: time-kernel identifiability; actual source birth history; causal stopping;
active/cutoff energy storage; higher-energy follow-up priorities.

## Scope and conventions

IN_SCOPE: directly born0.1–10eV electrons from unchanged1–4MeV H/He proton-impact
source; classical superthermal leading-log Coulomb-only drift; prescribed100K bath;
source ramp Qe=tA for0<=t<=1e10s; residual at0.1eV tracked separately.
OUT_OF_SCOPE: higher-energy cascade feed, photon delay, thermal matching, full gas
feedback, composition generalization, remaining proton losses, receiver/history.
PROTECTED_SCIENTIFIC_MEANING: source normalization on10keV–1PeV, disjoint binding and
electron kinetic energy, original atomic gates, source/state identity.
CONVENTIONS: SI; retain c, hbar, k_B; default metric(-,+,+,+); eV only an explicit energy unit.
BASELINE_AND_TOLERANCES: SCIENTIFIC_CONTRACT.json fixed before calculation; parent
e41e18873af438ef989ff44f505fe2665118fdec; FP64; tolerances not loosened.
CLAIM_CEILING: derived and numerically checked conditional stopping component.
CONVERGENCE_CRITERIA: fixed9-item numerical checks and independent scoped decision.

## Authorization and resources

EXISTING_AUTHORIZATION_AND_SOURCE: current request for the next bass_cr physics loop,
existing research publication/create-only dual-backup approval preserved in the project
context, PHYS01 handoff and contract. This work changes no production gate.
USER_BUDGET_OR_HARD_LIMIT: no new paid/HPC execution requested; lightweight local work.
AVAILABLE_SOURCES_TOOLS: exact parent bytes, primary articles, local SciPy, connectors.
EXTERNAL_ACTION_BOUNDARIES: additive research branch/draft PR and create-only backups;
no main merge, no force push, no external messages. R1 is selected before publication.

## Active evidence and state

ACTIVE_HYPOTHESES: H2 retained within closure; H1 shortcut rejected; H3 history promotion
held; H4 physical generator is next work. See HYPOTHESIS_GRAPH.md.
ACTIVE_ASSUMPTIONS: fixed bath, classical log, superthermal CSDA, leading local ramp.
CLAIM_STATUS_AND_EVIDENCE_POINTERS: EVIDENCE_LEDGER.md; CLAIM_GATE.json.
SOURCE_IDENTITIES: inputs/PARENT_SOURCE_MANIFEST.json and research/literature/source_audit.json.
SCIENTIFIC_AUTHORITY_BASIS: explicit derivation, actual new numerical run and independent
fixed-candidate decision. Template/package validity and model identity are not science evidence.
ACTUAL_EXECUTION_POINTERS: evidence/EXECUTION_RECEIPT.json, NUMERICAL_RESULT.json,
verification_stdout.log and verification_stderr.log. Final exit0;9/9 PASS_SCOPED.
INDEPENDENT_REVIEW_STATUS: PROMOTE_SCOPED; blocking findings0; review/INDEPENDENT_DECISION.json.
BLOCKERS_AND_FAILURE_CLASS: full delay is physically incomplete, not a runtime failure.
High-energy electron rates/branching, photon reservoir and thermal matching remain open.

## Completion and resumption

CURRENT_COMPLETION_BAR: CR-PHYS02A scoped work unit completed; parentPHYS02 OPEN.
COMPLETED_ITEMS: derivation, actual causal source convolution, storage ledger, numerical
verification, source/literature audit, independent decision, report and follow-up DAG.
PENDING_ITEMS: CR-PHYS02B rates/branching;02C high energy;02D photons; thermal matching;
parallel03 composition and04 proton losses; downstream05/06/07 stay waiting.
NEXT_MINIMAL_ACTION: fix source identities and absolute rates for10–1000eV electron-impact
H/He channels, then build a causal branching generator and downward boundary flux.
RESUME_FROM_EVIDENCE: START_CODEX_HANDOFF_KO.md and publication receipts; unchanged
prior suites are not rerun. Changed code/environment receives targeted checks.
NEXT_GATE: independent decision for the new rates/generator, not whole-history admission.
