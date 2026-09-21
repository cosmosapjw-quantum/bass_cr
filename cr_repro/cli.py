from __future__ import annotations
from pathlib import Path
import argparse,json
from .tdl import TDLRunner
from .aocc import OneElectronAOCC
from .util import atomic_json

def main():
 p=argparse.ArgumentParser(); sub=p.add_subparsers(dest='cmd',required=True)
 a=sub.add_parser('tdl'); a.add_argument('--config',required=True); a.add_argument('--out',required=True); a.add_argument('--max-steps',type=int)
 b=sub.add_parser('aocc'); b.add_argument('--config',required=True); b.add_argument('--out',required=True)
 ns=p.parse_args(); cfg=json.loads(Path(ns.config).read_text())
 if ns.cmd=='tdl': r=TDLRunner(cfg).run(ns.out,ns.max_steps)
 else:
  r=OneElectronAOCC(cfg).run(); Path(ns.out).mkdir(parents=True,exist_ok=True); atomic_json(Path(ns.out)/'result.json',r)
 print(json.dumps(r,indent=2))
if __name__=='__main__': main()
