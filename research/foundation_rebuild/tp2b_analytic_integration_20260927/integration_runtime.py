"""Canonical analytic numerical tasks for TP2B integration.

Role labels (reference/candidate) are intentionally excluded from numerical task
identity. Identity binds the effective integration mesh, quadrature order, exact
time, sector, frozen basis/physics, and analytic engine identity.
"""
from __future__ import annotations
from pathlib import Path
import json,os,tempfile
import numpy as np
import qualification_runtime as qr
from exact_cross import frame,resolution_edges,cross,MomentKernel
from task_plan import numerical_key

FULL_KEYS=qr.FULL_KEYS
CROSS_KEYS=qr.CROSS_KEYS


def role_request(family,z_center,dz,order,subdivisions,trajectory,edges,physics_identity,*,phase_budget,sector='full'):
    if family not in ('reference','candidate'): raise ValueError('family must be reference or candidate')
    if type(order) is not int or not 2<=order<=64: raise ValueError('bounded quadrature order required')
    if type(subdivisions) is not int or subdivisions not in (1,2,4): raise ValueError('bounded subdivisions required')
    if sector not in ('full','even'): raise ValueError('sector must be full or even')
    rel=np.asarray(trajectory.velocities[1]-trajectory.velocities[0],float)
    speed=float(np.linalg.norm(rel))
    if not np.isfinite(speed) or speed<=0: raise ValueError('positive relative speed required')
    t=(float(z_center)+float(dz))/speed
    _,R,axes,dv=frame(trajectory,t)
    kp=float(dv@axes[0])
    budget=None if family=='reference' else phase_budget
    eff=resolution_edges(np.asarray(edges,float),R,kp,subdivisions,budget)
    request={'order':order,'integration_edges':eff,'time_hex':float(t).hex(),'sector':sector}
    tid=numerical_key(request,physics_identity)
    method='reference' if family=='reference' else ('phase24' if order==24 else 'candidate')
    return {'family':family,'method':method,'reference_order':order if family=='reference' else None,
            'candidate_order':order if family=='candidate' and order!=24 else None,
            'order':order,'integration_subdivisions':subdivisions,'phase_budget':budget,
            'z_center_a0':float(z_center),'dz_a0':float(dz),'time_ta':t,'sector':sector,
            'effective_edge_sha256':__import__('hashlib').sha256(np.asarray(eff,dtype='<f8').tobytes()).hexdigest(),
            'numerical_task_id':tid}


def _atomic_file(path,writer):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix='.partial_',dir=path.parent)
    try:
        with os.fdopen(fd,'wb') as f:
            writer(f);f.flush();os.fsync(f.fileno())
        os.link(tmp,path)
        dfd=os.open(path.parent,os.O_RDONLY)
        try:os.fsync(dfd)
        finally:os.close(dfd)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)


def save_numeric_task(directory,result,payload):
    base=Path(directory)/'tasks'/result['numerical_task_id']
    arrays={k:np.asarray(payload['full'][k],complex) for k in FULL_KEYS}
    arrays.update({k:np.asarray(payload['cross'][k],complex) for k in CROSS_KEYS})
    if not all(np.isfinite(a).all() for a in arrays.values()):raise ValueError('nonfinite task arrays')
    npz=base.with_suffix('.npz');_atomic_file(npz,lambda f:np.savez_compressed(f,**arrays))
    receipt=dict(result);receipt['matrix_sha256']=qr.sha(npz);receipt['array_shapes']={k:list(v.shape) for k,v in arrays.items()}
    data=(json.dumps(receipt,indent=2,allow_nan=False)+'\n').encode();_atomic_file(base.with_suffix('.json'),lambda f:f.write(data))
    return receipt


