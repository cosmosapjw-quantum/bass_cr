#!/usr/bin/env python3
"""Frozen PHYS02G postprocess admission and one-child 90 second coordinator."""
import os
for _key in ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS','NUMEXPR_NUM_THREADS','OMP_MAX_ACTIVE_LEVELS'):
    os.environ[_key]='1'
import argparse
import hashlib
import io
import json
import pathlib
import platform
import signal
import stat
import subprocess
import sys
import time
import traceback
import uuid
import zipfile
STUDY=pathlib.Path(__file__).resolve().parents[1]
TASK='CR-PHYS02G-NCP-FRONTIER-ENVELOPE'
PINS={'state/SCIENTIFIC_CONTRACT.json':'517dd569f2e0d0857b37e33a5d90da6475978ab1a43374f3dfbe0323ffb35832',
      'state/VALIDATION_CONTRACT.json':'259d6964154cc190050761db092c9edd5499649867f822003db8afdfa42d9aba',
      'ncp/NCP_EXECUTION_CONTRACT.json':'06a06f865bba44ce93cc3bcf905cf95440de0978e87ee76529d2f440c6065856',
      'inputs/INPUT_IDENTITIES.json':'748076a5628c5a64ad4a057f96c58fd9b54da70dfef9d90e64823234c2df47c9',
      'inputs/F_BACKUP_DEPENDENCY.json':'984cb304788d9de7b89fd79d1bd1cf1daa57d12c5e63f5b1267a53743e22740f'}
CAP=512*1024*1024
REQUIRED_CODE=['src/moment_bounds.py','src/cached_analysis.py','src/frontier.py','ncp/postprocess_frontier.py']

