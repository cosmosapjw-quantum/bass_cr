"""Small exact controls for scientific identity, overlap, factor two and limits."""
from pathlib import Path
from fractions import Fraction as F
from dataclasses import replace
import argparse
import copy
import json
import sys
import event_union as eu

def make_source(weights=(4,3,2,1)):
    energy = (eu.CUTOFF, F(1), F(2), F(4))
    return eu.fixture_source(tuple(eu.Atom(f'a{i}', energy[i], F(w), i) for i,w in enumerate(weights)))

def make_claims(source, kind=eu.half_shift_lift, window=(0,1)):
    return eu.claims_by_partition(kind(source.atoms), source, eu.binding(window, source))

def main(outdir):
    outdir = Path(outdir)
    eu.require(outdir.is_dir(), 'RUNNER_CREATED_OUTPUT_DIRECTORY_REQUIRED')
    checks = []
    def positive(name, fn):
        try:
            ok = bool(fn())
            checks.append({'id': name, 'pass': ok, 'expected': 'true', 'observed': ok})
        except Exception as exc:
            checks.append({'id': name, 'pass': False, 'expected': 'true', 'observed': type(exc).__name__ + ':' + str(exc)})
    def refused(name, reason, fn):
        try:
            fn()
            checks.append({'id': name, 'pass': False, 'expected': reason, 'observed': 'ACCEPTED'})
        except ValueError as exc:
            checks.append({'id': name, 'pass': str(exc) == reason, 'expected': reason, 'observed': str(exc)})
        except Exception as exc:
            checks.append({'id': name, 'pass': False, 'expected': reason, 'observed': type(exc).__name__ + ':' + str(exc)})
    source = make_source()
    claims = make_claims(source)
    consume = lambda c=claims,s=source,nb=eu.NB,old=(): eu.consume_event_union(c, s, nb_m3=nb, previous_windows=old)
    def bound_fixture(weights):
        s = make_source(weights)
        result = eu.consume_event_union(make_claims(s), s, nb_m3=eu.NB)
        return (result['cross_duplicate_parent_density'] == eu.sharp_cross_bound(map(F,weights)) / 2
                and all(eu.marginal(eu.half_shift_lift(s.atoms), s.atoms)[a.key] == a.coefficient for a in s.atoms))
    positive('balanced_sharp_endpoint', lambda: bound_fixture((4,3,2,1)))
    positive('dominant_sharp_endpoint', lambda: bound_fixture((7,1,1,1)))
    positive('exact_half_boundary', lambda: bound_fixture((5,3,2,0)))
    positive('zero_measure', lambda: bound_fixture((0,0,0,0)))
    positive('one_positive_bin', lambda: bound_fixture((0,0,6,0)))
    positive('same_atom_pair_has_two_legs', lambda: eu.marginal(eu.diagonal_double_lift(source.atoms),source.atoms)
              == {a.key:a.coefficient for a in source.atoms})
    positive('within_bin_d_not_cross_bound', lambda: eu.evaluate_event_set(eu.diagonal_double_lift(source.atoms),
              source.atoms,[0,1,2,3],(0,1))['d'] > 0 and eu.consume_event_union(make_claims(source,eu.diagonal_double_lift),
              source,nb_m3=eu.NB)['cross_duplicate_parent_density'] == 0)
    positive('missing_nb_native_is_null', lambda: consume(nb=None)['native_source_species21'] is None
              and consume(nb=None)['native_species_correction21'] is None)
    positive('adjacent_time_windows_allowed', lambda: eu.consume_event_union(make_claims(source,window=(1,2)),
              source,nb_m3=eu.NB,previous_windows=((0,1),))['accepted_windows'] == [[0,1],[F(1),F(2)]])
    positive('fixtures_not_canonical_source', lambda: source.canonical_source_sha256 is None
              and consume()['input_kind'] == 'ALGEBRAIC_FIXTURE')
    positive('ionic_and_electron_charge_distinct', lambda: consume()['ionic_charge_correction_m3'] == -5
              and consume()['selected_electron_correction_m3'] == 0)
    positive('RR_and_retained_photon_unchanged', lambda: consume()['RR_correction'] == 0
              and consume()['retained_photon_correction'] == 0 and consume()['actual_full_native25'] is None)
    refused('wrong_same_state_nb', 'EXPLICIT_SAME_STATE_NB_REQUIRED', lambda: consume(nb=F(1)))
    refused('overlapping_time_return', 'OVERLAPPING_TIME_RETURN_OR_REPLAY_REFUSED', lambda: consume(old=((0,1),)))
    refused('unknown_history', 'FINITE_KNOWN_PROPER_HISTORY_REQUIRED', lambda: eu.binding((0,eu.T+1),source))
    refused('zero_window', 'FINITE_KNOWN_PROPER_HISTORY_REQUIRED', lambda: eu.binding((1,1),source))
    refused('nonfinite_scalar', 'EXACT_FINITE_SCALAR_REQUIRED', lambda: eu.exact('NaN'))
    refused('nonfinite_source_float', 'FINITE_BINARY64_REQUIRED', lambda: eu.lift_float(float('inf')))
    refused('negative_atom_weight', 'NEGATIVE_ATOM_WEIGHT', lambda: make_source((1,-1,0,0)))
    refused('source_support_extension', 'NATIVE_SUPPORT_EXTENSION_REFUSED', lambda: eu.fixture_source((eu.Atom('bad',F(11),F(1),3),)))
    refused('cutoff_relabel', 'BIRTH_PARTITION_MISMATCH', lambda: eu.fixture_source((eu.Atom('bad',eu.CUTOFF,F(1),1),)))
    refused('atom_digest_mutation', 'ATOM_PAYLOAD_CONTENT_MISMATCH', lambda: eu.validate_source(replace(source,
              atoms=(replace(source.atoms[0],coefficient=F(5)),)+source.atoms[1:])))
    refused('fixture_canonical_identity_forgery', 'FIXTURE_CANNOT_CLAIM_CANONICAL_SOURCE',
              lambda: eu.validate_source(replace(source,canonical_source_sha256=eu.SOURCE_SHA)))
    refused('unpinned_actual_source_forgery', 'PINNED_LOADER_ATTESTATION_REQUIRED',
              lambda: eu.validate_source(replace(source,provenance_kind='STORED_PHYS02_MODEL_IDENTIFIED_HE_ATOMS',
              attribution_npz_sha256=eu.NPZ_SHA,canonical_source_sha256=eu.SOURCE_SHA)))
    for field,value,reason in (
        ('state_id','foreign','SAME_STATE_REQUIRED'),
        ('isotope','He3','SOURCE_PARENT_ISOTOPE_STATE_MISMATCH'),
        ('parent_state','He4II','SOURCE_PARENT_ISOTOPE_STATE_MISMATCH'),
        ('frame','lab','MIXED_FRAME_REFUSED'),
        ('clock','coordinate_time','PROPER_CLOCK_REQUIRED'),
        ('support_eV',(eu.CUTOFF,F(11)),'NATIVE_SUPPORT_EXTENSION_REFUSED'),
        ('absolute_proper_volume_m3',F(1),'FIXED_DENSITY_SCOPE_REQUIRED'),
        ('atom_content_sha256','forged','SOURCE_BINDING_IDENTITY_MISMATCH'),
        ('actual_exclusive_measure','invented','UNVERIFIED_ACTUAL_MEASURE_CLAIM_REFUSED')):
        bad=copy.deepcopy(claims)
        for c in bad:c['binding'][field]=value
        refused('binding.'+field,reason,lambda bad=bad:consume(c=bad))
    bad=copy.deepcopy(claims)
    for c in bad:c['binding']['retained_photon_to_heating']=True
    refused('photon_port_reassignment','UNEXPECTED_BINDING_FIELDS',lambda:consume(c=bad))
    refused('overlapping_birth_partition','OVERLAPPING_PARTITION_CLAIMS_REFUSED',lambda:consume(c=claims+[claims[0]]))
    bad=copy.deepcopy(claims)
    cross_event=next(e for c in claims for e in c['events'] if len({source.atoms[int(k[1:])].partition for k in e.electrons})==2)
    incident=[c['partition'] for c in claims if cross_event in c['events']]
    bad[incident[0]]['events']=tuple(e for e in bad[incident[0]]['events'] if e.key!=cross_event.key)
    refused('F02_incomplete_cross_claim','INCOMPLETE_PARTITION_EVENT_CLAIM',lambda:consume(c=bad))
    bad=copy.deepcopy(claims)
    i=incident[1]
    bad[i]['events']=tuple(replace(e,coefficient=e.coefficient*2) if e.key==cross_event.key else e for e in bad[i]['events'])
    refused('conflicting_same_event_id','CONFLICTING_SAME_EVENT_ID',lambda:consume(c=bad))
    bad=make_claims(source,eu.single_lift)
    bad[0]['events']=tuple(replace(e,coefficient=e.coefficient*2) for e in bad[0]['events'])
    refused('F01_changed_source_marginal','SELECTED_SOURCE_MARGINAL_MISMATCH',lambda:consume(c=bad))
    bad=copy.deepcopy(claims)
    bad[incident[0]]['events'] += (cross_event,)
    refused('duplicate_event_within_partition','DUPLICATE_EVENT_IN_KERNEL',lambda:consume(c=bad))
    bad=make_claims(source,eu.single_lift)
    bad[0]['events']=tuple(replace(e,coefficient=F(-1)) for e in bad[0]['events'])
    refused('negative_event_weight','POSITIVE_EXACT_EVENT_WEIGHT_REQUIRED',lambda:consume(c=bad))
    # A factor-two mutation is rejected by the marginal, not hidden in a tolerance.
    bad_events=[replace(e,coefficient=e.coefficient*2) for e in eu.diagonal_double_lift(source.atoms)]
    bad=eu.claims_by_partition(bad_events,source,eu.binding((0,1),source))
    refused('double_leg_factor_two_mutation','SELECTED_SOURCE_MARGINAL_MISMATCH',lambda:consume(c=bad))
    large=make_source((100,0,0,0))
    refused('finite_inventory_depletion','CONDITIONAL_NEUTRAL_INVENTORY_EXHAUSTED',
              lambda:eu.consume_event_union(make_claims(large,eu.single_lift),large,nb_m3=eu.NB))
    result={'schema':'CR_HE_EVENT_UNION_CONTROLS_V1','unit':eu.UNIT_ID,
            'status':'PASS' if all(x['pass'] for x in checks) else 'FAIL',
            'checks':checks,'unique_checks':len(checks),'evaluations':len(checks),
            'pass_count':sum(x['pass'] for x in checks),'fail_count':sum(not x['pass'] for x in checks),
            'fixture_provenance':'ALGEBRAIC_FIXTURE; no actual exclusive He measure',
            'old_source_or_RR_replays':0,'budget':'execution receipt owned by bounded parent runner'}
    eu.write_new(outdir/'RESULT.json',result)
    print(json.dumps({k:result[k] for k in ('status','unique_checks','evaluations','pass_count','fail_count')}))
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('outdir');args=parser.parse_args()
    result=main(args.outdir)
    sys.exit(0 if result['status']=='PASS' else 1)
