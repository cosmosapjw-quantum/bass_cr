"""Durable task identity, checkpoint, and geometry qualification math for TP2A."""
from __future__ import annotations
from pathlib import Path
import hashlib,json,os,tempfile
import numpy as np

CROSS_KEYS=('S_tp','S_pt','H_tp','H_pt','D_tp','D_pt')
FULL_KEYS=('S','H','D')

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def _digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def task_identity(method,z_center,dz,context,reference_order=None):
    if method not in ('phase24','reference'):raise ValueError('unknown fixed method')
    vals=np.asarray([z_center,dz],float)
    if not np.isfinite(vals).all():raise ValueError('finite geometry required')
    if method=='reference':
        if isinstance(reference_order,bool) or not isinstance(reference_order,int):raise ValueError('reference order required')
    elif reference_order is not None:raise ValueError('phase24 has no reference order')
    return _digest({'method':method,'reference_order':reference_order,'z_center_hex':float(z_center).hex(),
                    'dz_hex':float(dz).hex(),'context':context})[:32]

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

def _write_json(path,value):
    data=(json.dumps(value,indent=2,allow_nan=False)+'\n').encode()
    _atomic_file(path,lambda f:f.write(data))

def _flatten(payload):
    arrays={k:np.asarray(payload['full'][k],complex) for k in FULL_KEYS}
    arrays.update({k:np.asarray(payload['cross'][k],complex) for k in CROSS_KEYS})
    return arrays

def save_task(directory,result,payload):
    directory=Path(directory);tid=result['task_id'];base=directory/'tasks'/tid
    arrays=_flatten(payload)
    if not all(np.isfinite(a).all() for a in arrays.values()):raise ValueError('nonfinite task arrays')
    npz=base.with_suffix('.npz')
    _atomic_file(npz,lambda f:np.savez_compressed(f,**arrays))
    receipt=dict(result)
    receipt['matrix_sha256']=sha(npz)
    receipt['array_shapes']={k:list(v.shape) for k,v in arrays.items()}
    _write_json(base.with_suffix('.json'),receipt)
    return receipt

def load_task(directory,task_id,context_id):
    directory=Path(directory);base=directory/'tasks'/task_id
    receipt=json.loads(base.with_suffix('.json').read_text())
    if receipt.get('task_id')!=task_id or receipt.get('context_id')!=context_id:
        raise ValueError('task context identity mismatch')
    npz=base.with_suffix('.npz')
    if sha(npz)!=receipt.get('matrix_sha256'):raise ValueError('task matrix hash mismatch')
    with np.load(npz,allow_pickle=False) as f:
        expected=set(FULL_KEYS+CROSS_KEYS)
        if set(f.files)!=expected:raise ValueError('task matrix keys mismatch')
        arrays={k:np.array(f[k]) for k in f.files}
    if not all(np.isfinite(a).all() for a in arrays.values()):raise ValueError('nonfinite cached task')
    return receipt,arrays

def _relative(a,b):
    d=float(np.linalg.norm(a-b));n=float(np.linalg.norm(b))
    return d/n if n else (0. if d==0 else float('inf'))

def _row_arrays(row):
    if 'full' in row:return row['full'],row['cross']
    full={k:row['arrays'][k] for k in FULL_KEYS}
    cross={k:row['arrays'][k] for k in CROSS_KEYS}
    return full,cross

def qualify_geometry_from_tasks(z_center,rows,epsilon_t,contract):
    if not np.isfinite(z_center) or not np.isfinite(epsilon_t) or epsilon_t<=0:raise ValueError('finite geometry and positive epsilon_t required')
    by={}
    for method in ('phase24','reference32'):
        subset=sorted([r for r in rows if r['method']==method],key=lambda r:r['dz_a0'])
        if len(subset)!=3 or [r['dz_a0'] for r in subset][1]!=0.:raise ValueError('three-point stencil required for '+method)
        by[method]=subset
    residuals={}
    for method,subset in by.items():
        minus,center,plus=subset
        fm,_=_row_arrays(minus);fc,_=_row_arrays(center);fp,_=_row_arrays(plus)
        fd=(fp['S']-fm['S'])/(2*epsilon_t);direct=fc['D']+fc['D'].conj().T
        den=max(float(np.linalg.norm(fd)),float(np.linalg.norm(direct)),1e-300)
        residuals[method]=float(np.linalg.norm(fd-direct)/den)
    parity={};maxpar=0.
    for rp,rr in zip(by['phase24'],by['reference32']):
        _,cp=_row_arrays(rp);_,cr=_row_arrays(rr);key=f"dz={rp['dz_a0']:+.8f}";parity[key]={}
        for k in CROSS_KEYS:
            x=_relative(cp[k],cr[k]);parity[key][k]=x;maxpar=max(maxpar,x)
    screens=contract['screens'];fail=[]
    for method in ('phase24','reference32'):
        if residuals[method]>screens['connection_relative_max']:fail.append(method+' connection')
        center=by[method][1];diag=center['diagnostics']
        if max(diag['S_hermiticity_relative'],diag['H_hermiticity_relative'])>screens['operator_hermiticity_relative_max']:
            fail.append(method+' Hermiticity')
        if diag['metric_ratio']<screens['metric_min_ratio']:fail.append(method+' metric ratio')
    if maxpar>screens['raw_cross_relative_max']:fail.append('phase24/reference32 raw cross parity')
    return {'z_a0':float(z_center),'connection_residuals':residuals,
            'max_raw_cross_relative_difference':maxpar,'raw_cross_relative_differences':parity,
            'failed_screens':fail,'capture_execution_allowed':False}



