"""Exact PHYS02 He event-measure lifts and once-only source-parent union.

This file reads a pinned saved attribution; it never imports a source fit,
projector, proton quadrature, transport or RR implementation. Conditional
event measures are witnesses, not measured helium exclusive cross sections.
"""
from dataclasses import dataclass
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import math

UNIT_ID = 'CR_PHYS02_HE_EVENT_UNION_V1'
STATE = 'CR_LOW_BIRTH_100K_CONDITIONAL_H1_HE4_FIXED_INVENTORY_V1'
FRAME = 'prescribed_gas_rest_frame_scalar'
SOURCE_SHA = '8fca44c378844029a72253179e557dfa97f6cca8e0f9d6e677d67919ca3797cf'
NPZ_SHA = '1c974c306b50f3deb86df712844f753b4402fb25e5dbc41c9a1de0254bf3ff47'
NB = F(8750, 47)
I1, I2 = F('24.59'), F('54.42')
EV_J = F('1.602176634e-19')
CUTOFF = F.from_float(.1)
T = F(10000000000)
SPECIES = ('n','H1I','H1II','DI','DII','TI','TII','He3I','He3II','He3III',
           'He4I','He4II','He4III','Li6I','Li6II','Li6III','Li6IV','Li7I','Li7II','Li7III','Li7IV')
MASSES = (1,1,1,2,2,3,3,3,3,3,4,4,4,6,6,6,6,7,7,7,7)
CHARGES = (0,0,1,0,1,0,1,0,1,2,0,1,2,0,1,2,3,0,1,2,3)
_ATTESTED_ACTUAL_DIGESTS = set()

def require(ok, reason):
    if not ok:
        raise ValueError(reason)

def exact(value):
    require(type(value) in (int, str, F), 'EXACT_FINITE_SCALAR_REQUIRED')
    try:
        return F(value)
    except (ValueError, ZeroDivisionError, OverflowError):
        raise ValueError('EXACT_FINITE_SCALAR_REQUIRED') from None

def lift_float(value):
    require(type(value) is float and math.isfinite(value), 'FINITE_BINARY64_REQUIRED')
    return F.from_float(value)

