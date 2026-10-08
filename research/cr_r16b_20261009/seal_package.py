"""Deterministic immutable research archive from a committed science tree."""
import argparse,hashlib,json,subprocess,zipfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--archive',type=Path,required=True);a=p.parse_args();repo=a.repo
commit=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip();tree=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD^{tree}'],text=True).strip()
paths=subprocess.check_output(['git','-C',str(repo),'ls-files','research/cr_r16b_20261009','research/cr_r16_20261009','docs/cr_r16_20261009','AGENTS.md','docs/READBACK_POLICY.md','docs/HPC_ACCURACY_POLICY_KO.md'],text=True).splitlines()
files={name:subprocess.check_output(['git','-C',str(repo),'show',commit+':'+name]) for name in paths}
files['inputs/BASS_CR_R16_THEORY_20261009_v1.zip']=a.archive.read_bytes()
assert hashlib.sha256(files['inputs/BASS_CR_R16_THEORY_20261009_v1.zip']).hexdigest()=='b6a537d87e626831073ced6354ac20c13a6dc180f9fa846cef6a1d5b434d45d5'
manifest={'source_commit':commit,'source_tree':tree,'fixed_timestamp':'2026-10-09T00:00:00','members':{name:{'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()} for name,b in sorted(files.items())},'delivery_receipt':'detached after seal; science contents immutable','verification_scope':'source archive+member manifest+CRC; new suite only, no parent science replay'}
files['PACKAGE_MANIFEST.json']=(json.dumps(manifest,indent=2)+'\n').encode()
with zipfile.ZipFile(a.output,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for name,b in sorted(files.items()):
  i=zipfile.ZipInfo(name,date_time=(2026,10,9,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;i.external_attr=0o100644<<16;z.writestr(i,b,compresslevel=9)
with zipfile.ZipFile(a.output) as z:
 assert z.testzip() is None
 for name,row in manifest['members'].items():
  b=z.read(name);assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256']
meta={'source_commit':commit,'source_tree':tree,'local':str(a.output),'bytes':a.output.stat().st_size,'sha256':hashlib.sha256(a.output.read_bytes()).hexdigest(),'md5':hashlib.md5(a.output.read_bytes()).hexdigest(),'manifest_member_count':len(manifest['members']),'CRC_and_all_members_verified':True}
a.output.with_suffix('.metadata.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps(meta))
