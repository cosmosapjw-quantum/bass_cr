#!/usr/bin/env python3
"""TP2B full18 geometry qualification using exact analytic angular moments.

The frozen TP2A radial-resolution policy and numerical screens are reused.
Only the cross-center angular backend is replaced. Candidate/reference role
labels may alias one canonical numerical task only when the effective mesh,
order, exact time, sector, basis/physics identity, and analytic engine match.
No capture, GPU, tolerance tuning, epsilon tuning, basis mutation, or even14
operator pruning exists in this qualification runner.
"""
from __future__ import annotations
import os
for _k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[_k]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
import argparse,concurrent.futures as cf,hashlib,json,multiprocessing as mp,subprocess,sys,time,traceback,zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;FND=HERE.parent;REPO=HERE.parents[2]
os.environ.setdefault('BASS_ANALYTIC_SOURCE_ROOT',str(REPO))
for p in (HERE,FND/'tp2a_reference_qualified_20260926',FND/'tp2a_analytic_pruning_20260926'/'code',FND/'tp2a_derivative_aware_20260926',FND/'tp2a_perf_20260926',FND/'src',FND/'full_operator_20260926',FND/'reaudit_20260925/repair',REPO):
    if str(p) not in sys.path:sys.path.insert(0,str(p))
import qualification_runtime as qr
import integration_runtime as ir
import policy_adapter as pa


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write_json(path,value):qr._write_json(path,value)

def build_parser():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True);p.add_argument('--analytic-build',required=True)
    p.add_argument('--workers',type=int);p.add_argument('--expected-commit');p.add_argument('--resume-from')
    return p

def resource_limits():
    from run_tp2a import resource_limits as upstream
    r=dict(upstream());r['default_workers']=min(8,r['default_workers']);r['recommended_max_workers']=min(8,r['max_safe_workers']);return r

def verify_sources():
    rec=json.loads((HERE/'SOURCE_MANIFEST.json').read_text())
    for rel,expected in rec['files'].items():
        if sha(HERE/rel)!=expected:raise ValueError('integration source identity mismatch: '+rel)
    deps=json.loads((HERE/'DEPENDENCY_PINS.json').read_text())
    for row in deps['files']:
        if sha(REPO/row['path'])!=row['sha256']:raise ValueError('dependency identity mismatch: '+row['path'])
    return {'integration_manifest_sha256':sha(HERE/'SOURCE_MANIFEST.json'),'dependency_pins_sha256':sha(HERE/'DEPENDENCY_PINS.json')}

