"""Create-only, staged z=0 spatial diagnostics with a global 24-attempt budget.

init/prepare never evaluate physical operators. Each explicit run consumes fresh
globally unique reservations, including failed process launches. No retries,
finite differences, trajectories, MPI execution, or production promotion.
"""
from pathlib import Path
from dataclasses import replace
import argparse
import fcntl
from functools import partial
import hashlib
import json
import os
import re
import resource
import signal
import subprocess
import sys
import time
import traceback

import central_bootstrap
from central_bootstrap import HERE, R4X, REPO, FND, HPC
import numpy as np
from runtime import load_bank, atomic_file, write_json
from resource_profile import census
from qualified_provider import _raw_difference, _screen_full

GiB = 1024**3
CAP = 24
GRID = [(32,1),(40,1),(48,1),(56,1),(64,1),(48,2),(56,2),(64,2),(48,4),(56,4),(64,4)]
SCREENS = {'raw_cross_relative_max': 1e-9, 'operator_hermiticity_relative_max': 1e-11,
           'metric_min_ratio': 1e-8}
RAW_KEYS = ('S_tp', 'S_pt', 'H_tp', 'H_pt', 'D_tp', 'D_pt')
ENV = {k:'1' for k in ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','BLIS_NUM_THREADS',
                       'NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS')}
ENV.update(OMP_NUM_THREADS='2', OMP_DYNAMIC='FALSE', OMP_MAX_ACTIVE_LEVELS='1', OMP_PROC_BIND='FALSE')
INPUTS = {'BASIS.npz':'889001a751cd3cae93ad217336587f5fc58db11c0a496843ecc7e7bbd93f83ec',
          'BASIS.json':'3cf2359dd9802e84f9ec4dc45f3585e0aa9712de38a3fb0a077300d257150131',
          'SCIENCE_CONTEXT.json':'cf484b252092d642c8c8487a8bf70deb61e7b0b9f2bc2f522a3325a146e7f746'}
CANDIDATE = {'CANDIDATE.json':'77df01c595ff1ac14236ff4537d7be7dd78d9642c498433d3b6e60c8c38ef35f',
             'CANDIDATE.npz':'c948eab57638938407d4f34ee8bdae879b926c84fc0b55d91ac2e9105a1cfed5'}

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()

def read_json(path):
    def pairs(items):
        result = {}
        for k,v in items:
            if k in result: raise ValueError('duplicate JSON key: '+k)
            result[k] = v
        return result
    return json.loads(Path(path).read_text(), object_pairs_hook=pairs,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))

def validate_pins(pins):
    for path, expected in pins.items():
        if sha(path) != expected: raise ValueError('pinned file changed: '+path)

def sources():
    files = set(FND.rglob('*.py')) | set((REPO/'cr_repro').rglob('*.py'))
    files |= set(R4X.glob('*.py')) | set(R4X.glob('*.f90')) | set(HERE.glob('*.py'))
    files |= set(HPC.glob('*.py')) | set((HPC/'native').glob('*.f90'))
    files.add(FND/'tp2a_analytic_pruning_20260926/code/moment_kernel.cpp')
    return {str(p.resolve()):sha(p) for p in sorted(files) if not p.name.startswith('test_')}

def check_environment():
    if any(os.environ.get(k) != v for k,v in ENV.items()):
        raise ValueError('strict BLAS=1, OMP=2 environment required before Python import')