def _connection_receipt(subset,epsilon_t,screens):
    subset=sorted(subset,key=lambda r:r['dz_a0'])
    if len(subset)!=3 or [r['dz_a0'] for r in subset][1]!=0.:
        raise ValueError('three-point stencil required')
    minus,center,plus=subset
    fm,_=_row_arrays(minus);fc,_=_row_arrays(center);fp,_=_row_arrays(plus)
    fd=(fp['S']-fm['S'])/(2*epsilon_t);direct=fc['D']+fc['D'].conj().T
    den=max(float(np.linalg.norm(fd)),float(np.linalg.norm(direct)),1e-300)
    residual=float(np.linalg.norm(fd-direct)/den)
    diag=center['diagnostics']
    herm=max(diag['S_hermiticity_relative'],diag['H_hermiticity_relative'])
    return {'connection_relative':residual,
            'connection_pass':residual<=screens['connection_relative_max'],
            'hermiticity_relative_max':herm,
            'hermiticity_pass':herm<=screens['operator_hermiticity_relative_max'],
            'metric_ratio':diag['metric_ratio'],
            'metric_pass':diag['metric_ratio']>=screens['metric_min_ratio']}


def _stencil_cross_relative_max(a,b):
    aa=sorted(a,key=lambda r:r['dz_a0']);bb=sorted(b,key=lambda r:r['dz_a0'])
    if len(aa)!=3 or len(bb)!=3:raise ValueError('three-point stencils required')
    value=0.;detail={}
    for ra,rb in zip(aa,bb):
        if ra['dz_a0']!=rb['dz_a0']:raise ValueError('stencil mismatch')
        _,ca=_row_arrays(ra);_,cb=_row_arrays(rb);key=f"dz={ra['dz_a0']:+.8f}";detail[key]={}
        for name in CROSS_KEYS:
            x=_relative(ca[name],cb[name]);detail[key][name]=x;value=max(value,x)
    return value,detail


def qualify_reference_ladder(rows,epsilon_t,contract):
    """Qualify a finite reference ladder before candidate comparison.

    The higher order is accepted only when it and the immediately preceding
    order both pass their own operator/connection screens and their raw cross
    stencils agree under the frozen raw-cross threshold.
    """
    if not np.isfinite(epsilon_t) or epsilon_t<=0:raise ValueError('positive finite epsilon_t required')
    screens=contract['screens'];orders=list(contract['reference_orders'])
    if len(orders)<2 or any(isinstance(q,bool) or not isinstance(q,int) for q in orders):
        raise ValueError('finite integer reference ladder with at least two orders required')
    if orders!=sorted(set(orders)):raise ValueError('strictly increasing unique reference ladder required')
    receipts={};attempted=[];previous=None;qualified=None
    for order in orders:
        subset=[r for r in rows if r.get('method')=='reference' and r.get('reference_order')==order]
        if len(subset)!=3:break
        attempted.append(order);rec=_connection_receipt(subset,epsilon_t,screens)
        rec['reference_order']=order;rec['previous_raw_cross_relative_max']=None;rec['previous_raw_cross_relative_differences']=None
        if previous is not None:
            diff,detail=_stencil_cross_relative_max(previous['rows'],subset)
            rec['previous_raw_cross_relative_max']=diff;rec['previous_raw_cross_relative_differences']=detail
            rec['raw_cross_convergence_pass']=diff<=screens['raw_cross_relative_max']
            if (previous['receipt']['connection_pass'] and previous['receipt']['hermiticity_pass'] and previous['receipt']['metric_pass']
                    and rec['connection_pass'] and rec['hermiticity_pass'] and rec['metric_pass']
                    and rec['raw_cross_convergence_pass']):
                qualified=order;receipts[str(order)]=rec;break
        else:rec['raw_cross_convergence_pass']=None
        receipts[str(order)]=rec;previous={'rows':subset,'receipt':rec}
    status='REFERENCE_QUALIFIED' if qualified is not None else 'REFERENCE_CONVERGENCE_UNRESOLVED'
    return {'status':status,'qualified_order':qualified,'attempted_orders':attempted,'orders':receipts,
            'candidate_evaluated':False}


