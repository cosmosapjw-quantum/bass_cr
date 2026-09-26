#!/usr/bin/env python3
"""Fixed z=-6 derivative-aware qualification. No capture or full scan."""
from __future__ import annotations
import os
for _k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[_k]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
import argparse,concurrent.futures as cf,hashlib,json,multiprocessing as mp,subprocess,sys,time,traceback,zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
FND=HERE.parent
REPO=HERE.parents[2]
PERF=FND/'tp2a_perf_20260926'
for p in (HERE,PERF,FND/'src',FND/'full_operator_20260926',FND/'reaudit_20260925/repair',REPO):
    if str(p) not in sys.path:sys.path.insert(0,str(p))


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write_new(path,value):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x') as f:json.dump(value,f,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())

def _worker(task):
    method,dz,contract,bank,native_dir=task
    import numpy as np
    from bass_foundations.two_center import Trajectory,symmetric_channels
    from cr_repro.observables import projectile_speed_au
    from full_operator import _bind_cross,assemble_full
    from native_ring import NativeRing
    from fast_cross import fast_cross as fast_reference
    from fast_cross_phase import fast_cross as fast_phase
    ch=symmetric_channels(bank);v=projectile_speed_au(contract['energy_keV_per_u'])
    tr=Trajectory(((0.,0.,0.),(contract['b_a0'],0.,0.)),((0.,0.,0.),(0.,0.,v)))
    t=(contract['z_a0']+dz)/v;evaluator=NativeRing(native_dir);tic=time.perf_counter()
    if method=='phase24':
        raw=fast_phase(tr,ch,bank[0].edges,t,order=contract['phase_order'],evaluator=evaluator,phase_budget=contract['phase_budget_rad'])
    elif method=='reference32':
        raw=fast_reference(tr,ch,bank[0].edges,t,order=contract['reference_order'],evaluator=evaluator)
    else:raise ValueError('unknown fixed method')
    snap=_bind_cross(tr,ch,t,raw,raw['metadata']);full=assemble_full(tr,ch,t,same_order=contract['same_center_order'],cross=snap)
    return {'method':method,'dz':dz,'t':t,'wall_seconds':time.perf_counter()-tic,
            'full':{k:full[k] for k in ('S','H','D')},
            'cross':{k:raw[k] for k in ('S_tp','S_pt','H_tp','H_pt','D_tp','D_pt')},
            'metadata':raw['metadata'],'diagnostics':full['diagnostics']}

def residual(rows,eps_t):
    import numpy as np
    minus,center,plus=rows
    fd=(plus['full']['S']-minus['full']['S'])/(2*eps_t)
    direct=center['full']['D']+center['full']['D'].conj().T
    den=max(float(np.linalg.norm(fd)),float(np.linalg.norm(direct)),1e-300)
    return float(np.linalg.norm(fd-direct)/den)

