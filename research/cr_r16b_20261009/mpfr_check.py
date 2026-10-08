"""Independent MPFR256 interval propagation; FT03 AD coefficients are shared."""
import argparse,json,time
from pathlib import Path
import gmpy2 as m

DOWN=m.context(precision=256,round=m.RoundDown);UP=m.context(precision=256,round=m.RoundUp)
def operation(context,fn):
    with m.context(context):return fn()
class I:
    def __init__(self,a=0,b=None):
        if isinstance(a,I):self.lo,self.hi=a.lo,a.hi;return
        aa=a if isinstance(a,m.mpfr) else str(a)
        bb=(a if b is None else b);bb=bb if isinstance(bb,m.mpfr) else str(bb)
        self.lo=operation(DOWN,lambda:m.mpfr(aa));self.hi=operation(UP,lambda:m.mpfr(bb))
        assert self.lo<=self.hi
    def __add__(self,b):
        b=I(b);return endpoints(operation(DOWN,lambda:self.lo+b.lo),operation(UP,lambda:self.hi+b.hi))
    __radd__=__add__
    def __neg__(self):return endpoints(operation(DOWN,lambda:-self.hi),operation(UP,lambda:-self.lo))
    def __sub__(self,b):return self+-I(b)
    def __mul__(self,b):
        b=I(b);pairs=[(x,y) for x in (self.lo,self.hi) for y in (b.lo,b.hi)]
        return endpoints(min(operation(DOWN,lambda:x*y) for x,y in pairs),max(operation(UP,lambda:x*y) for x,y in pairs))
    __rmul__=__mul__
    def mag(self):return max(operation(UP,lambda:abs(self.lo)),operation(UP,lambda:abs(self.hi)))
    def data(self):return [format(operation(DOWN,lambda:m.next_below(self.lo)),'.78g'),format(operation(UP,lambda:m.next_above(self.hi)),'.78g')]
def endpoints(a,b):
    v=object.__new__(I);v.lo,v.hi=a,b;assert a<=b;return v
def ssum(vals):return sum(vals,I(0))
def sym(a):return endpoints(operation(DOWN,lambda:-a),a)
def mv(A,v):return [ssum(a*b for a,b in zip(row,v)) for row in A]

def slab(A,g,start,d):
    M=[[a.mag() for a in row] for row in A]
    norm=max(ssum(I(a) for a in row).hi for row in M)
    q=(I(d)*I(norm)).hi;assert q<1
    v=[(I(d)*I((x+y).mag())).hi for x,y in zip(mv(A,start),g)];rho=list(v)
    for _ in range(8):
        v=[(I(d)*ssum(I(a)*I(b) for a,b in zip(row,v))).hi for row in M]
        rho=[(I(a)+I(b)).hi for a,b in zip(rho,v)]
    denominator=operation(DOWN,lambda:1-q)
    numerator=operation(UP,lambda:q*max(v))
    tail=operation(UP,lambda:numerator/denominator);rho=[(I(a)+I(tail)).hi for a in rho]
    tube=[a+sym(r) for a,r in zip(start,rho)]
    for _ in range(3):
        field=[a+b for a,b in zip(mv(A,tube),g)]
        new=[a+endpoints(min(m.mpfr(0),(I(d)*b).lo),max(m.mpfr(0),(I(d)*b).hi)) for a,b in zip(start,field)]
        tube=[endpoints(max(a.lo,b.lo),min(a.hi,b.hi)) for a,b in zip(tube,new)]
    finish=[a+I(d)*b for a,b in zip(start,[x+y for x,y in zip(mv(A,tube),g)])]
    return finish,tube

def run(prepared,out):
    started=time.monotonic();cells=[json.loads((prepared/f'cell_{i:02d}.json').read_text()) for i in range(32)]
    lam=[I(0)]*cells[-1]['dimension'];goal=I(0);rem=m.mpfr(0);birth=I(0);checks=[]
    for c in reversed(cells):
        for p in reversed(c['panels']):
            A=[[I(*v) for v in row] for row in p['Ahat']];At=list(map(list,zip(*A)))
            g=[I(*v) for v in p['goal']];r=[I(*v) for v in p['residual']];q=[I(v) for v in p['nonlinear_remainder_upper']];d=I(p['dt'])
            lam,tube=slab(At,g,lam,d)
            goal=goal-d*ssum(v*w for v,w in zip(tube,r))
            rem=(I(rem)+d*ssum(I(v.mag())*w for v,w in zip(tube,q))).hi
        if c['event_before']:
            ev=c['event_before'];birth=birth+ssum(a*I(*b) for a,b in zip(lam,ev['delta']));lam=lam[:ev['dimension_before']]
        checks.append({'cell':c['index'],'lambda_left':[x.data() for x in lam]})
    dual=goal+birth+sym(rem)
    # Independent forward interval propagation in a separate arithmetic backend.
    e=[I(0)]*cells[0]['dimension'];primal=I(0);primal_prefix=[]
    for c in cells:
        if c['event_before']:e.append(I(*c['event_before']['delta'][-1]))
        for p in c['panels']:
            A=[[I(*v) for v in row] for row in p['Ahat']];g=[I(*v) for v in p['goal']];r=[I(*v) for v in p['residual']]
            q=[I(v) for v in p['nonlinear_remainder_upper']];d=I(p['dt'])
            e,tube=slab(A,[-v+sym(w.hi) for v,w in zip(r,q)],e,d)
            primal=primal+d*ssum(a*b for a,b in zip(g,tube))
        primal_prefix.append({'cell':c['index'],'goal':primal.data()})
    assert max(dual.lo,primal.lo)<=min(dual.hi,primal.hi),'MPFR_PRIMAL_DUAL_DISJOINT'
    result={'status':'MPFR256_PRIMAL_DUAL_INTERVAL_CHECK_PASS','MPFR_version':m.mpfr_version(),'gmpy2_version':m.version(),
        'backward_signed_interval':dual.data(),'forward_signed_interval':primal.data(),'all_backward_boundaries':checks,
        'primal_prefix':primal_prefix,'shares_FT03_interval_AD_panels':True,'independent_propagation_arithmetic':True,
        'not_independent_RHS_backend':True,'MPFR_forward_boxes_relax_birth_correlations':'diagnostic cross-check; primary Decimal affine forward retains shared birth generators',
        'elapsed_s':time.monotonic()-started}
    with out.open('x') as f:f.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','backward_signed_interval','forward_signed_interval','elapsed_s')}),flush=True)

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--prepared',type=Path,required=True);a.add_argument('--output',type=Path,required=True)
    x=a.parse_args();run(x.prepared,x.output)
