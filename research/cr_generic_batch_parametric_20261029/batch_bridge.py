"""Exact multi-budget primal-dual witnesses for a finite bipartite HL flow.

Caller supplies the frozen exact Atom objects; this module supplies no physical kernel.
All budget queries share one min-cost-flow trajectory and are verified independently
against EVERY admissible source edge, including zero-capacity vertices.
"""
from __future__ import annotations
from collections import defaultdict
from fractions import Fraction as F
from math import lcm
from pathlib import Path
import subprocess

BATCH_BIN = Path(__file__).with_name('potentials_batch')
MAX_BITS = 105

def run_batch(atoms, K, budgets, *, executable=BATCH_BIN, timeout=90):
    if type(K) not in (F, int): raise TypeError('EXACT_K_REQUIRED')
    if F(K)<0: raise ValueError('NEGATIVE_K')
    atoms=tuple(atoms); budgets=tuple(budgets)
    if not budgets: raise ValueError('EMPTY_BUDGETS')
    if len(budgets)>128: raise ValueError('BUDGET_QUERY_CEILING_128')
    if any(type(c) not in (F, int) for c in budgets): raise TypeError('EXACT_BUDGET_REQUIRED')
    budgets=tuple(F(c) for c in budgets)
    if any(c<0 for c in budgets): raise ValueError('NEGATIVE_BUDGET')
    if any(type(a.energy) is not F or type(a.mass) is not F or a.energy<0 or a.mass<0 for a in atoms):
        raise TypeError('EXACT_NONNEGATIVE_ATOMS_REQUIRED')
    if len({a.key for a in atoms})!=len(atoms): raise ValueError('DUPLICATE_KEYS')
    H=[a for a in atoms if 2*a.energy>K and a.mass>0]
    L=[a for a in atoms if 2*a.energy<=K and a.mass>0]
    scale=lcm(*(a.mass.denominator for a in atoms),*(c.denominator for c in budgets))
    hi=[int(a.mass*scale) for a in H]
    lo=[int(a.mass*scale) for a in L]
    scaled=[int(c*scale) for c in budgets]
    if max([sum(hi)+sum(lo)+1]+hi+lo+scaled).bit_length()>MAX_BITS:
        raise OverflowError('I128_EXACT_SCALE_EXCEEDED')
    edge_list=[(i,j,int(a.bin!=b.bin)) for i,a in enumerate(H) for j,b in enumerate(L)
               if a.energy+b.energy<=K]
    lines=[f'{len(H)} {len(L)} {len(edge_list)} {len(budgets)}',
           *(str(v) for v in scaled),*(str(v) for v in hi),*(str(v) for v in lo),
           *(f'{i} {j} {cost}' for i,j,cost in edge_list)]
    proc=subprocess.run([str(executable)], input='\n'.join(lines)+'\n',text=True,
                        stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout)
    if proc.returncode!=0: raise RuntimeError(f'BATCH_CPP_FAILED_{proc.returncode}: {proc.stderr[-1500:]}')
    blocks=[];cur=[]
    for line in proc.stdout.splitlines():
        if line=='END':
            if not cur:raise AssertionError('EMPTY_RESULT_RECORD')
            blocks.append(cur);cur=[]
        else:cur.append(line.split())
    if cur or len(blocks)!=len(budgets): raise AssertionError('BAD_BATCH_OUTPUT_COUNT')
    results=[None]*len(budgets)
    original_edges=[(h,l) for h in atoms if 2*h.energy>K for l in atoms
                    if 2*l.energy<=K and h.energy+l.energy<=K]
    Ltot=sum((a.mass for a in atoms if 2*a.energy<=K),F(0))
    for rows in blocks:
        q={}; flows=[]; ph={};pl={}
        for row in rows:
            typ=row[0]
            if typ=='FLOW': flows.append((int(row[1]),int(row[2]),F(int(row[3]),int(row[4]))/scale))
            elif typ=='PH':ph[int(row[1])]=int(row[2])
            elif typ=='PL':pl[int(row[1])]=int(row[2])
            else:q[typ]=row[1:]
        required={'QUERY','STATUS','M','C','BUDGET','LOW','LAMBDA','PRICE_DENOM','STATS'}
        if set(q)!=required: raise AssertionError(('INCOMPLETE_RESULT_FIELDS',set(q)))
        idx=int(q['QUERY'][0]);
        if idx<0 or idx>=len(budgets) or results[idx] is not None:raise AssertionError('DUPLICATE_QUERY_RESULT')
        if F(int(q['BUDGET'][0]),scale)!=budgets[idx]:raise AssertionError('WRONG_BUDGET_RETURNED')
        m=F(int(q['M'][0]),int(q['M'][1]))/scale
        c_used=F(int(q['C'][0]),int(q['C'][1]))/scale
        lam=F(int(q['LAMBDA'][0]),int(q['LAMBDA'][1]))
        denom=int(q['PRICE_DENOM'][0]);
        if denom<=0 or set(ph)!=set(range(len(H))) or set(pl)!=set(range(len(L))):
            raise AssertionError('BAD_PRICE_VECTOR')
        prices={**{a.key:F(ph[i],denom) for i,a in enumerate(H)},
                **{a.key:F(pl[j],denom) for j,a in enumerate(L)}}
        prices.update({a.key:F(1) for a in atoms if a.mass==0})
        used=defaultdict(F);summ=summcross=F(0)
        last=set()
        for hi_idx,lo_idx,x in flows:
            if not (0<=hi_idx<len(H) and 0<=lo_idx<len(L)):raise AssertionError('BAD_EDGE_INDEX')
            if x<=0 or (hi_idx,lo_idx) in last:raise AssertionError('FLOW_DUPLICATE_OR_NONPOSITIVE')
            last.add((hi_idx,lo_idx));a,b=H[hi_idx],L[lo_idx]
            if a.energy+b.energy>K:raise AssertionError('FLOW_INADMISSIBLE')
            used[a.key]+=x;used[b.key]+=x;summ+=x
            if a.bin!=b.bin:summcross+=x
        if any(used[a.key]>a.mass for a in atoms):raise AssertionError('MARGINAL_VIOLATION')
        if summ!=m or summcross!=c_used or c_used>budgets[idx]:raise AssertionError('PRIMAL_MISMATCH')
        if any(p<0 for p in prices.values()) or lam<0:raise AssertionError('NEGATIVE_DUAL')
        for h,l in original_edges:
            if prices[h.key]+prices[l.key]+lam*int(h.bin!=l.bin)<1:
                raise AssertionError(('DUAL_EDGE_UNCOVERED',h.key,l.key))
        dual_obj=sum((a.mass*prices[a.key] for a in atoms),F(0))+lam*budgets[idx]
        if dual_obj!=m:raise AssertionError(('DUAL_GAP',dual_obj,m))
        results[idx]={'budget':budgets[idx],'M':m,'C':c_used,'d_max':(Ltot+m)/2,
                      'lambda_dual':lam,'gap':dual_obj-m,'state':q['STATUS'][0],
                      'checked_edges':len(original_edges),'positive_pairs':len(flows),
                      'flow':flows,'prices':prices,'cpp_stats':[int(v) for v in q['STATS']],
                      'source_scale':scale}
    if any(z is None for z in results):raise AssertionError('MISSING_QUERY')
    return results
