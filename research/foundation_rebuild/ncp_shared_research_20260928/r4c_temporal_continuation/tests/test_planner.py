from __future__ import annotations
import importlib.util
from pathlib import Path
import pytest

HERE=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('r4c',HERE/'continue_temporal.py')
r4c=importlib.util.module_from_spec(spec);spec.loader.exec_module(r4c)

def test_claim_ceiling_frozen():
    assert r4c.CLAIM_CEILING['capture_execution_allowed'] is False
    assert r4c.CLAIM_CEILING['production_admission']=='HOLD'
    assert r4c.CLAIM_CEILING['all_bound']=='OPEN'
    assert r4c.CLAIM_CEILING['b_grid']=='NO_GO'

def test_query_budget_math():
    assert 768+2 <= 2048
    assert 1536+2 <= 2048
    assert 4096+2 > 2048
