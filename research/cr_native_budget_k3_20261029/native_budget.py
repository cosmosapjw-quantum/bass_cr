"""Exact rational source-locked high/low cross-budget frontier.

Conditional finite He event marginals only, not physical event rates. The two-pass
primal is certified only when it attains independently computed exact Hall dual
capacities S (same bin) and M (all bins). No generic two-pass theorem assumed.
"""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path
from typing import Iterable

SOURCE_SHA = '1c974c306b50f3deb86df712844f753b4402fb25e5dbc41c9a1de0254bf3ff47'
ATOM_DIGEST = '2cfca578701a2355fa6f1f3f1f8a27c211e81b9b488f65cef1e1a89e4dbc7690'
PARENT_S = F('323478918562118325/3064991081731777716716694054300618367237478244367204352')
PARENT_M = F('3456415883490050789/12259964326927110866866776217202473468949912977468817408')
K3 = F(3)


def exact(x):
    if type(x) is F:
        return x
    if type(x) in (int, str):
        return F(x)
    raise TypeError('Exact Fraction, int or rational string required; no implicit float')


@dataclass(frozen=True)
class Atom:
    key: str
    energy: F
    mass: F
    bin: int

    def __post_init__(self):
        if not isinstance(self.key, str) or not self.key or type(self.bin) is not int or self.bin < 0:
            raise ValueError('invalid key/bin')
        if type(self.energy) is not F or type(self.mass) is not F:
            raise TypeError('Atom energy and mass must be Fraction')
        if self.energy < 0 or self.mass < 0:
            raise ValueError('negative energy or mass')

    @classmethod
    def parse(cls, key, energy, mass, bin):
        return cls(key, exact(energy), exact(mass), bin)


def load_pr116_npz(path: str | Path) -> tuple[Atom, ...]:
    """Exact binary64 lift from original PR116 source; fail closed on byte drift."""
    import io
    import numpy as np
    raw = Path(path).read_bytes()
    if sha256(raw).hexdigest() != SOURCE_SHA:
        raise ValueError('SOURCE_NPZ_SHA256_MISMATCH')
    with np.load(io.BytesIO(raw), allow_pickle=False) as arr:
        energies = arr['energy_eV_with_cutoff']
        masses = arr['identified_A_He_m3_s2']
        if (len(energies) != 3201 or len(masses) != 3201 or
                energies.dtype != np.dtype('float64') or masses.dtype != np.dtype('float64')):
            raise ValueError('SOURCE_NPZ_SHAPE_OR_DTYPE_MISMATCH')
        if not np.isfinite(energies).all() or not np.isfinite(masses).all():
            raise ValueError('SOURCE_NONFINITE')
        atoms = []
        for i, (energy, mass) in enumerate(zip(energies, masses)):
            e = F.from_float(float(energy))
            w = F.from_float(float(mass))
            b = 0 if i == 0 else (1 if e <= 1 else (2 if e <= 3 else 3))
            key = 'cutoff_ghost' if i == 0 else f'active_{i:04d}'
            atoms.append(Atom(key, e, w, b))
    digest = sha256(json.dumps([[a.key, str(a.energy), str(a.mass), a.bin]
                                for a in atoms], sort_keys=True, separators=(',', ':'),
                               allow_nan=False).encode()).hexdigest()
    if digest != ATOM_DIGEST:
        raise ValueError('SOURCE_ATOM_DIGEST_MISMATCH')
    return tuple(atoms)


def greedy(high: Iterable[Atom], low: Iterable[Atom], K: F):
    """One exact maximum weighted matching on a nested energy graph."""
    hs = sorted((a for a in high if a.mass > 0), key=lambda a: (-a.energy, a.key))
    ls = sorted((a for a in low if a.mass > 0), key=lambda a: (a.energy, a.key))
    remain_low = [a.mass for a in ls]
    remain_high = {}
    events = []
    j = 0
    for h in hs:
        rem = h.mass
        while rem > 0 and j < len(ls) and h.energy + ls[j].energy <= K:
            value = min(rem, remain_low[j])
            if value > 0:
                events.append((h.key, ls[j].key, value))
                rem -= value
                remain_low[j] -= value
            if remain_low[j] == 0:
                j += 1
        remain_high[h.key] = rem
    return tuple(events), remain_high


