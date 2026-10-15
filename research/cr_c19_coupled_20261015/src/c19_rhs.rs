//! C19: immutable original Rust IGM microphysics as a dynamic point evaluator.
//! No reinterpretation of h: owner AXBI chemistry evaluates h=0;
//! geometry and adiabatic work are separate. Args are numbers, not files.
//! All rates and state validation come from the owner crate.
use rei_microphysics::{
    axbi_driver::{Driver, DriverConfig},
    igm_state::{IgmGasState,w_ev_per_h_to_erg},
    igm_thermal::{igm_point_rhs,IgmPhotoInput}
};
use std::{env,path::Path};

fn run()->Result<(),Box<dyn std::error::Error>> {
    let a:Vec<String>=env::args().collect();
    if a.len()!=13 {
        return Err("usage: c19_rhs CONFIG CHECKPOINT xHII xHeII xHeIII W_EV_PER_H gammaHI gammaHeI gammaHeII heatHI heatHeI heatHeII".into());
    }
    let c=DriverConfig::read(&std::fs::read_to_string(&a[1])?)?;
    let (d,_)=Driver::new(c)?;
    let s=d.read_checkpoint(Path::new(&a[2]))?;
    let num=|i:usize|->Result<f64,Box<dyn std::error::Error>>{
        let x=a[i].parse::<f64>()?;
        if !x.is_finite(){return Err("nonfinite input".into());}
        Ok(x)
    };
    let g=IgmGasState::new([num(3)?,num(4)?,num(5)?], w_ev_per_h_to_erg(num(6)?)?)?;
    let mut photo=IgmPhotoInput::default();
    for i in 0..3 {
        photo.gamma_s[i]=num(7+i)?;
        photo.heat_erg_per_absorber_s[i]=num(10+i)?;
    }
    let nh=d.n_h0_cm3/s.a.powi(3);
    let nhe=d.n_he0_cm3/s.a.powi(3);
    let eos=g.eos(nh,nhe)?;
    let r=igm_point_rhs(&g,nh,nhe,0.0,2.7255/s.a,photo)?;
    println!("C19_NATIVE_RHS_V1");
    println!("FRACTION_DT\t{:.17e}\t{:.17e}\t{:.17e}",r.fraction_dt[0],r.fraction_dt[1],r.fraction_dt[2]);
    println!("W_DT_EV_PER_H_S\t{:.17e}",r.w_dt_erg_per_h_s/1.602176634e-12);
    println!("TEMP_K\t{:.17e}",eos.temperature_k);
    println!("PHOTO_EVENTS\t{:.17e}\t{:.17e}\t{:.17e}",r.photo_events_cm3_s[0],r.photo_events_cm3_s[1],r.photo_events_cm3_s[2]);
    println!("THERMAL_MICRO\t{:.17e}",r.thermal_micro_erg_cm3_s);
    println!("BINDING_MICRO\t{:.17e}",r.binding_micro_erg_cm3_s);
    println!("ESCAPE\t{:.17e}",r.escape_erg_cm3_s);
    println!("CMB_TO_GAS\t{:.17e}",r.cmb_to_gas_erg_cm3_s);
    println!("PHOTO_INPUT\t{:.17e}",r.photo_input_erg_cm3_s);
    println!("CI_EVENTS\t{:.17e}\t{:.17e}\t{:.17e}",r.ci_events_cm3_s[0],r.ci_events_cm3_s[1],r.ci_events_cm3_s[2]);
    println!("RR_EVENTS\t{:.17e}\t{:.17e}\t{:.17e}",r.rr_events_cm3_s[0],r.rr_events_cm3_s[1],r.rr_events_cm3_s[2]);
    println!("DR_EVENTS\t{:.17e}",r.dr_events_cm3_s);
    Ok(())
}
fn main(){if let Err(e)=run(){eprintln!("C19_RHS_ERROR {e}");std::process::exit(2)}}
