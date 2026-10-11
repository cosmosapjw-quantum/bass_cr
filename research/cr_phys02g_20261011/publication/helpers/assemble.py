#!/usr/bin/env python3
"""Create-only PHYS02G publication preparation. No remote writes or numerics."""
import argparse
import base64
import datetime
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import zipfile

UNIT='research/cr_phys02g_20261011'
LIMIT=95000
F_NAME='CR_PHYS02F_20261011_39e27281_HANDOFF.zip'
F_PATH='dependency_payload/'+F_NAME
F_PIN={'bytes':26927005,'sha256':'9d91d2971eab2db05e0039fe1fc2a5827086a28d585e792d56f6851840e6ebef'}


def sha(data):return hashlib.sha256(data).hexdigest()
def blob(data):return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def identity(data):return {'bytes':len(data),'sha256':sha(data)}
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def safe(path):
    p=PurePosixPath(path)
    if not path or path=='.' or p.is_absolute() or '..' in p.parts or '\\' in path or '\0' in path or str(p)!=path:
        raise ValueError('UNSAFE_PATH '+repr(path))
    return path

def read(root,path):
    p=root/safe(path)
    if p.is_symlink() or p.resolve()!=p or not p.is_file():raise ValueError('UNSAFE_OR_NONREGULAR_SOURCE '+str(p))
    return p.read_bytes()

def load(path):return json.loads(path.read_text())
def dump(path,obj,replace=False):
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.is_symlink():raise ValueError('SYMLINK_OUTPUT '+str(path))
    with path.open('w' if replace else 'x') as h:json.dump(obj,h,ensure_ascii=False,indent=2,allow_nan=False);h.write('\n')

def verify(data,row,path):
    if len(data)!=row['bytes'] or sha(data)!=row['sha256']:raise ValueError('IDENTITY_MISMATCH '+path)
    if 'git_blob_sha' in row and blob(data)!=row['git_blob_sha']:raise ValueError('GIT_BLOB_MISMATCH '+path)

def eligible(relative):
    parts=PurePosixPath(relative).parts
    if '__pycache__' in parts or relative.endswith(('.pyc','.pyo')) or relative=='FILE_MANIFEST.json':return False
    if parts[0]=='publication' and relative!='publication/READBACK_PLAN.json':return False
    return True

def members(root):
    base=root/UNIT
    if not base.is_dir() or base.is_symlink():raise ValueError('SOURCE_UNIT_REQUIRED')
    result=[]
    for p in sorted(base.rglob('*')):
        relative=p.relative_to(base).as_posix()
        if p.is_symlink():raise ValueError('SYMLINK_IN_UNIT '+relative)
        if p.is_file() and eligible(relative):result.append(UNIT+'/'+safe(relative))
    return result

def frozen(root):
    m=load(root/UNIT/'FILE_MANIFEST.json')
    if m.get('schema')!='cr-phys02g-file-manifest.v1' or m.get('path_basis')!='repository-root' or m.get('self_excluded')!=UNIT+'/FILE_MANIFEST.json':raise ValueError('UNIT_MANIFEST_SCHEMA')
    if set(m['files'])!=set(members(root)):raise ValueError('FINAL_UNIT_MEMBERSHIP_MISMATCH')
    for path,row in m['files'].items():verify(read(root,path),row,path)
    return m

def freeze(args):
    paths=members(args.repo)
    m={'schema':'cr-phys02g-file-manifest.v1','path_basis':'repository-root',
       'self_excluded':UNIT+'/FILE_MANIFEST.json','files':{p:identity(read(args.repo,p)) for p in paths}}
    target=args.repo/UNIT/'FILE_MANIFEST.json'
    dump(target,m,replace=args.replace_existing)
    print(json.dumps({'status':'FROZEN_BYTE_IDENTITIES_ONLY','files':len(paths),'manifest':str(target),'manifest_sha256':sha(target.read_bytes())}))

