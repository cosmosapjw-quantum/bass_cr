# Third-party notices and source scope

The new research Python sources carry SPDX GPL-3.0-only notices. The unchanged parent `LICENSE` is included as `LICENSE`. Parent research sources and raw tables remain under their original notices; this unit does not assign new licenses to third-party material.

The handoff preserves selected native CCC excitation data and original README notices from the recovered PHYS02B bundle. Their provenance and unchanged effective-cost convention are documented in the parent `inputs/CCC_USED_CHANNELS.json`, this unit's frozen contract, and source audits. A first-zero marker is not newly certified as a spectroscopic or exact target-Hamiltonian energy.

Primary atomic references include Kim and Rudd (1994), Kim, Johnson and Rudd (2000), Rohrmann and Vera Rueda (2022), and the NIST Electron-Impact Ionization database. Source URLs, used equations, printed coefficients, attribution, and limitations appear in `DERIVATION_KO.md` and `research/ionization_sources/ATOMIC_PRIMARY_SOURCE_AUDIT_KO.md`. Full copyrighted papers are not included in the handoff.

NumPy, SciPy, mpmath, threadpoolctl, and optional diagnostic plotting dependencies are external packages with their own licenses. Their installed package trees are not redistributed here. Runtime versions and actual threadpool information are recorded in execution evidence.

The verified research/coding harness ZIPs in `handoff_harness/` are delivered unchanged with their existing notices. Their inclusion provides operational context; it does not establish a measured implementation runtime-model identity or performance comparison.
