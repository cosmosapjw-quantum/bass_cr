"""Exact event correction for the unchanged R9 four-node cubic readout.

This is conditional error transport, not a certificate of supplied trajectories.
Error convention: exact integral minus quadrature. Jumps are right minus left
traces of the specified derivative with respect to the declared integration
coordinate. Isolated value jumps at quadrature nodes require a trace convention.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction as F
from math import comb,factorial
from typing import Sequence
from cubic_readout import panel,exact,ReadoutError,MissingPremise

Interval=tuple[F,F]

def checked_box(box: Interval) -> Interval:
    if len(box)!=2 or any(type(x) is not F for x in box) or box[0]>box[1]:
        raise ReadoutError('ORDERED_FRACTION_INTERVAL_REQUIRED')
    return box

def product(a:Interval,b:Interval)->Interval:
    checked_box(a);checked_box(b)
    v=[x*y for x in a for y in b]
    return min(v),max(v)

def _order(order:int)->None:
    if type(order) is not int or not 0<=order<=3:
        raise ReadoutError('JUMP_ORDER_MUST_BE_0_TO_3')

@dataclass(frozen=True)
class Jump:
    order:int
    location:Interval
    amplitude:Interval
    node_trace:str|None=None
    identity:str='external-premise'

    def validate(self)->None:
        _order(self.order);checked_box(self.location);checked_box(self.amplitude)
        if self.node_trace not in (None,'left','right'):
            raise ReadoutError('TRACE_MUST_BE_LEFT_OR_RIGHT')
        if not isinstance(self.identity,str) or not self.identity:
            raise ReadoutError('EVENT_IDENTITY_REQUIRED')

def kernel(nodes:Sequence[F],order:int,location:F,*,node_trace:str|None=None)->F:
    """L[(x-location)_+**order/order!], with explicit H(0) for order zero."""
    _order(order);p=panel(tuple(nodes))
    if type(location) is not F or not p.nodes[0]<=location<=p.nodes[-1]:
        raise ReadoutError('EVENT_NOT_IN_PANEL')
    if node_trace not in (None,'left','right'):
        raise ReadoutError('TRACE_MUST_BE_LEFT_OR_RIGHT')
    result=(p.nodes[-1]-location)**(order+1)/factorial(order+1)
    for x,w in zip(p.nodes,p.weights):
        if x>location:
            result-=w*(x-location)**order/factorial(order)
        elif x==location and order==0:
            if node_trace is None:
                raise MissingPremise('VALUE_JUMP_AT_NODE_REQUIRES_TRACE')
            if node_trace=='right':result-=w
    return result

def _power_linear(a:F,b:F,n:int)->tuple[F,...]:
    return tuple(F(comb(n,k))*a**(n-k)*b**k for k in range(n+1))

def _branch_coefficients(nodes:tuple[F,...],order:int,left:F,right:F)->tuple[F,...]:
    """Polynomial kernel at t=left+(right-left)*u in a node-free open branch."""
    p=panel(nodes);h=right-left;mid=(left+right)/2
    out=list(v/factorial(order+1) for v in _power_linear(p.nodes[-1]-left,-h,order+1))
    for x,w in zip(p.nodes,p.weights):
        if x>mid:
            for j,v in enumerate(_power_linear(x-left,-h,order)):
                out[j]-=w*v/factorial(order)
    return tuple(out)

def kernel_range(nodes:Sequence[F],order:int,location:Interval,*,node_trace:str|None=None)->Interval:
    """Rigorous rational Bernstein enclosure for an uncertain event location.

    Subdivide at actual quadrature nodes. For a value jump straddling a node,
    both one-sided limits are included rather than selecting an unknown trace.
    """
    _order(order);p=panel(tuple(nodes));lo,hi=checked_box(location)
    if lo<p.nodes[0] or hi>p.nodes[-1]:raise ReadoutError('EVENT_BOX_NOT_IN_PANEL')
    if lo==hi:
        v=kernel(p.nodes,order,lo,node_trace=node_trace);return v,v
    breaks=sorted(set([lo,hi]+[x for x in p.nodes if lo<x<hi]))
    bounds=[]
    for left,right in zip(breaks,breaks[1:]):
        a=_branch_coefficients(p.nodes,order,left,right);n=len(a)-1
        b=[sum((a[i]*F(comb(k,i),comb(n,i)) for i in range(k+1)),F(0)) for k in range(n+1)]
        bounds.extend(b)
    for t in breaks:
        if order==0 and t in p.nodes:
            bounds.extend(kernel(p.nodes,order,t,node_trace=s) for s in ['left','right'])
        else:bounds.append(kernel(p.nodes,order,t,node_trace=node_trace))
    return min(bounds),max(bounds)

def corrected_panel(nodes:Sequence[F],values:Sequence[F],node_errors:Sequence[F]|None,
                    regular_fourth_bound:F|None,events:Sequence[Jump]|None,*,
                    complete_events:bool=False,piecewise_regular:bool=False)->dict:
    """Enclose integral from node errors, smooth remainder, and all derivative jumps.

    The caller asserts: on each interval between supplied events, the target has
    bounded fourth derivative; one-sided jets through order three exist; there
    are no omitted jumps. Subtracting the jump polynomials gives a W^{4,infty}
    function. The unchanged R9 Lagrange absolute kernel is a safe smooth bound.
    Event uncertainty can cover any subset of THIS panel. Uncertain events that
    cross panel boundaries must be split/handled by a composite caller, not
    rounded into one panel. No missing amplitude is silently set to zero.
    """
    if (node_errors is None or regular_fourth_bound is None or events is None
            or not complete_events or not piecewise_regular):
        raise MissingPremise('NODE_REGULAR_DERIVATIVE_AND_COMPLETE_EVENT_PREMISES_REQUIRED')
    p=panel(tuple(nodes));v=exact(values);e=exact(node_errors)
    if len(v)!=4 or len(e)!=4 or any(x<0 for x in e):raise ReadoutError('FOUR_VALUES_AND_NONNEGATIVE_NODE_ERRORS_REQUIRED')
    if type(regular_fourth_bound) is not F or regular_fourth_bound<0:
        raise ReadoutError('NONNEGATIVE_FRACTION_REGULAR_BOUND_REQUIRED')
    q=sum((x*y for x,y in zip(p.weights,v)),F(0));cl=F(0);cu=F(0);terms=[]
    seen=set()
    for event in events:
        if not isinstance(event,Jump):raise ReadoutError('JUMP_OBJECT_REQUIRED')
        event.validate()
        key=(event.identity,event.order)
        if key in seen:raise ReadoutError('DUPLICATE_EVENT_DERIVATIVE')
        seen.add(key)
        k=kernel_range(p.nodes,event.order,event.location,node_trace=event.node_trace)
        t=product(k,event.amplitude);cl+=t[0];cu+=t[1]
        terms.append({'identity':event.identity,'order':event.order,'kernel':k,'contribution':t})
    node_r=sum((abs(w)*x for w,x in zip(p.weights,e)),F(0))
    smooth_r=p.remainder_kernel_abs*regular_fourth_bound
    r=node_r+smooth_r
    return {'quadrature':q,'jump_correction':(cl,cu),'node_radius':node_r,'regular_radius':smooth_r,
        'interval':(q+cl-r,q+cu+r),'events':terms,
        'status':'CONDITIONAL_ON_SUPPLIED_PIECEWISE_TARGET_PREMISES'}