def prepare(args):
    m=frozen(args.repo);paths=sorted(list(m['files'])+[UNIT+'/FILE_MANIFEST.json'])
    out=args.output/'git'
    if out.exists():raise ValueError('GIT_OUTPUT_EXISTS')
    out.mkdir(parents=True,exist_ok=False)
    mapping={};group=[];number=0;binary_count=0
    def packed(entries):return len((json.dumps({'encoding':'utf-8','entries':entries},ensure_ascii=False,indent=2)+'\n').encode())
    def flush():
        nonlocal group,number
        if group:dump(out/f'TEXT_GROUP_{number:03}.json',{'encoding':'utf-8','entries':group});group=[];number+=1
    for path in paths:
        data=read(args.repo,path);mode='100755' if os.stat(args.repo/path).st_mode & 0o111 else '100644'
        row={'path':safe(path),'mode':mode,'type':'blob','git_blob_sha':blob(data),**identity(data)}
        try:content=data.decode('utf-8');is_text='\0' not in content
        except UnicodeDecodeError:content=None;is_text=False
        entry={**row,'encoding':'utf-8','content':content}
        if is_text and packed([entry])<=LIMIT:
            if packed(group+[entry])>LIMIT:flush()
            row['payload_file']=f'TEXT_GROUP_{number:03}.json';group.append(entry)
        else:
            flush();filename=f'BASE64_BLOB_{len(mapping):03}.json';binary_count+=1
            dump(out/filename,{**row,'encoding':'base64','content':base64.b64encode(data).decode('ascii')});row['payload_file']=filename
        mapping[path]=row
    flush()
    payloads={p.name:identity(p.read_bytes()) for p in sorted(out.glob('*.json'))}
    result={'schema':'cr-phys02g-git-preparation.v1','new_unit_only':True,'publication_helpers_excluded':True,
            'unit_manifest_sha256':sha(read(args.repo,UNIT+'/FILE_MANIFEST.json')),
            'inline_group_limit_bytes':LIMIT,'files':mapping,'payload_files':payloads,
            'counts':{'new_unit_files':len(paths),'source_bytes':sum(r['bytes'] for r in mapping.values()),'text_groups':number,'base64_blob_objects':binary_count},
            'tree':[{'path':r['path'],'mode':r['mode'],'type':'blob','sha':r['git_blob_sha']} for r in mapping.values()]}
    dump(out/'GIT_TREE_ENTRIES.json',result)
    print(json.dumps({**result['counts'],'output':str(out),'tree_entries_sha256':sha((out/'GIT_TREE_ENTRIES.json').read_bytes())}))

README='''# CR-PHYS02G self-contained handoff

The G source uses repository-root layout under research/cr_phys02g_20261011/.
FILE_MANIFEST.json binds the frozen G core, including its internal NCP start instructions, review, reports, and DAG. SCIENCE_COMMIT_RECEIPT.json records the root-provided actual G science commit. BUNDLE_MANIFEST.json lists every payload byte identity and excludes itself.

The byte-identical prior F handoff is embedded at dependency_payload/CR_PHYS02F_20261011_39e27281_HANDOFF.zip. It contains the complete F source and frozen dependency payload, actual prior E return family, and both canonical Astra v4.0.0 harnesses. No additional attachments are needed for the handoff. The nested F ZIP is deliberately not duplicated as a full overlay here; its prior tested restore evidence remains applicable to those exact bytes.

G cached analysis has no new operator, pulse, expm, or linear solve. G frontier postprocessing is prepared and waits for the original actual F return. Current remote absence is not proof that F execution budget is unspent. Use G internal NCP start instructions and respect the original F reservation and execution rules. A new scoped independent review of actual F and G frontier output is required before an actual frontier numerical claim.

The optional clean-restore helper verifies every outer entry and the whole nested F ZIP hash, then invokes only G ncp/postprocess_frontier.py --plan with no F family. Its expected status is WAITING_FOR_F_ACTUAL_RETURN, never READY.
'''

