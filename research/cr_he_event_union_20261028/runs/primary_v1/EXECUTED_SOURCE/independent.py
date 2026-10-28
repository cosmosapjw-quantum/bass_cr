"""Independent C9 reference for the saved PHYS02 He event-union return.

No production module is imported.  The saved binary64 atoms are lifted exactly,
the published event witness is read as data, and He transitions are accumulated
from event incidences.  The small multigraph oracle enumerates all six cross-edge
multiplicities by dynamic programming; it does not use the proposed bound to
construct an optimum.  Execute only through the parent's bounded runner.
"""
import argparse
from fractions import Fraction as Q
from functools import lru_cache
import hashlib
import io
from itertools import combinations, product
import json
import os
from pathlib import Path
import sys

UNIT = 'CR_PHYS02_HE_EVENT_UNION_V1'
NPZ_SHA = '1c974c306b50f3deb86df712844f753b4402fb25e5dbc41c9a1de0254bf3ff47'
SOURCE_SHA = '8fca44c378844029a72253179e557dfa97f6cca8e0f9d6e677d67919ca3797cf'
INPUT_KIND = 'STORED_PHYS02_MODEL_IDENTIFIED_HE_ATOMS'
NB = Q(8750, 47)
FINAL_T = Q(10**10)
FINAL_FACTOR = FINAL_T**2 / 2
CHEMICAL = (Q(0), Q(2459, 100), Q(7901, 100))
EV_J = Q('1.602176634e-19')


