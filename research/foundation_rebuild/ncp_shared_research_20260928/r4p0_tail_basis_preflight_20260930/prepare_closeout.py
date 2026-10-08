"""Preparation-only CLI; no native execution or authorization consumption."""
import argparse
import json
from preflight import HERE,prepare

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__,allow_abbrev=False)
    parser.add_argument('--inputs',default=str(HERE/'inputs'))
    parser.add_argument('--out',required=True)
    args=parser.parse_args(argv)
    print(json.dumps(prepare(args.inputs,args.out),sort_keys=True))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
