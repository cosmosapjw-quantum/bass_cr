"""CLI entry point; science requires externally pinned one-shot approval."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import argparse,json
from static_tail import request,write_new,BINDING,GlobalBudget

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__,allow_abbrev=False)
    for name in ('proposal','source-pins','inputs','build','out'):p.add_argument('--'+name,required=True)
    p.add_argument('--approved-proposal-sha256',default='')
    p.add_argument('--preflight-only',action='store_true')
    a=p.parse_args(argv)
    try:
        result=request(a.proposal,a.source_pins,a.inputs,a.build,a.out,approved_sha=a.approved_proposal_sha256,preflight_only=a.preflight_only)
        print(json.dumps(result,sort_keys=True));return 0
    except Exception as exc:
        output=Path(a.out)
        if output.is_dir():
            if not (output/'FIRST_FAILURE.json').exists():write_new(output/'FIRST_FAILURE.json',{'type':type(exc).__name__,'message':str(exc)})
            if not (output/'RETURN_REPORT.json').exists():
                used=GlobalBudget(output/'GLOBAL_BUDGET').used() if (output/'GLOBAL_BUDGET/SEED.json').exists() else 0
                write_new(output/'RETURN_REPORT.json',{'status':'R4P0_B0_STATIC_EXECUTION_BLOCKED','new_native_operator_evaluations':used,
                    'new_authorization_consumed':int((output/'AUTHORIZATION_CONSUMED.json').exists()),'claim_ceiling':BINDING['claim_ceiling']})
        else:
            blocker=output.with_name(output.name+'_BLOCKER.json')
            if not blocker.exists():write_new(blocker,{'status':'R4P0_B0_STATIC_EXECUTION_BLOCKED','type':type(exc).__name__,'message':str(exc),'new_native_operator_evaluations':0,'new_authorization_consumed':0})
        print(json.dumps({'status':'R4P0_B0_STATIC_EXECUTION_BLOCKED','type':type(exc).__name__,'message':str(exc)}));return 2

if __name__=='__main__':raise SystemExit(main())
