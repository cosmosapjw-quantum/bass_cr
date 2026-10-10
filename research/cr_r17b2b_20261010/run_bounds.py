import sys,json,argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT/'src'))
from homotopy import compute
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--output',type=Path,required=True);x=a.parse_args();r=compute()
 with x.output.open('x') as f:f.write(json.dumps(r,indent=2)+'\n')
 print(json.dumps({k:r[k] for k in ['status','q_contraction','source_signed_interval_candidate','source_nonlinearity_nominal_tangent_remainder_radius','narrower_than_fallback']}))
