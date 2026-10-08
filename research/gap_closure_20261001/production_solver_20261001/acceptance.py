"""Compare the frozen local pilot and run its explicit cache-only restart check.

This performs no native operator calls. It never supplies a scattering state.
"""
from pathlib import Path
import argparse
import json
import sys
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[2]))
sys.path.insert(0,str(HERE/'runtime'))
from solver_plan import make_plan
from checkpoint_solver import run_cached,write_new,sha

def load(p):return json.loads(Path(p).read_text())

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__,allow_abbrev=False)
    p.add_argument('--fortran-run',required=True);p.add_argument('--reference-run',required=True)
    p.add_argument('--out',required=True)
    a=p.parse_args(argv);f=Path(a.fortran_run);r=Path(a.reference_run);out=Path(a.out)
    out.mkdir(parents=True,exist_ok=False)
    scope=load(HERE/'ACCEPTANCE_SCOPE.json')
    mf=load(f/'EXECUTION.json');mr=load(r/'EXECUTION.json')
    cf=mf['context'];cr=mr['context']
    for directory in (f,r):
        if not load(directory/'SUPERVISOR_RESULT.json')['success'] or not load(directory/'RESULT.json')['ok']:
            raise ValueError('both physical qualifications must complete before cache-only acceptance')
    if cf['backend']!='fortran' or cr['backend']!='reference':raise ValueError('backend comparison is not F90/C++')
    for key in ('physics','basis_identity','input_files','native_build_sha256','native_libraries',
                'native_source_hashes','qualification_contract','source_pins','same_center_order',
                'phase_budget','sector','cross_batch'):
        if cf[key]!=cr[key]:raise ValueError('backend comparison input differs: '+key)
    if len(mf['tasks'])!=4 or len(mr['tasks'])!=1 or mf['tasks'][0]['time_hex']!=mr['tasks'][0]['time_hex']:
        raise ValueError('pilot exact query plan mismatch')
    from cr_repro.observables import projectile_speed_au
    speed=projectile_speed_au(scope['model']['energy_keV_per_u'])
    for manifest,key in ((mf,'fortran'),(mr,'reference')):
        if any(manifest['resources'][k]!=scope[key][k] for k in ('ranks','threads','cpus')):
            raise ValueError('pilot rank/thread/CPU scope mismatch')
    if (float.fromhex(mf['tasks'][0]['time_hex'])!=scope['window_z_a0'][0]/speed or
        float.fromhex(mf['tasks'][-1]['time_hex'])!=scope['window_z_a0'][1]/speed):
        raise ValueError('pilot window differs from predeclared scope')
    attempts_f=f/'queue/tasks/00000000/attempts';attempts_r=r/'queue/tasks/00000000/attempts'
    names_f=sorted(x.name for x in attempts_f.glob('*.npz'));names_r=sorted(x.name for x in attempts_r.glob('*.npz'))
    if names_f!=names_r or len(names_f)<2:raise ValueError('qualification prefixes differ')
    differences=[]
    for name in names_f:
        pf=attempts_f/name;pr=attempts_r/name
        if load(pf.with_suffix('.json'))['resolution']!=load(pr.with_suffix('.json'))['resolution']:
            raise ValueError('resolution differs')
        with np.load(pf,allow_pickle=False) as af,np.load(pr,allow_pickle=False) as ar:
            if set(af.files)!=set(ar.files):raise ValueError('operator payload key mismatch')
            for key in sorted(af.files):
                x=af[key];y=ar[key]
                if x.shape!=y.shape or not np.isfinite(x).all() or not np.isfinite(y).all():
                    raise ValueError('operator shape/finiteness mismatch')
                delta=float(np.linalg.norm(x-y)/max(scope['parity']['norm_floor'],float(np.linalg.norm(y))))
                differences.append({'attempt':name,'array':key,'relative_frobenius_difference':delta,
                                    'bitwise_equal':bool(x.dtype==y.dtype and x.tobytes()==y.tobytes())})
    parity={'scope':'SAME_INPUT_FIRST_PHYSICAL_QUERY_ALL_ATTEMPT_FULL_AND_RAW_ARRAYS',
            'tolerance':scope['parity']['relative_frobenius_max'],'arrays':differences,
            'maximum_difference':max(x['relative_frobenius_difference'] for x in differences),
            'all_bitwise_equal':all(x['bitwise_equal'] for x in differences)}
    parity['passed']=parity['maximum_difference']<=parity['tolerance']
    write_new(out/'PHYSICAL_PARITY.json',parity)
    if not parity['passed']:raise ArithmeticError('predeclared physical backend parity failed')
    t0=float.fromhex(mf['tasks'][0]['time_hex']);tf=float.fromhex(mf['tasks'][-1]['time_hex'])
    plan=make_plan(t0,tf,scope['steps'],cf['context_id'],qualification_contract=cf['qualification_contract'],
                   selected_indices=cf['physics']['selected_indices'])
    if [q['time_hex'] for q in plan['queries']]!=[q['time_hex'] for q in mf['tasks']]:
        raise ValueError('operator and midpoint exact time grids differ')
    write_new(out/'SOLVER_PLAN.json',plan)
    c0=np.zeros(18,dtype=complex);c0[0]=1.
    full=run_cached(plan,f/'cache',out/'full',c0)
    partial=run_cached(plan,f/'cache',out/'paused',c0,stop_after_steps=1)
    resumed=run_cached(plan,f/'cache',out/'resumed',c0,resume_from=out/'paused')
    with np.load(out/'full/CANDIDATE_RESULT.npz',allow_pickle=False) as x, np.load(out/'resumed/CANDIDATE_RESULT.npz',allow_pickle=False) as y:
        exact={key:bool(x[key].shape==y[key].shape and x[key].dtype==y[key].dtype and
                        x[key].tobytes()==y[key].tobytes()) for key in x.files}
    result={'schema':'BASS_R4U_PHYSICAL_PIPELINE_ACCEPTANCE_V1',
            'acceptance_scope_sha256':sha(HERE/'ACCEPTANCE_SCOPE.json'),'acceptance_source_sha256':sha(__file__),
            'fortran_execution_sha256':sha(f/'EXECUTION.json'),'reference_execution_sha256':sha(r/'EXECUTION.json'),
            'physical_operator_queries':5,'physical_raw_attempts':sum(load(x/'queue/QUEUE_RECEIPT.json')['raw_attempts_reserved'] for x in (f,r)),
            'parity':parity,'full_vs_resume_bitwise':exact,'full':full,'partial':partial,'resumed':resumed,
            'initial_state_scope':scope['initial_state'],'performance_scope':scope['performance'],
            'mpi_physical_run':False,'NCP64_run':False,'new_native_calls_in_this_script':0,
            'temporal_accuracy_certified':False,**scope['claim_ceilings']}
    result['passed']=all(exact.values()) and full['discrete_norm_gate'] and resumed['discrete_norm_gate']
    write_new(out/'ACCEPTANCE_RESULT.json',result)
    print(json.dumps({k:result[k] for k in ('passed','physical_operator_queries','physical_raw_attempts','full_vs_resume_bitwise','production','capture')},indent=2))
    return 0 if result['passed'] else 1

if __name__=='__main__':raise SystemExit(main())