def admit_resources(workers, info):
    if type(workers) is not int or not 1 <= workers <= 3: raise ValueError('workers must be 1..3')
    slots = 2*workers+1
    if slots > min(info['usable_cpu_budget'],len(info['affinity_cpus'])):
        raise ValueError('two-CPU workers plus coordinator exceed CPU quota')
    available = min(info['memory_limit_bytes'],info['memory_available_bytes'])
    reserve = max(GiB,available//8); estimate = workers*GiB+GiB//2
    if estimate > available-reserve: raise ValueError('estimated RSS exceeds available memory after reserve')
    cpus = info['affinity_cpus'][:slots]
    return {'workers':workers, 'worker_cpu_sets':[cpus[2*i:2*i+2] for i in range(workers)],
            'coordinator_cpu_id':cpus[-1], 'moment_threads':2, 'radial_threads':1,
            'estimated_total_rss_bytes':estimate, 'memory_reserve_bytes':reserve,
            'memory_available_estimate_bytes':available, 'rss_estimate_not_enforcement':True,
            'MPI_execution':False, 'NCP64_scaling':'NOT_RUN', 'environment':ENV}

def validate_tasks(tasks):
    if not isinstance(tasks,list) or not 1 <= len(tasks) <= CAP: raise ValueError('bounded nonempty task list required')
    normalized=[]; seen=set()
    for row in tasks:
        if not isinstance(row,dict): raise ValueError('task must be an object')
        required={'order','subdivisions','moment_backend','radial_backend'}
        if set(row) not in (required,required|{'inner_phase_budget'}): raise ValueError('task keys invalid')
        row={**row,'inner_phase_budget':row.get('inner_phase_budget')}
        q,s = row['order'],row['subdivisions']
        if type(q) is not int or type(s) is not int or (q,s) not in GRID: raise ValueError('task outside original resolution grid')
        if row['moment_backend'] not in ('reference','fortran') or row['radial_backend'] not in ('python','fortran'):
            raise ValueError('unknown backend')
        beta=row['inner_phase_budget']
        if beta is not None and (type(beta) not in (int,float) or beta not in (24,12,6) or s!=1):
            raise ValueError('inner phase budget must be null/24/12/6; new rule requires subdivisions=1')
        ident=digest(row)
        if ident in seen: raise ValueError('duplicate task')
        seen.add(ident); normalized.append({**row,'index':len(normalized),'task_id':ident})
    return normalized

def init(args):
    check_environment()
    inputs,candidate,build,radial,contract = [Path(x).resolve() for x in
        (args.inputs,args.candidate,args.build,args.radial_manifest,args.contract)]
    if {n:sha(inputs/n) for n in INPUTS} != INPUTS: raise ValueError('archived input bytes changed')
    if {n:sha(candidate/n) for n in CANDIDATE} != CANDIDATE: raise ValueError('R4X candidate bytes changed')
    original,record=load_bank(inputs)
    from basis_representation import load_candidate, _source_identity
    bank=load_candidate(candidate,backend='python')  # no native load/evaluation
    new_record=read_json(candidate/'CANDIDATE.json')
    if len(bank)!=5 or len(original)!=5: raise ValueError('five radial modes required')
    for old,new in zip(original,bank):
        if (old.l,old.principal_n,old.energy)!=(new.l,new.principal_n,new.energy) or not np.array_equal(old.edges,new.edges):
            raise ValueError('candidate changed labels/energy/mesh')
    science=read_json(inputs/'SCIENCE_CONTEXT.json')['context']['contract']
    if (science['b_a0'],science['energy_keV_per_u'],science['same_center_order']) != (2.,100.,20):
        raise ValueError('trajectory/same-center contract mismatch')
    if [(x['order'],x['subdivisions']) for x in science['runtime_reference_resolutions']] != GRID:
        raise ValueError('original resolution ladder mismatch')
    if any(science['screens'][k]!=v for k,v in SCREENS.items()): raise ValueError('original qualification screens mismatch')
    nb=read_json(build/'BUILD_HPC.json')
    expected={'reference':sha(FND/'tp2a_analytic_pruning_20260926/code/moment_kernel.cpp'),
              'fortran':sha(HPC/'native/moment_kernel_real.f90')}
    if nb['source_hashes']!=expected or set(nb['libraries'])!={'libreference.so','libmoments_f90.so'}:
        raise ValueError('native moment source/library binding invalid')
    for n,h in nb['libraries'].items():
        if sha(build/n)!=h: raise ValueError('moment native binary changed')
    if {b['name'] for b in nb['builds']}!={'reference','fortran'}: raise ValueError('both moment build records required')
    for b in nb['builds']:
        flags=('-O3','-fno-fast-math','-ffp-contract=off') + (('-fopenmp','-fprotect-parens') if b['name']=='fortran' else ())
        if b['exit_code']!=0 or any(f not in b['command'] for f in flags): raise ValueError('strict moment build flags missing')
        if any(x in b['command'] for x in ('-Ofast','-ffast-math','-fassociative-math')): raise ValueError('unsafe moment build flags')
    rn=read_json(radial)
    if rn.get('schema')!='BASS_R4X_CONTINUOUS_NATIVE_V1' or rn.get('exit_code')!=0 or rn['source_hashes']!=_source_identity():
        raise ValueError('radial build/source binding invalid')
    if sha(radial.parent/'libcontinuous.so')!=rn['library_sha256']: raise ValueError('radial native binary changed')
    for flag in ('-O3','-fno-fast-math','-ffp-contract=off','-fprotect-parens','-fopenmp'):
        if flag not in rn['command']: raise ValueError('radial strict build flag missing')
    if any(x in rn['command'] for x in ('-Ofast','-ffast-math','-fassociative-math')): raise ValueError('unsafe radial build flag')
    from cr_repro.observables import projectile_speed_au
    pins={str(inputs/n):h for n,h in INPUTS.items()}
    pins.update({str(candidate/n):h for n,h in CANDIDATE.items()})
    for p in (build/'BUILD_HPC.json',build/'libreference.so',build/'libmoments_f90.so',radial,
              radial.parent/'libcontinuous.so',contract): pins[str(p)]=sha(p)
    info=census()
    core={'schema':'BASS_R4Y_CENTRAL_CONTEXT_V1','inputs':str(inputs),'candidate':str(candidate),
          'build':str(build),'radial_manifest':str(radial),'contract':str(contract),
          'input_pins':pins,'source_pins':sources(),'original_basis_identity':record['identity'],
          'candidate_basis_identity':new_record['identity'],'speed_a0_per_ta':projectile_speed_au(100.),
          'fixed_geometry':{'z_a0':0.,'b_a0':2.,'energy_keV_per_u':100.,'time_hex':float(0.).hex()},
          'fixed_numerics':{'same_center_order':20,'phase_budget':None,'sector':'full','batch':1024},
          'resolution_grid':[list(x) for x in GRID],'screens':SCREENS,'raw_attempt_budget':CAP,
          'resources':admit_resources(args.workers,info),'initial_census':info,
          'timeout_seconds_per_attempt':1800,'automatic_retries':0,'source_context_reuse':False,
          'G02':'UNRESOLVED','production_admission':'HOLD','capture_execution_allowed':False,
          'continuous_error_bound':False,'all_bound':'OPEN','b_grid':'NO_GO'}
    context={**core,'context_id':digest(core)}
    out=Path(args.out).resolve();out.mkdir(parents=True,exist_ok=False)
    write_json(out/'CONTEXT.json',context)
    return {'status':'CONTEXT_FROZEN_NO_PHYSICAL_CALLS','context_sha256':sha(out/'CONTEXT.json'),
            'context_id':context['context_id'],'out':str(out)}

def load_context(out,expected_sha):
    out=Path(out).resolve()
    if sha(out/'CONTEXT.json')!=expected_sha: raise ValueError('context byte hash mismatch')
    c=read_json(out/'CONTEXT.json')
    if c.get('schema')!='BASS_R4Y_CENTRAL_CONTEXT_V1' or digest({k:v for k,v in c.items() if k!='context_id'})!=c['context_id']:
        raise ValueError('context identity mismatch')
    if c['raw_attempt_budget']!=CAP or c['screens']!=SCREENS or c['resolution_grid']!=[list(x) for x in GRID]:
        raise ValueError('frozen budget/screens/grid changed')
    validate_pins(c['input_pins']);validate_pins(c['source_pins']);check_environment()
    return out,c

def batch_path(out,name):
    if not isinstance(name,str) or re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}',name) is None:
        raise ValueError('simple bounded batch name required')
    return out/'batches'/name

