//! FLRW-only source-age-tagged scalar photon characteristic, original Rust inputs.
//! Each emission birth time defines a separate canonical q=a_birth E_em packet.
//! Frozen ion fractions (not coupled thermal evolution); proper n_i(a)=n_i0/a^3.
//! Positive competing-risk absorption uses original AtomicProvider Verner fit.
//! Mathematical clock GL4, positive GL2 birth quadrature, midpoint event energy.
//! This is a reference oracle, NOT production transport or Bianchi anisotropy.
use rei_microphysics::{
  axbi_driver::{Driver,DriverConfig}, axbi_background::Cosmology,
  AtomicProvider, Absorber, HHeModel
};
use std::{env,path::Path};
const X4:[f64;4]=[-0.8611363115940526,-0.3399810435848563,0.3399810435848563,0.8611363115940526];
const W4:[f64;4]=[0.34785484513745385,0.6521451548625461,0.6521451548625461,0.34785484513745385];
const U2:[f64;2]=[-0.5773502691896257,0.5773502691896257];
const C_CM_S:f64=29979245800.0;
#[derive(Clone,Copy)]
struct Packet{q:f64,n:f64}
#[derive(Default)]
struct Ledgers {
  emitted_n:f64, emitted_u:f64, absorb:[f64;3], heat:[f64;3],
  work:f64, threshold_crossings:[u64;3], positive_failures:u64,
  emitted_n_err:f64, emitted_u_err:f64, absorb_err:[f64;3],
  heat_err:[f64;3], work_err:f64
}
fn kahan(sum:&mut f64,err:&mut f64,value:f64){
  let y=value-*err;
  let next=*sum+y;
  *err=(next-*sum)-y;
  *sum=next;
}
fn clock_h(a:f64,c:&Cosmology)->Result<f64,Box<dyn std::error::Error>>{
  Ok(c.hubble_flrw(a)?)
}
fn proper_dt(x0:f64,x1:f64,c:&Cosmology)->Result<f64,Box<dyn std::error::Error>>{
  if x1<x0{return Err("reversed clock".into());}
  let mid=0.5*(x1+x0);let h=0.5*(x1-x0);
  let mut acc=0.;
  for k in 0..4{
    acc+=W4[k]/clock_h((mid+h*X4[k]).exp(),c)?;
  }
  Ok(h*acc)
}
fn absorb_one(p:&mut Packet,x0:f64,x1:f64,dt:f64,fr:[f64;3],nh0:f64,
          atomic:&AtomicProvider, bind:&[f64;3], do_abs:bool, l:&mut Ledgers)->Result<(),Box<dyn std::error::Error>>{
  if p.n==0. {return Ok(())}
  let mid=0.5*(x0+x1);
  let e_start=p.q/ x0.exp();
  let e_mid=p.q/ mid.exp();
  let e_end=p.q/ x1.exp();
  if !(e_start.is_finite()&&e_mid.is_finite()&&e_end.is_finite()&&e_end>0.){
    return Err("bad characteristic energy".into());
  }
  let mut lam=[0.;3];
  if do_abs{
    let dens=nh0*(-3.*mid).exp();
    for k in 0..3{
      let absorber=match k{0=>Absorber::HI,1=>Absorber::HeI,_=>Absorber::HeII};
      lam[k]=C_CM_S*dens*fr[k]*atomic.cross_section(absorber,e_mid)?;
      if lam[k]<0. || !lam[k].is_finite(){return Err("negative/nonfinite opacity".into())}
    }
  }
  let total:f64=lam.iter().sum();
  let loss=if total>0. { p.n*(-(-total*dt).exp_m1()) } else {0.};
  let remain=p.n-loss;

  for k in 0..3 {
    let aj=if total>0. {loss*lam[k]/total} else {0.};
    if aj <0. || (aj>0. && e_mid+1e-11<bind[k]) {l.positive_failures+=1;return Err("invalid photoheat threshold".into())}
    kahan(&mut l.absorb[k],&mut l.absorb_err[k],aj);
    kahan(&mut l.heat[k],&mut l.heat_err[k],aj*(e_mid-bind[k]));

  }
  // Redshift energy work includes energy of photons lost at the midpoint event.
  // This makes the discrete photon+binding+heat+work ledger algebraically exact.
  // Avoid subtracting nearly equal large photon energies.
  // Both terms are nonnegative in expansion and account for absorbed photons
  // and survivors at their respective physical characteristic energies.
  let positive_work=loss*(e_start-e_mid)+remain*(e_start-e_end);
  kahan(&mut l.work,&mut l.work_err,positive_work);
  p.n=remain;
  Ok(())
}
// Exact crossings of the owner's FIT cutoffs, not its binding energies.
// Split support at xcrit=log(q/E_fit), then integrate only smooth cells.
fn absorb(p:&mut Packet,x0:f64,x1:f64,dt:f64,fr:[f64;3],nh0:f64,
          atomic:&AtomicProvider,bind:&[f64;3],do_abs:bool,
          cosmology:&Cosmology,l:&mut Ledgers)->Result<(),Box<dyn std::error::Error>>{
  if p.n==0.{return Ok(());}
  let e0=p.q/x0.exp();
  let e1=p.q/x1.exp();
  let mut intervals=vec![x0];
  for (k,thr) in [13.60,24.59,54.42].iter().enumerate(){
    if e0>=*thr&&e1<*thr{l.threshold_crossings[k]+=1;}
    let xt=(p.q / *thr).ln();
    if xt>x0&&xt<x1 {intervals.push(xt);}
  }
  intervals.push(x1);
  intervals.sort_by(|a,b|a.total_cmp(b));
  for window in intervals.windows(2){
    let this_dt=if intervals.len()==2 {dt} else {proper_dt(window[0],window[1],cosmology)?};
    absorb_one(p,window[0],window[1],this_dt,fr,nh0,atomic,bind,do_abs,l)?;
  }
  Ok(())
}
fn run()->Result<(),Box<dyn std::error::Error>>{
  let args:Vec<String>=env::args().collect();
  if args.len()!=7{
    return Err("usage: c20_native CONFIG CHECKPOINT A_END NSTEPS SOURCE_ON(0/1) ABS_ON(0/1)".into())
  }
  let cfg=DriverConfig::read(&std::fs::read_to_string(&args[1])?)?;
  if cfg.q_ref!=0. || cfg.same_h {return Err("C20_IS_FLRW_ONLY q_ref=0 same_h=false".into())}
  let (driver,_)=Driver::new(cfg)?;
  let old=driver.read_checkpoint(Path::new(&args[2]))?;
  let end:f64=args[3].parse()?;
  let nstep:usize=args[4].parse()?;
  let source_on=match args[5].as_str(){"1"=>true,"0"=>false,_=>return Err("invalid source switch".into())};
  let abs_on=match args[6].as_str(){"1"=>true,"0"=>false,_=>return Err("invalid absorption switch".into())};
  if !(old.a.is_finite()&&end.is_finite()&&end>old.a&&end<=0.2&&nstep>0&&nstep<=16384){
    return Err("C20_SCALE_DOMAIN_OR_STEP_CAP".into())
  }
  let model=HHeModel::controlled_fixture();
  let bind=model.threshold_ev;
  let c=Cosmology{h0_per_s:67.4*1e5/3.0856775814913673e24,omega_m:0.315,omega_r:9.2e-5,omega_lambda:1.-0.315-9.2e-5};
  // Verify the current explicit original C19 owner background and independent
  // public Cosmology evaluate the same H, rather than trusting duplicated constants.
  for a in [old.a,0.5*(old.a+end),end]{
    let actual=driver.background.point_at_scale(a)?.h_per_s;
    let ctrl=c.hubble_flrw(a)?;
    if ((actual-ctrl)/actual).abs()>1e-14{return Err("ORIGINAL_CLOCK_MODEL_MISMATCH".into())}
  }
  let nh0=driver.n_h0_cm3;
  let y=driver.n_he0_cm3/nh0;
  let g=old.gas.fractions;
  let fr=[1.-g[0],y*(1.-g[1]-g[2]),y*g[1]];
  if fr.iter().any(|&f|f<0.||!f.is_finite()){return Err("invalid checkpoint absorber".into())}
  let atomic=AtomicProvider::reference();
  let mut photons=vec![0.;driver.energies.len()];
  for (j,&n) in old.photons.iter().enumerate(){ photons[j % driver.energies.len()]+=n; }
  let mut packs:Vec<Packet>=photons.iter().zip(driver.energies.iter())
                  .filter(|(n,_)|**n>0.)
                  .map(|(&n,&e)|Packet{q:old.a*e,n}).collect();
  let n0=old.photons.iter().sum::<f64>();
  let u0=old.photons.iter().enumerate().map(|(i,&n)|n*driver.energies[i%driver.energies.len()]).sum::<f64>();
  let mut l=Ledgers::default();
  let x0=old.a.ln();let dx=(end/old.a).ln()/(nstep as f64);
  let t0=std::time::Instant::now();
  let mut time_integral=0.;
  let source_fraction_sum:f64=driver.source.spectral_cells.iter().map(|c|c.photon_fraction).sum();
  let angular_sum:f64=driver.source.angular_cells.iter().map(|c|c.count_fraction).sum();
  if (source_fraction_sum-1.).abs()>2e-12 || (angular_sum-1.).abs()>2e-12{
    return Err("owner spectrum/angular source normalization".into())
  }
  // FLRW angular weights factor exactly: same characteristic E(a) for every ray.
  // Preserve original total counts; do not pretend this trick works for Bianchi.
  for k in 0..nstep{
    let left=x0+(k as f64)*dx;let right=x0+((k+1) as f64)*dx;
    let dt=proper_dt(left,right,&c)?;
    time_integral+=dt;
    for p in packs.iter_mut(){absorb(p,left,right,dt,fr,nh0,&atomic,&bind,abs_on,&c,&mut l)?;}
    // Genuine native MD14 source sampled at two positive Gauss birth ages.
    if source_on{
      for &u in U2.iter(){
        let xbirth=0.5*(left+right)+0.5*dx*u;
        let ab=xbirth.exp();
        let rate=driver.source.at_redshift(1./ab-1.)?.per_h_s;
        let births=0.5*dx*rate/clock_h(ab,&c)?;
        let dt_birth_to_end=proper_dt(xbirth,right,&c)?;
        for cell in &driver.source.spectral_cells{
          let n=births*cell.photon_fraction;
          let mut p=Packet{q:ab*cell.energy_ev,n};
          kahan(&mut l.emitted_n,&mut l.emitted_n_err,n);
          kahan(&mut l.emitted_u,&mut l.emitted_u_err,n*cell.energy_ev);
          absorb(&mut p,xbirth,right,dt_birth_to_end,fr,nh0,&atomic,&bind,abs_on,&c,&mut l)?;
          if p.n>0. {packs.push(p);}
        }
      }
    }
  }
  let (mut n1,mut n1_err,mut u1,mut u1_err)=(0.,0.,0.,0.);
  for p in &packs {
    kahan(&mut n1,&mut n1_err,p.n);
    kahan(&mut u1,&mut u1_err,p.n*p.q/end);
  }
  let atot=l.absorb.iter().sum::<f64>();
  let htot=l.heat.iter().sum::<f64>();
  let btot=(0..3).map(|k|l.absorb[k]*bind[k]).sum::<f64>();
  let numres=n0+l.emitted_n-n1-atot;
  let eres=u0+l.emitted_u-u1-htot-btot-l.work;
  let owner_dt=driver.background.point_at_scale(end)?.time_s-driver.background.point_at_scale(old.a)?.time_s;
  let elapsed=t0.elapsed().as_secs_f64();
  // no json dependencies: valid output with explicit scientific scope and identity
  println!("{{\"schema\":\"BASS_CR_C20_NATIVE_FLRW_VERER_COHORT_V1\",\"scope\":\"fixed original gas fractions; exact original AXBI Rust input; FLRW only; no chemistry/thermal evolution\",\"q_ref\":0,\"a0\":{:.17e},\"a1\":{:.17e},\"nsteps\":{},\"source_on\":{},\"absorption_on\":{},\"input_n\":{:.17e},\"input_u_ev_h\":{:.17e},\"source_n\":{:.17e},\"source_u_ev_h\":{:.17e},\"end_n\":{:.17e},\"end_u_ev_h\":{:.17e},\"species_events_per_h\":[{:.17e},{:.17e},{:.17e}],\"species_heat_ev_h\":[{:.17e},{:.17e},{:.17e}],\"photon_redshift_work_ev_h\":{:.17e},\"number_residual\":{:.17e},\"energy_residual_ev_h\":{:.17e},\"time_gl4_s\":{:.17e},\"time_owner_simpson_s\":{:.17e},\"threshold_crossing_packet_counts\":[{},{},{}],\"active_cohorts\":{},\"original_ray_count\":{},\"source_spectrum_cells\":{},\"native_cpu_wall_s\":{:.7}}}",
  old.a,end,nstep,source_on,abs_on,n0,u0,l.emitted_n,l.emitted_u,n1,u1,
  l.absorb[0],l.absorb[1],l.absorb[2],l.heat[0],l.heat[1],l.heat[2],
  l.work,numres,eres,time_integral,owner_dt,l.threshold_crossings[0],
  l.threshold_crossings[1],l.threshold_crossings[2],packs.len(),
  driver.source.angular_cells.len(),driver.source.spectral_cells.len(),elapsed);
  Ok(())
}
fn main(){if let Err(e)=run(){eprintln!("C20_NATIVE_ERROR {e}");std::process::exit(2)}}
