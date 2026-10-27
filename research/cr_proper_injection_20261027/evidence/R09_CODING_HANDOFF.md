# R9 theory-to-code handoff

Use exact original fullBED9600 NPZ and NUMERICAL_RESULT hashes in inputs/INPUT_MANIFEST.json, with recorded original source snapshot4ca5a90de79c8fb82a25fd9e83615bec0dfa870b and identical-byte baselineD. Read arrays only; no source quadrature, projection, old generator/RHS/ODE replay.

For first9600 coordinates the stored B_i are energy coordinates: A_Ni=(U*/T²)B_i/E_i; A_E=(U*/T²)(sum active B_i+B_cutoffE). Add cutoff count9608 at0.1eV and cutoff energy9605 once. Low-cross9609/9610 are diagnostic duplicates; exclude them. FullBED/legacy share one physical source. Low/high birth partitions use the common parent U*=1.1242596728743301e-13eV/m³ and T=1e10s, without per-tag normalization.

Implement source native measure to proper j with clock/volume/target Jacobians once; stored PHYS02 inputs already include these factors. For segments with local elapsed polynomial coefficients, integrate stably using the difference times sum for linear histories. Positive width overlap in both time and native birth support defines duplicate events. Isotope/frame/state/support/horizon guards precede every actual return and registry mutation.

Produce3 tags ×6 windows: [0,T],[0,T/2],[T/2,T],[T/3,2T/3],[T(1-1e-6),T],[T,T]. Zero-width integrals0 are valid; missing history is null. Endpoint left rate at known T may be nonzero even for zero-width injection. No assumption outside [0,T].

Tolerances frozen atR1: source-moment relative2e-12, integration/additivity2e-14, energy conversion/balance scaled2e-14, independent Decimal reference2e-13. Use independent original-array Decimal80 reconstruction and saved original6moments. Preserve all controls/results and exact executed code. Actual nb/native25/worldtube totals/RR/retained heating stay null when their required inputs are absent.

C4 must bind current host admission and the separate20CPU-second budget including coordinator/failure costs before running. C9 independent review must inspect raw results plus code, close concrete findings, and disclose its reference/theory authorship. Workflow completion does not complete the physical join.

Native birth support and represented atomic support have different meanings. Here the original grid contains an exact10eV node; adjacent-node projection of high birth energies never reaches a node below10eV. The high-tag low_cross diagnostic includes the boundary E=10 and duplicates already represented mass. Therefore the recorded [0.1,10] and [10,900] supports need no enlargement; ownership uses native birth partitions, so touching10eV boundaries do not imply a duplicate source.
