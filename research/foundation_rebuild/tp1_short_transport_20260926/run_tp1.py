#!/usr/bin/env python3
"""TP1 short-window metric transport runner. Capture and GPU paths are absent by design."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import traceback
import xml.etree.ElementTree as ET
import zipfile

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_new(path,value):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8') as f:
        json.dump(value,f,indent=2,allow_nan=False)
        f.write('\n');f.flush();os.fsync(f.fileno())


def append_jsonl(path,value):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('a',encoding='utf-8') as f:
        f.write(json.dumps(value,allow_nan=False,separators=(',',':'))+'\n')
        f.flush();os.fsync(f.fileno())


def build_parser():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',required=True)
    p.add_argument('--expected-commit')
    return p


def git_identity():
    try:
        head=subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True,stderr=subprocess.DEVNULL).strip()
        tree=subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD^{tree}'],text=True,stderr=subprocess.DEVNULL).strip()
        return head,tree
    except (subprocess.CalledProcessError,FileNotFoundError):
        return None,None


def verify_sources(manifest_path=None,dependency_path=None):
    manifest_path=Path(manifest_path) if manifest_path is not None else HERE/'SOURCE_MANIFEST.json'
    if not manifest_path.exists():
        raise ValueError('source manifest missing')
    manifest=json.loads(manifest_path.read_text())
    actual={}
    for rel,expected in manifest.get('files',{}).items():
        p=HERE/rel
        if not p.is_file(): raise ValueError('source mismatch: missing '+rel)
        actual[rel]=sha(p)
        if actual[rel]!=expected: raise ValueError('source mismatch: '+rel)
    dep_path=(Path(dependency_path) if dependency_path is not None else HERE/'DEPENDENCY_PINS.json')
    if dep_path.exists():
        deps=json.loads(dep_path.read_text())
        for row in deps.get('files',[]):
            p=REPO/row['path']
            if not p.is_file(): raise ValueError('dependency mismatch: missing '+row['path'])
            digest=sha(p);actual['dependency:'+row['path']]=digest
            if digest!=row['sha256']: raise ValueError('dependency mismatch: '+row['path'])
    return actual


def run_new_tests(out):
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTEST_DISABLE_PLUGIN_AUTOLOAD='1',
             OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
    xml=Path(out)/'tests.xml';stdout=Path(out)/'tests.stdout';stderr=Path(out)/'tests.stderr'
    cmd=[sys.executable,'-m','pytest','-q','-p','no:cacheprovider',str(HERE/'tests'),'--junitxml='+str(xml)]
    with stdout.open('x') as so,stderr.open('x') as se:
        p=subprocess.run(cmd,stdout=so,stderr=se,env=env,timeout=300)
    counts=dict.fromkeys(['tests','failures','errors','skipped'],0)
    if xml.exists():
        for suite in ET.parse(xml).getroot().iter('testsuite'):
            for key in counts: counts[key]+=int(suite.attrib.get(key,0))
    counts['returncode']=p.returncode;counts['command']=cmd
    return counts


def status_for_phase(phase):
    return {
        'operator_diagnostics':'OPERATOR_TIME_NODE_FAILED',
        'metric_connection':'METRIC_CONNECTION_FAILED',
        'reference_transport':'REFERENCE_TRANSPORT_FAILED',
        'candidate_transport':'CANDIDATE_TRANSPORT_FAILED',
        'temporal_refinement':'TEMPORAL_REFINEMENT_FAILED',
        'preflight':'IDENTITY_OR_INPUT_BLOCKED',
        'new_tests':'IDENTITY_OR_INPUT_BLOCKED',
    }.get(phase,'IDENTITY_OR_INPUT_BLOCKED')


class TP1Failure(RuntimeError):
    def __init__(self,phase,message):
        super().__init__(message);self.phase=phase


def _progress(out,phase,**extra):
    row={'phase':phase,**extra}
    append_jsonl(Path(out)/'PROGRESS.jsonl',row)
    print(json.dumps(row,allow_nan=False),flush=True)


def execute_confirmatory(contract,out,progress):
    import numpy as np
    from bass_foundations.radial_basis import RadialSpec,atomic_bank
    from bass_foundations.two_center import Trajectory,symmetric_channels
    from cr_repro.observables import projectile_speed_au
    from operator_provider import OperatorProvider,metric_derivative_residual
    from reference_transport import find_target_1s,normalize_metric_state,run_reference
    from metric_transport import run_candidate,phase_aligned_metric_distance

    out=Path(out)
    v=projectile_speed_au(contract['energy_keV_per_u'])
    t0=contract['z_initial_a0']/v;tf=contract['z_final_a0']/v
    spec=RadialSpec(**contract['radial_spec'])
    channels=symmetric_channels(atomic_bank(spec))
    tr=Trajectory(((0.,0.,0.),(contract['b_a0'],0.,0.)),((0.,0.,0.),(0.,0.,v)))
    provider=OperatorProvider(tr,channels,same_order=contract['same_center_order'],cross_order=contract['cross_order'],
                              expected_channel_records=[c.record() for c in channels],
                              hermiticity_relative_max=contract['screens']['operator_hermiticity_relative_max'],
                              metric_min_ratio=contract['screens']['metric_min_ratio'])
    diagnostics=[]
    progress('operator_diagnostics',event='start')
    try:
        for z in contract['diagnostic_z_a0']:
            t=z/v;s=provider.at(t)
            diagnostics.append({'z_a0':z,'t_ta':t,
                'S_hermiticity_relative':s.diagnostics['S_hermiticity_relative'],
                'H_hermiticity_relative':s.diagnostics['H_hermiticity_relative'],
                'metric_min':s.diagnostics['metric_min'],'metric_max':s.diagnostics['metric_max'],
                'metric_ratio':s.diagnostics['metric_ratio']})
            progress('operator_diagnostics',event='node_complete',z_a0=z,evaluations=provider.evaluation_count)
    except BaseException as e:
        raise TP1Failure('operator_diagnostics',str(e)) from e
    write_new(out/'OPERATOR_DIAGNOSTICS.json',diagnostics)

    progress('metric_connection',event='start')
    eps_t=contract['epsilon_z_a0']/v
    metric_rows=[]
    for z in contract['diagnostic_z_a0']:
        try:
            row=metric_derivative_residual(provider,z/v,eps_t)
        except BaseException as e:
            raise TP1Failure('metric_connection',str(e)) from e
        scalar={'z_a0':z,'t_ta':z/v,'epsilon_t':eps_t,'relative_residual':row['relative_residual']}
        metric_rows.append(scalar)
        progress('metric_connection',event='node_complete',**scalar,evaluations=provider.evaluation_count)
        if scalar['relative_residual']>contract['screens']['metric_derivative_relative_max']:
            raise TP1Failure('metric_connection','metric derivative screen failed at z='+str(z))
    write_new(out/'METRIC_CONNECTION.json',metric_rows)

    idx=find_target_1s(channels);c0=np.zeros(len(channels),complex);c0[idx]=1.
    c0=normalize_metric_state(c0,provider.at(t0).S)
    sample_times=np.array([z/v for z in contract['diagnostic_z_a0']],float)
    progress('reference_transport',event='start',evaluations=provider.evaluation_count)
    try:
        rcfg=contract['reference_solver']
        ref=run_reference(provider,channels,t0,tf,c0=c0,rtol=rcfg['rtol'],atol=rcfg['atol'],sample_times=sample_times)
    except BaseException as e:
        raise TP1Failure('reference_transport',str(e)) from e
    np.savez_compressed(out/'REFERENCE_STATES.npz',times=ref.times,states=ref.states,
                        initial_state=ref.initial_state,final_state=ref.final_state,norm_history=ref.norm_history)
    ref_receipt={'method':ref.method,'rtol':ref.rtol,'atol':ref.atol,'nfev':ref.nfev,
                 'max_norm_drift':ref.max_norm_drift,'operator_evaluations_after':provider.evaluation_count}
    write_new(out/'REFERENCE_RECEIPT.json',ref_receipt)
    progress('reference_transport',event='complete',**ref_receipt)
    if ref.max_norm_drift>contract['screens']['reference_norm_drift_max']:
        raise TP1Failure('reference_transport','reference weighted norm drift screen failed')

    progress('candidate_transport',event='start',evaluations=provider.evaluation_count)
    candidates={}
    for n in contract['candidate_step_counts']:
        try:
            r=run_candidate(provider,c0,t0,tf,int(n))
        except BaseException as e:
            raise TP1Failure('candidate_transport',f'nstep={n}: {e}') from e
        np.savez_compressed(out/f'CANDIDATE_N{n}.npz',initial_state=r.initial_state,final_state=r.final_state,norm_history=r.norm_history)
        candidates[int(n)]=r
        row={'nstep':int(n),'dt':r.dt,'max_norm_drift':r.max_norm_drift,
             'max_generator_defect':r.max_generator_defect,'operator_evaluations_after':provider.evaluation_count}
        write_new(out/f'CANDIDATE_N{n}.json',row)
        progress('candidate_transport',event='candidate_complete',**row)
        if r.max_norm_drift>contract['screens']['candidate_norm_drift_max']:
            raise TP1Failure('candidate_transport',f'nstep={n} weighted norm drift screen failed')

    Sf=provider.at(tf).S
    final64=candidates[64].final_state;final32=candidates[32].final_state
    cref=ref.final_state
    dref=phase_aligned_metric_distance(cref,final64,Sf)
    d3264=phase_aligned_metric_distance(final32,final64,Sf)
    comparison={'candidate64_vs_reference_Sf_distance':dref,
                'candidate32_vs_64_Sf_distance':d3264,
                'operator_evaluation_count':provider.evaluation_count}
    write_new(out/'FINAL_COMPARISON.json',comparison)
    if dref>contract['screens']['candidate_reference_metric_distance_max']:
        raise TP1Failure('candidate_transport','candidate/reference final-state screen failed')
    progress('temporal_refinement',event='comparison',**comparison)
    if d3264>contract['screens']['candidate_32_to_64_metric_distance_max']:
        raise TP1Failure('temporal_refinement','candidate 32->64 refinement screen failed')

    return {
        'status':'TP1_SHORT_TRANSPORT_PASS','channel_count':len(channels),
        'z_initial_a0':contract['z_initial_a0'],'z_final_a0':contract['z_final_a0'],
        'epsilon_z_a0':contract['epsilon_z_a0'],'operator_diagnostics':diagnostics,
        'metric_connection':metric_rows,'reference':ref_receipt,
        'candidates':{str(k):{'nstep':v.nstep,'dt':v.dt,'max_norm_drift':v.max_norm_drift,
                             'max_generator_defect':v.max_generator_defect} for k,v in candidates.items()},
        'comparison':comparison,'operator_evaluation_count':provider.evaluation_count,
    }


def finish(out,report):
    out=Path(out)
    write_new(out/'RETURN_REPORT.json',report)
    files=sorted(p for p in out.rglob('*') if p.is_file())
    manifest={str(p.relative_to(out)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in files}
    write_new(out/'MANIFEST.json',manifest)
    archive=out.with_name(out.name+'_RETURN.zip')
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(p for p in out.rglob('*') if p.is_file()): z.write(p,str(p.relative_to(out)))
    return archive


def run_cli(argv=None,confirmatory_fn=execute_confirmatory):
    args=build_parser().parse_args(argv)
    out=Path(args.out).resolve();archive=out.with_name(out.name+'_RETURN.zip')
    if out.exists() or archive.exists():
        print('OUTPUT_EXISTS: choose a fresh output path; nothing overwritten',file=sys.stderr)
        return 3
    out.mkdir(parents=True)
    contract=json.loads((HERE/'CONTRACT.json').read_text())
    report={'schema':'BASS_FND_TP1_SHORT_TRANSPORT_RETURN_V1','status':'IN_PROGRESS',
            'scope':'18_CHANNEL_Z_MINUS12_TO_MINUS10_TRANSPORT_NO_CAPTURE',
            'capture_execution_allowed':False,'production_admission':'HOLD','all_bound':'OPEN','b_grid':'NO_GO',
            'original_capture_gap_resolved':False,'gpu_run':False,'capture_run_performed':False}
    phase='preflight';code=0
    try:
        head,tree=git_identity();report.update(execution_head=head,execution_tree=tree)
        if args.expected_commit and head!=args.expected_commit:
            raise ValueError('execution commit identity mismatch')
        sources=verify_sources()
        write_new(out/'INTAKE.json',{'contract':contract,'source_hashes':sources,'execution_head':head,'execution_tree':tree})
        phase='new_tests';_progress(out,phase,event='start')
        tests=run_new_tests(out);report['new_tests']=tests
        _progress(out,phase,event='complete',counts={k:tests[k] for k in ['tests','failures','errors','skipped','returncode']})
        if tests['returncode'] or tests['failures'] or tests['errors'] or tests['skipped']:
            raise RuntimeError('new TP1 tests did not all pass without skips')
        phase='operator_diagnostics'
        science=confirmatory_fn(contract,out,lambda ph,**kw:_progress(out,ph,**kw))
        report['tp1']=science
        report['status']=science.get('status','TP1_SHORT_TRANSPORT_PASS')
    except TP1Failure as e:
        phase=e.phase;report['status']=status_for_phase(phase);code=2
        report['first_failure']={'phase':phase,'type':type(e).__name__,'message':str(e)}
        (out/'failure.traceback.txt').write_text(traceback.format_exc())
    except KeyboardInterrupt as e:
        report['status']='INTERRUPTED';code=130
        report['first_failure']={'phase':phase,'type':type(e).__name__,'message':'interrupted'}
        (out/'failure.traceback.txt').write_text(traceback.format_exc())
    except (ImportError,ModuleNotFoundError) as e:
        report['status']='ENVIRONMENT_BLOCKED';code=3
        report['first_failure']={'phase':phase,'type':type(e).__name__,'message':str(e)}
        (out/'failure.traceback.txt').write_text(traceback.format_exc())
    except BaseException as e:
        report['status']=status_for_phase(phase);code=3
        report['first_failure']={'phase':phase,'type':type(e).__name__,'message':str(e)}
        (out/'failure.traceback.txt').write_text(traceback.format_exc())
    finish(out,report)
    print(json.dumps({'status':report['status'],'out':str(out),'archive':str(archive),
                      'capture_execution_allowed':False},indent=2),flush=True)
    return code


def main(): return run_cli()
if __name__=='__main__': raise SystemExit(main())