def prepare(args):
    out,c=load_context(args.out,args.context_sha256)
    plan=read_json(args.plan)
    if set(plan)!={'tasks'}: raise ValueError('plan must contain only tasks')
    tasks=validate_tasks(plan['tasks'])
    core={'schema':'BASS_R4Y_BATCH_MANIFEST_V1','context_id':c['context_id'],
          'context_sha256':args.context_sha256,'batch':args.batch,'tasks':tasks,
          'plan_sha256':sha(args.plan),'plan':plan,'no_retries':True}
    m={**core,'manifest_id':digest(core)}
    dest=batch_path(out,args.batch);dest.mkdir(parents=True,exist_ok=False)
    write_json(dest/'MANIFEST.json',m)
    return {'status':'BATCH_FROZEN_NO_PHYSICAL_CALLS','manifest_sha256':sha(dest/'MANIFEST.json'),
            'manifest_id':m['manifest_id'],'batch':args.batch,'tasks':len(tasks)}

def load_batch(out,c,batch,expected_sha):
    dest=batch_path(out,batch)
    if sha(dest/'MANIFEST.json')!=expected_sha: raise ValueError('batch manifest byte hash mismatch')
    m=read_json(dest/'MANIFEST.json')
    if m.get('schema')!='BASS_R4Y_BATCH_MANIFEST_V1' or m['context_id']!=c['context_id'] or m['batch']!=batch:
        raise ValueError('batch context binding mismatch')
    if digest({k:v for k,v in m.items() if k!='manifest_id'})!=m['manifest_id']:
        raise ValueError('manifest identity mismatch')
    if m['tasks']!=validate_tasks(m['plan']['tasks']): raise ValueError('batch tasks changed')
    return dest,m

