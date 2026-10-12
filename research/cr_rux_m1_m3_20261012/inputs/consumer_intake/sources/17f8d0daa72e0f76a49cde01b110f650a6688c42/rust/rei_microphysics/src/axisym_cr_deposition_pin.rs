// Exact provider output fixture. Provenance/approximation audit is preserved
// with CR_PACKET.json, SOURCE_MANIFEST.json and PROVIDER_AUDIT.json.
// It represents an instantaneous terminal operator on a prescribed collisionless
// CR snapshot; no causal turn-on deposition history or delay admission.
// Pinned source-manifest constant background, normalized at the source birth.
const PINNED_CR_H_S: f64 = 3.3e-17;
const PINNED_CR_SHEAR_S: f64 = 3.3e-18;
const PINNED_CR_DEPOSITION_XI001: Option<CrDepositionPacket<'static>> = Some(CrDepositionPacket {
    provider_id: "CRP_L17_MD14_RUDD_FS10_XI001_CONDITIONAL_V1",
    manifest_sha256: "79835c5eaa891f37f663c1852d6035ee446a25778763164cfea2d20531cdd901",
    packet_sha256: "1bb0d4e1c4c71a409ca170e8741fabd17fabe02195b86fe24a06875712d0e373",
    closure: "FS10_LOCAL_DEPOSITION_PROMPT_EXCITATION_AND_CONTINUUM_ESCAPE",
    gas: CrGasBinding {
        n_h_m3: 140.0,
        n_he_m3: 11.542553191489361,
        temperature_k: 100.0,
        time_s: 10000000000.0,
        xi: 0.01,
        y_he_mass_fraction: 0.248,
    },
    continuum_escape_power_j_m3_s: 0.0,
    excitation_escape_power_j_m3_s: 6.613224299070425e-43,
    full_injection_power_j_m3_s: 5.315371751092545e-34,
    heat_correction_j_m3_s: -1.649729386090965e-46,
    heat_power_j_m3_s: 1.2093044641845817e-42,
    ionization_power_j_m3_s: 1.3963750685843803e-42,
    modelled_ionization_loss_power_j_m3_s: 3.2670019626760045e-42,
    primary_rate_m3_s: [3.0408320268293704e-25, 3.939518790179256e-26],
    primary_threshold_j: [2.1798723611035473e-18, 3.939752343006e-18],
    raw_heat_power_j_m3_s: 1.2094694371231908e-42,
    secondary_rate_m3_s: [
        2.409590409465263e-25,
        1.3473438015813675e-26,
        1.8524260884188393e-29,
    ],
    secondary_threshold_j: [
        2.1789602222399996e-18,
        3.94135451964e-18,
        8.715840888959999e-18,
    ],
    table_correction_bound_j_m3_s: 2.4489321098323726e-46,
    table_raw_residual_j_m3_s: 1.649729386090965e-46,
});

// FS10's independently acquired xi=.1 table is a second discrete manifold
// point. It is not an interpolation between it and the xi=.01 packet.
const PINNED_CR_DEPOSITION_XI010: Option<CrDepositionPacket<'static>> = Some(CrDepositionPacket {
    provider_id: "CRP_L17_MD14_RUDD_FS10_XI010_CONDITIONAL_V1",
    manifest_sha256: "d34b42d652b8b721caabeda95ad729753a850f6da7499f4cedfeb8b299c35b44",
    packet_sha256: "2ecb1413c93f5cbc9ab64689ac17c191020320c9734138ea4bfaf291e10b6d46",
    closure: "FS10_LOCAL_DEPOSITION_PROMPT_EXCITATION_AND_CONTINUUM_ESCAPE",
    gas: CrGasBinding {
        n_h_m3: 140.0,
        n_he_m3: 11.542553191489361,
        temperature_k: 100.0,
        time_s: 10000000000.0,
        xi: 0.1,
        y_he_mass_fraction: 0.248,
    },
    continuum_escape_power_j_m3_s: 0.0,
    excitation_escape_power_j_m3_s: 2.1689058806714367e-43,
    full_injection_power_j_m3_s: 5.315371751092545e-34,
    heat_correction_j_m3_s: -6.077657498225953e-47,
    heat_power_j_m3_s: 1.8054996515543073e-42,
    ionization_power_j_m3_s: 9.476115446294631e-43,
    modelled_ionization_loss_power_j_m3_s: 2.970001784250914e-42,
    primary_rate_m3_s: [2.7643927516630653e-25, 3.581380718344779e-26],
    primary_threshold_j: [2.1798723611035473e-18, 3.939752343006e-18],
    raw_heat_power_j_m3_s: 1.8055604281292896e-42,
    secondary_rate_m3_s: [
        8.328070180048539e-26,
        5.504302721936275e-27,
        8.62720537811717e-29,
    ],
    secondary_threshold_j: [
        2.1789602222399996e-18,
        3.94135451964e-18,
        8.715840888959999e-18,
    ],
    table_correction_bound_j_m3_s: 2.2263019180294305e-46,
    table_raw_residual_j_m3_s: 6.077657498214004e-47,
});
