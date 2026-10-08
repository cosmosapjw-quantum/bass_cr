#!/usr/bin/env python3
"""Test-only entry point: fixed commands, fresh evidence, no code or gate repair."""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import signal
import subprocess
import sys
import time
import uuid
import xml.etree.ElementTree as ET
import zipfile


def write_new(path,value):
    with Path(path).open('x') as f:json.dump(value,f,indent=2,allow_nan=False);f.write('\n')


def prepare_output(path):
    p=Path(path).resolve();p.mkdir(parents=True,exist_ok=False);return p


def verify_sources(root):
    root=Path(root).resolve();data=json.loads((root/'SOURCE_MANIFEST.json').read_text());files=data.get('files')
    if not isinstance(files,dict) or not files:raise ValueError('nonempty source manifest required')
    for name,sha in files.items():
        path=root/name
        if Path(name).is_absolute() or '..' in Path(name).parts or not path.resolve().is_relative_to(root):
            raise ValueError('source manifest path escape')
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=sha:
            raise ValueError('source identity mismatch: '+name)
    actual={str(p.relative_to(root)) for p in root.rglob('*.py') if '__pycache__' not in p.parts and '.venv' not in p.parts}
    if actual-set(files):raise ValueError('undeclared Python source: '+', '.join(sorted(actual-set(files))))
    return len(files)


def run_step(name,argv,cwd,out,*,timeout=300,env=None):
    out=Path(out);tic=time.perf_counter();status='FAILED';code=126
    # Logs exist while the process runs, so a lost session retains partial output.
    with (out/f'{name}.stdout.txt').open('x') as stdout, (out/f'{name}.stderr.txt').open('x') as stderr:
        try:
            proc=subprocess.Popen(argv,cwd=cwd,env=env,stdout=stdout,stderr=stderr,start_new_session=os.name=='posix')
            try:
                code=proc.wait(timeout=timeout);status='PASSED' if code==0 else 'FAILED'
            except (subprocess.TimeoutExpired,KeyboardInterrupt) as e:
                status='TIMEOUT' if isinstance(e,subprocess.TimeoutExpired) else 'INTERRUPTED'
                code=124 if status=='TIMEOUT' else 130
                if os.name=='posix':os.killpg(proc.pid,signal.SIGTERM)
                else:proc.terminate()
                try:proc.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    if os.name=='posix':os.killpg(proc.pid,signal.SIGKILL)
                    else:proc.kill()
                    proc.wait()
        except OSError as e:
            code=126;status='ENVIRONMENT_BLOCKED';stderr.write(repr(e))
    result={'step':name,'argv':argv,'cwd':str(cwd),'returncode':code,'status':status,'seconds':time.perf_counter()-tic}
    write_new(out/f'{name}.receipt.json',result)
    return result


