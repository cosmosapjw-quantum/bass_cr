#!/usr/bin/env python3
"""Stdlib-only NEW H blank restore and one H --plan; never execute old suites.

Output: --dest/source/ is the repository-root execution layout;
--dest/provenance/ preserves original nested archives, manifests, canonical
harness ZIPs and failed return bytes. Destination must not already exist.
"""
import argparse
import datetime
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import time
import zipfile

H='research/cr_phys02h_20261011'
G='research/cr_phys02g_20261011'
F='research/cr_phys02f_20261011'
G_NAME='CR_PHYS02G_20261011_0ad3be0f_WITH_F_HOLD_HANDOFF.zip'
G_OUTER='dependency_payload/'+G_NAME
G_CORE='payload/CR_PHYS02G_20261011_0ad3be0f_HANDOFF.zip'
F_COMPLETE='dependency_payload/CR_PHYS02F_20261011_39e27281_HANDOFF.zip'
G_PIN={'bytes':58470931,'sha256':'2920fd78632ba41dce1f2d428db328862d4ad121f1b97bc746962ae847117707'}
G_CORE_PIN={'bytes':27795932,'sha256':'21c60d3d3f7193f2e957f17f2b610a306d0d85eaed08c90a52c0da8c5a1e602b'}
F_PIN={'bytes':26927005,'sha256':'9d91d2971eab2db05e0039fe1fc2a5827086a28d585e792d56f6851840e6ebef'}
FAILED='payload/CR_PHYS02F_LOCAL_OPERATOR_BINDING_HOLD_REMOTE_20261011T0700Z.tar.gz'
FAILED_PIN={'bytes':30522967,'sha256':'0b6d54f5811f4f8ee651a79e734c9dddf37a722133bd51acad3fcf16c110a4e5'}
CANONICAL=(
 'handoff_harness/physmath-coding-harness-gpt6-astra-v4.0.0-20260908.zip',
 'handoff_harness/physmath-research-harness-gpt6-astra-v4.0.0-20260908.zip')


def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(data):return hashlib.sha256(data).hexdigest()
def identity(data):return {'bytes':len(data),'sha256':sha(data)}
def safe(name):
    if not isinstance(name,str):raise ValueError('PATH_STRING_REQUIRED')
    p=PurePosixPath(name)
    if (not name or name=='.' or p.is_absolute() or '..' in p.parts or '\\' in name
            or str(p)!=name or any(ord(c)<32 or ord(c)==127 for c in name)
            or re.match(r'^[A-Za-z]:',name)):
        raise ValueError('UNSAFE_PATH '+repr(name))
    return name


def canonical(path):
    path=Path(path)
    if not path.is_absolute() or '..' in path.parts:raise ValueError('ABSOLUTE_NONTRAVERSING_PATH_REQUIRED')
    for item in (path,*path.parents):
        if item.is_symlink():raise ValueError('SYMLINK_PATH '+str(item))
    if path.resolve()!=path:raise ValueError('NONCANONICAL_PATH '+str(path))
    return path


def verify(data,pin,label):
    if len(data)!=pin['bytes'] or sha(data)!=pin['sha256']:raise ValueError('PAYLOAD_IDENTITY_MISMATCH '+label)


def load(data):return json.loads(data.decode('utf-8'))


class Archive:
    """Safe exact central directory plus source-consumption hash verification.

    Old archive historical suites are never run. New H outer is fully verified
    once. Old nested members are read/verified once only as consumed by this new
    restore; whole old archives are not independently replay-verified.
    """
    def __init__(self,raw,label,schema):
        self.label=label;self.raw=raw;self.zip=zipfile.ZipFile(io.BytesIO(raw));self.rows={};self.cache={}
        entries=self.zip.infolist();names=[]
        for entry in entries:
            safe(entry.filename)
            if entry.is_dir() or stat.S_IFMT(entry.external_attr>>16) not in (0,stat.S_IFREG):
                raise ValueError('NONREGULAR_ARCHIVE_ENTRY '+label+':'+entry.filename)
            names.append(entry.filename);self.rows[entry.filename]=entry
        if len(names)!=len(set(names)):raise ValueError('DUPLICATE_ARCHIVE_ENTRY '+label)
        if 'BUNDLE_MANIFEST.json' not in names:raise ValueError('MANIFEST_MISSING '+label)
        self.manifest_raw=self.zip.read('BUNDLE_MANIFEST.json');self.manifest=load(self.manifest_raw)
        if self.manifest.get('schema')!=schema or self.manifest.get('self_excluded')!='BUNDLE_MANIFEST.json':
            raise ValueError('ARCHIVE_SCHEMA '+label)
        self.files=self.manifest['files']
        if not isinstance(self.files,dict) or 'BUNDLE_MANIFEST.json' in self.files or set(names)!=set(self.files)|{'BUNDLE_MANIFEST.json'}:
            raise ValueError('EXACT_ARCHIVE_MEMBERSHIP_MISMATCH '+label)
        for path in self.files:safe(path)
    def get(self,path):
        safe(path)
        if path not in self.files:raise ValueError('REQUIRED_ARCHIVE_MEMBER_MISSING '+self.label+':'+path)
        if path not in self.cache:
            raw=self.zip.read(path);verify(raw,self.files[path],self.label+':'+path);self.cache[path]=raw
        return self.cache[path]
    def mode(self,path):return 0o755 if (self.rows[path].external_attr>>16)&0o111 else 0o644


