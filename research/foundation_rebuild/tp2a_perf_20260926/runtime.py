"""Deterministic per-geometry jobs and identity-bound atomic node checkpoints."""
from __future__ import annotations
from pathlib import Path
import hashlib,json,os,shutil,tempfile,time
import numpy as np
import paths
from bass_foundations.radial_basis import FEMRadial,readonly
from bass_foundations.two_center import Trajectory,symmetric_channels
from full_operator import assemble_full,_bind_cross
from fast_cross import fast_cross

KEYS=('S','H','D')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def atomic_file(path,writer):
    """Atomic create-only install; a partial file is never a valid checkpoint."""
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix='.partial_',dir=path.parent)
    try:
        with os.fdopen(fd,'wb') as f:
            writer(f);f.flush();os.fsync(f.fileno())
        os.link(tmp,path)  # fails on existing output; never overwrite
        dfd=os.open(path.parent,os.O_RDONLY)
        try:os.fsync(dfd)
        finally:os.close(dfd)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)

def write_json(path,value):
    data=(json.dumps(value,indent=2,allow_nan=False)+'\n').encode()
    atomic_file(path,lambda f:f.write(data))

def save_bank(directory,bank):
    directory=Path(directory)
    matrix=directory/'BASIS.npz'
    arrays={'edges':bank[0].edges,'coefficients':np.array([m.polynomial_coefficients for m in bank])}
    atomic_file(matrix,lambda f:np.savez_compressed(f,**arrays))
    modes=[{k:getattr(m,k) for k in ('l','principal_n','energy','identity','residual')} for m in bank]
    record={'schema':'BASS_TP2A_BASIS_V1','matrix_sha256':sha(matrix),'modes':modes}
    record['identity']=digest(record)
    write_json(directory/'BASIS.json',record)
    return record

def load_bank(directory):
    directory=Path(directory);rec=json.loads((directory/'BASIS.json').read_text())
    original={k:v for k,v in rec.items() if k!='identity'}
    if rec.get('identity')!=digest(original) or sha(directory/'BASIS.npz')!=rec['matrix_sha256']:
        raise ValueError('basis payload identity mismatch')
    with np.load(directory/'BASIS.npz',allow_pickle=False) as f:
        edges=f['edges'];co=f['coefficients']
        if len(co)!=len(rec['modes']):raise ValueError('basis count mismatch')
        bank=tuple(FEMRadial(m['l'],m['principal_n'],m['energy'],readonly(edges),readonly(c),m['identity'],m['residual']) for m,c in zip(rec['modes'],co))
    return bank,rec

def fast_full(trajectory,channels,t,order=24,same_order=20,evaluator=None,progress=None):
    x=fast_cross(trajectory,channels,channels[0].radial.edges,t,order=order,evaluator=evaluator,progress=progress)
    snap=_bind_cross(trajectory,channels,t,x,x['metadata'])
    return assemble_full(trajectory,channels,t,same_order=same_order,cross=snap)

def node_key(t):return hashlib.sha256(float(t).hex().encode()).hexdigest()[:24]

def load_node(directory,t,context_id):
    p=Path(directory)/'nodes'/node_key(t)
    rec=json.loads(p.with_suffix('.json').read_text())
    if rec['context_id']!=context_id or rec['time_hex']!=float(t).hex() or rec['matrix_sha256']!=sha(p.with_suffix('.npz')):
        raise ValueError('cached node identity mismatch')
    with np.load(p.with_suffix('.npz'),allow_pickle=False) as f:m={k:np.array(f[k]) for k in KEYS}
    n=rec['channel_count']
    if any(a.shape!=(n,n) or not np.isfinite(a).all() for a in m.values()):raise ValueError('cached node shape/finiteness')
    return m,rec

def restore_nodes(source,dest,context_id):
    """Explicit salvage into a NEW run. No prior evidence is overwritten."""
    source,dest=Path(source),Path(dest);count=0
    for p in sorted((source/'nodes').glob('*.json')):
        rec=json.loads(p.read_text());t=float.fromhex(rec['time_hex'])
        _,verified=load_node(source,t,context_id)
        for suffix in ('.npz','.json'):
            old=p.with_suffix(suffix);new=dest/'nodes'/old.name
            atomic_file(new,lambda f,old=old:f.write(old.read_bytes()))
        count+=1
    return count

