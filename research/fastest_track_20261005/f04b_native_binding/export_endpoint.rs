//! Observation wrapper: one discarded/full BE point, no adaptive acceptance.
#![allow(dead_code)]
#[derive(Debug)] pub enum ForwardError { InvalidInput(&'static str) }
mod hhe_events; mod thermal; mod microstep;
pub use hhe_events::*;
use microstep::*;
fn emit(name: &str, values: &[f64]) {
    for (i, value) in values.iter().enumerate() {
        println!("{name},{i},{:016x},{value:.17e}", value.to_bits());
    }
}
fn state(name: &str, s: &HHeState) {
    emit(name, &[s.fractions[0],s.fractions[1],s.fractions[2],s.u_erg_cm3,
        s.photon_cm3[0],s.photon_cm3[1],s.photon_cm3[2],s.escaped_erg_cm3]);
}
fn main() {
    let m = HHeModel::controlled_fixture();
    let old = HHeState::controlled_fixture(&m);
    let control = StepControl::default();
    emit("MODEL", &[m.n_h_cm3,m.n_he_cm3,m.c_cm_s,m.kb_erg_k,m.ev_erg]);
    emit("CHI", &m.threshold_ev); emit("ENERGY", &m.photon_energy_ev);
    emit("ALPHA", &m.alpha_cm3_s); emit("BETA", &m.beta_cm3_s);
    for a in 0..3 { emit(&format!("SIGMA{a}"), &m.sigma_cm2[a]); }
    state("OLD", &old);
    let dt = 1e8;
    emit("DT", &[dt]); emit("CONTROL", &[control.residual_tolerance]);
    println!("MAX_ITERATIONS,{}", control.max_iterations);
    let step = implicit_hhe_step(&m, &old, dt, control).expect("single BE observation");
    state("ENDPOINT", &step.state);
    emit("DIAGNOSTIC", &[step.residual_norm,step.local_error]);
    println!("ITERATIONS,{}", step.iterations);
    for a in 0..3 { emit(&format!("PHOTO{a}"), &step.events.photo_per_cm3[a]); }
    emit("COLLISION", &step.events.collision_per_cm3);
    emit("RECOMBINATION", &step.events.recombination_per_cm3);
    let rhs = hhe_rhs(&m, &step.state).expect("endpoint RHS observation");
    emit("RHS", &rhs.derivative); emit("ESCAPE_RHS", &[rhs.escaped_energy_rate]);
}
