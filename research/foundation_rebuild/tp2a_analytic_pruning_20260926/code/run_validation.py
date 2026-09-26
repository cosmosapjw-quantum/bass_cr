#!/usr/bin/env python3
"""Fixed six-node z=0 analytic-kernel qualification; never the old full scan.

Inputs are frozen matrices/basis from the supplied HP diagnosis. Source hashes
and native binary identity are checked. New operators are computed only for
h2q56 and h2q64 at z=-1e-4,0,+1e-4. Candidate/reference role aliases share raw
results, and are explicitly not counted as independent reference evidence.
"""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[k]='1'
import argparse,concurrent.futures as cf,hashlib,json,multiprocessing as mp,subprocess,sys,time,traceback,zipfile
from pathlib import Path
import numpy as np
import bootstrap
from runtime import load_bank
from bass_foundations.two_center import Trajectory,symmetric_channels
from cr_repro.observables import projectile_speed_au
from exact_cross import MomentKernel,KEYS,resolution_edges,frame
from assemble import assemble
from task_plan import numerical_key
ROOT=Path(__file__).resolve().parents[1]

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(path,obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    data=(json.dumps(obj,indent=2,allow_nan=False)+'\n').encode()
    temp=path.with_name(path.name+'.partial')
    with temp.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
    try:os.link(temp,path)
    finally:temp.unlink()

def check_sources():
    manifest=ROOT/'SOURCE_MANIFEST.json'
    if not manifest.exists():raise ValueError('release source manifest missing')
    for rel,value in json.loads(manifest.read_text())['files'].items():
        if sha(ROOT/rel)!=value:raise ValueError('source/input identity mismatch: '+rel)
    return sha(manifest)

def worker(job):
    root,build,out,q,z,key=job;root=Path(root);out=Path(out)
    bank,_=load_bank(root/'inputs/z0');channels=symmetric_channels(bank);v=projectile_speed_au(100)
    tr=Trajectory(((0,0,0),(2,0,0)),((0,0,0),(0,0,v)));kernel=MomentKernel(build)
    tic=time.perf_counter();cpu=time.process_time()
    raw,full=assemble(tr,channels,z/v,kernel,order=q,subdivisions=2)
    file=out/'nodes'/f'{key}.npz';file.parent.mkdir(parents=True,exist_ok=True)
    with file.open('xb') as f:np.savez_compressed(f,**{k:raw[k] for k in KEYS},**{k:full[k] for k in ('S','H','D')});f.flush();os.fsync(f.fileno())
    record={'order':q,'z_a0':z,'task_key':key,'matrix_sha256':sha(file),'wall_seconds':time.perf_counter()-tic,'cpu_seconds':time.process_time()-cpu,
      'metadata':raw['metadata'],'diagnostics':full['diagnostics'],'pid':os.getpid()}
    write(file.with_suffix('.json'),record);return record

def comparison(a,b):
    detail={}
    for k in KEYS:
        d=float(np.linalg.norm(a[k]-b[k]));n=float(np.linalg.norm(b[k]))
        if n==0 and d!=0:raise ArithmeticError('structural zero mismatch '+k)
        detail[k]=d/n if n else 0.
    return detail

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--native-build',required=True);p.add_argument('--out',required=True);p.add_argument('--workers',type=int,default=3);a=p.parse_args(argv)
    out=Path(a.out).resolve()
    if out.exists() or out.with_name(out.name+'_RETURN.zip').exists():p.error('create-only output exists')
    if not 1<=a.workers<=6:p.error('workers must be 1..6; six independent fixed nodes only')
    out.mkdir(parents=True);start=time.monotonic();phase='preflight';rc=0
    report={'schema':'BASS_ANALYTIC_Z0_QUALIFICATION_V1','status':'IN_PROGRESS','scope':'FROZEN_18_CHANNEL_Z0_STENCIL_ONLY',
       'capture_execution_allowed':False,'production_admission':'HOLD','all_bound':'OPEN','b_grid':'NO_GO','original_capture_gap_resolved':False}
    def emit(event,**kw):
        row={'event':event,'elapsed':time.monotonic()-start,**kw}
        with (out/'PROGRESS.jsonl').open('a') as f:f.write(json.dumps(row)+'\n');f.flush()
        print(json.dumps(row),flush=True)
    try:
        source=check_sources();kernel=MomentKernel(a.native_build);bank,brec=load_bank(ROOT/'inputs/z0');ch=symmetric_channels(bank);v=projectile_speed_au(100)
        tr=Trajectory(((0,0,0),(2,0,0)),((0,0,0),(0,0,v)))
        context={'source_manifest':source,'basis_identity':brec['identity'],'native':kernel.receipt['library_sha256'],'trajectory':tr.record()}
        identity=hashlib.sha256(json.dumps(context,sort_keys=True).encode()).hexdigest()
        roles=[];jobs={};lookup={}
        for role,q in [('reference_low',56),('reference_high',64),('candidate',56)]:
            for z in (-1e-4,0.,1e-4):
                _,R,axes,dv=frame(tr,z/v)
                req={'role':role,'order':q,'time_hex':float(z/v).hex(),'sector':'full','integration_edges':resolution_edges(bank[0].edges,R,float(dv@axes[0]),2,None).tolist()}
                key=numerical_key(req,identity);roles.append({**req,'key':key});lookup[(q,z)]=key
                jobs.setdefault(key,(str(ROOT),str(Path(a.native_build).resolve()),str(out),q,z,key))
        write(out/'INTAKE.json',{'context':context,'roles':roles,'unique_tasks':len(jobs),'aliased_role_requests':len(roles)-len(jobs)})
        # Only new tests. The old TP1/HP qualifiers are never called.
        phase='new_tests';env=dict(os.environ,PYTEST_DISABLE_PLUGIN_AUTOLOAD='1',BASS_MOMENT_BUILD=str(Path(a.native_build).resolve()))
        cmd=[sys.executable,'-m','pytest','-q','-p','no:cacheprovider',str(ROOT/'tests'),'--junitxml='+str(out/'tests.xml')]
        with (out/'tests.stdout').open('x') as so,(out/'tests.stderr').open('x') as se:proc=subprocess.run(cmd,stdout=so,stderr=se,env=env,timeout=180)
        report['new_tests_returncode']=proc.returncode
        if proc.returncode:raise RuntimeError('new analytic tests failed')
        phase='nodes';emit('nodes_start',unique_tasks=len(jobs),requested_roles=len(roles))
        records=[]
        with cf.ProcessPoolExecutor(max_workers=a.workers,mp_context=mp.get_context('spawn')) as pool:
            pending={pool.submit(worker,j):j for j in jobs.values()};last=time.monotonic()
            while pending:
                done,_=cf.wait(pending,timeout=.2,return_when=cf.FIRST_COMPLETED)
                if time.monotonic()-last>=5:emit('heartbeat',pending=len(pending));last=time.monotonic()
                for f in done:
                    pending.pop(f);record=f.result();records.append(record);emit('node_complete',order=record['order'],z=record['z_a0'],seconds=record['wall_seconds'])
        report['nodes']=records
        matrices={}
        for (q,z),key in lookup.items():
            with np.load(out/'nodes'/f'{key}.npz',allow_pickle=False) as f:matrices[(q,z)]={k:np.array(f[k]) for k in f.files}
        residuals={};h=1e-4/v;external={};refdiff={}
        for q in (56,64):
            m,c,p0=[matrices[(q,z)] for z in (-1e-4,0.,1e-4)]
            fd=(p0['S']-m['S'])/(2*h);direct=c['D']+c['D'].conj().T
            residuals[str(q)]=float(np.linalg.norm(fd-direct)/max(np.linalg.norm(fd),np.linalg.norm(direct),1e-300))
            for z in (-1e-4,0.,1e-4):
                with np.load(ROOT/'inputs/z0/hp'/f'h2q64_z{z:+.8f}.npz',allow_pickle=False) as old:
                    external[f'q{q}:z{z:+.8f}']=comparison(matrices[(q,z)],old)
        for z in (-1e-4,0.,1e-4):refdiff[str(z)]=comparison(matrices[(56,z)],matrices[(64,z)])
        worst_external=max(v for row in external.values() for v in row.values());worst_ref=max(v for row in refdiff.values() for v in row.values())
        failures=[]
        if max(residuals.values())>1e-6:failures.append('metric_connection')
        if max(worst_external,worst_ref)>1e-9:failures.append('raw_parity')
        report.update(connection_relative=residuals,vs_independent_stored_ring=external,reference_refinement=refdiff,
            max_external_relative=worst_external,max_refinement_relative=worst_ref,unique_operator_evaluations=len(jobs),role_requests=len(roles),aliased_requests=len(roles)-len(jobs),
            alias_is_independent_evidence=False,failed_screens=failures)
        report['status']='ANALYTIC_Z0_QUALIFICATION_PASS' if not failures else 'NUMERICAL_SCREEN_FAILED';rc=0 if not failures else 2
    except BaseException as e:
        rc=130 if isinstance(e,KeyboardInterrupt) else 3;report['status']='INTERRUPTED' if rc==130 else 'EXECUTION_OR_INPUT_BLOCKED'
        report['first_failure']={'phase':phase,'type':type(e).__name__,'message':str(e)};(out/'failure.traceback.txt').write_text(traceback.format_exc())
    report['wall_seconds']=time.monotonic()-start;emit('finalizing',status=report['status']);write(out/'RETURN_REPORT.json',report)
    write(out/'MANIFEST.json',{str(f.relative_to(out)):sha(f) for f in sorted(out.rglob('*')) if f.is_file()})
    archive=out.with_name(out.name+'_RETURN.zip')
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
        for f in sorted(out.rglob('*')):
            if f.is_file():z.write(f,str(f.relative_to(out)))
    print(json.dumps({'event':'finish','status':report['status'],'out':str(out),'archive':str(archive)}),flush=True);return rc
if __name__=='__main__':raise SystemExit(main())
