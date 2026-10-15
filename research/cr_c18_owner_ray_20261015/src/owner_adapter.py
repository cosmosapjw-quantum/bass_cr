"""Rust-validated AXBI ray/node photon stock -> C17 H/He local chemistry.

Owner Rust Driver.read_checkpoint and native source deposition/geometry
author all photon stocks, energy nodes, angular weights and cross-sections.
Local rate evaluation uses frozen gas and energy for an explicit proper
duration; this is not full AXBI gas/thermal history integration.
"""
from __future__ import annotations
from pathlib import Path
import json
from dataclasses import dataclass
import numpy as np
from species_events import species_resolved_affine,affine_photoheat
from exponential_source import absorb_with_source

C_CM_S=29979245800.
EV_ERG=1.602176634e-12
BIND_EV=np.array([13.598434599702,24.587389011,54.41776])

@dataclass
class NativeState:
    q:float
    a:float
    t_s:float
    b:float
    nH:float
    nHe:float
    xHII:float
    xHeII:float
    xHeIII:float
    Tg:float
    rust_N:float
    rust_U:float
    rust_NR:float
    rust_UR:float
    energies:np.ndarray
    sigma:np.ndarray
    rays:np.ndarray
    stocks:np.ndarray
    source:np.ndarray
    emission_rate:float
    ledger:np.ndarray

    @property
    def absorbers_per_H(self):
        return np.array([
            1-self.xHII,
            self.nHe/self.nH*(1-self.xHeII-self.xHeIII),
            self.nHe/self.nH*self.xHeII
        ])

    @property
    def absorbers_proper_cm3(self):
        return self.nH*self.absorbers_per_H

def read_native_export(path:Path)->NativeState:
    lines=path.read_text().splitlines()
    if lines[0]!="C18_RUST_AUTHORIZED_AXBI_RAY_STOCK_V1":
        raise ValueError("native AXBI Rust signature mismatch")
    table={}
    for line in lines[1:]:
        fields=line.split("\t")
        table.setdefault(fields[0],[]).append(fields[1:])
    meta=table["META"][0]
    if len(meta)!=16:raise ValueError("owner metadata has wrong shape")
    floats=list(map(float,meta[:14]))
    ne,nr=map(int,meta[14:])
    if ne!=49 or nr!=8:raise ValueError("nonbaseline energy/angular shape")
    E=np.empty(ne);cross=np.empty((ne,3))
    for record in table["ENERGY"]:
        i=int(record[0]);E[i]=float(record[1]);cross[i]=list(map(float,record[2:]))
    rays=np.empty((nr,6))
    for record in table["RAY"]:
        rays[int(record[0])]=list(map(float,record[1:]))
    stocks=np.zeros((nr,ne));source=np.zeros_like(stocks)
    for record in table["STOCK"]:
        k,i=map(int,record[:2])
        stocks[k,i]=float(record[2]);source[k,i]=float(record[3])
    if any(len(table[k])!=n for k,n in (("ENERGY",ne),("RAY",nr),("STOCK",nr*ne))):
        raise ValueError("missing owner ray/spectrum rows")
    rate=float(table["EMISSION_META"][0][0])
    state=NativeState(*floats,E,cross,rays,stocks,source,rate,
                      np.array(list(map(float,table["LEDGER"][0]))))
    if not np.all(np.isfinite(E)) or np.any(np.diff(E)<=0):
        raise AssertionError("energy support invalid")
    if any(np.any(x<0) for x in (cross,stocks,source)):
        raise AssertionError("native photon/source/cross section positivity")
    np.testing.assert_allclose(stocks.sum(),state.rust_N,rtol=1e-12,atol=1e-17)
    np.testing.assert_allclose(np.sum(stocks*E),state.rust_U,rtol=1e-12,atol=1e-17)
    np.testing.assert_allclose(source.sum(),rate,rtol=1e-12,atol=1e-30)
    np.testing.assert_allclose(state.rays[:,5].sum(),1.,rtol=0,atol=2e-14)
    if np.any(state.absorbers_per_H<0):
        raise AssertionError("negative native absorber fraction")
    return state

