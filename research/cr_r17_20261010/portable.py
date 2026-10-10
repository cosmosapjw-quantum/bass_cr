"""Git-only R17 reproduction: all exact numerical inputs are in one small file."""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal,localcontext
import argparse,hashlib,json,sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from causal_source import certify_source_goal,combine_time_source

def display(x):
    if isinstance(x,F):
        with localcontext() as c:
            c.prec=40;v=str(Decimal(x.numerator)/Decimal(x.denominator))
        return {'exact':str(x),'display':v}
    if isinstance(x,dict):return {k:display(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [display(v) for v in x]
    return x

def calculate():
    data=json.loads((ROOT/'inputs/R17_COMPACT_INPUT.json').read_text())
    args={k:F(v) for k,v in data['scalars'].items()}
    args['births']=[tuple(F(x) for x in r) for r in data['births']]
    result=certify_source_goal(**args)
    t=tuple(F(x) for x in data['time_interval']);oldS=F(data['old_source_radius'])
    S=result['source_tau_abs_upper'];combined=combine_time_source(t,S)
    return dict(task='BASS_CR_R17A_PORTABLE',source_tau_abs_upper=S,
        source_radius_reduction_fraction=1-S/oldS,new_total_interval=combined,
        total_width_reduction_fraction=1-(combined[1]-combined[0])/(t[1]-t[0]+2*oldS),
        parent_science_replayed=False,source_sign=None,physical='HOLD')

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--output',type=Path);v=a.parse_args()
    data=display(calculate());text=json.dumps(data,indent=2)+'\n'
    if v.output:
        if v.output.exists():raise FileExistsError('CREATE_ONLY_OUTPUT')
        v.output.parent.mkdir(parents=True,exist_ok=True);v.output.write_text(text)
    print(text)
