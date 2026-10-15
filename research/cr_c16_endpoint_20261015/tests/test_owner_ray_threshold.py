"""Actual pinned owner Verner threshold-crossing regression against Radau."""
from pathlib import Path
import numpy as np
import pytest
from owner_age_bridge import owner_namespace,source_identity
from owner_ray_benchmark import experiment

ROOT=Path("/home/cosmosapjw/Dropbox/bianchi/rei_bianchi")


def test_HI_14eV_threshold_has_exact_FLRW_crossing_and_extra_interval():
    ns=owner_namespace(ROOT)
    q0=experiment(ns,0.,nsteps=(16,32,64),threshold_aware=True)
    assert len(q0["detected_events_scale_factor"])==1
    expected=.1*14./13.6
    assert abs(q0["detected_events_scale_factor"][0]-expected)<1e-13
    assert all(c["actual_subintervals"]==c["nsteps"]+1
               for c in q0["curves"])
    # Strong-opacity survivor is checked across ALL five frequency channels.
    err=np.array([c["methods"]["C16_optical_quad"]["max_relative_photon_error"]
                  for c in q0["curves"]])
    assert err[0]/err[1]>3.7
    assert err[1]/err[2]>3.7
    assert err[-1]<1e-6


def test_threshold_aware_more_accurate_than_unpartitioned_after_refinement():
    ns=owner_namespace(ROOT)
    raw=experiment(ns,0.,nsteps=(32,64),threshold_aware=False)
    split=experiment(ns,0.,nsteps=(32,64),threshold_aware=True)
    for a,b in zip(raw["curves"],split["curves"]):
        erra=a["methods"]["C16_optical_quad"]["max_relative_photon_error"]
        errb=b["methods"]["C16_optical_quad"]["max_relative_photon_error"]
        assert errb<erra/100
        # Both use exactly the same independently integrated ODE reference.
        np.testing.assert_array_equal(raw["reference_Radau"],split["reference_Radau"])
        assert b["actual_subintervals"]==b["nsteps"]+1


@pytest.mark.parametrize("q",[-.01,.01])
def test_signed_q_event_threshold_and_positive_nonzero_survivors(q):
    ns=owner_namespace(ROOT)
    r=experiment(ns,q,nsteps=(32,64),threshold_aware=True)
    assert len(r["detected_events_scale_factor"])==1
    e=np.array([x["methods"]["C16_optical_quad"]["max_relative_photon_error"] for x in r["curves"]])
    assert e[0]/e[1]>3.6
    for x in r["curves"]:
        arr=np.asarray(x["methods"]["C16_optical_quad"]["photon_survivor_per_H"])
        assert np.all(arr>0)
