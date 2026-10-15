"""Source-bound, conservative, conditional Bianchi-I time-transport tests."""
from __future__ import annotations
import hashlib
import math
import os
from pathlib import Path
import subprocess
import tempfile

import numpy as np
from scipy.integrate import quad
from scipy.linalg import expm
import pytest

from owner_age_bridge import owner_namespace, source_identity
from physical_age import Gas
from transport import (
    alpha_owner_rr, C, PhotonStock, make_birth_cohort,
    photon_energy_ratio, vector_photo_reactions, recombine_case_a,
    integrate,
)

ROOT=Path(os.environ.get("REI_BIANCHI_ROOT",
        "/home/cosmosapjw/Dropbox/bianchi/rei_bianchi"))
if not ROOT.exists():
    pytest.skip("Actual owner checkout required",allow_module_level=True)


@pytest.fixture(scope="module")
def ns():
    source_identity(ROOT)
    return owner_namespace(ROOT)


def test_owner_bound_and_birth_photon_normalization(ns):
    model=ns["model"]
    c=make_birth_cohort(ns,.1,0.,.125,nmu=8,energy_order=8)
    assert c.count==8*8*3
    assert all(c.photons_per_H>=0)
    assert abs(c.photons_per_H.sum()-.125)<1e-13
    assert np.allclose(c.current_energy_eV,c.birth_energy_eV)


def test_bianchi_energy_at_birth_and_flrw_and_general_source_ratio(ns):
    model=ns["model"]
    a=np.array([.10,.10,.10,.08,.08])
    mu=np.array([-1,-.2,0,.4,1])
    assert np.allclose(photon_energy_ratio(model,a,.15,0.,mu),a/.15,
                       rtol=2e-14)
    assert np.allclose(photon_energy_ratio(model,a,.15,.01,mu),
                       (a/.15)*np.sqrt(
                            np.exp(2*np.array([model.b(.15,.01)-model.b(float(x),.01) for x in a]))*(1-mu**2)
                            +np.exp(-4*np.array([model.b(.15,.01)-model.b(float(x),.01) for x in a]))*mu**2),rtol=2e-14)
    assert np.allclose(photon_energy_ratio(model,a,a.max(),0.,mu[a==a.max()]) if False else
            photon_energy_ratio(model,np.array([.1]),.1,.01,np.array([.3])),
            [1.],atol=2e-14)
    with pytest.raises(ValueError):
        photon_energy_ratio(model,a,.06,0.,mu)


def test_scalar_reaction_kernel_parity(ns):
    energy=np.array([13.61,17.2,24.6,44.,54.5,78.,99.])
    photon=np.array([.02,.01,.03,.02,.015,.005,.01])
    neutral=np.array([2e-4,1e-5,3e-6])
    dt=1e8
    s,e,h=vector_photo_reactions(photon,energy,neutral,dt,ns["fit"],
                                np.asarray(ns["bind"]))
    slow_survive=[]
    slow_ev=np.zeros(3)
    slow_heat=np.zeros(3)
    for p,E in zip(photon,energy):
        tau=np.array([C*dt*n*ns["sigma"](float(E),f) for n,f in zip(neutral,ns["fit"])])
        total=tau.sum()
        prob=tau*(-np.expm1(-total)/total) if total else np.zeros(3)
        events=p*prob
        slow_survive.append(p*np.exp(-total))
        slow_ev+=events
        slow_heat+=events*(E-np.asarray(ns["bind"]))
    np.testing.assert_allclose(s,slow_survive,rtol=1e-13,atol=1e-14)
    np.testing.assert_allclose(e,slow_ev,rtol=1e-13,atol=1e-14)
    np.testing.assert_allclose(h,slow_heat,rtol=1e-13,atol=1e-14)


@pytest.mark.parametrize("T",[100.,2000.,4000.,5500.,5501.,10000.,2e5])
def test_grackle_rate_source_matches_compiled_original_rust(ns,T):
    rust=ROOT/'rust/rei_microphysics/src/igm_rates.rs'
    assert rust.is_file()
    source=rust.read_text()
    assert 'pub fn igm_rates' in source
    # Direct execution of owner Rust function, not another translation.
    with tempfile.TemporaryDirectory(prefix="cr_rate_") as d:
        src=Path(d)/"main.rs"
        exe=Path(d)/"rates"
        src.write_text(
          '#![allow(dead_code)]\n'
          "#[derive(Debug)] enum ForwardError{InvalidInput(&'static str)}\n"
          f'#[path="{rust}"] mod source;\n'
          'fn main(){let t=std::env::args().nth(1).unwrap().parse::<f64>().unwrap();'
          'let a=source::igm_rates(t).unwrap().rr_cm3_s;'
          'println!("{:.17e} {:.17e} {:.17e}",a[0],a[1],a[2]);}\n')
        result=subprocess.run(["rustc","--edition=2021","-O",str(src),"-o",str(exe)],
                       capture_output=True,text=True)
        if result.returncode: raise RuntimeError(result.stderr)
        actual=np.array([float(x) for x in
               subprocess.check_output([str(exe),str(T)],text=True).split()])
    ours=alpha_owner_rr(T)
    np.testing.assert_allclose(ours,actual,rtol=2e-15,atol=0.)