def junit_counts(path):
    tree=ET.parse(path);root=tree.getroot()
    nodes=[root] if root.tag=='testsuite' else list(root.findall('testsuite'))
    return {key:sum(int(n.get(key,'0')) for n in nodes) for key in ('tests','failures','errors','skipped')}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile',choices=['package','local'],default='local')
    parser.add_argument('--out');parser.add_argument('--expected-commit')
    a=parser.parse_args(argv);root=Path(__file__).resolve().parent;repo=root.parents[1]
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'_'+uuid.uuid4().hex[:8]
    out=prepare_output(a.out or repo/'runs/fnd_validation'/stamp)
    result={'schema':'BASS_FND_TEST_ONLY_RETURN_V1','profile':a.profile,'output':str(out),'steps':[],
      'production_admission':'HOLD','all_bound':'OPEN','b_grid':'NO_GO','capture_gap_resolved':False,
      'code_changes_by_runner':False,'collision_runs':0,'gpu_required_for_new_package':False,
      'legacy_full_suite':'NOT_REQUESTED' if a.profile=='package' else 'NOT_RUN',
      'scope':'LOCAL_REPRODUCTION_OF_FIXED_TEST_CONTRACT_NOT_PRODUCTION_ADMISSION'}
    stage='INTAKE'
    try:
        result['source_files_verified']=verify_sources(root)
        contract=json.loads((root/'VALIDATION_CONTRACT.json').read_text())
        if a.profile=='local' and not a.expected_commit:raise ValueError('local profile requires --expected-commit')
        if a.expected_commit:
            if len(a.expected_commit)!=40 or any(c not in '0123456789abcdef' for c in a.expected_commit):raise ValueError('expected commit must be full lowercase SHA')
            head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()
            if head!=a.expected_commit:raise ValueError('checkout commit identity mismatch')
            result['commit']=head
            frozen=hashlib.sha256()
            for f in sorted((repo/'cr_repro').glob('*.py')):
                frozen.update(f.name.encode());frozen.update(hashlib.sha256(f.read_bytes()).digest())
            result['legacy_source_digest']=frozen.hexdigest()
            if frozen.hexdigest()!='581ff84930bb862efafdfec5d39d5b25aebf9297ce7ce45f833a5abe125b2a5b':raise ValueError('frozen historical source identity mismatch')
            result['git_status_before']=subprocess.check_output(['git','status','--short'],cwd=repo,text=True)
        stage='ENVIRONMENT'
        env=dict(os.environ,PYTHONPATH=str(root/'src'),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',
                 MKL_NUM_THREADS='1',PYTHONHASHSEED='0',PYTHONDONTWRITEBYTECODE='1',PYTEST_DISABLE_PLUGIN_AUTOLOAD='1')
        result['environment']={'python':sys.version,'executable':sys.executable,'platform':platform.platform(),
          'packages':{name:importlib.metadata.version(name) for name in ('numpy','scipy','mpmath','pytest')}}
        write_new(out/'INTAKE.json',result)
        steps=[('foundation_tests',[sys.executable,'-m','pytest','-q','-ra','tests',f'--junitxml={out / "foundation.xml"}'],root,contract['test_timeout_seconds']),
               ('operator_cases',[sys.executable,'-m','bass_foundations.validation_cases','--out',str(out/'operator_cases')],root,contract['case_timeout_seconds'])]
        if a.profile=='local':
            steps.append(('legacy_tests',[sys.executable,'-m','pytest','-q','-ra','tests',f'--junitxml={out / "legacy.xml"}'],repo,contract['legacy_timeout_seconds']))
        failed=False
        for name,cmd,cwd,timeout in steps:
            stage=name
            step_env=env.copy()
            if name=='legacy_tests':step_env['PYTHONPATH']=str(repo)
            r=run_step(name,cmd,cwd,out,timeout=timeout,env=step_env)
            xml=out/('legacy.xml' if name=='legacy_tests' else 'foundation.xml')
            if name.endswith('tests') and xml.is_file():
                r['counts']=junit_counts(xml)
                if name=='foundation_tests' and (r['counts']['tests']<contract['minimum_package_tests'] or r['counts']['skipped']):
                    r['status']='INCOMPLETE_TEST_COVERAGE';r['returncode']=3
            result['steps'].append(r)
            if name=='legacy_tests':result['legacy_full_suite']=r['status']
            write_new(out/f'CHECKPOINT_{len(result["steps"]):02d}.json',result)
            print(json.dumps({'step':name,'status':r['status'],'returncode':r['returncode']}),flush=True)
            if r['returncode']!=0:failed=True;break
        result['status']='FAILED_RETAINED' if failed else 'PASS_TESTS_ONLY'
        if not failed and any(s.get('counts',{}).get('skipped',0) for s in result['steps']):result['status']='PASS_TESTS_WITH_EXPLICIT_SKIPS'
        stage='POSTRUN_IDENTITY'
        result['source_files_verified_after']=verify_sources(root)
        code=1 if failed else 0
    except Exception as e:
        result['status']=stage.upper()+'_BLOCKED';result['failure']={'stage':stage,'type':type(e).__name__,'message':str(e)};code=2
    write_new(out/'RETURN_REPORT.json',result)
    files={str(p.relative_to(out)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.rglob('*')) if p.is_file()}
    write_new(out/'MANIFEST.json',{'files':files,'self_excluded':True})
    archive=out.with_name(out.name+'_RETURN.zip')
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(out.rglob('*')):
            if p.is_file():z.write(p,str(p.relative_to(out)))
    print(json.dumps({'status':result['status'],'report':str(out/'RETURN_REPORT.json'),'archive':str(archive),'production_admission':'HOLD'}),flush=True)
    return code

if __name__=='__main__':raise SystemExit(main())
