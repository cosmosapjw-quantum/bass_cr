#!/usr/bin/env python3
"""Local PHYS02F publication preparation; performs no remote writes."""
import argparse
import base64
import hashlib
import json
import os
import re
import time
import zipfile
from pathlib import Path, PurePosixPath

UNIT = 'research/cr_phys02f_20261011'
LIMIT = 95000


def digest(data):
    return hashlib.sha256(data).hexdigest()


def blob(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()


def safe(path):
    p=PurePosixPath(path)
    if not path or p.is_absolute() or '..' in p.parts or '\\' in path or str(p)!=path:
        raise ValueError('UNSAFE_PATH '+path)
    return path


def read(root,path):
    path=safe(path); p=root/path
    if p.is_symlink() or p.resolve()!=p or not p.is_file():
        raise ValueError('NONREGULAR_OR_UNSAFE_SOURCE '+str(p))
    return p.read_bytes()


def load(p):
    return json.loads(p.read_text())


def dump(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')


def identity(data):
    return {'bytes':len(data),'sha256':digest(data)}


def verify_bytes(data,row,path):
    if len(data)!=row['bytes'] or digest(data)!=row['sha256']:
        raise ValueError('IDENTITY_MISMATCH '+path)
    if 'git_blob_sha' in row and blob(data)!=row['git_blob_sha']:
        raise ValueError('GIT_BLOB_MISMATCH '+path)


def eligible(relative):
    parts=PurePosixPath(relative).parts
    if '__pycache__' in parts or relative.endswith(('.pyc','.pyo')) or relative=='FILE_MANIFEST.json': return False
    if parts[0]=='publication' and relative!='publication/READBACK_PLAN.json': return False
    return True


def unit_members(root):
    base=root/UNIT; members=[]
    for p in sorted(base.rglob('*')):
        rel=p.relative_to(base).as_posix()
        if p.is_symlink(): raise ValueError('SYMLINK_IN_UNIT '+rel)
        if p.is_file() and eligible(rel): members.append(UNIT+'/'+safe(rel))
    return members


def frozen_unit(root):
    manifest=load(root/UNIT/'FILE_MANIFEST.json')
    files=manifest['files']
    if set(files)!=set(unit_members(root)):
        raise ValueError('FINAL_UNIT_MEMBERSHIP_MISMATCH')
    for path,row in files.items(): verify_bytes(read(root,path),row,path)
    return manifest


def freeze(args):
    files={path:identity(read(args.repo,path)) for path in unit_members(args.repo)}
    dump(args.repo/UNIT/'FILE_MANIFEST.json',{'schema':'cr-phys02f-file-manifest.v1','path_basis':'repository-root','self_excluded':UNIT+'/FILE_MANIFEST.json','files':files})
    print(json.dumps({'files':len(files),'manifest':str(args.repo/UNIT/'FILE_MANIFEST.json')}))


def prepare(args):
    manifest=frozen_unit(args.repo); members=sorted(list(manifest['files'])+[UNIT+'/FILE_MANIFEST.json'])
    out=args.output/'git'; out.mkdir(parents=True,exist_ok=True)
    if any(out.iterdir()): raise ValueError('GIT_OUTPUT_NOT_EMPTY')
    mapping={}; group=[]; number=0
    def flush():
        nonlocal group,number
        if group:
            dump(out/f'TEXT_GROUP_{number:03}.json',{'encoding':'utf-8','entries':group}); number+=1; group=[]
    for path in members:
        data=read(args.repo,path); mode='100755' if os.stat(args.repo/path).st_mode & 0o111 else '100644'
        row={'path':path,'mode':mode,'type':'blob','git_blob_sha':blob(data),**identity(data)}
        try: content=data.decode('utf-8'); text='\0' not in content
        except UnicodeDecodeError: text=False; content=None
        entry={**row,'encoding':'utf-8','content':content}
        packed=len(json.dumps({'encoding':'utf-8','entries':[entry]},ensure_ascii=False,indent=2).encode())
        if text and packed<=LIMIT:
            candidate=group+[entry]
            if len(json.dumps({'encoding':'utf-8','entries':candidate},ensure_ascii=False,indent=2).encode())+1>LIMIT: flush()
            row['payload_file']=f'TEXT_GROUP_{number:03}.json'; group.append(entry)
        else:
            flush(); name=f'BASE64_BLOB_{len(mapping):03}.json'
            dump(out/name,{**row,'encoding':'base64','content':base64.b64encode(data).decode('ascii')}); row['payload_file']=name
        mapping[path]=row
    flush(); dump(out/'GIT_TREE_ENTRIES.json',{'schema':'cr-phys02f-git-preparation.v1','new_unit_only':True,'unit_manifest_sha256':digest(read(args.repo,UNIT+'/FILE_MANIFEST.json')),'files':mapping,'tree':[{'path':r['path'],'mode':r['mode'],'type':r['type'],'sha':r['git_blob_sha']} for r in mapping.values()]})
    print(json.dumps({'new_unit_files':len(mapping),'text_groups':number,'output':str(out)}))


def bundle(args):
    if not re.fullmatch('[0-9a-f]{40}',args.science_commit) or not re.fullmatch('[0-9a-f]{40}',args.science_tree): raise ValueError('FULL_GIT_IDENTITIES_REQUIRED')
    unitmanifest=frozen_unit(args.repo); dep_path=UNIT+'/inputs/DEPENDENCY_PAYLOAD_MANIFEST.json'; deps=load(args.repo/dep_path)
    if len(deps['files'])!=538: raise ValueError('DEPENDENCY_COUNT_NOT_538')
    source={}; rows={}
    def add(path,data,expected=None,origin=None):
        safe(path)
        if expected is not None: verify_bytes(data,expected,path)
        if path in source:
            if source[path]!=data: raise ValueError('PAYLOAD_PATH_COLLISION '+path)
            return
        source[path]=data; rows[path]={**identity(data),'origin':origin}
    for path,row in deps['files'].items(): add(path,read(args.repo,path),row,'frozen_dependency')
    for path,row in unitmanifest['files'].items(): add(path,read(args.repo,path),row,'final_unit')
    add(UNIT+'/FILE_MANIFEST.json',read(args.repo,UNIT+'/FILE_MANIFEST.json'),origin='unit_manifest')
    harness=args.repo/'handoff_harness'
    canonical=['physmath-coding-harness-gpt6-astra-v4.0.0-20260908.zip','physmath-research-harness-gpt6-astra-v4.0.0-20260908.zip']
    for name in canonical: add('handoff_harness/'+name,read(args.repo,'handoff_harness/'+name),origin='canonical_harness')
    family=args.recovery/'CR_PHYS02E_RETURN_FAMILY_56273489b960aaa2.zip'
    familydata=family.read_bytes(); same=[p for p,r in rows.items() if r['sha256']==digest(familydata) and r['bytes']==len(familydata)]
    if same: placement=same
    else:
        placement=['prior_returns/'+family.name]; add(placement[0],familydata,origin='actual_PR35_family_envelope')
    receipt=load(args.science_receipt)
    if receipt.get('science_commit',receipt.get('commit'))!=args.science_commit or receipt.get('science_tree',receipt.get('tree'))!=args.science_tree:
        raise ValueError('SCIENCE_RECEIPT_IDENTITY_MISMATCH')
    add('SCIENCE_COMMIT_RECEIPT.json',args.science_receipt.read_bytes(),origin='root_provided_science_receipt')
    add('README_NCP_KO.md',args.readme.read_bytes(),origin='root_provided_readme')
    manifest={'schema':'cr-phys02f-self-contained-bundle.v1','self_excluded':'BUNDLE_MANIFEST.json','science_commit':args.science_commit,'science_tree':args.science_tree,'base_commit':deps['base_commit'],'base_tree':deps['base_tree'],'unit_manifest_sha256':digest(source[UNIT+'/FILE_MANIFEST.json']),'dependency_manifest_sha256':digest(source[dep_path]),'dependency_files':538,'new_unit_path':UNIT,'actual_PR35_family_placement':placement,'files':dict(sorted(rows.items()))}
    manifestdata=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode(); source['BUNDLE_MANIFEST.json']=manifestdata
    dest=args.output/f'CR_PHYS02F_20261011_{args.science_commit[:8]}_HANDOFF.zip'
    if dest.exists(): raise ValueError('BUNDLE_OUTPUT_EXISTS')
    args.output.mkdir(parents=True,exist_ok=True); now=time.localtime()[:6]
    with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for path in sorted(source):
            data=source[path]
            if path in rows: verify_bytes(data,rows[path],path)
            zi=zipfile.ZipInfo(path,date_time=now); zi.compress_type=zipfile.ZIP_DEFLATED
            executable=path.startswith(UNIT+'/') and (args.repo/path).is_file() and os.stat(args.repo/path).st_mode & 0o111
            zi.external_attr=((0o100755 if executable else 0o100644)<<16)
            z.writestr(zi,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)
    with zipfile.ZipFile(dest) as z:
        names=z.namelist()
        if len(names)!=len(set(names)) or set(names)!=set(source): raise ValueError('ZIP_MEMBERSHIP_MISMATCH')
        for path in names:
            actual=z.read(path)
            if path=='BUNDLE_MANIFEST.json':
                if actual!=manifestdata: raise ValueError('ZIP_BUNDLE_MANIFEST_MISMATCH')
            else: verify_bytes(actual,rows[path],path)
    dump(args.output/'BUNDLE_ASSEMBLY_RECEIPT.json',{'schema':'cr-phys02f-bundle-assembly.v1','zip':dest.name,**identity(dest.read_bytes()),'payload_files':len(rows),'archive_entries':len(source),'science_commit':args.science_commit,'science_tree':args.science_tree,'bundle_manifest_sha256':digest(manifestdata),'exact_membership_and_all_payload_hashes_verified':True,'actual_PR35_family_placement':placement})
    print(json.dumps({'zip':str(dest),'entries':len(source),'sha256':digest(dest.read_bytes())}))


def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--repo',type=Path,default=Path('/workspace/scratch/584ff08e1634/bass_cr_work')); p.add_argument('--output',type=Path,default=Path(__file__).resolve().parent)
    s=p.add_subparsers(dest='command',required=True)
    s.add_parser('freeze-unit-manifest').set_defaults(func=freeze); s.add_parser('prepare-git').set_defaults(func=prepare)
    b=s.add_parser('bundle'); b.add_argument('science_commit'); b.add_argument('science_tree'); b.add_argument('--science-receipt',type=Path,required=True); b.add_argument('--readme',type=Path,required=True); b.add_argument('--recovery',type=Path,default=Path('/workspace/scratch/584ff08e1634/recovery_inputs')); b.set_defaults(func=bundle)
    a=p.parse_args(); a.repo=a.repo.resolve(); a.output=a.output.resolve(); a.func(a)


if __name__=='__main__': main()
