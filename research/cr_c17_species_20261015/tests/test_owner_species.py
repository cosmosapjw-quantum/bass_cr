"""Owner-locked q and real Verner threshold species-attribution convergence."""
from pathlib import Path
import os
import numpy as np
import pytest

from owner_age_bridge import owner_namespace,source_identity
from owner_species_benchmark import case

ROOT=Path(os.environ.get("REI_BIANCHI_ROOT",
                          "/home/cosmosapjw/Dropbox/bianchi/rei_bianchi"))


@pytest.fixture(scope="module")
def ns():
    source_identity(ROOT)
    return owner_namespace(ROOT)


@pytest.mark.parametrize("q",[-.01,0.,.01])
def test_owner_HI_HeI_HeII_events_converge_second_order(q,ns):
    r=case(ns,q,nsteps=(16,32,64,128))
    # One threshold crossing is real for all three signed q.
    assert len(r["threshold_event_scale_factors"])==1
    prev=np.array([x['C16_species_total_max_rel_error'] for x in r['grid_runs']])
    now=np.array([x['C17_species_total_max_rel_error'] for x in r['grid_runs']])
    assert np.all(prev[1:]/now[1:] >100)
    assert np.all(prev[:-1]/prev[1:]<2.3)
    assert np.all(now[:-1]/now[1:]>3.7)
    assert now[-1]<4e-7
    for x in r["grid_runs"]:
        assert abs(x["C17_total_photons_residual"])<1e-11
        assert abs(x["C16_vs_C17_same_survivor_max_abs"])<1e-14
    assert r["reference_species_totals"][2]>0


def test_HI_threshold_no_opacity_branch_preserves_existing_photons(ns):
    r=case(ns,0.,nsteps=(8,))
    ref=np.array(r["reference_species_totals"])
    calculated=np.array(r["grid_runs"][0]["species_events_C17"])
    assert np.all(calculated>=0)
    assert np.isclose(sum(calculated),sum(ref),rtol=3e-4)