def reservations(out,c):
    rows=[]
    for p in sorted((out/'reservations').glob('*.json')):
        rec=read_json(p)
        if p.name!=f'{len(rows)+1:03}.json' or rec['global_attempt']!=len(rows)+1 or rec['context_id']!=c['context_id']:
            raise ValueError('global reservation ledger discontinuity/identity mismatch')
        rows.append(rec)
    if len(rows)>CAP or len({r['task']['task_id'] for r in rows})!=len(rows):
        raise ValueError('global budget/unique task ledger invalid')
    return rows

class CountingMoment:
    def __init__(self,kernel):
        self.kernel=kernel;self.calls=0;self.points=0;self.real_calls=0;self.fallback_calls=0
        self.backend_identity=kernel.backend_identity;self.receipt=kernel.receipt
    def accumulate(self,*args,**kwargs):
        self.calls+=1;self.points+=len(args[0])
        if kwargs.get('real_coefficients',False): self.real_calls+=1
        else: self.fallback_calls+=1
        return self.kernel.accumulate(*args,**kwargs)
    def evidence(self):
        return {'calls':self.calls,'radial_pairs':self.points,'real_coefficient_calls':self.real_calls,
                'complex_fallback_calls':self.fallback_calls,'backend_identity':self.backend_identity,
                'configured_openmp_threads':self.kernel.threads,'actual_openmp_team_observed':False,
                'reference_real_kernel_is_serial':self.kernel.backend=='reference'}

class CountingRadial:
    def __init__(self,native):
        self.native=native;self.calls=0;self.points=0;self.observed=set()
    def evaluate(self,mode,cells,s,h,threads):
        self.calls+=1;self.points+=len(cells)
        answer=self.native.evaluate(mode,cells,s,h,threads)
        self.observed.add(self.native.last_observed_threads)
        return answer
    def evidence(self):
        return {'calls':self.calls,'radial_points':self.points,'observed_openmp_team_sizes':sorted(self.observed),
                'configured_openmp_threads':1,'backend':'FORTRAN_SHARED_ENDPOINT_BUBBLE'}

def save_npz(path,arrays):
    atomic_file(path,lambda f:np.savez_compressed(f,**arrays))

