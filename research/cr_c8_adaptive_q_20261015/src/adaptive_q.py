"""Oracle-backed adaptive q-energy support with shape-free reaction bounds.

Frozen current gas/proper-time and one ray only. Does NOT infer child mass/mean
from parent N,U, nor recover missing spectral information. True child dyadic
packet moments are supplied by a separate positive source-oracle/packet ledger.
Geometry R, angular Jacobian, emission clock and source identity remain external.

Certified scope: conditional on the original moment_envelopes.ShapeFreeTemplate
outer evaluation at true child moments/support; all internal partition sums use
exact rational arithmetic on stored binary64 input. Independent child constraints
imply nested analytic feasible moment sets. We intersect global outer bounds
with previous bounds to preserve nesting in binary64 output.
"""
from __future__ import annotations
from bisect import bisect_left
from dataclasses import dataclass
from fractions import Fraction
from heapq import heappop, heappush
from math import isfinite, log, nextafter, inf, sqrt
from typing import Sequence
import numpy as np
from moment_envelopes import cached_template

FIT_CUTOFFS=(13.6,24.59,54.42)


def F(x):
    if isinstance(x,Fraction):return x
    v=float(x)
    if not isfinite(v):raise ValueError('finite dyadic expected')
    return Fraction.from_float(v)


class PositivePacketOracle:
    """Sorted packet distribution treated as the exact stored-dyadic measure.

    This oracle represents an *additional* piece of input evidence, not a
    property of the parent q-grid N,U alone.
    """
    def __init__(self,reference_energies,photons_per_h,source_id:str,ray_id:str,proper_epoch_s:float):
        es=np.asarray(reference_energies,float);ww=np.asarray(photons_per_h,float)
        if es.ndim!=1 or ww.ndim!=1 or len(es)!=len(ww) or not len(es):
            raise ValueError('positive packet measure required')
        if not np.all(np.isfinite(es)) or not np.all(np.isfinite(ww)) or np.any(es<=0) or np.any(ww<0):
            raise ValueError('invalid positive photon packet')
        if not source_id or not ray_id or not isfinite(proper_epoch_s):
            raise ValueError('physical packet provenance required')
        order=np.argsort(es,kind='stable')
        self.energies=[F(x) for x in es[order]]
        self.counts=[F(x) for x in ww[order]]
        self.source_id=str(source_id);self.ray_id=str(ray_id);self.proper_epoch_s=float(proper_epoch_s)
        self.prefix_n=[Fraction(0)];self.prefix_u=[Fraction(0)]
        for e,n in zip(self.energies,self.counts):
            self.prefix_n.append(self.prefix_n[-1]+n)
            self.prefix_u.append(self.prefix_u[-1]+e*n)
        self.total_n=self.prefix_n[-1];self.total_u=self.prefix_u[-1]

    def moments(self,a,b,closed_right:bool=False):
        """Half-open q-cell, except last inclusive; exact arithmetic."""
        lo,hi=F(a),F(b)
        if not lo<hi:raise ValueError('ordered q support required')
        left=bisect_left(self.energies,lo)
        right=bisect_left(self.energies,hi)
        if closed_right:
            while right<len(self.energies) and self.energies[right]==hi:right+=1
        return self.prefix_n[right]-self.prefix_n[left],self.prefix_u[right]-self.prefix_u[left]


@dataclass(frozen=True)
class Cell:
    ident:int
    a:float
    b:float
    n:Fraction
    u:Fraction
    bounds:tuple[tuple[Fraction,Fraction],...]
    score:float


