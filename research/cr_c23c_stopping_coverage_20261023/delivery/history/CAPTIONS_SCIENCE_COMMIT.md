# C23C figure captions and numeric scope

The final figure authority is `analysis/FINAL_FIGURE_RECEIPT.json`: three pairs come from `runs/c23c_saved_analysis_20261023_v2/`, and the cutoff_source_90mm pair comes from `runs/c23c_pdf_transport_repair_20261023_v3/`. The latter PDF was rendered and actually inspected in `runs/c23c_pdf_readback_render_20261023_v4/`. Both 180 mm and 90 mm PDFs are single-page vector outputs; the corresponding PNGs are previews. All values come from immutable `runs/c23c_source_cutoff_binding_20261023_v1/CASES.json`, SHA256 `c6db8c354c1e85e366f218eb8f0dfe42e99099ea18e370a1cf2062f816d5724d`. No new source quadrature, cutoff solve, atomic-rate evaluation or ODE was performed for these figures.

## Figure 1 — cutoff_source

At the actual saved PW19 redshift `z=2.479`, panel (a) compares the caloric cutoff `K_c=chi k_B T_cal` for chi=1.5 and 3 with the distinct 10 eV lower boundary of the adopted FS table. Lines connect the three declared synthetic bath fixtures for readability; they are not a redshift/temperature interpolation contract. Panel (b), for chi=3, partitions injected primary-electron kinetic energy into below-caloric-cutoff, active below FS, active inside FS, and active above FS categories. The six underlying thermal/active × FS cells are retained in the raw results; below-cutoff cells are aggregated only in the display. At small T0 the blue fraction is too small to resolve on this linear axis; its exact value is preserved. A zero-height above-FS category is valid for this source fixture and does not state that a physical photon tail is absent.

The cutoff classification is a finite inventory/EOS diagnostic. It does not establish deposition, thermalization time, Coulomb stopping or global rate coverage. In particular FS <10 eV support is not a universal atomic inelastic threshold.

## Figure 2 — caloric_response

The same saved z=2.479 fixtures illustrate why positive injected kinetic energy need not increase the temperature of the newly classified particle inventory. Panel (a) shows the positive magnitude `T0-T_cal` of the negative finite caloric change, for both chi choices. Panel (b), for chi=3, shows the two terms

`Delta T_cal = [L_E - (3/2) k_B T0 L_N] / [(3/2) k_B (N_B + L_N)]`.

Orange is the kinetic term, blue the particle-count term, and black diamonds their signed sum. Panel (b) uses a symmetric-log axis (linear threshold 0.001 K). The y range includes all bar endpoints. No physical cooling trajectory or heating rate is inferred: `physical_heating=null` until an admitted collision/energy-exchange closure exists. The real source is combined with an explicitly synthetic frozen bath and a fixed exposure; these are not measured IGM conditions.

## Visual read

Root inspected all four final PDF renders at their stored resolution. Axis units, signs, legends, color association, margins and 90/180 mm layouts are legible without clipping. v1's lower signed bar touched the frame; v2 only extends that axis and clarifies one legend label. Original executed v1 plot code was reconstructed by the two inverse text edits and verified against its already-recorded SHA before preservation; its original output and receipt are unchanged.

### Final transport correction

During publication cataloging, the v2 cutoff_source_90mm PDF was found to contain 4,060 bytes rather than its recorded 22,729 and failed PDF parsing. The cause is undetermined. Its original receipt and damaged bytes are retained as historical evidence. A targeted buffered, fsync/create-only serialization from the same saved CASES produced the v3 PDF. Its PNG is byte-identical to v2; the v4 stdout-rendered PDF image is byte-identical to the originally inspected v2 render. One empty v3 renderer file is retained as rejected evidence. All four selected final PDFs now parse and match their recorded SHA256. No scientific calculation was rerun.
