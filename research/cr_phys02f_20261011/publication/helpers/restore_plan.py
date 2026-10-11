#!/usr/bin/env python3
"""One final stdlib-only PHYS02F clean restore and --plan invocation."""
import argparse
import hashlib
import json
import os
import stat
import subprocess
import sys
import time
import zipfile
from pathlib import Path, PurePosixPath

UNIT='research/cr_phys02f_20261011'
PINS={
 'state/SCIENTIFIC_CONTRACT.json':'b50c316e91ebea6b1d0e5a43367b1cb31ae8836af328521fb366af9f54e35ccf',
 'ncp/NCP_EXECUTION_CONTRACT.json':'5c7517dcc08796f61ca811c7a5922622e0a2c5ff9be16312bbb1a768aa7db1f8',
 'state/VALIDATION_CONTRACT.json':'aa346614c4c444bac423eabd286939a4a1d2db20c0bb8e19281608f0ac778896',
 'inputs/INPUT_IDENTITIES.json':'4f5a871e3995fa7f18f3dae0e4da8ca1f150814bbb3a6d71e997f6fdeaff3def',
 'inputs/DEPENDENCY_PAYLOAD_MANIFEST.json':'248ad97e6417c3ba88bcbbfcb662f6fe65464e63eba6183421770ba06d41a341',
}


def utc(): return time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
def sha(data): return hashlib.sha256(data).hexdigest()
def filehash(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''): h.update(block)
    return h.hexdigest()
def safe(name):
    p=PurePosixPath(name)
    if not name or p.is_absolute() or '..' in p.parts or '\\' in name or '\0' in name or str(p)!=name:
        raise ValueError('UNSAFE_ZIP_PATH '+repr(name))
    return name

def verify(data,row,path):
    if len(data)!=row['bytes'] or sha(data)!=row['sha256']: raise ValueError('PAYLOAD_IDENTITY_MISMATCH '+path)
def load(data): return json.loads(data.decode('utf-8'))


