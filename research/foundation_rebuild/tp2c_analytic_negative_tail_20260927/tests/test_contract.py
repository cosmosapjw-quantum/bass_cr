import json
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parents[1]
C=json.loads((HERE/'CONTRACT.json').read_text())
sys.path.insert(0,str(HERE))
import run_negative_tail_qualification as runner


def test_exact_missing_negative_tail_and_full13_partition():
    assert C['new_z_samples_a0']==[-12.0,-10.0,-8.0,-6.0]
    assert C['predecessor_z_samples_a0']==[-4.0,-2.0,0.0,2.0,4.0,6.0,8.0,10.0,12.0]
    assert C['full13_z_samples_a0']==C['new_z_samples_a0']+C['predecessor_z_samples_a0']
    assert len(set(C['full13_z_samples_a0']))==13


def test_claim_ceiling_stays_closed():
    assert C['continuous_trajectory_error_bound'] is False
    assert C['capture_execution_allowed'] is False
    assert C['production_admission']=='HOLD'
    assert C['all_bound']=='OPEN'
    assert C['b_grid']=='NO_GO'
    assert C['original_capture_gap_resolved'] is False


def test_no_legacy_import_and_no_old_suite_rerun():
    assert C['legacy_ring_task_import_allowed'] is False
    assert C['old_test_suite_reexecution'] is False
    assert C['new_tests_only'] is True


def test_backend_and_sector_are_frozen():
    assert C['cross_backend']=='EXACT_SP_MOMENTS_CXX_V1'
    assert C['qualification_sector']=='full'
    assert C['radial_spec']=={'radius':64.0,'elements':40,'degree':4,'lmax':1,'bound_nmax':2,'positive_per_l':1,'positive_emax':2.0,'quad_order':12,'grading':2.0}


def test_resolution_ladders_are_bounded():
    for key in ('reference_resolutions','candidate_resolutions'):
        rows=C[key]
        assert rows
        assert len({(r['order'],r['subdivisions']) for r in rows})==len(rows)
        assert all(2 <= r['order'] <= 64 for r in rows)
        assert all(r['subdivisions'] in (1,2,4) for r in rows)


def test_predecessor_hashes_are_exact_sha256():
    assert len(C['predecessor_return_report_sha256'])==64
    assert len(C['predecessor_return_archive_sha256'])==64
    int(C['predecessor_return_report_sha256'],16)
    int(C['predecessor_return_archive_sha256'],16)


def test_tp2b_selected_evidence_relation_uses_nested_schema():
    row={
        'candidate_reference_alias':False,
        'candidate_vs_reference':{
            'evidence_relation':'INDEPENDENT_NUMERICAL_TASK_COMPARISON'
        }
    }
    assert runner.predecessor_selected_relation(row)=='INDEPENDENT_NUMERICAL_TASK_COMPARISON'
    assert 'evidence_relation' not in row