def hall_cut(high: Iterable[Atom], low: Iterable[Atom], K: F):
    """Exact weighted Hall dual (0/1 vertex cover) on a Ferrers graph."""
    hs = sorted((a for a in high if a.mass > 0), key=lambda a: -a.energy)
    ls = sorted((a for a in low if a.mass > 0), key=lambda a: a.energy)
    H = sum((a.mass for a in hs), F(0))
    high_sum = low_sum = delta = F(0)
    threshold = None
    i = j = 0
    while i < len(hs):
        e = hs[i].energy
        while i < len(hs) and hs[i].energy == e:
            high_sum += hs[i].mass
            i += 1
        while j < len(ls) and ls[j].energy + e <= K:
            low_sum += ls[j].mass
            j += 1
        deficiency = high_sum - low_sum
        if deficiency > delta:
            delta = deficiency
            threshold = e
    cover_high = set(a.key for a in hs if threshold is None or a.energy < threshold)
    cover_low = set(a.key for a in ls if threshold is not None and a.energy <= K-threshold)
    value = H-delta
    cover_cost = sum((a.mass for a in hs if a.key in cover_high), F(0)) + sum(
        (a.mass for a in ls if a.key in cover_low), F(0))
    if value != cover_cost:
        raise AssertionError('HALL_DUAL_COST_MISMATCH')
    return {'value': value, 'threshold': threshold,
            'cover_high': cover_high, 'cover_low': cover_low, 'deficiency': delta}


def _dual(atoms: tuple[Atom, ...], K: F, same: bool):
    active = [a for a in atoms if a.mass > 0]
    high = [a for a in active if 2*a.energy > K]
    low = [a for a in active if 2*a.energy <= K]
    groups = sorted(set(a.bin for a in active)) if same else [None]
    prices = {a.key: 0 for a in atoms}
    total = F(0)
    cuts = []
    for b in groups:
        hh = [a for a in high if not same or a.bin == b]
        ll = [a for a in low if not same or a.bin == b]
        cut = hall_cut(hh, ll, K)
        total += cut['value']
        for key in cut['cover_high'] | cut['cover_low']:
            prices[key] = 1
        cuts.append({'bin': b, 'threshold': str(cut['threshold']) if cut['threshold'] is not None else None,
                     'deficiency': str(cut['deficiency']), 'value': str(cut['value'])})
    # Extend an active-graph cover to all original vertices. A zero-mass
    # vertex can receive price 1 at zero dual objective cost; this covers
    # otherwise missing original-graph constraints without changing value.
    all_high = [a for a in atoms if 2*a.energy > K]
    all_low = [a for a in atoms if 2*a.energy <= K]
    for h in all_high:
        for l in all_low:
            if h.energy + l.energy > K or (same and h.bin != l.bin):
                continue
            if prices[h.key] + prices[l.key] < 1:
                if h.mass == 0:
                    prices[h.key] = 1
                elif l.mass == 0:
                    prices[l.key] = 1
                else:
                    raise AssertionError('DUAL_EDGE_UNCOVERED')
    for h in all_high:
        for l in all_low:
            if h.energy + l.energy <= K and (not same or h.bin == l.bin):
                if prices[h.key] + prices[l.key] < 1:
                    raise AssertionError('FULL_ORIGINAL_DUAL_EDGE_UNCOVERED')
    obj = sum((a.mass * prices[a.key] for a in atoms), F(0))
    if obj != total:
        raise AssertionError('DUAL_VALUE_MISMATCH')
    return {'value': total, 'prices': prices, 'cuts': cuts}


