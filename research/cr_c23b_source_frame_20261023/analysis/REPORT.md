# C23B saved-output analysis and figure delivery

## Outcome

Two scientific figures are ready for publication in independent 180 mm and 90 mm layouts, each as a vector PDF and 300 dpi PNG. **Use only `runs/c23b_saved_analysis_20261023_v3` for the current figures.** The earlier render revisions and their analyzer snapshots remain as audit history.

The analyzer reads six pinned input files from the completed source-provider and boost runs. It consumes the saved 10,864 z = 2.479 quadrature atoms and 32 tritium/neutron witness partitions. Its operations are file verification, arithmetic aggregation, table extraction and rendering. It does not import or call the science/source implementation. New source evaluations, new Lorentz transforms, ODE solves and historical physics reruns are all zero.

## Primary electron source: substantive result

For the three admitted channels at z = 2.479, the saved finite atomic source is dominated by different parts of the primary-electron energy range. All fractions below refer to **kinetic energy**, not electron counts, absorbed photon energy or a deposited-heat fraction.

| Absorbing target | Mean K [eV] | Below 10 eV | Within 10–9937.21 eV | Above 9937.21 eV within photon-fit support |
|---|---:|---:|---:|---:|
| H I | 3.73701137 | 0.6691841736 | 0.3308158254 | 9.55018577×10⁻¹⁰ |
| He I | 7.07386341 | 0.4066543092 | 0.5933456590 | 3.17713061×10⁻⁸ |
| He II | 19.96943547 | 0.0942896099 | 0.9057095315 | 8.58586520×10⁻⁷ |

Evidence: the pinned source run's `CASES.json`, reproduced without provider calls in the final run's `SOURCE_FRACTIONS.json`. The 64-bin energy histogram preserves the total saved kinetic supply to a maximum relative arithmetic difference of 6.5607210040808844×10⁻¹⁵. This is a rebinning consistency result, not a spectrum-accuracy bound.

The finite spectrum keeps its actual PW19 release identity. C23A's D1 two-moment diagnostic is not substituted or combined. The three adopted photoionization thresholds are rounded Verner fit thresholds, not exact isotope thresholds. Photon energies above 50 keV remain outside the admitted atomic fit, and their electron injection is unresolved. The finite FS energy range does not close its composition/stopping assumptions; actual FS gas admission and thermochemical/radiative closure remain open.

## Boosted rest-moment witnesses: substantive result

The saved diagnostics already show that equal normalized rest electron count, mean energy and allowed support interval do not fix finite energy-window coverage. These two mathematical measures remain explicitly distinct from evaluated beta spectra.

| Witness family | u | Mean-line kinetic coverage | Endpoint-mixture kinetic coverage |
|---|---:|---:|---:|
| Tritium | 0 | 1 | 0 |
| Tritium | 0.05 | 0.9540164313 | 0.06991834564 |
| Tritium | 0.2 | 0.1009719464 | 0.01678542345 |
| Neutron | 0.05 | 0 | 0.001297847704 |
| Neutron | 1 | 0.00003634177283 | 0 |

Evidence: the pinned boost run's `PARTITIONS.json`; all 32 plotted records are extracted in the final run's `boost_coverage.csv`. The neutron vertical axis has a linear region near zero and a logarithmic positive region; this display choice does not change stored values. The eight u samples are categorical display positions, and the markers have small visual offsets. No line interpolation or interpolation-accuracy claim is made.

## Figure revisions and audit

The user-supplied `07-Figure-Residual-Error-Pass.txt` and `08-Figure-Hostile-Audit.txt` protocols guided the review. The initial ledger was saved before the first correction. Actual v1 PNG inspection exposed a clipped source y label, overlapping titles/legends/footers and an unreadably narrow percentage segment in the 90 mm stacked bar. Revision 2 changed only layout: physical-mm positioning, separate header/legend/footer bands, and a numeric table for the narrow source figure. Revision 3 changes only the source legend's opaque white background so the finite-range guide cannot cross its labels.

The three numeric analysis products are byte-identical across all three revisions. Both boost PNGs are byte-identical between v2 and v3. Analyzer snapshots and pins for v1 and v2 are retained under `history`. All run directories are create-only, and no earlier result was overwritten.

The final four PNG layouts were actually opened and visually reviewed. Root independently opened all four v3 PNGs and reported no clipping or overlap. All visible text bounding boxes lie within the canvas; the minimum recorded font is 8.4 pt at 180 mm and 8.0 pt at 90 mm. The four PDFs each have one page at their declared physical width and contain embedded TrueType fonts. PDF metadata and text were read; separate PDF rasterization was not performed. The corresponding Matplotlib PNGs were the actual visual inspection surface. The final audit is scoped to these figures, labels and saved numbers, not to unperformed physical closure or interpolation tests.

## Resources and four-axis status

Each render run independently observed resource availability, acquired a cooperative lease, pinned its coordinator to CPU 6 and rendering worker to CPU 3, forced native thread counts to one, protected CPU 55 and wrote to a new run ID. All three leases have release receipts. Final v3 render time was 9.551244364 seconds wall and 9.463024036 seconds process CPU. These are rendering measurements only.

| Axis | Status at child handoff | Scope |
|---|---|---|
| EXECUTION | COMPLETE_SCOPED | Two figures, four layout variants; source/physics/ODE rerun count 0 |
| PUBLICATION | READY_FOR_PARENT | Eight final figure files, analyzer, exact pins, tables, captions and audit; remote publication acknowledgement belongs to parent |
| BACKUP | LOCAL_PINNED; REMOTE_PENDING_PARENT | Historical figures and sources preserved; child performed no remote upload and makes no multi-destination backup-completion claim |
| DAG | ANALYSIS_COMPLETE_SCOPED → PARENT_PUBLICATION/BACKUP | Physical source/composition/stopping admission and full thermochemical/radiative closure retain their parent status |

The narrow task is complete: 2/2 requested scientific figures and 4/4 requested layout variants. No percentage is assigned to the full physics program. `global_error_bound = null` is retained.

## Deliverable map

| Item | Relative path |
|---|---|
| Current figures and numerical extraction | `runs/c23b_saved_analysis_20261023_v3/` |
| Caption text and exact interpretation | `CAPTIONS.md` |
| Figure analyzer | `render_saved.py` |
| Exact immutable science-input pins | `INPUT_PINS.json` |
| Initial and v1 audit history | `AUDIT_LEDGER_INITIAL.json`, `AUDIT_V1_FINDINGS.json` |
| Final bounded hostile/residual audit | `FIGURE_AUDIT.json` |
| PDF page/font and PNG metadata inspection | `PDF_PNG_INSPECTION.json` |
| Final analysis receipt and publication manifest | `FINAL_RECEIPT.json`, `PUBLIC_MANIFEST.json` |

The render command accepts a fresh safe run ID and refuses an existing output directory. A future visual reflow should consume these same pinned saved inputs; it does not require re-executing a completed source or physics campaign.
