import json
from pathlib import Path

from research.foundation_rebuild.ncloud_f1_r2_parallel_admission_20260928.runtime_r2.task_plan import metric_times, plan_tasks, task_id


SIDE = Path(__file__).resolve().parents[3] / 'ncloud_f1_engine_admission_20260928'


def contracts():
    return (json.loads((SIDE / 'F1_REPRESENTATIVE_QUERIES.json').read_text()),
            json.loads((SIDE / 'F1_CONTRACT.json').read_text()))


def test_representative_task_count_165_and_exact_deduplication():
    reps, contract = contracts()
    plan = plan_tasks(reps, contract, 2.0, 'e' * 64, reps['source_archive_sha256'])
    assert plan.representative_specs == 165
    assert plan.metric_specs == 165
    assert len(plan.tasks) <= 330
    assert len({row['task_id'] for row in plan.tasks}) == len(plan.tasks)


def test_metric_times_match_old_f1_float_order():
    _, contract = contracts()
    triples = metric_times(2.0, contract)
    assert len(triples) == 5
    assert triples[2] == ((-0.00005).hex(), (0.0).hex(), (0.00005).hex())
    assert triples[0][1] == (-6.0).hex()


def test_task_identity_uses_numeric_context_and_ignores_consumer_role():
    context = {'engine_identity_sha256': 'e' * 64, 'historical_archive_sha256': 'a' * 64}
    baseline = task_id(context, '0x0.0p+0', 40, 1, consumer='representative')
    assert baseline == task_id(context, '0x0.0p+0', 40, 1, consumer='sentinel')
    for changed, time_hex, q, h in [({'engine_identity_sha256': 'f' * 64, 'historical_archive_sha256': 'a' * 64}, '0x0.0p+0', 40, 1),
                                     ({'engine_identity_sha256': 'e' * 64, 'historical_archive_sha256': 'b' * 64}, '0x0.0p+0', 40, 1),
                                     (context, '0x1.0000000000000p+0', 40, 1), (context, '0x0.0p+0', 48, 1),
                                     (context, '0x0.0p+0', 40, 2)]:
        assert baseline != task_id(changed, time_hex, q, h)


def test_plan_order_independent_of_representative_input_order():
    reps, contract = contracts()
    first = plan_tasks(reps, contract, 2.0, 'e' * 64, reps['source_archive_sha256'])
    reversed_reps = dict(reps, queries=list(reversed(reps['queries'])))
    second = plan_tasks(reversed_reps, contract, 2.0, 'e' * 64, reps['source_archive_sha256'])
    assert [x['task_id'] for x in first.tasks] == [x['task_id'] for x in second.tasks]
