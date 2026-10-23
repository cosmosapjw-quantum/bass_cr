# C23B PW19 spectral source: independent C9 review

**Decision: PASS_SCOPED_FINDINGS_CLOSED.** The executed v1 science result remains intact. Two API/documentation findings were corrected with a new, targeted guard run; the nine spectral cases were not repeated.

## EXECUTION | PUBLICATION | BACKUP | DAG

| Axis | This review's observed state |
|---|---|
| EXECUTION | C9 complete within the scope below: 13 original source pins, saved result pins, 32,592-row reaggregation, five source-conversion references, six new selected-cell reference integrals, saved correction receipt and static closure. |
| PUBLICATION | Local review artifacts ready for the parent C10 package. No remote publication by this reviewer. |
| BACKUP | Local create-only results and preserved source snapshot ready for parent backup. No new remote backup ACK or byte readback claimed by this reviewer. |
| DAG | Provider implementation → executed v1 → independent C9 findings → v2 guard correction → C9 closure COMPLETE_SCOPED. Parent publication/backup follow. Full thermochemistry, isotope mapping and secondary deposition remain OPEN. |

## 1. Evidence and reproduction boundary

The reviewed executed source identity is `277d49a9d48c94f6abf4f28fdef9e3be1d352fbb737a2edaed8ad46f1c260955`. All 13 source/data files were copied from the author's `source_providers/history/v1/` only after their byte sizes and SHA256 matched the original run's `SOURCE_IDENTITY.json`. The independent frozen copy is `source_snapshot_v1/`; `SNAPSHOT_MANIFEST.json` also binds the auxiliary unmodified anomaly evidence.

The preserved result is `source_providers/runs/c23b_pw19_spectral_source_20261023_v1/`, with three exact source redshifts, 2.316, 2.479 and 2.649, crossed with HI, HeI and HeII. This review read the saved 32,592 positive quadrature atoms and exactly reproduced every saved per-case number and kinetic-energy sum using `math.fsum`. This is reaggregation of existing bytes, not a repeat of their producer calculation.

The independent run is `review/provider_c9/runs/c23b_provider_independent_c9_20261023_v1/`. Its complete input identity, resource observation, cooperative lease, stdout/stderr, result and lease release are retained. New producer runs = 0; full-case integrations = 0; new ODE = 0; historical reruns = 0. The only new quadrature consisted of count and kinetic energy in three selected HI cells at z = 2.479.

## 2. Units and energy ownership