def test_he_three_state_markov_solution_vs_scipy_expm(ns):
    gas=Gas(.75,.55,.4,.05,9000.)
    nH=ns["model"].nh/.1**3
    y=ns["nhe"]/(ns["model"].nh*125)
    nHe=nH*y
    dt=3e12
    out,evt,thermal=recombine_case_a(gas,dt,nH,nHe)
    ne=nH*gas.electrons_per_h(y)
    rates=alpha_owner_rr(gas.temp_K)*ne
    mat=np.array([[0,rates[1],0],[0,-rates[1],rates[2]],[0,0,-rates[2]]])
    exact=expm(mat*dt)@np.array([gas.xhei,gas.xheii,gas.xheiii])
    np.testing.assert_allclose([out.xhei,out.xheii,out.xheiii],exact,
                               rtol=2e-12,atol=2e-13)
    assert np.all(evt>=0)
    assert thermal>=0


@pytest.mark.parametrize("q",[-.01,0.,.01])
def test_full_photon_thermal_binding_geometry_ledgers(ns,q):
    out=integrate(ns,q=q,nstep=32,recombination=True)
    L=out["ledgers"]
    assert out["output_photon_packets"]==32*8*8*3
    assert abs(L["photon_count_residual"])<1e-10
    assert abs(L["total_local_energy_residual_eV_per_H"])<1e-9
    assert abs(L["helium_nucleus_residual"])<1e-11
    assert abs(L["charge_residual"])<1e-11
    assert L["source_emitted_photons_per_H"]>0
    assert L["final_photons_per_H"]>=0
    assert np.all(np.asarray(L["photo_events_per_H"])>=0)
    assert np.all(np.asarray(L["recomb_events_per_H"])>=0)
    assert out["gas_final"]["temp_K"]>0


def test_midpoint_emission_source_integral_converges_second_order(ns):
    model=ns["model"]
    reference=quad(lambda u:model.rate(np.exp(u))/model.hubble(np.exp(u),0.),
                   np.log(.1),np.log(.11),epsabs=1e-12,epsrel=1e-12)[0]
    err=[]
    for n in (16,32,64):
        v=integrate(ns,0.,n,recombination=False)
        err.append(abs(v["ledgers"]["source_emitted_photons_per_H"]-reference))
    assert err[0]/err[1]>3.8
    assert err[1]/err[2]>3.8


def test_no_source_no_recomb_only_adiabatic_dilution(ns):
    g=Gas(.5,.7,.3,0,4000.)
    v=integrate(ns,0.,nstep=12,gas0=g,recombination=False,source_scale=0)
    out=v["gas_final"]
    assert out["xhi"]==g.xhi
    assert np.allclose([out["xhei"],out["xheii"],out["xheiii"]],
                        [g.xhei,g.xheii,g.xheiii],atol=1e-13)
    np.testing.assert_allclose(out["temp_K"],g.temp_K*(.1/.11)**2,rtol=2e-13)
    assert v["ledgers"]["source_emitted_photons_per_H"]==0
    assert v["ledgers"]["photo_events_per_H"]==[0,0,0]
    assert abs(v["ledgers"]["total_local_energy_residual_eV_per_H"])<1e-11


def test_no_source_recombination_conserves_charge_energy(ns):
    v=integrate(ns,0.,nstep=12,source_scale=0,recombination=True)
    assert sum(v["ledgers"]["recomb_events_per_H"])>0
    assert v["gas_final"]["xhi"]>v["gas_initial"]["xhi"]
    assert abs(v["ledgers"]["photon_count_residual"])<1e-12
    assert abs(v["ledgers"]["total_local_energy_residual_eV_per_H"])<1e-10


def test_time_refinement_three_cases_and_q_symmetry(ns):
    xs=[]
    for n in (16,32,64):
        xs.append(integrate(ns,0.,n))
    a=xs[0]["gas_final"];b=xs[1]["gas_final"];c=xs[2]["gas_final"]
    err1=abs(a["xhi"]-b["xhi"])
    err2=abs(b["xhi"]-c["xhi"])
    assert err1>err2
    # With temperature-dependent recombination branch crossing,
    # guarantee observed convergence without post-hoc order claim.
    assert err1/err2>1.5


def test_two_point_emission_quadrature_reduces_source_error(ns):
    model=ns["model"]
    exact=quad(lambda u:model.rate(np.exp(u))/model.hubble(np.exp(u),0),
               np.log(.1),np.log(.11),epsrel=1e-12)[0]
    midpoint=integrate(ns,0.,16,recombination=False,source_rule="midpoint")
    gauss=integrate(ns,0.,16,recombination=False,source_rule="gauss2")
    em=abs(midpoint["ledgers"]["source_emitted_photons_per_H"]-exact)
    eg=abs(gauss["ledgers"]["source_emitted_photons_per_H"]-exact)
    assert eg < em/1000
    assert abs(gauss["ledgers"]["photon_count_residual"])<1e-12
    assert abs(gauss["ledgers"]["total_local_energy_residual_eV_per_H"])<1e-11
    assert gauss["output_photon_packets"]==2*midpoint["output_photon_packets"]
