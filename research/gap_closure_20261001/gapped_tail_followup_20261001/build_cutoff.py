"""Bind exact bound arithmetic to the sibling static reference certificate."""
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path
from gapped_tail import first_integer_cutoff, tail_bound


def encode(value):
    if isinstance(value,F):
        return dict(rational=str(value),display_float=float(value))
    if isinstance(value,dict):
        return {k:encode(v) for k,v in value.items()}
    if isinstance(value,list):
        return [encode(v) for v in value]
    return value


def build():
    here=Path(__file__).resolve().parent
    reference=here.parent/'reference_certificate_followup_20261001/actual_certificate/REFERENCE_CERTIFICATE.json'
    raw=reference.read_bytes()
    cert=json.loads(raw)
    block=cert['reference_block_certificate']
    gap=F(block['a_lower']['rational'])+F(block['d_lower']['rational'])
    mapping=F(cert['original_to_negative_reference_projector_upper']['rational'])
    a=F(cert['support_radius_a0']['rational'])
    if (cert['selector_definition']['negative_rank']!=5
        or cert['selector_definition']['positive_rank']!=4
        or not cert['selector_definition']['full_angular_multiplets']
        or cert['status']!='STATIC_REFERENCE_AND_SELECTOR_MAPPING_VALIDATED'):
        raise ValueError('unexpected reference certificate scope')
    target=F(1,200000)
    args=dict(b=2,radius=a,charge=1,gap=gap,norm2=1)
    cutoff=first_integer_cutoff(target=target,**args)
    mapped_cutoff=first_integer_cutoff(target=target-mapping,**args)
    example_cutoff=first_integer_cutoff(target=target,**dict(args,gap=F(1,10)))
    # This comparison is explicitly ordinary floating arithmetic; the actual
    # new bound above is exact rational arithmetic with imported inputs.
    speed=2.00798
    k=math.sqrt(float(a*a-4))
    old_at_cutoff=float(a)*math.atanh(k/cutoff)/(speed*k)
    result=dict(
        schema='BASS_R4R_GAPPED_TAIL_BOUND_V1',
        status='EXACT_REFERENCE_CONDITIONAL_FAR_TAIL_BOUND_ONLY',
        reference_certificate_path=str(reference.relative_to(here.parent)),
        reference_certificate_sha256=hashlib.sha256(raw).hexdigest(),
        reference_certificate_status=cert['status'],
        reference_coefficients_sha256=cert['reference_coefficients_sha256'],
        reference_selector_identity_sha256=cert['selector_identity_sha256'],
        proof='GAPPED_TAIL_THEOREM.md equations (1)-(6)',
        parameters=args,
        certified_reference_gap_lower=gap,
        original_to_reference_same_state_projector_bound=mapping,
        research_target_per_side=target,
        minimum_integer_cutoff_a0=cutoff,
        bound_at_cutoff=tail_bound(Z=cutoff,**args),
        bound_at_previous_integer=tail_bound(Z=cutoff-1,**args),
        minimum_integer_cutoff_including_same_state_mapping_a0=mapped_cutoff,
        total_bound_including_mapping=tail_bound(Z=mapped_cutoff,**args)['probability_bound']+mapping,
        illustrative_gap_one_tenth=dict(gap=F(1,10),cutoff_a0=example_cutoff),
        old_rate_integral_comparison=dict(
            status='ORDINARY_FLOAT_COMPARISON_ONLY',speed_atomic= speed,
            old_bound_at_new_cutoff=old_at_cutoff,
            old_asymptotic_cutoff_for_same_target=float(a)/(speed*float(target)),
            ratio_old_to_new_at_new_cutoff=old_at_cutoff/float(tail_bound(Z=cutoff,**args)['probability_bound'])),
        budget_scope='Far-tail benchmark spends the full one-side research target; a nonzero finite bridge must also fit that target or use a farther cutoff. This is not a complete one-side certificate.',
        bridge_bound=None,dynamical_state_transfer_bound=None,
        original_B0_asymptotic_limit_proved=False,
        new_reference_adopted=False,
        native_calls=0,new_two_center_operator_queries=0,
        synthetic_two_level_ODE_checks=1,
        claim_ceilings=dict(capture=False,production='HOLD',all_bound='OPEN',b_grid='NO_GO',
                           original_capture_gap_resolved=False,continuous_global_supremum_bound=False,
                           continuous_trajectory_error_bound=False))
    output=here/'CONDITIONAL_CUTOFF.json'
    output.write_text(json.dumps(encode(result),indent=2)+'\n')
    print(json.dumps({'cutoff':cutoff,'cutoff_with_mapping':mapped_cutoff,'bound':float(result['bound_at_cutoff']['probability_bound']),
                      'gap':float(gap),'comparison':result['old_rate_integral_comparison']}))


if __name__=='__main__':
    build()
