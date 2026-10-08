"""Create a preparation artifact from an exact clean commit. Never runs science."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile
import zipfile
from preflight import HERE,CONTRACT,digest,prepare,write_new


def git(root,*args):
    return subprocess.check_output(['git','-C',str(root),*args],text=True).strip()


def make(inputs,destination):
    root=Path(git(HERE,'rev-parse','--show-toplevel'))
    if git(root,'status','--porcelain'):raise ValueError('clean exact commit required')
    head=git(root,'rev-parse','HEAD');tree=git(root,'rev-parse','HEAD^{tree}')
    prefix=HERE.relative_to(root)
    names=git(root,'ls-files',str(prefix)).splitlines()
    with tempfile.TemporaryDirectory(prefix='r4p0-package-') as temporary:
        stage=Path(temporary)
        for name in names:
            source=root/name
            if source.is_symlink():raise ValueError('source symlink')
            relative=source.relative_to(HERE);target=stage/relative;target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(source.read_bytes())
        fixtures=stage/'inputs';fixtures.mkdir()
        for name,pin in CONTRACT['input_files'].items():
            source=Path(inputs)/name
            data=source.read_bytes()
            if source.is_symlink() or len(data)!=pin['bytes'] or digest(data)!=pin['sha256']:raise ValueError('fixture identity mismatch: '+name)
            target=fixtures/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        # Regenerate separately and compare to the committed receipts. Do not
        # overwrite either a historical receipt or an existing package payload.
        regenerated=stage/'regenerated'
        prepare(fixtures,regenerated)
        for source in regenerated.iterdir():
            target=stage/'receipts'/source.name
            if target.read_bytes()!=source.read_bytes():raise ValueError('committed receipt differs from regenerated result: '+source.name)
            source.unlink()
        regenerated.rmdir()
        sourcepins={'schema':'BASS_R4P0_SOURCE_PINS_V1','preparation_commit':head,'preparation_tree':tree,
                    'science_identity':{k:CONTRACT[k] for k in ('a3_commit','a3_tree','science_return_sha256','predecessor_return_sha256')},
                    'source_files':{str(Path(n).relative_to(prefix)):digest((root/n).read_bytes()) for n in names},
                    'native_numerical_provenance':json.loads((HERE/'FROZEN_DEPENDENCY_PROVENANCE.json').read_text())}
        write_new(stage/'SOURCE_PINS.json',sourcepins)
        template=json.loads((stage/'receipts/FUTURE_NATIVE_TEMPLATES.json').read_text())
        template['preparation_commit']=head;template['preparation_tree']=tree
        template['source_pins_sha256']=digest((stage/'SOURCE_PINS.json').read_bytes())
        template['contract_pins']={n:digest((stage/'receipts'/n).read_bytes()) for n in ('R4P0_TAIL_PREFLIGHT_CONTRACT.json','B0_B3_BASIS_REGISTRY_CONTRACT.json')}
        write_new(stage/'FUTURE_AUTHORIZATION_TEMPLATE.json',template)
        manifest={'schema':'BASS_R4P0_CREATE_ONLY_PACKAGE_V1','preparation_commit':head,'preparation_tree':tree,
                  'native_authorized':False,'claim_ceiling':CONTRACT['claim_ceiling'],
                  'files':{str(p.relative_to(stage)):{'bytes':p.stat().st_size,'sha256':digest(p.read_bytes())} for p in sorted(stage.rglob('*')) if p.is_file()}}
        write_new(stage/'MANIFEST.json',manifest)
        destination=Path(destination);destination.parent.mkdir(parents=True,exist_ok=True)
        with zipfile.ZipFile(destination,'x',compression=zipfile.ZIP_DEFLATED) as z:
            for p in sorted(stage.rglob('*')):
                if p.is_file():z.write(p,str(p.relative_to(stage)))
    return {'preparation_commit':head,'preparation_tree':tree,'package':str(destination.resolve()),
            'bytes':destination.stat().st_size,'sha256':digest(destination.read_bytes())}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--inputs',required=True);p.add_argument('--out',required=True)
    a=p.parse_args();print(json.dumps(make(a.inputs,a.out),indent=2))
