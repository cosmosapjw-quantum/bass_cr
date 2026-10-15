"""Actual owner-source science regression, not mock/stub validation."""
import os
from pathlib import Path

import numpy as np
import pytest

from owner_age_bridge import (
    FEATURE_NAMES, design_positive, errors, gas_states, make_packets,
    owner_namespace, q_experiment, run, source_identity,
)

root = os.environ.get("REI_BIANCHI_ROOT")
if not root:
    pytest.skip("Set REI_BIANCHI_ROOT to run authoritative owner-source tests", allow_module_level=True)
ROOT = Path(root)


def test_owner_snapshot_is_known_and_unchanged():
    identity = source_identity(ROOT)
    assert sorted(identity) == ["age", "emission", "scenario"]


@pytest.mark.parametrize("q", [0.0, 0.01])
def test_exact_owner_scalar_formula_parity_including_heii(q):
    ns = owner_namespace(ROOT)
    ages = np.geomspace(ns["model"].ar, 0.2, 36)
    gases = np.array([(ns["nh"], ns["nhe"], 0.),
                      (.6*ns["nh"], .75*ns["nhe"], .25*ns["nhe"])])
    p = make_packets(ns, q, ages)
    got = p.response(gases)
    for ia in (0, 15, 35):
        for ig, gas in enumerate(gases):
            scalar = ns["vector"](float(ages[ia]), q, gas)
            fast = got[ig,ia]
            as_owner = np.array([fast[0], fast[1], fast[2],fast[3],fast[5]+fast[6]+fast[7]])
            np.testing.assert_allclose(as_owner,scalar,rtol=4e-12,atol=1e-13)
    assert np.max(got[1,:,4]) > 0
    assert np.max(got[1,:,7]) > 0


def test_photon_budget_and_photoelectron_energy_ledger():
    ns=owner_namespace(ROOT)
    ages=np.geomspace(ns["model"].ar,0.2,36)
    packet=make_packets(ns, -.01, ages)
    train, hold, _=gas_states(ns)
    T=packet.response(np.vstack((train,hold)))
    assert T.shape==(23,36,len(FEATURE_NAMES))
    assert np.all(T[:,:,0]>0)
    assert np.all(T[:,:,2:8]>=-1e-16)
    absorption=T[:,:,2:5].sum(axis=2)
    assert np.all(absorption<=T[:,:,0]+1e-12)
    absorbed_energy=T[:,:,5:8].sum(axis=2)+np.einsum("gaj,j->ga",T[:,:,2:5],packet.bind_eV)
    assert np.all(absorbed_energy<=T[:,:,1]+1e-10)
    assert np.all(T[:,:,-1] >= -1e-16)
    # Very small but independently positive HeII count exists when nHeII>0.
    assert T[1,:,4].sum()>0
    with pytest.raises(ValueError):
        packet.response(np.array([[1.,-1.,0.]]))


def test_multistate_holdout_improves_heii_without_changing_photon_number():
    row=q_experiment(0., str(ROOT))
    single,multi=row['designs']['1'],row['designs']['3']
    assert single['retained_age_count']<36 and multi['retained_age_count']<36
    assert single['holdout_max_error']>1e-2
    assert multi['holdout_max_error']<1e-6
    assert multi['holdout_max_error'] < single['holdout_max_error']*1e-4
    assert multi['photon_budget_violation']==0
    assert row['feature_names'][4]=="HeII_absorbed"


def test_serial_parallel_same_science():
    one=run(ROOT,1,qs=(-.01,0.,.01))
    two=run(ROOT,2,qs=(-.01,0.,.01))
    for x,y in zip(one['records'],two['records']):
        for key in ('1','3'):
            assert x['designs'][key]['weights'] == y['designs'][key]['weights']
            assert x['designs'][key]['holdout_max_error'] == y['designs'][key]['holdout_max_error']
    assert one['source_sha256']==two['source_sha256']
