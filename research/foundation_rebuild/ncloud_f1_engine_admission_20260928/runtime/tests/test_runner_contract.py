import json
import subprocess
import sys
from pathlib import Path

import pytest

from research.foundation_rebuild.ncloud_f1_engine_admission_20260928.runtime.run_f1_engine_admission import check_authorization, main


def authorization(tmp_path, **changes):
    d = {'schema': 'BASS_NCLOUD_F1_RUN_AUTHORIZATION_V1', 'implementation_commit': 'a' * 40,
         'implementation_tree': 'b' * 40, 'native_admission_allowed': True,
         'max_wall_seconds': 60, 'spending_limit_krw': 0, 'prepaid_host_approved': False}
    d.update(changes)
    p = tmp_path / 'synthetic_authorization_fixture.json'
    p.write_text(json.dumps(d))
    return p


def test_missing_authorization_blocks_before_science(tmp_path):
    with pytest.raises(Exception, match='F1_EXECUTION_NOT_AUTHORIZED'):
        check_authorization(tmp_path / 'missing.json', 'a' * 40, 'b' * 40)


@pytest.mark.parametrize('changes', [
    {'implementation_commit': 'c' * 40}, {'implementation_tree': 'd' * 40},
    {'native_admission_allowed': False}, {'max_wall_seconds': 0},
    {'spending_limit_krw': None, 'prepaid_host_approved': False},
    {'spending_limit_krw': -1}, {'schema': 'wrong'},
])
def test_invalid_authorization_blocks_before_science(tmp_path, changes):
    with pytest.raises(Exception, match='F1_EXECUTION_NOT_AUTHORIZED'):
        check_authorization(authorization(tmp_path, **changes), 'a' * 40, 'b' * 40)


def test_valid_synthetic_authorization_shape_is_accepted(tmp_path):
    assert check_authorization(authorization(tmp_path), 'a' * 40, 'b' * 40)['max_wall_seconds'] == 60


def test_cli_help_is_import_safe():
    script = Path(__file__).resolve().parents[1] / 'run_f1_engine_admission.py'
    p = subprocess.run([sys.executable, str(script), '--help'], capture_output=True, text=True)
    assert p.returncode == 0 and '--authorization' in p.stdout


def test_cli_without_authorization_never_claims_admission_pass(tmp_path):
    out = tmp_path / 'out'
    rc = main(['--out', str(out)])
    assert rc != 0
    if (out / 'RETURN_REPORT.json').exists():
        assert json.loads((out / 'RETURN_REPORT.json').read_text())['status'] != 'F1_ENGINE_ADMISSION_PASS'
    assert not (out / 'libmoments.so').exists()


def test_output_collision_preserves_existing_bytes(tmp_path):
    out = tmp_path / 'out'
    out.mkdir()
    marker = out / 'marker'
    marker.write_bytes(b'original')
    assert main(['--out', str(out)]) != 0
    assert marker.read_bytes() == b'original'


def test_f0_durable_gate_reads_published_repository_evidence():
    from research.foundation_rebuild.ncloud_f1_engine_admission_20260928.runtime.run_f1_engine_admission import verify_f0_durable, REPO
    evidence = verify_f0_durable(REPO)
    assert evidence['status'] == 'F0_DURABLE_CLOSED'
    assert evidence['scientific_status'] == 'TP2E_CACHE_ONLY_M4_COMPARISON_PASS'


def test_authorized_dispatch_uses_exact_commit_and_tree_without_native_work(tmp_path, monkeypatch):
    import research.foundation_rebuild.ncloud_f1_engine_admission_20260928.runtime.run_f1_engine_admission as runner
    head, tree = runner._identity()
    auth = authorization(tmp_path, implementation_commit=head, implementation_tree=tree)
    called = []
    def fake_execute(args, out, actual_head, actual_tree, approved):
        called.append((out, actual_head, actual_tree, approved['max_wall_seconds']))
        return 0
    monkeypatch.setattr(runner, 'execute_authorized', fake_execute)
    out = tmp_path / 'fresh'
    assert runner.main(['--authorization', str(auth), '--out', str(out)]) == 0
    assert called == [(out, head, tree, 60)]


def test_authorized_bad_archive_stops_before_build_and_never_claims_pass(tmp_path):
    from types import SimpleNamespace
    from research.foundation_rebuild.ncloud_f1_engine_admission_20260928.runtime.run_f1_engine_admission import execute_authorized
    bad_archive = tmp_path / 'bad_archive.zip'
    bad_archive.write_bytes(b'wrong archive')
    out = tmp_path / 'execution'
    approved = {'max_wall_seconds': 60, 'spending_limit_krw': 0}
    rc = execute_authorized(SimpleNamespace(archive=str(bad_archive)), out, 'a' * 40, 'b' * 40, approved)
    assert rc != 0
    report = json.loads((out / 'RETURN_REPORT.json').read_text())
    assert report['status'] == 'F1_INPUT_IDENTITY_BLOCKED'
    assert 'archive SHA/size mismatch' in report['first_failure']
    assert report['scientific_execution_performed'] is False
    assert not (out / 'engine').exists()


def test_infinite_cost_budget_rejected(tmp_path):
    with pytest.raises(Exception, match='F1_EXECUTION_NOT_AUTHORIZED'):
        check_authorization(authorization(tmp_path, spending_limit_krw=float('inf')), 'a' * 40, 'b' * 40)
