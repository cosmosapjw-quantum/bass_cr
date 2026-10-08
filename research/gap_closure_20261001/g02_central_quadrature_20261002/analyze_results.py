"""Post-run, read-only raw-array analysis for the bounded R4Y central experiment.

This file is separately identified after the runtime source freeze. It cannot
launch an operator, alter a cache, loosen a threshold, or promote production.
The final result is created only after every declared task is complete and the
explicit legacy/phase selections pass. Failed observations remain in the result.
"""
from pathlib import Path
import argparse
import itertools
import json
import numpy as np
import central_bootstrap
import runner as r


def label(task):
    beta=task['inner_phase_budget']
    rule=f"q{task['order']}_h{task['subdivisions']}" if beta is None else f"q{task['order']}_beta{beta:g}"
    return rule+'_'+task['moment_backend']+'_'+task['radial_backend']


def compare(a,b):
    maximum,detail=r._raw_difference(a['raw'],b['raw'])
    full_screens=all(x['screens']['hermiticity_pass'] and x['screens']['metric_pass'] for x in (a,b))
    exact_zero=all(x['central_control']['pass'] for x in (a,b))
    raw_pass=maximum<=r.SCREENS['raw_cross_relative_max']
    return {'a':a['label'],'b':b['label'],'max_six_raw_relative_difference':maximum,
            'six_raw_relative_differences':detail,'raw_difference_pass':raw_pass,
            'both_full_screens_pass':full_screens,'both_central_controls_pass':exact_zero,
            'central_absolute_maxima':[a['central_control']['maximum_absolute'],b['central_control']['maximum_absolute']],
            'conjunction_pass':raw_pass and full_screens and exact_zero,
            'six_raw_bitwise_equal':all(np.array_equal(a['raw'][k],b['raw'][k]) for k in r.RAW_KEYS),
            'full_bitwise_equal':all(np.array_equal(a['full'][k],b['full'][k]) for k in ('S','H','D')),
            'full_relative_differences':{k:float(np.linalg.norm(a['full'][k]-b['full'][k])/
                max(np.linalg.norm(a['full'][k]),np.linalg.norm(b['full'][k]),1e-300)) for k in ('S','H','D')},
            'evidence_relation':'OBSERVED_NUMERICAL_DIFFERENCE_NOT_CERTIFIED_ERROR'}


