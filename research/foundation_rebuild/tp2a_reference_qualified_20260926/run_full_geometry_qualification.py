#!/usr/bin/env python3
"""Reference-qualified derivative-aware TP2A geometry qualification.

Each geometry first qualifies a finite plain-Gauss reference ladder. Only after
the reference converges is phase-aware order24 judged against it. Reference
exhaustion is a separate blocker, never a candidate failure. No capture, GPU,
tolerance tuning, epsilon tuning, or basis mutation exists here.
"""
from __future__ import annotations
import os
for _k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[_k]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
import argparse,concurrent.futures as cf,hashlib,json,multiprocessing as mp,queue,subprocess,sys,time,traceback,zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;FND=HERE.parent;REPO=HERE.parents[2]
for p in (HERE,FND/'tp2a_derivative_aware_20260926',FND/'tp2a_perf_20260926',FND/'src',FND/'full_operator_20260926',FND/'reaudit_20260925/repair',REPO):
    if str(p) not in sys.path:sys.path.insert(0,str(p))
import qualification_runtime as qr


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write_json(path,value):
    qr._write_json(path,value)

def build_parser():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True);p.add_argument('--native-build',required=True)
    p.add_argument('--workers',type=int);p.add_argument('--expected-commit');p.add_argument('--resume-from')
    return p

def resource_limits():
    from run_tp2a import resource_limits as upstream
    r=upstream();r=dict(r);r['default_workers']=min(8,r['default_workers']);r['recommended_max_workers']=min(8,r['max_safe_workers']);return r

def geometry_task_specs(z,contract,context=None):
    """All possible task identities for one geometry; execution stays staged."""
    items=candidate_task_specs(z,contract,context)
    for order in contract['reference_orders']:
        items.extend(reference_task_specs(z,order,contract,context))
    return items


def reference_task_specs(z,order,contract,context=None):
    if order not in contract['reference_orders']:raise ValueError('reference order outside frozen ladder')
    eps=float(contract['epsilon_z_a0']);items=[]
    for dz in (-eps,0.,eps):
        row={'method':'reference','reference_order':int(order),'z_center_a0':float(z),'dz_a0':float(dz)}
        if context is not None:row['task_id']=qr.task_identity('reference',z,dz,context,reference_order=order)
        items.append(row)
    return items


def candidate_task_specs(z,contract,context=None):
    eps=float(contract['epsilon_z_a0']);items=[]
    for dz in (-eps,0.,eps):
        row={'method':'phase24','reference_order':None,'z_center_a0':float(z),'dz_a0':float(dz)}
        if context is not None:row['task_id']=qr.task_identity('phase24',z,dz,context)
        items.append(row)
    return items


def execute_geometry_policy(z,contract,epsilon_t,ensure_rows):
    orders=list(contract['reference_orders'])
    if len(orders)<2:raise ValueError('reference ladder requires at least two orders')
    reference_rows=[]
    first_specs=[]
    for order in orders[:2]:first_specs.extend(reference_task_specs(z,order,contract))
    reference_rows.extend(ensure_rows(first_specs))
    reference_receipt=qr.qualify_reference_ladder(reference_rows,epsilon_t,contract)
    remaining=orders[2:]
    while reference_receipt['status']!='REFERENCE_QUALIFIED' and remaining:
        order=remaining.pop(0)
        reference_rows.extend(ensure_rows(reference_task_specs(z,order,contract)))
        reference_receipt=qr.qualify_reference_ladder(reference_rows,epsilon_t,contract)
    if reference_receipt['status']=='REFERENCE_QUALIFIED':
        q=reference_receipt['qualified_order']
        selected=[r for r in reference_rows if r.get('reference_order')==q]
        candidate_rows=ensure_rows(candidate_task_specs(z,contract))
        result=qr.qualify_candidate_against_reference(z,candidate_rows,selected,epsilon_t,contract,q)
        result['reference_qualification']=reference_receipt
        return result
    return {'status':'REFERENCE_CONVERGENCE_UNRESOLVED','z_a0':float(z),
            'qualified_reference_order':None,'reference_qualification':reference_receipt,
            'failed_screens':['reference convergence unresolved'],
            'candidate_evaluated':False,'capture_execution_allowed':False}

def sequence_geometries(z_samples,execute):
    rows=[];first=None
    for z in z_samples:
        row=execute(float(z));rows.append(row)
        if row.get('status')=='REFERENCE_CONVERGENCE_UNRESOLVED':
            first={'kind':'reference','z_a0':float(z),'failed_screens':list(row.get('failed_screens',[]))};break
        if row.get('failed_screens'):
            first={'kind':'numerical','z_a0':float(z),'failed_screens':list(row['failed_screens'])};break
    return rows,first

