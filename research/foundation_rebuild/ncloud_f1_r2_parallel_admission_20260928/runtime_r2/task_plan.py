"""Plan exact independent operator tasks without changing F1 reducer order."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def task_id(context, time_hex, order, subdivisions, sector='full', consumer=None):
    """Consumer role deliberately has no part in scientific task identity."""
    del consumer
    if sector != 'full' or float.fromhex(time_hex).hex() != time_hex:
        raise ValueError('R2_TASK_IDENTITY_BLOCKED: noncanonical time or sector')
    if type(order) is not int or type(subdivisions) is not int:
        raise ValueError('R2_TASK_IDENTITY_BLOCKED: integer resolution required')
    key = {'engine_identity_sha256': context['engine_identity_sha256'],
           'historical_archive_sha256': context['historical_archive_sha256'],
           'time_hex': time_hex, 'order': order, 'subdivisions': subdivisions,
           'sector': sector}
    return hashlib.sha256(_canonical(key)).hexdigest()


def metric_times(speed, f1_contract):
    speed = float(speed)
    if not math.isfinite(speed) or speed <= 0:
        raise ValueError('R2_TASK_PLAN_BLOCKED: positive finite speed required')
    policy = f1_contract['parity_policy']
    epsilon_t = float(policy['epsilon_z_a0']) / speed
    result = []
    for z in policy['metric_connection_sentinels_z_a0']:
        t = float(z) / speed
        result.append(((t - epsilon_t).hex(), t.hex(), (t + epsilon_t).hex()))
    return tuple(result)


@dataclass(frozen=True)
class TaskPlan:
    tasks: tuple[dict, ...]
    representative_specs: int
    metric_specs: int
    consumer_task_ids: dict[str, tuple[str, ...]]


def plan_tasks(representatives, f1_contract, speed, engine_identity_sha256, archive_sha256):
    ladder = f1_contract['runtime_reference_resolutions']
    if len(ladder) != 11 and representatives.get('query_count') == 15:
        raise ValueError('R2_TASK_PLAN_BLOCKED: frozen ladder count drift')
    queries = representatives['queries']
    if len(queries) != representatives['query_count']:
        raise ValueError('R2_TASK_PLAN_BLOCKED: query count mismatch')
    context = {'engine_identity_sha256': engine_identity_sha256,
               'historical_archive_sha256': archive_sha256}
    by_id = {}
    consumers = {}
    def add(time_hex, role):
        ids = []
        for resolution in ladder:
            q, h = resolution['order'], resolution['subdivisions']
            identity = task_id(context, time_hex, q, h)
            by_id[identity] = {'task_id': identity, 'time_hex': time_hex,
                               'order': q, 'subdivisions': h, 'sector': 'full'}
            ids.append(identity)
        consumers[role] = tuple(ids)
    for query in queries:
        add(query['time_hex'], 'representative:' + query['query_id'])
    representative_specs = len(queries) * len(ladder)
    triples = metric_times(speed, f1_contract)
    for index, triple in enumerate(triples):
        for role, time_hex in zip(('minus', 'center', 'plus'), triple):
            add(time_hex, f'metric:{index}:{role}')
    return TaskPlan(tuple(by_id[key] for key in sorted(by_id)), representative_specs,
                    len(triples) * 3 * len(ladder), dict(sorted(consumers.items())))
