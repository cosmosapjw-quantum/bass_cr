"""Create an R4W archive containing the immutable R4V base and exact new evidence."""
from pathlib import Path
import argparse
import hashlib
import json
import zipfile


def sha(data):
    return hashlib.sha256(data).hexdigest()


def build(root, output):
    if output.exists():
        raise ValueError('create-only archive required')
    members={}
    def tree(path,prefix):
        for p in sorted(path.rglob('*')):
            if p.is_file() and not p.is_symlink() and '__pycache__' not in p.parts and p.suffix!='.pyc':
                members[prefix+'/'+p.relative_to(path).as_posix()]=p
    base=root/'deliverables_r4v/BASS_CR_R4V_RESEARCH_PACKAGE_20261001_v1.zip'
    if sha(base.read_bytes())!='dd7a5df422cc6b75a928d6583546ef5578de1e0fd5e7d669e0ae06253a1d69f3':
        raise ValueError('R4V base package identity mismatch')
    members['base/'+base.name]=base
    src=root/'recovered_r4u/source'
    rel='research/gap_closure_20261001/g02_stable_derivative_20261001'
    tree(src/rel,'source/'+rel)
    members['source/AGENTS.md']=src/'AGENTS.md'
    tree(root/'runs_r4w','runs_r4w')
    for p in sorted((root/'deliverables_r4w').iterdir()):
        if p.is_file() and p.suffix in ('.md','.json','.csv','.sqlite') and 'RECEIPT' not in p.name:
            members['reports/'+p.name]=p
    publication=root/'publication_r4w/PUBLICATION_RECEIPT.json'
    if publication.is_file():members['publication/PUBLICATION_RECEIPT.json']=publication
    manifest={'schema':'BASS_R4W_PACKAGE_MANIFEST_V1','base_package_sha256':'dd7a5df422cc6b75a928d6583546ef5578de1e0fd5e7d669e0ae06253a1d69f3',
        'members':[{'path':n,'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for n,p in sorted(members.items())],
        'scope':'One G02 research step; base contains original72operatorcaches and DBv8; overlay preserves them',
        'physical_G02_closed':False,'production':'HOLD','capture':False}
    with zipfile.ZipFile(output,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for n,p in sorted(members.items()):z.writestr(n,p.read_bytes())
        z.writestr('MANIFEST.json',json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    with zipfile.ZipFile(output) as z:
        if z.testzip() is not None:raise ValueError('archive CRC mismatch')
        for e in manifest['members']:
            data=z.read(e['path'])
            if len(data)!=e['bytes'] or sha(data)!=e['sha256']:
                raise ValueError('member identity mismatch: '+e['path'])
    return {'schema':'BASS_R4W_PACKAGE_VALIDATION_V1','file':output.name,'bytes':output.stat().st_size,
        'sha256':sha(output.read_bytes()),'members':len(members)+1,'CRC':'PASS','member_sha256':'PASS',
        'new_native_calls':0,'production':'HOLD','capture':False}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for k in ('root','output','receipt'):p.add_argument('--'+k,type=Path,required=True)
    a=p.parse_args()
    if a.receipt.exists():raise ValueError('create-only receipt required')
    r=build(a.root.resolve(),a.output.resolve())
    with a.receipt.open('x') as f:json.dump(r,f,indent=2);f.write('\n')
    print(json.dumps(r))