def certify(atoms: Iterable[Atom], K=3, *, expected_S=None, expected_M=None):
    """Certify simultaneous S/M attainment; refuse if the source is incompatible.

    The general two-pass greedy algorithm is not assumed to be universally optimal.
    Exact Hall upper bounds certify both endpoints for the supplied finite source.
    """
    K = exact(K)
    if K < 0:
        raise ValueError('NEGATIVE_K')
    atoms = tuple(atoms)
    if any(type(a) is not Atom for a in atoms) or len({a.key for a in atoms}) != len(atoms):
        raise ValueError('DUPLICATE_OR_INVALID_ATOM')
    same_dual = _dual(atoms, K, True)
    full_dual = _dual(atoms, K, False)
    high = [a for a in atoms if a.mass > 0 and 2*a.energy > K]
    low = [a for a in atoms if a.mass > 0 and 2*a.energy <= K]
    same_events = []
    residual_high = {a.key: a.mass for a in high}
    for b in sorted(set(a.bin for a in atoms)):
        pairs, rem = greedy((a for a in high if a.bin == b),
                            (a for a in low if a.bin == b), K)
        same_events.extend(pairs)
        residual_high.update(rem)
    S = sum((e[2] for e in same_events), F(0))
    if S != same_dual['value']:
        raise AssertionError('S_PRIMAL_DUAL_GAP')
    eligible_high_bins = {a.bin for a in high if a.energy <= K}
    if len(eligible_high_bins) > 1:
        raise ValueError('CROSS_GREEDY_REQUIRES_ONE_ELIGIBLE_HIGH_BIN')
    if eligible_high_bins:
        hb = next(iter(eligible_high_bins))
        residual_atoms = [Atom(a.key, a.energy, residual_high[a.key], a.bin) for a in high]
        cross_events, _ = greedy(residual_atoms, (a for a in low if a.bin != hb), K)
    else:
        cross_events = ()
    R = sum((e[2] for e in cross_events), F(0))
    M = S + R
    if M != full_dual['value']:
        raise AssertionError('SIMULTANEOUS_S_M_ATTAINMENT_NOT_CERTIFIED')
    if expected_S is not None and S != exact(expected_S):
        raise AssertionError('EXPECTED_S_MISMATCH')
    if expected_M is not None and M != exact(expected_M):
        raise AssertionError('EXPECTED_M_MISMATCH')
    lookup = {a.key: a for a in atoms}
    if len(lookup) != len(atoms):
        raise AssertionError('ATOM_KEY_DUPLICATE')
    used = defaultdict(F)
    for hi, lo, v in tuple(same_events) + tuple(cross_events):
        h, l = lookup[hi], lookup[lo]
        if not (v > 0 and 2*h.energy > K and 2*l.energy <= K and
                h.energy + l.energy <= K):
            raise AssertionError('INVALID_EDGE_OR_MASS')
        used[hi] += v
        used[lo] += v
    if any(used[a.key] > a.mass for a in atoms):
        raise AssertionError('MARGINAL_EXCESS')
    if any(lookup[hi].bin != lookup[lo].bin for hi, lo, _ in same_events):
        raise AssertionError('SAME_BIN_SUPPORT_DEFECT')
    if any(lookup[hi].bin == lookup[lo].bin for hi, lo, _ in cross_events):
        raise AssertionError('CROSS_BIN_SUPPORT_DEFECT')
    N = sum((a.mass for a in atoms), F(0))
    L = sum((a.mass for a in low), F(0))
    return {'atoms': atoms, 'lookup': lookup, 'K': K, 'N': N, 'L': L,
            'S': S, 'M': M, 'R': R,
            'same_events': tuple(same_events), 'cross_events': tuple(cross_events),
            'same_dual': same_dual, 'full_dual': full_dual,
            'scope': 'EXACT_NATIVE_K3_BUDGET_FRONTIER_IF_ENDPOINT_CERTIFICATES_PASS'}


