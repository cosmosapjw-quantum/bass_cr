#!/usr/bin/env python3
"""TP2D full-window transport with on-demand self-qualified analytic operators.

Every unique operator time requested by metric sentinels, DOP853 reference
transport, or the metric-frame candidate must independently qualify against a
finite adjacent resolution pair before S/H/D are returned. No interpolation,
capture observable, all-bound extraction, b integration, or global supremum
certificate is present in this runner.
"""
from __future__ import annotations
import argparse,hashlib,json,os,shutil,subprocess,sys,time,traceback,xml.etree.ElementTree as ET,zipfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
FND=HERE.parent
REPO=HERE.parents[2]
ANALYTIC=FND/'tp2a_analytic_pruning_20260926'/'code'
PERF=FND/'tp2a_perf_20260926'
TP1=FND/'tp1_short_transport_20260926'
FND_SRC=FND/'src'
FULL=FND/'full_operator_20260926'
REPAIR=FND/'reaudit_20260925/repair'
for p in (HERE,ANALYTIC,PERF,TP1,FND_SRC,FULL,REPAIR,REPO):
    if str(p) not in sys.path:sys.path.insert(0,str(p))

from qualified_provider import ResolutionQualificationError,OperatorQueryBudgetExceeded


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def write_new(path,value):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8') as f:
        json.dump(value,f,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())

def copy_new(source,destination):
    source=Path(source);destination=Path(destination);destination.parent.mkdir(parents=True,exist_ok=True)
    with destination.open('xb') as f:
        f.write(source.read_bytes());f.flush();os.fsync(f.fileno())

def append_jsonl(path,value):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('a',encoding='utf-8') as f:
        f.write(json.dumps(value,allow_nan=False,separators=(',',':'))+'\n');f.flush();os.fsync(f.fileno())


def build_parser():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',required=True)
    p.add_argument('--analytic-build',required=True)
    p.add_argument('--predecessor-report',required=True)
    p.add_argument('--predecessor-archive',required=True)
    p.add_argument('--expected-commit')
    p.add_argument('--resume-from')
    return p


def git_identity():
    try:
        head=subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True,stderr=subprocess.DEVNULL).strip()
        tree=subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD^{tree}'],text=True,stderr=subprocess.DEVNULL).strip()
        return head,tree
    except (subprocess.CalledProcessError,FileNotFoundError):
        return None,None


