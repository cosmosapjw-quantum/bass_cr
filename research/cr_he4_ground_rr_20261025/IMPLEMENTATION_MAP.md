# Definition–implementation–evidence map

| Definition / operation | Implementation | Actual evidence |
|---|---|---|
| Native source identity and all21 input pins | `verify`, `validate_config`, `prepare_inputs.py` | `inputs/INPUT_MANIFEST.json`; canonical164payload checks |
| HeI I24.59,d4,nHeII.02, positive finite support | `coefficients` | controls_v2; C9 selected independent coefficients |
| Saved PR105 K as exact numerical baseline | `consume` | equality checks vs PR104 grids/offdiagonals, H1 rates |
| Shared H1+He competition | physical16 columns6–9 | 192 primary RHS; four-RHS analytic control |
| Rare single-channel bound | `w`, `eta`, pHe bound metrics | every primarycase JSON; Decimal70 C9 |
| Stable CE/time/H1 changes | response3 | primary savedNPZ and source rows |
| Conditional time | conditional4 | primary rows; C9 all48 selected RHS |
| Separate H1/He photon and internal rewards | `source_average`, energy_terms | own-scale energycontrol; signed total ledger |
| Immutable source projection reuse | `source_average` | masks, count/kinetic identitychecks; oldprojectioncalls0 |
| Grid and upper-domain comparisons | `primary.py` | 216 comparisons in SOURCE_WEIGHTED_RESULTS |
| Bounded and create-only execution | `dispatch.py` | RESOURCE_ADMISSION/PRE_EXECUTION/DISPATCH_RECEIPT perrun |
| No baseline solver replay | input recovery then alteredoperator only | oldprimary/generator/quadrature/ODE counters0 |

The public source repository omits private NPZ input/output arrays and native
table bytes. The canonical source ZIP carries them with exact hashes. No
production solver imports the independent reviewer, and the reviewer imports
no production module. The failed controls_v1 admission has no child start; its
receipt and prior dispatcher source remain under runs/evidence.
