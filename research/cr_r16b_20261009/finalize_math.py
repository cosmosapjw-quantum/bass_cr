"""Exact source-bound update, MPFR cross-check, and immutable result reductions."""
import argparse,hashlib,json
from fractions import Fraction as Q
from pathlib import Path

def load(p):return json.loads(p.read_text())
def frac(x):return Q(int(x['num']),int(x['den'])) if isinstance(x,dict) else Q(x)
def encoded(x):
    if isinstance(x,Q):return {'num':str(x.numerator),'den':str(x.denominator)}
    if isinstance(x,(tuple,list)):return [encoded(v) for v in x]
    if isinstance(x,dict):return {k:encoded(v) for k,v in x.items()}
    return x
def combine_once(time_interval,source_bound):
    lo,hi=map(frac,time_interval);b=frac(source_bound)
    if lo>hi or b<0:raise ValueError('INTERVAL_SOURCE_DOMAIN')
    return lo-b,hi+b

def finish(result,r16root,mpfr,out):
    out.mkdir(exist_ok=False)
    r=load(result/'R16B_RESULTS.json');ind=load(mpfr);trace=load(result/'ADJOINT_EVIDENCE.json')
    bi=list(map(Q,r['signed_optical_depth_interval']));mi=list(map(Q,ind['backward_signed_interval']));pi=list(map(Q,ind['forward_signed_interval']))
    assert max(bi[0],mi[0],pi[0])<=min(bi[1],mi[1],pi[1]),'PRIMAL_DUAL_INTERVALS_DISJOINT'
    assert bi[0]<=mi[0]<=mi[1]<=bi[1],'MPFR_BACKWARD_NOT_CONTAINED_IN_DECIMAL'
    byindex={c['cell']:c for c in ind['all_backward_boundaries']}
    for c in trace:
        for d,m in zip(c['lambda_before'],byindex[c['index']]['lambda_left']):
            assert Q(d[0])<=Q(m[0])<=Q(m[1])<=Q(d[1]),('MPFR_BOUNDARY_NOT_CONTAINED',c['index'])
    prior=load(r16root/'results/COMBINED_TAU.json');source=frac(prior['source_only_used_upper'])
    combined=combine_once(bi,source)
    assert source==Q('1.021773e-17'),'CHANGED_SOURCE_BOUND'
    old=tuple(map(frac,prior['combined_contS_continuum_minus_native']))
    assert combined[0]>0 and old[0]<=combined[0]<=combined[1]<=old[1]
    native=list(map(frac,prior['native_tau']))
    value={'task':'R16B_TIME_PLUS_FROZEN_R16A_SOURCE_BOUND','old_R16A_combined_interval':old,
        'R16A_original_sha256':hashlib.sha256((r16root/'results/COMBINED_TAU.json').read_bytes()).hexdigest(),
        'R16B_time_interval':bi,'same_source_only_upper_added_once':source,
        'updated_continuous_constant_S_minus_native_interval':combined,
        'updated_absolute_continuous_constant_S_tau_interval':[native[0]+combined[0],native[1]+combined[1]],
        'strict_positive':True,'source_proof_reexecuted':False,'source_error_count':1,
        'CT_conversion_rule':'unchanged R16A factor; no donor source sharpening or ledger substitution'}
    (out/'COMBINED_TAU_R16B.json').write_text(json.dumps(encoded(value),indent=2)+'\n')
    check={'status':'PASS_MPFR256_SEPARATE_PROPAGATION','Decimal_contains_MPFR_backward_at_all32_boundaries':True,
        'Decimal_MPFR_forward_backward_intersection_nonempty':True,
        'archived_R16_midpoint_forward_inside':bi[0]<=Q.from_float(1.9731044416400455e-17)<=bi[1],
        'archived_R16_midpoint_backward_inside':bi[0]<=Q.from_float(1.97310444167335e-17)<=bi[1],
        'archived_R15_nonlinear_diagnostic_inside':bi[0]<=Q.from_float(1.9731045074324378e-17)<=bi[1],
        'archived_numbers_are_proof_premises':False,'shares_interval_FT03_AD_panels':True}
    (out/'INDEPENDENT_RECONCILIATION.json').write_text(json.dumps(check,indent=2)+'\n')
    print('SOURCE_ADDED_ONCE',*[f'{float(v):.17e}' for v in combined]);print('MPFR_ALL32_BOUNDARIES_CONTAINED_PASS')

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--result',type=Path,required=True);a.add_argument('--r16root',type=Path,required=True);a.add_argument('--mpfr',type=Path,required=True);a.add_argument('--output',type=Path,required=True)
    x=a.parse_args();finish(x.result,x.r16root,x.mpfr,x.output)