def restore(args,receipt):
    receipt['zip']={'path':str(args.zip),'bytes':args.zip.stat().st_size,'sha256':filehash(args.zip)}
    if args.dest.exists() or args.dest.is_symlink(): raise ValueError('DESTINATION_ALREADY_EXISTS')
    if args.dest.resolve()!=args.dest or args.receipt.resolve()!=args.receipt: raise ValueError('SYMLINK_OR_NONCANONICAL_OUTPUT_PATH')
    if args.receipt.is_relative_to(args.dest): raise ValueError('RECEIPT_MUST_BE_EXTERNAL')
    with zipfile.ZipFile(args.zip) as z:
        entries=z.infolist(); names=[]
        for item in entries:
            safe(item.filename); mode=item.external_attr>>16
            if item.is_dir() or stat.S_ISLNK(mode) or stat.S_IFMT(mode) not in (0,stat.S_IFREG): raise ValueError('NONREGULAR_ZIP_ENTRY '+item.filename)
            names.append(item.filename)
        if len(names)!=len(set(names)): raise ValueError('DUPLICATE_ZIP_ENTRY')
        if 'BUNDLE_MANIFEST.json' not in names: raise ValueError('BUNDLE_MANIFEST_ABSENT')
        mb=z.read('BUNDLE_MANIFEST.json'); manifest=load(mb); files=manifest['files']
        if manifest.get('schema')!='cr-phys02f-self-contained-bundle.v1' or manifest.get('new_unit_path')!=UNIT or manifest.get('self_excluded')!='BUNDLE_MANIFEST.json': raise ValueError('CURRENT_F_BUNDLE_SCHEMA_OR_UNIT_REQUIRED')
        if set(names)!=set(files)|{'BUNDLE_MANIFEST.json'} or 'BUNDLE_MANIFEST.json' in files: raise ValueError('EXACT_ARCHIVE_MEMBERSHIP_MISMATCH')
        for path,row in files.items(): safe(path); verify(z.read(path),row,path)
        receipt['bundle_manifest']={'sha256':sha(mb),'schema':manifest['schema'],'payload_files':len(files)}
        science=load(z.read('SCIENCE_COMMIT_RECEIPT.json'))
        for key,alias in [('science_commit','commit'),('science_tree','tree')]:
            identity=manifest.get(key)
            if not isinstance(identity,str) or len(identity)!=40 or any(c not in '0123456789abcdef' for c in identity) or science.get(key,science.get(alias))!=identity: raise ValueError('SCIENCE_IDENTITY_MISMATCH '+key)
        for key in ('base_commit','base_tree'):
            identity=manifest.get(key)
            if not isinstance(identity,str) or len(identity)!=40 or any(c not in '0123456789abcdef' for c in identity): raise ValueError('BASE_IDENTITY_REQUIRED '+key)
        unitpath=UNIT+'/FILE_MANIFEST.json'; unitbytes=z.read(unitpath); um=load(unitbytes)
        if manifest.get('unit_manifest_sha256')!=sha(unitbytes) or um.get('schema')!='cr-phys02f-file-manifest.v1' or um.get('path_basis')!='repository-root': raise ValueError('UNIT_MANIFEST_BINDING_MISMATCH')
        expected_unit={p for p in files if p.startswith(UNIT+'/') and p!=unitpath}
        if set(um['files'])!=expected_unit: raise ValueError('EXACT_UNIT_MEMBERSHIP_MISMATCH')
        for path,row in um['files'].items(): verify(z.read(path),row,path)
        contract_identities={}
        for relative,pin in PINS.items():
            path=UNIT+'/'+relative; actual=sha(z.read(path))
            if actual!=pin: raise ValueError('FROZEN_CONTRACT_IDENTITY_MISMATCH '+path)
            contract_identities[relative]=actual
        dp=UNIT+'/inputs/DEPENDENCY_PAYLOAD_MANIFEST.json'; deps=load(z.read(dp))
        if manifest.get('dependency_manifest_sha256')!=PINS['inputs/DEPENDENCY_PAYLOAD_MANIFEST.json'] or manifest.get('dependency_files')!=538 or len(deps['files'])!=538: raise ValueError('DEPENDENCY_BINDING_OR_COUNT_MISMATCH')
        for key in ('base_commit','base_tree'):
            if deps.get(key)!=manifest[key]: raise ValueError('DEPENDENCY_BASE_IDENTITY_MISMATCH '+key)
        for path,row in deps['files'].items(): verify(z.read(path),row,path)
        dag=load(z.read(UNIT+'/state/NEXT_DAG.json')); task=next(t for t in dag['tasks'] if t['id']=='CR-PHYS02F-NCP-ADJOINT-RESIDENCE')
        ref=task['independent_review']; decisionpath=UNIT+'/'+safe(ref['path']); decisionbytes=z.read(decisionpath)
        if sha(decisionbytes)!=ref['sha256']: raise ValueError('DECISION_IDENTITY_MISMATCH')
        decision=load(decisionbytes)
        if decision.get('decision')!='PASS_SCOPED': raise ValueError('DECISION_NOT_PASS_SCOPED')
        receipt['bindings']={k:manifest[k] for k in ('science_commit','science_tree','base_commit','base_tree','unit_manifest_sha256','dependency_manifest_sha256')}
        receipt['bindings'].update(contract_identities=contract_identities,decision={'path':decisionpath,'sha256':sha(decisionbytes),'decision':decision['decision']},science_receipt_sha256=sha(z.read('SCIENCE_COMMIT_RECEIPT.json')))
        # Only after every entry and binding validates, create the fresh destination.
        args.dest.mkdir(parents=True,exist_ok=False)
        for item in entries:
            target=args.dest/item.filename; target.parent.mkdir(parents=True,exist_ok=True)
            data=z.read(item.filename)
            if item.filename!='BUNDLE_MANIFEST.json': verify(data,files[item.filename],item.filename)
            with target.open('xb') as f: f.write(data)
            mode=item.external_attr>>16
            target.chmod(0o755 if mode & 0o111 else 0o644)
            if filehash(target)!=sha(data): raise ValueError('RESTORED_FILE_IDENTITY_MISMATCH '+item.filename)
    restored=[p.relative_to(args.dest).as_posix() for p in args.dest.rglob('*') if p.is_file()]
    if set(restored)!=set(names) or len(restored)!=len(names): raise ValueError('EXACT_RESTORED_MEMBERSHIP_MISMATCH')
    receipt['restore']={'destination':str(args.dest),'files':len(restored),'exact_membership_verified':True,'all_payload_size_sha_verified':True}
    command=[sys.executable,str(args.dest/UNIT/'ncp/launch_residence.py'),'--plan']
    env=os.environ.copy(); env['PYTHONDONTWRITEBYTECODE']='1'
    planreceipt={'command_argv':command,'cwd':str(args.dest),'python_executable':sys.executable,'python_version':sys.version,'PYTHONDONTWRITEBYTECODE':'1','timeout_s':60,'invocations':1,'started_utc':utc()}
    receipt['plan']=planreceipt; t=time.monotonic()
    try:
        r=subprocess.run(command,cwd=args.dest,env=env,capture_output=True,text=True,timeout=60)
        planreceipt.update(stdout=r.stdout,stderr=r.stderr,exit_code=r.returncode)
    except subprocess.TimeoutExpired as e:
        def text(x): return x.decode('utf-8',errors='replace') if isinstance(x,bytes) else (x or '')
        planreceipt.update(stdout=text(e.stdout),stderr=text(e.stderr),exit_code=None,timed_out=True)
        raise ValueError('STDLIB_PLAN_TIMEOUT') from e
    finally: planreceipt.update(ended_utc=utc(),wall_s=time.monotonic()-t)
    if r.returncode!=0: raise ValueError('STDLIB_PLAN_NONZERO_EXIT')
    plan=load(r.stdout.encode()); planreceipt['parsed_plan']=plan
    if plan.get('admission_status')!='READY': raise ValueError('STDLIB_PLAN_ADMISSION_NOT_READY')
    resource=plan.get('resource_probe',{}).get('status')
    receipt['resource_status']=resource
    if resource!='NOT_PROBED_BY_STDLIB_PLAN': raise ValueError('UNEXPECTED_STDLIB_PLAN_RESOURCE_STATUS')
    receipt['status']='IMPLEMENTATION_VERIFIED_RESTORE_AND_READY_PLAN_PENDING_ROOT_ACCEPTANCE'


def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--zip',type=Path,required=True); p.add_argument('--dest',type=Path,required=True); p.add_argument('--receipt',type=Path,required=True); a=p.parse_args()
    if any(not x.is_absolute() for x in (a.zip,a.dest,a.receipt)): p.error('All paths must be absolute')
    if a.receipt.exists() or a.receipt.is_symlink(): p.error('Receipt already exists')
    receipt={'schema':'cr-phys02f-clean-restore-plan-receipt.v1','started_utc':utc(),'helper_sha256':filehash(Path(__file__)),'status':'STARTED','physics_execution':{'G':0,'pulse':0,'expm':0,'numerical_preflight':0,'test_suites':0}}
    code=0
    try: restore(a,receipt)
    except Exception as e: receipt.update(status='FAILED',failure={'type':type(e).__name__,'message':str(e)}); code=1
    finally:
        receipt['ended_utc']=utc(); a.receipt.parent.mkdir(parents=True,exist_ok=True)
        with a.receipt.open('x') as f: json.dump(receipt,f,indent=2,allow_nan=False); f.write('\n')
    print(json.dumps({'status':receipt['status'],'receipt':str(a.receipt)})); return code


if __name__=='__main__': sys.exit(main())
