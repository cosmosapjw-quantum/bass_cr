"""Measured optimization: vectorized Duhamel source/sink and sparse no-source lane."""
from __future__ import annotations
import argparse
import importlib.util
import json
import math
import time
from pathlib import Path
import numpy as np

from owner_age_bridge import owner_namespace,verner_sigma_array
from physical_age import Gas
from transport import integrate
from exponential_source import absorb_with_source,phi_neg


def old_module(source:Path):
    sp=importlib.util.spec_from_file_location("c13_previous_transport",source)
    module=importlib.util.module_from_spec(sp)
    sp.loader.exec_module(module)
    return module


def scalar_exact(photons,source,rates,dt):
    end=np.empty_like(photons)
    counts=np.zeros_like(rates)
    for k in range(len(photons)):
        tau=dt*float(np.sum(rates[k]))
        P=1.-math.exp(-tau)
        ph=-math.expm1(-tau)/tau if tau>0 else 1.
        new=photons[k]*math.exp(-tau)+source[k]*dt*ph
        lost=photons[k]+source[k]*dt-new
        end[k]=new
        if tau>0:
            counts[k]=rates[k]/sum(rates[k])*lost
    return end,counts


def benchmark(owner:Path,source_c13:Path,nrep=5):
    ns=owner_namespace(owner)
    E=np.tile(np.linspace(13.61,100.,512),8)
    gas=np.array([ns["model"].nh/.105**3*.9,
                 ns["nhe"]/125/.105**3*.85,
                 ns["nhe"]/125/.105**3*.15])
    rates=29979245800*np.column_stack(
       [verner_sigma_array(E,p) for p in ns["fit"]])*gas[None,:]
    n=len(E);dt=8e12
    source=np.full(n,1e-19)
    initial=np.full(n,1e-6)
    old=scalar_exact(initial,source,rates,dt)
    new=absorb_with_source(initial,source,rates,dt)
    np.testing.assert_allclose(old[0],new[0],rtol=1e-13,atol=1e-15)
    np.testing.assert_allclose(old[1],new[1],rtol=1e-12,atol=1e-14)
    trials=[]
    for _ in range(nrep):
        t=time.perf_counter();scalar_exact(initial,source,rates,dt)
        ts=time.perf_counter()-t
        t=time.perf_counter();absorb_with_source(initial,source,rates,dt)
        tv=time.perf_counter()-t
        trials.append({'scalar_s':ts,'vector_s':tv})
    original=old_module(source_c13)
    original_out=original.integrate(ns,0.,128,source_scale=0,recombination=True)
    now_out=integrate(ns,0.,128,source_scale=0,recombination=True,rr_ne_method="frozen")
    for k in original_out['gas_final']:
        np.testing.assert_allclose(original_out['gas_final'][k],
            now_out['gas_final'][k],atol=1e-12,rtol=2e-13)
    no_src=[]
    for _ in range(3):
        t=time.perf_counter();original.integrate(ns,0.,128,source_scale=0,recombination=True)
        old_s=time.perf_counter()-t
        t=time.perf_counter();integrate(ns,0.,128,source_scale=0,recombination=True,rr_ne_method='frozen')
        new_s=time.perf_counter()-t
        no_src.append({'old_s':old_s,'new_s':new_s})
    scalar=float(np.median([i['scalar_s'] for i in trials]))
    vector=float(np.median([i['vector_s'] for i in trials]))
    old_s=float(np.median([i['old_s'] for i in no_src]))
    new_s=float(np.median([i['new_s'] for i in no_src]))
    return {
      "schema":"BASS_CR_C14_OPTIMIZATION_BENCH_V1",
      "source":"real owner Verner H/He three species; representative E 13.61..100eV; 8x512 energies",
      "vectorized_source_sink":{"npayload":n,"samples":trials,"scalar_median_s":scalar,
          "vector_median_s":vector,"ratio":scalar/vector,
          "accuracy":"same photon/source/rates/time; element parity <=1e-12 rtol"},
      "sparse_zero_source":{"source_scale":0,"nsteps":128,"samples":no_src,
          "old_median_s":old_s,"new_median_s":new_s,"ratio":old_s/new_s,
          "accuracy":"same xHI,xHeI,xHeII,xHeIII,T, scoped 1e-12 abs"},
      "rr_midpoint_cost":"Reported separately in source/no-source subproblem; no full Bianchi production speedup claim"
    }


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--owner",type=Path,required=True)
    p.add_argument("--base",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    result=benchmark(args.owner,args.base)
    args.out.parent.mkdir(exist_ok=True,parents=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({"vector_ratio":result['vectorized_source_sink']['ratio'],
                      "no_source_ratio":result['sparse_zero_source']['ratio']},indent=2))
