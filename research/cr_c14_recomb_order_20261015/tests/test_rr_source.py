"""C14 regression tests: owner H/He RR, exact photon birth, positivity and ODE order."""
from __future__ import annotations
import json
import os
from pathlib import Path

import numpy as np
import pytest
from scipy.integrate import quad

from owner_age_bridge import owner_namespace,source_identity
from physical_age import Gas
from transport import integrate,recombine_case_a,alpha_owner_rr
from rr_order import orders,reference
from exponential_source import (
    absorb_with_source,midpoint_born_source,
    test_matrix_lambda_from_owner as owner_opacity,
    phi_neg,absorbed_source_fraction,
)

ROOT=Path(os.environ.get("REI_BIANCHI_ROOT",
       "/home/cosmosapjw/Dropbox/bianchi/rei_bianchi"))


@pytest.fixture(scope="module")
def ns():
    source_identity(ROOT)
    return owner_namespace(ROOT)


@pytest.mark.parametrize("T",[4000.,9000.])
def test_recomb_midpoint_restores_second_order(T,ns):
    gas=Gas(.9,.85,.15,0.,T)
    result=orders(ns,numbers=(8,16,32,64),g=gas,ne_method="midpoint")
    e=np.array([abs(r["xhi_error"]) for r in result["rows"]])
    assert np.all(e[:-1]/e[1:]>3.8)
    old=orders(ns,numbers=(8,16,32,64),g=gas,ne_method="frozen")
    eold=np.array([abs(r["xhi_error"]) for r in old["rows"]])
    assert np.all(eold[:-1]/eold[1:] <2.2)
    assert e[-1] < eold[-1]/100


@pytest.mark.parametrize("T",[4000.,9000.])
def test_frozen_rr_is_backward_compatible(T,ns):
    g=Gas(.9,.85,.15,0.,T)
    ne=g.electrons_per_h(ns["nhe"]/(ns["model"].nh*125))
    rr=alpha_owner_rr(T)
    nH=ns["model"].nh/.1**3
    y=ns["nhe"]/(ns["model"].nh*125)
    dt=1e12
    out,evt,_=recombine_case_a(g,dt,nH,nH*y,ne_method="frozen")
    expected=(1-g.xhi)*np.exp(-rr[0]*nH*ne*dt)
    np.testing.assert_allclose(1-out.xhi,expected,rtol=1e-13)
    assert all(evt>=0)


def test_midpoint_rr_charge_nuclei_and_thermal_ledger(ns):
    g=Gas(.8,.4,.55,.05,4700.)
    nH=ns["model"].nh/.12**3
    y=ns["nhe"]/(ns["model"].nh*125)
    nHe=nH*y
    out,events,escape=recombine_case_a(g,1e13,nH,nHe,ne_method="midpoint")
    assert np.all(events>=0)
    assert abs(out.xhei+out.xheii+out.xheiii-1)<1e-12
    assert abs((g.thermal_energy_ev_per_h(y)-out.thermal_energy_ev_per_h(y))-escape)<1e-12
    assert out.electrons_per_h(y)<g.electrons_per_h(y)
    # Recompute the n_e midpoint implicit equation on its physical branch:
    from scipy.optimize import brentq
    ne0=g.electrons_per_h(y)
    rr=alpha_owner_rr(g.temp_K)
    def xend(ne):
        a=rr*nH*1e13*ne
        h2=(1-g.xhi)*np.exp(-a[0])
        he3=g.xheiii*np.exp(-a[2])
        if abs(a[1]-a[2])<1e-8:
            he2=np.exp(-a[1])*(g.xheii+a[2]*g.xheiii)
        else:
            he2=g.xheii*np.exp(-a[1])+g.xheiii*a[2]*(np.exp(-a[2])-np.exp(-a[1]))/(a[1]-a[2])
        return h2+y*(he2+2*he3)
    mid=brentq(lambda v:v-.5*(ne0+xend(v)),0,ne0,xtol=2e-14)
    expected_h2=(1-g.xhi)*np.exp(-rr[0]*nH*mid*1e13)
    np.testing.assert_allclose(1-out.xhi,expected_h2,rtol=2e-12)


@pytest.mark.parametrize("tau",[0.,1e-12,1e-7,1.,10.,100.,2000.])
def test_exact_source_phi_integral(tau):
    if tau==0:
        assert phi_neg(tau)==1
        assert absorbed_source_fraction(tau)==0
        return
    direct=quad(lambda z:np.exp(-tau*(1-z)),0.,1.,epsabs=1e-14,epsrel=1e-13)[0]
    np.testing.assert_allclose(phi_neg(tau),direct,rtol=2e-12,atol=1e-15)
    np.testing.assert_allclose(phi_neg(tau)+absorbed_source_fraction(tau),1.,rtol=0,atol=4e-16)


def test_positive_3species_source_absorption_conservation(ns):
    photons=np.array([0.,1.,2.,3.])
    source=np.array([.01,.02,.03,.01])
    rates=np.array([[0,0,0],
                    [1e-20,2e-20,1e-20],
                    [1e-4,2e-4,1e-4],
                    [8e-13,7e-13,1e-13]])
    end,events,born=absorb_with_source(photons,source,rates,1e4)
    assert np.all(end>=0) and np.all(events>=0)
    np.testing.assert_allclose(photons+source*1e4,end+events.sum(axis=1),rtol=1e-13,atol=1e-11)
    assert end[0]==100
    assert events[0].sum()==0
    with pytest.raises(ValueError):
        absorb_with_source(photons,np.array([0.,-1.,0.,0.]),rates,1e4)


def test_owner_opacity_midpoint_failure_and_exact_source(ns):
    E,lam=owner_opacity(ns)
    assert np.all(lam>=0)
    from scipy.integrate import quad
    proper=quad(lambda u:1/ns["model"].hubble(np.exp(u),0),
                np.log(.1),np.log(.11))[0]
    dt=proper/128
    tau=lam[0].sum()*dt
    assert tau>100
    emit=np.array([.01])
    rate=emit/dt
    new,ev,ret=absorb_with_source(np.array([0.]),rate,lam[:1],dt)
    midpoint=midpoint_born_source(np.array([0.]),rate,lam[:1],dt)
    assert new[0]>0 and midpoint[0]/new[0]<1e-50
    np.testing.assert_allclose(new[0],emit[0]*phi_neg(tau),rtol=1e-14)


def test_no_source_optimization_does_not_create_zero_mass_packets(ns):
    k=integrate(ns,0.,128,source_scale=0.,rr_ne_method="frozen")
    assert k["output_photon_packets"]==0
    assert k["packet_memory_bytes"]==0
    np.testing.assert_allclose(k["gas_final"]["xhi"],
                              0.9038310775775847,rtol=5e-13)


def test_rr_midpoint_vs_full_source_case_positivity(ns):
    d=integrate(ns,0.,16,rr_ne_method="midpoint")
    old=integrate(ns,0.,16,rr_ne_method="frozen")
    assert abs(d["ledgers"]["photon_count_residual"])<1e-12
    assert abs(d["ledgers"]["total_local_energy_residual_eV_per_H"])<1e-11
    assert min(d["gas_final"][k] for k in ("xhi","xhei","xheii","xheiii"))>=0
    assert old["gas_final"]["xhi"]!=d["gas_final"]["xhi"]