def run_worker(out,context_sha,batch,manifest_sha,index,slot):
    out,c=load_context(out,context_sha);dest,m=load_batch(out,c,batch,manifest_sha)
    if type(index) is not int or not 0<=index<len(m['tasks']): raise ValueError('worker task index invalid')
    if type(slot) is not int or not 0<=slot<c['resources']['workers']: raise ValueError('worker slot invalid')
    task=m['tasks'][index];cpus=c['resources']['worker_cpu_sets'][slot]
    matches=[r for r in reservations(out,c) if r['manifest_id']==m['manifest_id'] and r['task']==task]
    if len(matches)!=1 or matches[0]['worker_cpu_set']!=cpus: raise ValueError('worker reservation mismatch')
    if set(cpus)!=os.sched_getaffinity(0): raise ValueError('worker exact affinity mismatch')
    target=dest/'attempts'/f'{index:03}';target.mkdir(parents=True,exist_ok=False)
    write_json(target/'STARTED.json',{'task':task,'reservation':matches[0],'pid':os.getpid(),'affinity':cpus})
    started=time.monotonic()
    try:
        from basis_representation import load_candidate
        from bass_foundations.two_center import Trajectory,symmetric_channels
        from kernel import HPCMomentKernel
        import continuous_exact_cross as cross_module
        import continuous_full_operator as full_module
        bank=load_candidate(c['candidate'],backend=task['radial_backend'],native_manifest=c['radial_manifest'],threads=1)
        radial=None
        if task['radial_backend']=='fortran':
            radial=CountingRadial(bank[0].native)
            bank=tuple(replace(b,native=radial) for b in bank)
        channels=symmetric_channels(bank)
        if len(channels)!=18: raise ValueError('full18 basis required')
        tr=Trajectory(((0.,0.,0.),(2.,0.,0.)),((0.,0.,0.),(0.,0.,c['speed_a0_per_ta'])))
        kernel=CountingMoment(HPCMomentKernel(c['build'],backend=task['moment_backend'],threads=2))
        pair_rule=None
        if task['inner_phase_budget'] is not None:
            from phase_pairs import phase_pairs
            pair_rule=partial(phase_pairs,phase_budget=task['inner_phase_budget'])
        raw=cross_module.cross(tr,channels,0.,kernel,order=task['order'],subdivisions=task['subdivisions'],
                               phase_budget=None,batch=1024,sector='full',pair_rule=pair_rule)
        raw['metadata'].update(backend=kernel.backend_identity,kernel_build=kernel.receipt,
            r4y_context_id=c['context_id'],manifest_id=m['manifest_id'],candidate_basis_identity=c['candidate_basis_identity'],
            radial_backend=task['radial_backend'],moment_backend=task['moment_backend'],archived_context_compatible=False,
            inner_phase_budget=task['inner_phase_budget'],
            pair_rule='ORIGINAL_BATCHES' if pair_rule is None else 'R4Y_INNER_PHASE_PANELS')
        save_npz(target/'RAW.npz',{k:raw[k] for k in RAW_KEYS})
        radial_cross=radial.evidence() if radial else {'backend':'PYTHON_FP64_SHARED_ENDPOINT_BUBBLE','OpenMP_execution':False}
        write_json(target/'RAW.json',{'metadata':raw['metadata'],'sha256':sha(target/'RAW.npz'),
            'moment_call_evidence':kernel.evidence(),'radial_cross_call_evidence':radial_cross})
        bound=full_module._bind_cross(tr,channels,0.,raw,raw['metadata'])
        full=full_module.assemble_full(tr,channels,0.,same_order=20,cross=bound)
        arrays={k:full[k] for k in ('S','H','D')}
        for center in ('T','P'):
            for k in ('S','H','D','H0','V_other','A','indices'): arrays[center+'__'+k]=full['same_center'][center][k]
        save_npz(target/'FULL.npz',arrays)
        rec={'status':'COMPLETED_CENTRAL_SPATIAL_DIAGNOSTIC','task':task,'context_id':c['context_id'],
             'manifest_id':m['manifest_id'],'reservation':matches[0],'candidate_basis_identity':c['candidate_basis_identity'],
             'raw_sha256':sha(target/'RAW.npz'),'full_sha256':sha(target/'FULL.npz'),
             'raw_metadata_sha256':sha(target/'RAW.json'),'input_pins':c['input_pins'],
             'source_pins_digest':digest(c['source_pins']),'diagnostics':full['diagnostics'],
             'central_s_diagonal_control':central_s_control(raw),
             'qualification_screens':_screen_full(full,c['screens']),'moment_call_evidence':kernel.evidence(),
             'radial_total_call_evidence':radial.evidence() if radial else radial_cross,
             'wall_seconds':time.monotonic()-started,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
             'pid':os.getpid(),'affinity':sorted(os.sched_getaffinity(0)),
             'production_admission':'HOLD','capture_execution_allowed':False}
        write_json(target/'COMPLETED.json',rec)
        return {'task_id':task['task_id'],'status':rec['status'],'wall_seconds':rec['wall_seconds']}
    except BaseException as exc:
        write_json(target/'FAILED.json',{'task':task,'context_id':c['context_id'],'exception':type(exc).__name__,
            'message':str(exc),'traceback':traceback.format_exc(),'wall_seconds':time.monotonic()-started,'no_retry':True})
        raise

