#!/usr/bin/env python3
"""TP2C: qualify the four missing negative-tail geometries with the TP2B analytic backend.

This runner byte-verifies the user's successful TP2B predecessor evidence, runs
only TP2C-new tests, then evaluates z/a0 = -12,-10,-8,-6 with the same frozen
full18 basis, exact s+p analytic backend, finite resolution ladders, and screens.
No legacy ring task import, capture propagation, tolerance tuning, basis change,
or continuous-trajectory certificate is permitted.
"""
from __future__ import annotations
import os
for _k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[_k]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
import argparse,concurrent.futures as cf,hashlib,json,multiprocessing as mp,subprocess,sys,time,traceback,zipfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
FND=HERE.parent
TP2B=FND/'tp2b_analytic_integration_20260927'
if str(TP2B) not in sys.path:sys.path.insert(0,str(TP2B))
import run_analytic_geometry_qualification as base

REPO=base.REPO
qr=base.qr
ir=base.ir
pa=base.pa


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path,value):
    qr._write_json(path,value)


def parser():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',required=True)
    p.add_argument('--analytic-build',required=True)
    p.add_argument('--predecessor-report',required=True)
    p.add_argument('--predecessor-archive',required=True)
    p.add_argument('--workers',type=int)
    p.add_argument('--expected-commit')
    p.add_argument('--resume-from')
    return p


def verify_own_sources():
    manifest=json.loads((HERE/'SOURCE_MANIFEST.json').read_text())
    for rel,expected in manifest['files'].items():
        if sha(HERE/rel)!=expected:
            raise ValueError('TP2C source identity mismatch: '+rel)
    pins=json.loads((HERE/'UPSTREAM_PINS.json').read_text())
    for row in pins['files']:
        if sha(REPO/row['path'])!=row['sha256']:
            raise ValueError('TP2B upstream identity mismatch: '+row['path'])
    tp2b_pins=base.verify_sources()
    return {
        'tp2c_source_manifest_sha256':sha(HERE/'SOURCE_MANIFEST.json'),
        'tp2c_upstream_pins_sha256':sha(HERE/'UPSTREAM_PINS.json'),
        'tp2b_source_pins':tp2b_pins,
    }


def verify_predecessor(report_path,archive_path,contract):
    report_path=Path(report_path).resolve();archive_path=Path(archive_path).resolve()
    if sha(report_path)!=contract['predecessor_return_report_sha256']:
        raise ValueError('predecessor RETURN_REPORT sha256 mismatch')
    if sha(archive_path)!=contract['predecessor_return_archive_sha256']:
        raise ValueError('predecessor RETURN archive sha256 mismatch')
    report=json.loads(report_path.read_text())
    if report.get('status')!=contract['predecessor_status']:
        raise ValueError('unexpected predecessor status')
    if report.get('execution_head')!=contract['upstream_tp2b_commit'] or report.get('execution_tree')!=contract['upstream_tp2b_tree']:
        raise ValueError('unexpected predecessor Git identity')
    counts=report.get('new_tests',{}).get('counts',{})
    if report.get('new_tests',{}).get('returncode')!=0 or counts!={'tests':29,'failures':0,'errors':0,'skipped':0}:
        raise ValueError('unexpected predecessor test evidence')
    rows=report.get('completed_geometry',[])
    zs=[float(r.get('z_a0')) for r in rows]
    if zs!=contract['predecessor_z_samples_a0']:
        raise ValueError('unexpected predecessor geometry coverage')
    for row in rows:
        if row.get('status')!='GEOMETRY_QUALIFIED' or row.get('failed_screens'):
            raise ValueError('predecessor contains unqualified geometry')
        if row.get('candidate_reference_alias'):
            raise ValueError('predecessor selected candidate/reference pair was aliased')
        if row.get('evidence_relation')!='INDEPENDENT_NUMERICAL_TASK_COMPARISON':
            raise ValueError('predecessor selected comparison was not independent')
    ceilings={
        'capture_execution_allowed':False,
        'production_admission':'HOLD',
        'all_bound':'OPEN',
        'b_grid':'NO_GO',
        'original_capture_gap_resolved':False,
        'continuous_trajectory_error_bound':False,
    }
    for key,value in ceilings.items():
        if report.get(key)!=value:
            raise ValueError('predecessor claim ceiling mismatch: '+key)
    with zipfile.ZipFile(archive_path) as zf:
        names=set(zf.namelist())
        if 'RETURN_REPORT.json' not in names:
            raise ValueError('predecessor archive lacks RETURN_REPORT.json')
        if hashlib.sha256(zf.read('RETURN_REPORT.json')).hexdigest()!=contract['predecessor_return_report_sha256']:
            raise ValueError('predecessor archive/report bytes disagree')
    return {
        'report_path':str(report_path),
        'archive_path':str(archive_path),
        'return_report_sha256':sha(report_path),
        'return_archive_sha256':sha(archive_path),
        'status':report['status'],
        'execution_head':report['execution_head'],
        'execution_tree':report['execution_tree'],
        'completed_geometry':rows,
        'new_tests':report['new_tests'],
    }