class AdaptiveQGrid:
    """Greedy heap refinement using actual child packet moments.

    Rejects unsupported parent-only N,U splits. Supports single ray and one
    current proper clock. Interval ledgers are exact dyadic Fraction sums.
    """
    def __init__(self,oracle:PositivePacketOracle,ref_edges:Sequence[float],ratio_R:float,
                 neutrals_cm3:Sequence[float],dt_s:float,budgets:Sequence[float],
                 nodes_per_branch:int=4):
        if not isinstance(oracle,PositivePacketOracle):
            raise ValueError('adaptive child moments need positive packet oracle')
        ed=np.asarray(ref_edges,float)
        if len(ed)<2 or not np.all(np.isfinite(ed)) or np.any(np.diff(ed)<=0):
            raise ValueError('fixed ordered q-bin edges required')
        if not isfinite(ratio_R) or ratio_R<=0 or not (0<ed[0]<ed[-1]<=50000):
            raise ValueError('physical reference energy/R invalid')
        self.edges=[float(x) for x in ed]
        if oracle.energies[0]<F(ed[0]) or oracle.energies[-1]>F(ed[-1]):
            raise ValueError('packet measure exceeds declared full q support')
        self.ratio=float(ratio_R)
        self.neutrals=tuple(float(n) for n in neutrals_cm3)
        self.dt=float(dt_s)
        self.budgets=tuple(float(b) for b in budgets)
        if len(self.budgets)!=6 or any(not isfinite(b) or b<=0 for b in self.budgets):
            raise ValueError('all six physical observable budgets must be positive')
        if len(self.neutrals)!=3 or any(not isfinite(x) or x<0 for x in self.neutrals) or not isfinite(self.dt) or self.dt<0:
            raise ValueError('invalid current gas / proper clock')
        self.oracle=oracle;self.nodes=nodes_per_branch
        self.cells={};self.heap=[];self.serial=0;self.split_count=0;self.trace=[]
        self.raw_low=[Fraction(0)]*6;self.raw_high=[Fraction(0)]*6
        for a,b in zip(self.edges[:-1],self.edges[1:]):
            c=self._make(float(a),float(b),closed_right=(b==self.edges[-1]))
            self._insert(c)
        self.global_lo=self.raw_low.copy();self.global_hi=self.raw_high.copy()
        self.initial_cell_count=len(self.cells)
        self._check_moment_conservation()

    def _make(self,a,b,closed_right=False):
        n,u=self.oracle.moments(a,b,closed_right)
        if n==0:
            bounds=tuple((Fraction(0),Fraction(0)) for _ in range(6))
            score=0.
        else:
            mn=u/n
            if mn<F(a) or mn>F(b):raise ArithmeticError('true positive child mean outside q cell')
            # Widen physical q-cell endpoints to encompass exact stored dyadics.
            aa=F(a)*F(self.ratio);bb=F(b)*F(self.ratio)
            lo=nextafter(float(aa),-inf);hi=nextafter(float(bb),inf)
            if lo<=0 or hi>50000:raise ValueError('physical support out of the Verner fit')
            t=cached_template(lo,hi,self.neutrals,self.dt,self.nodes)
            z=t.evaluate(n,mn*F(self.ratio))
            bounds=tuple((F(x),F(y)) for x,y in z['event']+z['heat'])
            if any(h<l for l,h in bounds):raise ArithmeticError('invalid certified interval')
            score=max(float((h-l)/F(budget)) for (l,h),budget in zip(bounds,self.budgets))
        self.serial+=1
        return Cell(self.serial,a,b,n,u,bounds,score)

    def _insert(self,c):
        self.cells[c.ident]=c
        for j,(a,b) in enumerate(c.bounds):
            self.raw_low[j]+=a;self.raw_high[j]+=b
        heappush(self.heap,(-c.score,c.a,c.ident))

    def _delete(self,c):
        del self.cells[c.ident]
        for j,(a,b) in enumerate(c.bounds):
            self.raw_low[j]-=a;self.raw_high[j]-=b

    def _split_location(self,c):
        # Whenever an active atomic fit boundary lies inside the *physical*
        # range, put an explicit q-edge there, before generic logarithmic split.
        a=F(c.a);b=F(c.b);r=F(self.ratio)
        active=[float(F(fit)/r) for fit in FIT_CUTOFFS if a<F(fit)/r<b]
        if active:
            candidate=min(active,key=lambda v:abs(log(v)-.5*(log(c.a)+log(c.b))))
        else:
            candidate=sqrt(c.a*c.b)
        if not c.a<candidate<c.b:return None
        return candidate

    def _check_moment_conservation(self):
        count=sum((c.n for c in self.cells.values()),Fraction(0))
        energy=sum((c.u for c in self.cells.values()),Fraction(0))
        if count!=self.oracle.total_n or energy!=self.oracle.total_u:
            raise ArithmeticError('not the original exact photon count / first energy moment')

    def _commit_intersection(self):
        # Both previous and new intervals enclose the SAME exact observables.
        for j in range(6):
            a=max(self.global_lo[j],self.raw_low[j]);b=min(self.global_hi[j],self.raw_high[j])
            if b<a:raise ArithmeticError('inconsistent old/new outer intervals')
            self.global_lo[j]=a;self.global_hi[j]=b

    def run(self,max_cells:int,stop_on_precision:bool=False):
        if not isinstance(max_cells,int) or max_cells>8192:
            raise ValueError('bounded integer adaptive grid required')
        if max_cells<len(self.cells):raise ValueError('cannot coarsen from moment-only input')
        while len(self.cells)<max_cells and self.heap:
            if stop_on_precision and self.precision_goal_met():break
            _,_,ident=heappop(self.heap)
            c=self.cells.get(ident)
            if c is None:continue
            if c.n==0:break  # all positive cells have >= score
            loc=self._split_location(c)
            if loc is None:continue
            left=self._make(c.a,loc)
            right=self._make(loc,c.b,closed_right=(c.b==self.edges[-1]))
            if left.n+right.n!=c.n or left.u+right.u!=c.u:
                raise ArithmeticError('true child moments are not a partition of parent')
            # Prevalidate complete global intersection, transactional state.
            trial_lower=[self.raw_low[j]-c.bounds[j][0]+left.bounds[j][0]+right.bounds[j][0] for j in range(6)]
            trial_upper=[self.raw_high[j]-c.bounds[j][1]+left.bounds[j][1]+right.bounds[j][1] for j in range(6)]
            if any(max(self.global_lo[j],trial_lower[j])>min(self.global_hi[j],trial_upper[j]) for j in range(6)):
                raise ArithmeticError('inconsistent split enclosures: unchanged state')
            self._delete(c);self._insert(left);self._insert(right)
            self._commit_intersection();self.split_count+=1
            self.trace.append({'split':self.split_count,'a':c.a,'b':c.b,'at':loc,'score':c.score,
                               'new_cells':len(self.cells)})
        self._check_moment_conservation()
        return self.summary()

    def precision_goal_met(self):
        return all(self.global_hi[j]-self.global_lo[j]<=F(t) for j,t in enumerate(self.budgets))

    def summary(self):
        outer=[]
        for a,b in zip(self.global_lo,self.global_hi):
            outer.append((0. if a<=0 else nextafter(float(a),-inf),
                          0. if b<=0 else nextafter(float(b),inf)))
        return {'cells':len(self.cells),'nonempty':sum(c.n>0 for c in self.cells.values()),
                'splits':self.split_count,'event':outer[:3],'heat':outer[3:],
                'widths':[hi-lo for lo,hi in outer],
                'mass':float(self.oracle.total_n), 'reference_energy_eV':float(self.oracle.total_u),
                'stored_moments_bytes':len(self.cells)*2*8,
                'shape_free':'CONDITIONAL_TO_TRUE_CHILD_MOMENTS_AND_BIN_SUPPORT',
                'exact_dyadic_partition':True,
                'precision_target_met':self.precision_goal_met(),
                'precision_gate':'PASS_SCOPED' if self.precision_goal_met() else 'HOLD_PRECISION_TARGET',
                'requested_width_scales':self.budgets}

    def sorted_edges(self):
        return sorted({v for c in self.cells.values() for v in (c.a,c.b)})