def load_payload(target,c,m,task):
    rec=read_json(target/'COMPLETED.json')
    if rec['task']!=task or rec['context_id']!=c['context_id'] or rec['manifest_id']!=m['manifest_id']:
        raise ValueError('completed task binding mismatch')
    for file,key in (('RAW.npz','raw_sha256'),('FULL.npz','full_sha256'),('RAW.json','raw_metadata_sha256')):
        if sha(target/file)!=rec[key]: raise ValueError('completed payload changed')
    with np.load(target/'RAW.npz',allow_pickle=False) as z: raw={k:z[k].copy() for k in RAW_KEYS}
    with np.load(target/'FULL.npz',allow_pickle=False) as z: full={k:z[k].copy() for k in z.files}
    for k in ('S','H','D'):
        if full[k].shape!=(18,18) or not np.isfinite(full[k]).all(): raise ValueError('invalid full operator')
        if not np.array_equal(full[k][:9,9:],raw[k+'_tp']) or not np.array_equal(full[k][9:,:9],raw[k+'_pt']):
            raise ValueError('full/raw assembly mismatch')
    if any(raw[k].shape!=(9,9) or not np.isfinite(raw[k]).all() for k in RAW_KEYS): raise ValueError('invalid raw operator')
    return rec,raw,full

def central_s_control(raw):
    """Independent exact-zero central identical-s control; never changes raw D."""
    a=np.asarray(raw['D_tp'])
    if a.shape!=(9,9) or not np.isfinite(a).all(): raise ValueError('central control requires finite full nine-channel raw D_tp')
    values=[float(abs(a[i,i])) for i in range(3)]
    return {'indices_0_based':[0,1,2],'D_tp_diagonal_absolute':values,
            'maximum_absolute':max(values),'absolute_threshold':1e-12,'pass':max(values)<=1e-12,
            'reference':'EXACT_ZERO_AT_Z0_IDENTICAL_REAL_S_CHANNELS_DERIVED_IN_TASK_CONTRACT',
            'raw_D_projected':False}

