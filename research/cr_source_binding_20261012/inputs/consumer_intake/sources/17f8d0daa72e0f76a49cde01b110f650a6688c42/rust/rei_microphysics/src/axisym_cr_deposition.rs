//! Opt-in, source-bound local CR deposition component.
//!
//! The proton population remains outside the ambient H/He inventory. This
//! receiver accepts ionization/deposition events, not injected baryon counts.
//! Prompt excitation and continuum radiation escape under the named closure;
//! no photons are reinjected without a spectrum. This is not a CR history,
//! FT03 cold-gas extrapolation, or a change to SourceBoundConditional.
use crate::{
    axisym_coupled_derivative, AxisymCoupledDerivative, AxisymCoupledState, AxisymLocalSources,
    AxisymmetricPoint, ForwardError, IsotopeSpecies,
};

pub const CR_DEPOSITION_CLOSURE: &str =
    "FS10_LOCAL_DEPOSITION_PROMPT_EXCITATION_AND_CONTINUUM_ESCAPE";
pub const CR_BOLTZMANN_J_K: f64 = 1.380_649e-23;

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct CrGasBinding {
    pub time_s: f64,
    pub n_h_m3: f64,
    pub n_he_m3: f64,
    /// Adopted FS10-style manifold: x_HII = x_HeII = xi; x_HeIII = 0.
    /// The selected Y_He is a scenario, not verified equality to the table's
    /// original Monte Carlo abundance (which is not independently specified).
    pub xi: f64,
    pub temperature_k: f64,
    pub y_he_mass_fraction: f64,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct CrDepositionPacket<'a> {
    pub provider_id: &'a str,
    pub manifest_sha256: &'a str,
    pub packet_sha256: &'a str,
    pub closure: &'a str,
    pub gas: CrGasBinding,
    /// Order HI, HeI; source-specific primary thresholds are retained.
    pub primary_rate_m3_s: [f64; 2],
    pub primary_threshold_j: [f64; 2],
    /// Order HI, HeI, HeII; these are secondary event yields, not powers.
    pub secondary_rate_m3_s: [f64; 3],
    pub secondary_threshold_j: [f64; 3],
    pub ionization_power_j_m3_s: f64,
    /// Chosen-interpolation heat BEFORE the bounded energy-closure projection.
    /// Includes an explicit threshold-anchor interpolation correction; the
    /// provider audit retains that correction and raw tabulated heat separately.
    pub raw_heat_power_j_m3_s: f64,
    pub heat_power_j_m3_s: f64,
    pub heat_correction_j_m3_s: f64,
    pub excitation_escape_power_j_m3_s: f64,
    pub continuum_escape_power_j_m3_s: f64,
    /// Energy lost in the explicitly modelled ionization/degradation component.
    /// It is not the full injected proton power or a complete stopping model.
    pub modelled_ionization_loss_power_j_m3_s: f64,
    pub full_injection_power_j_m3_s: f64,
    /// Signed chosen-interpolation channel sum minus modelled loss, before the
    /// bounded numerical energy-closure projection. This is not a physical
    /// uncertainty certificate or an assertion of simple print-rounding error.
    pub table_raw_residual_j_m3_s: f64,
    pub table_correction_bound_j_m3_s: f64,
}

// Generated from the independently acquired provider packet, not a numeric
// default. Until such a packet exists the receiver is fail-closed.
include!("axisym_cr_deposition_pin.rs");

pub fn pinned_cr_deposition_packet() -> Result<CrDepositionPacket<'static>, ForwardError> {
    pinned_cr_deposition_packet_for_xi(0.01)
}

/// Return one exact acquired FS10 composition knot. The receiver never
/// interpolates packets across ionization fractions.
pub fn pinned_cr_deposition_packet_for_xi(
    xi: f64,
) -> Result<CrDepositionPacket<'static>, ForwardError> {
    match xi.to_bits() {
        x if x == 0.01_f64.to_bits() => {
            PINNED_CR_DEPOSITION_XI001.ok_or(ForwardError::MissingAuthority("CR_PACKET_NOT_PINNED"))
        }
        x if x == 0.1_f64.to_bits() => {
            PINNED_CR_DEPOSITION_XI010.ok_or(ForwardError::MissingAuthority("CR_PACKET_NOT_PINNED"))
        }
        _ => Err(ForwardError::MissingAuthority(
            "CR_PACKET_COMPOSITION_NOT_PINNED",
        )),
    }
}

