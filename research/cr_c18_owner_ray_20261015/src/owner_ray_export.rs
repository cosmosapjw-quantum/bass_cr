//! C18 read-only Rust-owned AXBI checkpoint and exact source grid exporter.
//! Link from owner rei_microphysics, not C18 reimplementations.
use rei_microphysics::{axbi_driver::{Driver,DriverConfig},Absorber,AtomicProvider,CharacteristicRay};
use std::{env,fs::File,io::{BufWriter,Write},path::Path};
fn run()->Result<(),Box<dyn std::error::Error>>{
 let args:Vec<String>=env::args().collect();
 if args.len()!=4{return Err("usage: owner_ray_export CFG CHECKPOINT OUTPUT_TSV".into());}
 let config=DriverConfig::read(&std::fs::read_to_string(&args[1])?)?;
 let (driver,_)=Driver::new(config)?;
 let state=driver.read_checkpoint(Path::new(&args[2]))?;
 let (number,energy)=driver.photon_inventory(&state);
 let (nr,er)=driver.residuals(&state)?;
 let nh=driver.n_h0_cm3/state.a.powi(3);let nhe=driver.n_he0_cm3/state.a.powi(3);
 let eos=state.gas.eos(nh,nhe)?;
 let gref=driver.background.point_at_scale(1./21.)?.geometry()?;
 let g=driver.background.point_at_scale(state.a)?.geometry()?;
 let mut out=BufWriter::new(File::create(&args[3])?);
 writeln!(out,"C18_RUST_AUTHORIZED_AXBI_RAY_STOCK_V1")?;
 writeln!(out,"META\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{}\t{}",
  driver.config.q_ref,state.a,driver.background.point_at_scale(state.a)?.time_s,
  driver.background.point_at_scale(state.a)?.b,nh,nhe,
  state.gas.fractions[0],state.gas.fractions[1],state.gas.fractions[2],eos.temperature_k,
  number,energy,nr,er,driver.energies.len(),driver.source.angular_cells.len())?;
 writeln!(out,"LEDGER\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}",state.ledgers.source_n,state.ledgers.absorbed_n,state.ledgers.boundary_n,state.ledgers.source_u,state.ledgers.boundary_u)?;
 let atomic=AtomicProvider::reference();
 for (i,&e) in driver.energies.iter().enumerate(){
  let x=[atomic.cross_section(Absorber::HI,e)?,atomic.cross_section(Absorber::HeI,e)?,atomic.cross_section(Absorber::HeII,e)?];
  writeln!(out,"ENERGY\t{}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}",i,e,x[0],x[1],x[2])?;
 }
 let mut rays=Vec::new();
 for (k,cell) in driver.source.angular_cells.iter().enumerate(){
  let init=CharacteristicRay::new(1.,[(1.-cell.mu*cell.mu).sqrt(),0.,cell.mu],0.)?;
  let curr=init.pullback(&gref,&g)?;
  let j=init.solid_angle_jacobian(&gref,&g)?;
  rays.push((k,cell.mu,cell.count_fraction,j,curr.direction[2],curr.energy_ev));
 }
 let norm:f64=rays.iter().map(|x|x.2*x.3).sum();
 for (k,mu,w,j,mu_curr,ratio) in rays{
  writeln!(out,"RAY\t{}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}",k,mu,w,j,mu_curr,ratio,w*j/norm)?;
 }
 // Exact source deposition using owner's public AxbiSource and Driver::deposit.
 // Same source/R*J weights and two-neighbor nodal assignment as Driver::inject.
 let emitted_rate=driver.source.at_redshift(1./state.a-1.)?.per_h_s;
 let mut emission=vec![0.0;state.photons.len()];
 let mut source_boundary=0.0;
 for (k,cell) in driver.source.angular_cells.iter().enumerate(){
  let init=CharacteristicRay::new(1.,[(1.-cell.mu*cell.mu).sqrt(),0.,cell.mu],0.)?;
  let jac=init.solid_angle_jacobian(&gref,&g)?;
  let angular=cell.count_fraction*jac/norm;
  for spectral in &driver.source.spectral_cells{
   let count_rate=emitted_rate*angular*spectral.photon_fraction;
   let (bn,_) =driver.deposit(&mut emission,k,spectral.energy_ev,count_rate)?;
   source_boundary+=bn;
  }
 }
 let rate_sum:f64=emission.iter().sum();
 if (rate_sum+source_boundary-emitted_rate).abs()>1e-11*emitted_rate.abs().max(1e-30){
  return Err("owner emission node budget failed".into());
 }
 writeln!(out,"EMISSION_META\t{:.17e}\t{:.17e}\t{:.17e}",emitted_rate,rate_sum,source_boundary)?;
 for k in 0..driver.source.angular_cells.len(){
  for (i,n) in state.photons[k*driver.energies.len()..(k+1)*driver.energies.len()].iter().enumerate(){
    let idx=k*driver.energies.len()+i;
    writeln!(out,"STOCK\t{}\t{}\t{:.17e}\t{:.17e}",k,i,n,emission[idx])?;
  }
 }
 out.flush()?;
 println!("C18_RUST_READ_OK q={:.5} a={:.17e} photons={} rays={} N={:.17e} U_eV_per_H={:.17e} N_res={:.17e} E_res={:.17e}",
  driver.config.q_ref,state.a,state.photons.len(),driver.source.angular_cells.len(),number,energy,nr,er);
 Ok(())
}
fn main(){if let Err(e)=run(){eprintln!("C18_RUST_FAIL: {e}");std::process::exit(2);}}