The release provenance is [Taira et al., v1.0.0](https://doi.org/10.5281/zenodo.15367103), Git commit `863c3b7fa73a8510fbf57ee7b75ad1e8c34086de`, release archive SHA256 `afd470b9fd934234e7f6e815d6887814a2ff8767e61f0d2a8e6187efde8d0d55`. The saved Zenodo metadata labels this software release CC0. This is a statement about the pinned release metadata, not a new license assessment of every cited scientific work.

The pinned original Cloudy-format header is `E [Ryd] log (J_nu)`. The pinned release converter multiplies the reconstructed frequency and intensity by 4π, so the CSV column is

\[
S(E)=4\pi\nu J_\nu,
\qquad [S]={\rm erg\,s^{-1}\,cm^{-2}},
\]

as spectral energy per logarithmic photon-energy interval. It is not an energy integral for each CSV bin. The five independently reconstructed rows use the release's own numerical conversion constants; the largest relative difference from the stored S is **4.0851071591×10⁻¹⁵**. The conversion's legacy constants are part of its identity. The integration uses the explicitly declared current eV-to-erg constant, 1.602176634×10⁻¹².

For a target at rest in the bath frame, a zero-recoil single-primary approximation and a source-fit binding parameter χ give

\[
K=E-\chi,\quad
q(K)=\frac{S(K+\chi)\,\sigma(K+\chi)}{(\mathrm{eV\ in\ erg})(K+\chi)^2}.
\]

Here q is per absorbing target, per proper second, per electron kinetic eV. The log-E quadrature Jacobian yields positive weight proportional to Sσ/E; the implementation has this factor. No extra c belongs in this expression for an intensity Jν. The angularly integrated scalar photon count flux is not a net vector radiation flux.

The energy ledger is χΓ plus the primary-electron kinetic-energy supply equals absorbed photon energy. The latter kinetic energy is not already thermal heat. The provider records secondary heat as null. Finite recoil, electron stopping/deposition and coupling to the thermal/radiative energy closure require their own admitted models.

Evidence: the pinned `taira_v1_0_0/make_UVB_data_table.py`, the three paired original-format `.out` files, `CONTRACT.json`, the saved `SOURCE_CONVERSION_AUDIT.json`, and independent `RESULT.json`.

## 3. Atomic fit and finite support

The official Verner table bytes have SHA256 `a53e73b0af4cc6b801aef67b84bd964e3ed8c9c4992f214e4a69dc7e4443f389`. The admitted model rows are:

| Atomic fit label | Z, bound electrons | Source-fit threshold χ (eV) | Maximum photon energy (eV) |
|---|---:|---:|---:|
| HI | 1, 1 | 13.60 | 50,000 |
| HeI | 2, 2 | 24.59 | 50,000 |
| HeII | 2, 1 | 54.42 | 50,000 |

These are rounded fit parameters of the pinned ground-state elemental atomic model. In particular, HI 13.60 must not be silently replaced by the earlier C23A convention 13.6058. Neither value by itself provides an isotope-resolved H1/D/T binding contract. HI/HeI/HeII labels do not establish the required mapping onto H1, D, T, He3 or He4; that mapping remains OPEN.

Above 50 keV the source intensity is known but the admitted atomic event rate is unknown. The contract leaves that rate unresolved and the API rejects an out-of-domain atomic query. It must not be filled with zero. Spectral interpolation is explicitly positive log S linear in log E and is part of this finite representation. Only the three exact admitted redshifts are available; redshift interpolation is not implemented.

## 4. Independent numerical scope

The independent reference parses literal table strings, uses a separately expressed Verner formula and power-law spectrum at 70 decimal digits, and integrates in linear photon energy. It compares two moments to 16 already saved quadrature atoms per chosen cell:

| HI photon interval at z = 2.479 (eV) | Number relative difference | Kinetic-energy relative difference |
|---|---:|---:|
| 13.6 to 14.203715482857126 | 4.7659×10⁻¹⁵ | 2.7993×10⁻¹⁵ |
| 96.63622680824096 to 101.46014275863574 | 9.3253×10⁻¹⁵ | 9.6993×10⁻¹⁵ |
| 49239.19240631055 to 50000 | 2.4981×10⁻¹⁴ | 2.4636×10⁻¹⁴ |

All six references pass the declared 2×10⁻¹¹ scoped comparison tolerance. This checks the near-threshold cell, an intermediate cell and the upper-domain cell. It is not an independent re-integration of all nine cases, an atomic-model uncertainty estimate, or a global error bound. `global_error_bound` remains null.

Observed resource gate: quota 8 cores, sampled spare 7.947 cores and available memory 5,925,470,208 bytes. The run acquired CPUs 7/5 through the cooperative lease, executed its worker only on CPU 5 with native numerical thread counts 1, and released its lease. CPU time was 1.811876996 s, elapsed worker time 1.874694859 s and peak RSS 35,352 KiB. CPU 55 was not available or used. These are review measurements, not a claimed scientific speedup.

## 5. Findings, correction and closure

| Finding | Actual v1 evidence | Correction and C9 disposition |
|---|---|---|
| Atomic provider identity could be bypassed | Public dataclass construction/`replace` admitted noncanonical parameters; replacing HI χ by 12 eV produced σ(12 eV) = 8.86550001466418×10⁻¹⁸ cm². The v1 consuming type guard still accepted that instance. Saved v1 cases used the pinned table constructor and are unaffected. | v2 checks all nine coefficients and the admitted channel at construction and again in `sigma_cm2`, `electron_density`, and `photoelectron_atoms`. Static AST/table comparison confirms all three canonical tuples exactly match the pinned official table. CLOSED. |
| Threshold terminology was broader than the model | The old saved key `below_threshold_physical_zero` could be read as an exact physical/isotope assertion. | New guard keys say `source_fit_threshold_zero`; original v1 logs remain unchanged. Model-fit interpretation and isotope limits remain explicit. CLOSED. |

The actual saved correction run is `source_providers/runs/c23b_atomic_provider_guard_20261023_v2/`. Its **51 targeted checks all pass**, including manual construction, dataclass replacement, unknown channel, NaN/bool coefficients and mutated-object consumer rejection. It reports zero new spectral cases, zero ODE and zero historical reruns. This reviewer read and verified the receipt and source pins; the 51-case suite was not repeated.

Corrected source code SHA256: `71b7e3a6b6f1c68ec15bcb19b98014bc025ef595f53df29703f11e25f36f4a8d`.

Corrected aggregate source identity: `bed0b482329d34397e1709c34b155533a353d1f418c979e538bc1baac4ecc0bc`.

Guard `SUMMARY.json`: 7,122 bytes, SHA256 `a6429106919ee2f50f356cafe27065c58e23fc5ecf87b21f541011442181ef58`.

The v1/v2 code difference adds API binding checks. Interpolation, the Verner equation, quadrature weights, energy ledger, source support and normalization are unchanged. The preserved original v1 pins and the new correction identity must remain distinct in publication.

## 6. Quarantine and comparison limits

The pinned z = 0 CSV remains `QUARANTINED_UNRESOLVED_CAUSE`, without repair or interpolation through it. Its SHA256 is `2f00b47d5707733231fdaeb6fe9ab8c997a7935f3a218cef258d3f85316e276f`. Its 626 positive intensities cluster near 3.77×10¹⁹, with the anomaly receipt reporting a near-HI ratio about 4.16×10²⁵ relative to z = 0.04912. This review independently reread the anomalous bytes and min/max and checked z = 0 is not admitted. It did not establish the upstream cause; paired original-format z = 0 evidence remains unavailable in the inspected release subset.

The saved comparison with C23A D1 (`arxiv1801.04931v1`) correctly keeps a separate source/model identity. The photon-rate ratios span approximately 1.003 to 1.643; the HeII ratios vary from 1.211 to 1.643 across these three redshifts. These numbers are diagnostics of different identities and conventions, not a source equivalence acceptance criterion. No release, ensemble or source-run identity is merged.

The reviewed provider is an admitted finite primary-electron source component. It does not complete atomic isotope coverage, CR transport, finite stopping, deposition, thermal evolution, UV-source evolution, radiative transfer, nuclear networks or the full cosmological feedback system. Original inaccessible conversation evidence remains UNAVAILABLE as recorded in the parent intake. No historical failure or incomplete external campaign is changed by this review.
