#!/usr/bin/env python3
"""Create-only H publication preparation. No remote writes or numerics.

Root must authorize freeze, Git preparation and the one new outer assembly.
Historical ZIP input is embedded unchanged; no historical archive verification
suite, extraction or plan is executed by this helper.
"""
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

UNIT='research/cr_phys02h_20261011'
LIMIT=95000
G_NAME='CR_PHYS02G_20261011_0ad3be0f_WITH_F_HOLD_HANDOFF.zip'
G_PATH='dependency_payload/'+G_NAME
G_PIN={'bytes':58470931,'sha256':'2920fd78632ba41dce1f2d428db328862d4ad121f1b97bc746962ae847117707'}


def sha(data):return hashlib.sha256(data).hexdigest()
def blob(data):return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def identity(data):return {'bytes':len(data),'sha256':sha(data)}
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def safe(path):
    if not isinstance(path,str):raise ValueError('PATH_STRING_REQUIRED')
    p=PurePosixPath(path)
    if (not path or path=='.' or p.is_absolute() or '..' in p.parts or '\\' in path
            or str(p)!=path or any(ord(c)<32 or ord(c)==127 for c in path)
            or re.match(r'^[A-Za-z]:',path)):
        raise ValueError('UNSAFE_PATH '+repr(path))
    return path


def canonical(path):
    path=Path(path)
    if not path.is_absolute() or '..' in path.parts:raise ValueError('ABSOLUTE_NONTRAVERSING_PATH_REQUIRED')
    for component in (path,*path.parents):
        if component.is_symlink():raise ValueError('SYMLINK_PATH '+str(component))
    if path.resolve()!=path:raise ValueError('NONCANONICAL_PATH '+str(path))
    return path


def read(root,path):
    p=canonical(root/safe(path))
    if not p.is_file() or not stat.S_ISREG(p.stat().st_mode):raise ValueError('NONREGULAR_SOURCE '+str(p))
    return p.read_bytes()


