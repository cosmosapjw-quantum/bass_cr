"""Create-only per-stage backup package with explicit members and content manifest."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tarfile

def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def package(root,stage):
    repo=root/'worktree';dest=root/'packages'/stage;dest.mkdir(parents=True,exist_ok=False)
    if stage in ('A','B','C','B_preparation_refinement'):
        if not (root/stage/'COMPLETE.json').is_file():raise ValueError('only completed job packages')
        shutil.copytree(root/stage,dest/stage)
    elif stage not in ('PREREGISTRATION','FINAL'):raise ValueError('unknown stage')
    source_paths = ['cr_repro','vendor_w1r','configs/r3m15','scripts','tests','docs/r3m15','docs/roadmap']
    if stage == 'FINAL':
        source_paths.append('results/R3M15')
    for name in source_paths:
        shutil.copytree(repo/name,dest/'source'/name,ignore=shutil.ignore_patterns('__pycache__','.pytest_cache'))
    for name in ['pyproject.toml','requirements.txt']:
        shutil.copy2(repo/name,dest/'source'/name)
    shutil.copytree(root/'receipts',dest/'receipts',ignore=shutil.ignore_patterns('*.sqlite*'))
    for path in root.glob('historical_*.json'):shutil.copy2(path,dest/path.name)
    manifest={'schema':'R3M15_STAGE_PACKAGE_V1','stage':stage,
              'git_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip(),
              'claim_ceiling':'bgrid NO_GO; all-bound OPEN; no scientific admission from delivery',
              'files':[{'path':str(p.relative_to(dest)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(dest.rglob('*')) if p.is_file()]}
    (dest/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
    archive=root/f'BASS_CR_R3M15_{stage}_20260922_v1.tar.zst'
    if archive.exists():raise FileExistsError(archive)
    subprocess.run(['tar','-I','zstd -T2 -3','-cf',str(archive),'-C',str(dest),'.'],check=True)
    expected={r['path']:r for r in manifest['files']};seen=set()
    proc=subprocess.Popen(['zstd','-dc',str(archive)],stdout=subprocess.PIPE)
    with tarfile.open(fileobj=proc.stdout,mode='r|') as tar:
        for member in tar:
            if not member.isfile():continue
            name=member.name.removeprefix('./')
            if name=='MANIFEST.json':continue
            assert name in expected
            digest=hashlib.file_digest(tar.extractfile(member),'sha256').hexdigest()
            assert digest==expected[name]['sha256'] and member.size==expected[name]['bytes']
            seen.add(name)
    assert proc.wait()==0 and seen==set(expected)
    archive.chmod(0o444)
    ident={'stage':stage,'path':str(archive),'name':archive.name,'bytes':archive.stat().st_size,'sha256':sha(archive),
           'md5':hashlib.md5(archive.read_bytes()).hexdigest() if archive.stat().st_size<64*1024**2 else None,
           'manifest_sha256':sha(dest/'MANIFEST.json'),'local_archive_members_verified':len(seen),'remote_restore_verified':False}
    (root/f'ARCHIVE_{stage}.json').write_text(json.dumps(ident,indent=2)+'\n')
    # Existing authorized Drive adapter uses bounded 32 MiB parts.
    parts=root/'drive_parts'/stage;parts.mkdir(parents=True,exist_ok=False);rows=[];chunk=32*1024**2
    total=(archive.stat().st_size+chunk-1)//chunk
    with archive.open('rb') as stream:
        for i in range(total):
            data=stream.read(chunk);p=parts/f'{archive.name}.part{i+1:03d}of{total:03d}'
            p.write_bytes(data);p.chmod(0o444)
            rows.append({'index':i+1,'name':p.name,'path':str(p),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'md5':hashlib.md5(data).hexdigest()})
    (root/f'DRIVE_PARTS_{stage}.json').write_text(json.dumps({'archive':ident,'ordered_parts':rows},indent=2)+'\n')
    print(json.dumps(ident,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--stage',required=True)
    a=p.parse_args();package(a.root,a.stage)
