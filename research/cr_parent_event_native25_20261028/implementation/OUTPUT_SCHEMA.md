# Prospective parent-event output schema V1

Unit: `CR_PHYS02_PARENT_EVENT_NATIVE25_V1`. This is an interface specification,
not an executed result. New authoritative scalar arithmetic is serialized as
decimal strings; original saved response scalars remain binary64 numbers with
their original file SHA, JSON pointer, and hexadecimal representations.

## CLI and ownership

All worker dispatches use exactly one `--out`, matching `runs/<run_id>`.

```text
python implementation/parent_event.py prepare --out runs/prepare_v1
python implementation/controls.py --prepared runs/prepare_v1 --out runs/controls_v1
python implementation/parent_event.py primary --prepared runs/prepare_v1 --out runs/primary_v1
python implementation/independent_reference.py --primary runs/primary_v1/RESULT.json --out runs/independent_v1
```

Every CLI checks `CR_BOUNDED_UNIT`, `CR_BOUNDED_OUTDIR`,
`CR_BOUNDED_ATTEMPT_ID`, and the create-only `RESERVATION.json` written by the
new runner before doing scientific imports or calculations. A reference may
offer `--outdir` as a parser alias, but root dispatch uses `--out` for runner
binding. Output files are create-only. No production import is required by the
independent reference.

## Preparation

`PREPARATION.json` has schema `CR_PARENT_EVENT_PREPARATION_V1`, `unit`, `status`,
`input_identity`, `coefficient_identification`, `projection_validation`,
`artifacts`, `checks`, and `scope`. `status` is `PASS_SCOPED_MODEL_IDENTIFICATION`
only after actual applicable checks pass, otherwise
`MODEL_IDENTIFICATION_UNRESOLVED`. A failed preparation writes its diagnostic
record and does not authorize primary adoption or an alternate fit.

`coefficient_identification` keys:

- `theta_order`: `["theta_H","theta_He1","theta_He2"]`, meaning c2_H, c1_He, c2_He.
- `theta_decimal`, `theta_float64`, `theta_float64_hex`: three-element lists.
- `input_representation`, `recovery_bands`, `holdout_results`.
- `M_decimal`, `B_decimal`, `inverse_B_decimal`: 3×3 string arrays.
- `row_scales_decimal`, `column_scales_decimal`, `z_decimal`.
- `rcond_inf_decimal`, `sensitivity_decimal`, `positive_lower_z_decimal`.
- `solve_residual_decimal`, `precision_decimal_digits`, `pivot_log`, `checks`, `status`.

Each holdout row has `interval_eV`, `saved_binary64`, `saved_hex`,
`predicted_decimal`, `relative_error_decimal`, `relative_error_float64`, `pass`.
The source constant representations are exact lifts of original binary64;
declared energy-convention decimal lexemes are separate.

`projection_validation.target_totals` contains keys `H` and `He`. Each target
has string `number_coefficient_m3_s2`, `energy_coefficient_eV_m3_s2`,
`analytic_number_coefficient_m3_s2`, `analytic_energy_coefficient_eV_m3_s2` and
the corresponding `analytic_number_relative_error` and
`analytic_energy_relative_error`. Other projection keys include
`canonical_atom_count`, `max_atom_relative_error`, `canonical_exact_zero_pass`,
`canonical_total_number_relative_error`, `canonical_total_energy_relative_error`,
`atom_relative_tolerance`, `quadrature`, `checks`, and `status`.

`ATTRIBUTION_ARRAYS.npz` contains binary64 arrays. Its first row is the original
cutoff ghost at 0.1 eV; the following 3200 rows are the exact saved active grid.
The active grid is never regenerated.

| Member | Shape | Meaning |
|---|---|---|
| `energy_eV_with_cutoff` | (3201,) | Original ghost + original active grid |
| `canonical_A_m3_s2` | (3201,) | Unchanged original selected source numbers |
| `basis_K` | (3201,3) | Newly evaluated original-Q8 linear basis projector |
| `identified_A_H_m3_s2` | (3201,) | Identified H contribution |
| `identified_A_He_m3_s2` | (3201,) | Identified inclusive-He electron contribution |
| `reconstruction_residual_A_m3_s2` | (3201,) | H+He−canonical; never reassigned |
| `atom_relative_error` | (3201,) | Absolute residual / own canonical atom scale |
| `quadrature_nodes` | (8,) | Actual new NumPy leggauss(8) output |
| `quadrature_weights` | (8,) | Actual new NumPy leggauss(8) output |

Preparation records exact artifact/member bytes and SHA256 under
`artifacts["ATTRIBUTION_ARRAYS.npz"].arrays[member]`, with `shape`, `dtype`
(NumPy dtype.str, e.g. `<f8`), `order`, `bytes`, and `sha256`. Primary copies the
same NPZ bytes after validating preparation provenance; it does not recompute
the fit or source projection.

## Primary RESULT.json

Schema `CR_PARENT_EVENT_RESULT_V1`; top-level fields are `unit`, `status`,
`input_identity`, `scope`, `preparation`, `coefficient_identification`,
`projection_validation`, `baseline`, `prefixes`, `observation_bins`,
`adoption_registry`, `acceptance`, `unresolved_inputs`, `artifacts`, and
`resource_receipt_reference`. `baseline.Y_decimal` is the exact same-state
conditional 21-species inventory divided by explicit nb, with `n_b_m3_decimal`,
`n_part0_m3_decimal`, `T0_K_decimal`, `species_order`, `charges`, `mass_numbers`.
The successful scoped status is `PASS_SCOPED_PARENT_EVENT_PARTIAL_RETURN`;
failed internal criteria use `HOLD_SCOPED_PARENT_EVENT_RETURN`. Both retain the
actual full physical point as null. `input_identity` uses exact original
manifest path/bytes/SHA rows for `source_record`, `moment_source`,
`coverage_source`, `saved_response`, `saved_response_arrays`, together with
`family_id`, `partition_id`, `source_revision`, `retained_revision`, and
`source_payload_sha256`.

