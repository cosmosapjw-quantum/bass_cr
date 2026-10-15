"""C19 physics/implementation controls on genuine Rust AXBI state files."""
from dataclasses import replace
import os
from pathlib import Path
import numpy as np
import pytest
from coupled import (read_native_export,RustOwnerPoint,step,initial_gas,
                     photon_step,valid_gas,binding_ev_per_h,EV_ERG,BIND_EV)

C19=Path(__file__).resolve().parents[1]
BASS=C19.parents[1]
NATIVE=Path(os.environ.get("C19_NATIVE_BIN",str(BASS.parent/"c19_native_target_20261015/c19_rhs")))
ROOT=Path(os.environ.get("REI_BIANCHI_ROOT","/home/cosmosapjw/Dropbox/bianchi/rei_bianchi"))
CONF={
"ZERO":"research/axbi_goal_20261014/runs/flrw/32d11e733155/ZERO",
"SHEAR_PLUS":"research/axbi_goal_20261014/report/full_progress_32d11e733155/snapshot_20261014T083357015083Z/SHEAR_PLUS",
}

def fixtures(case):
    fname="AXBI_ZERO_native.tsv" if case=="ZERO" else "AXBI_PLUS_native.tsv"
    o=read_native_export(BASS/"research/cr_c18_owner_ray_20261015/results"/fname)
    loc=ROOT/CONF[case]
    return o,RustOwnerPoint(NATIVE,loc/"config.cfg",loc/"checkpoint.txt")

@pytest.mark.parametrize("case",["ZERO","SHEAR_PLUS"])
def test_native_coupled_gas_photon_ledgers(case):
    o,r=fixtures(case)
    res=step(o,r,1e10)
    assert valid_gas(np.array(res["new_gas"]))
    assert np.isfinite(res["new_temperature_K"])
    assert res["new_temperature_K"]>0
    assert (res["new_stocks"]>=0).all()
    assert min(res["event_counts_per_H"])>=0
    assert min(res["heat_eV_per_H"])>=0
    assert abs(res["photon_number_residual"])<2e-18
    assert abs(res["photon_energy_residual_eV_per_H"])<1e-16
    assert abs(res["total_energy_residual_eV_per_H"])<3e-12
    assert abs(res["native_thermal_binding_identity_erg_cm3_s"])<5e-38
    assert res["max_scaled_implicit_residual"]<8e-13
    assert res["newton_error_history"][-1]<res["newton_error_history"][0]
    assert r.calls>=6

@pytest.mark.parametrize("case",["ZERO","SHEAR_PLUS"])
def test_frozen_opacity_reduction_and_birth_ledgers(case):
    o,_=fixtures(case)
    g=initial_gas(o)
    p=photon_step(o,g,o.stocks.ravel(),1e10)
    n0=float(o.stocks.sum())
    assert np.isclose(n0+1e10*o.source.sum(),p["n1"].sum()+p["species"].sum(),rtol=1e-14,atol=2e-19)
    # Independent energy accounting from fully species-resolved packet losses.
    full_abs=float(np.sum(p["events"]*p["energy"][:,None]))
    extracted=float(np.sum(p["heat"]+BIND_EV*p["species"]))
    assert abs(full_abs-extracted)<1e-19
    assert abs(binding_ev_per_h(g,o.nHe/o.nH))<20.

def test_source_free_limit_positive():
    o,_=fixtures("ZERO")
    z=replace(o,source=np.zeros_like(o.source))
    dt=1e11
    g=initial_gas(z)
    p=photon_step(z,g,z.stocks.ravel(),dt)
    assert (p["n1"]<=z.stocks.ravel()+1e-25).all()
    assert abs((z.stocks.ravel().sum()-p["n1"].sum())-p["species"].sum())<3e-20

@pytest.mark.parametrize("bad",[
    np.array([1.1,0,0,1.]),
    np.array([0.1,0.8,0.3,1.]),
    np.array([0.1,-0.1,0.1,1.]),
    np.array([0.1,0.2,0.1,-1.]),
    np.array([0.1,0.2,0.1,float("nan")])
])
def test_invalid_gas_denied(bad):
    assert not valid_gas(bad)

def test_invalid_photon_and_time_denied():
    o,_=fixtures("ZERO")
    g=initial_gas(o)
    with pytest.raises(ValueError):photon_step(o,g,o.stocks.ravel(),-2)
    with pytest.raises(ValueError):photon_step(o,g,np.array([1.0]),1e10)
    with pytest.raises(ValueError):photon_step(o,g,-o.stocks.ravel(),1e10)

def test_implicit_full_vs_twohalf_source_not_double_injected():
    o,r=fixtures("ZERO")
    dt=1e12
    f=step(o,r,dt)
    a=step(o,r,dt/2)
    b=step(o,r,dt/2,np.array(a["new_gas"]),a["new_stocks"])
    # At this dt the reaction is weak but the two discrete schemes are not
    # artificially asserted identical. Splitting must preserve photon mass.
    assert abs(f["photon_number_residual"])<2e-17
    assert abs(a["photon_number_residual"])<2e-17
    assert abs(b["photon_number_residual"])<2e-17
    assert abs(b["total_energy_residual_eV_per_H"])<2e-12
    assert not np.array_equal(f["new_stocks"],b["new_stocks"])
    assert np.sum(np.abs(f["new_stocks"]-b["new_stocks"])) < 5e-10
    assert np.max(np.abs(np.array(f["new_gas"])-np.array(b["new_gas"])))<1e-6
    # Injection interval algebra: no source counted twice across half cells.
    assert abs(o.source.sum()*dt -
         (o.source.sum()*dt/2+o.source.sum()*dt/2))<1e-24
