"""Isolated child entry point. Use supervise_g03.py for process-group teardown."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import argparse,json
from g03_executor import request


def main():
    p=argparse.ArgumentParser(description=__doc__,allow_abbrev=False)
    for name in ('proposal','source-pins','inputs','build','out','approved-proposal-sha256'):p.add_argument('--'+name,required=True)
    a=p.parse_args()
    try:
        result=request(a.proposal,a.source_pins,a.inputs,a.build,a.out,approved_sha=a.approved_proposal_sha256)
        print(json.dumps(result));return 0
    except BaseException as exc:
        print(json.dumps({'status':'G03_SIGNED48_EXECUTION_BLOCKED','type':type(exc).__name__,'message':str(exc)}));return 2


if __name__=='__main__':raise SystemExit(main())
