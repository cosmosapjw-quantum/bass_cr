//! Persistent explicit-fixture bridge to UNMODIFIED native non-photo H/He RHS.
//! No checkpoint is read or reinterpreted. Photo and expansion inputs are zero.
//! IO uses only std; build against the immutable owner selected by build_native.sh.
use rei_microphysics::{
    igm_state::{w_ev_per_h_to_erg, IgmGasState},
    igm_thermal::{igm_point_rhs, IgmPhotoInput},
};
use std::io::{self, BufRead, Write};
const EV_ERG: f64 = 1.602176634e-12;
const OWNER: &str = "6ea2b1b4b3875c9163cafc45efe720afded43fc4";

fn prepared_point(fields: &[&str]) -> Result<String, String> {
    use rei_microphysics::axbi_driver::{Driver, DriverConfig};
    if fields.len() != 10 { return Err("PROTOCOL ABSORB a dt nh0 nhe0 x y z E N".into()); }
    let v: Vec<f64> = fields[1..].iter().map(|s| s.parse::<f64>())
        .collect::<Result<_,_>>().map_err(|_| "PROTOCOL float".to_string())?;
    if v.iter().any(|v| !v.is_finite()) {return Err("DOMAIN nonfinite".into());}
    let (a,dt,nh0,nhe0,x,y,z,energy,n0)=(v[0],v[1],v[2],v[3],v[4],v[5],v[6],v[7],v[8]);
    if !(a>=1.0/21.0 && a<=0.2 && dt>0.0 && nh0>0.0 && nhe0>=0.0 && n0>=0.0 && energy>0.0 && x>=0.0 && x<=1.0 && y>=0.0 && z>=0.0 && y+z<=1.0) {return Err("DOMAIN prepared fixture".into());}
    let mut cfg=DriverConfig::baseline();cfg.background_panels=64;cfg.transport_cells=32;
    let (d,_) = Driver::new(cfg).map_err(|e|format!("DOMAIN {e:?}"))?;
    let geom=d.background.point_at_scale(a).map_err(|e|format!("DOMAIN {e:?}"))?.geometry().map_err(|e|format!("DOMAIN {e:?}"))?;
    let mut state=d.transport.empty_state();
    d.transport.add_delta(&mut state,0,energy/( (1.0/21.0)/a ),n0).map_err(|e|format!("DOMAIN {e:?}"))?;
    let prepared=d.transport.prepare(&state,&geom).map_err(|e|format!("DOMAIN {e:?}"))?;
    let nh=nh0/a.powi(3);let nhe=nhe0/a.powi(3);
    let absorbers=[nh*(1.0-x),nhe*(1.0-y-z),nhe*y];
    let out=prepared.evaluate(absorbers,nh,dt).map_err(|e|format!("DOMAIN {e:?}"))?;
    let (n1,u1)=d.transport.inventory(&out.state,&geom).map_err(|e|format!("DOMAIN {e:?}"))?;
    let mut vals=vec![n1,u1];
    for i in 0..3 {vals.push(out.photo.gamma_s[i]*absorbers[i]/nh*dt);}
    for i in 0..3 {vals.push(out.photo.heat_erg_per_absorber_s[i]*absorbers[i]/nh*dt/EV_ERG);}
    Ok(format!("ABSORBED\t{}",vals.iter().map(|x|format!("{x:.17e}")).collect::<Vec<_>>().join("\t")))
}

fn export_source(args: &[String]) -> Result<(),String> {
    use rei_microphysics::axbi_driver::{Driver,DriverConfig};
    if args.len()!=5 {return Err("usage: --export-source a0 dln_a source_subdivisions".into());}
    let a0=args[2].parse::<f64>().map_err(|e|e.to_string())?;
    let dx=args[3].parse::<f64>().map_err(|e|e.to_string())?;
    let sub=args[4].parse::<usize>().map_err(|e|e.to_string())?;
    if !(a0>=1.0/21.0 && dx>0.0 && dx<=0.1 && a0*dx.exp()<=0.2 && sub>=1 && sub<=64) {return Err("source export domain".into());}
    let mut c=DriverConfig::baseline();c.energy_subdivisions=sub;c.n_mu=8;c.background_panels=64;c.transport_cells=32;
    let (d,_)=Driver::new(c).map_err(|e|format!("{e:?}"))?;
    println!("C21E_SOURCE_V1\t{OWNER}");
    println!("DENSITY\t{:.17e}\t{:.17e}",d.n_h0_cm3,d.n_he0_cm3);
    for u in [-1.0_f64/3.0_f64.sqrt(),1.0_f64/3.0_f64.sqrt()] {
        let x=a0.ln()+0.5*dx*(1.0+u);let a=x.exp();
        let h=d.background.point_at_scale(a).map_err(|e|format!("{e:?}"))?.h_per_s;
        let j=d.source.at_redshift(1.0/a-1.0).map_err(|e|format!("{e:?}"))?.per_h_s;
        println!("BIRTH\t{x:.17e}\t{h:.17e}\t{j:.17e}");
    }
    for c in &d.source.spectral_cells {
        println!("CELL\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}",c.lower_ev,c.upper_ev,c.energy_ev,c.photon_fraction);
    }
    Ok(())
}