def verify_sources():
    manifest=json.loads((HERE/'SOURCE_MANIFEST.json').read_text())
    for rel,expected in manifest['files'].items():
        if sha(HERE/rel)!=expected:raise ValueError('package source identity mismatch: '+rel)
    pins=json.loads((HERE/'DEPENDENCY_PINS.json').read_text())
    for row in pins['files']:
        if sha(REPO/row['path'])!=row['sha256']:raise ValueError('upstream source identity mismatch: '+row['path'])
    return {'source_manifest_sha256':sha(HERE/'SOURCE_MANIFEST.json'),'dependency_pins_sha256':sha(HERE/'DEPENDENCY_PINS.json')}

def finish(out,report):
    write_json(out/'RETURN_REPORT.json',report)
    files={str(p.relative_to(out)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(out.rglob('*')) if p.is_file() and not p.name.startswith('.partial_')}
    write_json(out/'MANIFEST.json',files);archive=out.with_name(out.name+'_RETURN.zip')
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(out.rglob('*')):
            if p.is_file() and not p.name.startswith('.partial_'):z.write(p,str(p.relative_to(out)))
    print(json.dumps({'status':report['status'],'report':str(out/'RETURN_REPORT.json'),'archive':str(archive),'capture_execution_allowed':False}),flush=True)

def main(argv=None):
    a=build_parser().parse_args(argv);out=Path(a.out).resolve();archive=out.with_name(out.name+'_RETURN.zip')
    if out.exists() or archive.exists():build_parser().error('output exists; nothing overwritten')
    out.mkdir(parents=True);start=time.monotonic();phase='preflight';rc=0
    report={'schema':'BASS_TP2A_FULL_GEOMETRY_RETURN_V1','status':'IN_PROGRESS','scope':'NINE_REMAINING_GEOMETRIES_DERIVATIVE_AWARE_ONLY',
        'capture_execution_allowed':False,'production_admission':'HOLD','all_bound':'OPEN','b_grid':'NO_GO','original_capture_gap_resolved':False,
        'gpu_run':False,'propagation_run':False,'completed_geometry':[]}
    def emit(**row):
        row={'elapsed_seconds':time.monotonic()-start,**row}
        with (out/'PROGRESS.jsonl').open('a') as f:f.write(json.dumps(row,separators=(',',':'))+'\n');f.flush();os.fsync(f.fileno())
        print(json.dumps(row),flush=True)
    emit(event='run_start',out=str(out))
    try:
        pins=verify_sources();contract=json.loads((HERE/'CONTRACT.json').read_text())
        head=subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True,stderr=subprocess.DEVNULL).strip() if (REPO/'.git').exists() else None
        tree=subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD^{tree}'],text=True,stderr=subprocess.DEVNULL).strip() if head else None
        if a.expected_commit and head!=a.expected_commit:raise ValueError('execution commit mismatch')
        from bass_foundations.radial_basis import RadialSpec,atomic_bank
        from cr_repro.observables import projectile_speed_au
        from native_ring import NativeRing
        from runtime import save_bank,load_bank
        native_dir=str(Path(a.native_build).resolve());native=NativeRing(native_dir).receipt
        limits=resource_limits();workers=a.workers if a.workers is not None else limits['default_workers']
        if workers<1 or workers>limits['max_safe_workers']:raise ValueError('workers exceeds detected CPU/memory safety budget')
        config=dict(contract);config['speed']=projectile_speed_au(contract['energy_keV_per_u'])
        if a.resume_from:
            source=Path(a.resume_from).resolve();bank,basis_record=load_bank(source)
            for name in ('BASIS.json','BASIS.npz'):qr._atomic_file(out/name,lambda f,name=name:f.write((source/name).read_bytes()))
        else:
            bank=atomic_bank(RadialSpec(**contract['radial_spec']));basis_record=save_bank(out,bank)
        context={'contract':contract,'basis_identity':basis_record['identity'],'native_library_sha256':native['library_sha256'],'source_pins':pins}
        context_id=qr._digest(context);all_specs=[spec for z in contract['z_samples_a0'] for spec in geometry_task_specs(z,contract,context)]
        allowed={s['task_id'] for s in all_specs};restored=0
        if a.resume_from:
            previous=json.loads((Path(a.resume_from)/'INTAKE.json').read_text())
            if previous['context']!=context:raise ValueError('resume context differs; no automatic cache migration')
            restored=qr.restore_tasks(a.resume_from,out,context_id,allowed)
        report.update(execution_head=head,execution_tree=tree,workers=workers,resources=limits,native_build=native,restored_tasks=restored)
        write_json(out/'INTAKE.json',{'context':context,'context_id':context_id,'report':report})
        phase='new_tests';env=dict(os.environ,PYTEST_DISABLE_PLUGIN_AUTOLOAD='1');cmd=[sys.executable,'-m','pytest','-q','-p','no:cacheprovider',str(HERE/'tests'),'--junitxml='+str(out/'tests.xml')]
        emit(event='tests_start');p=subprocess.run(cmd,stdout=(out/'tests.stdout').open('x'),stderr=(out/'tests.stderr').open('x'),env=env,timeout=180)
        if p.returncode:raise RuntimeError('new sidecar tests failed')
        emit(event='tests_complete',returncode=p.returncode)
        phase='geometry_scan';ctx=mp.get_context('spawn')
        with cf.ProcessPoolExecutor(max_workers=workers,mp_context=ctx,initializer=qr.worker_init,initargs=(config,bank,native_dir,context_id,str(out))) as pool:
            def execute_geometry(z):
                def ensure_rows(specs_without_ids):
                    specs=[]
                    for item in specs_without_ids:
                        row=dict(item)
                        row['task_id']=qr.task_identity(row['method'],z,row['dz_a0'],context,
                            reference_order=row.get('reference_order'))
                        specs.append(row)
                    missing=[]
                    for spec in specs:
                        try:
                            qr.load_task(out,spec['task_id'],context_id)
                            emit(event='task_reused',z_a0=z,method=spec['method'],reference_order=spec.get('reference_order'),dz_a0=spec['dz_a0'])
                        except FileNotFoundError:
                            missing.append(spec)
                    if missing:
                        emit(event='task_batch_start',z_a0=z,method=missing[0]['method'],reference_order=missing[0].get('reference_order'),missing_tasks=len(missing),workers=workers)
                    futures={pool.submit(qr.worker_task,s):s for s in missing};last=time.monotonic()
                    while futures:
                        done,_=cf.wait(futures,timeout=.25,return_when=cf.FIRST_COMPLETED)
                        if time.monotonic()-last>=5:
                            emit(event='heartbeat',z_a0=z,pending_tasks=len(futures));last=time.monotonic()
                        for f in done:
                            spec=futures.pop(f);res=f.result();emit(event='task_complete',z_a0=z,method=spec['method'],reference_order=spec.get('reference_order'),dz_a0=spec['dz_a0'],reused=res['reused'],wall_seconds=res['wall_seconds'])
                    return [qr.task_row(out,s['task_id'],context_id) for s in specs]
                emit(event='geometry_start',z_a0=z,workers=workers,reference_orders=contract['reference_orders'])
                receipt=execute_geometry_policy(z,contract,contract['epsilon_z_a0']/config['speed'],ensure_rows)
                write_json(out/'geometry'/f"z_{z:+05.1f}.json",receipt)
                emit(event='geometry_complete',z_a0=z,status=receipt['status'],qualified_reference_order=receipt.get('qualified_reference_order'),failed_screens=receipt.get('failed_screens',[]))
                return receipt
            rows,first=sequence_geometries(contract['z_samples_a0'],execute_geometry)
        report['completed_geometry']=rows
        if first:
            report['first_failure']=first;rc=2
            report['status']='REFERENCE_CONVERGENCE_UNRESOLVED' if first['kind']=='reference' else 'NUMERICAL_SCREEN_FAILED'
        elif len(rows)!=len(contract['z_samples_a0']):raise RuntimeError('missing declared geometry results')
        else:report['status']='TP2A_REFERENCE_QUALIFIED_FULL_GEOMETRY_PASS'
    except BaseException as e:
        rc=130 if isinstance(e,KeyboardInterrupt) else 3;report['status']='INTERRUPTED' if rc==130 else ('IDENTITY_OR_INPUT_BLOCKED' if isinstance(e,(ValueError,FileNotFoundError)) else 'EXECUTION_OR_ENVIRONMENT_BLOCKED')
        report['first_failure']={'phase':phase,'type':type(e).__name__,'message':str(e)};(out/'failure.traceback.txt').write_text(traceback.format_exc())
    report['wall_seconds']=time.monotonic()-start;report['continuous_trajectory_error_bound']=False
    finish(out,report);return rc
if __name__=='__main__':raise SystemExit(main())
