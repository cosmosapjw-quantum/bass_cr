"""Exact fractional HL frontier on a Ferrers-by-birth-bin interval network.

Inputs remain original, immutable per-atom mass/energy/bin values. All returned
witnesses and budget LP duals are independently checked on the *uncompressed*
original admissibility graph, including zero-mass source atoms.
"""
from __future__ import annotations
from collections import defaultdict
from fractions import Fraction as F
from bisect import bisect_right
from math import lcm
from pathlib import Path
import subprocess

DEFAULT_EXE = Path(__file__).with_name('prefix_ssp')
MAX_BITS=105


def run_prefix(atoms,K,budgets,*,executable=DEFAULT_EXE,timeout=90):
    atoms=tuple(atoms); budgets=tuple(budgets)
    if type(K) not in (int,F):raise TypeError('EXACT_K_REQUIRED')
    if F(K)<0:raise ValueError('NEGATIVE_K')
    if not budgets or len(budgets)>128:raise ValueError('INVALID_BUDGET_COUNT')
    if any(type(c) not in (int,F) or c<0 for c in budgets):raise ValueError('INVALID_EXACT_BUDGET')
    budgets=tuple(F(c) for c in budgets); K=F(K)
    if any(type(a.energy) is not F or type(a.mass) is not F or a.energy<0 or a.mass<0 for a in atoms):raise TypeError('INVALID_ATOMS')
    if len({a.key for a in atoms})!=len(atoms):raise ValueError('DUPLICATE_KEYS')
    highs=[a for a in atoms if 2*a.energy>K and a.mass>0]
    lows=[a for a in atoms if 2*a.energy<=K and a.mass>0]
    # Bin order is an internal coordinate only; raw bin identifiers remain unmodified.
    raw_bins=sorted({a.bin for a in highs+lows},key=lambda v:(type(v).__name__,str(v)))
    if not raw_bins:raw_bins=[0]
    bidx={v:i for i,v in enumerate(raw_bins)}
    low_by_bin=[sorted((a for a in lows if a.bin==v),key=lambda a:(a.energy,str(a.key))) for v in raw_bins]
    sorted_lows=[a for block in low_by_bin for a in block]
    energies=[[a.energy for a in block] for block in low_by_bin]
    keep=[];cut=[];isolated=[]
    for h in highs:
        prefix=[bisect_right(energies[b],K-h.energy) for b in range(len(raw_bins))]
        if sum(prefix)>0:keep.append(h);cut.append(prefix)
        else:isolated.append(h)
    H=keep;L=sorted_lows
    scale=lcm(*(a.mass.denominator for a in atoms),*(c.denominator for c in budgets))
    capsH=[int(a.mass*scale) for a in H];capsL=[int(a.mass*scale) for a in L]
    qs=[int(c*scale) for c in budgets]
    if max([sum(capsH)+sum(capsL)+1]+capsH+capsL+qs).bit_length()>MAX_BITS:
        raise OverflowError('SCALE_EXCEEDS_I128_GUARD')
    lines=[f'{len(H)} {len(L)} {len(raw_bins)} {len(budgets)}',
           *map(str,qs),*map(str,capsH),*map(str,capsL),
           *(str(bidx[a.bin]) for a in H),*(str(bidx[a.bin]) for a in L),
           *(str(k) for prefix in cut for k in prefix)]
    proc=subprocess.run([str(executable)],input='\n'.join(lines)+'\n',text=True,
                        capture_output=True,timeout=timeout)
    if proc.returncode!=0:raise RuntimeError(f'PREFIX_CPP_FAILED_{proc.returncode}: {proc.stderr[-1400:]}')
    blocks=[];cur=[]
    for row in proc.stdout.splitlines():
        if row=='END':
            if not cur:raise AssertionError('EMPTY_RECORD')
            blocks.append(cur);cur=[]
        else:cur.append(row.split())
    if cur or len(blocks)!=len(budgets):raise AssertionError('BAD_RESULT_COUNT')
    valid_original_edges=[(h,l) for h in atoms if 2*h.energy>K for l in atoms if 2*l.energy<=K and h.energy+l.energy<=K]
    Ltot=sum((a.mass for a in atoms if 2*a.energy<=K),F(0))
    results=[None]*len(budgets)
    for rows in blocks:
        props={};ph={};pl={};flow=[]
        for row in rows:
            name=row[0]
            if name=='FLOW':flow.append((int(row[1]),int(row[2]),F(int(row[3]),int(row[4]))/scale))
            elif name=='PH':ph[int(row[1])]=int(row[2])
            elif name=='PL':pl[int(row[1])]=int(row[2])
            else:props[name]=row[1:]
        required={'QUERY','M','C','BUDGET','LOW','LAMBDA','PRICE_DENOM','STATS'}
        if set(props)!=required:raise AssertionError(('BAD_FIELDS',set(props)))
        idx=int(props['QUERY'][0]);
        if not 0<=idx<len(budgets) or results[idx] is not None:raise AssertionError('DUPLICATE_QUERY')
        if F(int(props['BUDGET'][0]),scale)!=budgets[idx]:raise AssertionError('WRONG_BUDGET')
        if set(ph)!=set(range(len(H))) or set(pl)!=set(range(len(L))):raise AssertionError('PRICE_INDEX_SET')
        pd=int(props['PRICE_DENOM'][0]);
        if pd<=0:raise AssertionError('PRICE_DENOM')
        prices={**{a.key:F(ph[i],pd) for i,a in enumerate(H)},**{a.key:F(pl[j],pd) for j,a in enumerate(L)}}
        # Omitted source atoms have zero-mass or zero-degree. Covers zero-mass edges by price 1.
        prices.update({a.key:F(0) for a in isolated})
        prices.update({a.key:F(1) for a in atoms if a.mass==0})
        if set(prices)!={a.key for a in atoms}:raise AssertionError('ORIGINAL_ATOM_PRICE_MISSING')
        m=F(int(props['M'][0]),int(props['M'][1]))/scale
        c_used=F(int(props['C'][0]),int(props['C'][1]))/scale
        lam=F(int(props['LAMBDA'][0]),int(props['LAMBDA'][1]))
        originalflow=[];used=defaultdict(F);mm=cc=F(0);pairs=set()
        for hi,lo,weight in flow:
            if not (0<=hi<len(H) and 0<=lo<len(L)) or (hi,lo) in pairs or weight<=0:
                raise AssertionError('INVALID_FLOW')
            pairs.add((hi,lo));h,l=H[hi],L[lo]
            if h.energy+l.energy>K:raise AssertionError('ENERGY_SUPPORT_FAIL')
            used[h.key]+=weight;used[l.key]+=weight;mm+=weight;cc+=int(h.bin!=l.bin)*weight
            originalflow.append((h.key,l.key,weight))
        if any(used[a.key]>a.mass for a in atoms) or mm!=m or cc!=c_used or c_used>budgets[idx]:
            raise AssertionError('PRIMAL_CONSERVATION_FAIL')
        if any(p<0 for p in prices.values()) or lam<0:raise AssertionError('DUAL_NEGATIVE')
        for h,l in valid_original_edges:
            if prices[h.key]+prices[l.key]+lam*int(h.bin!=l.bin)<1:
                raise AssertionError(('UNCOMPRESSED_DUAL_EDGE_FAIL',h.key,l.key))
        obj=sum((a.mass*prices[a.key] for a in atoms),F(0))+lam*budgets[idx]
        if obj!=m:raise AssertionError(('PRIMAL_DUAL_GAP',obj,m))
        stats=list(map(int,props['STATS']))
        if len(stats)!=7:raise AssertionError('BAD_STATS')
        results[idx]={'budget':budgets[idx],'M':m,'C':c_used,'d_max':(Ltot+m)/2,
                      'lambda_dual':lam,'gap':obj-m,'flow':originalflow,'prices':prices,
                      'checked_edges':len(valid_original_edges),'positive_pairs':len(originalflow),
                      'pruned_high':len(isolated),'active_high':len(H),'active_low':len(L),
                      'cpp_stats':stats,'source_scale':scale}
    if any(v is None for v in results):raise AssertionError('MISSING_RESULT')
    return results