def role_specs(z,contract):
    out=[];eps=float(contract['epsilon_z_a0'])
    for family in ('reference','candidate'):
        for rule in pa.resolution_plan(contract,family):
            for dz in (-eps,0.,eps):out.append({'family':family,'order':rule['order'],'integration_subdivisions':rule['subdivisions'],'z_center_a0':float(z),'dz_a0':float(dz)})
    return out

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
    report={'schema':'BASS_TP2B_ANALYTIC_FULL_GEOMETRY_RETURN_V1','status':'IN_PROGRESS','scope':'FULL18_OPERATOR_QUALIFICATION_ONLY',
      'capture_execution_allowed':False,'production_admission':'HOLD','all_bound':'OPEN','b_grid':'NO_GO','original_capture_gap_resolved':False,
      'qualification_sector':'full','even14_pruning_used':False,'legacy_ring_task_imported':False,'completed_geometry':[],
      'unique_operator_evaluations':0,'role_requests':0,'aliased_requests':0,'reused_task_reads':0}
    def emit(**row):
        row={'elapsed_seconds':time.monotonic()-start,**row}
        with (out/'PROGRESS.jsonl').open('a') as f:f.write(json.dumps(row,separators=(',',':'))+'\n');f.flush();os.fsync(f.fileno())
        print(json.dumps(row),flush=True)
    emit(event='run_start',out=str(out))
    try:
        pins=verify_sources();contract=json.loads((HERE/'CONTRACT.json').read_text())
        if contract.get('qualification_sector')!='full' or contract.get('cross_backend')!='EXACT_SP_MOMENTS_CXX_V1':raise ValueError('unexpected fixed integration contract')
        head=subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True,stderr=subprocess.DEVNULL).strip() if (REPO/'.git').exists() else None
        tree=subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD^{tree}'],text=True,stderr=subprocess.DEVNULL).strip() if head else None
        if a.expected_commit and head!=a.expected_commit:raise ValueError('execution commit mismatch')
        from bass_foundations.radial_basis import RadialSpec,atomic_bank
        from bass_foundations.two_center import Trajectory,symmetric_channels
        from cr_repro.observables import projectile_speed_au
        from exact_cross import MomentKernel
        from runtime import save_bank,load_bank
        analytic_dir=str(Path(a.analytic_build).resolve());analytic=MomentKernel(analytic_dir).receipt
        limits=resource_limits();workers=a.workers if a.workers is not None else limits['default_workers']
        if workers<1 or workers>limits['max_safe_workers']:raise ValueError('workers exceeds detected CPU/memory safety budget')
        config=dict(contract);config['speed']=projectile_speed_au(contract['energy_keV_per_u'])
        if a.resume_from:
            source=Path(a.resume_from).resolve();bank,basis_record=load_bank(source)
            for name in ('BASIS.json','BASIS.npz'):ir._atomic_file(out/name,lambda f,name=name:f.write((source/name).read_bytes()))
        else:
            bank=atomic_bank(RadialSpec(**contract['radial_spec']));basis_record=save_bank(out,bank)
        trajectory=Trajectory(((0.,0.,0.),(contract['b_a0'],0.,0.)),((0.,0.,0.),(0.,0.,config['speed'])))
        physics_identity={'contract_sha256':sha(HERE/'CONTRACT.json'),'basis_identity':basis_record['identity'],
          'analytic_source_sha256':analytic['source_sha256'],'analytic_library_sha256':analytic['library_sha256'],
          'same_center_order':contract['same_center_order'],'qualification_sector':'full','source_pins':pins}
        context={'contract':contract,'physics_identity':physics_identity};context_id=qr._digest(context)
        all_roles=[]
        for z in contract['z_samples_a0']:
            for s in role_specs(z,contract):
                all_roles.append(ir.role_request(s['family'],z,s['dz_a0'],s['order'],s['integration_subdivisions'],trajectory,bank[0].edges,physics_identity,phase_budget=contract['phase_budget_rad'],sector='full'))
        allowed={r['numerical_task_id'] for r in all_roles};restored=0
        if a.resume_from:
            previous=json.loads((Path(a.resume_from)/'INTAKE.json').read_text())
            if previous['context']!=context:raise ValueError('resume context differs; no automatic cache migration')
            restored=ir.restore_numeric_tasks(a.resume_from,out,context_id,allowed)
        report.update(execution_head=head,execution_tree=tree,workers=workers,resources=limits,analytic_build=analytic,restored_tasks=restored)
        write_json(out/'INTAKE.json',{'context':context,'context_id':context_id,'report':report})
        phase='tests';env=dict(os.environ,PYTEST_DISABLE_PLUGIN_AUTOLOAD='1',BASS_TEST_ANALYTIC_BUILD=analytic_dir,BASS_MOMENT_BUILD=analytic_dir,BASS_ANALYTIC_SOURCE_ROOT=str(REPO))
        cmd=[sys.executable,'-m','pytest','-q','-p','no:cacheprovider',str(HERE/'tests'),str(FND/'tp2a_analytic_pruning_20260926'/'tests'/'test_analytic.py'),str(FND/'tp2a_analytic_pruning_20260926'/'tests'/'test_task_plan.py'),'--junitxml='+str(out/'tests.xml')]
        emit(event='tests_start')
        with (out/'tests.stdout').open('x') as so,(out/'tests.stderr').open('x') as se:p=subprocess.run(cmd,stdout=so,stderr=se,env=env,timeout=180)
        import xml.etree.ElementTree as ET
        counts={k:0 for k in ('tests','failures','errors','skipped')}
        if (out/'tests.xml').exists():
            for suite in ET.parse(out/'tests.xml').getroot().iter('testsuite'):
                for k in counts:counts[k]+=int(suite.attrib.get(k,0))
        report['new_tests']={'returncode':p.returncode,'counts':counts}
        if p.returncode or not counts['tests'] or any(counts[k] for k in ('failures','errors','skipped')):raise RuntimeError('integration tests failed or skipped')
        emit(event='tests_complete',counts=counts)
        phase='geometry_scan';ctx=mp.get_context('spawn');seen_roles={}
        with cf.ProcessPoolExecutor(max_workers=workers,mp_context=ctx,initializer=ir.worker_init,initargs=(config,bank,analytic_dir,context_id,str(out))) as pool:
            def execute_geometry(z):
                def ensure_rows(specs):
                    roles=[]
                    for s in specs:
                        role=ir.role_request(s['family'],z,s['dz_a0'],s['order'],s['integration_subdivisions'],trajectory,bank[0].edges,physics_identity,phase_budget=contract['phase_budget_rad'],sector='full')
                        roles.append(role);report['role_requests']+=1
                    unique={r['numerical_task_id']:r for r in roles};missing=[]
                    for tid,spec in unique.items():
                        try:ir.load_numeric_task(out,tid,context_id);report['reused_task_reads']+=1
                        except FileNotFoundError:missing.append(spec)
                    futures={pool.submit(ir.worker_task,s):s for s in missing};last=time.monotonic()
                    if missing:emit(event='numeric_batch_start',z_a0=z,unique_missing=len(missing),role_requests=len(roles),workers=workers)
                    while futures:
                        done,_=cf.wait(futures,timeout=.25,return_when=cf.FIRST_COMPLETED)
                        if time.monotonic()-last>=5:emit(event='heartbeat',z_a0=z,pending_numeric_tasks=len(futures));last=time.monotonic()
                        for f in done:
                            spec=futures.pop(f);res=f.result()
                            if not res['reused']:report['unique_operator_evaluations']+=1
                            emit(event='numeric_task_complete',z_a0=z,order=spec['order'],subdivisions=spec['integration_subdivisions'],wall_seconds=res['wall_seconds'])
                    rows=[]
                    for role in roles:
                        receipt,arrays=ir.load_numeric_task(out,role['numerical_task_id'],context_id)
                        sig=(role['family'],role['order'],role['integration_subdivisions'])
                        prior=seen_roles.setdefault(role['numerical_task_id'],set());aliased=bool(prior and sig not in prior)
                        if aliased:report['aliased_requests']+=1
                        prior.add(sig);rows.append(ir.role_row(role,receipt,arrays,aliased=aliased))
                    return rows
                emit(event='geometry_start',z_a0=z,workers=workers)
                receipt=pa.execute_geometry_policy(z,contract,contract['epsilon_z_a0']/config['speed'],ensure_rows,emit)
                write_json(out/'geometry'/f"z_{z:+05.1f}.json",receipt)
                emit(event='geometry_complete',z_a0=z,status=receipt['status'],qualified_reference_order=receipt.get('qualified_reference_order'),qualified_candidate_order=receipt.get('qualified_candidate_order'),failed_screens=receipt.get('failed_screens',[]))
                return receipt
            rows,first=pa.sequence_geometries(contract['z_samples_a0'],execute_geometry)
        report['completed_geometry']=rows
        if first:
            report['first_failure']=first;rc=2;report['status']={'reference':'REFERENCE_CONVERGENCE_UNRESOLVED','candidate':'CANDIDATE_CONVERGENCE_UNRESOLVED'}.get(first['kind'],'NUMERICAL_SCREEN_FAILED')
        elif len(rows)!=len(contract['z_samples_a0']):raise RuntimeError('missing declared geometry results')
        else:report['status']='TP2B_ANALYTIC_FULL18_GEOMETRY_PASS'
    except BaseException as e:
        rc=130 if isinstance(e,KeyboardInterrupt) else 3;report['status']='INTERRUPTED' if rc==130 else ('IDENTITY_OR_INPUT_BLOCKED' if isinstance(e,(ValueError,FileNotFoundError)) else 'EXECUTION_OR_ENVIRONMENT_BLOCKED')
        report['first_failure']={'phase':phase,'type':type(e).__name__,'message':str(e)};(out/'failure.traceback.txt').write_text(traceback.format_exc())
    report['wall_seconds']=time.monotonic()-start;report['continuous_trajectory_error_bound']=False
    finish(out,report);return rc
if __name__=='__main__':raise SystemExit(main())
