use rei_microphysics::axisym_cr_deposition::{
    cr_deposition_derivative, pinned_cr_deposition_geometry, pinned_cr_deposition_packet,
    pinned_cr_deposition_packet_for_xi, CrDepositionPacket,
};
use rei_microphysics::{AxisymCoupledState, AxisymmetricPoint, IsotopeNumberState, IsotopeSpecies};

const KB: f64 = 1.380_649e-23;

fn state(p: &CrDepositionPacket<'_>) -> AxisymCoupledState {
    let g = p.gas;
    let mut n = [0.; 13];
    n[IsotopeSpecies::H1Neutral as usize] = g.n_h_m3 * (1. - g.xi);
    n[IsotopeSpecies::H1Ionized as usize] = g.n_h_m3 * g.xi;
    n[IsotopeSpecies::He4Neutral as usize] = g.n_he_m3 * (1. - g.xi);
    n[IsotopeSpecies::He4SinglyIonized as usize] = g.n_he_m3 * g.xi;
    let isotopes = IsotopeNumberState::new(n).unwrap();
    let particles = isotopes.thermal_particle_density_all_thermal_m3().unwrap();
    AxisymCoupledState {
        isotopes,
        thermal_energy_j_m3: 1.5 * KB * particles * g.temperature_k,
        photon_number_m3: 0.,
        photon_energy_j_m3: 0.,
        photon_delta_pressure_j_m3: 0.,
    }
}

fn geometry() -> AxisymmetricPoint {
    pinned_cr_deposition_geometry().unwrap()
}

fn close(a: f64, b: f64) {
    let scale = a.abs().max(b.abs());
    assert!((a - b).abs() <= 2e-13 * scale, "{a:e} != {b:e}");
}

#[test]
fn pinned_source_drives_actual_closed_local_derivative() {
    let p = pinned_cr_deposition_packet().unwrap();
    let gas = state(&p);
    let result =
        cr_deposition_derivative(true, p.gas.time_s, geometry(), &gas, KB, || Ok(p)).unwrap();
    let d = result.derivative;
    let a = result.audit.unwrap();
    let [h, he0, he1] = a.ionization_rate_m3_s;
    close(
        d.sources.species_m3_s[IsotopeSpecies::H1Neutral as usize],
        -h,
    );
    close(
        d.sources.species_m3_s[IsotopeSpecies::H1Ionized as usize],
        h,
    );
    close(
        d.sources.species_m3_s[IsotopeSpecies::He4Neutral as usize],
        -he0,
    );
    close(
        d.sources.species_m3_s[IsotopeSpecies::He4SinglyIonized as usize],
        he0 - he1,
    );
    close(
        d.sources.species_m3_s[IsotopeSpecies::He4DoublyIonized as usize],
        he1,
    );
    close(d.sources.electron_m3_s, h + he0 + he1);
    let hubble = geometry().mean_hubble_per_s;
    let ne = gas
        .isotopes
        .moments()
        .unwrap()
        .neutral_free_electron_density_m3;
    close(d.electron_m3_s, -3. * hubble * ne + h + he0 + he1);
    let np = gas
        .isotopes
        .thermal_particle_density_all_thermal_m3()
        .unwrap();
    let expected_dt =
        2. * p.heat_power_j_m3_s / (3. * KB * np) - p.gas.temperature_k * (h + he0 + he1) / np;
    close(
        d.temperature_k_s,
        -2. * hubble * p.gas.temperature_k + expected_dt,
    );
    close(d.sources.internal_power_j_m3_s, p.ionization_power_j_m3_s);
    close(
        d.sources.external_power_j_m3_s,
        p.modelled_ionization_loss_power_j_m3_s,
    );
    close(
        d.sources.escape_power_j_m3_s,
        p.excitation_escape_power_j_m3_s + p.continuum_escape_power_j_m3_s,
    );
    assert_eq!(d.sources.photon_number_m3_s, 0.);
    assert_eq!(d.sources.photon_power_j_m3_s, 0.);
    assert_eq!(a.table_raw_residual_j_m3_s, p.table_raw_residual_j_m3_s);
    assert_eq!(a.heat_correction_j_m3_s, p.heat_correction_j_m3_s);
    assert_eq!(a.full_injection_power_j_m3_s, p.full_injection_power_j_m3_s);
    // Full proton injection is not substituted for modelled ionization loss.
    assert_ne!(
        a.full_injection_power_j_m3_s,
        d.sources.external_power_j_m3_s
    );
}