def rel(a,b):
    import numpy as np
    n=float(np.linalg.norm(b));d=float(np.linalg.norm(a-b))
    return d/n if n else (0. if d==0 else float('inf'))

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',required=True);p.add_argument('--native-build',required=True);p.add_argument('--workers',type=int,default=6);p.add_argument('--expected-commit')
    a=p.parse_args(argv);out=Path(a.out).resolve();archive=out.with_name(out.name+'_RETURN.zip')
    if out.exists() or archive.exists():p.error('create-only output exists')
    if a.workers<1 or a.workers>12:p.error('workers must be 1..12')
    out.mkdir(parents=True);report={'schema':'BASS_TP2A_ZMINUS6_QUALIFICATION_RETURN_V1','status':'IN_PROGRESS',
        'capture_execution_allowed':False,'production_admission':'HOLD','all_bound':'OPEN','b_grid':'NO_GO','original_capture_gap_resolved':False}
    rc=0;phase='preflight'
    try:
        contract=json.loads((HERE/'CONTRACT.json').read_text())
        head=subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True,stderr=subprocess.DEVNULL).strip() if (REPO/'.git').exists() else None
        report['execution_head']=head
        if a.expected_commit and head!=a.expected_commit:raise ValueError('execution commit mismatch')
        from bass_foundations.radial_basis import RadialSpec,atomic_bank
        from native_ring import NativeRing
        native=NativeRing(Path(a.native_build).resolve()).receipt
        bank=atomic_bank(RadialSpec(**contract['radial_spec']))
        report['basis_identities']=[m.identity for m in bank];report['native_build']=native
        eps=contract['epsilon_z_a0'];tasks=[(m,d,contract,bank,str(Path(a.native_build).resolve())) for m in ('phase24','reference32') for d in (-eps,0.,eps)]
        phase='qualification';print(json.dumps({'event':'qualification_start','tasks':[[x[0],x[1]] for x in tasks]}),flush=True)
        with cf.ProcessPoolExecutor(max_workers=min(a.workers,len(tasks)),mp_context=mp.get_context('spawn')) as pool:
            rows=list(pool.map(_worker,tasks))
        import numpy as np
        by={m:sorted([r for r in rows if r['method']==m],key=lambda r:r['dz']) for m in ('phase24','reference32')}
        v=__import__('cr_repro.observables',fromlist=['projectile_speed_au']).projectile_speed_au(contract['energy_keV_per_u']);eps_t=eps/v
        residuals={m:residual(by[m],eps_t) for m in by}
        parity={};maxpar=0.
        for rp,rr in zip(by['phase24'],by['reference32']):
            key=f"dz={rp['dz']:+.8f}";parity[key]={}
            for k in rp['cross']:
                x=rel(rp['cross'][k],rr['cross'][k]);parity[key][k]=x;maxpar=max(maxpar,x)
        for r in rows:
            tag=f"{r['method']}_dz{r['dz']:+.8f}"
            with (out/(tag+'.npz')).open('xb') as f:np.savez_compressed(f,**r['full'],**r['cross'])
            write_new(out/(tag+'.json'),{'method':r['method'],'dz':r['dz'],'t':r['t'],'wall_seconds':r['wall_seconds'],'metadata':r['metadata'],'diagnostics':r['diagnostics'],'matrix_sha256':sha(out/(tag+'.npz'))})
        failures=[]
        if residuals['phase24']>contract['connection_screen']:failures.append('phase24 connection')
        if residuals['reference32']>contract['connection_screen']:failures.append('reference32 connection')
        if maxpar>contract['raw_tp_parity_relative_max']:failures.append('phase24/reference32 raw TP parity')
        report.update(z_a0=contract['z_a0'],epsilon_z_a0=eps,connection_residuals=residuals,
                      max_raw_cross_relative_difference=maxpar,raw_cross_relative_differences=parity,
                      phase_metadata=by['phase24'][1]['metadata'],reference_metadata=by['reference32'][1]['metadata'],
                      failed_screens=failures)
        report['status']='ZMINUS6_DERIVATIVE_AWARE_QUALIFICATION_PASS' if not failures else 'NUMERICAL_SCREEN_FAILED';rc=0 if not failures else 2
    except BaseException as e:
        rc=130 if isinstance(e,KeyboardInterrupt) else 3
        report['status']='INTERRUPTED' if rc==130 else 'EXECUTION_OR_INPUT_BLOCKED';report['first_failure']={'phase':phase,'type':type(e).__name__,'message':str(e)}
        (out/'failure.traceback.txt').write_text(traceback.format_exc())
    write_new(out/'RETURN_REPORT.json',report)
    manifest={str(q.relative_to(out)):{'sha256':sha(q),'bytes':q.stat().st_size} for q in sorted(out.rglob('*')) if q.is_file()}
    write_new(out/'MANIFEST.json',manifest)
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
        for q in sorted(out.rglob('*')):
            if q.is_file():z.write(q,str(q.relative_to(out)))
    print(json.dumps({'status':report['status'],'report':str(out/'RETURN_REPORT.json'),'archive':str(archive),'capture_execution_allowed':False},indent=2),flush=True)
    return rc
if __name__=='__main__':raise SystemExit(main())
