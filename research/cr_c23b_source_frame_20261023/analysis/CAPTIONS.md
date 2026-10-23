# C23B publication captions — saved-output analysis

The authoritative figure revision is `runs/c23b_saved_analysis_20261023_v3`. Each figure has separate 180 mm and 90 mm layouts in PDF and 300 dpi PNG. The 90 mm source figure uses a numeric fraction table, and the 90 mm boost figure stacks the two panels. These are reflows with at least 8 pt text, not scaled-down copies.

## Figure 1. Primary electron supply and its finite energy-domain partition

**Primary photoelectron energy supply from the admitted PW19 release view at redshift 2.479.** Panel (a) rebins the 10,864 saved positive quadrature atoms for H I, He I and He II into 64 equal logarithmic kinetic-energy bins. The ordinate in a bin is

\[
\frac{\sum_{j\in\mathrm{bin}}K_j w_j}
 {\ln(K_{\mathrm{hi}}/K_{\mathrm{lo}})},
\]

where `w_j` is the saved electron-number weight per absorbing target per proper second, and `K_j` is the electron kinetic energy in eV. Thus the ordinate has units eV target⁻¹ s⁻¹ per unit natural logarithm of kinetic energy; it is an energy-weighted histogram of finite quadrature, not a newly evaluated continuous spectrum. Empty low-energy histogram bins contain no saved quadrature nodes and do not assert a zero continuous injection density. The sum over all histogram bins preserves the saved total kinetic supply to a maximum relative difference of 6.57×10⁻¹⁵ across these channels.

The source belongs to the bath frame with ground-state absorbing targets at rest and the provider's zero-recoil approximation. Its photon-to-primary-electron mapping uses the **adopted rounded Verner fit thresholds**, χ = 13.60, 24.59 and 54.42 eV for H I, He I and He II, respectively, and `K = Eγ − χ`. These numbers are the admitted fit parameters, not isotope-resolved exact thresholds. The admitted atomic fit ends at photon energy 50 keV; consequently the three electron source supports end at 50 keV minus their respective χ. Radiation above that photon limit has no assigned atomic event or electron-injection rate in this model and is not assumed absent.

The shaded region and dashed limits mark the finite FS response-table energy range, 10–9937.21 eV. Panel (b) gives fractions of the **total kinetic energy in this finite atomic source**, partitioned below, within and above that range. At 180 mm, the extremely small high-energy fractions are written explicitly beside the stacked bars; at 90 mm all fractions are reflowed into a table. Values in the 90 mm table are fractions, not percentages. The mean electron kinetic energies are 3.737011, 7.073863 and 19.969435 eV, respectively. The sub-10 eV fractions are 0.66918417, 0.40665431 and 0.09428961. The fractions above the FS upper energy, but still inside the admitted photon-fit support, are 9.5502×10⁻¹⁰, 3.1771×10⁻⁸ and 8.5859×10⁻⁷.

These are energy-domain bookkeeping fractions. The figure does not establish physical FS deposition for the actual gas, infer a spectrum from C23A's two radiation moments, close the composition or stopping contract, or supply a thermal/radiative energy closure. The underlying source provenance and fit support are recorded in `source_providers`; the analyzer consumes only the completed run's CSV and JSON, whose exact bytes are pinned in `INPUT_PINS.json`.

**Files:** `primary_electron_source_180mm.{png,pdf}` and `primary_electron_source_90mm.{png,pdf}` in the authoritative run directory.

## Figure 2. Equal rest-moment witnesses have different finite energy coverage after a boost

**Saved isotropic electron-measure diagnostics for tritium and neutron rest moments, transformed to the bath frame.** In each panel, the mean-energy line, μ_line = δ(K−K̄), and the endpoint mixture, μ_end = (1−K̄/Q)δ(K) + (K̄/Q)δ(K−Q), share unit electron count and the same rest-frame mean kinetic energy K̄ within the common allowed interval 0≤K≤Q. The tritium witness uses K̄ = 5.690 keV and Q = 18.590 keV; the neutron witness uses K̄ = 301.370 keV and Q = 782.347 keV. `Q` here labels the adopted upper support parameter of these diagnostics. **Neither measure is an evaluated beta spectrum.**

The plotted quantity is the stored bath-frame kinetic-energy moment inside 10–9937.21 eV divided by the stored total bath-frame kinetic-energy moment. The independent variable is the dimensionless boost parameter u = γβ. The eight stored samples are displayed at equally spaced categorical positions; small opposite horizontal offsets separate coincident markers. The positions and offsets imply no interpolation in u, and no lines or newly evaluated intermediate samples are present. The tritium panel uses a linear vertical axis. The neutron panel uses a symmetric-logarithmic vertical axis, linear for |fraction|≤10⁻⁶, so that exact zero and the small positive saved fractions remain visible. All plotted fractions are nonnegative.

At u = 0 the tritium mean line is wholly within the finite energy range and has coverage 1, whereas its endpoint mixture has coverage 0. At u = 0.05 these values are 0.95401643 and 0.06991835; at u = 0.2 they are 0.10097195 and 0.01678542. For the neutron samples, the endpoint mixture has coverage 0.0012978477 at u = 0.05, while the mean line has coverage 3.6341773×10⁻⁵ at u = 1. These are properties of the saved witness measures at the specified boosts, not predictions for physical beta spectra. In particular, a zero-energy rest-frame component may acquire bath-frame kinetic energy after a boost; its entry into the finite window does not make a generic gas-deposition model admissible.

The displayed comparison establishes that the declared rest count, mean and support bound alone do not determine finite energy-window coverage. It neither asserts accuracy of an interpolated FS response nor establishes physical deposition for an unspecified gas composition. The figure consumes 32 completed partition records; it performs no Lorentz transform, source call, ODE solve or physics rerun. Exact input bytes are pinned in `INPUT_PINS.json`; the extracted table is `boost_coverage.csv` in the authoritative analysis run. `global_error_bound = null` remains unchanged.

**Files:** `boost_finite_energy_coverage_180mm.{png,pdf}` and `boost_finite_energy_coverage_90mm.{png,pdf}` in the authoritative run directory.
