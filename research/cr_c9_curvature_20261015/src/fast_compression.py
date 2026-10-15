"""Heap-accelerated *equivalent* greedy compression for frozen-neutral ray lanes.

Reference: compressed_cohorts.CompressedCohortTransport.compress, unchanged.
The score for a pair depends only on its two current cohorts, frozen-neutral
inputs, forecast range, and fixed budgets. Its score is NOT affected by the
remaining global budget, only its admissibility is. Once a candidate exceeds a
budget it can be discarded permanently, because spent budget only increases.

Adjacent links plus generation counters let us update at most two new pairs after
an accepted merge: O(N log N) pair work rather than repeatedly rescanning every
surviving adjacent pair. Identical left-to-right deterministic tie policy.

No independent chemical/gas evolution or full-history error is certified here.
"""
from __future__ import annotations
from dataclasses import dataclass
from heapq import heappush, heappop
from math import isfinite
from typing import Sequence
from compressed_cohorts import (CompressedCohortTransport, CompressionHold,
    CompressionCertificate, one_step_pair_bounds, _validate_neutrals, _total_moments)


@dataclass
class _Node:
    energy: float
    count: float
    order: int
    prev: '_Node | None' = None
    next: '_Node | None' = None
    generation: int = 0
    alive: bool = True


class HeapCompressedCohortTransport(CompressedCohortTransport):
    """Drop-in accelerated compressor with reference parity and transactional holds."""

    _pair_bounds=staticmethod(one_step_pair_bounds)
    _accum=staticmethod(lambda a,b: a+b)

    def compress(self, neutrals_cm3: Sequence[float], dt_s: float,
                 min_future_redshift_ratio: float = 1.,
                 event_abs_budget: float = .01,
                 heat_abs_budget_eV: float = .1):
        nn = _validate_neutrals(neutrals_cm3, dt_s)
        if any(not isfinite(v) or v<0 for v in (event_abs_budget,heat_abs_budget_eV)):
            raise ValueError('finite nonnegative budgets required')
        if not isfinite(min_future_redshift_ratio) or not 0<min_future_redshift_ratio<=1:
            raise ValueError('invalid redshift forecast')
        initial = sorted((float(e),float(n)) for e,n in self.cohorts if n>0)
        n_initial=len(initial)
        n_left=n_initial
        moments_before=_total_moments(initial)
        spent_e=[0.]*3;spent_h=[0.]*3
        merges=0
        nodes=[_Node(e,n,j) for j,(e,n) in enumerate(initial)]
        for i,node in enumerate(nodes):
            if i:node.prev=nodes[i-1]
            if i+1<len(nodes):node.next=nodes[i+1]
        heap=[]

        def offer(left:_Node|None):
            if left is None or not left.alive or left.next is None:return
            right=left.next
            if not right.alive:raise ArithmeticError('invalid adjacency')
            try:
                eb,hb=self._pair_bounds(left.energy,left.count,right.energy,right.count,
                                            nn,dt_s,min_future_redshift_ratio)
            except CompressionHold:
                return
            score=max(max(eb,default=0.)/(event_abs_budget or 1),
                      max(hb,default=0.)/(heat_abs_budget_eV or 1))
            heappush(heap,(score,right.energy-left.energy,left.order,
                           left.generation,right.generation,left,right,eb,hb))

        # NOTE heapq only compares Node if all previous tuple fields tie. Unique
        # left.order (initial rank) makes that impossible for live candidates.
        for node in nodes[:-1]:offer(node)
        while n_left>self.max_cohorts:
            choice=None
            while heap:
                score,gap,order,lg,rg,left,right,eb,hb=heappop(heap)
                if not (left.alive and right.alive and left.next is right and
                        right.prev is left and left.generation==lg and right.generation==rg):
                    continue
                # Once budget is exceeded it cannot become feasible later.
                if any(self._accum(spent_e[k],eb[k])>event_abs_budget for k in range(3)):continue
                if any(self._accum(spent_h[k],hb[k])>heat_abs_budget_eV for k in range(3)):continue
                choice=(left,right,eb,hb)
                break
            if choice is None:
                raise CompressionHold(f'HOLD_BUDGET_OR_THRESHOLD target={self.max_cohorts} '
                                      f'currently={n_left} n_initial={n_initial}')
            left,right,eb,hb=choice
            n=left.count+right.count
            left.energy=(left.count*left.energy+right.count*right.energy)/n
            left.count=n
            left.generation+=1
            nxt=right.next
            left.next=nxt
            if nxt:nxt.prev=left
            right.alive=False
            right.generation+=1
            n_left-=1;merges+=1
            for k in range(3):spent_e[k]=self._accum(spent_e[k],eb[k]);spent_h[k]=self._accum(spent_h[k],hb[k])
            offer(left.prev)
            offer(left)
        out=[]
        node=nodes[0] if nodes else None
        while node is not None:
            out.append((node.energy,node.count));node=node.next
        if len(out)!=n_left:raise ArithmeticError('linked cohort count disagreement')
        after=_total_moments(out)
        if not(abs(moments_before[0]-after[0])<=3e-13*max(moments_before[0],1) and
               abs(moments_before[1]-after[1])<=3e-13*max(moments_before[1],1)):
            raise ArithmeticError('number or energy moment changed')
        certificate=CompressionCertificate(n_initial,len(out),merges,
            tuple(spent_e),tuple(spent_h),min_future_redshift_ratio,nn,dt_s)
        self.cohorts=out
        self.last_certificate=certificate
        return certificate
