"""Exact, read-only task cache adapter for the unchanged F1 reducer."""
from .task_plan import task_id


def cached_evaluator(store, context):
    if dict(context) != store.context:
        raise ValueError('R2_CACHE_CONTEXT_BLOCKED: store context mismatch')

    def evaluate(t, order, subdivisions):
        time_hex = float(t).hex()
        spec = {'time_hex': time_hex, 'order': int(order),
                'subdivisions': int(subdivisions), 'sector': 'full'}
        spec['task_id'] = task_id(context, time_hex, spec['order'], spec['subdivisions'])
        return store.load(spec)

    return evaluate