def analyze(root,context_sha):
    root,c=r.load_context(root,context_sha)
    ledger=r.reservations(root,c)
    observations={};batch_records=[];bindings=[]
    for dest in sorted((root/'batches').iterdir()):
        if not dest.is_dir(): continue
        manifest_sha=r.sha(dest/'MANIFEST.json')
        _,m=r.load_batch(root,c,dest.name,manifest_sha)
        if m['context_sha256']!=context_sha: raise ValueError('batch context byte binding mismatch')
        complete=r.read_json(dest/'COMPLETED.json')
        summary=r.read_json(dest/'SUMMARY.json')
        if complete['context_id']!=c['context_id'] or complete['manifest_id']!=m['manifest_id']:
            raise ValueError('batch completion binding mismatch')
        if complete['summary_sha256']!=r.sha(dest/'SUMMARY.json') or summary['manifest_id']!=m['manifest_id']:
            raise ValueError('batch summary binding mismatch')
        if complete['actual_cross_calls']!=len(m['tasks']) or complete['owned_worker_processes_remaining']!=0:
            raise ValueError('batch was not completely terminal')
        started=r.read_json(dest/'STARTED.json')
        if started['context_id']!=c['context_id'] or started['manifest_id']!=m['manifest_id']:
            raise ValueError('batch start binding mismatch')
        for task in m['tasks']:
            target=dest/'attempts'/f"{task['index']:03}"
            rec,raw,full=r.load_payload(target,c,m,task)
            reservation=rec['reservation']
            if reservation not in ledger or reservation['task']!=task or reservation['manifest_id']!=m['manifest_id']:
                raise ValueError('worker completion does not match global reservation')
            if rec['source_pins_digest']!=r.digest(c['source_pins']) or rec['input_pins']!=c['input_pins']:
                raise ValueError('worker source/input pin binding mismatch')
            rawrec=r.read_json(target/'RAW.json');meta=rawrec['metadata']
            if rawrec['sha256']!=rec['raw_sha256'] or any(meta[k]!=v for k,v in
                [('order',task['order']),('subdivisions',task['subdivisions']),
                 ('inner_phase_budget',task['inner_phase_budget']),('r4y_context_id',c['context_id']),
                 ('manifest_id',m['manifest_id']),('candidate_basis_identity',c['candidate_basis_identity'])]):
                raise ValueError('raw metadata task binding mismatch')
            screens=r._screen_full(full,c['screens']);control=r.central_s_control(raw)
            if screens!=rec['qualification_screens'] or control!=rec['central_s_diagonal_control']:
                raise ValueError('stored screens disagree with fresh array analysis')
            name=label(task)
            if name in observations: raise ValueError('duplicate completed numerical task')
            if rec['moment_call_evidence']['radial_pairs']!=meta['radial_pairs']:
                raise ValueError('native moment count disagrees with cross metadata')
            row={'label':name,'task':task,'batch':dest.name,'global_attempt':reservation['global_attempt'],
                 'screens':screens,'central_control':control,'raw_sha256':rec['raw_sha256'],
                 'full_sha256':rec['full_sha256'],'radial_pairs':meta['radial_pairs'],
                 'wall_seconds':rec['wall_seconds'],'peak_rss_kib':rec['peak_rss_kib'],
                 'moment_call_evidence':rec['moment_call_evidence'],
                 'radial_total_call_evidence':rec['radial_total_call_evidence'],
                 'volume_relative_error':meta['volume_relative_error'],'raw':raw,'full':full}
            observations[name]=row
            for filename in ('RAW.npz','RAW.json','FULL.npz','COMPLETED.json'):
                bindings.append({'path':str(target/filename),'sha256':r.sha(target/filename)})
        batch_records.append({'name':dest.name,'manifest_id':m['manifest_id'],'manifest_sha256':manifest_sha,
            'summary_sha256':r.sha(dest/'SUMMARY.json'),'completed_sha256':r.sha(dest/'COMPLETED.json'),
            'actual_cross_calls':complete['actual_cross_calls'],'wall_seconds':summary['batch_wall_seconds'],
            'completed_indices':sorted(t['index'] for t in m['tasks'])})
    if len(observations)!=len(ledger) or sorted(x['global_attempt'] for x in observations.values())!=list(range(1,len(ledger)+1)):
        raise ValueError('not every globally reserved attempt has one completed raw payload')
    if not observations: raise ValueError('no completed tasks')
    all_pairs=[compare(a,b) for a,b in itertools.combinations(observations.values(),2)]
    def pair(a,b): return compare(observations[a],observations[b])
    f='_fortran_fortran'
    legacy=[pair('q56_h2'+f,'q64_h2'+f),pair('q56_h2'+f,'q48_h4'+f),pair('q64_h2'+f,'q48_h4'+f)]
    phase=[pair('q40_beta24'+f,'q48_beta24'+f),pair('q40_beta24'+f,'q40_beta12'+f),
           pair('q48_beta24'+f,'q40_beta12'+f)]
    agreement=[pair('q40_beta12'+f,'q64_h2'+f),pair('q48_beta24'+f,'q64_h2'+f)]
    prior_failed_phase=pair('q32_beta24'+f,'q40_beta24'+f)
    parity=pair('q40_h1_reference_python','q40_h1'+f)
    parity_pass=parity['six_raw_bitwise_equal'] and parity['full_bitwise_equal']
    selected_pass=parity_pass and all(p['conjunction_pass'] for p in legacy+phase+agreement)
    performance=[]
    reference=observations['q64_h2'+f]
    for name in ('q40_beta24'+f,'q48_beta24'+f,'q40_beta12'+f):
        x=observations[name]
        performance.append({'task':name,'reference':reference['label'],
            'reference_radial_pairs_over_task':reference['radial_pairs']/x['radial_pairs'],
            'reference_wall_seconds_over_task':reference['wall_seconds']/x['wall_seconds'],
            'timing_scope':'OVERLAPPING_LOCAL_WORKERS_OBSERVATION_NOT_CONTROLLED_BENCHMARK'})
    return {'schema':'BASS_R4Y_CENTRAL_RESULT_V1','context_id':c['context_id'],
        'context_sha256':context_sha,'source_pins':c['source_pins'],'input_pins':c['input_pins'],
        'analysis_source':{'path':str(Path(__file__).resolve()),'sha256':r.sha(__file__),
                           'execution_context_source_pin_member':False,'scope':'POST_RUN_READ_ONLY_ANALYSIS'},
        'status':'CENTRAL_LOCAL_SPATIAL_QUALIFICATION_PASS' if selected_pass else 'CENTRAL_LOCAL_SPATIAL_QUALIFICATION_UNRESOLVED',
        'selected_checks_pass':selected_pass,'backend_parity_pass':parity_pass,'backend_parity':parity,
        'legacy_selected_checks':legacy,'phase_selected_checks':phase,'cross_rule_agreement':agreement,
        'retained_initial_phase_failure':prior_failed_phase,'all_pair_observations':all_pairs,
        'thresholds':{**c['screens'],'central_identical_s_absolute_max':1e-12},
        'rows':[{k:v for k,v in x.items() if k not in ('raw','full')} for x in observations.values()],
        'batch_records':batch_records,'payload_bindings':bindings,'performance_observations':performance,
        'actual_raw_operator_calls':len(observations),'global_reserved_attempts':len(ledger),
        'maximum_raw_attempt_budget':r.CAP,'automatic_retries':0,'physical_calls_by_this_analysis':0,
        'batch_wall_seconds_sum':sum(x['wall_seconds'] for x in batch_records),
        'worker_wall_times_overlap_not_summed':True,'MPI_execution':False,'NCP64_scaling':'NOT_RUN',
        'qualification_scope':'ONE_EXACT_CENTRAL_GEOMETRY_AND_SEPARATE_R4X_BANK_ONLY',
        'continuous_error_bound':False,'whole_trajectory_derivative_test':False,
        'G02':'UNRESOLVED','production_admission':'HOLD','capture_execution_allowed':False,
        'all_bound':'OPEN','b_grid':'NO_GO'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',required=True);p.add_argument('--context-sha256',required=True)
    p.add_argument('--out',required=True);a=p.parse_args()
    result=analyze(a.root,a.context_sha256)
    concise={k:result[k] for k in ('status','actual_raw_operator_calls','global_reserved_attempts',
                                  'backend_parity_pass','legacy_selected_checks','phase_selected_checks','cross_rule_agreement')}
    if not result['selected_checks_pass']:
        print(json.dumps({**concise,'final_result_written':False},indent=2,allow_nan=False))
        raise SystemExit(2)
    r.write_json(a.out,result)
    print(json.dumps({**concise,'final_result_written':True,'result_sha256':r.sha(a.out)},indent=2,allow_nan=False))


if __name__=='__main__':main()
