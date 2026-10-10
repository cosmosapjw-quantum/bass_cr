# CR-PHYS02D: heat-delay information from saved ramp endpoints

This unit derives and evaluates finite-window heat-delay moments from the already completed 2,400/4,800/9,600-node ramp results. It prepares a new two-model pulse response at the same 9,600-node energy grid.

- Research results and interpretation: `REPORT_KO.md`.
- Complete derivation and independent small oracles: `research/theory_contribution/`.
- Actual saved-data analysis: `evidence/endpoint/RESULT.json`.
- Current state: `state/RESEARCH_STATE.md` and `state/NEXT_DAG.json`.
- Independent decision and exact reviewed identities: `review/INDEPENDENT_DECISION.json`.
- NCP handoff: `START_NCP_CODEX_KO.md` and `ncp/README_KO.md`.

The inherited source, bath, atomic channels, Coulomb prescription, precision and energy grid are unchanged. Actual new physical G builds and pulse transports in this unit's preparation are zero. The NCP pulse task needs its own actual return and subsequent independent scientific review.

The archive includes all required pinned transitive inputs, the already completed 9,600-node return, first failures, the returned resource adapter, and both Astra v4.0.0 harnesses. A later receipt-only commit can add publication evidence while preserving the science files and immutable archive.
