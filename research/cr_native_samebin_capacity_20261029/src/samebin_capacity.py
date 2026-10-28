"""Exact same-bin and unrestricted high--low capacity on finite energy-threshold marginals.

This is a conditional finite-event capacity calculation, NOT an exclusive kernel,
physical energy-loss rate, or sufficient (d,C) polygon theorem.
"""
from __future__ import annotations
from dataclasses import dataclass
from collections import defaultdict
from fractions import Fraction as F
from typing import Iterable


def fraction(x):
    if type(x) is F:
        return x
    if type(x) is int:
        return F(x)
    if type(x) is str:
        return F(x)
    raise TypeError('exact rational required, no implicit float rounding')


@dataclass(frozen=True)
class Atom:
    key: str
    energy_eV: F
    coefficient: F
    partition: int

    def __post_init__(self):
        if not isinstance(self.key,str) or not self.key or type(self.partition) is not int or self.partition<0:
            raise ValueError('invalid key or partition')
        if type(self.energy_eV) is not F or type(self.coefficient) is not F:
            raise TypeError('Atom requires Fraction fields; use Atom.parse for integers and strings')
        if self.energy_eV<0 or self.coefficient<0:
            raise ValueError('nonnegative energy and mass required')

    @classmethod
    def parse(cls, row):
        return cls(row['key'],fraction(row['energy_eV']),fraction(row['coefficient']),row['partition'])


def _within_group(high,low,K):
    """Greedy primal and nested-neighborhood Hall cut dual for one bipartite group."""
    high=sorted(high,key=lambda a:(-a.energy_eV,a.key))
    low=sorted(low,key=lambda a:(a.energy_eV,a.key))
    # Greedy explicitly supplies a full rational primal (pair capacities).
    j=0
    left=[a.coefficient for a in low]
    pairs=[]
    for h in high:
        remain=h.coefficient
        while remain>0 and j<len(low):
            if low[j].energy_eV+h.energy_eV>K:
                break
            amount=min(remain,left[j])
            if amount:
                pairs.append((h.key,low[j].key,amount))
                remain-=amount
                left[j]-=amount
            if left[j]==0:
                j+=1
    S=sum((v for _,_,v in pairs),F(0))
    H=sum((a.coefficient for a in high),F(0))
    # Exact Hall deficiency, maximum always among a suffix of sorted high energies.
    k=0
    high_sum=F(0); low_neighborhood=F(0)
    delta=F(0); active_threshold=None
    i=0
    while i<len(high):
        e=high[i].energy_eV
        while i<len(high) and high[i].energy_eV==e:
            high_sum+=high[i].coefficient
            i+=1
        while k<len(low) and low[k].energy_eV+e<=K:
            low_neighborhood+=low[k].coefficient
            k+=1
        deficiency=high_sum-low_neighborhood
        if deficiency>delta:
            delta=deficiency
            active_threshold=e
    dual=H-delta
    if S!=dual:
        raise AssertionError('PRIMAL_DUAL_GAP')
    return {
        'S':S,'dual':dual,'H':H,'deficiency':delta,
        'cut_threshold_high_eV':active_threshold,
        'pairs':pairs,'high_count':len(high),'low_count':len(low)
    }


def solve(atoms:Iterable[Atom],cap,within_same_bin=True):
    K=fraction(cap)
    if K<0:raise ValueError('negative energy cap')
    atoms=tuple(atoms)
    if len(set(a.key for a in atoms))!=len(atoms):raise ValueError('duplicate atom key')
    if any(type(a) is not Atom for a in atoms):raise TypeError('atom must be typed Atom')
    active=[a for a in atoms if a.coefficient>0]
    group=defaultdict(lambda:{'high':[],'low':[]})
    for a in active:
        ident=a.partition if within_same_bin else 0
        group[ident]['low' if 2*a.energy_eV<=K else 'high'].append(a)
    rows=[]; pairs=[]
    for b in sorted(group):
        d=_within_group(group[b]['high'],group[b]['low'],K)
        rows.append({**d,'partition':b})
        pairs+=d['pairs']
    S=sum((row['S'] for row in rows),F(0))
    dual=sum((row['dual'] for row in rows),F(0))
    N=sum((a.coefficient for a in active),F(0))
    L=sum((a.coefficient for a in active if 2*a.energy_eV<=K),F(0))
    if S!=dual or S<0 or S>L:
        raise AssertionError('INVALID_CAPACITY_OR_CERTIFICATE')
    # independent per-atom margin capacity checks and support verification
    by_key={a.key:a for a in active}
    used=defaultdict(F)
    for hi,lo,mass in pairs:
        a,b=by_key[hi],by_key[lo]
        if mass<=0 or a.energy_eV+b.energy_eV>K or 2*a.energy_eV<=K or 2*b.energy_eV>K:
            raise AssertionError('INVALID_PRIMAL_EDGE')
        if within_same_bin and a.partition!=b.partition:
            raise AssertionError('SAME_BIN_VIOLATION')
        used[hi]+=mass; used[lo]+=mass
    if any(used[a.key]>a.coefficient for a in active):
        raise AssertionError('MARGINAL_EXCESS')
    return {'K':K,'N':N,'L':L,'S':S,'dual':dual,'pairs':pairs,'group_certs':rows,'active_atom_count':len(active),
            'method':'EXACT_FERRERS_WEIGHTED_HALL_PRIMAL_DUAL'}


def bounds(atoms,K,C):
    """Only necessary bound at user-supplied C; never asserts attainability."""
    same=solve(atoms,K,within_same_bin=True)
    full=solve(atoms,K,within_same_bin=False)
    C=fraction(C)
    if C<0:raise ValueError('negative C')
    if full['N']!=same['N'] or full['L']!=same['L']:
        raise AssertionError('INCONSISTENT_GROUP_SUMS')
    D=(same['L']+full['S'])/2
    new_bound=min(D,(same['L']+same['S']+C)/2)
    return { 'S':same['S'],'M':full['S'],'L':same['L'],'N':same['N'],
             'D':D,'C':C,'d_max_necessary':new_bound,
             'old_S_zero_recovery':same['S']==0,
             'scope':'NECESSARY_OUTER_BOUND_ONLY' }