def witness(cert, cross_budget):
    """Construct full original-atom primal and dual certificate for any c>=0."""
    c = exact(cross_budget)
    if c < 0:
        raise ValueError('NEGATIVE_CROSS_BUDGET')
    S, M, R = cert['S'], cert['M'], cert['R']
    theta = min(F(1), c/R) if R else F(0)
    same_events = cert['same_events']
    cross_events = tuple((h, l, v*theta) for h, l, v in cert['cross_events'] if v*theta > 0)
    used = defaultdict(F)
    for h, l, v in same_events + cross_events:
        used[h] += v
        used[l] += v
    low_diagonal = []
    high_single = []
    for a in cert['atoms']:
        rem = a.mass-used[a.key]
        if rem < 0:
            raise AssertionError('NEGATIVE_RESIDUAL')
        if 2*a.energy <= cert['K']:
            if rem:
                low_diagonal.append((a.key, rem/2))
            if used[a.key]+2*(rem/2) != a.mass:
                raise AssertionError('LOW_MARGINAL_DEFECT')
        else:
            if rem:
                high_single.append((a.key, rem))
            if used[a.key]+rem != a.mass:
                raise AssertionError('HIGH_MARGINAL_DEFECT')
    cross_used = sum((v for _, _, v in cross_events), F(0))
    M_budget = sum((v for _, _, v in same_events+cross_events), F(0))
    d = M_budget + sum((v for _, v in low_diagonal), F(0))
    if cross_used > c or d != (cert['L']+M_budget)/2 or M_budget != min(M,S+c):
        raise AssertionError('FRONTIER_PRIMAL_DEFECT')
    # Explicit exact dual, including cross-budget multiplier.
    if c < R:
        lam = 1
        dual = cert['same_dual']
        dual_cost = S+c
    else:
        lam = 0
        dual = cert['full_dual']
        dual_cost = M
    prices = dual['prices']
    for h, l, _ in cert['same_events']+cert['cross_events']:
        if prices[h]+prices[l]+(lam if cert['lookup'][h].bin != cert['lookup'][l].bin else 0) < 1:
            raise AssertionError('DUAL_EDGE_DEFECT')
    if dual_cost != M_budget:
        raise AssertionError('BUDGETED_PRIMAL_DUAL_GAP')
    return {'c': c, 'cross_used': cross_used, 'M_budget': M_budget,
            'd_max': d, 'same_events': same_events, 'cross_events': cross_events,
            'low_diagonal': tuple(low_diagonal), 'high_single': tuple(high_single),
            'lambda': lam, 'dual_prices': prices, 'dual_cost': dual_cost,
            'primal_dual_gap': dual_cost-M_budget, 'N': cert['N'], 'L': cert['L']}


def native_summary(path, budgets=('0', '1/2', '1')):
    atoms = load_pr116_npz(path)
    cert = certify(atoms, 3, expected_S=PARENT_S, expected_M=PARENT_M)
    return {'source_sha256': SOURCE_SHA, 'atom_digest': ATOM_DIGEST,
            'K_eV': '3', 'N': str(cert['N']), 'L': str(cert['L']),
            'S': str(cert['S']), 'M': str(cert['M']), 'R': str(cert['R']),
            'S_events': len(cert['same_events']), 'cross_events': len(cert['cross_events']),
            'cuts_same': cert['same_dual']['cuts'], 'cuts_all': cert['full_dual']['cuts'],
            'frontier': [dict(c=str((v:=witness(cert,c))['c']),
                              cross_used=str(v['cross_used']), M_budget=str(v['M_budget']),
                              d_max=str(v['d_max']), lambda_dual=v['lambda'],
                              gap=str(v['primal_dual_gap'])) for c in budgets],
            'scope': cert['scope']}


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('source_npz', help='byte-identical original PR116 ATTRIBUTION_ARRAYS.npz')
    p.add_argument('--c', action='append', default=[], help='exact rational cross-budget in m^-3 s^-2')
    a = p.parse_args()
    print(json.dumps(native_summary(a.source_npz, a.c or ['0', str(PARENT_M-PARENT_S)]),
                     indent=2, sort_keys=True))
