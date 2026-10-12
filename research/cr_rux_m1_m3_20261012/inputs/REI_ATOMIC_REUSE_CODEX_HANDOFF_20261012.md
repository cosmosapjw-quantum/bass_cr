# Codex start handoff: atomic-reuse EoR track (2026-10-12)

Work in `cosmosapjw-quantum/rei_bianchi`. Do not reset branches, force push, merge, or repeat completed scientific calculations. Read AGENTS.md and the historical `docs/atomic_reionization_handoff_20261004_v1/00_READ_FIRST_KO.md`, `GLOBAL_DAG.json`, `TASK_CARDS.jsonl`, `PR_PLAN.json`; treat historical execution states as historical.

Use `REI_ATOMIC_REUSE_DAG_20261012.json` and `REI_ATOMIC_REUSE_PLAN_20261012.md` as a NEW PROPOSED successor overlay, not as a claim that scientific nodes are complete. These files are local handoff artifacts, not yet Git-published.

First implement bounded RUX00 and RUX02, then RUX03. Exact source pins, provider claim boundaries and documented failures must be preserved. The critical archive inputs to inspect are:
- `/BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/REI_BIANCHI_PHYSICAL_INPUT_HANDOFF_20261010_v2.tar`
- `/BASS_DERIVATION_DOSSIERS_20260912/REI_PHYSINPUT_P01_PRODUCTION_20261010_c168e578.tar.gz`
- `/BASS_DERIVATION_DOSSIERS_20260912/REI_PHYSINPUT_P02A_20261010_8a80fa9.tar.gz`
- `/BASS_DERIVATION_DOSSIERS_20260912/REI_PHYSINPUT_P03A_20261010_d6ad8b7.tar.gz`
- `/BASS_DERIVATION_DOSSIERS_20260912/REI_P03A_SOURCE_DELTA_20261010_05c45c3.tar.gz`
- `/BASS_DERIVATION_DOSSIERS_20260912/REI_N2_LOCAL_INPUT_RESEARCH_20261010_v1/RECEIPT.md`
- `/bianchi/rei_bianchi/rust/rei_microphysics/src/`
- `/bianchi/rei_bianchi/runs/rei_fastest_v1/paired/`

Bind the exact physical input and case A/B photon owner. Do not combine legacy effective HI opacity with local HI absorption for the same events. Preserve Verner photon cutoffs separately from ionization binding-energy values. All species/photons/heating in gas proper frame with clear comoving conversion. Do not interpret source-null as zero or infer physical source from the F08 synthetic 13.7 eV fixture.

Only after RUX02/RUX03/RUX04 gates PASS, reuse existing `coupled_primary.rs`, `angular_photons.rs`, `axisym_radiation.rs`, `paired_runtime.rs`, `homogeneous_rates.rs`, BASS tau/visibility receiver. Run a matched short physical FLRW/BI interval, then a source-backed EoR history. Store `input_identity`, `branch`, `commit`, exact commands/exit codes, output checksums, nuclei/charge/photon/energy ledgers, modeled-vs-numerical errors, failures, claim ceiling in durable step receipts. No heavy NCP work should launch without measured/specified genuinely heavy job and validated physical inputs. H/He precision, CR, and HH are opt-in sensitivities, not blocking dependencies.

Return an inventory of actual admitted inputs, exact missing fields, approved tasks and a minimal first executable target. If physics inputs remain incomplete, return PHYSICAL_HOLD, do not invent them. If writing/pushing is not authorized by the current operator, stop at a clean local change and report its status.