def load_numeric_task(directory,numerical_task_id,context_id):
    base=Path(directory)/'tasks'/numerical_task_id
    receipt=json.loads(base.with_suffix('.json').read_text())
    if receipt.get('numerical_task_id')!=numerical_task_id or receipt.get('context_id')!=context_id:raise ValueError('numerical task context mismatch')
    npz=base.with_suffix('.npz')
    if qr.sha(npz)!=receipt.get('matrix_sha256'):raise ValueError('numerical task matrix hash mismatch')
    with np.load(npz,allow_pickle=False) as f:
        expected=set(FULL_KEYS+CROSS_KEYS)
        if set(f.files)!=expected:raise ValueError('numerical task keys mismatch')
        arrays={k:np.array(f[k]) for k in f.files}
    return receipt,arrays


def role_row(role,receipt,arrays,*,aliased=False):
    return {'method':role['method'],'family':role['family'],'reference_order':role.get('reference_order'),
            'candidate_order':role.get('candidate_order'),'integration_subdivisions':role['integration_subdivisions'],
            'z_center_a0':role['z_center_a0'],'dz_a0':role['dz_a0'],'numerical_task_id':role['numerical_task_id'],
            'alias_reuse':bool(aliased),'evidence_relation':('ALIASED_SAME_NUMERICAL_TASK_NOT_INDEPENDENT_CROSSCHECK' if aliased else 'DIRECT_NUMERICAL_TASK'),
            'diagnostics':receipt['diagnostics'],'metadata':receipt['metadata'],
            'full':{k:arrays[k] for k in FULL_KEYS},'cross':{k:arrays[k] for k in CROSS_KEYS}}

_STATE={}

def worker_init(config,bank,analytic_dir,context_id,out):
    from bass_foundations.two_center import Trajectory,symmetric_channels
    channels=symmetric_channels(bank);v=float(config['speed'])
    tr=Trajectory(((0.,0.,0.),(config['b_a0'],0.,0.)),((0.,0.,0.),(0.,0.,v)))
    _STATE.clear();_STATE.update(config=config,bank=bank,channels=channels,trajectory=tr,kernel=MomentKernel(analytic_dir),context_id=context_id,out=Path(out))


def worker_task(spec):
    import os,time
    from assemble import assemble
    s=_STATE;tid=spec['numerical_task_id']
    try:
        receipt,_=load_numeric_task(s['out'],tid,s['context_id'])
        return {'numerical_task_id':tid,'reused':True,'wall_seconds':0.,'pid':os.getpid(),'receipt':receipt}
    except FileNotFoundError: pass
    tic=time.perf_counter()
    raw,full=assemble(s['trajectory'],s['channels'],spec['time_ta'],s['kernel'],order=spec['order'],
        subdivisions=spec['integration_subdivisions'],phase_budget=spec['phase_budget'],sector='full')
    result={'schema':'BASS_TP2B_ANALYTIC_NUMERICAL_TASK_V1','numerical_task_id':tid,'context_id':s['context_id'],
            'order':spec['order'],'integration_subdivisions':spec['integration_subdivisions'],'phase_budget':spec['phase_budget'],
            'time_ta':spec['time_ta'],'sector':'full','diagnostics':full['diagnostics'],'metadata':raw['metadata'],
            'wall_seconds':time.perf_counter()-tic,'pid':os.getpid(),'capture_execution_allowed':False}
    payload={'full':{k:np.asarray(full[k]) for k in FULL_KEYS},'cross':{k:np.asarray(raw[k]) for k in CROSS_KEYS}}
    receipt=save_numeric_task(s['out'],result,payload)
    return {'numerical_task_id':tid,'reused':False,'wall_seconds':result['wall_seconds'],'pid':os.getpid(),'receipt':receipt}


def restore_numeric_tasks(source,destination,context_id,allowed_ids):
    source,destination=Path(source),Path(destination);allowed=set(allowed_ids);count=0
    if not (source/'tasks').exists():return 0
    for p in sorted((source/'tasks').glob('*.json')):
        tid=p.stem
        if tid not in allowed:continue
        load_numeric_task(source,tid,context_id)
        for suffix in ('.json','.npz'):
            old=(source/'tasks'/tid).with_suffix(suffix);new=(destination/'tasks'/tid).with_suffix(suffix)
            _atomic_file(new,lambda f,old=old:f.write(old.read_bytes()))
        count+=1
    return count