#[test]
fn xi010_source_drives_actual_closed_local_derivative_without_interpolation() {
    let p = pinned_cr_deposition_packet_for_xi(0.1).unwrap();
    let gas = state(&p);
    let result =
        cr_deposition_derivative(true, p.gas.time_s, geometry(), &gas, KB, || Ok(p)).unwrap();
    let d = result.derivative;
    let a = result.audit.unwrap();
    assert_eq!(p.provider_id, "CRP_L17_MD14_RUDD_FS10_XI010_CONDITIONAL_V1");
    close(d.sources.internal_power_j_m3_s, p.ionization_power_j_m3_s);
    close(
        d.sources.external_power_j_m3_s,
        p.modelled_ionization_loss_power_j_m3_s,
    );
    close(
        d.sources.escape_power_j_m3_s,
        p.excitation_escape_power_j_m3_s + p.continuum_escape_power_j_m3_s,
    );
    assert_eq!(d.sources.photon_number_m3_s, 0.);
    assert_eq!(a.table_raw_residual_j_m3_s, p.table_raw_residual_j_m3_s);
    assert!(pinned_cr_deposition_packet_for_xi(0.05).is_err());
}

#[test]
fn geometry_mismatch_cannot_reuse_source_pinned_packet() {
    let p = pinned_cr_deposition_packet().unwrap();
    let gas = state(&p);
    for bad in [
        AxisymmetricPoint::new(1., 0., 0., 0.).unwrap(),
        AxisymmetricPoint {
            mean_hubble_per_s: geometry().mean_hubble_per_s * 1.01,
            ..geometry()
        },
        AxisymmetricPoint {
            shear_per_s: -geometry().shear_per_s,
            ..geometry()
        },
        AxisymmetricPoint {
            mean_scale_factor: 1.,
            ..geometry()
        },
        AxisymmetricPoint {
            anisotropy: 0.,
            ..geometry()
        },
    ] {
        assert_eq!(
            cr_deposition_derivative(true, p.gas.time_s, bad, &gas, KB, || Ok(p))
                .unwrap_err()
                .code(),
            "CR_DEPOSITION_GEOMETRY_BINDING"
        );
    }
}

#[test]
fn off_calls_provider_zero_times_and_preserves_geometry_only() {
    let p = pinned_cr_deposition_packet().unwrap();
    let gas = state(&p);
    let h = 2e-17;
    let geom = AxisymmetricPoint::new(1., 0., h, 1e-18).unwrap();
    let result = cr_deposition_derivative(false, p.gas.time_s, geom, &gas, KB, || {
        panic!("OFF must not evaluate any provider, packet or table")
    })
    .unwrap();
    assert!(result.audit.is_none());
    assert_eq!(result.derivative.sources.species_m3_s, [0.; 13]);
    close(
        result.derivative.thermal_energy_j_m3_s,
        -5. * h * gas.thermal_energy_j_m3,
    );
    close(
        result.derivative.temperature_k_s,
        -2. * h * p.gas.temperature_k,
    );
}