def plain(value):
    if isinstance(value, Q):
        return str(value)
    if isinstance(value, dict):
        return {str(k): plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [plain(v) for v in value]
    return value


def digest(value):
    return hashlib.sha256(json.dumps(plain(value), sort_keys=True,
                                    separators=(',', ':')).encode()).hexdigest()


def read_json(path):
    raw = Path(path).read_bytes()
    return json.loads(raw), {'path': str(path), 'bytes': len(raw),
                            'sha256': hashlib.sha256(raw).hexdigest()}


def number(value):
    if type(value) not in (str, int):
        raise ValueError('EXACT_SERIALIZED_NUMBER_REQUIRED')
    return Q(value)


def empty_return():
    return {**dict.fromkeys(('s', 'p', 'd', 'parents', 'selected_electrons',
                            'selected_energy_eV_m3'), Q(0)),
            'ion_density_delta': [Q(0), Q(0), Q(0)]}


def incidence_reference(events, energy, partition):
    """Direct HeI -> HeII/HeIII transitions, before one time integration."""
    union = empty_return()
    pieces = [empty_return() for _ in range(4)]
    cross = Q(0)

    def add(target, chosen, multiplicity, weight):
        target['parents'] += weight
        target['selected_electrons'] += len(chosen) * weight
        target['selected_energy_eV_m3'] += sum((energy[k] for k in chosen), Q(0)) * weight
        # The daughter is fixed by the full event, including any partner leg.
        target['ion_density_delta'][0] -= weight
        target['ion_density_delta'][multiplicity] += weight
        topology = 's' if multiplicity == 1 else ('d' if len(chosen) == 2 else 'p')
        target[topology] += weight

    for _, legs, weight in events:
        add(union, legs, len(legs), weight)
        incident = set(partition[k] for k in legs)
        for part in incident:
            chosen = tuple(k for k in legs if partition[k] == part)
            add(pieces[part], chosen, len(legs), weight)
        if len(incident) == 2:
            cross += weight

    for record in [union] + pieces:
        for name in ('s', 'p', 'd', 'parents', 'selected_electrons', 'selected_energy_eV_m3'):
            record[name] *= FINAL_FACTOR
        record['ion_density_delta'] = tuple(x * FINAL_FACTOR for x in record['ion_density_delta'])
        ion = record['ion_density_delta']
        record['ionic_charge_delta'] = sum(Q(i) * ion[i] for i in range(3))
        record['recipient_chemical_eV_m3'] = sum(CHEMICAL[i] * ion[i] for i in range(3))
    return union, pieces, cross * FINAL_FACTOR


EDGES = tuple(combinations(range(4), 2))


@lru_cache(maxsize=None)
def cross_multigraph(edge_index, capacities):
    """Maximize half-unit cross-pair mass by exhaustive edge assignments.

    Each edge multiplicity consumes that many half-units from each endpoint.
    The returned count is the number of feasible edge-assignment completions;
    unused capacities are single events. No analytic bound enters this oracle.
    """
    if edge_index == len(EDGES):
        return 0, (), 1
    i, j = EDGES[edge_index]
    best, witness, count = -1, (), 0
    for multiplicity in range(min(capacities[i], capacities[j]) + 1):
        remaining = list(capacities)
        remaining[i] -= multiplicity
        remaining[j] -= multiplicity
        tail_best, tail_witness, tail_count = cross_multigraph(edge_index + 1, tuple(remaining))
        count += tail_count
        if multiplicity + tail_best > best:
            best = multiplicity + tail_best
            witness = (multiplicity,) + tail_witness
    return best, witness, count


def main(outdir, npz_path=None, primary_path=None, witness_path=None):
    outdir = Path(outdir)
    if not outdir.is_dir():
        raise ValueError('RUNNER_CREATED_OUTPUT_DIRECTORY_REQUIRED')
    unit = Path(os.environ.get('CR_UNIT_ROOT', str(Path(__file__).resolve().parents[1])))
    npz_path = Path(npz_path) if npz_path else unit.parents[1] / 'research/cr_parent_event_native25_20261028/runs/prepare_v1/ATTRIBUTION_ARRAYS.npz'
    primary_path = Path(primary_path) if primary_path else unit / 'runs/primary_v1/RESULT.json'
    witness_path = Path(witness_path) if witness_path else primary_path.parent / 'HALFSHIFT_EVENT_WITNESS.json'
    checks, graph_rows, identities = [], [], {}

    def check(name, condition, **detail):
        row = {'id': name, 'pass': bool(condition)}
        if detail:
            row.update(plain(detail))
        checks.append(row)

    def equal(name, actual, expected):
        ok = actual == expected
        check(name, ok, **({} if ok else {'actual': actual, 'expected': expected}))

    try:
        contract, identities['contract'] = read_json(unit / 'CONTRACT.json')
        equal('contract.unit', contract['unit'], UNIT)
        equal('contract.npz_pin', contract['source']['attribution_npz_sha256'], NPZ_SHA)
        equal('contract.canonical_source_pin', contract['source']['actual_JSON_sha256'], SOURCE_SHA)
        equal('contract.same_state_nb', number(contract['state']['nb_m3']), NB)
        equal('contract.proper_history', contract['source']['proper_history_s'], [0, 10**10])
        equal('contract.native_binding', tuple(number(x) for x in contract['state']['native_binding_eV']),
              (CHEMICAL[1], CHEMICAL[2] - CHEMICAL[1]))

        raw = npz_path.read_bytes()
        identities['attribution_npz'] = {'path': str(npz_path), 'bytes': len(raw),
                                         'sha256': hashlib.sha256(raw).hexdigest()}
        equal('input.exact_npz_bytes', identities['attribution_npz']['sha256'], NPZ_SHA)
        if identities['attribution_npz']['sha256'] != NPZ_SHA:
            raise ValueError('PINNED_INPUT_MISMATCH')
        import numpy as np
        with np.load(io.BytesIO(raw), allow_pickle=False) as arrays:
            ee = arrays['energy_eV_with_cutoff']
            ww = arrays['identified_A_He_m3_s2']
            equal('input.atom_shapes', (ee.shape, ww.shape), ((3201,), (3201,)))
            equal('input.binary64_types', (str(ee.dtype), str(ww.dtype)), ('float64', 'float64'))
            check('input.finite_ordered_positive', bool(np.all(np.isfinite(ee)))
                  and bool(np.all(np.diff(ee) > 0)) and bool(np.all(np.isfinite(ww)))
                  and bool(np.all(ww > 0)))
            energies = [Q.from_float(float(x)) for x in ee]
            weights = [Q.from_float(float(x)) for x in ww]
        equal('input.endpoints', (energies[0], energies[-1]), (Q.from_float(.1), Q(10)))
        keys = ['cutoff_ghost'] + [f'active_{i:04d}' for i in range(1, len(weights))]
        parts = [0 if i == 0 else 1 if e <= 1 else 2 if e <= 3 else 3 for i, e in enumerate(energies)]
        energy, weight, partition = dict(zip(keys, energies)), dict(zip(keys, weights)), dict(zip(keys, parts))
        atom_digest = digest(list(zip(keys, energies, weights, parts)))
        counts = [sum((w for w, p in zip(weights, parts) if p == b), Q(0)) for b in range(4)]
        kinetic = [sum((w * e for w, e, p in zip(weights, energies, parts) if p == b), Q(0)) for b in range(4)]
        total, total_energy = sum(counts, Q(0)), sum(kinetic, Q(0))
        bound = min(total / 2, total - max(counts))

        primary, identities['primary_result'] = read_json(primary_path)
        witness, identities['halfshift_witness'] = read_json(witness_path)
        equal('primary.status', primary['status'], 'PASS_SCOPED')
        equal('primary.unit', primary['unit'], UNIT)
        equal('primary.npz_identity', primary['input']['sha256'], NPZ_SHA)
        equal('primary.source_identity', primary['input']['canonical_source_sha256'], SOURCE_SHA)
        equal('primary.atom_content', primary['input']['atom_content_sha256'], atom_digest)
        equal('primary.provenance', primary['input']['attribution_provenance'], INPUT_KIND)
        equal('primary.partition_atom_counts', primary['partition_atom_counts'], [parts.count(i) for i in range(4)])
        equal('primary.partition_counts', tuple(number(x) for x in primary['coefficient_count_m3_s2']), tuple(counts))
        equal('primary.partition_energies', tuple(number(x) for x in primary['coefficient_energy_eV_m3_s2']), tuple(kinetic))
        equal('primary.cross_bound', number(primary['coefficient_cross_bound_m3_s2']), bound)
        equal('witness.file_sha256', primary['witness_file']['sha256'], identities['halfshift_witness']['sha256'])
        equal('witness.file_bytes', primary['witness_file']['bytes'], identities['halfshift_witness']['bytes'])
        equal('witness.kind', witness['kind'], 'CONDITIONAL_MARGINAL_LIFT')
        equal('witness.unit', witness['unit'], UNIT)
        equal('witness.npz_pin', witness['attribution_npz_sha256'], NPZ_SHA)
        equal('witness.atom_content', witness['atom_content_sha256'], atom_digest)
        equal('witness.actual_exclusive_stays_null', witness['actual_exclusive_measure'], None)
        events = []
        seen = set()
        reconstructed = dict.fromkeys(keys, Q(0))
        symmetric_first = dict.fromkeys(keys, Q(0))
        Dparts = [[Q(0) for _ in range(4)] for _ in range(4)]
        for event in witness['events']:
            event_id, legs, w = event['event_id'], tuple(event['electron_atom_ids']), number(event['event_coefficient'])
            if (type(event_id) is not str or not event_id or event_id in seen or len(legs) != 2
                    or any(k not in weight for k in legs) or w <= 0
                    or event['provenance'] != 'CONDITIONAL_MARGINAL_LIFT'):
                raise ValueError('INVALID_CONDITIONAL_DOUBLE_EVENT_WITNESS')
            seen.add(event_id)
            events.append((event_id, legs, w))
            for k in legs:
                reconstructed[k] += w
                symmetric_first[k] += w / 2
            p, q = (partition[k] for k in legs)
            Dparts[p][q] += w / 2
            Dparts[q][p] += w / 2
        for k in keys:
            equal('marginal.' + k, reconstructed[k], weight[k])
        check('symmetric_measure.two_first_marginals', all(2 * symmetric_first[k] == reconstructed[k] for k in keys))
        equal('symmetric_measure.partition_marginals', tuple(2 * sum(row, Q(0)) for row in Dparts), tuple(counts))
        equal('symmetric_measure.total_D', sum((sum(row, Q(0)) for row in Dparts), Q(0)), total / 2)
        equal('symmetric_measure.cross_mass', 2 * sum((Dparts[i][j] for i, j in EDGES), Q(0)), bound)
        equal('witness.kernel_content', digest(events), primary['witnesses']['halfshift']['kernel_content_sha256'])

        kernels = {'single': [('single:' + k, (k,), weight[k]) for k in keys if weight[k]],
                   'diagonal': [('diagonal:' + k, (k, k), weight[k] / 2) for k in keys if weight[k]],
                   'halfshift': events}
        for name, kernel in kernels.items():
            label = name + '.'
            record = primary['witnesses'][name]
            actual = record['consumer']
            union, pieces, cross = incidence_reference(kernel, energy, partition)
            equal(label + 'event_count', record['event_atoms'], len(kernel))
            equal(label + 'kernel_content', record['kernel_content_sha256'], digest(kernel))
            equal(label + 'provenance', actual['input_kind'], INPUT_KIND)
            equal(label + 'atom_identity', actual['atom_content_sha256'], atom_digest)
            equal(label + 'npz_identity', actual['attribution_npz_sha256'], NPZ_SHA)
            for b, reference in [('union', union)] + [(str(i), p) for i, p in enumerate(pieces)]:
                reported = actual['union'] if b == 'union' else actual['partition_returns'][int(b)]
                for field, expected in reference.items():
                    got = tuple(number(x) for x in reported[field]) if field == 'ion_density_delta' else number(reported[field])
                    equal(label + b + '.' + field, got, expected)
            naive_ions = tuple(sum((p['ion_density_delta'][i] for p in pieces), Q(0)) for i in range(3))
            correction = tuple(union['ion_density_delta'][i] - naive_ions[i] for i in range(3))
            equal(label + 'direct_incidence_correction', correction, (cross, Q(0), -cross))
            equal(label + 'cross_duplicate_count', number(actual['cross_duplicate_parent_density']), cross)
            equal(label + 'sharp_endpoint', cross, bound * FINAL_FACTOR if name == 'halfshift' else Q(0))
            equal(label + 'selected_count', union['selected_electrons'], total * FINAL_FACTOR)
            equal(label + 'selected_energy', union['selected_energy_eV_m3'], total_energy * FINAL_FACTOR)
            ion21 = [Q(0)] * 10 + list(union['ion_density_delta']) + [Q(0)] * 8
            corr21 = [Q(0)] * 10 + list(correction) + [Q(0)] * 8
            for field, expected in [('source_ion_density_delta21', ion21),
                                    ('correction_to_sum_of_partition_ion_density21', corr21),
                                    ('native_source_species21', [x / NB for x in ion21]),
                                    ('native_species_correction21', [x / NB for x in corr21])]:
                equal(label + field, tuple(number(x) for x in actual[field]), tuple(expected))
            chemical_difference = union['recipient_chemical_eV_m3'] - sum((p['recipient_chemical_eV_m3'] for p in pieces), Q(0))
            charge_difference = union['ionic_charge_delta'] - sum((p['ionic_charge_delta'] for p in pieces), Q(0))
            for field, expected in [('chemical_correction_eV_m3', chemical_difference),
                                    ('ionic_charge_correction_m3', charge_difference),
                                    ('native_ionic_charge_correction', charge_difference / NB),
                                    ('selected_birth_zeta', union['selected_electrons'] / NB),
                                    ('selected_birth_wnt_J_per_baryon', union['selected_energy_eV_m3'] * EV_J / NB),
                                    ('selected_electron_correction_m3', Q(0)),
                                    ('selected_kinetic_correction_eV_m3', Q(0)),
                                    ('RR_correction', Q(0)), ('retained_photon_correction', Q(0)), ('nb_m3', NB)]:
                equal(label + field, number(actual[field]), expected)
            equal(label + 'chemical_sign_and_coefficient', chemical_difference, -Q(7901, 100) * cross)
            equal(label + 'charge_sign_and_factor_two', charge_difference, -2 * cross)
            equal(label + 'nucleus_conservation', sum(union['ion_density_delta'], Q(0)), Q(0))
            check(label + 'finite_inventory', union['parents'] <= Q(1085, 94) * Q(99, 100))
            for field in ('actual_full_native25', 'actual_T', 'actual_donor_work', 'outside_partner_response',
                          'actual_exclusive_event_measure', 'global_physical_error'):
                equal(label + field, actual[field], None)
            equal(label + 'physical_activation', actual['full_physical_consumer_activation'], False)
            equal(label + 'normalization_not_reapplied', actual['new_source_normalization_applied'], False)
        check('double_count_distinct_from_cross', number(primary['witnesses']['diagonal']['consumer']['union']['d']) > 0
              and number(primary['witnesses']['diagonal']['consumer']['cross_duplicate_parent_density']) == 0)

        for field, expected in [('N_He_m3', total * FINAL_FACTOR), ('U_He_eV_m3', total_energy * FINAL_FACTOR),
                                ('Cmax_m3', bound * FINAL_FACTOR), ('Cmax_over_N', bound / total)]:
            equal('final.' + field, number(primary['final_prefix'][field]), expected)
        equal('final.chemical_interval', tuple(number(x) for x in primary['final_prefix']['chemical_correction_interval_eV_m3']),
              (-CHEMICAL[2] * bound * FINAL_FACTOR, Q(0)))
        equal('final.native_interval', tuple(number(x) for x in primary['final_prefix']['native_HeI_correction_interval']),
              (Q(0), bound * FINAL_FACTOR / NB))
        bin_factors = []
        for mode, rows in [('prefix', primary['prefixes']), ('bin', primary['disjoint_birth_time_bins'])]:
            equal('time.' + mode + '.count', len(rows), 4)
            for i, row in enumerate(rows):
                start = Q(0) if mode == 'prefix' else FINAL_T * i / 4
                end = FINAL_T * (i + 1) / 4
                expected_factor = (end**2 - start**2) / 2
                equal(f'time.{mode}.{i}.window', tuple(number(x) for x in row['window_s']), (start, end))
                for field, expected in [('factor_s2', expected_factor), ('N_He_m3', total * expected_factor),
                                        ('U_He_eV_m3', total_energy * expected_factor)]:
                    equal(f'time.{mode}.{i}.{field}', number(row[field]), expected)
                equal(f'time.{mode}.{i}.cross_interval', tuple(number(x) for x in row['cross_bound_m3']),
                      (Q(0), bound * expected_factor))
                if mode == 'bin':
                    bin_factors.append(expected_factor)
        equal('time.disjoint_additivity', sum(bin_factors, Q(0)), FINAL_FACTOR)
        check('time.prefixes_nonadditive', sum((number(x['factor_s2']) for x in primary['prefixes']), Q(0)) != FINAL_FACTOR)
        for field in ('actual_Ccross', 'actual_exclusive_measure', 'actual_full_native25'):
            equal('primary.' + field, primary[field], None)
        equal('primary.physical_activation', primary['physical_activation'], False)
        equal('primary.source_replays', primary['old_source_fit_or_projection_calls'], 0)
        equal('primary.RR_replays', primary['old_RR_calls'], 0)

        for masses in product(range(3), repeat=4):
            capacities = tuple(2 * n for n in masses)
            max_units, assignments, feasible_count = cross_multigraph(0, capacities)
            optimum = Q(max_units, 2)
            expected = min(Q(sum(masses), 2), Q(sum(masses) - max(masses)))
            degrees = [sum(m for (i, j), m in zip(EDGES, assignments) if v in (i, j)) for v in range(4)]
            equal('graph.bound.' + ''.join(map(str, masses)), optimum, expected)
            check('graph.feasibility.' + ''.join(map(str, masses)), all(d <= c for d, c in zip(degrees, capacities))
                  and sum(assignments) == max_units)
            graph_rows.append({'marginal_masses': masses, 'edge_multiplicities_in_half_units': assignments,
                               'single_residual_half_units': [c - d for c, d in zip(capacities, degrees)],
                               'maximum_cross_mass': optimum, 'sharp_bound': expected,
                               'feasible_multigraph_assignments': feasible_count})
    except Exception as exc:
        check('reference.fatal', False, exception=type(exc).__name__, message=str(exc))

    passed = sum(row['pass'] for row in checks)
    result = {'schema': 'CR_HE_EVENT_UNION_INDEPENDENT_V1', 'unit': UNIT,
              'status': 'PASS' if checks and passed == len(checks) else 'FAIL',
              'checks': checks, 'comparison_count': len(checks), 'pass_count': passed,
              'fail_count': len(checks) - passed, 'input_identities': identities,
              'production_imports': [], 'reference_method': 'exact binary64 lift; direct He transition incidences; exhaustive six-edge DP',
              'graph_cases': graph_rows, 'graph_case_count': len(graph_rows),
              'graph_domain': 'all 81 n_i in {0,1,2}; capacities 2*n_i; cross-event mass in units 1/2; unused legs are singles',
              'graph_general_theorem': 'finite falsification/reference test; general sharpness uses the separately reviewed R6 construction',
              'dp_cache': cross_multigraph.cache_info()._asdict(), 'report_comparison_rule': 'EXACT_RATIONAL_EQUALITY',
              'old_source_fit_or_projection_calls': 0, 'old_RR_calls': 0,
              'actual_exclusive_measure': None, 'actual_full_native25': None, 'physical_activation': False,
              'budget': 'execution receipt owned by bounded parent runner'}
    with (outdir / 'RESULT.json').open('x') as stream:
        json.dump(plain(result), stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps({k: result[k] for k in ('status', 'comparison_count', 'pass_count', 'fail_count', 'graph_case_count')}))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('outdir')
    parser.add_argument('--npz')
    parser.add_argument('--primary')
    parser.add_argument('--witness')
    args = parser.parse_args()
    outcome = main(args.outdir, args.npz, args.primary, args.witness)
    sys.exit(0 if outcome['status'] == 'PASS' else 1)