/// Fixed background snapshot from the same source manifest as the packet.
pub fn pinned_cr_deposition_geometry() -> Result<AxisymmetricPoint, ForwardError> {
    let time = pinned_cr_deposition_packet()?.gas.time_s;
    AxisymmetricPoint::new(
        (PINNED_CR_H_S * time).exp(),
        PINNED_CR_SHEAR_S * time,
        PINNED_CR_H_S,
        PINNED_CR_SHEAR_S,
    )
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct CrDepositionAudit {
    pub ionization_rate_m3_s: [f64; 3],
    pub table_raw_residual_j_m3_s: f64,
    pub heat_correction_j_m3_s: f64,
    pub table_correction_bound_j_m3_s: f64,
    pub corrected_energy_residual_j_m3_s: f64,
    pub modelled_ionization_loss_power_j_m3_s: f64,
    pub full_injection_power_j_m3_s: f64,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct CrDepositionResult {
    pub derivative: AxisymCoupledDerivative,
    pub audit: Option<CrDepositionAudit>,
}

fn error(code: &'static str) -> ForwardError {
    ForwardError::InvalidInput(code)
}

fn sum(values: impl IntoIterator<Item = f64>) -> f64 {
    let (mut s, mut c) = (0_f64, 0_f64);
    for v in values {
        let next = s + v;
        c += if s.abs() >= v.abs() {
            (s - next) + v
        } else {
            (v - next) + s
        };
        s = next;
    }
    s + c
}

fn closed(residual: f64, scale: f64) -> bool {
    residual.is_finite()
        && scale.is_finite()
        && scale >= 0.
        && if scale == 0. {
            residual == 0.
        } else {
            residual.abs() <= 128. * f64::EPSILON * scale
        }
}

fn equal(a: f64, b: f64) -> bool {
    closed(a - b, a.abs().max(b.abs()))
}

fn numbers(p: &CrDepositionPacket<'_>) -> Vec<f64> {
    [
        p.gas.time_s,
        p.gas.n_h_m3,
        p.gas.n_he_m3,
        p.gas.xi,
        p.gas.temperature_k,
        p.gas.y_he_mass_fraction,
    ]
    .into_iter()
    .chain(p.primary_rate_m3_s)
    .chain(p.primary_threshold_j)
    .chain(p.secondary_rate_m3_s)
    .chain(p.secondary_threshold_j)
    .chain([
        p.ionization_power_j_m3_s,
        p.raw_heat_power_j_m3_s,
        p.heat_power_j_m3_s,
        p.heat_correction_j_m3_s,
        p.excitation_escape_power_j_m3_s,
        p.continuum_escape_power_j_m3_s,
        p.modelled_ionization_loss_power_j_m3_s,
        p.full_injection_power_j_m3_s,
        p.table_raw_residual_j_m3_s,
        p.table_correction_bound_j_m3_s,
    ])
    .collect()
}

fn validate_packet(p: &CrDepositionPacket<'_>) -> Result<CrDepositionAudit, ForwardError> {
    if numbers(p).iter().any(|v| !v.is_finite())
        || p.gas.n_h_m3 <= 0.
        || p.gas.n_he_m3 <= 0.
        || !(0. ..1.).contains(&p.gas.xi)
        || p.gas.temperature_k <= 0.
        || !(0. ..1.).contains(&p.gas.y_he_mass_fraction)
        || p.primary_rate_m3_s
            .iter()
            .chain(&p.secondary_rate_m3_s)
            .any(|v| *v < 0.)
        || p.primary_threshold_j
            .iter()
            .chain(&p.secondary_threshold_j)
            .any(|v| *v <= 0.)
        || [
            p.ionization_power_j_m3_s,
            p.raw_heat_power_j_m3_s,
            p.heat_power_j_m3_s,
            p.excitation_escape_power_j_m3_s,
            p.continuum_escape_power_j_m3_s,
            p.modelled_ionization_loss_power_j_m3_s,
            p.full_injection_power_j_m3_s,
            p.table_correction_bound_j_m3_s,
        ]
        .iter()
        .any(|v| *v < 0.)
    {
        return Err(error("CR_DEPOSITION_DOMAIN"));
    }
    if p.closure != CR_DEPOSITION_CLOSURE {
        return Err(error("CR_DEPOSITION_CLOSURE"));
    }
    let y = p.gas.y_he_mass_fraction;
    if !equal(p.gas.n_he_m3 / p.gas.n_h_m3, y / (4. * (1. - y))) {
        return Err(error("CR_DEPOSITION_COMPOSITION"));
    }
    let ion_power = sum(p
        .primary_rate_m3_s
        .iter()
        .zip(p.primary_threshold_j)
        .chain(p.secondary_rate_m3_s.iter().zip(p.secondary_threshold_j))
        .map(|(r, e)| r * e));
    if !equal(ion_power, p.ionization_power_j_m3_s) {
        return Err(error("CR_DEPOSITION_IONIZATION_POWER"));
    }
    let loss = p.modelled_ionization_loss_power_j_m3_s;
    let raw = sum([
        p.raw_heat_power_j_m3_s,
        ion_power,
        p.excitation_escape_power_j_m3_s,
        p.continuum_escape_power_j_m3_s,
        -loss,
    ]);
    let scale = sum([
        p.raw_heat_power_j_m3_s,
        ion_power,
        p.excitation_escape_power_j_m3_s,
        p.continuum_escape_power_j_m3_s,
        loss,
    ]);
    if !closed(raw - p.table_raw_residual_j_m3_s, scale)
        || p.table_raw_residual_j_m3_s.abs() > p.table_correction_bound_j_m3_s
        || p.heat_correction_j_m3_s.abs() > p.table_correction_bound_j_m3_s
        || !closed(
            p.heat_correction_j_m3_s + p.table_raw_residual_j_m3_s,
            scale,
        )
        || !closed(
            p.heat_power_j_m3_s - p.raw_heat_power_j_m3_s - p.heat_correction_j_m3_s,
            scale,
        )
    {
        return Err(error("CR_DEPOSITION_TABLE_CORRECTION"));
    }
    let corrected = sum([
        p.heat_power_j_m3_s,
        ion_power,
        p.excitation_escape_power_j_m3_s,
        p.continuum_escape_power_j_m3_s,
        -loss,
    ]);
    if !closed(corrected, scale) {
        return Err(error("CR_DEPOSITION_ENERGY_LEDGER"));
    }
    let rates = [
        p.primary_rate_m3_s[0] + p.secondary_rate_m3_s[0],
        p.primary_rate_m3_s[1] + p.secondary_rate_m3_s[1],
        p.secondary_rate_m3_s[2],
    ];
    if rates.iter().any(|v| !v.is_finite()) {
        return Err(error("CR_DEPOSITION_OVERFLOW"));
    }
    Ok(CrDepositionAudit {
        ionization_rate_m3_s: rates,
        table_raw_residual_j_m3_s: p.table_raw_residual_j_m3_s,
        heat_correction_j_m3_s: p.heat_correction_j_m3_s,
        table_correction_bound_j_m3_s: p.table_correction_bound_j_m3_s,
        corrected_energy_residual_j_m3_s: corrected,
        modelled_ionization_loss_power_j_m3_s: loss,
        full_injection_power_j_m3_s: p.full_injection_power_j_m3_s,
    })
}

fn bound_packet(p: &CrDepositionPacket<'_>) -> Result<CrDepositionAudit, ForwardError> {
    let audit = validate_packet(p)?;
    let expected = pinned_cr_deposition_packet_for_xi(p.gas.xi)?;
    // The provider acquisition path verifies source bytes. Here the compiled
    // output fixture is checked field-for-field; identity strings alone cannot
    // bless arbitrary numbers as physical output.
    if p.provider_id != expected.provider_id
        || p.manifest_sha256 != expected.manifest_sha256
        || p.packet_sha256 != expected.packet_sha256
        || p.closure != expected.closure
        || !numbers(p)
            .iter()
            .zip(numbers(&expected))
            .all(|(a, b)| a.to_bits() == b.to_bits())
    {
        return Err(error("CR_DEPOSITION_SOURCE_PIN_MISMATCH"));
    }
    Ok(audit)
}

fn validate_state(
    time_s: f64,
    state: &AxisymCoupledState,
    kb: f64,
    gas: CrGasBinding,
) -> Result<(), ForwardError> {
    if time_s.to_bits() != gas.time_s.to_bits() || kb.to_bits() != CR_BOLTZMANN_J_K.to_bits() {
        return Err(error("CR_DEPOSITION_STATE_BINDING"));
    }
    let mut expected = [0.; 13];
    expected[IsotopeSpecies::H1Neutral as usize] = gas.n_h_m3 * (1. - gas.xi);
    expected[IsotopeSpecies::H1Ionized as usize] = gas.n_h_m3 * gas.xi;
    expected[IsotopeSpecies::He4Neutral as usize] = gas.n_he_m3 * (1. - gas.xi);
    expected[IsotopeSpecies::He4SinglyIonized as usize] = gas.n_he_m3 * gas.xi;
    for species in IsotopeSpecies::ALL {
        if !equal(
            state.isotopes.density_m3(species),
            expected[species as usize],
        ) {
            return Err(error("CR_DEPOSITION_STATE_BINDING"));
        }
    }
    let particles = state.isotopes.thermal_particle_density_all_thermal_m3()?;
    let u = 1.5 * kb * particles * gas.temperature_k;
    if !equal(state.thermal_energy_j_m3, u) {
        return Err(error("CR_DEPOSITION_STATE_BINDING"));
    }
    Ok(())
}

fn validate_geometry(geometry: AxisymmetricPoint) -> Result<(), ForwardError> {
    let expected = pinned_cr_deposition_geometry()?;
    if !equal(geometry.mean_scale_factor, expected.mean_scale_factor)
        || !equal(geometry.anisotropy, expected.anisotropy)
        || !equal(geometry.mean_hubble_per_s, expected.mean_hubble_per_s)
        || !equal(geometry.shear_per_s, expected.shear_per_s)
    {
        return Err(error("CR_DEPOSITION_GEOMETRY_BINDING"));
    }
    Ok(())
}

/// OFF never evaluates the provider. ON is one exact, source-pinned local gas
/// state, not an interpolated state/history. No primary photons are consumed.
pub fn cr_deposition_derivative<'a, F>(
    enabled: bool,
    time_s: f64,
    geometry: AxisymmetricPoint,
    state: &AxisymCoupledState,
    kb_j_k: f64,
    provider: F,
) -> Result<CrDepositionResult, ForwardError>
where
    F: FnOnce() -> Result<CrDepositionPacket<'a>, ForwardError>,
{
    let mut sources = AxisymLocalSources {
        species_m3_s: [0.; 13],
        electron_m3_s: 0.,
        photon_number_m3_s: 0.,
        photon_power_j_m3_s: 0.,
        thermal_power_j_m3_s: 0.,
        internal_power_j_m3_s: 0.,
        escape_power_j_m3_s: 0.,
        external_power_j_m3_s: 0.,
    };
    let audit = if enabled {
        let p = provider()?;
        let a = bound_packet(&p)?;
        validate_geometry(geometry)?;
        validate_state(time_s, state, kb_j_k, p.gas)?;
        let [h, he0, he1] = a.ionization_rate_m3_s;
        sources.species_m3_s[IsotopeSpecies::H1Neutral as usize] = -h;
        sources.species_m3_s[IsotopeSpecies::H1Ionized as usize] = h;
        sources.species_m3_s[IsotopeSpecies::He4Neutral as usize] = -he0;
        sources.species_m3_s[IsotopeSpecies::He4SinglyIonized as usize] = he0 - he1;
        sources.species_m3_s[IsotopeSpecies::He4DoublyIonized as usize] = he1;
        sources.electron_m3_s = sum([h, he0, he1]);
        sources.thermal_power_j_m3_s = p.heat_power_j_m3_s;
        sources.internal_power_j_m3_s = p.ionization_power_j_m3_s;
        sources.escape_power_j_m3_s =
            p.excitation_escape_power_j_m3_s + p.continuum_escape_power_j_m3_s;
        sources.external_power_j_m3_s = p.modelled_ionization_loss_power_j_m3_s;
        Some(a)
    } else {
        None
    };
    let derivative =
        axisym_coupled_derivative(time_s, geometry, state, kb_j_k, |_, _| Ok(sources))?;
    Ok(CrDepositionResult { derivative, audit })
}
