"""Durable cache-only execution of the unchanged TP1 midpoint recurrence."""
from pathlib import Path
import hashlib
import json
import math
import os
import platform
import tempfile
import traceback
import numpy as np
import scipy
from scipy.linalg import solve,solve_triangular
import bootstrap_runtime as paths
from execution_admission import strict_json,THREAD_KEYS
from metric_transport import candidate_step,metric_frame_generator
from reference_transport import normalize_metric_state
from qualified_cache import QualifiedCache,sha
from solver_plan import validate_plan,digest,CEILINGS,METHOD

def _atomic(path,writer):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix='.partial_',dir=path.parent)
    try:
        with os.fdopen(fd,'wb') as stream:
            writer(stream);stream.flush();os.fsync(stream.fileno())
        os.link(tmp,path)
        directory=os.open(path.parent,os.O_RDONLY)
        try:os.fsync(directory)
        finally:os.close(directory)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)

def write_new(path,value):
    data=(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n').encode()
    _atomic(path,lambda stream:stream.write(data))

def _copy_new(source,target):
    data=Path(source).read_bytes();_atomic(target,lambda stream:stream.write(data))

def _array_identity(value):
    a=np.ascontiguousarray(value,dtype=np.complex128)
    return {'dtype':'complex128','shape':list(a.shape),'data_sha256':hashlib.sha256(a.tobytes()).hexdigest()}

def runtime_identity():
    if any(os.environ.get(key)!='1' for key in THREAD_KEYS):
        raise ValueError('set OMP/OPENBLAS/MKL/NUMEXPR thread limits to1 before Python starts')
    files=[paths.HERE/name for name in ('bootstrap_runtime.py','solver_plan.py','cache_consistency.py','qualified_cache.py',
                                       'checkpoint_solver.py','solver_cli.py')]
    files += [paths.TP1/'metric_transport.py',paths.TP1/'reference_transport.py',
              paths.TP2D/'qualified_provider.py',paths.R4F/'parallel_bridge.py',paths.R4C/'execution_admission.py']
    cpu=next((line.split(':',1)[1].strip() for line in Path('/proc/cpuinfo').read_text().splitlines()
              if line.startswith('model name')),'unknown')
    return {'source_files':{str(p.relative_to(paths.REPO)):sha(p) for p in files},
            'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,
            'machine':platform.machine(),'system':platform.system(),'cpu_model':cpu,
            'numerical_threads':{key:os.environ[key] for key in THREAD_KEYS}}

def _step_time(plan,index):
    return plan['t0_hex'] if index==0 else plan['steps'][index-1]['tb_hex']

def _save_checkpoint(out,plan,identity,index,y,norm0,maxdef,previous):
    base=out/'checkpoints'/f'STEP_{index:08d}'
    npz=base.with_suffix('.npz')
    _atomic(npz,lambda stream:np.savez_compressed(stream,y=np.asarray(y,dtype=complex)))
    norm=float(np.vdot(y,y).real)
    record={'schema':'BASS_MIDPOINT_CHECKPOINT_V1','identity_digest':digest(identity),'step':index,
            'time_hex':_step_time(plan,index),'payload_sha256':sha(npz),'previous_checkpoint_sha256':previous,
            'metric_frame_norm':norm,'initial_metric_frame_norm':norm0,'max_generator_defect':maxdef}
    write_new(base.with_suffix('.json'),record)
    return record,sha(base.with_suffix('.json'))

def _load_checkpoints(source,plan,identity):
    source=Path(source).resolve()
    if strict_json(source/'RUN_CONTEXT.json')!=identity:
        old=strict_json(source/'RUN_CONTEXT.json')
        if old.get('initial_input')!=identity['initial_input']:raise ValueError('resume initial-state identity differs')
        raise ValueError('resume plan/cache/source/environment identity differs')
    directory=source/'checkpoints'
    jsons={p.stem for p in directory.glob('STEP_*.json')};arrays={p.stem for p in directory.glob('STEP_*.npz')}
    if jsons!=arrays:raise ValueError('orphan checkpoint file: no automatic deletion or retry')
    if not jsons:raise ValueError('no completed checkpoint')
    wanted={f'STEP_{i:08d}' for i in range(len(jsons))}
    if jsons!=wanted or len(jsons)>plan['nstep']+1:raise ValueError('checkpoint sequence gap or unexpected step')
    previous=None;norms=[];maxdef=0.;records=[];last_y=None
    for index in range(len(jsons)):
        base=directory/f'STEP_{index:08d}';jp=base.with_suffix('.json');npz=base.with_suffix('.npz')
        if jp.is_symlink() or npz.is_symlink():raise ValueError('checkpoint symlink forbidden')
        row=strict_json(jp)
        if (row.get('schema')!='BASS_MIDPOINT_CHECKPOINT_V1' or row.get('step')!=index
            or row.get('identity_digest')!=digest(identity) or row.get('time_hex')!=_step_time(plan,index)
            or row.get('previous_checkpoint_sha256')!=previous or row.get('payload_sha256')!=sha(npz)):
            raise ValueError('checkpoint identity/chain/payload mismatch')
        with np.load(npz,allow_pickle=False) as data:
            if set(data.files)!={'y'}:raise ValueError('unexpected checkpoint payload')
            y=np.array(data['y'])
        if y.shape!=(18,) or y.dtype!=np.dtype('complex128') or not np.isfinite(y).all():
            raise ValueError('checkpoint state shape/type/finiteness mismatch')
        norm=float(np.vdot(y,y).real)
        if row['metric_frame_norm']!=norm or norm<=0:raise ValueError('checkpoint state norm mismatch')
        norms.append(norm)
        if row['initial_metric_frame_norm']!=norms[0]:raise ValueError('checkpoint initial norm mismatch')
        value=row['max_generator_defect']
        if not isinstance(value,(int,float)) or not math.isfinite(value) or value<maxdef:
            raise ValueError('checkpoint generator diagnostic mismatch')
        maxdef=value;previous=sha(jp);last_y=y;records.append(row)
    return source,records,last_y,norms,maxdef,previous

def run_cached(plan,cache_dir,out,c0,*,resume_from=None,stop_after_steps=None):
    """Continue exact midpoint y recurrence using only prequalified cached arrays.

    Resume imports a fully verified checkpoint prefix into a NEW output directory.
    The original run and any orphan/failure evidence are never overwritten.
    Per-step persistence changes I/O only, not time-grid arithmetic or recurrence.
    c0 is explicitly supplied, normalized once exactly as the original candidate,
    and bound by its original canonical complex128 bytes. No old endpoint is
    inferred as an initial state for a different window.
    """
    plan=validate_plan(plan);out=Path(out).resolve()
    if out.exists():raise FileExistsError('fresh create-only output required')
    if out.is_relative_to(paths.REPO):raise ValueError('execution output must be outside source tree')
    c0=np.asarray(c0,dtype=complex)
    if c0.shape!=(18,) or not np.isfinite(c0).all():raise ValueError('explicit finite18-channel initial state required')
    stop=plan['nstep'] if stop_after_steps is None else stop_after_steps
    if type(stop) is not int or not 1<=stop<=plan['nstep']:raise ValueError('stop_after_steps must be1..nstep')
    cache=QualifiedCache(cache_dir,plan)
    identity={'schema':'BASS_MIDPOINT_EXECUTION_CONTEXT_V1','method':METHOD,'plan':plan,
              'cache_manifest_sha256':cache.manifest_sha256,'initial_input':_array_identity(c0),
              'normalization':'ONCE_AT_T0_USING_FROZEN_NORMALIZE_METRIC_STATE; NEVER_PER_STEP',
              'runtime':runtime_identity(),**CEILINGS}
    t0=float.fromhex(plan['t0_hex']);tf=float.fromhex(plan['tf_hex'])
    initial=normalize_metric_state(c0,cache.at(t0).S)
    g0=metric_frame_generator(cache.at(t0));y0=g0.R@initial
    imported=None
    if resume_from is not None:
        imported=_load_checkpoints(resume_from,plan,identity)
        if stop<len(imported[1])-1:raise ValueError('requested stop precedes imported checkpoint')
        with np.load(imported[0]/'checkpoints/STEP_00000000.npz',allow_pickle=False) as data:
            if not np.array_equal(data['y'],y0):raise ValueError('checkpoint0 differs from exact initial-state construction')
    out.mkdir(parents=True,exist_ok=False)
    try:
        write_new(out/'RUN_CONTEXT.json',identity);write_new(out/'CACHE_MANIFEST.json',cache.manifest)
        _atomic(out/'INITIAL_STATE.npz',lambda stream:np.savez_compressed(stream,input_state=c0,normalized_state=initial))
        if imported is None:
            y=y0;norms=[float(np.vdot(y,y).real)];maxdef=g0.antihermitian_defect;completed=0
            _,previous=_save_checkpoint(out,plan,identity,0,y,norms[0],maxdef,None)
        else:
            source,records,y,norms,maxdef,previous=imported;completed=len(records)-1
            for index in range(completed+1):
                for ext in ('.npz','.json'):
                    name=f'STEP_{index:08d}'+ext
                    _copy_new(source/'checkpoints'/name,out/'checkpoints'/name)
            write_new(out/'RESUME_RECEIPT.json',{'source_context_sha256':sha(source/'RUN_CONTEXT.json'),
                       'source_final_checkpoint_sha256':previous,'imported_checkpoint_count':completed+1,
                       'source_run_unchanged':True,'native_queries_repeated':0,
                       'source_failure_sha256':sha(source/'FIRST_FAILURE.json') if (source/'FIRST_FAILURE.json').is_file() else None,
                       'source_result_sha256':sha(source/'RESULT.json') if (source/'RESULT.json').is_file() else None,
                       'source_failure_semantics':'PRESERVED; EXPLICIT_CACHE_STATE_RESUME_DOES_NOT_RECLASSIFY_OLD_FAILURE'})
        for index in range(completed,stop):
            step=plan['steps'][index]
            y,gen=candidate_step(cache,y,float.fromhex(step['ta_hex']),float.fromhex(step['tb_hex']))
            if not np.isfinite(y).all():raise ArithmeticError('nonfinite candidate state')
            maxdef=max(maxdef,gen.antihermitian_defect)
            norm=float(np.vdot(y,y).real);norms.append(norm)
            _,previous=_save_checkpoint(out,plan,identity,index+1,y,norms[0],maxdef,previous)
        drift=float(np.max(np.abs(np.asarray(norms)-norms[0])))
        result={'schema':'BASS_MIDPOINT_EXECUTION_RESULT_V1','method':METHOD,'plan_sha256':plan['plan_sha256'],
                'context_id':plan['context_id'],'completed_steps':stop,'nstep':plan['nstep'],
                'status':'CHECKPOINTED_PARTIAL' if stop<plan['nstep'] else 'CANDIDATE_COMPLETE_REVIEW_REQUIRED',
                'max_norm_drift':drift,'max_generator_defect':float(maxdef),
                'discrete_norm_gate':drift<=plan['qualification_contract']['screens']['candidate_norm_drift_max'],
                'temporal_refinement_gate':'NOT_EVALUATED','independent_reference_gate':'NOT_EVALUATED',
                'state_initialization':'EXPLICIT_CALLER_VECTOR; NORMALIZED_ONCE',
                'new_native_operator_calls':0,'cache_reads':cache.reads,'operator_interpolation_used':False,
                'last_checkpoint_sha256':previous,**CEILINGS}
        if stop==plan['nstep']:
            final=cache.at(tf);rf=metric_frame_generator(final).R
            cf=solve_triangular(rf,y,lower=False,check_finite=False)
            J=np.eye(18,dtype=complex)[:,plan['selected_indices']]
            rhs=J.conj().T@final.S@cf;gram=J.conj().T@final.S@J
            selected=np.vdot(rhs,solve(gram,rhs,assume_a='pos',check_finite=False))
            norm_final=np.vdot(cf,final.S@cf)
            if not np.isfinite(cf).all() or abs(selected.imag)>1e-10*max(1.,abs(selected.real)):
                raise ArithmeticError('final state/selected-span quadratic form unresolved')
            result.update(final_metric_norm=float(norm_final.real),selected_span_population=float(selected.real),
                          selected_indices=plan['selected_indices'],observable_scope='FINITE_SELECTED_SPAN_DIAGNOSTIC_NOT_CAPTURE',
                          cache_reads=cache.reads)
            _atomic(out/'CANDIDATE_RESULT.npz',lambda stream:np.savez_compressed(stream,
                    initial_state=initial,final_state=cf,norm_history=np.asarray(norms,float)))
            result['state_payload_sha256']=sha(out/'CANDIDATE_RESULT.npz')
        write_new(out/'RESULT.json',result)
        return result
    except BaseException as exc:
        if not (out/'FIRST_FAILURE.json').exists():
            write_new(out/'FIRST_FAILURE.json',{'type':type(exc).__name__,'message':str(exc),
                      'traceback':traceback.format_exc(),'new_native_operator_calls':0,**CEILINGS})
        raise