_STATE={}
def worker_init(config,bank,context_id,out,events,cancel,native_dir):
    channels=symmetric_channels(bank)
    for c in channels:
        c.radial.edges.setflags(write=False);c.radial.polynomial_coefficients.setflags(write=False)
    v=config['speed'];tr=Trajectory(((0.,0.,0.),(config['b_a0'],0.,0.)),((0.,0.,0.),(0.,0.,v)))
    evaluator=None
    if native_dir:
        from native_ring import NativeRing
        evaluator=NativeRing(native_dir)
    _STATE.update(config=config,channels=channels,tr=tr,id=context_id,out=Path(out),events=events,cancel=cancel,evaluator=evaluator)

def worker_geometry(z):
    s=_STATE;cfg=s['config'];t=float(z/cfg['speed']);eps=cfg['epsilon_z_a0']/cfg['speed'];out=s['out'];started=time.monotonic();evaluation_count=0
    def emit(event,**kw):
        if s['events'] is not None:s['events'].put({'event':event,'pid':os.getpid(),'z_a0':z,**kw})
    def progress(data):
        if s['cancel'] is not None and s['cancel'].is_set():raise InterruptedError('peer cancelled scan')
        emit('kernel_progress',**data)
    def at(time_t):
        nonlocal evaluation_count
        key=node_key(time_t);p=out/'nodes'/key
        if p.with_suffix('.json').exists():
            mats,rec=load_node(out,time_t,s['id']);emit('node_reused',time_hex=float(time_t).hex());return mats,rec
        if s['cancel'] is not None and s['cancel'].is_set():raise InterruptedError('peer cancelled scan')
        tic=time.monotonic();x=fast_full(s['tr'],s['channels'],time_t,order=cfg['cross_order'],same_order=cfg['same_center_order'],evaluator=s['evaluator'],progress=progress)
        mats={k:x[k] for k in KEYS};npz=p.with_suffix('.npz')
        atomic_file(npz,lambda f:np.savez_compressed(f,**mats))
        rec={'schema':'BASS_TP2A_NODE_V1','context_id':s['id'],'time_hex':float(time_t).hex(),'channel_count':len(s['channels']),
             'matrix_sha256':sha(npz),'diagnostics':x['diagnostics'],'metadata':x['metadata'],
             'wall_seconds':time.monotonic()-tic,'pid':os.getpid()}
        write_json(p.with_suffix('.json'),rec);evaluation_count+=1;emit('node_complete',time_hex=rec['time_hex'],wall_seconds=rec['wall_seconds'])
        return mats,rec
    emit('geometry_start')
    center,rec=at(t);minus,_=at(t-eps);plus,_=at(t+eps)
    fd=(plus['S']-minus['S'])/(2*eps);direct=center['D']+center['D'].conj().T
    den=max(float(np.linalg.norm(fd)),float(np.linalg.norm(direct)),1e-300)
    residual=float(np.linalg.norm(fd-direct)/den)
    failures=[]
    if not np.isfinite(residual) or residual>cfg['screens']['metric_derivative_relative_max']:failures.append('metric connection')
    diag=rec['diagnostics']
    if diag['metric_ratio']<cfg['screens']['metric_min_ratio']:failures.append('metric ratio')
    if max(diag['S_hermiticity_relative'],diag['H_hermiticity_relative'])>cfg['screens']['operator_hermiticity_relative_max']:failures.append('Hermiticity')
    result={'z_a0':z,'t_ta':t,'channel_count':len(s['channels']),'metric_connection_relative':residual,
            'epsilon_t':eps,'diagnostics':diag,'failed_screens':failures,'new_operator_evaluations':evaluation_count,
            'wall_seconds':time.monotonic()-started,'pid':os.getpid(),'capture_execution_allowed':False}
    write_json(out/'geometry'/f'{node_key(t)}.json',result)
    emit('geometry_complete',metric_connection_relative=residual,failed_screens=failures,wall_seconds=result['wall_seconds'])
    return result
