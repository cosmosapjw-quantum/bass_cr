"""Owner source/Verner/Bianchi-I geometry, frozen-gas ray-channel ODE benchmark.

A mathematically specified independent *manufactured local ray channel*.
Gas FRACTIONS frozen, proper density n_H(a)~a^-3. Spectrum has five fixed
birth-energy channels anchored at a0, with E(a)=E(a0)*Bianchi redshift.
The owner emission law populates these channels at every epoch, which
is a channel-input convention, NOT the canonical age-resolved SOURCE07
frequency/ray allocation (there photons birth at their true epochs).

Independent Radau integrates continuous source and variable opacity
in d ln a. Compare C15 midpoint-born, endpoint-weighted approximate
and C16 positive optical quadrature. No H/He gas back-reaction
and no claim about production EoR history or angular R*J.
"""
from __future__ import annotations
import argparse,json,time
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

from owner_age_bridge import owner_namespace,verner_sigma_array
from transport import photon_energy_ratio
from continuous_source import proper_dt
from endpoint_quadrature import endpoint_weighted,optical_quadrature


def experiment(ns,q:float,nsteps=(8,16,32,64,128,256),a0=.1,a1=.11,threshold_aware=False):
    m=ns["model"]
    energies=np.array([14.,20.,32.,70.,90.])
    mus=np.array([-1.,-.5,0.,.5,1.])
    weights=np.array([float(ns["spec"].phi(float(E))) for E in energies])
    weights/=weights.sum()
    y=ns["nhe"]/(m.nh*125.)
    composition=np.array([.9,y*.85,y*.15])
    fit=ns["fit"]

    def coefficients(a):
        H=m.hubble(float(a),float(q))
        E=energies*photon_energy_ratio(m,np.full(len(energies),a0),
                                float(a),float(q),mus)
        proper=m.nh/a**3
        rates=29979245800.*proper*composition[None,:]*np.column_stack(
                    [verner_sigma_array(E,p) for p in fit])
        source=m.rate(float(a))*weights
        return H,source,rates,E

    # Threshold-crossing epochs are physical nonsmooth events. A single
    # linear opacity interpolant must not straddle an HI/HeI/HeII cutoff.
    event_times=[]
    for emit,mu in zip(energies,mus):
        def energy_at(a):
            return emit*photon_energy_ratio(m,np.array([a0]),a,
                                            q,np.array([mu]))[0]
        for cut in (13.60,24.59,54.42):
            f0=energy_at(a0)-cut
            f1=energy_at(a1)-cut
            if f0*f1<0.:
                root=brentq(lambda aa:energy_at(aa)-cut,a0,a1,
                            xtol=1e-15)
                event_times.append(np.log(root))
    event_times=sorted(set(event_times))

    def rhs(ln_a,N):
        a=np.exp(ln_a)
        h,s,r,_=coefficients(a)
        return (s-r.sum(axis=1)*N)/h

    def jac(ln_a,N):
        a=np.exp(ln_a)
        h,_,r,_=coefficients(a)
        return np.diag(-r.sum(axis=1)/h)

    t0=time.perf_counter()
    result=solve_ivp(rhs,(np.log(a0),np.log(a1)),np.zeros(len(energies)),
        method="Radau",jac=jac,rtol=3e-11,atol=1e-15)
    if not result.success:raise RuntimeError(result.message)
    ref=result.y[:,-1]
    reference_time=time.perf_counter()-t0
    print('RAD_REF',q,ref.tolist(),'nfev',result.nfev,
          'seconds',reference_time,flush=True)

    curves=[]
    for n in nsteps:
        uniform=np.linspace(np.log(a0),np.log(a1),n+1)
        xgrid=np.unique(np.r_[uniform,event_times]) if threshold_aware else uniform
        numbers={key:np.zeros(len(energies))
                 for key in ("C15_midpoint","C16_endpoint_weighted","C16_optical_quad")}
        ledger={k:0. for k in numbers}
        start=time.perf_counter()
        for j in range(len(xgrid)-1):
            al,ar=np.exp(xgrid[j]),np.exp(xgrid[j+1])
            amid=np.sqrt(al*ar)
            dt=proper_dt(m,float(al),float(ar),q)
            # Evaluate one-sided opacity at a threshold boundary.
            # Verner sigma(E<th)=0 and sigma(E=th)>0: the jump must
            # never be interpolated across the entire cell.
            small=min(1e-11,(xgrid[j+1]-xgrid[j])*1e-6)
            aleft_inside=np.exp(xgrid[j]+small) if any(
                abs(xgrid[j]-event)<2e-13 for event in event_times) else al
            aright_inside=np.exp(xgrid[j+1]-small) if any(
                abs(xgrid[j+1]-event)<2e-13 for event in event_times) else ar
            _,Sl,_,_=coefficients(al)
            _,Sr,_,_=coefficients(ar)
            _,_,L0,_=coefficients(aleft_inside)
            _,_,L1,_=coefficients(aright_inside)
            _,Sm,Lmid,_=coefficients(amid)
            tau=dt*Lmid.sum(axis=1)
            old=numbers["C15_midpoint"]
            numbers["C15_midpoint"]=old*np.exp(-tau)+dt*Sm*np.exp(-tau/2)
            ledger["C15_midpoint"]+=float(dt*Sm.sum())
            for name,solver in (("C16_endpoint_weighted",endpoint_weighted),
                                ("C16_optical_quad",optical_quadrature)):
                old=numbers[name]
                new,events=solver(old,Sl,Sr,L0,L1,dt)
                born=.5*dt*(Sl+Sr)
                residual=old+born-new-events.sum(axis=1)
                if np.max(abs(residual))>1e-11:
                    raise ArithmeticError("C16 photon conservation")
                numbers[name]=new
                ledger[name]+=float(born.sum())
        run_secs=time.perf_counter()-start
        error={}
        for name,calc in numbers.items():
            error[name]={
               "photon_survivor_per_H":calc.tolist(),
               "max_relative_photon_error":float(np.max(
                       np.abs(calc-ref)/np.maximum(abs(ref),1e-17))),
               "max_absolute_photon_error":float(np.max(abs(calc-ref))),
               "emitted_photons_per_H":ledger[name],
            }
        curves.append({"nsteps":n,"actual_subintervals":len(xgrid)-1,
                       "threshold_event_count":len(event_times),
                       "methods":error,"combined_run_seconds":run_secs})
        print('N',q,n,{k:round(v["max_relative_photon_error"],9) for k,v in error.items()},flush=True)
    return {"q":q,"threshold_aware":threshold_aware,
            "detected_events_scale_factor":[float(np.exp(x)) for x in event_times],
            "method":"owner Scenario/Spectrum/Verner/Bianchi ratio; manufactured birth-frame ray channels",
            "zero_photon_initial":True,
            "photon_energy_eV_at_a0":energies.tolist(),
            "birth_mu":mus.tolist(),
            "gas_composition":"proper nH(a)*(.9, y*.85, y*.15); no gas evolution",
            "reference_Radau":ref.tolist(),
            "reference_nfev":result.nfev,
            "reference_wall_seconds":reference_time,
            "nsteps":list(nsteps),"curves":curves}


def run(root:Path):
    ns=owner_namespace(root)
    start=time.perf_counter()
    data=[experiment(ns,q,threshold_aware=flag)
          for q in (-.01,0.,.01) for flag in (False,True)]
    return {"schema":"C16_OWNER_BACKED_TIME_VARIABLE_OPACITY_NUMERIC_V1",
        "claim":"local manufactured fixed-ray channel; not actual SOURCE07 propagated age stocks",
        "results":data,"total_wall_seconds":time.perf_counter()-start,
        "admission":"OWNER_RAY_MAPPING_AND_FULL_IGM_PHYSICS_HOLD"}


if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--owner",type=Path,required=True)
    a.add_argument("--out",type=Path,required=True)
    opt=a.parse_args()
    out=run(opt.owner)
    opt.out.parent.mkdir(parents=True,exist_ok=True)
    opt.out.write_text(json.dumps(out,indent=2)+"\n")
    print("RUN_TOTAL",out["total_wall_seconds"])