def local_photo_step(owner:NativeState,dt:float=1e10,outer=64,inner=48):
    if not (dt>0 and np.isfinite(dt)):raise ValueError("positive proper dt needed")
    N0=owner.stocks.ravel().copy()
    s=owner.source.ravel().copy()
    E=np.tile(owner.energies,len(owner.rays))
    sigma=np.tile(owner.sigma,(len(owner.rays),1))
    lam=C_CM_S*owner.absorbers_proper_cm3[None,:]*sigma
    N,ev,raw,time_mom=species_resolved_affine(
         N0,s,s,lam,lam,dt,outer_nodes=outer,inner_nodes=inner,
         with_time_moments=True)
    oracle,exact_ev,_=absorb_with_source(N0,s,lam,dt)
    np.testing.assert_allclose(N,oracle,rtol=2e-11,atol=2e-15)
    np.testing.assert_allclose(ev,exact_ev,rtol=2e-9,atol=1e-16)
    e=ev.sum(axis=0)
    Q=affine_photoheat(ev,time_mom,E,E,BIND_EV).sum(axis=0)
    B=e*BIND_EV
    emitted=float(dt*s.sum())
    nres=float(N0.sum()+emitted-N.sum()-e.sum())
    eres=float(np.dot(N0,E)+dt*np.dot(s,E)-np.dot(N,E)-sum(Q+B))
    abundance=owner.absorbers_per_H
    gam=np.zeros(3);h=np.zeros(3)
    np.divide(e,dt*abundance,out=gam,where=abundance>0)
    np.divide(Q*EV_ERG,dt*abundance,out=h,where=abundance>0)
    if np.any((abundance==0)&((e>0)|(Q>0))):
        raise AssertionError("absent species cannot photoionize")
    return {
       "scope":"owner Rust checkpoint actual photon stock; fixed gas/energy and source over local proper dt",
       "q":owner.q,"a":owner.a,"t_s":owner.t_s,"proper_dt_s":dt,
       "gas":{"xHII":owner.xHII,"xHeII":owner.xHeII,"xHeIII":owner.xHeIII,
              "Tg_K":owner.Tg,"nH_cm3":owner.nH,"nHe_cm3":owner.nHe},
       "native_49_energies_x_8_rays":int(owner.stocks.size),
       "native_photons_per_H":owner.rust_N,
       "native_energy_eV_per_H":owner.rust_U,
       "native_photon_number_residual":owner.rust_NR,
       "native_augmented_energy_residual_eV_per_H":owner.rust_UR,
       "native_source_photon_rate_per_H_s":owner.emission_rate,
       "newborn_photons_per_H":emitted,
       "species_photoevents_per_H":e.tolist(),
       "species_heat_eV_per_H":Q.tolist(),
       "species_binding_eV_per_H":B.tolist(),
       "last_photons_per_H":float(N.sum()),
       "photo_gamma_per_absorber_s":gam.tolist(),
       "photo_heat_erg_per_absorber_s":h.tolist(),
       "photon_number_residual":nres,
       "local_photon_energy_residual_eV_per_H":eres,
       "raw_quadrature_moment_diagnostics":raw,
       "native_RJ_angular_fraction_sum":float(owner.rays[:,5].sum()),
       "scientific_gate":"SCOPED_NATIVE_CHECKPOINT_PHOTO_INPUT__FULL_EOR_HOLD"
    }

if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("--zero",type=Path,required=True)
    parser.add_argument("--plus",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--dt",type=float,default=1e10)
    args=parser.parse_args()
    results={label:local_photo_step(read_native_export(fn),args.dt)
             for label,fn in (("ZERO",args.zero),("SHEAR_PLUS",args.plus))}
    args.out.parent.mkdir(exist_ok=True,parents=True)
    args.out.write_text(json.dumps({"schema":"C18_RUST_AXBI_NATIVE_HHE_INPUT_V1",
       "note":"different checkpoint epochs, not controlled same-time anisotropy comparison",
       "cases":results},indent=2)+"\n")
    for key,d in results.items():
        print(key,"photoevents",d["species_photoevents_per_H"],
           "heat_eV",d["species_heat_eV_per_H"],
           "mass_res",d["photon_number_residual"],
           "energy_res",d["local_photon_energy_residual_eV_per_H"])