fn evaluate(line: &str) -> Result<String, String> {
    let fields: Vec<&str> = line.split_whitespace().collect();
    if fields.first()==Some(&"ABSORB") {return prepared_point(&fields);}
    if fields.len() != 8 || fields[0] != "EVAL" {
        return Err("PROTOCOL expected EVAL a nH0 nHe0 xHII xHeII xHeIII w_eV_H".into());
    }
    let mut v = [0.0_f64; 7];
    for i in 0..7 {
        v[i] = fields[i + 1].parse::<f64>().map_err(|_| "PROTOCOL invalid float".to_string())?;
        if !v[i].is_finite() { return Err("DOMAIN nonfinite input".into()); }
    }
    let [a, nh0, nhe0, x, y, z, w] = v;
    if !(a > 0.0 && a <= 1.0 && nh0 > 0.0 && nhe0 >= 0.0) {
        return Err("DOMAIN explicit epoch/density".into());
    }
    if nhe0 == 0.0 && (y != 0.0 || z != 0.0) {
        return Err("DOMAIN absent helium requires zero fractions".into());
    }
    let nh = nh0 / a.powi(3);
    let nhe = nhe0 / a.powi(3);
    let state = IgmGasState::new([x, y, z], w_ev_per_h_to_erg(w).map_err(|e| format!("DOMAIN {e:?}"))?)
        .map_err(|e| format!("DOMAIN {e:?}"))?;
    let eos = state.eos(nh, nhe).map_err(|e| format!("DOMAIN {e:?}"))?;
    let r = igm_point_rhs(&state, nh, nhe, 0.0, 2.7255 / a, IgmPhotoInput::default())
        .map_err(|e| format!("DOMAIN {e:?}"))?;
    let mut out = vec![a, nh, nhe, eos.temperature_k];
    out.extend(r.fraction_dt);
    out.extend([
        r.w_dt_erg_per_h_s / EV_ERG,
        r.binding_micro_erg_cm3_s / nh / EV_ERG,
        r.escape_erg_cm3_s / nh / EV_ERG,
        r.cmb_to_gas_erg_cm3_s / nh / EV_ERG,
    ]);
    out.extend(r.ci_events_cm3_s.map(|e| e / nh));
    out.extend(r.rr_events_cm3_s.map(|e| e / nh));
    out.push(r.dr_events_cm3_s / nh);
    out.extend(r.photo_events_cm3_s.map(|e| e / nh));
    out.push(r.photo_input_erg_cm3_s / nh / EV_ERG);
    out.push(r.expansion_work_erg_cm3_s / nh / EV_ERG);
    if out.iter().any(|x| !x.is_finite()) {return Err("DOMAIN nonfinite output".into());}
    Ok(format!("OK\t{}", out.iter().map(|x| format!("{x:.17e}")).collect::<Vec<_>>().join("\t")))
}

fn run() -> io::Result<()> {
    let built_owner = option_env!("C21E_OWNER_SHA").unwrap_or("UNPINNED");
    if built_owner != OWNER {
        return Err(io::Error::new(io::ErrorKind::InvalidData, "OWNER_ID_NOT_EMBEDDED"));
    }
    let mut output = io::BufWriter::new(io::stdout().lock());
    writeln!(output, "C21E_NONPHOTO_V1\t{OWNER}")?;
    output.flush()?;
    for line in io::stdin().lock().lines() {
        let line = line?;
        if line.trim() == "QUIT" { break; }
        let reply = match evaluate(&line) {
            Ok(value) => value,
            Err(e) => format!("ERR\t{}", e.replace('\n', " ").replace('\t', " ")),
        };
        writeln!(output, "{reply}")?;
        output.flush()?;
    }
    Ok(())
}
fn main() {
    let args:Vec<String>=std::env::args().collect();
    if args.get(1).map(String::as_str)==Some("--export-source") {
        if option_env!("C21E_OWNER_SHA")!=Some(OWNER) {eprintln!("OWNER_ID_NOT_EMBEDDED");std::process::exit(2);}
        if let Err(e)=export_source(&args) {eprintln!("C21E_SOURCE_ERROR {e}");std::process::exit(2);}
        return;
    }
    if args.len()!=1 {eprintln!("C21E_UNKNOWN_ARGUMENT");std::process::exit(2);}
    if let Err(e) = run() { eprintln!("C21E_BRIDGE_ERROR {e}"); std::process::exit(2); }
}

#[cfg(test)]
mod tests {
    use super::*;
    fn fixture() -> String {
        let y_he = 0.2454 / (4.0 * (1.0 - 0.2454));
        let w = 1.5 * 1.380649e-16 / EV_ERG * 8500.0 * (1.0 + y_he + 0.2 + y_he * (0.15 + 2.0 * 0.01));
        format!("EVAL .09 1.8981984507140266e-7 {} .2 .15 .01 {w:.17e}",1.8981984507140266e-7*y_he)
    }
    #[test]
    fn explicit_fixture_no_checkpoint_and_zero_photos() {
        let s = evaluate(&fixture()).unwrap();
        let v: Vec<f64> = s.split_whitespace().skip(1).map(|s| s.parse().unwrap()).collect();
        assert_eq!(v.len(), 23);
        assert!(v[3] > 8499.999 && v[3] < 8500.001);
        assert!(v[18..].iter().all(|v| *v == 0.0));
    }
    #[test]
    fn nonphoto_energy_identity() {
        let s = evaluate(&fixture()).unwrap();
        let v: Vec<f64> = s.split_whitespace().skip(1).map(|s| s.parse().unwrap()).collect();
        let residual = v[7] + v[8] + v[9] - v[10];
        let scale = v[7].abs()+v[8].abs()+v[9].abs()+v[10].abs();
        assert!(residual.abs() <= 1e-12*scale+1e-30);
    }
    #[test]
    fn invalid_requests_rejected() {
        assert!(evaluate("bad").is_err());
        assert!(evaluate("EVAL NaN 1e-7 0 0 0 0 1").is_err());
        assert!(evaluate("EVAL .09 1e-7 0 .2 .15 .01 1").is_err());
    }
}
