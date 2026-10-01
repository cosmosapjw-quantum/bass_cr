"""G02-specific spawn admission; unchanged numerical worker after exact checks."""
from fd_executor import verify_source,verify_inputs,exact_items,verify_budget,GlobalBudget
import worker_runtime
_STATE_ITEMS=None


def initialize(inputs,build,pins,out,budget_dir,cpus,ram):
    global _STATE_ITEMS
    verify_budget(GlobalBudget(budget_dir),len(cpus))
    verify_source(pins)
    contract,plan,native=verify_inputs(inputs,build)
    if native!=pins['native']:raise ValueError('worker native receipt mismatch')
    _STATE_ITEMS={x.query_id:x for x in exact_items(plan)}
    worker_runtime.initialize_worker(inputs,build,contract,plan['context_id'],budget_dir,out+'/worker_tasks',cpus,ram)


def compute(item):
    if _STATE_ITEMS is None or _STATE_ITEMS.get(item.query_id)!=item:
        raise ValueError('unexpected G02 query ID/time before native worker')
    return worker_runtime.compute_query(item)
