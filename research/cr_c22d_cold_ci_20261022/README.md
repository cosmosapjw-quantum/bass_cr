# C22D: finite-source H1 collisional ionization in a sandbox LRS pilot

**Science status: COMPLETE_SCOPED.** Four new integrations connect a pinned H1 electron-impact ionization source to the inherited finite-UV, thermal, Compton-bath and H1 n=2 model. All four saved and solver-accepted meshes pass the frozen conservation/domain checks. The nine-field BDF versus tighter Radau comparison passes its registered `2e-7` normalized criterion. Historical C21O/C22A/B/C integrations were reused; recovery reintegrations are zero.

Start with [REPORT_KO.md](REPORT_KO.md), [SCIENCE_ACCEPTANCE.json](SCIENCE_ACCEPTANCE.json), and [analysis_v1/ANALYSIS_REPORT_KO_v2.md](analysis_v1/ANALYSIS_REPORT_KO_v2.md). The current figure authority is [analysis_v1/figures_v2](analysis_v1/figures_v2); original figures and the display-correction history remain available. [evidence/review_final/FINAL_REVIEW_KO.md](evidence/review_final/FINAL_REVIEW_KO.md) records independent saved-array and source review.

## Frozen model and result

- Execution source identity: `2e065d2ec2605fcee4bd9f6444e90b58f85bbf047f4d1444dfe7e386eb828c72` (42 files).
- New equation: `H1(1s)+e -> H1+ +2e`; the event adds one free electron, moves the adopted threshold energy from thermal to binding energy, and adds no escaping-CI reservoir.
- Full/solver dimensions: 78/75. Only the inherited exact-zero n/T coordinates are removed. All 21 atomic inventory populations remain represented in outputs.
- Four new raw histories: 804 saved and 8,047 accepted samples; 72 segments. No NCP dispatch or old ODE rerun.
- LRS CI counter at z=2: `7.37974053e-6 / Href`. Same-registry CI ON−OFF final temperature: `-0.001745967 K`; final free-electron fraction change: `-8.78303490e-7 / Href`.
- The finite source uses 13.6058 eV as the CCC table convention. This differs from the physical H1 ionization energy. Old C22C versus the new registry is a separate comparison, not part of the matched CI effect.
- The CI effect on shear is unresolved at the present solver-comparison scale. Stable wall-time speedup and a global error certificate remain open.

## Evidence and continuation

`runs/` contains immutable new raw data and execution receipts. `analysis_v1/` contains saved/accepted diagnostics and the strict reference comparison. `evidence/theory/` binds rate coverage, energy/charge derivations, primary sources and the next line-energy contract. `evidence/optimization/` preserves same-input byte-equality checks and measured, variable timings. `evidence/latest_external_intake/` preserves the 7-repository intake and external failure history.

The next bounded unit uses stored signed H and shear to diagnose directional redshift and records missing line-transfer inputs as null. Geometry, level rates, 2-photon spectrum, cascade branching, mixing and secondary-electron sources are required before adopting an escape or fast-level closure. Full thermochemical/radiative closure remains OPEN; high-energy nuclear and general tilted/triaxial/polarized CMB remain HOLD. `global_error_bound=null`.

Publication and backup are independent axes. The source-only GitHub commit is `9496f159a0387713d9135398e1f1a3b3e4dcbee0`; final text publication, complete local commit/bundle and provider receipts are bound by the external final authority. The completed execution checkpoint already has actual Library and Dropbox byte/SHA/CRC readback evidence. Drive preservation remains OPEN. See [DELIVERY_SCOPE_KO.md](DELIVERY_SCOPE_KO.md) and the final authority accompanying the release archive.

Restoration reads already-verified ZIP bytes and creates a new destination. Existing run directories and completed trajectories are never recreated by an ODE run.