def verify_ancestry(upstream,head):
    if head is None or not (REPO/'.git').exists():return
    p=subprocess.run(['git','-C',str(REPO),'merge-base','--is-ancestor',str(upstream),str(head)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    if p.returncode!=0:raise ValueError('execution commit does not descend from frozen TP2C commit')


def verify_sources(manifest_path=None,dependency_path=None):
    manifest_path=Path(manifest_path) if manifest_path is not None else HERE/'SOURCE_MANIFEST.json'
    dependency_path=Path(dependency_path) if dependency_path is not None else HERE/'DEPENDENCY_PINS.json'
    manifest=json.loads(manifest_path.read_text());actual={}
    for rel,expected in manifest.get('files',{}).items():
        p=HERE/rel
        if not p.is_file():raise ValueError('source mismatch: missing '+rel)
        got=sha(p);actual['self:'+rel]=got
        if got!=expected:raise ValueError('source mismatch: '+rel)
    deps=json.loads(dependency_path.read_text())
    for row in deps.get('files',[]):
        p=REPO/row['path']
        if not p.is_file():raise ValueError('dependency mismatch: missing '+row['path'])
        got=sha(p);actual['dependency:'+row['path']]=got
        if got!=row['sha256']:raise ValueError('dependency mismatch: '+row['path'])
    return actual


def verify_predecessor(report_path,archive_path,contract):
    report_path=Path(report_path).resolve();archive_path=Path(archive_path).resolve()
    if sha(report_path)!=contract['predecessor_return_report_sha256']:
        raise ValueError('predecessor RETURN_REPORT sha256 mismatch')
    if sha(archive_path)!=contract['predecessor_return_archive_sha256']:
        raise ValueError('predecessor RETURN archive sha256 mismatch')
    report=json.loads(report_path.read_text())
    if report.get('status')!=contract['predecessor_status']:
        raise ValueError('unexpected predecessor status')
    if report.get('execution_head')!=contract['upstream_tp2c_commit'] or report.get('execution_tree')!=contract['upstream_tp2c_tree']:
        raise ValueError('unexpected predecessor Git identity')
    counts=report.get('new_tests',{}).get('counts',{})
    if report.get('new_tests',{}).get('returncode')!=0 or counts!={'tests':8,'failures':0,'errors':0,'skipped':0}:
        raise ValueError('unexpected predecessor test evidence')
    if report.get('full13_static_geometry_coverage') is not True or report.get('full13_z_samples_a0')!=contract['reference_sample_z_a0']:
        raise ValueError('unexpected predecessor full13 static geometry coverage')
    ceilings={'continuous_trajectory_error_bound':False,'capture_execution_allowed':False,'production_admission':'HOLD',
              'all_bound':'OPEN','b_grid':'NO_GO','original_capture_gap_resolved':False}
    for key,value in ceilings.items():
        if report.get(key)!=value:raise ValueError('predecessor claim ceiling mismatch: '+key)
    with zipfile.ZipFile(archive_path) as zf:
        if zf.testzip() is not None:raise ValueError('predecessor archive CRC/integrity failure')
        if 'RETURN_REPORT.json' not in set(zf.namelist()):raise ValueError('predecessor archive lacks RETURN_REPORT.json')
        if hashlib.sha256(zf.read('RETURN_REPORT.json')).hexdigest()!=contract['predecessor_return_report_sha256']:
            raise ValueError('predecessor archive/report bytes disagree')
    return {'status':report['status'],'execution_head':report['execution_head'],'execution_tree':report['execution_tree'],
            'return_report_sha256':sha(report_path),'return_archive_sha256':sha(archive_path),
            'new_tests':report['new_tests'],'full13_static_geometry_coverage':True}


def run_new_tests(out):
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTEST_DISABLE_PLUGIN_AUTOLOAD='1',
             OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1')
    xml=Path(out)/'tests.xml';stdout=Path(out)/'tests.stdout';stderr=Path(out)/'tests.stderr'
    cmd=[sys.executable,'-m','pytest','-q','-p','no:cacheprovider',str(HERE/'tests'),'--junitxml='+str(xml)]
    with stdout.open('x') as so,stderr.open('x') as se:
        p=subprocess.run(cmd,stdout=so,stderr=se,env=env,timeout=180)
    counts={k:0 for k in ('tests','failures','errors','skipped')}
    if xml.exists():
        for suite in ET.parse(xml).getroot().iter('testsuite'):
            for key in counts:counts[key]+=int(suite.attrib.get(key,0))
    return {**counts,'returncode':p.returncode,'command':cmd}


def status_for_phase(phase):
    return {'preflight':'IDENTITY_OR_INPUT_BLOCKED','new_tests':'NEW_TESTS_FAILED',
            'metric_connection':'METRIC_CONNECTION_FAILED','reference_transport':'REFERENCE_TRANSPORT_FAILED',
            'candidate_transport':'TEMPORAL_REFINEMENT_UNRESOLVED',
            'operator_qualification':'RUNTIME_OPERATOR_QUALIFICATION_FAILED'}.get(phase,'EXECUTION_OR_ENVIRONMENT_BLOCKED')


class TP2DFailure(RuntimeError):
    def __init__(self,phase,message):super().__init__(message);self.phase=phase


def _progress(out,phase,**extra):
    row={'elapsed_seconds':time.monotonic()-_progress.started,'phase':phase,**extra}
    append_jsonl(Path(out)/'PROGRESS.jsonl',row);print(json.dumps(row,allow_nan=False),flush=True)
_progress.started=time.monotonic()


def execute_confirmatory(contract,out,analytic_build,predecessor,resume_from,progress):
    import numpy as np
    from bass_foundations.radial_basis import RadialSpec,atomic_bank
    from bass_foundations.two_center import Trajectory,symmetric_channels
    from cr_repro.observables import projectile_speed_au
    from exact_cross import MomentKernel
    from assemble import assemble
    from runtime import save_bank,load_bank
    from reference_transport import find_target_1s,normalize_metric_state,run_reference
    from metric_transport import run_candidate,phase_aligned_metric_distance
    from qualified_provider import ResolutionQualifiedProvider,restore_query_store
    from analytic_adapter import AnalyticEvaluator
    from transport_policy import metric_derivative_residual,assess_temporal_pair

    out=Path(out);analytic_dir=str(Path(analytic_build).resolve())
    kernel=MomentKernel(analytic_dir);analytic=kernel.receipt
    if analytic.get('source_sha256')!=contract['analytic_source_sha256']:raise ValueError('analytic source sha256 mismatch')
    if analytic.get('library_sha256')!=contract['analytic_library_sha256']:raise ValueError('analytic library sha256 mismatch')
    if contract.get('runtime_phase_budget') is not None:raise ValueError('TP2D runtime provider must not use phase-budget candidate semantics')
    if contract.get('operator_interpolation_used') is not False:raise ValueError('operator interpolation is outside TP2D scope')
    if contract.get('reference_solver',{}).get('method')!='DOP853':raise ValueError('unexpected reference solver')

    if resume_from:
        source=Path(resume_from).resolve();bank,basis_record=load_bank(source)
        copy_new(source/'BASIS.json',out/'BASIS.json');copy_new(source/'BASIS.npz',out/'BASIS.npz')
    else:
        bank=atomic_bank(RadialSpec(**contract['radial_spec']));basis_record=save_bank(out,bank)
    channels=symmetric_channels(bank);v=projectile_speed_au(contract['energy_keV_per_u'])
    trajectory=Trajectory(((0.,0.,0.),(contract['b_a0'],0.,0.)),((0.,0.,0.),(0.,0.,v)))
    physics_identity={'schema':'BASS_TP2D_RUNTIME_PHYSICS_IDENTITY_V1','contract_sha256':sha(HERE/'CONTRACT.json'),
        'basis_identity':basis_record['identity'],'analytic_source_sha256':analytic['source_sha256'],
        'analytic_library_sha256':analytic['library_sha256'],'same_center_order':contract['same_center_order'],
        'qualification_sector':'full','predecessor_return_report_sha256':predecessor['return_report_sha256'],
        'predecessor_return_archive_sha256':predecessor['return_archive_sha256'],
        'source_manifest_sha256':sha(HERE/'SOURCE_MANIFEST.json'),'dependency_pins_sha256':sha(HERE/'DEPENDENCY_PINS.json')}
    context={'contract':contract,'physics_identity':physics_identity};context_id=digest(context)
    restored=0
    if resume_from:
        previous=json.loads((Path(resume_from)/'SCIENCE_CONTEXT.json').read_text())
        if previous.get('context')!=context or previous.get('context_id')!=context_id:
            raise ValueError('resume context differs; no automatic cache migration')
        restored=restore_query_store(resume_from,out,context_id)
    write_new(out/'SCIENCE_CONTEXT.json',{'context':context,'context_id':context_id,'restored_queries':restored})

    evaluator=AnalyticEvaluator(assemble,trajectory=trajectory,channels=channels,kernel=kernel)
    def on_qualified(row):
        n=int(row['unique_runtime_queries'])
        if n<=5 or n%10==0:
            progress('operator_qualification',event='runtime_query_qualified',**{k:v for k,v in row.items() if k!='event'})
    provider=ResolutionQualifiedProvider(evaluate=evaluator,resolutions=contract['runtime_reference_resolutions'],
        screens=contract['screens'],context_id=context_id,out_dir=out,
        max_unique_queries=contract['max_unique_runtime_queries'],on_qualified=on_qualified)

    eps_t=contract['epsilon_z_a0']/v;metric_rows=[]
    progress('metric_connection',event='start',restored_queries=restored)
    for z in contract['metric_sentinel_z_a0']:
        row=metric_derivative_residual(provider,z/v,eps_t)
        scalar={'z_a0':float(z),'t_ta':float(z/v),'epsilon_t':float(eps_t),'relative_residual':float(row['relative_residual'])}
        metric_rows.append(scalar);progress('metric_connection',event='sentinel_complete',**scalar)
        if scalar['relative_residual']>contract['screens']['metric_derivative_relative_max']:
            raise TP2DFailure('metric_connection','metric derivative screen failed at z='+str(z))
    write_new(out/'METRIC_CONNECTION.json',metric_rows)

    t0=contract['z_initial_a0']/v;tf=contract['z_final_a0']/v
    s0=provider.at(t0);idx=find_target_1s(channels);c0=np.zeros(len(channels),complex);c0[idx]=1.
    c0=normalize_metric_state(c0,s0.S)
    sample_times=np.asarray([z/v for z in contract['reference_sample_z_a0']],float)
    progress('reference_transport',event='start',unique_runtime_queries=provider.unique_query_count)
    try:
        rcfg=contract['reference_solver']
        ref=run_reference(provider,channels,t0,tf,c0=c0,rtol=rcfg['rtol'],atol=rcfg['atol'],sample_times=sample_times)
    except (ResolutionQualificationError,OperatorQueryBudgetExceeded):raise
    except BaseException as e:raise TP2DFailure('reference_transport',str(e)) from e
    np.savez_compressed(out/'REFERENCE_STATES.npz',times=ref.times,states=ref.states,initial_state=ref.initial_state,
                        final_state=ref.final_state,norm_history=ref.norm_history)
    ref_receipt={'method':ref.method,'rtol':ref.rtol,'atol':ref.atol,'nfev':ref.nfev,'max_norm_drift':ref.max_norm_drift,
                 'unique_runtime_queries_after':provider.unique_query_count,'raw_operator_evaluations_after':provider.raw_operator_evaluation_count}
    write_new(out/'REFERENCE_RECEIPT.json',ref_receipt);progress('reference_transport',event='complete',**ref_receipt)
    if ref.max_norm_drift>contract['screens']['reference_norm_drift_max']:
        raise TP2DFailure('reference_transport','reference weighted norm drift screen failed')

    Sf=provider.at(tf).S;previous=None;attempts=[];selected=None
    progress('candidate_transport',event='start',step_counts=contract['candidate_step_counts'])
    for n in contract['candidate_step_counts']:
        try:r=run_candidate(provider,c0,t0,tf,int(n))
        except (ResolutionQualificationError,OperatorQueryBudgetExceeded):raise
        except BaseException as e:raise TP2DFailure('candidate_transport',f'nstep={n}: {e}') from e
        np.savez_compressed(out/f'CANDIDATE_N{n}.npz',initial_state=r.initial_state,final_state=r.final_state,norm_history=r.norm_history)
        crec={'nstep':int(n),'dt':float(r.dt),'max_norm_drift':float(r.max_norm_drift),'max_generator_defect':float(r.max_generator_defect),
              'unique_runtime_queries_after':provider.unique_query_count,'raw_operator_evaluations_after':provider.raw_operator_evaluation_count}
        write_new(out/f'CANDIDATE_N{n}.json',crec);progress('candidate_transport',event='candidate_complete',**crec)
        if previous is not None:
            pair=assess_temporal_pair(previous,r,ref.final_state,Sf,phase_aligned_metric_distance,contract['screens'])
            attempts.append(pair);write_new(out/f'TEMPORAL_PAIR_N{previous.nstep}_N{r.nstep}.json',pair)
            progress('candidate_transport',event='temporal_pair_assessed',**pair)
            if pair['qualified']:
                selected={'result':r,'receipt':pair};break
        previous=r
    if selected is None:raise TP2DFailure('candidate_transport','finite candidate temporal ladder exhausted without qualification')
    temporal={'status':'TEMPORAL_REFINEMENT_QUALIFIED','selected_nstep':selected['result'].nstep,
              'selected_pair':selected['receipt'],'attempts':attempts}
    write_new(out/'TEMPORAL_QUALIFICATION.json',temporal)
    audit=provider.audit_summary();write_new(out/'PROVIDER_AUDIT.json',audit)
    if not audit['all_runtime_operator_queries_qualified']:
        raise TP2DFailure('operator_qualification','not every runtime operator query is qualified')
    return {'status':'TP2D_RUNTIME_SELF_QUALIFIED_FULL_WINDOW_TRANSPORT_PASS','z_initial_a0':contract['z_initial_a0'],
            'z_final_a0':contract['z_final_a0'],'channel_count':len(channels),'metric_connection':metric_rows,
            'reference':ref_receipt,'temporal_qualification':temporal,'provider_audit':audit,
            'all_runtime_operator_queries_qualified':True,'full_window_transport_qualified':True,
            'continuous_global_supremum_bound':False,'continuous_trajectory_error_bound':False,
            'capture_execution_allowed':False,'restored_queries':restored}


def finish(out,report):
    out=Path(out);write_new(out/'RETURN_REPORT.json',report)
    files={str(p.relative_to(out)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(out.rglob('*')) if p.is_file()}
    write_new(out/'MANIFEST.json',files);archive=out.with_name(out.name+'_RETURN.zip')
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(out.rglob('*')):
            if p.is_file():z.write(p,str(p.relative_to(out)))
    return archive


def base_report():
    return {'schema':'BASS_TP2D_RUNTIME_SELF_QUALIFIED_FULL_WINDOW_RETURN_V1','status':'IN_PROGRESS',
        'scope':'18_CHANNEL_Z_MINUS12_TO_PLUS12_TRANSPORT_RUNTIME_QUERIES_SELF_QUALIFIED_NO_CAPTURE',
        'all_runtime_operator_queries_qualified':False,'full_window_transport_qualified':False,
        'operator_interpolation_used':False,'continuous_trajectory_error_bound':False,'continuous_global_supremum_bound':False,
        'capture_execution_allowed':False,'production_admission':'HOLD','all_bound':'OPEN','b_grid':'NO_GO',
        'original_capture_gap_resolved':False,'old_test_suite_reexecuted':False,'legacy_ring_task_imported':False,
        'capture_run_performed':False,'gpu_run':False}


def run_cli(argv=None,confirmatory_fn=execute_confirmatory):
    args=build_parser().parse_args(argv);out=Path(args.out).resolve();archive=out.with_name(out.name+'_RETURN.zip')
    if out.exists() or archive.exists():
        print('OUTPUT_EXISTS: choose a fresh output path; nothing overwritten',file=sys.stderr);return 3
    out.mkdir(parents=True);_progress.started=time.monotonic();report=base_report();phase='preflight';code=0
    try:
        contract=json.loads((HERE/'CONTRACT.json').read_text());head,tree=git_identity();report.update(execution_head=head,execution_tree=tree)
        if args.expected_commit and head!=args.expected_commit:raise ValueError('execution commit identity mismatch')
        verify_ancestry(contract['upstream_tp2c_commit'],head)
        sources=verify_sources();predecessor=verify_predecessor(args.predecessor_report,args.predecessor_archive,contract)
        report['predecessor']=predecessor
        write_new(out/'INTAKE.json',{'contract':contract,'execution_head':head,'execution_tree':tree,'source_hashes':sources,'predecessor':predecessor})
        phase='new_tests';_progress(out,phase,event='start',scope='tp2d_new_tests_only')
        tests=run_new_tests(out);report['new_tests']=tests
        _progress(out,phase,event='complete',counts={k:tests[k] for k in ('tests','failures','errors','skipped','returncode')})
        if tests['returncode'] or not tests['tests'] or tests['failures'] or tests['errors'] or tests['skipped']:
            raise TP2DFailure('new_tests','new TP2D tests did not all pass without skips')
        phase='science';science=confirmatory_fn(contract,out,args.analytic_build,predecessor,args.resume_from,lambda ph,**kw:_progress(out,ph,**kw))
        report['tp2d']=science;report['status']=science['status']
        for key in ('all_runtime_operator_queries_qualified','full_window_transport_qualified','continuous_global_supremum_bound','continuous_trajectory_error_bound'):
            report[key]=science[key]
    except OperatorQueryBudgetExceeded as e:
        report['status']='OPERATOR_QUERY_BUDGET_EXHAUSTED';code=2
        report['first_failure']={'phase':'operator_qualification','type':type(e).__name__,'message':str(e)}
        (out/'failure.traceback.txt').write_text(traceback.format_exc())
    except ResolutionQualificationError as e:
        report['status']='RUNTIME_OPERATOR_QUALIFICATION_FAILED';code=2
        report['first_failure']={'phase':'operator_qualification','type':type(e).__name__,'message':str(e)}
        (out/'failure.traceback.txt').write_text(traceback.format_exc())
    except TP2DFailure as e:
        report['status']=status_for_phase(e.phase);code=3 if e.phase=='new_tests' else 2
        report['first_failure']={'phase':e.phase,'type':type(e).__name__,'message':str(e)}
        (out/'failure.traceback.txt').write_text(traceback.format_exc())
    except KeyboardInterrupt:
        report['status']='INTERRUPTED';code=130;report['first_failure']={'phase':phase,'type':'KeyboardInterrupt','message':'interrupted'}
        (out/'failure.traceback.txt').write_text(traceback.format_exc())
    except (ImportError,ModuleNotFoundError) as e:
        report['status']='ENVIRONMENT_BLOCKED';code=3;report['first_failure']={'phase':phase,'type':type(e).__name__,'message':str(e)}
        (out/'failure.traceback.txt').write_text(traceback.format_exc())
    except BaseException as e:
        report['status']=status_for_phase(phase);code=3;report['first_failure']={'phase':phase,'type':type(e).__name__,'message':str(e)}
        (out/'failure.traceback.txt').write_text(traceback.format_exc())
    report['wall_seconds']=time.monotonic()-_progress.started;finish(out,report)
    print(json.dumps({'status':report['status'],'report':str(out/'RETURN_REPORT.json'),'archive':str(archive),
                      'capture_execution_allowed':False},indent=2),flush=True)
    return code


def main():return run_cli()
if __name__=='__main__':raise SystemExit(main())