def restored_source_pin(source,manifest,label):
    if manifest.get('path_basis')!='repository-root' or not isinstance(manifest.get('files'),dict):
        raise ValueError('SOURCE_MANIFEST_SCHEMA '+label)
    for path,pin in manifest['files'].items():
        safe(path)
        if path not in source:raise ValueError('SOURCE_PAYLOAD_MISSING '+label+':'+path)
        verify(source[path][0],pin,label+':'+path)


def restore(args,receipt):
    zip_path=canonical(args.zip);dest=canonical(args.dest);receipt_path=canonical(args.receipt)
    if not zip_path.is_file():raise ValueError('REGULAR_ZIP_REQUIRED')
    if dest.exists() or dest.is_symlink():raise ValueError('NEW_BLANK_DESTINATION_REQUIRED')
    if receipt_path.is_relative_to(dest):raise ValueError('RECEIPT_MUST_BE_EXTERNAL')
    raw=zip_path.read_bytes();receipt['zip']={'path':str(zip_path),**identity(raw)}
    h=Archive(raw,'H_outer','cr-phys02h-self-contained-outer.v1')
    for path in h.files:h.get(path)  # one complete NEW outer entry verification pass
    if h.manifest.get('new_unit_path')!=H or h.manifest.get('nested_G')!={'path':G_OUTER,**G_PIN}:
        raise ValueError('H_NESTED_G_OR_UNIT_BINDING')
    extras={G_OUTER,'SCIENCE_COMMIT_RECEIPT.json','START_NCP_CODEX_KO.md'}
    if {p for p in h.files if not p.startswith(H+'/')}!=extras:raise ValueError('H_OUTER_EXACT_NONCORE_MEMBERS')
    umpath=H+'/FILE_MANIFEST.json';umraw=h.get(umpath);um=load(umraw)
    if (sha(umraw)!=h.manifest['unit_manifest_sha256'] or um.get('schema')!='cr-phys02h-file-manifest.v1'
            or um.get('path_basis')!='repository-root' or um.get('self_excluded')!=umpath):
        raise ValueError('H_UNIT_MANIFEST_BINDING')
    if set(um['files'])!={p for p in h.files if p.startswith(H+'/') and p!=umpath}:raise ValueError('H_UNIT_EXACT_MEMBERSHIP')
    for path,pin in um['files'].items():verify(h.get(path),pin,path)
    science=load(h.get('SCIENCE_COMMIT_RECEIPT.json'))
    for key,alias in (('science_commit','commit'),('science_tree','tree')):
        value=h.manifest.get(key)
        if not isinstance(value,str) or not re.fullmatch('[0-9a-f]{40}',value) or science.get(key,science.get(alias))!=value:
            raise ValueError('H_ACTUAL_SCIENCE_RECEIPT_BINDING '+key)
    start=h.manifest['internal_start_path']
    if not start.startswith(H+'/') or not start.endswith('/START_NCP_CODEX_KO.md') or h.get(start)!=h.get('START_NCP_CODEX_KO.md'):
        raise ValueError('H_START_INSTRUCTIONS_BINDING')
    graw=h.get(G_OUTER);g=Archive(graw,'G_outer','cr-phys02g-late-f-hold-envelope.v1')
    if {k:g.files[G_CORE][k] for k in ('bytes','sha256')}!=G_CORE_PIN:raise ValueError('OBSERVED_G_CORE_PIN_CHANGED')
    gcraw=g.get(G_CORE);gc=Archive(gcraw,'G_core','cr-phys02g-self-contained-bundle.v1')
    if gc.manifest.get('new_unit_path')!=G or gc.manifest.get('nested_F')!={'path':F_COMPLETE,**F_PIN}:
        raise ValueError('OBSERVED_G_CORE_F_BINDING_CHANGED')
    fraw=gc.get(F_COMPLETE);f=Archive(fraw,'F_complete','cr-phys02f-self-contained-bundle.v1')
    if f.manifest.get('new_unit_path')!=F or f.manifest.get('dependency_files')!=538:
        raise ValueError('OBSERVED_COMPLETE_F_DEPENDENCIES_CHANGED')
    source={};provenance={}
    def add(mapping,path,data,mode=0o644):
        safe(path)
        if path in mapping:raise ValueError('OVERLAY_OR_PROVENANCE_COLLISION '+path)
        mapping[path]=(data,mode)
    # Complete F repository content: old root receipt/readme are provenance.
    for path in f.files:
        if path.startswith(('research/','docs/','.codex/','handoff_harness/')) or path=='AGENTS.md':
            add(source,path,f.get(path),f.mode(path))
        else:add(provenance,'F_root/'+path,f.get(path),f.mode(path))
    for path in gc.files:
        if path.startswith(G+'/'):add(source,path,gc.get(path),gc.mode(path))
        elif path!=F_COMPLETE:add(provenance,'G_core_root/'+path,gc.get(path),gc.mode(path))
    for path in h.files:
        if path.startswith(H+'/'):add(source,path,h.get(path),h.mode(path))
    # Historical failed fingerprint source belongs to G publication/late_f.
    inputs=load(h.get(H+'/inputs/INPUT_IDENTITIES.json'))
    for path in inputs['files']:
        if path not in source and path.startswith(G+'/publication/late_f/'):
            prior='late_f/'+path[len(G+'/publication/late_f/'):]
            add(source,path,g.get(prior),g.mode(prior))
    add(provenance,'H_outer/BUNDLE_MANIFEST.json',h.manifest_raw)
    add(provenance,'H_outer/SCIENCE_COMMIT_RECEIPT.json',h.get('SCIENCE_COMMIT_RECEIPT.json'))
    add(provenance,'H_outer/START_NCP_CODEX_KO.md',h.get('START_NCP_CODEX_KO.md'))
    add(provenance,'archives/'+G_NAME,graw)
    add(provenance,'archives/'+PurePosixPath(G_CORE).name,gcraw)
    add(provenance,'archives/'+PurePosixPath(F_COMPLETE).name,fraw)
    add(provenance,'G_outer/BUNDLE_MANIFEST.json',g.manifest_raw)
    add(provenance,'G_core/BUNDLE_MANIFEST.json',gc.manifest_raw)
    add(provenance,'F_complete/BUNDLE_MANIFEST.json',f.manifest_raw)
    if {k:g.files[FAILED][k] for k in ('bytes','sha256')}!=FAILED_PIN:raise ValueError('OBSERVED_FAILED_RETURN_PIN_CHANGED')
    add(provenance,'old_failure/'+PurePosixPath(FAILED).name,g.get(FAILED))
    for path in CANONICAL:
        if path not in source:raise ValueError('CANONICAL_HARNESS_MISSING '+path)
        add(provenance,'canonical/'+PurePosixPath(path).name,source[path][0])
    restored_source_pin(source,inputs,'H_inputs')
    dep=load(source[F+'/inputs/DEPENDENCY_PAYLOAD_MANIFEST.json'][0])
    if len(dep['files'])!=538:raise ValueError('F_DEPENDENCY_COUNT_CHANGED')
    restored_source_pin(source,dep,'F538')
    # All bytes, complete membership, paths and source identities check before
    # the first output creation. No overwrite is allowed, even equal-content.
    for mapping in (source,provenance):
        paths=set(mapping)
        for path in paths:
            for parent in PurePosixPath(path).parents:
                if parent.as_posix() in paths:raise ValueError('FILE_DIRECTORY_PREFIX_COLLISION '+path)
    dest.mkdir(parents=True,exist_ok=False)
    for dirname,mapping in (('source',source),('provenance',provenance)):
        for path,(data,mode) in sorted(mapping.items()):
            target=dest/dirname/path;target.parent.mkdir(parents=True,exist_ok=True)
            canonical(target)
            with target.open('xb') as handle:handle.write(data)
            target.chmod(mode)
    actual={p.relative_to(dest).as_posix() for p in dest.rglob('*') if p.is_file()}
    expected={'source/'+p for p in source}|{'provenance/'+p for p in provenance}
    if actual!=expected:raise ValueError('RESTORED_EXACT_MEMBERSHIP_MISMATCH')
    receipt['restore']={'destination':str(dest),'source_root':str(dest/'source'),
        'source_files':len(source),'provenance_files':len(provenance),'exact_membership':True,
        'new_outer_payload_verification_passes':1,'historical_suite_or_plan_runs':0,
        'original_nested_archives_preserved':True,'canonical_harnesses_preserved':list(CANONICAL)}
    command=[sys.executable,str(dest/'source'/H/'ncp/run_and_collect.py'),'--plan','--source-root',str(dest/'source'),'--run',str(dest/'planned_run')]
    env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1'
    for key in ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS','NUMEXPR_NUM_THREADS','OMP_MAX_ACTIVE_LEVELS'):env[key]='1'
    plan={'command_argv':command,'invocations':1,'started_utc':utc(),'timeout_s':60,'PYTHONDONTWRITEBYTECODE':'1'}
    receipt['plan']=plan;started=time.monotonic()
    try:
        result=subprocess.run(command,cwd=dest/'source',env=env,capture_output=True,text=True,timeout=60)
        plan.update(actual_exit=result.returncode,stdout=result.stdout,stderr=result.stderr)
    except subprocess.TimeoutExpired as error:
        def txt(value):return value.decode('utf-8',errors='replace') if isinstance(value,bytes) else value or ''
        plan.update(actual_exit=None,stdout=txt(error.stdout),stderr=txt(error.stderr),timed_out=True)
        raise ValueError('H_STDLIB_PLAN_TIMEOUT') from error
    finally:plan.update(ended_utc=utc(),wall_s=time.monotonic()-started)
    if result.returncode!=0:raise ValueError('H_STDLIB_PLAN_NONZERO_EXIT')
    parsed=json.loads(result.stdout);plan['parsed_plan']=parsed
    if parsed.get('status')!='PLAN_ONLY_NO_GENERATOR_CALLS' or parsed.get('execution_status')!='NOT_EXECUTED':
        raise ValueError('H_PLAN_ONLY_STATUS_REQUIRED')
    if parsed.get('call_counts')!={'G':0,'pulse':0,'expm':0,'resolvent':0,'linear_solve':0}:
        raise ValueError('H_PLAN_ZERO_COUNTER_REQUIRED')
    if 'source_binding' not in parsed:raise ValueError('H_RESTORED_SOURCE_PIN_ADMISSION_FAILED')
    holds=parsed.get('holds',[])
    permitted=('RESOURCE_','RUNTIME_')
    if any(not str(row.get('code','')).startswith(permitted) for row in holds):
        raise ValueError('H_PLAN_UNEXPECTED_HOLD '+json.dumps(holds))
    receipt['status']='PASS_NEW_H_BLANK_RESTORE_AND_PLAN_WITH_SOURCE_BINDING'
    receipt['runtime_resource_holds']=holds


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--zip',type=Path,required=True)
    p.add_argument('--dest',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True)
    args=p.parse_args()
    for value in (args.zip,args.dest,args.receipt):canonical(value)
    if args.receipt.exists() or args.receipt.is_symlink():p.error('Create-only external receipt required')
    receipt={'schema':'cr-phys02h-new-blank-restore-plan.v1','started_utc':utc(),
             'helper_sha256':sha(Path(__file__).read_bytes()),'status':'STARTED',
             'physics_execution':{'G':0,'pulse':0,'expm':0,'resolvent':0,'solves':0,'test_suites':0}}
    code=0
    try:restore(args,receipt)
    except Exception as error:receipt.update(status='FAILED',failure={'type':type(error).__name__,'message':str(error)});code=1
    finally:
        receipt['ended_utc']=utc();args.receipt.parent.mkdir(parents=True,exist_ok=True)
        with args.receipt.open('x') as handle:json.dump(receipt,handle,indent=2,allow_nan=False);handle.write('\n')
    print(json.dumps({'status':receipt['status'],'receipt':str(args.receipt)}));return code

if __name__=='__main__':sys.exit(main())
