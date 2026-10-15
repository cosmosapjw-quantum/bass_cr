"""C19 isolated source-aware H/He coupled local step on genuine AXBI rays.

A backward-Euler gas point step with exact frozen-*endpoint*-opacity photon
exponential (constant in-step ray source and node energies). Photoevent/heat
rates are *integrated* photon losses divided by dt before passing them to
the original Rust igm_point_rhs. Source is deposited once; geometry h=0.
This is not a physical full EoR time history, Case-B/OTS solver or a
certified integrator over an evolving cosmological ray trajectory.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import subprocess
import sys
import numpy as np
from exponential_source import absorb_with_source
from owner_adapter import NativeState,read_native_export,C_CM_S,EV_ERG,BIND_EV

KB_ERG_K=1.380649e-16

def valid_gas(g:np.ndarray)->bool:
    x,y,z,w=map(float,g)
    return bool(np.isfinite(g).all() and 0<=x<=1 and y>=0 and z>=0
                and y+z<=1 and w>0)

def initial_gas(owner:NativeState)->np.ndarray:
    he=owner.nHe/owner.nH
    ne_per_h=owner.xHII+he*(owner.xHeII+2*owner.xHeIII)
    particles_per_h=1+he+ne_per_h
    w=1.5*KB_ERG_K*owner.Tg*particles_per_h/EV_ERG
    g=np.array([owner.xHII,owner.xHeII,owner.xHeIII,w],dtype=float)
    if not valid_gas(g):raise ValueError("bad original gas")
    return g

def binding_ev_per_h(g:np.ndarray,he_ratio:float)->float:
    # H II, He II (1st binding), He III (both ionization energies).
    return float(BIND_EV[0]*g[0]+he_ratio*(BIND_EV[1]*(g[1]+g[2])+BIND_EV[2]*g[2]))

def photon_step(owner:NativeState,g:np.ndarray,n0:np.ndarray,dt:float)->dict:
    if not valid_gas(g) or not (np.isfinite(dt) and dt>0):
        raise ValueError("invalid local state or proper duration")
    n0=np.asarray(n0,dtype=float)
    if n0.shape!=owner.stocks.ravel().shape or not np.isfinite(n0).all() or (n0<0).any():
        raise ValueError("invalid native packet shape/count")
    he=owner.nHe/owner.nH
    frac=np.array([1-g[0],he*(1-g[1]-g[2]),he*g[1]])
    if (frac<0).any():raise ValueError("invalid absorber fractions")
    energy=np.tile(owner.energies,len(owner.rays))
    cross=np.tile(owner.sigma,(len(owner.rays),1))
    rates=C_CM_S*owner.nH*cross*frac[None,:]
    source=owner.source.ravel()
    n1,events,_=absorb_with_source(n0,source,rates,dt)
    total=np.sum(events,axis=0)
    heat=np.sum(events*(energy[:,None]-BIND_EV[None,:]),axis=0)
    if (heat<-1e-24).any():raise ValueError("negative physical photoheat")
    gamma=np.divide(total,dt*frac,out=np.zeros(3),where=frac>0)
    power=np.divide(heat*EV_ERG,dt*frac,out=np.zeros(3),where=frac>0)
    if np.any((frac==0)&(total>1e-24)):raise AssertionError("absent absorber events")
    return {"n1":n1,"events":events,"species":total,"heat":heat,
            "gamma":gamma,"power":power,"energy":energy,"source":source}

@dataclass(frozen=True)
class NativePoint:
    fraction_dt:np.ndarray
    w_dt_ev_s:float
    temperature:float
    photo_events_cm3_s:np.ndarray
    thermal_micro:float
    binding_micro:float
    escape:float
    cmb:float
    photo_input:float
    ci:np.ndarray
    rr:np.ndarray
    dr:float

class RustOwnerPoint:
    """Launch a separately compiled, immutable-owner Rust microphysics bridge."""
    def __init__(self,binary:Path,config:Path,checkpoint:Path):
        self.binary=Path(binary);self.config=Path(config);self.checkpoint=Path(checkpoint)
        if not all(x.is_file() for x in (self.binary,self.config,self.checkpoint)):
            raise FileNotFoundError("C19 Rust binary and exact owner config/checkpoint are mandatory")
        self.calls=0

    def __call__(self,g:np.ndarray,gamma:np.ndarray,power:np.ndarray)->NativePoint:
        if not valid_gas(g):raise ValueError("inadmissible gas input")
        args=[str(self.binary),str(self.config),str(self.checkpoint)]
        args += [format(float(v),".17e") for v in list(g)+list(gamma)+list(power)]
        run=subprocess.run(args,text=True,capture_output=True,check=False,timeout=30)
        self.calls+=1
        if run.returncode!=0:
            raise ValueError("Owner Rust RHS refused the physical state: "+run.stderr.strip()[:350])
        lines=run.stdout.splitlines()
        if not lines or lines[0]!="C19_NATIVE_RHS_V1":
            raise RuntimeError("unrecognized owner Rust RHS output")
        rows={a[0]:np.array(list(map(float,a[1:]))) for line in lines[1:] if (a:=line.split("\t"))}
        one=lambda key:float(rows[key][0])
        return NativePoint(rows["FRACTION_DT"],one("W_DT_EV_PER_H_S"),one("TEMP_K"),
          rows["PHOTO_EVENTS"],one("THERMAL_MICRO"),one("BINDING_MICRO"),
          one("ESCAPE"),one("CMB_TO_GAS"),one("PHOTO_INPUT"),
          rows["CI_EVENTS"],rows["RR_EVENTS"],one("DR_EVENTS"))

def evaluation(owner:NativeState,rust:RustOwnerPoint,g0:np.ndarray,
               n0:np.ndarray,g:np.ndarray,dt:float):
    phot=photon_step(owner,g,n0,dt)
    native=rust(g,phot["gamma"],phot["power"])
    rhs=np.r_[native.fraction_dt,native.w_dt_ev_s]
    residue=g-g0-dt*rhs
    if not np.isfinite(residue).all():raise FloatingPointError("nonfinite residual")
    # A distinct native-rate/eV ledger: photon/H rates map to cm^-3 s^-1.
    np.testing.assert_allclose(native.photo_events_cm3_s,owner.nH*phot["species"]/dt,
        rtol=3e-13,atol=1e-33)
    np.testing.assert_allclose(native.photo_input,
        owner.nH*np.sum(phot["heat"]+phot["species"]*BIND_EV)*EV_ERG/dt,
        rtol=3e-13,atol=1e-40)
    return residue,phot,native

def step(owner:NativeState,rust:RustOwnerPoint,dt:float,
         g0:np.ndarray|None=None,n0:np.ndarray|None=None,
         tol:float=8e-13,maxiter:int=12)->dict:
    if g0 is None:g0=initial_gas(owner)
    else:g0=np.array(g0,dtype=float,copy=True)
    if n0 is None:n0=owner.stocks.ravel().copy()
    else:n0=np.array(n0,dtype=float,copy=True)
    if not valid_gas(g0):raise ValueError("invalid starting chemistry state")
    scale=np.array([1.,1.,1.,max(g0[3],1e-5)])
    g=g0.copy()
    history=[]
    for k in range(maxiter+1):
        residue,p,native=evaluation(owner,rust,g0,n0,g,dt)
        err=float(np.max(np.abs(residue)/scale))
        history.append(err)
        if err<tol:break
        if k==maxiter:raise RuntimeError("C19_GAS_NEWTON_HOLD_ITERATION_CAP")
        jac=np.empty((4,4))
        for j in range(4):
            # use forward difference unless physical face reached
            h=1e-6*max(abs(g[j]),1e-4) if j<3 else 2e-6*max(g[j],1e-4)
            gg=g.copy();gg[j]+=h
            if not valid_gas(gg):
                h=-h
                gg[j]=g[j]+h
            rr,_,_=evaluation(owner,rust,g0,n0,gg,dt)
            jac[:,j]=(rr-residue)/h
        try:delta=np.linalg.solve(jac,-residue)
        except np.linalg.LinAlgError as e:raise RuntimeError("C19_SINGULAR_JACOBIAN") from e
        accepted=False
        for ls in range(26):
            trial=g+(2.**(-ls))*delta
            if not valid_gas(trial):continue
            try: rtrial,_,_=evaluation(owner,rust,g0,n0,trial,dt)
            except (ValueError,FloatingPointError):continue
            err_trial=float(np.max(np.abs(rtrial)/scale))
            if err_trial<err:
                g=trial
                accepted=True
                break
        if not accepted:raise RuntimeError("C19_LINESEARCH_HOLD")
    photon0=float(n0.sum());photon1=float(p["n1"].sum())
    emitted=float(dt*p["source"].sum())
    events=float(p["species"].sum())
    mass_res=photon0+emitted-photon1-events
    energy_before=float(np.dot(n0,p["energy"]))
    energy_after=float(np.dot(p["n1"],p["energy"]))
    energy_emitted=float(dt*np.dot(p["source"],p["energy"]))
    photon_energy_res=(energy_before+energy_emitted-energy_after-
                      float(np.sum(p["heat"]+p["species"]*BIND_EV)))
    he_ratio=owner.nHe/owner.nH
    delta_bind=binding_ev_per_h(g,he_ratio)-binding_ev_per_h(g0,he_ratio)
    delta_thermal=float(g[3]-g0[3])
    escaped=dt*native.escape/(owner.nH*EV_ERG)
    cmb=dt*native.cmb/(owner.nH*EV_ERG)
    # Photon+gas+ionization binding+escape-CMB-emission ledger, zero in Case A.
    global_energy_res=(energy_after-energy_before-energy_emitted+
                       delta_thermal+delta_bind+escaped-cmb)
    rate_identity=(native.thermal_micro+native.binding_micro+native.escape
                   -native.cmb-native.photo_input)
    return {
      "initial_gas":g0.tolist(),"new_gas":g.tolist(),
      "initial_temperature_K":owner.Tg,"new_temperature_K":native.temperature,
      "new_stocks":p["n1"],"event_counts_per_H":p["species"].tolist(),
      "heat_eV_per_H":p["heat"].tolist(),"gamma_s":p["gamma"].tolist(),
      "photon_number_residual":mass_res,
      "photon_energy_residual_eV_per_H":photon_energy_res,
      "total_energy_residual_eV_per_H":global_energy_res,
      "native_thermal_binding_identity_erg_cm3_s":rate_identity,
      "native_escaped_eV_per_H":escaped,"native_CMB_to_gas_eV_per_H":cmb,
      "max_scaled_implicit_residual":history[-1],
      "newton_error_history":history,"owner_rhs_calls":rust.calls,
      "status":"C19_SCOPED_REAL_AXBI_SINGLE_EPOCH_CASE_A_MICROPHYSICS",
    }

def summarize(d:dict)->dict:
    o={k:v for k,v in d.items() if k!="new_stocks"}
    return o

if __name__=="__main__":
    import argparse
    a=argparse.ArgumentParser()
    a.add_argument("--zero",type=Path,required=True)
    a.add_argument("--plus",type=Path,required=True)
    a.add_argument("--native",type=Path,required=True)
    a.add_argument("--owner-root",type=Path,required=True)
    a.add_argument("--out",type=Path,required=True)
    a.add_argument("--dt",type=float,default=1e10)
    args=a.parse_args()
    cases={
      "ZERO":("research/axbi_goal_20261014/runs/flrw/32d11e733155/ZERO",args.zero),
      "SHEAR_PLUS":("research/axbi_goal_20261014/report/full_progress_32d11e733155/snapshot_20261014T083357015083Z/SHEAR_PLUS",args.plus)}
    results={}
    for name,(rel,fname) in cases.items():
        base=args.owner_root/rel
        rust=RustOwnerPoint(args.native,base/"config.cfg",base/"checkpoint.txt")
        original=read_native_export(fname)
        full=step(original,rust,args.dt)
        half1=step(original,rust,args.dt/2)
        half2=step(original,rust,args.dt/2,np.array(half1["new_gas"]),half1["new_stocks"])
        results[name]={
          "full":summarize(full),"half2_gas":half2["new_gas"],
          "single_minus_twohalf":(np.array(full["new_gas"])-np.array(half2["new_gas"])).tolist(),
          "single_minus_twohalf_stocks_L1":float(np.sum(np.abs(full["new_stocks"]-half2["new_stocks"]))),
          "max_half_conservation":float(max(abs(half1["total_energy_residual_eV_per_H"]),abs(half2["total_energy_residual_eV_per_H"]))),
          "total_rhs_calls":rust.calls}
    args.out.parent.mkdir(exist_ok=True,parents=True)
    args.out.write_text(json.dumps({"schema":"C19_SOURCE_AWARE_AXBI_COUPLED_CASE_A_V1",
      "owner_checkpoint_epochs":"DIFFERENT; no same-time anisotropy comparison",
      "scope":"single epoch fixed nH/nHe, a, E, sigma and source; true native Rust H/He/CMB thermal RHS, geometry h0; no OTS",
      "proper_dt_s":args.dt,"cases":results},indent=2)+"\n")
    for name,v in results.items():
        print(name,"gas",v["full"]["new_gas"],"ledger",v["full"]["total_energy_residual_eV_per_H"],
              "rhs_calls",v["total_rhs_calls"],flush=True)
