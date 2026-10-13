"""Exact finite atomic branch continuation for a source-bound reaction path.

The path parameter is an event extent, not an exact solution of the kinetic
ODE. Every raw state is reconstructed from the immutable initial state.
All SI state values are Fractions; a source float is explicitly interpreted
as its finite binary rational, as in the accepted kernel adapter.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q
from typing import Mapping


@dataclass(frozen=True)
class AtomicRaw:
    base_count: Q
    base_energy: Q
    energies: tuple[Q, ...]
    weights: tuple[Q, ...]
    k_b: Q
    chi: Q

    def __post_init__(self):
        if not isinstance(self.k_b,Q) or not isinstance(self.chi,Q):
            raise TypeError("Use explicit exact constants")
        if self.base_count<=0 or self.base_energy<=0 or self.k_b<=0 or self.chi<Q(3,2):
            raise ValueError("Positive base inventory and chi >= 3/2 required")
        if len(self.energies)!=len(self.weights) or any(x<0 for x in self.weights):
            raise ValueError("Mismatched or negative atom weights")
        if any(w<=0 for w in self.energies) or any(a>=b for a,b in zip(self.energies,self.energies[1:])):
            raise ValueError("Distinct positive ordered support required")

    @property
    def c_v(self): return Q(3,2)*self.k_b

    @property
    def alpha(self): return self.chi*self.k_b

    def branch(self,k:int):
        if not 0<=k<=len(self.energies): raise ValueError("Invalid branch index")
        n=self.base_count+sum(self.weights[:k],Q(0))
        u=self.base_energy+sum((w*a for w,a in zip(self.energies[:k],self.weights[:k])),Q(0))
        t=u/(self.c_v*n); cut=self.alpha*t
        low=Q(0) if k==0 else self.energies[k-1]
        high=None if k==len(self.energies) else self.energies[k]
        return {"branch":k,"temperature":t,"cutoff":cut,"thermal_count":n,
                "thermal_energy":u,"active_count":sum(self.weights[k:],Q(0)),
                "active_energy":sum((w*a for w,a in zip(self.energies[k:],self.weights[k:])),Q(0)),
                "consistent":low<=cut and (high is None or cut<high)}

    def select_from(self,inherited:int):
        """Finite deterministic repair from the explicitly inherited branch.

        A lower violation triggers removal; an upper violation triggers addition.
        For chi>=3/2 these scans cannot reverse within one fixed raw state.
        This defines a branch-selection convention, not global EOS uniqueness.
        """
        current=self.branch(inherited); trace=[current]
        if inherited and current['cutoff']<self.energies[inherited-1]:
            while current['branch'] and current['cutoff']<self.energies[current['branch']-1]:
                current=self.branch(current['branch']-1);trace.append(current)
        else:
            while current['branch']<len(self.energies) and self.energies[current['branch']]<=current['cutoff']:
                current=self.branch(current['branch']+1);trace.append(current)
        if not current['consistent']: raise ArithmeticError("Finite scan failed")
        return current,trace


def raw_reaction_state(base:Mapping[str,Q],column:Mapping[str,Q],extent:Q):
    """A single common extent updates every ledger exactly once."""
    if extent<0: raise ValueError("Negative extent")
    state={k:Q(base.get(k,0))+Q(column.get(k,0))*extent for k in base.keys()|column.keys()}
    if any(v<0 for v in state.values()): raise ValueError("Reaction exhausted a donor")
    return state


def single_ion_step_for_extent(extent:Q,neutral_initial:Q,coefficient:Q,volume:Q=Q(1),parent_initial:Q=Q(1)):
    """Inverse of the self-consistent one-family capacity map, in seconds.

    f=coefficient*parent_initial*(neutral_initial-extent)/volume,
    xi=h f/[1+h f(1/parent_initial+1/neutral_initial)].
    """
    if min(neutral_initial,coefficient,volume,parent_initial)<=0 or extent<0:
        raise ValueError("Invalid positive reaction domain")
    d=1/parent_initial+1/neutral_initial
    if extent>=min(neutral_initial,1/d): raise ValueError("Extent outside finite-step branch")
    if extent==0:return Q(0)
    return extent*volume/(coefficient*parent_initial*(neutral_initial-extent)*(1-d*extent))
