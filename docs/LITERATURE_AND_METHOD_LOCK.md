# R3M10 literature/method lock

- Kołakowska et al., PRA 58, 2872 (1998), DOI 10.1103/PhysRevA.58.2872: 3D Cartesian TDSE; capture obtained by explicit projection on projectile hydrogen states at 10, 40, 100 keV.
- Kołakowska, Pindzola, Schultz, PRA 59, 3588 (1999), DOI 10.1103/PhysRevA.59.3588: low-n lattice + high-n CTMC total charge transfer, close to McClure furnace scale.
- Toshima, PRA 59, 1981 (1999), DOI 10.1103/PhysRevA.59.1981: two-center pseudostate completeness; asymmetric continuum expansions converge more slowly/fail in regimes.
- Abdurakhmanov, Kadyrov, Bray, JPB 49 03LT01 (2016), DOI 10.1088/0953-4075/49/3/03LT01: two-center QM-CCC and independent single-/two-center electron-loss consistency.
- Horbatsch (1997), DOI 10.30970/JPS.01.383: Cartesian p-H continuum has saddle-point longitudinal population near ~0.5 vp, motivating explicit continuum/region diagnostics.
- Gordon, Jirauschek, Kärtner, PRA 73 042505 (2006): Coulomb-singularity-aware discretization literature. This package instead uses a cell-centered uniform lattice so neither nucleus is forced onto a node for the frozen b-grid; this is an independent discretization, not a reproduction of their ABC method.

TDL propagation here is a second-order Strang split operator with FFT kinetic step and a cosine mask absorber. It is deliberately an independently auditable implementation, not a claim about the private Nichols propagator.

## R3M26 current authority (2026-09-24)

The historical sources above remain comparison/method provenance. Production is now defined by the explicit internally consistent model and validated numerical implementation, not exact paper reproduction. The derivation, additional primary sources and applicability limits are in `r3m26/MODEL_FOUNDATION_KO.md`. The canonical controlled runner uses a fixed-rate CAP with symmetric half steps; the historical base runner's per-step post-mask is not the current time-refinement authority. Frozen `cr_repro/*.py` remains unchanged in R3M26.
