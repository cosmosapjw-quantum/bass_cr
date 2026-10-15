"""Scientific tests against the SHA-locked actual rei_bianchi C8 source."""
from __future__ import annotations
import os
from pathlib import Path

import numpy as np
import pytest

from owner_age_bridge import owner_namespace, make_packets, source_identity
from physical_age import (
    Gas, physical_age_rule, positive_nullspace_reduce,
    emission_packets, absorb_species, evolve
)
from continuum_oracle import reference_eight
from independent_ode import solve_reference

ROOT=Path(os.environ.get("REI_BIANCHI_ROOT",
                          "/home/cosmosapjw/Dropbox/bianchi/rei_bianchi"))
if not ROOT.exists():
    pytest.skip("Must set valid REI_BIANCHI_ROOT for owner-bound science tests",
                allow_module_level=True)


@pytest.fixture(scope="module")
def owner():
    source_identity(ROOT)
    return owner_namespace(ROOT)


def training():
    return (Gas(), Gas(.25,.25,.6,.15,1500.), Gas(.95,.8,.15,.05,400.))


@pytest.mark.parametrize("q", [-.01,0.,.01])
def test_md14_weighted_source_integrates_owner_rate_without_moment_loss(owner,q):
    a,w=physical_age_rule(owner,q,32)
    source_exact=owner["model"].total_emitted(q)
    assert np.all(np.diff(a)>0)
    assert np.all(w>0)
    assert abs(sum(w)-source_exact)/source_exact < 1e-11


def test_independent_quadpack_helium_ionization_and_heat(owner):
    ages=np.array([.08,.14,.2])
    q=.01
    nH=owner["model"].nh*125
    nHe=owner["nhe"]
    gas=np.array([.7*nH,.6*nHe,.35*nHe])
    packet=make_packets(owner,q,ages)
    fixed_gl=packet.response(gas[None,:])[0]
    for age,actual in zip(ages,fixed_gl):
        quad=reference_eight(owner,float(age),q,gas)
        np.testing.assert_allclose(actual,quad,rtol=2e-11,atol=2e-12)
    assert fixed_gl[-1,4]>0
    assert fixed_gl[-1,7]>0


@pytest.mark.parametrize("q", [-.01,0.,.01])
def test_constructive_sparse_weights_reproduce_all_training_moments(owner,q):
    packet,metadata=emission_packets(owner,q,48,training(),"three")
    assert 0<metadata["retained_age_nodes"]<48
    assert metadata["training_relative_error"]<1e-10
    assert np.isclose(np.sum(metadata["compressed_weights"]),
                      np.sum(metadata["raw_emission_weights"]),rtol=1e-12)
    assert np.all(metadata["compressed_weights"]>=0)
    assert len(packet.flux)==metadata["npackets"]
    assert np.isclose(sum(packet.flux),np.sum(metadata["raw_emission_weights"]),
                      rtol=1e-12)
    assert metadata["compression_numerics"]["algorithm"]=="positive_SVD_nullspace_pruning"


def test_pruned_age_packets_are_exactly_equivalent_to_zeros(owner):
    from owner_age_bridge import make_packets
    ages=48;q=.01
    optimized,metadata=emission_packets(owner,q,ages,training(),"three")
    old=make_packets(owner,q,metadata["ages"])
    old.flux *= np.repeat(metadata["compressed_weights"],
                     np.diff(np.r_[old.age_starts,len(old.flux)]))
    g=Gas()
    a=evolve(owner,old,g,8e10,16,"midpoint")
    b=evolve(owner,optimized,g,8e10,16,"midpoint")
    for k in b["final_gas"]:
        np.testing.assert_allclose(a["final_gas"][k],b["final_gas"][k],
                                   rtol=5e-13,atol=1e-11)
    assert optimized.flux.nbytes < old.flux.nbytes


def test_coupled_chemical_nuclei_photon_energy_conservation(owner):
    packet,_=emission_packets(owner,0.,32,training(),"full")
    r=evolve(owner,packet,Gas(),8e10,32,"midpoint")
    l=r["ledger"]
    assert abs(l["photon_number_residual"])<3e-12
    assert abs(l["photon_energy_residual_eV_per_H"])<3e-11
    assert abs(l["thermal_energy_residual_eV_per_H"])<3e-11
    assert abs(l["helium_nuclei_residual"])<3e-12
    assert abs(l["charge_residual_per_H"])<3e-12
    assert r["final_gas"]["xhi"]<.7
    assert r["final_gas"]["xheiii"]>.05
    assert r["final_gas"]["temp_K"]>1200


def test_zero_absorbers_no_spurious_ionization_or_heating(owner):
    packet,_=emission_packets(owner,0.,24,training(),"three")
    g=Gas(xhi=0.,xhei=0.,xheii=0.,xheiii=1.,temp_K=1000.)
    r=evolve(owner,packet,g,1e10,8,"midpoint")
    for k in g.__dict__:
        assert abs(r["final_gas"][k]-g.__dict__[k])<5e-10
    assert abs(r["ledger"]["photon_number_residual"])<1e-12
    assert np.allclose(r["ledger"]["absorbed_photons_per_H"],0,atol=1e-12)


def test_midpoint_second_order_against_independent_ode(owner):
    packet,_=emission_packets(owner,0.,32,training(),"one")
    g=Gas()
    exact=solve_reference(owner,packet,g,8e10,rtol=1e-11,atol=1e-13)
    errs=[]
    for steps in [8,16,32]:
        mp=evolve(owner,packet,g,8e10,steps,"midpoint")
        fr=evolve(owner,packet,g,8e10,steps,"frozen")
        em=abs(mp["final_gas"]["xhi"]-exact["final_gas"]["xhi"])
        ef=abs(fr["final_gas"]["xhi"]-exact["final_gas"]["xhi"])
        assert em<ef
        errs.append(em)
    assert errs[0]/errs[1]>3.5
    assert errs[1]/errs[2]>3.5
    assert abs(exact["photons_residual"])<1e-10
    assert abs(exact["energy_residual"])<1e-10


def test_compressed_chemistry_with_independent_ode_holdout(owner):
    g=Gas()
    reference={}
    for mode in ("full","one","three"):
        packet,_=emission_packets(owner,0.,32,training(),mode)
        reference[mode]=solve_reference(owner,packet,g,8e10)
    full=reference["full"]["final_gas"]
    err1=abs(reference["one"]["final_gas"]["temp_K"]-full["temp_K"])
    err3=abs(reference["three"]["final_gas"]["temp_K"]-full["temp_K"])
    assert err3<err1*1e-2
    assert err3<1e-5


def test_serial_spawn_parallel_produce_the_same_states():
    from compare_ode import compare
    serial=compare(ROOT,n_age=24,workers=1,qs=(0.,.01))
    parallel=compare(ROOT,n_age=24,workers=2,qs=(0.,.01))
    for a,b in zip(serial["results"],parallel["results"]):
        assert a["q_ref"]==b["q_ref"]
        for mode in ("full","one","three"):
            assert a["modes"][mode]["retained_age_nodes"]==b["modes"][mode]["retained_age_nodes"]
            for key,val in a["modes"][mode]["final_gas"].items():
                np.testing.assert_allclose(val,b["modes"][mode]["final_gas"][key],rtol=2e-12,atol=1e-11)
