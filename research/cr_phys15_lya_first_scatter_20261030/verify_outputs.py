#!/usr/bin/env python3
"""Byte-precise regeneration check against committed expected result hashes."""
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify(path:Path):
 manifest=json.loads((ROOT/'EXPECTED_OUTPUT_SHA256.json').read_text())
 bad=[]
 for name,expected in manifest.items():
  f=path/name
  if not f.is_file() or sha(f)!=expected:bad.append(name)
 print(json.dumps({'expected':len(manifest),'matched':len(manifest)-len(bad),'bad':bad},indent=2))
 if bad:raise SystemExit(1)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--results',type=Path,default=ROOT/'results');args=p.parse_args();verify(args.results)
