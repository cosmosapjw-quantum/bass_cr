# EVIDENCE_LEDGER

Project: bass_cr / CR-PHYS02A. Date: 2026-10-10. All claims have the fixed-state,
direct-ejection, 0.1–10 eV Coulomb-only ceiling in SCIENTIFIC_CONTRACT.json.

| Evidence ID | Claim | Kind | Locator | Exact support | Relation / audit | Limit |
|---|---|---|---|---|---|---|
| E01 | Terminal yields do not identify delay | literature-supported; derived | FS10 §§2,6.1; DERIVATION_KO.md §2 | Time rescaling preserves terminal yield and changes delay | supports / SUPPORTED | No full time kernel supplied |
| E02 | Absolute classical stopping closure | literature-supported, conditional | Khrapak2020 Eq6; FS10 Eq5; literature/SOURCE_AUDIT.md | 4π energy-loss coefficient, reduced-mass classical cutoff | supports / PARTIALLY_SUPPORTED | Near crossover and thermal cutoff; neutral collision condition unmeasured |
| E03 | Exact clock and ramp response within closure | derived | DERIVATION_KO.md §§3–6 | Ei primitive, causal power/cumulative heat, cutoff flux, energy conservation | supports / SUPPORTED | Leading local expansion; prescribed bath |
| E04 | Numerical realization of E03 | numerically checked | NUMERICAL_RESULT.json checks 1,2,4,5 | Independent adaptive integral and ODE, 64/96 rule, energy ledger | supports / SUPPORTED | Independent numerical routes share physical closure |
| E05 | Source identity and normalization | implementation-verified; numerically checked | PARENT_SOURCE_MANIFEST.json; NUMERICAL_RESULT.json | Exact inherited injection/Rudd bytes; separated SDCS coefficient check | supports / SUPPORTED | Active proton collisions only 1–4 MeV |
| E06 | Local ramp approximation size | numerically checked | source_approximation_samples in NUMERICAL_RESULT.json | Three exact Bianchi coefficient comparisons, max6.93e-7 | limits / SUPPORTED | Finite samples; no continuous bound |
| E07 | Guard and OFF behavior | implementation-verified | EXECUTION_RECEIPT.json; verification_stdout.log | Actual exit0, fixed-density rejection, unsupported domains, exact zero/OFF | supports / SUPPORTED | New study only; old suites rerun0 |
| E08 | Endpoint ratio and storage fractions | numerically checked | NUMERICAL_RESULT.json time_series[-1] | Power ratio.220764561; deposited/active/cutoff ledger | supports / SUPPORTED | Not full CR history or physical-error certificate |
| E09 | Next energy range priority | numerically checked | details.direct_electron_source_bands | 10–1000 eV accounts for71.06949% of direct secondary kinetic input | contextual / SUPPORTED | Source weight alone is not a cascade delay result |
| E10 | Parent heat scale comparison | implementation-verified; derived | inputs/PARENT_CR_PACKET.json; PARENT_REFERENCE_PROVENANCE.json | Same parent terminal heat1.2093044641845817e-42; ~7.05% magnitude comparison | contextual / SUPPORTED | Neither full suppression nor rigorous bound |
| E11 | Independent decision | independent external decision review | review/INDEPENDENT_DECISION.json, INDEPENDENT_REVIEW_KO.md | Separate reviewer of fixed candidate, equations, scope and actual execution | supports / see decision | Not cross-model evidence or physical precision validation |
| E12 | Whole delay/IGM history | unresolved | DAG.json; CLAIM_GATE.json | Higher-energy cascade, photon/cutoff matching, composition and losses absent | missing / UNSUPPORTED | Admission false; production HOLD |

## Exact source and execution identities

Parent source commit: e41e18873af438ef989ff44f505fe2665118fdec. Exact module hashes
are checked at import and retained in inputs/PARENT_SOURCE_MANIFEST.json. The original
parent CR_PACKET was copied without modifying its scientific fields; provenance is
separate. Published article versions and actually read scopes are recorded in
research/literature/source_audit.json; unacquired numerical atomic data are marked.

The actual final command, cwd, process exit, raw stdout/stderr hashes, current source
hashes, NumPy/SciPy/Python versions and FP64 declaration are in evidence/EXECUTION_RECEIPT.json
and evidence/NUMERICAL_RESULT.json. Earlier successful outputs remain with PRE_CUTOFF_FLUX
and PRE_FIXED_DENSITY labels. They do not substitute for the final execution identity.

Research source acquisition was performed by /root/secondary_delay_sources. That role
did not design the implementation or decide promotion. /root/phys02_decision_review
performed the separate final decision; /root owned derivation, implementation and tests.
Shared model family is not independent empirical validation of plasma physics.
