"""Create-only CLI for the count-only discrete model reference."""
import argparse,json,sys
from pathlib import Path
from .provider import evaluate_count
from .core import ContractError

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True);p.add_argument('--source-sha256',required=True)
    p.add_argument('--event',type=Path,required=True);p.add_argument('--event-sha256',required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    try:
        result=evaluate_count(a.source.read_bytes(),a.source_sha256,a.event.read_bytes(),a.event_sha256)
        with a.output.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2);f.write('\n')
    except (ContractError,OSError) as e:
        print(json.dumps({'status':'REJECTED','reason':str(e)}),file=sys.stderr);return 2
    print(json.dumps({'status':'MODEL_REFERENCE_WRITTEN','output':str(a.output),'physical_admission':False}));return 0
if __name__=='__main__':raise SystemExit(main())