There are four `prefixes` and four `observation_bins`. Each row has:

- `index` (0..3), `interval_s` (two exact binary64 times), and saved-compatible
  `role`: `nonadditive_cumulative_prefix` or `disjoint_observation_bin`.
- `source_H_N_E` and `source_He_electron_N_E`: decimal-string `number_m3`,
  `energy_eV_m3`, `endpoint_number_rate_m3_s`, `endpoint_energy_rate_eV_m3_s`;
  endpoint values use known source history, with T marked as a left limit.
- `canonical_source_N_E`: original saved `number_m3` and `energy_eV_m3` numbers.
- `split_residuals`: decimal-string `number_m3`, `energy_eV_m3`,
  `number_relative`, `energy_relative`; never heat or thermal electrons.
- `saved_response_reference`: original RESULT/ARRAYS path/hash, JSON pointer,
  and exact saved row fields. No old response is recomputed.
- `event_terms`: new decimal-string `J_H`, `N_eHe`; original binary64 `C_H`,
  `C_He`, `K_H`, `K_He`, `retained_photon_H`, `retained_photon_He`,
  `cutoff_direct_N`, `cutoff_drift_N`, `cutoff_N`, `cutoff_U`, `Coulomb_Q`,
  `active_N_change`, `active_U_change`; `saved_binary64_hex` and `saved_channels`
  preserve the own-scale RR evidence. Declared source/RR binding and literal
  terms are stored separately under `energy_sidecars`.
- `native_affine_Y`: `intercept_decimal`, `coefficient_p_decimal`,
  `coefficient_d_decimal`, each length21; `intercept_float64`; `parameter_units`,
  `actual_parameters` with s/p/d null, `intercept_is_actual_branch=false`,
  `unknown_partner_addendum=null`. Parameters p,d are proper m^-3.
- `selected_nonthermal_component`: `retention` and `assimilation_fixture`,
  each with string `delta_zeta` and `delta_w_nt_J_per_baryon`. This is the
  selected component, never a complete unknown-partner state.
- `energy_sidecars`: `L0_eV_m3`, `chemical_intercept_eV_m3`,
  `chemical_coefficient_p_eV`, `chemical_coefficient_d_eV`,
  `literal_convention_residual_eV_m3`, `literal_terms_eV_m3`,
  `selected_balance_intercept_eV_m3`, `saved_energy_residual_eV_m3`,
  `balance_residual_after_saved_eV_m3`; all new evaluated scalars are strings.
  `branch_lift` has symbolic p/d coefficients; actual donor work/I2src/partner
  work/excitation stay null and are not silently merged with literal residuals.
  `saved_energy_residual_eV_m3` has the explicit sign
  `Uinj-(dUactive+UC+QC+PH+PHe-IHRR*CH-IHeRR*CHe)`. The after-saved residual is
  `selected_balance_intercept-literal_convention_residual-saved_energy_residual`.
  Original saved kinetic/total residual fields remain separate unchanged
  numbers. `literal_terms_eV_m3` keys are `source_H_convention`,
  `source_He_convention`, `RR_H_convention`, `RR_He_convention`.
- `retained_photon_reference`: per-channel exact saved NPZ descriptor,
  `count_member`, `energy_member`, `row_index`, member hashes, and saved port.
  Count members are `capture_H_prefix_m3`, `capture_He_prefix_m3` or the `_bins_`
  versions; photon energy members are `photon_H_energy_eV` and
  `photon_He_energy_eV`. No spectrum/time-history inversion is performed.
- `conditional_caloric`: two explicitly named p=d=0 fixtures, `retention` and
  `assimilation`. Each stores decimal-string `Q_J_m3`, `thermal_count_m3`,
  `baseline_thermal_energy_J_m3`, `baseline_particle_density_m3`,
  `delta_T_ratio`, `delta_logT`; binary64 diagnostic `delta_logT_float64`;
  `baseline_prefix_index` (null at origin). Bin baselines use the previous
  saved-prefix conditional Q/count endpoint. These fixtures are not actual He
  branch measurements and do not feed rates back.
- `conditional_closed_He_family`: p=0 fixtures at d/N_He=0,1/4,1/2; all labelled
  conditional, with species deltas and branch chemical lift, never an actual
  parameter default. Their kinetic/photon outputs remain separate.
- `checks`, `actual_full_native25=null`, `actual_external_work=null`,
  `actual_temperature_point=null`, `physical_heating_complete=false`.

All meaningful checks are serialized with actual results. `acceptance` reports
only current executed checks; old 517/112/46 are neither rerun nor added.
`adoption_registry` records nonadditive-prefix refusal and unique disjoint-bin
partial bookkeeping claims, with inherited RR-component ownership. It does not
activate a full physical consumer. Global completion/error/budget/currency and
absolute worldtube totals remain null.

`adoption_registry` is an object with `scope`, `claims`, `claim_count`,
`prefixes_additively_adopted=false`, `aggregate_includes_prior_RR=true`,
`full_consumer_activation=false`, `all_response_components_once`. Each claim
has family/recipient identity, component (`birth`, `RR:H`, `RR:He`, `cutoff`),
proper interval, native birth support, proper clock and interval meaning.
Only actual passing partial bookkeeping generates claims; diagnostic prefixes
and conditional fixtures cannot be additive claims.
