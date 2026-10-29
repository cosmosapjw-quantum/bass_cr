"""Exact integer-scaled C++ SSP oracle with independent Python Fraction witness verifier.

No physical exclusive He kernel or energy K is derived here. Original atoms are read
through the hash-locked PR121 native_budget loader by the caller.
"""
from __future__ import annotations
import math
import subprocess
from collections import defaultdict
from fractions import Fraction as F
from pathlib import Path

BIN = Path(__file__).with_name('potentials_ssp')
MAX_BITS = 105   # bounded i128 intermediate products, fail closed


def run_exact(atoms, K, budget, *, executable=BIN, timeout=45.0):
    # No implicit float conversion at the trust boundary.
    if type(K) not in (F, int) or type(budget) not in (F, int):
        raise TypeError('EXACT_RATIONAL_INPUT_REQUIRED')
    K, budget = F(K), F(budget)
    if K < 0 or budget < 0:
        raise ValueError('NONNEGATIVE_K_AND_BUDGET')
    atoms = tuple(atoms)
    if any(type(a.energy) is not F or type(a.mass) is not F for a in atoms):
        raise TypeError('EXACT_ATOMS_ONLY')
    if len({a.key for a in atoms}) != len(atoms):
        raise ValueError('DUPLICATE_ATOMS')
    H = [a for a in atoms if 2*a.energy > K and a.mass>0]
    L = [a for a in atoms if 2*a.energy <= K and a.mass>0]
    scale = math.lcm(*(a.mass.denominator for a in atoms),budget.denominator)
    hi = [int(a.mass*scale) for a in H]
    lo = [int(a.mass*scale) for a in L]
    budget_scaled = int(budget*scale)
    if max([budget_scaled, sum(hi)+sum(lo)+1]+hi+lo).bit_length() > MAX_BITS:
        raise OverflowError('I128_EXACT_SCALE_EXCEEDED')
    graph_edges=[(i,j,int(a.bin!=b.bin))
                 for i,a in enumerate(H) for j,b in enumerate(L)
                 if a.energy+b.energy<=K]
    lines=[f'{len(H)} {len(L)} {len(graph_edges)} {budget_scaled}',
           *(str(v) for v in hi),*(str(v) for v in lo),
           *(f'{i} {j} {cost}' for i,j,cost in graph_edges)]
    proc=subprocess.run([str(executable)], input='\n'.join(lines)+'\n',text=True,
                        stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout)
    if proc.returncode != 0: raise RuntimeError(f'CPP_FAILED_{proc.returncode}: {proc.stderr[-1200:]}')
    values={}; flow=[]; ph={};pl={}
    for ln in proc.stdout.splitlines():
        row=ln.split(); tag=row[0]
        if tag=='FLOW':flow.append((int(row[1]),int(row[2]),F(int(row[3]),int(row[4]))/scale))
        elif tag=='PH':ph[int(row[1])]=int(row[2])
        elif tag=='PL':pl[int(row[1])]=int(row[2])
        else:values[tag]=row[1:]
    if values.get('END')!=[]: raise AssertionError('TRUNCATED_CPP_WITNESS')
    m=F(int(values['M'][0]),int(values['M'][1]))/scale
    cross=F(int(values['C'][0]),int(values['C'][1]))/scale
    lam=F(int(values['LAMBDA'][0]),int(values['LAMBDA'][1]))
    price_denom=int(values['PRICE_DENOM'][0])
    prices={**{a.key:F(ph[i],price_denom) for i,a in enumerate(H)},
            **{a.key:F(pl[j],price_denom) for j,a in enumerate(L)}}
    # Optional zero-mass atoms are priced at unit cost without changing the objective.
    prices.update({a.key:F(1) for a in atoms if a.mass==0})
    used=defaultdict(F)
    actual_m=actual_cross=F(0)
    for i,j,x in flow:
        if x<=0: raise AssertionError('NONPOSITIVE_PRIMAL_FLOW')
        a,b=H[i],L[j]
        if a.energy+b.energy>K: raise AssertionError('INADMISSIBLE_PRIMAL_EDGE')
        used[a.key]+=x;used[b.key]+=x
        actual_m+=x
        if a.bin!=b.bin:actual_cross+=x
    if actual_m!=m or actual_cross!=cross or cross>budget: raise AssertionError('BUDGETED_PRIMAL_OBJECTIVE_DEFECT')
    if any(used[a.key]>a.mass for a in atoms): raise AssertionError('SOURCE_ATOM_CAPACITY_DEFECT')
    dual_obj=sum((a.mass*prices[a.key] for a in atoms),F(0))+budget*lam
    checked=0
    for h in (a for a in atoms if 2*a.energy>K):
        for l in (a for a in atoms if 2*a.energy<=K):
            if h.energy+l.energy<=K:
                if prices[h.key]+prices[l.key]+lam*int(h.bin!=l.bin)<1:
                    raise AssertionError(('DUAL_EDGE_UNCOVERED',h.key,l.key))
                checked+=1
    if dual_obj!=m: raise AssertionError(('PRIMAL_DUAL_GAP',dual_obj,m))
    Ltot=sum((a.mass for a in atoms if 2*a.energy<=K),F(0))
    return dict(M=m, C=cross, d_max=(Ltot+m)/2, lambda_dual=lam,
                gap=dual_obj-m, checked_edges=checked, flow=flow, prices=prices,
                state=values['STATUS'][0], scale=scale, cpp_stats=[int(v) for v in values['STATS']],
                H=len(H),L=len(L),eligible_edges=len(graph_edges))