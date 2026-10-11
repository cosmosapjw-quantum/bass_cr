"""Independent read-only rational comparison of stored G scalar envelopes.

No producer imports, model construction, scientific solver, pulse, or analysis rerun.
The independent reference uses exact fractions of source JSON decimal tokens.
"""
from pathlib import Path
from fractions import Fraction as F
import hashlib
import json
import math

U = Path(__file__).resolve().parents[1]
PACKET_SHA = '2a2389c7abc776f7169ac7d124dd5d7910f8d5a66b7b97fe22f64101fd035916'

def ident(p):
    b = p.read_bytes()
    return {'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}

def qjson(p):
    return json.loads(p.read_text(), parse_float=F, parse_int=F)

def generic(a, b, x):
    v = b-a*a
    assert a >= 0 and x >= 0 and v >= 0 and (a > 0 or b == 0)
    if not v:
        return (F(int(x < a)),)*2
    lo = 1-v/(v+(a-x)**2) if x < a else F(0)
    # Independent minimum of three proven majorants, rather than b/a branches.
    up = min(F(1), a/x if x else F(1), v/(v+(x-a)**2) if x > a else F(1))
    return lo, up

def record(row, T):
    q = 1-row['p']
    if q:
        a = (row['mu_s']-T+T*row['R'])/q
        b = (row['m2_s2']-2*T*row['mu_s']+T*T-T*T*row['S'])/q
        assert a > 0 and b >= a*a
    else:
        a = b = F(0)
    return {'source': row, 'q': q, 'a': a, 'b': b}

def environment(raw, T, t):
    s = record(raw['selected'], T)
    birth = [record(row, T) for row in raw['birth_columns']]
    H = sum(row['source']['H0'] for row in birth)
    weights = [row['source']['H0']/H for row in birth]
    def residual(r):
        if t == T:
            return (r['q'],)*2
        return tuple(r['q']*z for z in generic(r['a'], r['b'], t-T)) if r['q'] else (F(0), F(0))
    total = generic(s['source']['mu_s'], s['source']['m2_s2'], t)
    pooled = residual(s)
    components = [residual(row) for row in birth]
    mixed = tuple(sum(w*r[k] for w, r in zip(weights, components)) for k in (0, 1))
    intersection = (s['q'],)*2 if t == T else (max(total[0], pooled[0], mixed[0]), min(total[1], pooled[1], mixed[1]))
    return {'unconditional': total, 'pooled_residual': pooled, 'birth_residual': mixed, 'intersection': intersection}

def main():
    packet = json.loads((U/'review/REVIEW_PACKET.json').read_text())
    assert ident(U/'review/REVIEW_PACKET.json')['sha256'] == PACKET_SHA
    bindings = []
    for name, expected in packet['files'].items():
        actual = ident(U/name)
        assert actual == expected, name
        bindings.append({'path': name, **actual})
    pins = json.loads((U/'inputs/INPUT_IDENTITIES.json').read_text())
    input_bindings = []
    for name, item in pins['files'].items():
        actual = ident(U.parents[1]/item['repository_path'])
        assert actual == {k:item[k] for k in ('bytes', 'sha256')}, name
        input_bindings.append({'key': name, **actual})
    raw = qjson(U/'inputs/F_CACHED_NUMERICAL_ARTIFACT.json')
    saved = json.loads((U/'evidence/analysis/NUMERICAL_ARTIFACT.json').read_text())
    plot = json.loads((U/'evidence/figures/PLOT_DATA.json').read_text())
    summary = json.loads((U/'evidence/analysis/RESULTS_SUMMARY.json').read_text())
    comparisons = []
    endpoints = []
    for model in ('fullBED', 'legacy'):
        rows = saved['models'][model]
        assert plot['models'][model]['curve'] == rows['curve']
        assert plot['models'][model]['brackets'] == rows['brackets']
        for i, row in enumerate(rows['curve']):
            ref = environment(raw['models'][model], raw['T_s'], F(str(row['t_s'])))
            for component, pair in ref.items():
                for k, key in enumerate(('lower', 'upper')):
                    actual = row[component][key]
                    difference = F.from_float(actual)-pair[k]
                    limit = F('2e-14')+F('2e-12')*abs(pair[k])
                    passed = abs(difference) <= limit
                    comparisons.append({'model':model,'curve_index':i,'component':component,'bound':key,
                                        'signed_difference':float(difference),'tolerance_fraction':float(abs(difference)/limit),'pass':passed})
                    assert passed, (model, i, component, key)
        for bracket, presented in zip(rows['brackets'], summary['models'][model]['quantile_brackets_years']):
            assert bracket['lower_value'] > bracket['threshold']
            assert bracket['upper_value'] <= bracket['threshold']
            assert bracket['lower_s'] <= bracket['upper_s']
            assert all(bracket[k]['iterations'] <= 80 for k in ('lower_bisection','upper_bisection'))
            assert presented['lower'] == bracket['lower_s']/31557600
            assert presented['upper'] == bracket['upper_s']/31557600
            c = 1-F(str(bracket['fraction']))
            low = environment(raw['models'][model],raw['T_s'],F(str(bracket['lower_s'])))['intersection'][0]
            high = environment(raw['models'][model],raw['T_s'],F(str(bracket['upper_s'])))['intersection'][1]
            endpoints.append({'model':model,'fraction':bracket['fraction'],'working_FP64_endpoint_conditions':True,
                              'decimal_token_exact_lower_margin':float(low-c),'decimal_token_exact_upper_margin':float(c-high),
                              'decimal_token_exact_conditions':bool(low>c and high<=c),
                              'scope':'Sign differences near a root are recorded without clipping; no directed rounding or certified enclosing numerical interval is claimed by the producer report.'})
    result={'schema':'cr-phys02g-independent-saved-arithmetic.v1','status':'PASS_WITH_RECORDED_FLOAT_ENDPOINT_LIMITATION',
            'packet_sha256':PACKET_SHA,'candidate_files_verified':len(bindings),'direct_F_inputs_verified':len(input_bindings),
            'candidate_file_bindings':bindings,'direct_input_bindings':input_bindings,
            'comparisons':comparisons,'comparison_count':len(comparisons),
            'max_tolerance_fraction':max(r['tolerance_fraction'] for r in comparisons),
            'endpoints':endpoints,'endpoint_decimal_condition_mismatches':sum(not r['decimal_token_exact_conditions'] for r in endpoints),
            'plots_and_summary_equal_saved_data':True,'producer_modules_imported':False,
            'actual_cached_analysis_reruns':0,'physical_G':0,'linear_solves':0,'pulse':0,'expm':0,
            'reference_scope':'Exact Fraction arithmetic on recorded decimal tokens; not a bound on the physical or floating-point source moment error.'}
    target=U/'review/REVIEW_SAVED_ARITHMETIC_RESULT.json'
    with target.open('x') as h:
        json.dump(result,h,indent=2,allow_nan=False);h.write('\n')
    print(json.dumps({k:result[k] for k in ('status','candidate_files_verified','direct_F_inputs_verified','comparison_count','max_tolerance_fraction','endpoint_decimal_condition_mismatches','endpoints')},indent=2))

if __name__ == '__main__':
    main()
