//! Evolving-epoch C21 point bridge to the unmodified native H/He RHS.
//! Proper densities and T_CMB belong to the requested FLRW scale factor.
//! Geometry owns adiabatic work, hence the native RHS receives h=0.
use rei_microphysics::{
    axbi_driver::{Driver, DriverConfig},
    igm_state::{w_ev_per_h_to_erg, IgmGasState},
    igm_thermal::{igm_point_rhs, IgmPhotoInput},
};
use std::{env, path::Path};

fn run() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<String> = env::args().collect();
    if args.len() != 14 {
        return Err("usage: c21_epoch_rhs CONFIG CHECKPOINT A_EVAL xHII xHeII xHeIII W_EV_PER_H gammaHI gammaHeI gammaHeII heatHI heatHeI heatHeII".into());
    }
    let cfg = DriverConfig::read(&std::fs::read_to_string(&args[1])?)?;
    if cfg.q_ref != 0.0 || cfg.same_h {
        return Err("C21_EPOCH_BRIDGE_FLRW_ONLY".into());
    }
    let (driver, _) = Driver::new(cfg)?;
    let checkpoint = driver.read_checkpoint(Path::new(&args[2]))?;
    let number = |i: usize| -> Result<f64, Box<dyn std::error::Error>> {
        let v = args[i].parse::<f64>()?;
        if !v.is_finite() {
            return Err("C21_EPOCH_BRIDGE_NONFINITE".into());
        }
        Ok(v)
    };
    let a_eval = number(3)?;
    if a_eval < checkpoint.a {
        return Err("C21_EPOCH_BRIDGE_PRECHECKPOINT".into());
    }
    // The original owner decides the background domain and clock convention.
    let epoch = driver.background.point_at_scale(a_eval)?;
    if epoch.s_per_s != 0.0 {
        return Err("C21_EPOCH_BRIDGE_NONFLRW_BACKGROUND".into());
    }
    let gas = IgmGasState::new(
        [number(4)?, number(5)?, number(6)?],
        w_ev_per_h_to_erg(number(7)?)?,
    )?;
    let mut photo = IgmPhotoInput::default();
    for i in 0..3 {
        photo.gamma_s[i] = number(8 + i)?;
        photo.heat_erg_per_absorber_s[i] = number(11 + i)?;
    }
    let nh = driver.n_h0_cm3 / a_eval.powi(3);
    let nhe = driver.n_he0_cm3 / a_eval.powi(3);
    let tcmb = 2.7255 / a_eval;
    let eos = gas.eos(nh, nhe)?;
    let rhs = igm_point_rhs(&gas, nh, nhe, 0.0, tcmb, photo)?;
    println!("C21_NATIVE_RHS_EPOCH_V1");
    println!("EVAL_A\t{:.17e}", a_eval);
    println!("NH_CM3\t{:.17e}", nh);
    println!("NHE_CM3\t{:.17e}", nhe);
    println!("TCMB_K\t{:.17e}", tcmb);
    println!("FRACTION_DT\t{:.17e}\t{:.17e}\t{:.17e}", rhs.fraction_dt[0], rhs.fraction_dt[1], rhs.fraction_dt[2]);
    println!("W_DT_EV_PER_H_S\t{:.17e}", rhs.w_dt_erg_per_h_s / 1.602176634e-12);
    println!("TEMP_K\t{:.17e}", eos.temperature_k);
    println!("PHOTO_EVENTS\t{:.17e}\t{:.17e}\t{:.17e}", rhs.photo_events_cm3_s[0], rhs.photo_events_cm3_s[1], rhs.photo_events_cm3_s[2]);
    println!("THERMAL_MICRO\t{:.17e}", rhs.thermal_micro_erg_cm3_s);
    println!("BINDING_MICRO\t{:.17e}", rhs.binding_micro_erg_cm3_s);
    println!("ESCAPE\t{:.17e}", rhs.escape_erg_cm3_s);
    println!("CMB_TO_GAS\t{:.17e}", rhs.cmb_to_gas_erg_cm3_s);
    println!("PHOTO_INPUT\t{:.17e}", rhs.photo_input_erg_cm3_s);
    println!("CI_EVENTS\t{:.17e}\t{:.17e}\t{:.17e}", rhs.ci_events_cm3_s[0], rhs.ci_events_cm3_s[1], rhs.ci_events_cm3_s[2]);
    println!("RR_EVENTS\t{:.17e}\t{:.17e}\t{:.17e}", rhs.rr_events_cm3_s[0], rhs.rr_events_cm3_s[1], rhs.rr_events_cm3_s[2]);
    println!("DR_EVENTS\t{:.17e}", rhs.dr_events_cm3_s);
    Ok(())
}

fn main() {
    if let Err(err) = run() {
        eprintln!("C21_EPOCH_RHS_ERROR {err}");
        std::process::exit(2);
    }
}