def qualify_candidate_against_reference(z_center,candidate_rows,reference_rows,epsilon_t,contract,qualified_order):
    screens=contract['screens']
    candidate=_connection_receipt(candidate_rows,epsilon_t,screens)
    reference=_connection_receipt(reference_rows,epsilon_t,screens)
    diff,detail=_stencil_cross_relative_max(candidate_rows,reference_rows)
    failures=[]
    if not candidate['connection_pass']:failures.append('phase24 connection')
    if not candidate['hermiticity_pass']:failures.append('phase24 Hermiticity')
    if not candidate['metric_pass']:failures.append('phase24 metric ratio')
    # A qualified reference is an input contract here; if it no longer passes,
    # refuse to reinterpret the candidate comparison.
    if not (reference['connection_pass'] and reference['hermiticity_pass'] and reference['metric_pass']):
        raise ValueError('qualified reference failed its own operator screens')
    if diff>screens['raw_cross_relative_max']:failures.append('phase24/qualified-reference raw cross parity')
    return {'status':('GEOMETRY_QUALIFIED' if not failures else 'NUMERICAL_SCREEN_FAILED'),
            'z_a0':float(z_center),'qualified_reference_order':int(qualified_order),
            'candidate':candidate,'reference':reference,
            'candidate_vs_reference':{'max_raw_cross_relative_difference':diff,
                                      'raw_cross_relative_differences':detail},
            'failed_screens':failures,'capture_execution_allowed':False}

def restore_tasks(source,destination,context_id,allowed_ids):
    source,destination=Path(source),Path(destination);allowed=set(allowed_ids);count=0
    tasks=source/'tasks'
    if not tasks.exists():return 0
    for receipt_path in sorted(tasks.glob('*.json')):
        tid=receipt_path.stem
        if tid not in allowed:continue
        receipt,_=load_task(source,tid,context_id)
        for suffix in ('.npz','.json'):
            old=(source/'tasks'/tid).with_suffix(suffix);new=(destination/'tasks'/tid).with_suffix(suffix)
            _atomic_file(new,lambda f,old=old:f.write(old.read_bytes()))
        count+=1
    return count

_STATE={}

def worker_init(config,bank,native_dir,context_id,out):
    from bass_foundations.two_center import Trajectory,symmetric_channels
    from native_ring import NativeRing
    channels=symmetric_channels(bank)
    v=float(config['speed'])
    trajectory=Trajectory(((0.,0.,0.),(config['b_a0'],0.,0.)),((0.,0.,0.),(0.,0.,v)))
    _STATE.clear();_STATE.update(config=config,bank=bank,channels=channels,trajectory=trajectory,
        evaluator=NativeRing(native_dir),context_id=context_id,out=Path(out))

def worker_task(spec):
    import os,time
    from full_operator import _bind_cross,assemble_full
    from fast_cross import fast_cross as reference_cross
    from fast_cross_phase import fast_cross as phase_cross
    s=_STATE;cfg=s['config'];z=float(spec['z_center_a0']);dz=float(spec['dz_a0']);method=spec['method'];tid=spec['task_id'];reference_order=spec.get('reference_order')
    try:
        receipt,arrays=load_task(s['out'],tid,s['context_id'])
        return {'task_id':tid,'reused':True,'wall_seconds':0.,'pid':os.getpid(),'receipt':receipt}
    except FileNotFoundError:
        pass
    t=(z+dz)/cfg['speed'];tic=time.perf_counter()
    if method=='phase24':
        raw=phase_cross(s['trajectory'],s['channels'],s['bank'][0].edges,t,order=cfg['phase_order'],
            evaluator=s['evaluator'],phase_budget=cfg['phase_budget_rad'])
    elif method=='reference':
        if reference_order not in cfg['reference_orders']:raise ValueError('reference order outside frozen ladder')
        raw=reference_cross(s['trajectory'],s['channels'],s['bank'][0].edges,t,order=reference_order,evaluator=s['evaluator'])
    else:raise ValueError('unknown fixed method')
    snap=_bind_cross(s['trajectory'],s['channels'],t,raw,raw['metadata'])
    full=assemble_full(s['trajectory'],s['channels'],t,same_order=cfg['same_center_order'],cross=snap)
    payload={'full':{k:np.asarray(full[k]) for k in FULL_KEYS},'cross':{k:np.asarray(raw[k]) for k in CROSS_KEYS},'diagnostics':full['diagnostics']}
    result={'schema':'BASS_TP2A_FULL_GEOMETRY_TASK_V1','task_id':tid,'context_id':s['context_id'],'method':method,
        'z_center_a0':z,'dz_a0':dz,'reference_order':reference_order,'time_ta':t,'channel_count':len(s['channels']),
        'diagnostics':full['diagnostics'],'metadata':raw['metadata'],'wall_seconds':time.perf_counter()-tic,'pid':os.getpid(),
        'capture_execution_allowed':False}
    receipt=save_task(s['out'],result,payload)
    return {'task_id':tid,'reused':False,'wall_seconds':result['wall_seconds'],'pid':os.getpid(),'receipt':receipt}

def task_row(directory,task_id,context_id):
    receipt,arrays=load_task(directory,task_id,context_id)
    return {'method':receipt['method'],'reference_order':receipt.get('reference_order'),'z_center_a0':receipt['z_center_a0'],'dz_a0':receipt['dz_a0'],
        'diagnostics':receipt['diagnostics'],'metadata':receipt['metadata'],
        'full':{k:arrays[k] for k in FULL_KEYS},'cross':{k:arrays[k] for k in CROSS_KEYS}}