def digest(raw):return hashlib.sha256(raw).hexdigest()
def utc():return time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
def parse(raw):return json.loads(raw)
def load(path):return parse(path.read_bytes())
def write(path,value):
    with pathlib.Path(path).open('x') as f:
        json.dump(value,f,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
def safe_name(name):
    p=pathlib.PurePosixPath(name)
    if not name or '\\' in name or p.is_absolute() or any(v in ('..','.') for v in p.parts) or p.as_posix()!=name:
        raise ValueError('UNSAFE_MEMBER '+name)
    return name

def safe_file(root,name):
    safe_name(name); p=root/name
    if any(v.is_symlink() for v in [p,*p.parents] if v.is_relative_to(root)) or not p.is_file() or not p.resolve().is_relative_to(root.resolve()):
        raise ValueError('UNSAFE_OR_MISSING_FILE '+name)
    return p

def identity(raw,item,name):
    if len(raw)!=item['bytes'] or digest(raw)!=item['sha256']:
        raise ValueError('IDENTITY_MISMATCH '+name)

def own_admission(study=STUDY):
    for name,pin in PINS.items():
        if digest(safe_file(study,name).read_bytes())!=pin:
            raise ValueError('FROZEN_G_CONTRACT_MISMATCH '+name)
    required=list(PINS)+REQUIRED_CODE
    mf=study/'FILE_MANIFEST.json'; rp=study/'review/INDEPENDENT_DECISION.json'
    if not mf.is_file() or not rp.is_file():
        return {'status':'WAITING_FOR_G_FINAL_MANIFEST_AND_REVIEW','contracts_verified':True}
    manifest=load(mf); root=study.parents[1];prefix=study.relative_to(root).as_posix()+'/'
    if manifest.get('schema')!='cr-phys02g-file-manifest.v1' or manifest.get('path_basis')!='repository-root':
        raise ValueError('G_MANIFEST_SCHEMA_MISMATCH')
    for name,item in manifest['files'].items():
        identity(safe_file(root,name).read_bytes(),item,name)
    if any(prefix+name not in manifest['files'] for name in required+['review/INDEPENDENT_DECISION.json','state/NEXT_DAG.json']):
        raise ValueError('G_MANIFEST_REQUIRED_CODE_COVERAGE_MISSING')
    review=load(rp)
    expected={'decision':'PASS_SCOPED','reviewer_role':'INDEPENDENT_ASTRA',
              'independent_of_implementation':True,'independent_of_candidate_design':True,'independent_of_acceptance':True,
              'scientific_contract_sha256':PINS['state/SCIENTIFIC_CONTRACT.json'],
              'validation_contract_sha256':PINS['state/VALIDATION_CONTRACT.json'],
              'ncp_contract_sha256':PINS['ncp/NCP_EXECUTION_CONTRACT.json'],
              'input_manifest_sha256':PINS['inputs/INPUT_IDENTITIES.json'],
              'dependency_manifest_sha256':PINS['inputs/F_BACKUP_DEPENDENCY.json']}
    if any(review.get(k)!=v for k,v in expected.items()):raise ValueError('G_REVIEW_SCOPE_OR_IDENTITY_MISMATCH')
    reviewed=review.get('reviewed_files',{})
    if set(required)-set(reviewed):raise ValueError('G_REVIEW_CODE_COVERAGE_MISSING')
    for name,item in reviewed.items():identity(safe_file(study,name).read_bytes(),item,name)
    dag=load(safe_file(study,'state/NEXT_DAG.json'))
    if dag.get('schema')!='cr-phys02g-next-dag.v1' or dag.get('scientific_contract_sha256')!=PINS['state/SCIENTIFIC_CONTRACT.json']:raise ValueError('G_DAG_IDENTITY_MISMATCH')
    matches=[row for row in dag.get('tasks',[]) if row.get('id')==TASK]
    if len(matches)!=1:raise ValueError('G_DAG_TASK_MEMBERSHIP_MISMATCH')
    task=matches[0]
    expected_task={'status':'WAITING_FOR_F_ACTUAL_RETURN','preparation_status':'PASS_SCOPED','consumed':False,
                   'max_postprocess_runs':1,'total_wall_s':90,'physical_G_calls':0,'linear_solve_calls':0,'pulse_calls':0,'expm_calls':0}
    if any(task.get(k)!=v for k,v in expected_task.items()):raise ValueError('G_DAG_PREPARATION_OR_BUDGET_MISMATCH')
    reference=task.get('independent_review',{})
    if reference.get('path')!='review/INDEPENDENT_DECISION.json' or reference.get('sha256')!=digest(rp.read_bytes()):raise ValueError('G_DAG_FINAL_REVIEW_BINDING_MISMATCH')
    return {'status':'PREPARED_SOURCE_ADMITTED','review_sha256':digest(rp.read_bytes()),'manifest_sha256':digest(mf.read_bytes()),'actual_F_review_required':True}

def verify_family(directory, study=STUDY):
    root=pathlib.Path(directory)
    if not root.is_absolute() or root.is_symlink() or not root.is_dir():raise ValueError('ABS_EXISTING_F_FAMILY_REQUIRED')
    root=root.resolve(); fm=load(safe_file(root,'RETURN_FAMILY_MANIFEST.json'))
    files=fm.get('files',{})
    actual=set()
    for p in root.rglob('*'):
        if p.is_symlink():raise ValueError('SYMLINK_FAMILY_FORBIDDEN')
        if p.is_file():actual.add(p.relative_to(root).as_posix())
    if actual!=set(files)|{'RETURN_FAMILY_MANIFEST.json'}:raise ValueError('F_FAMILY_MEMBERSHIP_MISMATCH')
    for name,item in files.items():identity(safe_file(root,name).read_bytes(),item,name)
    names=[n for n in files if n.endswith('.zip')]
    if len(names)!=1:raise ValueError('EXACTLY_ONE_F_NUMERICAL_ZIP_REQUIRED')
    archive=safe_file(root,names[0]);raw={}
    with zipfile.ZipFile(archive) as z:
        entries=z.infolist();members=[x.filename for x in entries]
        if len(members)!=len(set(members)):raise ValueError('DUPLICATE_ZIP_MEMBER')
        if sum(x.file_size for x in entries)>CAP:raise ValueError('ZIP_UNCOMPRESSED_CAP_EXCEEDED')
        for item in entries:
            safe_name(item.filename)
            if item.is_dir() or stat.S_ISLNK(item.external_attr>>16):raise ValueError('ZIP_DIRECTORY_OR_SYMLINK_FORBIDDEN')
        rm=parse(z.read('RETURN_MANIFEST.json'))
        if set(members)!=set(rm['files'])|{'RETURN_MANIFEST.json'}:raise ValueError('F_ZIP_MEMBERSHIP_MISMATCH')
        for name,item in rm['files'].items():
            raw[name]=z.read(name);identity(raw[name],item,name)
    ids=load(study/'inputs/INPUT_IDENTITIES.json')['files']
    for name,item in ids.items():identity(raw['source_unit/'+name],item,name)
    source_manifest=parse(raw['source_unit/FILE_MANIFEST.json'])
    if source_manifest.get('schema')!='cr-phys02f-file-manifest.v1' or source_manifest.get('path_basis')!='repository-root':raise ValueError('F_SOURCE_MANIFEST_SCHEMA_MISMATCH')
    prefix='research/cr_phys02f_20261011/'
    for name,item in source_manifest['files'].items():
        if not name.startswith(prefix):raise ValueError('F_SOURCE_MANIFEST_ROOT_MISMATCH')
        identity(raw['source_unit/'+name[len(prefix):]],item,name)
    fids=parse(raw['source_unit/inputs/INPUT_IDENTITIES.json'])['files']
    deps=rm.get('dependencies',{})
    if set(deps)!=set(fids):raise ValueError('F_DEPENDENCY_KEY_MEMBERSHIP_MISMATCH')
    for key,item in fids.items():
        dep=deps[key]
        if any(dep.get(k)!=item[k] for k in ('path','bytes','sha256')):raise ValueError('F_KNOWN_DEPENDENCY_POINTER_MISMATCH '+key)
        identity(raw[dep['archive_path']],item,key)
    verify_success(raw,root,files,rm)
    return {'directory':str(root),'zip_name':names[0],'zip_sha256':files[names[0]]['sha256'],
            'family_manifest_sha256':digest((root/'RETURN_FAMILY_MANIFEST.json').read_bytes()),
            'raw':raw,'manifest':rm,'f_inputs':fids,'scientific_approval':'NOT_CREATED_BY_METADATA_VERIFICATION'}

def verify_runtime(runtime):
    if (runtime.get('python'),runtime.get('numpy'),runtime.get('scipy'))!=('3.12.3','2.4.2','1.17.0') or not runtime.get('threadpools') or any(p.get('num_threads')!=1 for p in runtime['threadpools']):
        raise ValueError('EXACT_NUMERICAL_RUNTIME_REQUIRED')

def verify_success(raw,root,files,manifest):
    required=('WRAPPER_ACTUAL_EXIT.json','WRAPPER_COLLECTION_EXIT.json','WRAPPER_EXECUTE_EXIT.json','ACTUAL_EXIT.json','RUNTIME.json','stdout.log','stderr.log')
    if set(required)-set(files):raise ValueError('F_EXTERNAL_SIDECARS_MISSING')
    actual=load(root/'WRAPPER_ACTUAL_EXIT.json')
    if any(actual.get(k)!=v for k,v in {'actual_exit':0,'execute_exit':0,'collection_exit':0,'execute_calls':1,'collection_calls':1,'automatic_retry':False}.items()):raise ValueError('F_WRAPPER_FAILED_OR_RETRIED')
    ex=load(root/'WRAPPER_EXECUTE_EXIT.json'); col=load(root/'WRAPPER_COLLECTION_EXIT.json')
    if ex.get('actual_exit')!=0 or col.get('actual_exit')!=0 or ex.get('execute_calls')!=1 or ex.get('automatic_retry') is not False or col.get('collection_calls')!=1:raise ValueError('F_EXTERNAL_ACTUAL_EXIT_FAILED')
    if raw['actual_run/WRAPPER_EXECUTE_EXIT.json']!=(root/'WRAPPER_EXECUTE_EXIT.json').read_bytes():raise ValueError('F_INTERNAL_EXTERNAL_WRAPPER_MISMATCH')
    for name in ('ACTUAL_EXIT.json','RUNTIME.json','stdout.log','stderr.log'):
        if raw['actual_run/'+name]!=(root/name).read_bytes():raise ValueError('F_INTERNAL_EXTERNAL_SIDECAR_MISMATCH '+name)
    exitrow=parse(raw['actual_run/ACTUAL_EXIT.json'])
    if exitrow.get('actual_exit')!=0 or exitrow.get('observed_child_exit')!=0:raise ValueError('F_ACTUAL_RUN_FAILED')
    result=parse(raw['actual_run/NUMERICAL_RESULT.json'])
    wanted={'completed_G_builds':2,'completed_resolvent_blocks':2,'actual_triangular_solve_calls':10,'pulse_calls':0,'expm_calls':0}
    if any(result.get(k)!=v for k,v in wanted.items()) or [x.get('model') for x in result['models']]!=['fullBED','legacy']:raise ValueError('F_COMPLETION_COUNTS_OR_MODELS_MISMATCH')
    verify_runtime(parse(raw['actual_run/RUNTIME.json']));verify_runtime(result['runtime'])
    for k,v in wanted.items():
        if exitrow.get(k)!=v:raise ValueError('F_ACTUAL_EXIT_COUNTS_MISMATCH '+k)
    def count(pattern):return sum(pathlib.PurePosixPath(n).match(pattern) for n in raw)
    if count('actual_run/SOLVE_*_RESERVED.json')!=10 or count('actual_run/SOLVE_*_COMPLETED.json')!=10:raise ValueError('F_SOLVE_RECEIPTS_MISMATCH')
    for i,model in enumerate(('fullBED','legacy'),1):
        expected={f'BUILD_{i}_RESERVATION.json':'RESERVED_BEFORE_BUILD',f'G_COMPLETION_{i}.json':'COMPLETED_CONSTRUCTOR',
                  f'RESOLVENT_{i}_RESERVATION.json':'RESERVED_BEFORE_FIVE_SOLVES',f'RESOLVENT_{i}_COMPLETION.json':'COMPLETED_FIVE_SOLVES_AND_CROSSCHECKS'}
        for name,state in expected.items():
            row=parse(raw['actual_run/'+name])
            if row.get('model')!=model or row.get('state')!=state:raise ValueError('F_COMPLETION_RECEIPT_MISMATCH '+name)
        parity=parse(raw[f'actual_run/G_PARITY_{i}.json'])
        if parity.get('status')!='EXACT_RAW_CSC_AND_SAVED_GRID_MATCH' or not parity.get('method_names'):raise ValueError('F_G_PARITY_MISSING')
    # Recheck G raw identity against frozen E dependency records without importing F's solver module.
    deps=manifest['dependencies']
    for i,model in enumerate(('fullBED','legacy'),1):
        current=parse(raw[f'actual_run/G_COMPLETION_{i}.json'])['operator_identity']
        reference=parse(raw[deps['actual_'+model+'_G']['archive_path']])['operator_identity']
        if current.get('G')!=reference.get('G') or current.get('energy_eV')!=reference.get('energy_eV'):raise ValueError('F_FROZEN_G_IDENTITY_MISMATCH')
        c=current.get('method_bindings',{});r=reference.get('method_bindings',{})
        if not c or set(c)!=set(r) or any(v.get('same_parent_object') is not True for v in list(c.values())+list(r.values())) or any(c[k].get('qualname')!=r[k].get('qualname') for k in c):raise ValueError('F_METHOD_BINDING_PARITY_MISMATCH')
    for name,value in raw.items():
        if pathlib.PurePosixPath(name).match('actual_run/SOLVE_*_RESERVED.json') or pathlib.PurePosixPath(name).match('actual_run/SOLVE_*_COMPLETED.json'):
            row=parse(value); expected='RESERVED' if name.endswith('_RESERVED.json') else 'COMPLETED'
            if row.get('state')!=expected or row.get('model') not in ('fullBED','legacy') or row.get('solve') not in ('q0','q1','q2','w','v'):raise ValueError('F_SOLVE_RECEIPT_CONTENT_MISMATCH')
    collection_archive=col.get('return_archive',{}); actual_archive=actual.get('return_archive',{})
    zipname=next(name for name in files if name.endswith('.zip'))
    if collection_archive!=actual_archive or any(collection_archive.get(k)!=files[zipname][k] for k in ('bytes','sha256')) or pathlib.Path(collection_archive.get('path','')).name!=zipname:raise ValueError('F_COLLECTION_ARCHIVE_POINTER_MISMATCH')


def plan(family=None):
    admission=own_admission()
    result={'status':'WAITING_FOR_F_ACTUAL_RETURN','state':'PREPARED_NOT_EXECUTED','source_admission':admission,
            'actual_postprocess_reservations':0,'physical_G_calls':0,'linear_solve_calls':0,'pulse_calls':0,'expm_calls':0}
    if family:
        f=verify_family(family)
        result['F_identity']={k:v for k,v in f.items() if k not in ('raw','manifest','f_inputs')}
        result['status']='WAITING_FOR_G_FINAL_REVIEW' if admission['status']!='PREPARED_SOURCE_ADMITTED' else 'PREPARED_FOR_SINGLE_POSTPROCESS_ACTUAL_F_REVIEW_REQUIRED'
    return result

def numerical_preflight(out):
    import importlib.metadata
    import numpy as np
    from threadpoolctl import threadpool_info
    runtime={'python':platform.python_version(),'numpy':np.__version__,'scipy':importlib.metadata.version('scipy'),'threadpools':threadpool_info()}
    write(out/'RUNTIME.json',runtime);verify_runtime(runtime)
    return np,runtime

def worker(out,family,fd):
    with os.fdopen(fd) as f:cap=f.read()
    reservation=load(out/'RESERVATION.json')
    if reservation['coordinator_pid']!=os.getppid() or reservation['out']!=str(out) or digest(cap.encode())!=reservation['capability_sha256']:raise ValueError('OWNED_CHILD_CAPABILITY_REQUIRED')
    if own_admission()['status']!='PREPARED_SOURCE_ADMITTED':raise ValueError('G_SOURCE_REVIEW_REQUIRED')
    f=verify_family(family);np,runtime=numerical_preflight(out)
    sys.path.insert(0,str(STUDY/'src'))
    from frontier import prepare,envelope
    cached=load(STUDY/'inputs/F_CACHED_NUMERICAL_ARTIFACT.json');identity((STUDY/'inputs/F_CACHED_NUMERICAL_ARTIFACT.json').read_bytes(),load(STUDY/'inputs/INPUT_IDENTITIES.json')['local_cached_copy'],'cached')
    results={}
    from threadpoolctl import threadpool_info
    for model in ('fullBED','legacy'):
        if any(p['num_threads']!=1 for p in threadpool_info()):raise ValueError('NUMERICAL_POOLS_CHANGED')
        def npz(raw):
            with np.load(io.BytesIO(raw),allow_pickle=False) as z:return {k:z[k] for k in z.files}
        arrays=npz(f['raw'][f'actual_run/RESIDENCE_{model}_9600.npz'])
        deps=f['manifest']['dependencies']; source=npz(f['raw'][deps[model+'_9600_npz']['archive_path']]);pulse=npz(f['raw'][deps['actual_'+model+'_pulse']['archive_path']])
        for key,expected in [('energy_eV',source['energy_eV']),('b_active',source['source_vectors'][:9600]),('xT',pulse['pulse_states'][-1,:9600])]:
            if arrays[key].dtype!=expected.dtype or not np.array_equal(arrays[key],expected):raise ValueError('EXACT_F_ARRAY_SOURCE_PULSE_MISMATCH '+key)
        # Exact pulse/source identity is independently hash-bound in the F dependencies.
        if not np.array_equal(pulse['energy_eV'],source['energy_eV']) or not np.array_equal(pulse['source_vectors'],source['source_vectors']):raise ValueError('EXACT_PULSE_SOURCE_MISMATCH')
        own=parse(f['raw'][f'actual_run/RESULT_{model}.json'])
        prepared=prepare(arrays,own,cached['models'][model])
        times=sorted(set([1e10]+np.geomspace(1e10,1e6*31557600,241).tolist()+[v*31557600 for v in (1000,10000,30000,100000,300000,1000000)]))
        curve=[envelope(prepared,float(t)) for t in times]
        results[model]={'status':'NUMERICALLY_CHECKED_EXACT_SAVED_INPUTS_NOT_FORWARD_ERROR_CERTIFIED','checks':prepared['checks'],
                        'zero_q0_states':prepared['zero_q0_states'],'zero_weight_states':prepared['zero_weight_states'],'curve':curve}
    write(out/'FRONTIER_ANALYSIS.json',{'status':'ACTUAL_F_AND_G_NEW_INDEPENDENT_ASTRA_REVIEW_REQUIRED','models':results,'runtime':runtime})
    write(out/'INPUT_AND_SOURCE_IDENTITIES.json',{'G_contracts':PINS,'G_source_admission':own_admission(),
             'F_family':{k:v for k,v in f.items() if k not in ('raw','manifest','f_inputs')},'original_F_family_included':False,
             'original_F_family_required_in_outer_handoff':True})
    return 0

def reserve(out,ledger,family_sha):
    if not ledger.is_absolute() or ledger.is_symlink():raise ValueError('ABS_STABLE_LEDGER_REQUIRED')
    ledger.mkdir(parents=True,exist_ok=True)
    key=digest((TASK+'\n'+PINS['state/SCIENTIFIC_CONTRACT.json']+'\n'+family_sha).encode())
    path=ledger/(key+'.json');cap=uuid.uuid4().hex+uuid.uuid4().hex
    record={'task':TASK,'scientific_contract_sha256':PINS['state/SCIENTIFIC_CONTRACT.json'],'F_zip_sha256':family_sha,
            'coordinator_pid':os.getpid(),'out':str(out),'capability_sha256':digest(cap.encode()),'utc':utc(),
            'state':'RESERVED_NO_AUTOMATIC_RETRY','wall_s':90,'max_postprocess_runs':1}
    write(path,record);write(out/'RESERVATION.json',record)
    return cap,path

def coordinate(out,ledger,family,*,timeout_s=90,command=None):
    # timeout_s/command are dependency-injection hooks for bounded coordinator unit tests; CLI has no override.
    start=time.monotonic();deadline=start+timeout_s;start_utc=utc();child=None;observed=None;owned=False;child_command=None
    out=pathlib.Path(out);ledger=pathlib.Path(ledger);froot=pathlib.Path(family)
    if not out.is_absolute() or not froot.is_absolute() or not ledger.is_absolute():raise ValueError('ABSOLUTE_DIRECTORIES_REQUIRED')
    if out.exists() or out.is_symlink() or out.resolve().is_relative_to(STUDY.resolve()) or out.resolve().is_relative_to(froot.resolve()) or ledger.resolve().is_relative_to(out.resolve()) or ledger.resolve().is_relative_to(STUDY.resolve()) or ledger.resolve().is_relative_to(froot.resolve()):raise ValueError('FRESH_OUTPUT_AND_EXTERNAL_STABLE_LEDGER_REQUIRED')
    out.mkdir(parents=True,exist_ok=False);owned=True
    receipt={};code=1
    try:
        with (out/'stdout.log').open('xb') as stdout,(out/'stderr.log').open('xb') as stderr:
            p=plan(family);write(out/'PLAN_AND_ADMISSION.json',p)
            if p['source_admission']['status']!='PREPARED_SOURCE_ADMITTED':raise ValueError('G_SOURCE_REVIEW_REQUIRED')
            cap,ledgerpath=reserve(out,ledger,p['F_identity']['zip_sha256'])
            readfd,writefd=os.pipe();os.write(writefd,cap.encode());os.close(writefd)
            cmd=command or [sys.executable,str(pathlib.Path(__file__).resolve()),'--worker','--out',str(out),'--f-family-dir',str(froot),'--capability-fd',str(readfd)]
            child_command=cmd
            try:
                if time.monotonic()>=deadline:raise TimeoutError('COORDINATOR_PREPARATION_EXHAUSTED_DEADLINE')
                child=subprocess.Popen(cmd,stdout=stdout,stderr=stderr,pass_fds=(readfd,),start_new_session=True)
                try:
                    observed=child.wait(timeout=max(0,deadline-time.monotonic()));code=observed
                    receipt['status']='ACTUAL_F_AND_G_NEW_INDEPENDENT_ASTRA_REVIEW_REQUIRED' if code==0 else 'FIRST_FAILURE_PRESERVED'
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid,signal.SIGKILL);observed=child.wait();code=124;receipt['status']='TIMEOUT_FIRST_FAILURE_PRESERVED'
            finally:os.close(readfd)
    except Exception:
        if child is not None and child.poll() is None:os.killpg(child.pid,signal.SIGKILL);observed=child.wait()
        receipt.update(status='COORDINATOR_FIRST_FAILURE_PRESERVED',exception=traceback.format_exc());code=1
        with (out/'stderr.log').open('a') as err:err.write(receipt['exception'])
    finally:
        if owned:
            receipt.update(actual_exit=code,observed_child_exit=observed,start_utc=start_utc,end_utc=utc(),elapsed_s=time.monotonic()-start,
                           deadline_s=timeout_s,command=sys.argv,child_command=child_command,physical_G_calls=0,linear_solve_calls=0,pulse_calls=0,expm_calls=0,automatic_retry=False)
            write(out/'ACTUAL_EXIT.json',receipt)
            files={p.name:{'bytes':p.stat().st_size,'sha256':digest(p.read_bytes())} for p in out.iterdir() if p.is_file()}
            write(out/'RETURN_MANIFEST.json',{'schema':'cr-phys02g-postprocess-return.v1','files':files,'original_F_family_included':False,
                     'original_F_family_required_in_outer_handoff':True,'source_unit':str(STUDY),'status':receipt['status']})
    return code

def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--plan',action='store_true');g.add_argument('--execute',action='store_true');g.add_argument('--worker',action='store_true',help=argparse.SUPPRESS)
    p.add_argument('--f-family-dir');p.add_argument('--out');p.add_argument('--ledger-dir');p.add_argument('--capability-fd',type=int,help=argparse.SUPPRESS);a=p.parse_args()
    if a.plan:print(json.dumps(plan(a.f_family_dir),indent=2));return 0
    if a.worker:
        if not a.out or not a.f_family_dir or a.capability_fd is None:raise ValueError('PRIVATE_OWNED_WORKER_REQUIRED')
        return worker(pathlib.Path(a.out),a.f_family_dir,a.capability_fd)
    if not a.out or not a.ledger_dir or not a.f_family_dir:raise ValueError('EXECUTE_REQUIRES_FAMILY_OUTPUT_LEDGER')
    return coordinate(a.out,a.ledger_dir,a.f_family_dir)
if __name__=='__main__':
    try:sys.exit(main())
    except Exception:traceback.print_exc();sys.exit(1)
