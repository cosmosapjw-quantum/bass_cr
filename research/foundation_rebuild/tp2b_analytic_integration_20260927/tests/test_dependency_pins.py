from pathlib import Path
import json

HERE=Path(__file__).resolve().parents[1]
FND=HERE.parent


def test_tp2b_pins_runtime_code_not_superseded_tp2a_contract():
    deps=json.loads((HERE/'DEPENDENCY_PINS.json').read_text())
    by_path={row['path']:row['sha256'] for row in deps['files']}

    contract_path='research/foundation_rebuild/tp2a_reference_qualified_20260926/CONTRACT.json'
    runtime_path='research/foundation_rebuild/tp2a_reference_qualified_20260926/qualification_runtime.py'

    assert contract_path not in by_path
    upstream=json.loads((FND/'tp2a_reference_qualified_20260926'/'SOURCE_MANIFEST.json').read_text())
    assert by_path[runtime_path]==upstream['files']['qualification_runtime.py']


def test_tp2b_owns_the_resolution_contract_it_executes():
    contract=json.loads((HERE/'CONTRACT.json').read_text())
    assert contract['schema']=='BASS_TP2B_ANALYTIC_RESOLUTION_INTEGRATION_V1'
    assert contract['cross_backend']=='EXACT_SP_MOMENTS_CXX_V1'
    assert contract['qualification_sector']=='full'
    assert contract['legacy_ring_task_import_allowed'] is False
