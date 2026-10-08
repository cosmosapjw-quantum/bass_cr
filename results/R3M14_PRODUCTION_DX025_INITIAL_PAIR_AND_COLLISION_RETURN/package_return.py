"""Create a fresh archive and validate each member against the payload manifest."""
from pathlib import Path
import os,json,hashlib,shutil,subprocess,tarfile,time
O=Path('/mnt/sn850x2t/bass_cr_r3m14_20260922'); P=O/'production_return';P.mkdir(exist_ok=False)
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
for name in ['initial025','initial0125','collision0125','report','receipts']:
    shutil.copytree(O/name,P/name,copy_function=os.link)
for p in O.glob('*.stdout'):os.link(p,P/p.name)
for p in O.glob('*.stderr'):os.link(p,P/p.name)
for name in ['pair.json','trace_command.py','run_chunks.py','build_report.py','package_return.py']:
    shutil.copy2(O/name,P/name)
for name in ['cr_repro','configs/r3m13','tests','scripts']:
    # Full source/tests/scripts are small; no old output/evidence or .git copied.
    shutil.copytree(O/'worktree'/name,P/'source'/name,ignore=shutil.ignore_patterns('__pycache__'))
for name in ['pyproject.toml']:
    shutil.copy2(O/'worktree'/name,P/'source'/name)
files=[{'path':str(p.relative_to(P)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(P.rglob('*')) if p.is_file()]
manifest={'schema':'BASS_CR_R3M14_PRODUCTION_ARCHIVE_MANIFEST_V1','work_unit':'R3M14_PRODUCTION_DX025_INITIAL_PAIR_AND_COLLISION_RETURN','decision':'NO_GO','files':files,'archive_sha_location':'detached ARCHIVE.json; no self-reference','old_r3m12_drive_backup':'UNCHANGED_1_OF_19'}
(P/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
(P/'MANIFEST.sha256').write_text(''.join(f"{r['sha256']}  {r['path']}\n" for r in files))
A=O/'BASS_CR_R3M14_PRODUCTION_RETURN_20260922_v1.tar.zst';assert not A.exists()
tic=time.time();subprocess.run(['tar','-I','zstd -T4 -3','-cf',str(A),'-C',str(P),'.'],check=True)
proc=subprocess.Popen(['zstd','-dc',str(A)],stdout=subprocess.PIPE)
expected={r['path']:r for r in files}; seen=set()
with tarfile.open(fileobj=proc.stdout,mode='r|') as t:
 for m in t:
  if not m.isfile():continue
  n=m.name.removeprefix('./')
  if n in ['MANIFEST.json','MANIFEST.sha256']:continue
  assert n in expected
  h=hashlib.file_digest(t.extractfile(m),'sha256').hexdigest()
  assert h==expected[n]['sha256'] and m.size==expected[n]['bytes'],n
  seen.add(n)
assert proc.wait()==0 and seen==set(expected)
A.chmod(0o444)
info={'schema':'BASS_CR_R3M14_ARCHIVE_IDENTITY_V1','name':A.name,'path':str(A),'bytes':A.stat().st_size,'sha256':sha(A),'manifest_sha256':sha(P/'MANIFEST.json'),'verified_members':len(seen),'status':'ALL_ARCHIVED_MEMBER_BYTES_VERIFIED','pack_and_verify_seconds':time.time()-tic}
(O/'ARCHIVE.json').write_text(json.dumps(info,indent=2)+'\n')
parts=O/'drive_parts';parts.mkdir(exist_ok=False);size=32*1024*1024;total=(A.stat().st_size+size-1)//size;rows=[]
assert total<=64
with A.open('rb') as f:
 for i in range(1,total+1):
  p=parts/f'{A.name}.part{i:03d}of{total:03d}';p.write_bytes(f.read(size));p.chmod(0o444)
  rows.append({'index':i,'name':p.name,'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'status':'LOCAL_PART_READY'})
(O/'DRIVE_PARTS.json').write_text(json.dumps({'archive':info,'ordered_parts':rows,'dual_backup_complete':False},indent=2)+'\n')
print(json.dumps(info,indent=2));print('parts',total)