def load(path):return json.loads(path.read_text())
def dump(path,obj,replace=False):
    canonical(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w' if replace else 'x') as h:
        json.dump(obj,h,ensure_ascii=False,indent=2,allow_nan=False);h.write('\n');h.flush();os.fsync(h.fileno())


def verify(data,row,path):
    if len(data)!=row['bytes'] or sha(data)!=row['sha256']:raise ValueError('IDENTITY_MISMATCH '+path)
    if 'git_blob_sha' in row and blob(data)!=row['git_blob_sha']:raise ValueError('GIT_BLOB_MISMATCH '+path)


def eligible(relative):
    parts=PurePosixPath(relative).parts
    if '__pycache__' in parts or relative.endswith(('.pyc','.pyo')) or relative=='FILE_MANIFEST.json':return False
    if parts[0]=='publication':
        # These preparation helpers are explicitly included by root instruction;
        # post-freeze publication receipts/helpers not in this named scope stay out.
        return relative=='publication/READBACK_PLAN.json' or relative in (
            'publication/helpers/assemble.py','publication/helpers/restore_plan.py')
    return True


def members(root):
    base=canonical(root/UNIT)
    if not base.is_dir():raise ValueError('SOURCE_UNIT_REQUIRED')
    result=[]
    for p in sorted(base.rglob('*')):
        relative=p.relative_to(base).as_posix()
        if p.is_symlink():raise ValueError('SYMLINK_IN_UNIT '+relative)
        if p.is_file() and eligible(relative):result.append(UNIT+'/'+safe(relative))
    return result



def selected_return_pins(root):
    metadata=load(root/UNIT/'inputs/latest_returns/PINNED_FILE_IDENTITIES.json')
    records=metadata.get('files')
    expected_heads={39:'0c1379efe9b60d70d9cdb69f447eeb62c8720d13',
                    40:'839309f6f1edc69e3c24f4d34cc8adba4f7a161f'}
    if not isinstance(records,list) or len(records)!=33:raise ValueError('EXACT_SELECTED33_RECORDS_REQUIRED')
    expected=set()
    for row in records:
        if row.get('pr') not in expected_heads or row.get('head')!=expected_heads[row['pr']]:
            raise ValueError('PINNED_PR39_PR40_HEAD_CHANGED')
        path=UNIT+'/inputs/latest_returns/pinned/pr'+str(row['pr'])+'/'+safe(row['path'])
        if path in expected:raise ValueError('DUPLICATE_SELECTED_RETURN_PATH')
        expected.add(path);data=read(root,path)
        verify(data,row,path)
        if blob(data)!=row['git_blob']:raise ValueError('SELECTED_RETURN_BLOB_MISMATCH '+path)
    actual={path for path in members(root) if path.startswith(UNIT+'/inputs/latest_returns/pinned/')}
    if actual!=expected:raise ValueError('EXACT_SELECTED33_NAMESPACED_MEMBER_SET_REQUIRED')
    return expected


def frozen(root):
    selected_return_pins(root)
    m=load(root/UNIT/'FILE_MANIFEST.json')
    if (m.get('schema')!='cr-phys02h-file-manifest.v1' or m.get('path_basis')!='repository-root'
            or m.get('self_excluded')!=UNIT+'/FILE_MANIFEST.json'):
        raise ValueError('UNIT_MANIFEST_SCHEMA')
    if set(m['files'])!=set(members(root)):raise ValueError('FINAL_UNIT_MEMBERSHIP_MISMATCH')
    for path,row in m['files'].items():verify(read(root,path),row,path)
    return m


def freeze(args):
    selected_return_pins(args.repo)
    paths=members(args.repo)
    m={'schema':'cr-phys02h-file-manifest.v1','path_basis':'repository-root',
       'self_excluded':UNIT+'/FILE_MANIFEST.json','publication_helper_scope':'preparation only; separate from numerical execution review',
       'files':{p:identity(read(args.repo,p)) for p in paths}}
    target=args.repo/UNIT/'FILE_MANIFEST.json';dump(target,m,replace=args.replace_existing)
    print(json.dumps({'status':'FROZEN_BYTE_IDENTITIES_ONLY','files':len(paths),'manifest':str(target),
                      'manifest_sha256':sha(target.read_bytes())}))


def prepare(args):
    m=frozen(args.repo);paths=sorted(list(m['files'])+[UNIT+'/FILE_MANIFEST.json'])
    out=canonical(args.output/'git')
    if out.exists():raise ValueError('GIT_OUTPUT_EXISTS')
    out.mkdir(parents=True,exist_ok=False)
    mapping={};group=[];number=0;binary_count=0;deduplicated=0;objects={}
    def packed(entries):return len((json.dumps({'encoding':'utf-8','entries':entries},ensure_ascii=False,indent=2)+'\n').encode())
    def flush():
        nonlocal group,number
        if group:dump(out/f'TEXT_GROUP_{number:03}.json',{'encoding':'utf-8','entries':group});group=[];number+=1
    for path in paths:
        data=read(args.repo,path);mode='100755' if os.stat(args.repo/path).st_mode & 0o111 else '100644'
        row={'path':safe(path),'mode':mode,'type':'blob','git_blob_sha':blob(data),**identity(data)}
        key=row['git_blob_sha']
        if key in objects:
            old=objects[key]
            if (old['bytes'],old['sha256'])!=(row['bytes'],row['sha256']):raise ValueError('BLOB_HASH_COLLISION')
            row.update(payload_file=old['payload_file'],same_content_as=old['path']);deduplicated+=1
            mapping[path]=row;continue
        try:content=data.decode('utf-8');is_text='\0' not in content
        except UnicodeDecodeError:content=None;is_text=False
        entry={**row,'encoding':'utf-8','content':content}
        if is_text and packed([entry])<=LIMIT:
            if packed(group+[entry])>LIMIT:flush()
            row['payload_file']=f'TEXT_GROUP_{number:03}.json';group.append(entry)
        else:
            flush();filename=f'BASE64_BLOB_{len(objects):04}.json';binary_count+=1
            dump(out/filename,{**row,'encoding':'base64','content':base64.b64encode(data).decode('ascii')});row['payload_file']=filename
        mapping[path]=row;objects[key]=row
    flush()
    result={'schema':'cr-phys02h-git-preparation.v1','new_unit_only':True,
            'unit_manifest_sha256':sha(read(args.repo,UNIT+'/FILE_MANIFEST.json')),
            'inline_group_limit_bytes':LIMIT,'files':mapping,
            'payload_files':{p.name:identity(p.read_bytes()) for p in sorted(out.glob('*.json'))},
            'counts':{'new_unit_files':len(paths),'source_bytes':sum(r['bytes'] for r in mapping.values()),
                      'text_groups':number,'base64_blob_objects':binary_count,'unique_blob_objects':len(objects),
                      'duplicate_content_paths':deduplicated},
            'tree':[{'path':r['path'],'mode':r['mode'],'type':'blob','sha':r['git_blob_sha']} for r in mapping.values()]}
    dump(out/'GIT_TREE_ENTRIES.json',result)
    print(json.dumps({**result['counts'],'output':str(out),
                      'tree_entries_sha256':sha((out/'GIT_TREE_ENTRIES.json').read_bytes())}))


def bundle(args):
    m=frozen(args.repo);receipt=load(args.science_receipt)
    commit=receipt.get('science_commit',receipt.get('commit'));tree=receipt.get('science_tree',receipt.get('tree'))
    for value in (commit,tree):
        if not isinstance(value,str) or not re.fullmatch('[0-9a-f]{40}',value):raise ValueError('ACTUAL_FULL_SCIENCE_IDENTITIES_REQUIRED')
    umraw=read(args.repo,UNIT+'/FILE_MANIFEST.json')
    if receipt.get('unit_manifest',{}).get('sha256',sha(umraw))!=sha(umraw):raise ValueError('SCIENCE_RECEIPT_MANIFEST_MISMATCH')
    gpath=canonical(args.g_zip)
    if not gpath.is_file() or gpath.stat().st_size!=G_PIN['bytes']:raise ValueError('HISTORICAL_G_INPUT_METADATA_MISMATCH')
    # No standalone historical archive re-verification pass: exact G bytes are
    # checked as one entry in the single verification pass on the NEW H archive.
    gdata=gpath.read_bytes()
    start_path=canonical(args.start)
    if not start_path.is_file():raise ValueError('START_INSTRUCTIONS_REQUIRED')
    startraw=start_path.read_bytes()
    matching=[p for p,pin in m['files'].items() if p.endswith('/START_NCP_CODEX_KO.md') and identity(startraw)=={k:pin[k] for k in ('bytes','sha256')}]
    if len(matching)!=1:raise ValueError('START_MUST_MATCH_ONE_FROZEN_INTERNAL_FILE')
    payload={};rows={}
    def add(path,data,origin,pin=None):
        safe(path)
        if path in payload:raise ValueError('PAYLOAD_COLLISION '+path)
        if pin is not None and len(data)!=pin['bytes']:raise ValueError('INPUT_SIZE_MISMATCH '+path)
        payload[path]=data;rows[path]={**(pin if pin is not None else identity(data)),'origin':origin}
    for path,pin in m['files'].items():add(path,read(args.repo,path),'frozen_H_core',pin)
    add(UNIT+'/FILE_MANIFEST.json',umraw,'H_file_manifest')
    add('SCIENCE_COMMIT_RECEIPT.json',args.science_receipt.read_bytes(),'root_provided_actual_H_science_receipt')
    add('START_NCP_CODEX_KO.md',startraw,'exact_frozen_internal_start_instructions')
    add(G_PATH,gdata,'byte_identical_complete_G_outer_with_F_and_canonical_harnesses',G_PIN)
    science=load(args.repo/UNIT/'state/SCIENTIFIC_CONTRACT.json')
    manifest={'schema':'cr-phys02h-self-contained-outer.v1','self_excluded':'BUNDLE_MANIFEST.json',
              'science_commit':commit,'science_tree':tree,'base_commit':science['base_commit'],'base_tree':science['base_tree'],
              'new_unit_path':UNIT,'unit_manifest_sha256':sha(umraw),
              'nested_G':{'path':G_PATH,**G_PIN},'internal_start_path':matching[0],'files':dict(sorted(rows.items()))}
    mb=(json.dumps(manifest,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode();payload['BUNDLE_MANIFEST.json']=mb
    args.output.mkdir(parents=True,exist_ok=True)
    dest=args.output/f'CR_PHYS02H_20261011_{commit[:8]}_HANDOFF.zip'
    receipt_path=args.output/'OUTER_ASSEMBLY_RECEIPT.json'
    if dest.exists() or dest.is_symlink() or receipt_path.exists() or receipt_path.is_symlink():raise ValueError('CREATE_ONLY_OUTPUT_REQUIRED')
    now=datetime.datetime.now().timetuple()[:6]
    with zipfile.ZipFile(dest,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for path,data in sorted(payload.items()):
            zi=zipfile.ZipInfo(path,date_time=now);zi.compress_type=zipfile.ZIP_STORED if path==G_PATH else zipfile.ZIP_DEFLATED
            executable=path.startswith(UNIT+'/') and os.stat(args.repo/path).st_mode & 0o111
            zi.external_attr=((0o100755 if executable else 0o100644)<<16);archive.writestr(zi,data)
    verified=0
    with zipfile.ZipFile(dest) as archive:
        names=archive.namelist()
        if len(names)!=len(set(names)) or set(names)!=set(payload):raise ValueError('ZIP_EXACT_MEMBERSHIP_MISMATCH')
        for item in archive.infolist():
            safe(item.filename)
            if item.is_dir() or stat.S_IFMT(item.external_attr>>16) not in (0,stat.S_IFREG):raise ValueError('NONREGULAR_ZIP_ENTRY')
            actual=archive.read(item.filename)
            if item.filename=='BUNDLE_MANIFEST.json':
                if actual!=mb:raise ValueError('BUNDLE_MANIFEST_BYTES_MISMATCH')
            else:verify(actual,rows[item.filename],item.filename);verified+=1
    artifact={'schema':'cr-phys02h-outer-assembly.v1','status':'PASS_EXACT_PACKAGING_ONLY','created_utc':utc(),
              'zip':dest.name,**identity(dest.read_bytes()),'payload_files':len(rows),'archive_entries':len(payload),
              'science_commit':commit,'science_tree':tree,'bundle_manifest_sha256':sha(mb),
              'nested_G':manifest['nested_G'],'exact_membership':True,'verified_payload_files':verified,
              'completed_archive_verification_passes':1,'physics_execution':{'G':0,'pulse':0,'expm':0,'solves':0},
              'historical_archive_restore_or_plan_runs':0}
    dump(receipt_path,artifact)
    print(json.dumps({'zip':str(dest),'entries':len(payload),'bytes':artifact['bytes'],'sha256':artifact['sha256']}))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo',type=Path,default=Path('/workspace/scratch/584ff08e1634/bass_cr_work'))
    p.add_argument('--output',type=Path,default=Path('/workspace/scratch/584ff08e1634/phys02h_publish_work'))
    commands=p.add_subparsers(dest='command',required=True)
    f=commands.add_parser('freeze-unit');f.add_argument('--replace-existing',action='store_true');f.set_defaults(func=freeze)
    commands.add_parser('prepare-git').set_defaults(func=prepare)
    b=commands.add_parser('bundle');b.add_argument('--science-receipt',type=Path,required=True);b.add_argument('--start',type=Path,required=True)
    b.add_argument('--g-zip',type=Path,default=Path('/workspace/scratch/584ff08e1634/phys02g_publish_work')/G_NAME);b.set_defaults(func=bundle)
    args=p.parse_args();args.repo=canonical(args.repo);args.output=canonical(args.output)
    if hasattr(args,'science_receipt'):args.science_receipt=canonical(args.science_receipt)
    args.func(args)

if __name__=='__main__':main()
