"""Spawn initializer/whitelist wrapper around the unchanged R4F worker."""
import bootstrap_tail
from static_tail import verify_source,verify_inputs,exact_items,binding_plan
import worker_runtime
_STATE_ITEMS=None

def initialize(inputs,build,pins,out,budget_dir,cpus,ram):
    global _STATE_ITEMS
    verify_source(pins)
    contract,plan,native=verify_inputs(inputs,build)
    _STATE_ITEMS={x.query_id:x for x in exact_items(plan)}
    worker_runtime.initialize_worker(inputs,build,contract,plan['context_id'],budget_dir,out+'/worker_tasks',cpus,ram)

def compute(item):
    if _STATE_ITEMS is None or _STATE_ITEMS.get(item.query_id)!=item:raise ValueError('unexpected static-tail query ID/time')
    return worker_runtime.compute_query(item)