def summarize(out,c,dest,m):
    rows=[];payloads=[]
    for task in m['tasks']:
        rec,raw,full=load_payload(dest/'attempts'/f"{task['index']:03}",c,m,task)
        rows.append({'task':task,'raw_sha256':rec['raw_sha256'],'full_sha256':rec['full_sha256'],
            'screens':rec['qualification_screens'],'central_s_diagonal_control':central_s_control(raw),
            'wall_seconds':rec['wall_seconds'],'peak_rss_kib':rec['peak_rss_kib'],
            'moment_call_evidence':rec['moment_call_evidence'],'radial_total_call_evidence':rec['radial_total_call_evidence']})
        payloads.append((task,raw,full))
    comparisons=[]
    for i,(a,ar,af) in enumerate(payloads):
        for b,br,bf in payloads[i+1:]:
            rawmax,detail=_raw_difference(ar,br)
            same_rule=(a['order'],a['subdivisions'],a['inner_phase_budget'])==(b['order'],b['subdivisions'],b['inner_phase_budget'])
            same_backend=(a['moment_backend'],a['radial_backend'])==(b['moment_backend'],b['radial_backend'])
            comparisons.append({'a':a['task_id'],'b':b['task_id'],'same_rule':same_rule,'same_backend':same_backend,
                'max_six_raw_relative_difference':rawmax,'six_raw_relative_differences':detail,
                'six_raw_bitwise_equal':all(np.array_equal(ar[k],br[k]) for k in RAW_KEYS),
                'full_bitwise_equal':all(np.array_equal(af[k],bf[k]) for k in ('S','H','D')),
                'full_relative_differences':{k:float(np.linalg.norm(af[k]-bf[k])/max(np.linalg.norm(af[k]),np.linalg.norm(bf[k]),1e-300)) for k in ('S','H','D')},
                'raw_resolution_screen_pass':rawmax<=c['screens']['raw_cross_relative_max'] if same_backend and not same_rule else None,
                'interpretation':'OBSERVED_DIFFERENCE_NOT_CERTIFIED_ERROR'})
    return {'schema':'BASS_R4Y_BATCH_SUMMARY_V1','context_id':c['context_id'],'manifest_id':m['manifest_id'],
        'rows':rows,'pair_comparisons':comparisons,'actual_cross_calls':len(rows),'global_reserved_attempts':len(reservations(out,c)),
        'G02':'UNRESOLVED','production_admission':'HOLD','capture_execution_allowed':False,'continuous_error_bound':False}

def terminate_owned(running):
    for proc,log,index,tick in running.values():
        if proc.poll() is None:
            try: os.killpg(proc.pid,signal.SIGTERM)
            except ProcessLookupError: pass
    deadline=time.monotonic()+2
    for proc,log,index,tick in running.values():
        try: proc.wait(timeout=max(.01,deadline-time.monotonic()))
        except subprocess.TimeoutExpired:
            try: os.killpg(proc.pid,signal.SIGKILL)
            except ProcessLookupError: pass
            proc.wait(timeout=5)
        finally: log.close()

