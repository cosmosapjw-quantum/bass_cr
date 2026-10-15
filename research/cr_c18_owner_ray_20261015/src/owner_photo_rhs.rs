//! Read owner AXBI checkpoint and call ORIGINAL igm_thermal::igm_point_rhs.
 //! No source files are mutated. Converts C18 species photo input per absorber
 //! into native Rust proper heating, collisional, recombination and gas RHS.
use rei_microphysics::{
 axbi_driver::{Driver,DriverConfig},
 igm_thermal::{igm_point_rhs,IgmPhotoInput}
};
use std::{env,path::Path};
fn run()->Result<(),Box<dyn std::error::Error>>{
 let args:Vec<String>=env::args().collect();
 if args.len()!=9{
  return Err("usage: owner_photo_rhs CONFIG CHECKPOINT GAMMA_HI GAMMA_HEI GAMMA_HEII HEAT_HI_ERG HEAT_HEI_ERG HEAT_HEII_ERG".into());
 }
 let c=DriverConfig::read(&std::fs::read_to_string(&args[1])?)?;
 let (d,_)=Driver::new(c)?;
 let s=d.read_checkpoint(Path::new(&args[2]))?;
 let mut photo=IgmPhotoInput::default();
 for i in 0..3{
  photo.gamma_s[i]=args[3+i].parse::<f64>()?;
  photo.heat_erg_per_absorber_s[i]=args[6+i].parse::<f64>()?;
 }
 let nH=d.n_h0_cm3/s.a.powi(3);
 let nHe=d.n_he0_cm3/s.a.powi(3);
 let rhs=igm_point_rhs(&s.gas,nH,nHe,0.0,2.7255/s.a,photo)?;
 println!("C18_OWNER_POINT_RHS_V1");
 println!("GAMMA\t{:.17e}\t{:.17e}\t{:.17e}",
  photo.gamma_s[0],photo.gamma_s[1],photo.gamma_s[2]);
 println!("PHOTO_EVENT_RATE_CM3_S\t{:.17e}\t{:.17e}\t{:.17e}",
  rhs.photo_events_cm3_s[0],rhs.photo_events_cm3_s[1],rhs.photo_events_cm3_s[2]);
 println!("PHOTO_INPUT_ERG_CM3_S\t{:.17e}",rhs.photo_input_erg_cm3_s);
 println!("FRACTION_DT_S\t{:.17e}\t{:.17e}\t{:.17e}",
  rhs.fraction_dt[0],rhs.fraction_dt[1],rhs.fraction_dt[2]);
 println!("THERMAL_POWER_ERG_PER_H_S\t{:.17e}",rhs.w_dt_erg_per_h_s);
 println!("RR_EVENTS_CM3_S\t{:.17e}\t{:.17e}\t{:.17e}",
  rhs.rr_events_cm3_s[0],rhs.rr_events_cm3_s[1],rhs.rr_events_cm3_s[2]);
 println!("CI_EVENTS_CM3_S\t{:.17e}\t{:.17e}\t{:.17e}",
  rhs.ci_events_cm3_s[0],rhs.ci_events_cm3_s[1],rhs.ci_events_cm3_s[2]);
 println!("DR_EVENTS_CM3_S\t{:.17e}",rhs.dr_events_cm3_s);
 println!("ESCAPE_ERG_CM3_S\t{:.17e}",rhs.escape_erg_cm3_s);
 println!("THERMAL_MICRO_ERG_CM3_S\t{:.17e}",rhs.thermal_micro_erg_cm3_s);
 println!("BINDING_MICRO_ERG_CM3_S\t{:.17e}",rhs.binding_micro_erg_cm3_s);
 Ok(())
}
fn main(){if let Err(e)=run(){eprintln!("C18_OWNER_RHS_FAIL {e}");std::process::exit(2)}}