def bundle(args):
    m=frozen(args.repo);receipt=load(args.science_receipt)
    commit=receipt.get('science_commit',receipt.get('commit'));tree=receipt.get('science_tree',receipt.get('tree'))
    if not isinstance(commit,str) or not isinstance(tree,str) or not re.fullmatch('[0-9a-f]{40}',commit) or not re.fullmatch('[0-9a-f]{40}',tree):raise ValueError('ACTUAL_FULL_SCIENCE_IDENTITIES_REQUIRED')
    if receipt.get('unit_manifest',{}).get('sha256',sha(read(args.repo,UNIT+'/FILE_MANIFEST.json')))!=sha(read(args.repo,UNIT+'/FILE_MANIFEST.json')):raise ValueError('SCIENCE_RECEIPT_UNIT_MANIFEST_MISMATCH')
    dep=load(args.repo/UNIT/'inputs/F_BACKUP_DEPENDENCY.json')
    if dep['archive_path']!=F_PATH or {k:dep[k] for k in ('bytes','sha256')}!=F_PIN:raise ValueError('F_DEPENDENCY_PIN_MISMATCH')
    if args.f_zip.is_symlink() or not args.f_zip.is_file():raise ValueError('NONREGULAR_F_ZIP')
    fdata=args.f_zip.read_bytes();verify(fdata,F_PIN,F_PATH)
    payload={};rows={}
    def add(path,data,origin,pin=None):
        safe(path)
        if path in payload:raise ValueError('PAYLOAD_COLLISION '+path)
        if pin is not None:verify(data,pin,path)
        payload[path]=data;rows[path]={**identity(data),'origin':origin}
    for path,pin in m['files'].items():add(path,read(args.repo,path),'final_G_core',pin)
    add(UNIT+'/FILE_MANIFEST.json',read(args.repo,UNIT+'/FILE_MANIFEST.json'),'G_file_manifest')
    add('SCIENCE_COMMIT_RECEIPT.json',args.science_receipt.read_bytes(),'root_provided_actual_C1_receipt')
    add('README_NCP.md',README.encode(),'handoff_readme')
    add(F_PATH,fdata,'byte_identical_prior_F_handoff',F_PIN)
    science=load(args.repo/UNIT/'state/SCIENTIFIC_CONTRACT.json')
    manifest={'schema':'cr-phys02g-self-contained-bundle.v1','self_excluded':'BUNDLE_MANIFEST.json',
              'science_commit':commit,'science_tree':tree,'base_commit':science['base_commit'],'base_tree':science['base_tree'],
              'new_unit_path':UNIT,'unit_manifest_sha256':sha(payload[UNIT+'/FILE_MANIFEST.json']),
              'nested_F':{'path':F_PATH,**F_PIN},'files':dict(sorted(rows.items()))}
    mb=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode();payload['BUNDLE_MANIFEST.json']=mb
    args.output.mkdir(parents=True,exist_ok=True)
    dest=args.output/f'CR_PHYS02G_20261011_{commit[:8]}_HANDOFF.zip'
    if dest.exists() or dest.is_symlink():raise ValueError('BUNDLE_OUTPUT_EXISTS')
    receipt_path=args.output/'BUNDLE_ASSEMBLY_RECEIPT.json'
    if receipt_path.exists():raise ValueError('BUNDLE_RECEIPT_EXISTS')
    now=datetime.datetime.now().timetuple()[:6]
    with zipfile.ZipFile(dest,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for path,data in sorted(payload.items()):
            zi=zipfile.ZipInfo(path,date_time=now);zi.compress_type=zipfile.ZIP_STORED if path==F_PATH else zipfile.ZIP_DEFLATED
            executable=path.startswith(UNIT+'/') and os.stat(args.repo/path).st_mode & 0o111
            zi.external_attr=((0o100755 if executable else 0o100644)<<16)
            archive.writestr(zi,data)
    with zipfile.ZipFile(dest) as archive:
        names=archive.namelist()
        if len(names)!=len(set(names)) or set(names)!=set(payload):raise ValueError('ZIP_MEMBERSHIP_MISMATCH')
        for item in archive.infolist():
            safe(item.filename)
            if item.is_dir() or stat.S_IFMT(item.external_attr>>16) not in (0,stat.S_IFREG):raise ValueError('NONREGULAR_ZIP_ENTRY')
            actual=archive.read(item.filename)
            if item.filename=='BUNDLE_MANIFEST.json':
                if actual!=mb:raise ValueError('BUNDLE_MANIFEST_BYTES_MISMATCH')
            else:verify(actual,rows[item.filename],item.filename)
    artifact={'schema':'cr-phys02g-bundle-assembly.v1','created_utc':utc(),'zip':dest.name,**identity(dest.read_bytes()),
              'payload_files':len(rows),'archive_entries':len(payload),'science_commit':commit,'science_tree':tree,
              'bundle_manifest_sha256':sha(mb),'nested_F':manifest['nested_F'],
              'exact_membership_and_all_payload_hashes_verified':True,'physics_execution':{'G':0,'pulse':0,'expm':0,'solves':0}}
    dump(receipt_path,artifact)
    print(json.dumps({'zip':str(dest),'entries':len(payload),'bytes':artifact['bytes'],'sha256':artifact['sha256']}))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo',type=Path,default=Path('/workspace/scratch/584ff08e1634/bass_cr_work'))
    p.add_argument('--output',type=Path,default=Path('/workspace/scratch/584ff08e1634/phys02g_publish_work'))
    commands=p.add_subparsers(dest='command',required=True)
    f=commands.add_parser('freeze-unit');f.add_argument('--replace-existing',action='store_true',help='Only for explicit root-authorized refreeze');f.set_defaults(func=freeze)
    commands.add_parser('prepare-git').set_defaults(func=prepare)
    b=commands.add_parser('bundle');b.add_argument('--science-receipt',type=Path,required=True)
    b.add_argument('--f-zip',type=Path,default=Path('/workspace/scratch/584ff08e1634/phys02f_publish_work')/F_NAME);b.set_defaults(func=bundle)
    a=p.parse_args();a.repo=a.repo.resolve();a.output=a.output.resolve();a.func(a)

if __name__=='__main__':main()
