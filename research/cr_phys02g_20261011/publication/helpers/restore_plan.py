#!/usr/bin/env python3
"""Stdlib-only exact G outer restore and missing-F --plan; no F unpack/numerics."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import time
import zipfile

UNIT='research/cr_phys02g_20261011'
F_PATH='dependency_payload/CR_PHYS02F_20261011_39e27281_HANDOFF.zip'
F_PIN={'bytes':26927005,'sha256':'9d91d2971eab2db05e0039fe1fc2a5827086a28d585e792d56f6851840e6ebef'}
PINS={
 'state/SCIENTIFIC_CONTRACT.json':'517dd569f2e0d0857b37e33a5d90da6475978ab1a43374f3dfbe0323ffb35832',
 'state/VALIDATION_CONTRACT.json':'259d6964154cc190050761db092c9edd5499649867f822003db8afdfa42d9aba',
 'ncp/NCP_EXECUTION_CONTRACT.json':'06a06f865bba44ce93cc3bcf905cf95440de0978e87ee76529d2f440c6065856',
 'inputs/INPUT_IDENTITIES.json':'748076a5628c5a64ad4a057f96c58fd9b54da70dfef9d90e64823234c2df47c9',
 'inputs/F_BACKUP_DEPENDENCY.json':'984cb304788d9de7b89fd79d1bd1cf1daa57d12c5e63f5b1267a53743e22740f',
}


def utc():return time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
def sha(data):return hashlib.sha256(data).hexdigest()
def filehash(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()
def safe(path):
    p=PurePosixPath(path)
    if not path or path=='.' or p.is_absolute() or '..' in p.parts or '\\' in path or '\0' in path or str(p)!=path:raise ValueError('UNSAFE_PATH '+repr(path))
    return path

def verify(data,row,path):
    if len(data)!=row['bytes'] or sha(data)!=row['sha256']:raise ValueError('PAYLOAD_IDENTITY_MISMATCH '+path)
def load(data):return json.loads(data.decode('utf-8'))
def eligible(path):
    rel=PurePosixPath(path).relative_to(UNIT).as_posix();parts=PurePosixPath(rel).parts
    return rel!='FILE_MANIFEST.json' and '__pycache__' not in parts and not rel.endswith(('.pyc','.pyo')) and (parts[0]!='publication' or rel=='publication/READBACK_PLAN.json')


def restore(args,receipt):
    receipt['zip']={'path':str(args.zip),'bytes':args.zip.stat().st_size,'sha256':filehash(args.zip)}
    if args.zip.is_symlink() or not args.zip.is_file():raise ValueError('NONREGULAR_ZIP_SOURCE')
    if args.dest.exists() or args.dest.is_symlink():raise ValueError('DESTINATION_ALREADY_EXISTS')
    if args.dest.resolve()!=args.dest or args.receipt.resolve()!=args.receipt:raise ValueError('NONCANONICAL_OUTPUT_PATH')
    if args.receipt.is_relative_to(args.dest):raise ValueError('RECEIPT_MUST_BE_EXTERNAL')
    with zipfile.ZipFile(args.zip) as archive:
        entries=archive.infolist();names=[]
        for entry in entries:
            safe(entry.filename)
            mode=entry.external_attr>>16
            if entry.is_dir() or stat.S_IFMT(mode) not in (0,stat.S_IFREG):raise ValueError('NONREGULAR_ZIP_ENTRY '+entry.filename)
            names.append(entry.filename)
        if len(names)!=len(set(names)):raise ValueError('DUPLICATE_ZIP_ENTRY')
        if 'BUNDLE_MANIFEST.json' not in names:raise ValueError('BUNDLE_MANIFEST_ABSENT')
        mb=archive.read('BUNDLE_MANIFEST.json');manifest=load(mb);files=manifest['files']
        if manifest.get('schema')!='cr-phys02g-self-contained-bundle.v1' or manifest.get('self_excluded')!='BUNDLE_MANIFEST.json' or manifest.get('new_unit_path')!=UNIT:raise ValueError('G_BUNDLE_SCHEMA_REQUIRED')
        if set(names)!=set(files)|{'BUNDLE_MANIFEST.json'} or 'BUNDLE_MANIFEST.json' in files:raise ValueError('EXACT_ARCHIVE_MEMBERSHIP_MISMATCH')
        for path,pin in files.items():safe(path);verify(archive.read(path),pin,path)
        extras={'SCIENCE_COMMIT_RECEIPT.json','README_NCP.md',F_PATH}
        if {p for p in files if not p.startswith(UNIT+'/')}!=extras:raise ValueError('UNEXPECTED_NONCORE_PAYLOAD')
        science=load(archive.read('SCIENCE_COMMIT_RECEIPT.json'))
        for key,alias in [('science_commit','commit'),('science_tree','tree')]:
            value=manifest.get(key)
            if not isinstance(value,str) or not re.fullmatch('[0-9a-f]{40}',value) or science.get(key,science.get(alias))!=value:raise ValueError('SCIENCE_IDENTITY_MISMATCH '+key)
        for key in ('base_commit','base_tree'):
            if not isinstance(manifest.get(key),str) or not re.fullmatch('[0-9a-f]{40}',manifest[key]):raise ValueError('BASE_IDENTITY_REQUIRED '+key)
        umpath=UNIT+'/FILE_MANIFEST.json';umbytes=archive.read(umpath);um=load(umbytes)
        if manifest['unit_manifest_sha256']!=sha(umbytes) or um.get('schema')!='cr-phys02g-file-manifest.v1' or um.get('path_basis')!='repository-root' or um.get('self_excluded')!=umpath:raise ValueError('UNIT_MANIFEST_BINDING_MISMATCH')
        unitfiles={p for p in files if p.startswith(UNIT+'/') and p!=umpath}
        if any(not eligible(p) for p in unitfiles) or set(um['files'])!=unitfiles:raise ValueError('EXACT_CORE_UNIT_MEMBERSHIP_MISMATCH')
        for path,pin in um['files'].items():verify(archive.read(path),pin,path)
        identities=load(archive.read(UNIT+'/state/CONTRACT_IDENTITY.json'))
        if set(identities)!=set(PINS):raise ValueError('FROZEN_CONTRACT_PIN_SET_MISMATCH')
        for relative,pin in PINS.items():
            data=archive.read(UNIT+'/'+relative)
            if identities[relative]['sha256']!=pin or sha(data)!=pin:raise ValueError('FROZEN_CONTRACT_IDENTITY_MISMATCH '+relative)
            verify(data,identities[relative],relative)
        selected_science=load(archive.read(UNIT+'/state/SCIENTIFIC_CONTRACT.json'))
        if any(selected_science[key]!=manifest[key] for key in ('base_commit','base_tree')):raise ValueError('FROZEN_BASE_BINDING_MISMATCH')
        if manifest.get('nested_F')!={'path':F_PATH,**F_PIN}:raise ValueError('NESTED_F_MANIFEST_PIN_MISMATCH')
        dep=load(archive.read(UNIT+'/inputs/F_BACKUP_DEPENDENCY.json'))
        if dep['archive_path']!=F_PATH or {k:dep[k] for k in ('bytes','sha256')}!=F_PIN:raise ValueError('FROZEN_F_DEPENDENCY_MISMATCH')
        verify(archive.read(F_PATH),F_PIN,F_PATH)
        receipt['bindings']={'science_commit':manifest['science_commit'],'science_tree':manifest['science_tree'],
            'bundle_manifest_sha256':sha(mb),'unit_manifest_sha256':sha(umbytes),'frozen_contract_sha256':PINS,
            'nested_F':{'path':F_PATH,**F_PIN,'whole_archive_verified':True,'unpacked':False,'prior_F_TO04_not_rerun':True}}
        # All outer bytes, safe names, and frozen bindings validate before any restore.
        args.dest.mkdir(parents=True,exist_ok=False)
        for entry in entries:
            target=args.dest/entry.filename;target.parent.mkdir(parents=True,exist_ok=True)
            data=archive.read(entry.filename)
            if entry.filename!='BUNDLE_MANIFEST.json':verify(data,files[entry.filename],entry.filename)
            with target.open('xb') as h:h.write(data)
            target.chmod(0o755 if (entry.external_attr>>16)&0o111 else 0o644)
            if filehash(target)!=sha(data):raise ValueError('RESTORED_FILE_IDENTITY_MISMATCH '+entry.filename)
    restored=[p.relative_to(args.dest).as_posix() for p in args.dest.rglob('*') if p.is_file()]
    if len(restored)!=len(names) or set(restored)!=set(names):raise ValueError('RESTORED_MEMBERSHIP_MISMATCH')
    receipt['restore']={'destination':str(args.dest),'files':len(restored),'all_entry_hashes_verified':True,'exact_membership_verified':True}
    command=[sys.executable,str(args.dest/UNIT/'ncp/postprocess_frontier.py'),'--plan']
    env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1'
    plan={'command_argv':command,'cwd':str(args.dest),'python_executable':sys.executable,'python_version':sys.version,
          'started_utc':utc(),'timeout_s':60,'invocations':1,'F_family_argument':None,'PYTHONDONTWRITEBYTECODE':'1'}
    receipt['plan']=plan;start=time.monotonic()
    try:
        result=subprocess.run(command,cwd=args.dest,env=env,capture_output=True,text=True,timeout=60)
        plan.update(stdout=result.stdout,stderr=result.stderr,actual_exit=result.returncode)
    except subprocess.TimeoutExpired as error:
        def txt(x):return x.decode('utf-8',errors='replace') if isinstance(x,bytes) else x or ''
        plan.update(stdout=txt(error.stdout),stderr=txt(error.stderr),actual_exit=None,timed_out=True)
        raise ValueError('G_STDLIB_PLAN_TIMEOUT') from error
    finally:plan.update(ended_utc=utc(),wall_s=time.monotonic()-start)
    if result.returncode!=0:raise ValueError('G_STDLIB_PLAN_NONZERO_EXIT')
    parsed=load(result.stdout.encode());plan['parsed_plan']=parsed
    if parsed.get('status')!='WAITING_FOR_F_ACTUAL_RETURN':raise ValueError('G_PLAN_EXPECTED_WAITING_FOR_F_ACTUAL_RETURN')
    admission=parsed.get('source_admission',{})
    if admission.get('status')!='PREPARED_SOURCE_ADMITTED':raise ValueError('G_PLAN_FINAL_SOURCE_ADMISSION_REQUIRED')
    for counter in ('actual_postprocess_reservations','physical_G_calls','linear_solve_calls','pulse_calls','expm_calls'):
        if parsed.get(counter)!=0:raise ValueError('G_PLAN_ZERO_COUNTER_REQUIRED '+counter)
    restored_unit=args.dest/UNIT
    if admission.get('review_sha256')!=filehash(restored_unit/'review/INDEPENDENT_DECISION.json'):
        raise ValueError('G_PLAN_RESTORED_REVIEW_BINDING_MISMATCH')
    if admission.get('manifest_sha256')!=filehash(restored_unit/'FILE_MANIFEST.json'):
        raise ValueError('G_PLAN_RESTORED_MANIFEST_BINDING_MISMATCH')
    receipt['status']='IMPLEMENTATION_VERIFIED_G_CLEAN_RESTORE_WAITING_PLAN_PENDING_ROOT_ACCEPTANCE'


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--zip',type=Path,required=True)
    p.add_argument('--dest',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True);a=p.parse_args()
    if any(not value.is_absolute() for value in (a.zip,a.dest,a.receipt)):p.error('All paths must be absolute')
    if a.receipt.exists() or a.receipt.is_symlink():p.error('Receipt already exists')
    receipt={'schema':'cr-phys02g-clean-restore-plan-receipt.v1','started_utc':utc(),
             'helper_sha256':filehash(Path(__file__)),'status':'STARTED',
             'physics_execution':{'G':0,'pulse':0,'expm':0,'solves':0,'numerical_preflight':0,'test_suites':0},'prior_F_restore_runs':0}
    code=0
    try:restore(a,receipt)
    except Exception as error:receipt.update(status='FAILED',failure={'type':type(error).__name__,'message':str(error)});code=1
    finally:
        receipt['ended_utc']=utc();a.receipt.parent.mkdir(parents=True,exist_ok=True)
        with a.receipt.open('x') as h:json.dump(receipt,h,indent=2,allow_nan=False);h.write('\n')
    print(json.dumps({'status':receipt['status'],'receipt':str(a.receipt)}));return code

if __name__=='__main__':sys.exit(main())
