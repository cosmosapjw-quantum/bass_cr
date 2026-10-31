# CR PHYS19: Williams-1998 crosswalk preparation (exploratory, source-conditional, HOLD)

Parent source PR143 HEAD `737ebb5e76cfc1e9b5ba238250956932455235a2`, frozen parent PR142 HEAD `b64d3a0e1895e004e89ea3ffc92ceb6aadd5c55c`. Input original 2066 He-origin first H(1s->2p) excitation events, from PR143 `SOURCE_2P_ALIGNMENT_MOMENTS.csv` Git blob `d7034188ca5a02dc37db24aaf8f7d550624567bd`. No event/rate/source-owner mutation. Earliest excitation sum 3.3158906934521573e-31 m^-3; latest sum 9.85567761064524e-32 m^-3.

## Actual science artifacts

- `results/SOURCE_2066_BORN_THETA_{30,90,150}DEG.csv` (2,066 rows each, **6,198 new conditional physical data rows**): actual source electron energies 14.60140625..20.99 eV, original event IDs/weights/A2 retained, new collision-plane pure momentum-transfer Born coherence at three specified electron scattering angles. NOT experimentally reconstructed rho, NOT a DCS-weighted source emission prediction, NOT physical source electron-axis distribution.
- `results/ONEILL1998_54P4_MEASURED_P1_P2.csv` (**11 measured reference rows**): O'Neill et al. PRL 80,1630 (1998), Table I, reduced P1,P2 and quoted 1sigma, measured at 54.4 eV with atomic deuterium target. Only central-value PSD-derived |I| upper bounds, NOT measured I, NOT 16.5 eV source data.
- `results/PURE_Q_BORN_REFERENCE_16P5_NOT_MEASURED.csv` (**37 theoretical rows**): E=16.5 eV, angles 0..180 step5, pure-q model for method contrast, NOT Williams 1998 measured `lambda,R,I`.
- Total **6,246 new science rows** with explicit evidence tiers. No claim of new main-DAG completed node.

### Algebra and definitions

Under a declared two-state collision-plane restriction, `P1=2lambda-1, P2=-2sqrt(2)R, P3=2sqrt(2)I`, and `B={{lambda,-sqrt(2)(R+iI)}, {-sqrt(2)(R-iI),1-lambda}}`. Wolfram symbolically verifies eigenvalues `(1±sqrt((2lambda-1)^2+8(R^2+I^2)))/2`. PSD iff `0<=lambda<=1` and `2(R^2+I^2)<=lambda(1-lambda)`. This is not a universal reconstruction of a general 3x3 orbital-spin density matrix. The `I` symbol in this section is the imaginary correlation parameter, not photon intensity.

Pure-q Born limit: `r=sqrt((E-10.1988 eV)/E)`, `q_z=1-r cos(theta)`, `q_x=-r sin(theta)`, `lambda=q_z^2/(q_z^2+q_x^2)`, `R=-q_z q_x/(sqrt(2)(q_z^2+q_x^2))`, `I=0`. This reference neglects finite atomic recoil in its purely angular kinematics. Axis signs are conventions requiring explicit crosswalk to experimental collision frame.

### Results and scope

Source-retained totals match prior after floating-point sum, and across 6198 new source model rows `max |det B| < 2.5e-16`; 54.4-eV measured central P1/P2 11/11 lie in the unit disk, min `det B(I=0)=0.0403`. 16.5-eV Born lambda at theta=50 degrees =0.6185093884 for this model. Same-author local 8/8 tests pass under ordinary Python and `python -O` for independently packaged reference code; **GitHub source script itself was not executed in native CI**.

PRIMARY missing input: Williams, J. F. (1998), *New and Old Measurements of Electron Scattering in Atomic Hydrogen*, *Australian Journal of Physics* 51,633–643, DOI 10.1071/P98023, Figures 6 (measured separate 2p DCS at 16.5 eV) and 7 (measured lambda,R,I at 16.5 eV). Official URL https://www.publish.csiro.au/ph/pdf/p98023 . Text read, but reliable raster/vector figure coordinates and error covariance NOT captured; no numeric measured 16.5-eV data were invented. Need page images/PDF with usable axis ticks, plotted symbols and error bars, ideally author numerical tables and common normalization covariance.

Useful cross-check: Bray, Konovalov, McCarthy 1991 *PRA* 44 5586, DOI 10.1103/PhysRevA.44.5586 (theory); Wang, Callaway, Unnikrishnan 1994 *PRA* 49 1854, DOI 10.1103/PhysRevA.49.1854 (theory). Higher-energy O'Neill benchmark is NOT transportable to the low-energy source without new physics evidence.

## Execute

From repository root: `python research/cr_phys19_williams1998_crosswalk_20261031/reproduce_phys19.py`. It rejects changed source bytes using original Git blob SHA1 and original event count/rates. Existing branch-generated rows may differ in last formatting digits from Python because remote rows were generated in an independently implemented JavaScript numerical pass; assess numerical/structural equivalence, not arbitrary byte identity.

## Gates / durable state

**CENTRAL_DAG 28/88 DELTA0; EXTENSION_DAG 0/3 DELTA0.** PHYS18 auxiliary still 1/1 conditional review HOLD, PHYS19 new scoped data product 1/1 produced but scientific source/claim HOLD. `PHYSICAL_2P_DENSITY_MATRIX=UNBOUND`, `ELECTRON_DIRECTION_OWNER=UNBOUND`, `FULL_RII_DETAILED_BALANCE=UNBOUND`, `PHYSICAL_K=UNBOUND`, `GLOBAL_HE_EXCLUSIVE=UNBOUND`. `PRODUCTION=NATIVE25=L4=HOLD`, `NO_MERGE=true`, `NO_FORCE_PUSH=true`, `AUTO_NEXT_NODE=false`. Real distinct-author R06/C09 NOT_RUN, native subagent NOT_RUN. Browser extension inaccessible (origin context), remote desktop offline. New files published to a dedicated draft successor branch, not merged; fresh Drive/Dropbox upload NOT_RUN, not advertised as dual backup.