#[test]
fn identity_and_ledger_consistent_numeric_tampering_are_rejected() {
    let p = pinned_cr_deposition_packet().unwrap();
    let gas = state(&p);
    let mut bad = p;
    bad.provider_id = "manufactured_same_numbers";
    let err =
        cr_deposition_derivative(true, p.gas.time_s, geometry(), &gas, KB, || Ok(bad)).unwrap_err();
    assert_eq!(err.code(), "CR_DEPOSITION_SOURCE_PIN_MISMATCH");
    bad = p;
    bad.full_injection_power_j_m3_s *= 1.01;
    let err =
        cr_deposition_derivative(true, p.gas.time_s, geometry(), &gas, KB, || Ok(bad)).unwrap_err();
    assert_eq!(err.code(), "CR_DEPOSITION_SOURCE_PIN_MISMATCH");
}

#[test]
fn cold_temperature_and_composition_are_bound_not_extrapolated() {
    let p = pinned_cr_deposition_packet().unwrap();
    let mut gas = state(&p);
    gas.thermal_energy_j_m3 *= 1.01;
    assert_eq!(
        cr_deposition_derivative(true, p.gas.time_s, geometry(), &gas, KB, || Ok(p))
            .unwrap_err()
            .code(),
        "CR_DEPOSITION_STATE_BINDING"
    );
    let good = state(&p);
    let mut n = std::array::from_fn(|i| good.isotopes.density_m3(IsotopeSpecies::ALL[i]));
    let shift = p.gas.n_he_m3 * 1e-5;
    n[IsotopeSpecies::He4Neutral as usize] -= shift;
    n[IsotopeSpecies::He4DoublyIonized as usize] += shift;
    gas = good;
    gas.isotopes = IsotopeNumberState::new(n).unwrap();
    assert_eq!(
        cr_deposition_derivative(true, p.gas.time_s, geometry(), &gas, KB, || Ok(p))
            .unwrap_err()
            .code(),
        "CR_DEPOSITION_STATE_BINDING"
    );
    assert_eq!(
        cr_deposition_derivative(true, p.gas.time_s + 1., geometry(), &good, KB, || Ok(p))
            .unwrap_err()
            .code(),
        "CR_DEPOSITION_STATE_BINDING"
    );
}

#[test]
fn provider_thresholds_and_raw_table_defect_cannot_be_discarded() {
    let p = pinned_cr_deposition_packet().unwrap();
    let gas = state(&p);
    let mut bad = p;
    bad.primary_threshold_j[0] *= 1.01;
    assert_eq!(
        cr_deposition_derivative(true, p.gas.time_s, geometry(), &gas, KB, || Ok(bad))
            .unwrap_err()
            .code(),
        "CR_DEPOSITION_IONIZATION_POWER"
    );
    bad = p;
    bad.table_raw_residual_j_m3_s += p.modelled_ionization_loss_power_j_m3_s * 1e-3;
    assert_eq!(
        cr_deposition_derivative(true, p.gas.time_s, geometry(), &gas, KB, || Ok(bad))
            .unwrap_err()
            .code(),
        "CR_DEPOSITION_TABLE_CORRECTION"
    );
    bad = p;
    bad.table_correction_bound_j_m3_s = 0.;
    assert_eq!(
        cr_deposition_derivative(true, p.gas.time_s, geometry(), &gas, KB, || Ok(bad))
            .unwrap_err()
            .code(),
        "CR_DEPOSITION_TABLE_CORRECTION"
    );
}

#[test]
fn invalid_values_and_unavailable_photon_closures_fail_closed() {
    let p = pinned_cr_deposition_packet().unwrap();
    let gas = state(&p);
    let mut bad = p;
    bad.heat_power_j_m3_s = f64::NAN;
    assert_eq!(
        cr_deposition_derivative(true, p.gas.time_s, geometry(), &gas, KB, || Ok(bad))
            .unwrap_err()
            .code(),
        "CR_DEPOSITION_DOMAIN"
    );
    bad = p;
    bad.closure = "explicit_transport_without_spectrum";
    assert_eq!(
        cr_deposition_derivative(true, p.gas.time_s, geometry(), &gas, KB, || Ok(bad))
            .unwrap_err()
            .code(),
        "CR_DEPOSITION_CLOSURE"
    );
}