def serial(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(k): serial(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(v) for v in value]
    return value

def content_id(value):
    return hashlib.sha256(json.dumps(serial(value), sort_keys=True, separators=(',', ':')).encode()).hexdigest()

@dataclass(frozen=True)
class Atom:
    key: str
    energy_eV: F
    coefficient: F
    partition: int

@dataclass(frozen=True)
class Event:
    key: str
    electrons: tuple
    coefficient: F
    provenance: str = 'CONDITIONAL_MARGINAL_LIFT'

@dataclass(frozen=True)
class AtomBundle:
    atoms: tuple
    provenance_kind: str
    atom_content_sha256: str
    attribution_npz_sha256: str | None
    canonical_source_sha256: str | None

def atom_content_id(atoms):
    return content_id([(a.key, a.energy_eV, a.coefficient, a.partition) for a in atoms])

def validate_atoms(atoms):
    require(len(atoms) > 0, 'NONEMPTY_ATOM_DECLARATION_REQUIRED')
    require(len({a.key for a in atoms}) == len(atoms), 'DUPLICATE_ELECTRON_ATOM_KEY')
    for atom in atoms:
        require(type(atom.key) is str and bool(atom.key), 'ATOM_KEY_REQUIRED')
        require(isinstance(atom.energy_eV, F) and isinstance(atom.coefficient, F), 'EXACT_ATOM_SCALARS_REQUIRED')
        require(CUTOFF <= atom.energy_eV <= 10, 'NATIVE_SUPPORT_EXTENSION_REFUSED')
        require(atom.coefficient >= 0, 'NEGATIVE_ATOM_WEIGHT')
        require(type(atom.partition) is int and 0 <= atom.partition < 4, 'FOUR_BIRTH_PARTITIONS_REQUIRED')
        lo_hi = ((CUTOFF, CUTOFF), (CUTOFF, F(1)), (F(1), F(3)), (F(3), F(10)))
        lo, hi = lo_hi[atom.partition]
        require(atom.energy_eV == CUTOFF if atom.partition == 0 else lo < atom.energy_eV <= hi,
                'BIRTH_PARTITION_MISMATCH')

def fixture_source(atoms):
    atoms = tuple(atoms)
    validate_atoms(atoms)
    return AtomBundle(atoms, 'ALGEBRAIC_FIXTURE', atom_content_id(atoms), None, None)

def load_pinned_source(path):
    """Only this byte-verified loader attests stored PHYS02 atom identity.

    The process-local attestation and the immutable atom content digest prevent
    an arbitrary fixture from acquiring canonical provenance merely by copying
    a source-SHA label. They are scientific identity checks, not a sandbox.
    """
    raw = Path(path).read_bytes()
    require(hashlib.sha256(raw).hexdigest() == NPZ_SHA, 'ATTRIBUTION_NPZ_BYTE_IDENTITY_MISMATCH')
    import io
    import numpy as np
    with np.load(io.BytesIO(raw), allow_pickle=False) as data:
        energy = data['energy_eV_with_cutoff']
        weights = data['identified_A_He_m3_s2']
        require(energy.shape == (3201,) and weights.shape == (3201,), 'EXACT_3201_SOURCE_ATOMS_REQUIRED')
        require(energy.dtype == np.dtype('float64') and weights.dtype == np.dtype('float64'), 'STORED_BINARY64_REQUIRED')
        require(float(energy[0]) == .1 and float(energy[-1]) == 10., 'FIXED_SOURCE_ENDPOINTS_REQUIRED')
        require(bool(np.all(np.isfinite(energy))) and bool(np.all(np.diff(energy) > 0)), 'ORDERED_FINITE_SOURCE_REQUIRED')
        require(bool(np.all(np.isfinite(weights))) and bool(np.all(weights >= 0)), 'POSITIVE_FINITE_SOURCE_REQUIRED')
        atoms = tuple(Atom('cutoff_ghost' if i == 0 else f'active_{i:04d}',
                           lift_float(float(e)), lift_float(float(w)),
                           0 if i == 0 else (1 if e <= 1 else (2 if e <= 3 else 3)))
                      for i, (e, w) in enumerate(zip(energy, weights)))
    digest = atom_content_id(atoms)
    _ATTESTED_ACTUAL_DIGESTS.add(digest)
    return AtomBundle(atoms, 'STORED_PHYS02_MODEL_IDENTIFIED_HE_ATOMS', digest, NPZ_SHA, SOURCE_SHA)

def validate_source(source):
    require(type(source) is AtomBundle, 'ATOM_SOURCE_BUNDLE_REQUIRED')
    validate_atoms(source.atoms)
    require(atom_content_id(source.atoms) == source.atom_content_sha256, 'ATOM_PAYLOAD_CONTENT_MISMATCH')
    if source.provenance_kind == 'ALGEBRAIC_FIXTURE':
        require(source.attribution_npz_sha256 is None and source.canonical_source_sha256 is None,
                'FIXTURE_CANNOT_CLAIM_CANONICAL_SOURCE')
    else:
        require(source.provenance_kind == 'STORED_PHYS02_MODEL_IDENTIFIED_HE_ATOMS'
                and source.attribution_npz_sha256 == NPZ_SHA and source.canonical_source_sha256 == SOURCE_SHA,
                'SOURCE_PROVENANCE_MISMATCH')
        require(source.atom_content_sha256 in _ATTESTED_ACTUAL_DIGESTS, 'PINNED_LOADER_ATTESTATION_REQUIRED')

def validate_events(events, atoms):
    keys = {a.key for a in atoms}
    seen = set()
    for event in events:
        require(type(event) is Event, 'TYPED_EVENT_REQUIRED')
        require(type(event.key) is str and bool(event.key), 'EVENT_KEY_REQUIRED')
        require(event.key not in seen, 'DUPLICATE_EVENT_IN_KERNEL')
        seen.add(event.key)
        require(event.provenance == 'CONDITIONAL_MARGINAL_LIFT', 'ACTUAL_EXCLUSIVE_MEASURE_NOT_PROVIDED')
        require(isinstance(event.coefficient, F) and event.coefficient > 0, 'POSITIVE_EXACT_EVENT_WEIGHT_REQUIRED')
        require(type(event.electrons) is tuple and len(event.electrons) in (1, 2)
                and all(k in keys for k in event.electrons), 'EVENT_ELECTRON_SUPPORT_MISMATCH')

def marginal(events, atoms):
    validate_events(events, atoms)
    result = {a.key: F(0) for a in atoms}
    for event in events:
        for key in event.electrons:
            result[key] += event.coefficient
    return result

def single_lift(atoms):
    validate_atoms(atoms)
    return [Event('single:' + a.key, (a.key,), a.coefficient) for a in atoms if a.coefficient]

def diagonal_double_lift(atoms):
    validate_atoms(atoms)
    return [Event('diagonal:' + a.key, (a.key, a.key), a.coefficient / 2) for a in atoms if a.coefficient]

def half_shift_lift(atoms):
    """A sparse unordered lift from mass coordinates x and x + N/2.

    Consecutive partition blocks attain Cmax even in the dominant-bin case;
    any remaining self-pairs belong to total d, not to cross C.
    """
    validate_atoms(atoms)
    ordered = [a for _, a in sorted(enumerate(atoms), key=lambda item: (item[1].partition, item[0]))
               if a.coefficient]
    total = sum((a.coefficient for a in ordered), F(0))
    if not total:
        return []
    half = total / 2
    edges = [F(0)]
    for atom in ordered:
        edges.append(edges[-1] + atom.coefficient)
    breaks = {F(0), half}
    for edge in edges:
        if 0 < edge < half:
            breaks.add(edge)
        if 0 < edge - half < half:
            breaks.add(edge - half)
    cuts = sorted(breaks)
    i = j = 0
    result = []
    for left, right in zip(cuts, cuts[1:]):
        while edges[i + 1] <= left:
            i += 1
        while edges[j + 1] <= left + half:
            j += 1
        result.append(Event(f'halfshift:{len(result):05d}', (ordered[i].key, ordered[j].key), right - left))
    return result

def partition_masses(atoms):
    out = [F(0)] * 4
    for atom in atoms:
        out[atom.partition] += atom.coefficient
    return tuple(out)

def sharp_cross_bound(masses):
    masses = tuple(exact(x) for x in masses)
    require(bool(masses) and all(x >= 0 for x in masses), 'NONNEGATIVE_MARGINAL_MASSES_REQUIRED')
    total = sum(masses, F(0))
    return min(total / 2, total - max(masses))

def known_window_factor(window):
    require(type(window) in (tuple, list) and len(window) == 2, 'PROPER_WINDOW_REQUIRED')
    a, b = map(exact, window)
    require(0 <= a < b <= T, 'FINITE_KNOWN_PROPER_HISTORY_REQUIRED')
    return (b * b - a * a) / 2

def binding(window, source):
    validate_source(source)
    known_window_factor(window)
    return {'state_id': STATE, 'isotope': 'He4', 'parent_state': 'He4I', 'frame': FRAME,
            'clock': 'proper_s', 'proper_volume_mode': 'fixed', 'absolute_proper_volume_m3': None,
            'window': tuple(map(exact, window)), 'support_eV': (CUTOFF, F(10)),
            'inventory_authority': 'CONDITIONAL_100K', 'actual_exclusive_measure': None,
            'source_sha256': source.canonical_source_sha256,
            'attribution_npz_sha256': source.attribution_npz_sha256,
            'atom_content_sha256': source.atom_content_sha256, 'input_kind': source.provenance_kind}

def validate_binding(value, source):
    validate_source(source)
    require(set(value) == {'state_id','isotope','parent_state','frame','clock','proper_volume_mode',
                          'absolute_proper_volume_m3','window','support_eV','inventory_authority',
                          'actual_exclusive_measure','source_sha256','attribution_npz_sha256',
                          'atom_content_sha256','input_kind'}, 'UNEXPECTED_BINDING_FIELDS')
    require(value.get('state_id') == STATE and value.get('inventory_authority') == 'CONDITIONAL_100K', 'SAME_STATE_REQUIRED')
    require(value.get('isotope') == 'He4' and value.get('parent_state') == 'He4I', 'SOURCE_PARENT_ISOTOPE_STATE_MISMATCH')
    require(value.get('frame') == FRAME, 'MIXED_FRAME_REFUSED')
    require(value.get('clock') == 'proper_s', 'PROPER_CLOCK_REQUIRED')
    require(value.get('proper_volume_mode') == 'fixed' and value.get('absolute_proper_volume_m3') is None,
            'FIXED_DENSITY_SCOPE_REQUIRED')
    require(value.get('support_eV') == (CUTOFF, F(10)), 'NATIVE_SUPPORT_EXTENSION_REFUSED')
    require(value.get('actual_exclusive_measure') is None, 'UNVERIFIED_ACTUAL_MEASURE_CLAIM_REFUSED')
    require(value.get('source_sha256') == source.canonical_source_sha256
            and value.get('attribution_npz_sha256') == source.attribution_npz_sha256
            and value.get('atom_content_sha256') == source.atom_content_sha256
            and value.get('input_kind') == source.provenance_kind, 'SOURCE_BINDING_IDENTITY_MISMATCH')
    known_window_factor(value['window'])

def claims_by_partition(events, source, bound):
    validate_binding(bound, source)
    validate_events(events, source.atoms)
    part = {a.key: a.partition for a in source.atoms}
    return [{'partition': p, 'binding': dict(bound),
             'events': tuple(e for e in events if any(part[k] == p for k in e.electrons))}
            for p in range(4)]

def evaluate_event_set(events, atoms, selected, window):
    validate_events(events, atoms)
    factor = known_window_factor(window)
    require(len(selected) == len(set(selected)) and all(type(p) is int and 0 <= p < 4 for p in selected),
            'DISJOINT_PARTITION_SET_REQUIRED')
    amap = {a.key: a for a in atoms}
    s = p = d = parents = electrons = energy = F(0)
    for event in events:
        chosen = [amap[k] for k in event.electrons if amap[k].partition in selected]
        if not chosen:
            continue
        weight = event.coefficient * factor
        parents += weight
        electrons += len(chosen) * weight
        energy += sum((a.energy_eV for a in chosen), F(0)) * weight
        if len(event.electrons) == 1:
            s += weight
        elif len(chosen) == 1:
            p += weight
        else:
            d += weight
    ion = (-parents, s, p + d)
    require(sum(ion, F(0)) == 0 and ion[1] + 2 * ion[2] == electrons + p, 'NUCLEUS_OR_CHARGE_IDENTITY_FAILED')
    require(s + p + 2 * d == electrons and parents == electrons - d, 'EVENT_MARGINAL_IDENTITY_FAILED')
    return {'s': s, 'p': p, 'd': d, 'parents': parents, 'selected_electrons': electrons,
            'selected_energy_eV_m3': energy, 'ion_density_delta': ion,
            'ionic_charge_delta': ion[1] + 2 * ion[2],
            'recipient_chemical_eV_m3': I1 * ion[1] + (I1 + I2) * ion[2]}

def consume_event_union(claims, source, *, nb_m3, previous_windows=()):
    """Apply one exact source-parent union; overlapping time returns are refused.

    Event IDs can repeat across birth-partition claims inside this call. Every
    such claim must agree in content and include all selected incidences.
    This returns conditional source components, never a full coupled state.
    """
    require(bool(claims), 'NONEMPTY_CLAIMS_REQUIRED')
    validate_source(source)
    atoms = source.atoms
    first = claims[0]['binding']
    validate_binding(first, source)
    selected = []
    byid = {}
    amap = {a.key: a for a in atoms}
    for claim in claims:
        validate_binding(claim['binding'], source)
        require(claim['binding'] == first, 'MIXED_BINDING_OR_WINDOW_REFUSED')
        part = claim['partition']
        require(type(part) is int and 0 <= part < 4 and part not in selected, 'OVERLAPPING_PARTITION_CLAIMS_REFUSED')
        selected.append(part)
        validate_events(claim['events'], atoms)
        for event in claim['events']:
            require(any(amap[k].partition == part for k in event.electrons), 'EVENT_NOT_IN_CLAIMED_PARTITION')
            require(event.key not in byid or byid[event.key] == event, 'CONFLICTING_SAME_EVENT_ID')
            byid[event.key] = event
    a, b = first['window']
    for old in previous_windows:
        known_window_factor(old)
        c, d = map(exact, old)
        require(b <= c or d <= a, 'OVERLAPPING_TIME_RETURN_OR_REPLAY_REFUSED')
    claimkeys = {c['partition']: {e.key for e in c['events']} for c in claims}
    for event in byid.values():
        for part in selected:
            if any(amap[k].partition == part for k in event.electrons):
                require(event.key in claimkeys[part], 'INCOMPLETE_PARTITION_EVENT_CLAIM')
    events = list(byid.values())
    projected = marginal(events, atoms)
    require(all(projected[x.key] == x.coefficient for x in atoms if x.partition in selected),
            'SELECTED_SOURCE_MARGINAL_MISMATCH')
    combined = evaluate_event_set(events, atoms, selected, (a, b))
    require(combined['parents'] <= F(1085, 94) * F(99, 100), 'CONDITIONAL_NEUTRAL_INVENTORY_EXHAUSTED')
    pieces = [evaluate_event_set(c['events'], atoms, [c['partition']], (a, b)) for c in claims]
    require(sum((x['selected_electrons'] for x in pieces), F(0)) == combined['selected_electrons']
            and sum((x['selected_energy_eV_m3'] for x in pieces), F(0)) == combined['selected_energy_eV_m3'],
            'SELECTED_ELECTRON_PARTITION_ADDITIVITY_FAILED')
    cross = sum((x['parents'] for x in pieces), F(0)) - combined['parents']
    correction = (cross, F(0), -cross)
    naive = tuple(sum((x['ion_density_delta'][i] for x in pieces), F(0)) for i in range(3))
    require(tuple(naive[i] + correction[i] for i in range(3)) == combined['ion_density_delta'],
            'PARTITION_UNION_CORRECTION_FAILED')
    ion21 = [F(0)] * 21
    correction21 = [F(0)] * 21
    ion21[10:13] = combined['ion_density_delta']
    correction21[10:13] = correction
    require(sum(a * y for a, y in zip(MASSES, ion21)) == 0, 'BARYON_NUMBER_CHANGED')
    out = {'scope': 'CONDITIONAL_HE_SOURCE_EVENT_UNION', 'input_kind': source.provenance_kind,
           'atom_content_sha256': source.atom_content_sha256, 'attribution_npz_sha256': source.attribution_npz_sha256,
           'source_ion_density_delta21': ion21, 'correction_to_sum_of_partition_ion_density21': correction21,
           'cross_duplicate_parent_density': cross, 'union': combined, 'partition_returns': pieces,
           'chemical_correction_eV_m3': -(I1 + I2) * cross, 'ionic_charge_correction_m3': -2 * cross,
           'selected_electron_correction_m3': F(0), 'selected_kinetic_correction_eV_m3': F(0),
           'RR_correction': F(0), 'retained_photon_correction': F(0), 'new_source_normalization_applied': False,
           'nb_m3': nb_m3, 'native_source_species21': None, 'native_species_correction21': None,
           'native_ionic_charge_correction': None, 'selected_birth_zeta': None,
           'selected_birth_wnt_J_per_baryon': None, 'actual_full_native25': None, 'actual_T': None,
           'actual_donor_work': None, 'outside_partner_response': None, 'actual_exclusive_event_measure': None,
           'global_physical_error': None, 'full_physical_consumer_activation': False,
           'accepted_windows': [list(x) for x in previous_windows] + [[a, b]],
           'composition_rule': 'Use union source species OR corrected partition sum once; attach saved RR once; do not add this full source contribution again to an existing source return.'}
    if nb_m3 is not None:
        nb = exact(nb_m3)
        require(nb == NB, 'EXPLICIT_SAME_STATE_NB_REQUIRED')
        out.update(native_source_species21=[x / nb for x in ion21],
                   native_species_correction21=[x / nb for x in correction21],
                   native_ionic_charge_correction=-2 * cross / nb,
                   selected_birth_zeta=combined['selected_electrons'] / nb,
                   selected_birth_wnt_J_per_baryon=combined['selected_energy_eV_m3'] * EV_J / nb)
    return out

def write_new(path, value):
    path = Path(path)
    raw = (json.dumps(serial(value), indent=2, allow_nan=False) + '\n').encode()
    with path.open('xb') as stream:
        stream.write(raw)
    return {'path': str(path), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
