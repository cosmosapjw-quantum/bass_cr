"""Budgeted reference tensor Gauss enclosure with explicit analytic remainder.

No difference between quadrature orders is used as an error bound. Uses the
unchanged certified Legendre-rule implementation and fixed-point arithmetic.
A returned cell enclosure is never mislabeled as a complete matrix certificate.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction as F
import time
from dyadic import I,ZERO,sym
from complex_box import C,ellipse_box
from quadrature import certified_rule,gauss_constant
from weak_kernel import kernel

@dataclass
class Budget:
    max_evaluations:int
    deadline:float|None=None
    evaluations:int=0
    def charge(self,n=1):
        if type(n) is not int or n<0 or self.evaluations+n>self.max_evaluations:raise RuntimeError('evaluation budget exhausted')
        if self.deadline is not None and time.monotonic()>self.deadline:raise TimeoutError('wall budget exhausted')
        self.evaluations+=n

def cell_enclosure(candidate,cell,ctx,entry,*,box=(F(0),F(1),F(0),F(1)),n=8,rho=F(2),budget=None):
    """entry=(left_mode,right_mode,left_m,right_m), values per reference cell."""
    if type(n) is not int or n<1 or n>128:raise ValueError('degree range 1..128')
    u0,u1,w0,w1=map(F,box)
    if not (0<=u0<u1<=1 and 0<=w0<w1<=1):raise ValueError('reference subcell outside unit square')
    if len(entry)!=4:raise ValueError('entry has four indices')
    hu=(u1-u0)/2;hw=(w1-w0)/2;uc=(u0+u1)/2;wc=(w0+w1)/2
    if budget is None:raise ValueError('explicit evaluation budget required')
    budget.charge(2)
    # Any possible r=0 pole is rejected here before Gaussian value evaluation.
    mu=kernel(candidate,cell,ctx,ellipse_box(uc,hu,rho),C(I.bounds(w0,w1)),*entry).upper()
    mw=kernel(candidate,cell,ctx,C(I.bounds(u0,u1)),ellipse_box(wc,hw,rho),*entry).upper()
    err={key:(mu[key]+mw[key])*(2*hu*hw*gauss_constant(n,rho)) for key in mu}
    nodes,weights,root_receipts=certified_rule(n)
    ans={key:C() for key in mu}
    for x,wx in zip(nodes,weights):
        for y,wy in zip(nodes,weights):
            budget.charge()
            p=kernel(candidate,cell,ctx,C(x*hu+uc),C(y*hw+wc),*entry).value()
            weight=wx*wy*(hu*hw)
            for key in ans:ans[key]=ans[key]+p[key]*weight
    numeric={key:C(v) for key,v in ans.items()}
    for key in ans:
        ans[key]=ans[key]+C(sym(err[key]),sym(err[key]))
    return {'values':ans,'numeric':numeric,'analytic_modulus_error':err,
            'analytic_sup_u':mu,'analytic_sup_w':mw,'degree':n,
            'rho':str(rho),'box':list(map(str,box)),'point_evaluations':n*n,
            'root_brackets':root_receipts,'entry':entry,'chart':cell.kind,
            'coverage':'ONE_CELL_ONE_ENTRY_ONLY'}

def scalar_dump(c):return {'real':c.re.dump(),'imag':c.im.dump()}

def dump_enclosure(result):
    out={k:v for k,v in result.items() if k not in ('values','numeric','analytic_modulus_error','analytic_sup_u','analytic_sup_w')}
    for k in ('values','numeric'):out[k]={s:scalar_dump(x) for s,x in result[k].items()}
    for k in ('analytic_modulus_error','analytic_sup_u','analytic_sup_w'):out[k]={s:x.dump() for s,x in result[k].items()}
    return out

def entry_enclosure(candidate,cells,ctx,entry,*,absolute_target,degree=32,rho=F(2),max_depth=6,budget=None,checkpoint=None):
    """Whole-cover single-entry reference. Failure never becomes a zero cell.

    A fixed degree and finite deterministic subdivision policy are part of the
    caller's sealed contract. This is not a high-performance native backend.
    """
    target=F(absolute_target)
    if target<=0 or not cells or max_depth<0:raise ValueError('positive target, nonempty cover and nonnegative depth required')
    if budget is None:raise ValueError('explicit budget required')
    acc=None;accepted=0;roots_done=0;records=[]
    allowance=target/(4*len(cells))
    for ci,cell in enumerate(cells):
        todo=[((F(0),F(1),F(0),F(1)),0,allowance)]
        while todo:
            box,depth,tol=todo.pop()
            try:
                r=cell_enclosure(candidate,cell,ctx,entry,box=box,n=degree,rho=rho,budget=budget)
                # For one cross entry, include K_TP and the reverse H_TP†.
                rad=sum((I(r['values'][k].re.radius())+I(r['values'][k].im.radius()) for k in ('K_TP','H_TP')),ZERO).abs_upper()
                ok=rad.hi<=I(tol).lo
            except ZeroDivisionError:
                r=None;ok=False
            if not ok:
                if depth>=max_depth:raise RuntimeError('unresolved cell width/pole at depth limit')
                a,b,c,d=box
                if b-a>=d-c:
                    m=(a+b)/2;boxes=((a,m,c,d),(m,b,c,d))
                else:
                    m=(c+d)/2;boxes=((a,b,c,m),(a,b,m,d))
                for sub in reversed(boxes):todo.append((sub,depth+1,tol/2))
                continue
            if acc is None:acc={k:C() for k in r['values']}
            for k in acc:acc[k]=acc[k]+r['values'][k]
            accepted+=1
            rec={'root_cell':ci,'depth':depth,'enclosure':dump_enclosure(r)}
            records.append(rec)
            if checkpoint is not None:checkpoint(rec)
        roots_done+=1
    radius=sum((I(acc[k].re.radius())+I(acc[k].im.radius()) for k in ('K_TP','H_TP')),ZERO).abs_upper()
    return {'values':acc,'radius_upper':radius,'target':str(target),'target_met':radius.hi<=I(target).lo,
            'coverage':'COMPLETE_COVER_SINGLE_ENTRY_NOT_FULL_MATRIX','root_cells':roots_done,
            'accepted_cells':accepted,'evaluations':budget.evaluations,'cell_records':records}