def finish(out,report):
    write_json(out/'RETURN_REPORT.json',report)
    files={str(p.relative_to(out)):{'sha256':sha(p),'bytes':p.stat().st_size}
           for p in sorted(out.rglob('*')) if p.is_file() and not p.name.startswith('.partial_')}
    write_json(out/'MANIFEST.json',files)
    archive=out.with_name(out.name+'_RETURN.zip')
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(out.rglob('*')):
            if p.is_file() and not p.name.startswith('.partial_'):
                zf.write(p,str(p.relative_to(out)))
    print(json.dumps({'status':report['status'],'report':str(out/'RETURN_REPORT.json'),'archive':str(archive),'capture_execution_allowed':False}),flush=True)


def main(argv=None):
    a=parser().parse_args(argv)
    out=Path(a.out).resolve();archive=out.with_name(out.name+'_RETURN.zip')
    if out.exists() or archive.exists():parser().error('output exists; nothing overwritten')
    out.mkdir(parents=True)
    start=time.monotonic();phase='preflight';rc=0
    report={
        'schema':'BASS_TP2C_ANALYTIC_FULL13_STATIC_GEOMETRY_RETURN_V1',
        'status':'IN_PROGRESS',
        'scope':'FULL13_DISCRETE_STATIC_OPERATOR_GEOMETRY_ONLY',
        'capture_execution_allowed':False,
        'production_admission':'HOLD',
        'all_bound':'OPEN',
        'b_grid':'NO_GO',
        'original_capture_gap_resolved':False,
        'continuous_trajectory_error_bound':False,
        'qualification_sector':'full',
        'even14_pruning_used':False,
        'legacy_ring_task_imported':False,
        'old_test_suite_reexecuted':False,
        'completed_geometry':[],
        'unique_operator_evaluations':0,
        'role_requests':0,
        'aliased_requests':0,
        'reused_task_reads':0,
    }
    def emit(**row):
        row={'elapsed_seconds':time.monotonic()-start,**row}
        with (out/'PROGRESS.jsonl').open('a') as f:
            f.write(json.dumps(row,separators=(',',':'))+'\n');f.flush();os.fsync(f.fileno())
        print(json.dumps(row),flush=True)
    emit(event='run_start',out=str(out))
    try:
        source_pins=verify_own_sources()
        contract=json.loads((HERE/'CONTRACT.json').read_text())
        predecessor=verify_predecessor(a.predecessor_report,a.predecessor_archive,contract)
        head=subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True,stderr=subprocess.DEVNULL).strip() if (REPO/'.git').exists() else None
        tree=subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD^{tree}'],text=True,stderr=subprocess.DEVNULL).strip() if head else None
        if a.expected_commit and head!=a.expected_commit:
            raise ValueError('execution commit mismatch')
        if head:
            ancestry=subprocess.run(['git','-C',str(REPO),'merge-base','--is-ancestor',contract['upstream_tp2b_commit'],head],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            if ancestry.returncode!=0:
                raise ValueError('TP2C execution commit does not descend from frozen TP2B commit')
        from bass_foundations.radial_basis import RadialSpec,atomic_bank
        from bass_foundations.two_center import Trajectory
        from cr_repro.observables import projectile_speed_au
        from exact_cross import MomentKernel
        from runtime import save_bank,load_bank
        analytic_dir=str(Path(a.analytic_build).resolve())
        analytic=MomentKernel(analytic_dir).receipt
        if analytic.get('source_sha256')!=contract['analytic_source_sha256']:
            raise ValueError('analytic source sha256 mismatch')
        if analytic.get('library_sha256')!=contract['analytic_library_sha256']:
            raise ValueError('analytic library sha256 mismatch')
        limits=base.resource_limits();workers=a.workers if a.workers is not None else limits['default_workers']
        if workers<1 or workers>limits['max_safe_workers']:
            raise ValueError('workers exceeds detected CPU/memory safety budget')
        config=dict(contract);config['speed']=projectile_speed_au(contract['energy_keV_per_u'])
        if a.resume_from:
            source=Path(a.resume_from).resolve();bank,basis_record=load_bank(source)
            for name in ('BASIS.json','BASIS.npz'):
                ir._atomic_file(out/name,lambda f,name=name:f.write((source/name).read_bytes()))
        else:
            bank=atomic_bank(RadialSpec(**contract['radial_spec']));basis_record=save_bank(out,bank)
        trajectory=Trajectory(((0.,0.,0.),(contract['b_a0'],0.,0.)),((0.,0.,0.),(0.,0.,config['speed'])))
        physics_identity={
            'contract_sha256':sha(HERE/'CONTRACT.json'),
            'basis_identity':basis_record['identity'],
            'analytic_source_sha256':analytic['source_sha256'],
            'analytic_library_sha256':analytic['library_sha256'],
            'same_center_order':contract['same_center_order'],
            'qualification_sector':'full',
            'source_pins':source_pins,
            'predecessor_return_report_sha256':predecessor['return_report_sha256'],
            'predecessor_return_archive_sha256':predecessor['return_archive_sha256'],
        }
        context={'contract':contract,'physics_identity':physics_identity};context_id=qr._digest(context)
        all_roles=[];eps=float(contract['epsilon_z_a0'])
        for z in contract['new_z_samples_a0']:
            for family in ('reference','candidate'):
                for rule in pa.resolution_plan(contract,family):
                    for dz in (-eps,0.,eps):
                        spec={'family':family,'order':rule['order'],'integration_subdivisions':rule['subdivisions'],'z_center_a0':float(z),'dz_a0':float(dz)}
                        all_roles.append(ir.role_request(spec['family'],z,spec['dz_a0'],spec['order'],spec['integration_subdivisions'],trajectory,bank[0].edges,physics_identity,phase_budget=contract['phase_budget_rad'],sector='full'))
        allowed={r['numerical_task_id'] for r in all_roles};restored=0
        if a.resume_from:
            previous=json.loads((Path(a.resume_from)/'INTAKE.json').read_text())
            if previous['context']!=context:
                raise ValueError('resume context differs; no automatic cache migration')
            restored=ir.restore_numeric_tasks(a.resume_from,out,context_id,allowed)
        report.update(execution_head=head,execution_tree=tree,workers=workers,resources=limits,analytic_build=analytic,restored_tasks=restored,predecessor=predecessor)
        write_json(out/'INTAKE.json',{'context':context,'context_id':context_id,'report':report})

        phase='tests';env=dict(os.environ,PYTEST_DISABLE_PLUGIN_AUTOLOAD='1',BASS_ANALYTIC_SOURCE_ROOT=str(REPO))
        cmd=[sys.executable,'-m','pytest','-q','-p','no:cacheprovider',str(HERE/'tests'),'--junitxml='+str(out/'tests.xml')]
        emit(event='tests_start',scope='tp2c_new_tests_only')
        with (out/'tests.stdout').open('x') as so,(out/'tests.stderr').open('x') as se:
            p=subprocess.run(cmd,stdout=so,stderr=se,env=env,timeout=120)
        import xml.etree.ElementTree as ET
        counts={k:0 for k in ('tests','failures','errors','skipped')}
        if (out/'tests.xml').exists():
            for suite in ET.parse(out/'tests.xml').getroot().iter('testsuite'):
                for k in counts:counts[k]+=int(suite.attrib.get(k,0))
        report['new_tests']={'returncode':p.returncode,'counts':counts}
        if p.returncode or not counts['tests'] or any(counts[k] for k in ('failures','errors','skipped')):
            raise RuntimeError('TP2C new tests failed or skipped')
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
            rows,first=pa.sequence_geometries(contract['new_z_samples_a0'],execute_geometry)
        report['completed_geometry']=rows
        if first:
            report['first_failure']=first;rc=2;report['status']={'reference':'REFERENCE_CONVERGENCE_UNRESOLVED','candidate':'CANDIDATE_CONVERGENCE_UNRESOLVED'}.get(first['kind'],'NUMERICAL_SCREEN_FAILED')
        elif len(rows)!=len(contract['new_z_samples_a0']):
            raise RuntimeError('missing declared negative-tail geometry results')
        else:
            report['full13_static_geometry_coverage']=True
            report['full13_z_samples_a0']=contract['full13_z_samples_a0']
            report['status']='TP2C_ANALYTIC_FULL13_STATIC_GEOMETRY_PASS'
    except BaseException as e:
        rc=130 if isinstance(e,KeyboardInterrupt) else 3
        report['status']='INTERRUPTED' if rc==130 else ('IDENTITY_OR_INPUT_BLOCKED' if isinstance(e,(ValueError,FileNotFoundError)) else 'EXECUTION_OR_ENVIRONMENT_BLOCKED')
        report['first_failure']={'phase':phase,'type':type(e).__name__,'message':str(e)}
        (out/'failure.traceback.txt').write_text(traceback.format_exc())
    report['wall_seconds']=time.monotonic()-start
    finish(out,report)
    return rc

if __name__=='__main__':
    raise SystemExit(main())
