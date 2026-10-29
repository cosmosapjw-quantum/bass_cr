"""Exact Ferrers-prefix reduction of *original* high-low dual inequalities.

This is a dual-certificate accelerator only, not an altered optimization LP,
physical event kernel, or replacement for exact primal/zero-gap verification.
Every zero-mass atom and logically admissible original edge is included.
"""
from bisect import bisect_right
from fractions import Fraction as F


class DualPrefixOracle:
    """Precompute exact high/bin prefix support; certify every original dual edge.

    For each high h and low birth-bin b, E_l <= K-E_h selects a prefix.
    As chi(h,b) is constant throughout it, min_j p_l suffices. An exact
    representative failing original pair is returned if the test fails.
    """
    def __init__(self, atoms, K):
        atoms = tuple(atoms)
        self.low = {}
        for a in atoms:
            if 2*a.energy <= K:
                self.low.setdefault(a.bin, []).append(a)
        self.energy = {}
        for b, group in self.low.items():
            group.sort(key=lambda a: (a.energy, str(a.key)))
            self.energy[b] = [a.energy for a in group]
        self.queries = []
        self.logical_edges = 0
        for h in atoms:
            if 2*h.energy <= K:
                continue
            for b, low_energies in self.energy.items():
                k = bisect_right(low_energies, K-h.energy)
                self.logical_edges += k
                if k:
                    self.queries.append((h.key, h.bin != b, b, k))
        self.prefix_constraints = len(self.queries)

    def verify(self, prices, lam):
        """Return (original logical edge count, grouped inequality count).

        The nonnegativity of prices and lambda is checked separately by the
        caller; no float arithmetic or tolerance is used here.
        """
        prefix_min = {}
        for b, group in self.low.items():
            mins = []
            pmin = None
            witness = None
            for a in group:
                p = prices[a.key]
                if pmin is None or p < pmin:
                    pmin, witness = p, a.key
                mins.append((pmin, witness))
            prefix_min[b] = mins
        for high_key, is_cross_bin, b, k in self.queries:
            p_low, low_key = prefix_min[b][k-1]
            if prices[high_key] + p_low + lam*int(is_cross_bin) < 1:
                raise AssertionError(('UNCOMPRESSED_DUAL_EDGE_FAIL', high_key, low_key))
        return self.logical_edges, self.prefix_constraints


def explicit_original_dual_check(atoms, K, prices, lam):
    """Slow independent literal enumeration, for differential testing only."""
    highs = [a for a in atoms if 2*a.energy > K]
    lows = [a for a in atoms if 2*a.energy <= K]
    count = 0
    for h in highs:
        for l in lows:
            if h.energy+l.energy <= K:
                count += 1
                if prices[h.key]+prices[l.key]+lam*int(h.bin != l.bin) < 1:
                    raise AssertionError(('UNCOMPRESSED_DUAL_EDGE_FAIL', h.key, l.key))
    return count
