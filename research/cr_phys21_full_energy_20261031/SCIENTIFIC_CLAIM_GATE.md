# PHYS21 one-pass hostile scientific / code review, same author

Finding 1 THEORY/Numeric REPAIRED: The initial linear-in-cos(theta) 24-node integration overestimated original printed 2p integrated cross sections at 35eV by +5.62% and 40eV by +6.92%; invalidates initial source-level quadrupole and Stokes. Corrected to angular PCHIP(log DCS) and 0.25-degree per-bin Simpson, smoothly PSD interpolated B. Corrected 35 and 40 residuals -0.155% / -0.567% and independent Python/JS spot parity, without relaxing tolerance. Old first-pass files SUPSERSEDED NOT DELETED.

Finding 2 SCIENCE/CONDITIONAL: Original Bray 1991 6CCO five-energy printed 120 rows are theory, not empirical or convergent CCC. Williams 1998 experimental Fig6/7 approximate 16.5eV digitization is independent measured anchor. The 19.58-35eV bracket eliminates missing-energy source coverage for all 456 events; however interpolation theory systematic not fully constrained. 35 vs40 published-anchor variation is sensitivity only, not true confidence interval.

Finding 3 PHYSICS/DIRECTION BLOCK_NOW_FOR_GLOBAL: 2×2 reduced collision-plane density B is not the physical full 2p fine/hyperfine density. Original 2066 source events have electron E/rate but no actual incidence angular owner; local collision-plane Stokes Q/U/V for different electron angles refer to rotating photon direction/basis and cannot sum to global IGM polarization. The published atlas explicitly marks local, no global claim.

Finding 4 SCIENCE/SOURCE: IAEA CollisionDB D109688 B61 DOI appears to name an ion-atom article unrelated to e-H 2p, hence not promoted to primary. For totals use original Curtin CCC distributor and published model identity; for angle/polarization use Bray printed 6CCO, measured comparison Williams 1998.

Finding 5 IMPLEMENTATION/VERIFIED: Original 2066 source Git blob exact, event weights original, 2066 new highorder rows, 456*24=10944 highorder tail, 96 atlas. GitHub direct full readback max angular bin mass residual <9e-16, zero PSD failures and zero Stokes cone failures, source total exactly conserved within rounding, exact recoil energy residual ~6.71e-16. Local standalone checks 30/30 standard +30/30 optimized. Native GH-specific Python script not CI run, distinct-author review R06/C09 NOT_RUN.

Status: PHYS21 scoped data CONSTRUCTED, SCIENCE_REVIEW_HOLD. Canonical DAG28/88 delta0, extension0/3 delta0, production/native25/L4 HOLD. No merge, no force push, auto-next false.
