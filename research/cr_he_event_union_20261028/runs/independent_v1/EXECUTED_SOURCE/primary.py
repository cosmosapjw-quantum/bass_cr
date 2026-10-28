"""Bounded primary pass on already saved PHYS02 He attribution atoms."""
from pathlib import Path
from fractions import Fraction as F
import argparse
import hashlib
import json
import sys
import event_union as eu

def main(outdir, npz_path=None):
    outdir = Path(outdir)
    eu.require(outdir.is_dir(), 'RUNNER_CREATED_OUTPUT_DIRECTORY_REQUIRED')
    if npz_path is None:
        unit = Path(__file__).resolve().parents[1]
        npz_path = unit.parents[1] / 'research/cr_parent_event_native25_20261028/runs/prepare_v1/ATTRIBUTION_ARRAYS.npz'
    source = eu.load_pinned_source(npz_path)
    atoms = source.atoms
    counts = eu.partition_masses(atoms)
    energies = tuple(sum((a.energy_eV * a.coefficient for a in atoms if a.partition == k), F(0)) for k in range(4))
    total = sum(counts, F(0))
    energy = sum(energies, F(0))
    bound = eu.sharp_cross_bound(counts)
    factor = eu.known_window_factor((0, eu.T))
    checks = []
    def check(name, condition, **details):
        checks.append({'id': name, 'pass': bool(condition), **eu.serial(details)})
    check('input.3201_atoms', len(atoms) == 3201)
    check('input.active3200_and_ghost1', sum(a.partition == 0 for a in atoms) == 1 and len(atoms) - 1 == 3200)
    check('input.all_positive_coefficients', all(a.coefficient > 0 for a in atoms))
    check('partition.count_complete', total == sum((a.coefficient for a in atoms), F(0)))
    check('partition.energy_complete', energy == sum((a.energy_eV * a.coefficient for a in atoms), F(0)))
    check('bound.nonnegative_and_two_legs', 0 <= bound <= total / 2)
    check('bound.minority_leg_limit', bound <= total - max(counts))
    records = {}
    atom_comparisons = []
    witness_meta = None
    for name, make in (('single', eu.single_lift), ('diagonal', eu.diagonal_double_lift), ('halfshift', eu.half_shift_lift)):
        events = make(atoms)
        reconstructed = eu.marginal(events, atoms)
        failures = [a.key for a in atoms if reconstructed[a.key] != a.coefficient]
        atom_comparisons.append({'id_prefix': name + '.atom.', 'count': len(atoms),
                                 'pass_count': len(atoms) - len(failures), 'failed_atom_ids': failures,
                                 'maximum_exact_absolute_residual': max(abs(reconstructed[a.key] - a.coefficient) for a in atoms)})
        check(name + '.exact_atomwise_marginal', not failures)
        claims = eu.claims_by_partition(events, source, eu.binding((0, eu.T), source))
        result = eu.consume_event_union(claims, source, nb_m3=eu.NB)
        expected_cross = bound * factor if name == 'halfshift' else F(0)
        check(name + '.sharp_cross_endpoint', result['cross_duplicate_parent_density'] == expected_cross)
        check(name + '.selected_count', result['union']['selected_electrons'] == total * factor)
        check(name + '.selected_kinetic_energy', result['union']['selected_energy_eV_m3'] == energy * factor)
        expected_d = F(0) if name == 'single' else total * factor / 2
        check(name + '.total_double_count_separate', result['union']['d'] == expected_d)
        check(name + '.same_state_nb_once', result['native_species_correction21'][10] == expected_cross / eu.NB)
        check(name + '.chemical_correction', result['chemical_correction_eV_m3'] == -(eu.I1 + eu.I2) * expected_cross)
        check(name + '.fixed_unresolved_fields', result['actual_full_native25'] is None
              and result['actual_donor_work'] is None and result['outside_partner_response'] is None
              and result['actual_exclusive_event_measure'] is None and not result['full_physical_consumer_activation'])
        check(name + '.RR_photon_unchanged', result['RR_correction'] == 0 and result['retained_photon_correction'] == 0)
        records[name] = {'event_atoms': len(events), 'input_provenance': source.provenance_kind,
                         'consumer': result, 'kernel_content_sha256': eu.content_id([(e.key, e.electrons, e.coefficient) for e in events])}
        if name == 'halfshift':
            witness_meta = eu.write_new(outdir / 'HALFSHIFT_EVENT_WITNESS.json',
                {'schema': 'CR_HE_EVENT_UNION_CONDITIONAL_WITNESS_V1', 'unit': eu.UNIT_ID,
                 'kind': 'CONDITIONAL_MARGINAL_LIFT', 'actual_exclusive_measure': None,
                 'atom_content_sha256': source.atom_content_sha256, 'attribution_npz_sha256': eu.NPZ_SHA,
                 'weight_units': 'proper m^-3 s^-2; event source coefficient, not event rate at unspecified time',
                 'q_event': 't * coefficient on proper [0,1e10] s',
                 'events': [{'event_id': e.key, 'electron_atom_ids': e.electrons,
                             'event_coefficient': e.coefficient, 'provenance': e.provenance} for e in events]})
    times = (F(0), eu.T / 4, eu.T / 2, 3 * eu.T / 4, eu.T)
    prefixes = []
    bins = []
    for end in times[1:]:
        f = eu.known_window_factor((0, end))
        prefixes.append({'role': 'nonadditive_birth_prefix', 'window_s': [F(0), end], 'factor_s2': f,
                         'N_He_m3': total * f, 'U_He_eV_m3': energy * f,
                         'cross_bound_m3': [F(0), bound * f], 'partition_count_m3': [x * f for x in counts]})
    for start, end in zip(times, times[1:]):
        f = eu.known_window_factor((start, end))
        bins.append({'role': 'additive_disjoint_birth_time_bin_not_saved_observation_response',
                     'window_s': [start, end], 'factor_s2': f, 'N_He_m3': total * f,
                     'U_He_eV_m3': energy * f, 'cross_bound_m3': [F(0), bound * f]})
    check('time.factor_additivity', sum((x['factor_s2'] for x in bins), F(0)) == factor)
    check('time.number_additivity', sum((x['N_He_m3'] for x in bins), F(0)) == prefixes[-1]['N_He_m3'])
    check('time.energy_additivity', sum((x['U_He_eV_m3'] for x in bins), F(0)) == prefixes[-1]['U_He_eV_m3'])
    check('time.bound_same_witness_additivity', sum((x['cross_bound_m3'][1] for x in bins), F(0)) == bound * factor)
    check('time.prefixes_not_additive', sum((x['N_He_m3'] for x in prefixes), F(0)) != prefixes[-1]['N_He_m3'])
    all_pass = all(c['pass'] for c in checks)
    result = {'schema': 'CR_HE_EVENT_UNION_PRIMARY_V1', 'unit': eu.UNIT_ID,
              'status': 'PASS_SCOPED' if all_pass else 'FAIL',
              'input': {'path': str(npz_path), 'sha256': eu.NPZ_SHA, 'atom_content_sha256': source.atom_content_sha256,
                        'canonical_source_sha256': eu.SOURCE_SHA, 'attribution_provenance': source.provenance_kind,
                        'attribution_is_not_canonical_source_replacement': True},
              'checks': checks, 'logical_check_count': len(checks),
              'logical_pass_count': sum(c['pass'] for c in checks),
              'atomwise_exact_comparisons': atom_comparisons,
              'atomwise_comparison_count': sum(x['count'] for x in atom_comparisons),
              'atomwise_pass_count': sum(x['pass_count'] for x in atom_comparisons),
              'full_saved_source_consumer_calls': 3, 'old_source_fit_or_projection_calls': 0, 'old_RR_calls': 0,
              'partition_labels': ['cutoff ghost only', 'active (.1,1]', 'active (1,3]', 'active (3,10]'],
              'partition_atom_counts': [sum(a.partition == k for a in atoms) for k in range(4)],
              'coefficient_count_m3_s2': counts, 'coefficient_energy_eV_m3_s2': energies,
              'coefficient_cross_bound_m3_s2': bound,
              'final_prefix': {'N_He_m3': total * factor, 'U_He_eV_m3': energy * factor,
                               'Cmax_m3': bound * factor, 'Cmax_over_N': bound / total,
                               'chemical_correction_interval_eV_m3': [-(eu.I1 + eu.I2) * bound * factor, F(0)],
                               'native_HeI_correction_interval': [F(0), bound * factor / eu.NB]},
              'prefixes': prefixes, 'disjoint_birth_time_bins': bins, 'witnesses': records,
              'witness_file': witness_meta, 'actual_Ccross': None, 'actual_exclusive_measure': None,
              'actual_full_native25': None, 'physical_activation': False,
              'source_model_error': 'inherited accepted attribution tolerance; no new certified source uncertainty interval',
              'budget': 'execution receipt owned by bounded parent runner'}
    eu.write_new(outdir / 'RESULT.json', result)
    print(json.dumps({'status': result['status'], 'logical_checks': len(checks),
                      'logical_pass': result['logical_pass_count'], 'atom_comparisons': result['atomwise_comparison_count'],
                      'atom_pass': result['atomwise_pass_count'], 'N_He_m3': float(total * factor), 'Cmax_m3': float(bound * factor)}))
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('outdir')
    parser.add_argument('--npz')
    args = parser.parse_args()
    result = main(args.outdir, args.npz)
    sys.exit(0 if result['status'] == 'PASS_SCOPED' else 1)
