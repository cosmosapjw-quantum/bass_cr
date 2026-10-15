"""Authenticated owner C8/C14 -> positive continuous photon birth test suite."""
from __future__ import annotations
import os
from pathlib import Path
import numpy as np
import pytest
from scipy.integrate import quad

from owner_age_bridge import owner_namespace,source_identity
from physical_age import Gas
from transport import integrate
from continuous_source import evolve_continuous,proper_dt
from exponential_source import absorb_with_source,phi_neg

ROOT=Path(os.environ.get("REI_BIANCHI_ROOT",
                          "/home/cosmosapjw/Dropbox/bianchi/rei_bianchi"))
if not ROOT.exists():
    pytest.skip("actual owner source folder required",allow_module_level=True)

@pytest.fixture(scope="module")
def ns():
    source_identity(ROOT)
    return owner_namespace(ROOT)


@pytest.mark.parametrize("q",[-.01,0.,.01])
def test_owner_clock_positive_against_independent_quadpack(ns,q):
    m=ns["model"]
    actual=proper_dt(m,.1,.11,q)
    oracle=quad(lambda s:1/m.hubble(np.exp(s),q),
                np.log(.1),np.log(.11),epsrel=1e-12)[0]
    assert abs(actual-oracle)/oracle < 1e-6


def test_positive_source_and_all_ledgers(ns):
    new=evolve_continuous(ns,0.,32)
    l=new['ledgers']
    assert l['final_photons_per_H']>0
    assert all(x>=0 for x in l['photo_events_per_H'])
    assert all(x>=0 for x in l['RR_events_per_H'])
    assert abs(l['photon_number_residual'])<1e-12
    assert abs(l['local_energy_residual_eV_per_H'])<1e-11
    assert abs(l['nuclei_He_residual'])<1e-12
    assert abs(l['charge_residual_per_H'])<1e-12
    assert new['gas_final']['temp_K']>0
    assert new['gas_final']['xhi']<.9
    assert new['gas_final']['xheiii']>0


@pytest.mark.parametrize("q",[0.,.01])
def test_cached_and_uncached_birth_identical(ns,q):
    a=evolve_continuous(ns,q,24,cached_birth_spectrum=False)
    b=evolve_continuous(ns,q,24,cached_birth_spectrum=True)
    for k in a['gas_final']:
        np.testing.assert_allclose(a['gas_final'][k],b['gas_final'][k],
                                   rtol=1e-13,atol=1e-13)
    for k in ('final_photons_per_H','final_photon_energy_eV_per_H',
              'source_photons_per_H','photon_number_residual',
              'local_energy_residual_eV_per_H'):
        np.testing.assert_allclose(a['ledgers'][k],b['ledgers'][k],
                                   rtol=2e-12,atol=1e-12)


def test_lossless_only_exact_zero_packet_pruning(ns):
    a=evolve_continuous(ns,0.,16,exact_zero_prune=False)
    b=evolve_continuous(ns,0.,16,exact_zero_prune=True)
    assert b['photon_packet_count']<=a['photon_packet_count']
    for k in a['gas_final']:
        np.testing.assert_allclose(a['gas_final'][k],b['gas_final'][k],
                rtol=1e-13,atol=2e-12)
    np.testing.assert_allclose(a['ledgers']['final_photons_per_H'],
                               b['ledgers']['final_photons_per_H'],
                               rtol=1e-13,atol=2e-13)


def test_no_source_gas_recombination_second_order(ns):
    g=Gas(.9,.85,.15,0.,4000.)
    a=evolve_continuous(ns,0.,16,source_scale=0,gas0=g)
    b=evolve_continuous(ns,0.,32,source_scale=0,gas0=g)
    assert a['photon_packet_count']==b['photon_packet_count']==0
    assert a['ledgers']['final_photons_per_H']==0
    from rr_order import reference
    target,T,_=reference(ns,g)
    e16=abs(a['gas_final']['xhi']-target[0])
    e32=abs(b['gas_final']['xhi']-target[0])
    assert e16/e32>3.7
    assert abs(a['ledgers']['local_energy_residual_eV_per_H'])<1e-12


def test_owner_source_zero_opacity_photon_and_energy_second_order(ns):
    m=ns['model'];spec=ns['spec']
    lo,hi=np.log(.1),np.log(.11)
    N=quad(lambda z:m.rate(np.exp(z))/m.hubble(np.exp(z),0),
           lo,hi,epsrel=1e-12)[0]
    integral_phi=quad(lambda E:float(spec.phi(E)),13.6,100.,
                      epsrel=1e-12)[0]
    mean_E=quad(lambda E:E*float(spec.phi(E)),13.6,100.,
                epsrel=1e-12)[0]/integral_phi
    expected_E=(mean_E/.11)*quad(
           lambda z:m.rate(np.exp(z))/m.hubble(np.exp(z),0)*np.exp(z),
           lo,hi,epsrel=1e-12)[0]
    old=[]
    for n in (16,32,64):
        x=evolve_continuous(ns,0.,n,
               gas0=Gas(0.,0.,0.,1.,4000.),recombination=False)
        assert all(np.isclose(x['gas_final'][k],v,atol=1e-10)
                   for k,v in [('xhi',0.),('xhei',0.),('xheii',0.),('xheiii',1.)])
        old.append((abs(x['ledgers']['final_photons_per_H']-N),
                    abs(x['ledgers']['final_photon_energy_eV_per_H']-expected_E)))
        assert abs(x['ledgers']['local_energy_residual_eV_per_H'])<1e-12
    err=np.asarray(old)
    assert np.all(err[0]/err[1]>3.7)
    assert np.all(err[1]/err[2]>3.7)


def test_high_tau_source_survivors_without_physical_gate_promotion(ns):
    old=integrate(ns,0.,32,rr_ne_method="midpoint")
    new=evolve_continuous(ns,0.,32)
    # A positive continuous source contributes at the END of an opaque
    # interval. Existing C13 midpoint point injection loses most of it.
    assert new['ledgers']['final_photons_per_H']>1e-7
    assert new['ledgers']['final_photons_per_H']>100*old['ledgers']['final_photons_per_H']
    assert abs(new['ledgers']['photon_number_residual'])<1e-12
    # We do not assert that the model with evolving gas is "exact".


def test_C15_gas_midpoint_empirical_temporal_order(ns):
    vals=[]
    for n in (16,32,64,128):
        result=evolve_continuous(ns,0.,n)
        vals.append([result['gas_final']['xhi'],result['gas_final']['temp_K'],
                     result['ledgers']['final_photons_per_H']])
    a=np.array(vals)
    # Consecutive differences should shrink near factor four for gas.
    d=np.abs(np.diff(a,axis=0))
    assert d[0,0]/d[1,0]>3.
    assert d[1,0]/d[2,0]>3.
    assert d[0,1]/d[1,1]>3.
    assert d[1,1]/d[2,1]>3.
    # Photon survivor only shrinks about factor two in this stiff case:
    # keep its *separate* unresolved global-order status.
    assert 1.5<d[1,2]/d[2,2]<2.5


def test_reject_invalid_source_and_clock(ns):
    for kw in ({"source_scale":-1},{"nstep":1},{"a0":.11,"a1":.1},
               {"rr_ne_method":"unknown"}):
        with pytest.raises(ValueError):
            evolve_continuous(ns,0.,**kw)
    with pytest.raises(ValueError):
        proper_dt(ns['model'],.2,.1,0.)