def execute(out,context_sha,batch,manifest_sha):
    out,c=load_context(out,context_sha);dest,m=load_batch(out,c,batch,manifest_sha)
    lock=(out/'budget.lock').open('a+b')
    try:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BaseException:
        lock.close();raise
    running={};completed=[];reserved=0;started=time.monotonic();original_affinity=os.sched_getaffinity(0)
    previous_term=signal.getsignal(signal.SIGTERM)
    def stop_on_term(signum,frame):
        raise SystemExit('coordinator received SIGTERM; cancel owned workers')
    signal.signal(signal.SIGTERM,stop_on_term)
    begun=False
    try:
        history=reservations(out,c)
        if len(history)+len(m['tasks'])>CAP: raise ValueError('global attempt cap would be exceeded')
        if {r['task']['task_id'] for r in history}&{t['task_id'] for t in m['tasks']}:
            raise ValueError('task was already reserved; retries/repeated tasks forbidden')
        actual=census();fresh=admit_resources(c['resources']['workers'],actual)
        if any(fresh[k]!=c['resources'][k] for k in ('worker_cpu_sets','coordinator_cpu_id')):
            raise ValueError('fresh CPU allocation changed')
        write_json(dest/'STARTED.json',{'context_id':c['context_id'],'manifest_id':m['manifest_id'],
            'fresh_census':actual,'resource_admission':fresh,'pid':os.getpid(),'prior_reserved_attempts':len(history)})
        begun=True
        os.sched_setaffinity(0,{fresh['coordinator_cpu_id']})
        next_index=0
        while next_index<len(m['tasks']) or running:
            for slot,cpus in enumerate(fresh['worker_cpu_sets']):
                if slot in running or next_index>=len(m['tasks']): continue
                index=next_index;task=m['tasks'][index]
                validate_pins(c['input_pins']);validate_pins(c['source_pins'])
                attempt=len(history)+reserved+1
                reservation={'context_id':c['context_id'],'manifest_id':m['manifest_id'],'batch':batch,
                    'global_attempt':attempt,'task':task,'worker_cpu_set':cpus,'raw_attempt_budget':CAP}
                write_json(out/'reservations'/f'{attempt:03}.json',reservation)
                reserved+=1
                logpath=dest/'logs'/f'{index:03}.log';logpath.parent.mkdir(exist_ok=True)
                log=logpath.open('xb')
                argv=[sys.executable,str(Path(__file__).resolve()),'worker','--out',str(out),
                    '--context-sha256',context_sha,'--batch',batch,'--manifest-sha256',manifest_sha,
                    '--index',str(index),'--slot',str(slot)]
                try:
                    proc=subprocess.Popen(argv,stdout=log,stderr=subprocess.STDOUT,
                        env={**os.environ,**ENV},start_new_session=True,
                        preexec_fn=lambda cpus=cpus:os.sched_setaffinity(0,set(cpus)))
                except BaseException:
                    log.close();raise
                running[slot]=(proc,log,index,time.monotonic());next_index+=1
            for slot,(proc,log,index,tick) in list(running.items()):
                code=proc.poll()
                if code is None:
                    if time.monotonic()-tick>c['timeout_seconds_per_attempt']: raise TimeoutError(f'raw attempt {index} exceeded frozen timeout')
                    continue
                log.close();del running[slot]
                if code!=0: raise RuntimeError(f'raw attempt {index} failed with {code}; no retry')
                completed.append(index)
                print(json.dumps({'event':'attempt_completed','batch':batch,'index':index,'completed_count':len(completed)}),flush=True)
            if running: time.sleep(.1)
        summary=summarize(out,c,dest,m);summary['batch_wall_seconds']=time.monotonic()-started
        summary['wall_times_overlap_do_not_sum']=True
        write_json(dest/'SUMMARY.json',summary)
        write_json(dest/'COMPLETED.json',{'context_id':c['context_id'],'manifest_id':m['manifest_id'],
            'summary_sha256':sha(dest/'SUMMARY.json'),'actual_cross_calls':len(completed),
            'global_reserved_attempts':len(reservations(out,c)),'owned_worker_processes_remaining':0})
        return {'status':'BATCH_COMPLETED','batch':batch,'actual_cross_calls':len(completed),
                'global_reserved_attempts':len(reservations(out,c)),'summary':str(dest/'SUMMARY.json')}
    except BaseException as exc:
        terminate_owned(running)
        if begun:
            write_json(dest/'FAILED.json',{'context_id':c['context_id'],'manifest_id':m['manifest_id'],
                'exception':type(exc).__name__,'message':str(exc),'reserved_attempts_this_batch':reserved,
                'global_reserved_attempts':len(reservations(out,c)),'completed_indices':completed,
                'no_retry':True,'owned_worker_processes_remaining':0})
        raise
    finally:
        os.sched_setaffinity(0,original_affinity)
        signal.signal(signal.SIGTERM,previous_term)
        fcntl.flock(lock,fcntl.LOCK_UN);lock.close()

def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    a=sub.add_parser('init')
    for k in ('inputs','candidate','build','radial-manifest','contract','out'): a.add_argument('--'+k,required=True)
    a.add_argument('--workers',type=int,default=3)
    for name in ('prepare','run','worker'):
        a=sub.add_parser(name)
        for k in ('out','context-sha256','batch'): a.add_argument('--'+k,required=True)
        if name=='prepare': a.add_argument('--plan',required=True)
        else: a.add_argument('--manifest-sha256',required=True)
        if name=='worker':
            a.add_argument('--index',type=int,required=True);a.add_argument('--slot',type=int,required=True)
    a=p.parse_args()
    if a.command=='init': result=init(a)
    elif a.command=='prepare': result=prepare(a)
    elif a.command=='run': result=execute(a.out,a.context_sha256,a.batch,a.manifest_sha256)
    else: result=run_worker(a.out,a.context_sha256,a.batch,a.manifest_sha256,a.index,a.slot)
    print(json.dumps(result,indent=2,allow_nan=False))

if __name__=='__main__': main()
