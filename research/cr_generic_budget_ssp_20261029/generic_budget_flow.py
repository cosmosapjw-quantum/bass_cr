"""Small exact rational budgeted high-low matching, arbitrary bin labels.

The SSP min-cost flow enumerates the exact piecewise-linear C_min(m) and
inverts it to obtain M(c). This is a finite conditional event LP, not a
physical rate model. The reference is not a scalable 3201-atom solver.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction as F
from collections import defaultdict
from native_budget import Atom, exact


@dataclass
class Arc:
    to: int
    rev: int
    residual: F
    cost: int


def _sym(x):
    from sympy import Rational
    return Rational(x.numerator, x.denominator)


def _frac(x):
    from sympy import Rational
    a,b=Rational(x).as_numer_denom()
    return F(int(a),int(b))


class ExactBudgetFlow:
    def __init__(self, atoms, K, max_atoms=14, max_edges=100):
        self.atoms=tuple(atoms)
        self.K=exact(K)
        if self.K<0:raise ValueError('NEGATIVE_K')
        if any(type(a) is not Atom for a in self.atoms):raise TypeError('ATOM_TYPE')
        if len({a.key for a in self.atoms})!=len(self.atoms):raise ValueError('DUPLICATE_KEYS')
        if len(self.atoms)>max_atoms:raise ValueError('SMALL_INSTANCE_ONLY')
        self.high=[a for a in self.atoms if 2*a.energy>self.K and a.mass>0]
        self.low=[a for a in self.atoms if 2*a.energy<=self.K and a.mass>0]
        self.L=sum((a.mass for a in self.low),F(0))
        self.eligible=[(h,l) for h in self.high for l in self.low
                       if h.energy+l.energy<=self.K]
        if len(self.eligible)>max_edges:raise ValueError('SMALL_INSTANCE_EDGE_CEILING')
        self.s=0
        self.t=1+len(self.high)+len(self.low)
        self.graph=[[] for _ in range(self.t+1)]
        self.edge_refs=[];self.original_caps=[];self.costs=[];self.snapshots=[]
        self._make_graph()
        self._enumerate_cost_curve()

    def _add(self,u,v,capacity,cost):
        i,j=len(self.graph[u]),len(self.graph[v])
        self.graph[u].append(Arc(v,j,capacity,cost))
        self.graph[v].append(Arc(u,i,F(0),-cost))
        return (u,i)

    def _make_graph(self):
        for i,h in enumerate(self.high):self._add(self.s,1+i,h.mass,0)
        for j,l in enumerate(self.low):
            self._add(1+len(self.high)+j,self.t,l.mass,0)
        hi={h.key:i for i,h in enumerate(self.high)}
        lo={l.key:j for j,l in enumerate(self.low)}
        for h,l in self.eligible:
            cap=min(h.mass,l.mass)
            cost=int(h.bin!=l.bin)
            ref=self._add(1+hi[h.key],1+len(self.high)+lo[l.key],cap,cost)
            self.edge_refs.append(ref);self.original_caps.append(cap);self.costs.append(cost)

    def _flows(self):
        return tuple(cap-self.graph[u][i].residual
                     for (u,i),cap in zip(self.edge_refs,self.original_caps))

    def _shortest(self):
        n=len(self.graph)
        dist=[None]*n;prev=[None]*n;dist[self.s]=0
        for _ in range(n-1):
            changed=False
            for u in range(n):
                if dist[u] is None:continue
                for i,e in enumerate(self.graph[u]):
                    if e.residual<=0:continue
                    d=dist[u]+e.cost
                    if dist[e.to] is None or d<dist[e.to]:
                        dist[e.to]=d;prev[e.to]=(u,i);changed=True
            if not changed:break
        for u in range(n):
            if dist[u] is None:continue
            for e in self.graph[u]:
                if e.residual>0 and dist[e.to] is not None and dist[u]+e.cost<dist[e.to]:
                    raise AssertionError('NEGATIVE_RESIDUAL_CYCLE')
        return dist[self.t],prev

    def _enumerate_cost_curve(self):
        m=C=F(0)
        self.snapshots=[{'m':m,'C':C,'flow':self._flows(),'slope':None}]
        max_steps=2*len(self.edge_refs)+2*len(self.high)+2*len(self.low)+5
        for _ in range(max_steps):
            slope,prev=self._shortest()
            if slope is None:break
            if slope<0:raise AssertionError('NEGATIVE_MARGINAL_COST')
            prev_slope=self.snapshots[-1]['slope']
            if prev_slope is not None and slope<prev_slope:
                raise AssertionError('NONCONVEX_COST_CURVE')
            path=[];node=self.t;seen=set()
            while node!=self.s:
                if node in seen or prev[node] is None:
                    raise AssertionError('BROKEN_AUGMENTING_PATH')
                seen.add(node);u,i=prev[node];path.append((u,i));node=u
            delta=min(self.graph[u][i].residual for u,i in path)
            if delta<=0:raise AssertionError('NONPOSITIVE_AUGMENTATION')
            for u,i in path:
                e=self.graph[u][i];e.residual-=delta
                self.graph[e.to][e.rev].residual+=delta
            m+=delta;C+=slope*delta
            flow=self._flows()
            if C!=sum((x*k for x,k in zip(flow,self.costs)),F(0)):
                raise AssertionError('COST_NOT_EQUAL_CROSS_MASS')
            if m!=sum(flow,F(0)):raise AssertionError('FLOW_VALUE_MISMATCH')
            self.snapshots.append({'m':m,'C':C,'flow':flow,'slope':slope})
        else:raise ValueError('AUGMENTATION_GUARD_EXCEEDED')
        self.M=self.snapshots[-1]['m'];self.C_at_M=self.snapshots[-1]['C']

    def _exact_dual(self,c,m,flow):
        """Independent LP dual for small instances, including zero-mass vertices."""
        from sympy import symbols, Rational
        from sympy.solvers.simplex import lpmin
        H=[a for a in self.atoms if 2*a.energy>self.K]
        L=[a for a in self.atoms if 2*a.energy<=self.K]
        all_edges=[(h,l) for h in H for l in L if h.energy+l.energy<=self.K]
        if not all_edges:
            return {'objective':F(0),'gap':F(0),'lambda':F(0),'prices':{a.key:F(0) for a in self.atoms}}
        pp=symbols('p0:'+str(len(self.atoms)))
        lam=symbols('lambda')
        idx={a.key:i for i,a in enumerate(self.atoms)}
        constraints=[x>=0 for x in pp]+[lam>=0]
        constraints += [pp[idx[h.key]]+pp[idx[l.key]]+
                        (lam if h.bin!=l.bin else 0)>=1 for h,l in all_edges]
        obj=sum((pp[i]*_sym(a.mass) for i,a in enumerate(self.atoms)),Rational(0))+lam*_sym(c)
        opt,sol=lpmin(obj,constraints)
        dual=_frac(opt)
        prices={a.key:_frac(sol.get(pp[i],Rational(0))) for i,a in enumerate(self.atoms)}
        multiplier=_frac(sol.get(lam,Rational(0)))
        if any(prices[h.key]+prices[l.key]+multiplier*(h.bin!=l.bin)<1 for h,l in all_edges):
            raise AssertionError('DUAL_EDGE_UNCOVERED')
        if dual!=m:raise AssertionError('BUDGETED_PRIMAL_DUAL_GAP')
        return {'objective':dual,'gap':dual-m,'lambda':multiplier,'prices':prices}

    def witness(self,c,*,certify_dual=True):
        c=exact(c)
        if c<0:raise ValueError('NEGATIVE_BUDGET')
        selected=self.snapshots[0]['flow']
        for i in range(1,len(self.snapshots)):
            before,after=self.snapshots[i-1],self.snapshots[i]
            if after['C']<=c:
                selected=after['flow']
                continue
            if after['C']>before['C']:
                t=(c-before['C'])/(after['C']-before['C'])
                selected=tuple(x+(y-x)*t for x,y in zip(before['flow'],after['flow']))
            break
        # Convex interpolation of adjacent min-cost flows preserves all marginals.
        used=defaultdict(F)
        primal=[]
        for (h,l),v in zip(self.eligible,selected):
            if v<0:raise AssertionError('NEGATIVE_FLOW')
            if v:
                primal.append((h.key,l.key,v))
                used[h.key]+=v;used[l.key]+=v
        if any(used[a.key]>a.mass for a in self.atoms):
            raise AssertionError('CAPACITY_VIOLATION')
        m=sum(selected,F(0))
        C=sum((v*k for v,k in zip(selected,self.costs)),F(0))
        if C>c:raise AssertionError('CROSS_BUDGET_VIOLATION')
        low_diagonal=tuple((a.key,(a.mass-used[a.key])/2) for a in self.atoms
                           if 2*a.energy<=self.K and a.mass>used[a.key])
        high_single=tuple((a.key,a.mass-used[a.key]) for a in self.atoms
                          if 2*a.energy>self.K and a.mass>used[a.key])
        d=m+sum((v for _,v in low_diagonal),F(0))
        if d!=(self.L+m)/2:raise AssertionError('DOUBLE_EVENT_MASS_DEFECT')
        dual=self._exact_dual(c,m,selected) if certify_dual else None
        return {'budget':c,'M_budget':m,'cross_used':C,'d_max':d,
                'high_low':tuple(primal),'low_diagonal':low_diagonal,
                'high_single':high_single,'dual':dual}

    def breakpoints(self):
        """Exact flow/cost endpoints, with zero-cost and equal-slope runs merged."""
        curve=[(F(0),F(0),None)]
        for i in range(1,len(self.snapshots)):
            now=self.snapshots[i];prev=self.snapshots[i-1]
            if i>1 and now['slope']==prev['slope']:
                curve[-1]=(now['C'],now['m'],now['slope'])
            else:
                curve.append((now['C'],now['m'],now['slope']))
        return tuple(curve)


def summarize(atoms,K,budgets):
    obj=ExactBudgetFlow(atoms,K)
    return {'breakpoints':[(str(c),str(m),s) for c,m,s in obj.breakpoints()],
            'frontier':[{'c':str(c),'M':str((r:=obj.witness(c))['M_budget']),
                         'C':str(r['cross_used']),'d':str(r['d_max']),
                         'dual_gap':str(r['dual']['gap']),
                         'lambda':str(r['dual']['lambda'])} for c in budgets]}