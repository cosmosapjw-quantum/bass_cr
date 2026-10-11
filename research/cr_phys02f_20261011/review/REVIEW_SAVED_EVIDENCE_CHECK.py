#!/usr/bin/env python3
"""Independent read-only PHYS02F review arithmetic; no candidate imports/solves."""
import argparse
from datetime import datetime, timezone
from decimal import Decimal as D, localcontext
import hashlib
import json
from pathlib import Path
import time

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load_decimal(path):
    return json.loads(path.read_text(), parse_float=D, parse_int=D)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    started = datetime.now(timezone.utc).isoformat()
    clock = time.monotonic()
    repo = args.repo.resolve()
    unit = repo/'research/cr_phys02f_20261011'
    packet_path = unit/'state/REVIEW_PACKET.json'
    packet = json.loads(packet_path.read_text())
    actual_read = {}
    for rel, identity in packet['reviewed_files'].items():
        path = unit/rel
        raw = path.read_bytes()
        measured = {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
        assert measured == identity, ('CANDIDATE_BINDING_MISMATCH', rel)
        actual_read[rel] = measured
    dep_path = unit/'inputs/DEPENDENCY_PAYLOAD_MANIFEST.json'
    deps = json.loads(dep_path.read_text())['files']
    ids = json.loads((unit/'inputs/INPUT_IDENTITIES.json').read_text())['files']
    for rel, entry in list(deps.items()) + [(x['path'], x) for x in ids.values()]:
        path = repo/rel
        assert path.is_file() and not path.is_symlink()
        assert path.resolve().is_relative_to(repo)
        assert path.stat().st_size == entry['bytes'] and digest(path) == entry['sha256'], ('INPUT_BINDING_MISMATCH', rel)
    checks = []
    def equal(name, actual, expected, scale=D(1)):
        actual, expected = D(actual), D(expected)
        difference = actual-expected
        allowed = D('2e-14')*scale+D('2e-12')*max(abs(actual),abs(expected))
        assert abs(difference) <= allowed, (name, str(difference), str(allowed))
        checks.append({'name':name, 'normalized_absolute_difference':str(abs(difference)/scale),
                       'fraction_of_frozen_tolerance':str(abs(difference)/allowed) if allowed else '0'})
    T, yr = D('1e10'), D(31557600)
    output = load_decimal(unit/'evidence/analysis/NUMERICAL_ARTIFACT.json')
    oracle = load_decimal(unit/'evidence/analysis/DECIMAL80_ORACLE.json')
    plot = load_decimal(unit/'evidence/analysis/PLOTTING_DATA.json')
    model_rows = {}
    with localcontext() as context:
        context.prec = 80
        for model in ('fullBED', 'legacy'):
            source = load_decimal(repo/ids['actual_'+model+'_result']['path'])
            rows = source['birth_columns'] + [source['selected']]
            target_rows = output['models'][model]['birth_columns'] + [output['models'][model]['selected']]
            derived_rows = []
            for index, (row, target) in enumerate(zip(rows,target_rows)):
                H,p,R,S,mu,m2 = (row['H0'],row['cdf'][-1],row['R'],row['S'],row['mean_lag_s'],row['second_moment_s2'])
                assert H > 0 and 0 < p < 1
                e1 = T*(p-R)
                e2 = T*T*(p-2*R+S)
                l1,l2 = mu-e1,m2-e2
                # Independent tail shift from the partition's raw moments.
                r1,r2 = l1-T*(1-p),l2-2*T*l1+T*T*(1-p)
                derived = {}
                for section,q,first,second in [('early',p,e1,e2),('tail',1-p,l1,l2),('tail_residual',1-p,r1,r2),('total',D(1),mu,m2)]:
                    mean = first/q
                    variance = second/q-mean*mean
                    if section == 'early':
                        variance = T*T*(p*S-R*R)/(p*p)
                    assert first >= 0 and second >= 0 and variance >= 0
                    values = {'probability':q,'raw_m1_s':first,'raw_m2_s2':second,'mean_s':mean,'second_s2':second/q,'variance_s2':variance}
                    derived[section] = values
                    for key,expected in values.items():
                        scale = T*T if key.endswith('s2') else T if key.endswith('_s') else D(1)
                        equal(f'{model}.{index}.{section}.{key}',target[section][key],expected,scale)
                        equal(f'{model}.{index}.stored_decimal.{section}.{key}',oracle[model]['columns'][index][section][key],expected,scale)
                total_var = p*(derived['early']['variance_s2']+(derived['early']['mean_s']-mu)**2)+(1-p)*(derived['tail']['variance_s2']+(derived['tail']['mean_s']-mu)**2)
                equal(f'{model}.{index}.partition_variance',total_var,m2-mu*mu,T*T)
                for slot, (cdf,k) in enumerate(zip(row['cdf'],row['kernel_per_s'])):
                    equal(f'{model}.{index}.plotCDF.{slot}',plot[model]['cdf'][index][slot],cdf)
                    equal(f'{model}.{index}.plotDensity.{slot}',plot[model]['density_per_s'][index][slot],k/H,D(1)/T)
                derived_rows.append({'H':H,'p':p,'mu':mu,'m2':m2,'derived':derived})
            totalH = sum(row['H'] for row in derived_rows[:2])
            weights = []
            for index,row in enumerate(derived_rows[:2]):
                numerators = {'eventual':row['H'],'early':row['H']*row['p'],'tail':row['H']*(1-row['p']),'mean_share':row['H']*row['mu']}
                denominators = {'eventual':totalH,'early':sum(x['H']*x['p'] for x in derived_rows[:2]),'tail':sum(x['H']*(1-x['p']) for x in derived_rows[:2]),'mean_share':sum(x['H']*x['mu'] for x in derived_rows[:2])}
                weights.append({name:value/denominators[name] for name,value in numerators.items()})
                for name,value in weights[-1].items():
                    equal(f'{model}.birth{index}.{name}',output['models'][model]['birth_mixture']['weights'][index][name]['value'],value)
            selected = derived_rows[-1]
            mix_variance = sum(row['H']/totalH*(row['derived']['total']['variance_s2']+(row['mu']-selected['mu'])**2) for row in derived_rows[:2])
            equal(f'{model}.birth_total_variance',output['models'][model]['selected']['total']['variance_s2'],mix_variance,T*T)
            model_rows[model] = {'p':str(selected['p']),'early_mean_years':str(selected['derived']['early']['mean_s']/yr),'uncapped_mean_years':str(selected['mu']/yr),'tail_remaining_mean_years':str(selected['derived']['tail_residual']['mean_s']/yr),'low_birth_weights':{k:str(v) for k,v in weights[0].items()}}
    # Only read stored arrays. No physical module, preflight, G or solver imports.
    import numpy as np
    npz_read = {}
    for model in ('fullBED','legacy'):
        source = json.loads((repo/ids['actual_'+model+'_result']['path']).read_text())
        with np.load(repo/ids['actual_'+model+'_pulse']['path'],allow_pickle=False) as z:
            arrays = {k:z[k] for k in z.files}
        with np.load(repo/ids[model+'_9600_npz']['path'],allow_pickle=False) as z:
            reference_E,reference_source = z['energy_eV'],z['source_vectors']
        assert all(np.isfinite(a).all() for a in arrays.values())
        assert arrays['pulse_states'].shape == (17,9611,2)
        assert np.array_equal(arrays['energy_eV'],reference_E)
        assert np.array_equal(arrays['source_vectors'],reference_source)
        assert np.array_equal(arrays['pulse_states'][0],reference_source)
        assert np.array_equal(arrays['sample_u'],np.arange(17)/16)
        heat = arrays['pulse_states'][:,9600,:]
        max_cdf_error = 0.0
        for index,row in enumerate(source['birth_columns']+[source['selected']]):
            observed = heat[:,index] if index < 2 else heat.sum(axis=1)
            error = float(np.max(np.abs(observed/row['H0']-np.array(row['cdf']))))
            assert error <= 2e-14
            max_cdf_error = max(max_cdf_error,error)
        npz_read[model] = {'pulse_shape':list(arrays['pulse_states'].shape),'all_finite':True,'saved_E_exact':True,'source_and_initial_state_exact':True,'sample_u_exact':True,'max_cdf_absolute_difference':max_cdf_error,'minimum_pulse_value':float(arrays['pulse_states'].min())}
    result = {'schema':'cr-phys02f-independent-saved-evidence-review.v1',
              'reviewer':'/root/phys02f_remote_intake','scope':'read-only identity and independent Decimal80 saved-arithmetic/NPZ checks; no candidate module execution',
              'started_utc':started,'ended_utc':datetime.now(timezone.utc).isoformat(),'wall_s':time.monotonic()-clock,
              'review_packet_sha256':digest(packet_path),'candidate_bound_files':actual_read,
              'dependency_files_verified':len(deps),'direct_inputs_verified':len(ids),'all_candidate_hashes_match':True,
              'scalar_comparisons':len(checks),'maximum_fraction_of_frozen_scalar_tolerance':max(float(x['fraction_of_frozen_tolerance']) for x in checks),
              'scalar_results':model_rows,'stored_npz_read':npz_read,
              'physical_G_builds':0,'expm_calls':0,'pulse_calls':0,'triangular_solve_calls':0,
              'candidate_test_runs':0,'candidate_analysis_reruns':0,'actual_NCP_execution':False,
              'comparison_records':checks}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({key:result[key] for key in ('dependency_files_verified','direct_inputs_verified','all_candidate_hashes_match','scalar_comparisons','maximum_fraction_of_frozen_scalar_tolerance','stored_npz_read','physical_G_builds','triangular_solve_calls','candidate_test_runs')}))

if __name__ == '__main__':
    main()
