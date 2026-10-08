"""Plan, validate and execute an identity-bound cache-only midpoint candidate."""
from pathlib import Path
import argparse
import json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import numpy as np
import bootstrap_runtime
from execution_admission import strict_json
from solver_plan import make_plan
from qualified_cache import QualifiedCache
from checkpoint_solver import run_cached,write_new

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__,allow_abbrev=False)
    subs=parser.add_subparsers(dest='command',required=True)
    p=subs.add_parser('plan',allow_abbrev=False)
    p.add_argument('--t0',type=float,required=True);p.add_argument('--tf',type=float,required=True)
    p.add_argument('--nstep',type=int,required=True);p.add_argument('--context-id',required=True)
    p.add_argument('--qualification-contract',required=True);p.add_argument('--selected-indices',required=True)
    p.add_argument('--out',required=True)
    p=subs.add_parser('verify-cache',allow_abbrev=False)
    p.add_argument('--plan',required=True);p.add_argument('--cache-dir',required=True)
    p=subs.add_parser('propagate',allow_abbrev=False)
    p.add_argument('--plan',required=True);p.add_argument('--cache-dir',required=True)
    p.add_argument('--initial-state',required=True);p.add_argument('--state-key',default='initial_state')
    p.add_argument('--out',required=True);p.add_argument('--resume-from');p.add_argument('--stop-after-steps',type=int)
    a=parser.parse_args(argv)
    if a.command=='plan':
        plan=make_plan(a.t0,a.tf,a.nstep,a.context_id,qualification_contract=strict_json(a.qualification_contract),
                       selected_indices=[int(x) for x in a.selected_indices.split(',')])
        write_new(Path(a.out),plan);result={'plan_sha256':plan['plan_sha256'],'unique_queries':len(plan['queries'])}
    elif a.command=='verify-cache':
        cache=QualifiedCache(a.cache_dir,strict_json(a.plan))
        result={'status':'EXACT_QUALIFIED_CACHE_COMPLETE','manifest_sha256':cache.manifest_sha256,
                'queries':len(cache.records),'new_native_operator_calls':0}
    else:
        with np.load(a.initial_state,allow_pickle=False) as payload:
            c0=np.array(payload[a.state_key])
        result=run_cached(strict_json(a.plan),a.cache_dir,a.out,c0,
                          resume_from=a.resume_from,stop_after_steps=a.stop_after_steps)
    print(json.dumps(result,indent=2,allow_nan=False))
    return 0

if __name__=='__main__':raise SystemExit(main())
