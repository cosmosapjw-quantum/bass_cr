"""R16 exact rational global Fubini recomposition of the inherited R15 interval.

The result is conditional on inherited physical tube/interval proofs. This tool
only rearranges accepted residual/envelope bounds: it does not refine signed
Jacobian information or repeat the donor proof.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
from zipfile import ZipFile
import argparse,hashlib,json,math

R14_SHA='afac64fea33ac53dd4aac537a80cfc4e7917bb1447057aef67803afcca9d0f36'
REI_SHA='a3971b386edb9dc585b8657ea095ab171159b7881a52a59f574d0ef694538b48'

def frac(v):
    if isinstance(v,dict):return F(int(v['num']),int(v['den']))
    return F(v)
def box(v):return tuple(map(frac,v))
def plus(x,y):return x[0]+y[0],x[1]+y[1]
def minus(x):return -x[1],-x[0]
def times(x,y):
    a=[v*w for v in x for w in y]
    return min(a),max(a)
def scale(x,s):return (x[0]*s,x[1]*s) if s>=0 else (x[1]*s,x[0]*s)
def sum_boxes(arr):
    x=F(0),F(0)
    for el in arr:x=plus(x,el)
    return x

def exp_moment(alpha,order):
    return sum(((-alpha)**k/F(math.factorial(k)*(k+1)) for k in range(order+1)),F(0))

def exact_binary(v):return F.from_float(float(v))

def verify_native_history(contents:str) -> dict:
    rec=[json.loads(x) for x in contents.splitlines()]
    pts={r['index']:r for r in rec if r.get('kind')=='point' and r.get('variant')==0}
    roots={r['index']:r for r in rec if r.get('kind')=='root'}
    if set(pts)!=set(range(32)) or set(roots)!=set(range(32)):
        raise ValueError('NONCANONICAL_NATIVE_SEQUENCE')
    births=[]
    for i in range(1,32):
        a=pts[i-1]['gas']+pts[i-1]['p1'];b=pts[i]['old']+pts[i]['p0'][:len(pts[i-1]['p1'])]
        if len(b)!=len(a) or any(exact_binary(x)!=exact_binary(y) for x,y in zip(a,b)):
            raise ValueError('NATIVE_INTERFACE_MISMATCH')
        if roots[i]['t0']!=roots[i-1]['t1']:
            raise ValueError('NATIVE_CLOCK_MISMATCH')
        if len(pts[i]['p0'])>len(pts[i-1]['p1']):
            if len(pts[i]['p0'])!=len(pts[i-1]['p1'])+1:
                raise ValueError('COHORT_DIMENSION')
            births.append(i)
    if births!=[4,8,12,16,20,24]:raise ValueError('BIRTH_LIST')
    return {'cells':32,'gas_and_old_cohort_interface_exact':True,'birth_indices':births}

def compute(parent_root:Path):
    parent_root=Path(parent_root)
    root=parent_root/'source/research/cr_xthread_r15_20261008'
    recs=json.loads((root/'results/run_v1/CELL_RESULTS.json').read_text())
    old=json.loads((root/'results/run_v1/RESULTS.json').read_text())
    if len(recs)!=32:raise ValueError('CELL_COUNT')
    p14=parent_root/'inputs/BASS_CR_XTHREAD_R14_20261008_v1.zip'
    prei=parent_root/'inputs/REI_XTHREAD_BRIDGE13_20261008.zip'
    for path,hashval in ((p14,R14_SHA),(prei,REI_SHA)):
        if hashlib.sha256(path.read_bytes()).hexdigest()!=hashval:
            raise ValueError('SHA256_MISMATCH')
    with ZipFile(p14) as z:
        assert z.testzip() is None
        first=json.loads(z.read('CR_XTHREAD_R14_20261008/inputs/rei_bridge12_20261008/results/final_verified/interval/RESIDUAL_SLICES.json'))
        cert=json.loads(z.read('CR_XTHREAD_R14_20261008/inputs/rei_bridge12_20261008/results/final_verified/interval/CELL_CERTIFICATE.json'))
        r14=json.loads(z.read('CR_XTHREAD_R14_20261008/results/GOAL.json'))
    with ZipFile(prei) as z:
        assert z.testzip() is None
        native=verify_native_history(z.read('rei_bridge13_20261008/inputs/BRIDGE11_NATIVE.jsonl').decode())
    fhe=frac(r14['constants']['f_he'])
    c=[F(1),fhe,2*fhe]
    mass=[];rs=[];remainders=[];cp=[]
    for i,cell in enumerate(recs):
        if i:
            alpha=frac(cell['alpha']);d=box(cell['density_factor']);sc=frac(cell['scale'])
            mass.append(times(scale(d,sc),(exp_moment(alpha,5),exp_moment(alpha,6))))
            ps=cell['residual_panels'];coupling=cell['duhamel_feedback_upper_scaled']
        else:
            mass.append((F(0),F(0)))
            ps=first;coupling=cert['duhamel_coupling_remainder_upper_scaled']
        r=(F(0),F(0));previous=F(0)
        for item in ps:
            a,b=box(item['s'])
            if a!=previous or b<=a:raise ValueError('NONCONTIGUOUS_RESIDUAL_PANELS')
            rb=[box(x) for x in item['residual'][:3]]
            tr=(sum(c[j]*rb[j][0] for j in range(3)),sum(c[j]*rb[j][1] for j in range(3)))
            r=plus(r,scale(tr,b-a));previous=b
        if previous!=1:raise ValueError('INCOMPLETE_RESIDUAL_COVERAGE')
        rs.append(r)
        cp.append(sum(c[j]*frac(coupling[j]) for j in range(3)))
        remainders.append(frac(cell['remainder']))
    # At each cell i, W_later(T_i_end) is the mass of all *future* cells.
    future=[(F(0),F(0)) for _ in recs]
    rest=F(0),F(0)
    for i in reversed(range(32)):
        future[i]=rest
        rest=plus(rest,mass[i])
    local=sum_boxes(box(x['forcing']) for x in recs)
    future_direct=sum_boxes(times(minus(r),m) for r,m in zip(rs,future))
    direct=plus(local,future_direct)
    local_fb=sum(remainders,F(0))
    future_fb=sum(future[i][1]*cp[i] for i in range(32))
    bound=local_fb+future_fb
    assert bound>=0
    new=(direct[0]-bound,direct[1]+bound)
    prior=box(old['signed_tau_difference_interval'])
    intersection=max(prior[0],new[0]),min(prior[1],new[1])
    if intersection[0]>intersection[1]:raise AssertionError('EMPTY_OLD_NEW_INTERSECTION')
    return dict(native=native,interval=tuple(new),old_interval=prior,local_direct=local,
        global_future_direct=future_direct,global_direct=direct,
        local_feedback=local_fb,future_feedback=future_fb,feedback_bound=bound,
        intersection=intersection,
        endpoint_difference=(new[0]-prior[0],new[1]-prior[1]),
        global_strict_sign_positive=new[0]>0,panels=sum(64 if i==0 else 16 for i in range(32)),
        claim='SAME_INPUT_CONDITIONAL_INTERVAL_RECOMPOSITION; NOT A NEW SCIENTIFIC PROOF')

def display(x):
    if isinstance(x,F):return {'num':str(x.numerator),'den':str(x.denominator),'float':float(x)}
    if isinstance(x,(list,tuple)):return [display(i) for i in x]
    if isinstance(x,dict):return {k:display(v) for k,v in x.items()}
    return x

if __name__=='__main__':
    cli=argparse.ArgumentParser();cli.add_argument('--parent',type=Path,required=True);cli.add_argument('--output',type=Path,required=True)
    args=cli.parse_args();out=compute(args.parent)
    if args.output.exists():raise FileExistsError('CREATE_ONLY_OUTPUT')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(display(out),indent=2)+'\n')
    print(json.dumps({k:display(out[k]) for k in ['interval','old_interval','endpoint_difference','global_strict_sign_positive','panels']},indent=2))
