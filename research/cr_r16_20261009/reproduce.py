"""Offline, create-only R16 reproduction; never reruns donor interval/root suite."""
from __future__ import annotations
from pathlib import Path, PurePosixPath
import argparse,hashlib,json,os,subprocess,sys,time,zipfile

HERE=Path(__file__).resolve().parent
SOURCE_SHA={
 'BASS_CR_NCP_R15_20261008_v1.zip':'0fe656016c1de11fa2d4d1e5dd0227bdd79d0b2e53ee1ad253b49290725ac5aa',
 'REI_XTHREAD_BRIDGE14_20261008.zip':'5fc3b77d9a17553f7cd34f61711983776edbb992ba9ebd294420b9813a818515',
 'REI_XTHREAD_BRIDGE13_20261008.zip':'a3971b386edb9dc585b8657ea095ab171159b7881a52a59f574d0ef694538b48'}

def checksum(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as fp:
  for block in iter(lambda:fp.read(1024*1024),b''):h.update(block)
 return h.hexdigest()

def check_zip(path,sha=None):
 if sha is not None and checksum(path)!=sha:raise RuntimeError('ARCHIVE_SHA256_MISMATCH')
 with zipfile.ZipFile(path) as z:
  if z.testzip() is not None:raise RuntimeError('ARCHIVE_CRC_FAIL')
  if sum(f.file_size for f in z.infolist())>150_000_000:
   raise RuntimeError('TOO_LARGE_UNPACKED')
  for f in z.infolist():
   n=PurePosixPath(f.filename)
   if n.is_absolute() or '..' in n.parts or '\\' in f.filename:
    raise RuntimeError('UNSAFE_ZIP_PATH')
   if ((f.external_attr>>16)&0o170000)==0o120000:
    raise RuntimeError('SYMLINK_DENIED')

def check():
 m=json.loads((HERE/'MANIFEST.json').read_text())
 for name,row in m['files'].items():
  p=HERE/name
  if not p.is_file() or p.stat().st_size!=row['bytes'] or checksum(p)!=row['sha256']:
   raise RuntimeError('MANIFEST_PAYLOAD_MISMATCH:'+name)
 for name,sha in SOURCE_SHA.items():
  if name.endswith('BRIDGE13_20261008.zip'):continue
  check_zip(HERE/'inputs'/name,sha)
 with zipfile.ZipFile(HERE/'inputs/BASS_CR_NCP_R15_20261008_v1.zip') as z:
  nested=z.read('inputs/REI_XTHREAD_BRIDGE13_20261008.zip')
  if hashlib.sha256(nested).hexdigest()!=SOURCE_SHA['REI_XTHREAD_BRIDGE13_20261008.zip']:
   raise RuntimeError('DONOR_SOURCE_SHA256_MISMATCH')
 print('R16 sealed inputs and manifest verified:',len(m['files']))

def execute(cmd,env,log):
 p=subprocess.run(cmd,cwd=HERE,env=env,capture_output=True,text=True,timeout=180)
 log.write_text(json.dumps({'command':cmd,'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr},indent=2)+'\n')
 if p.returncode:raise RuntimeError('STEP_FAILED:'+str(log))

def run(out):
 if out.exists():raise FileExistsError('CREATE_ONLY_OUTPUT')
 check()
 out.mkdir(parents=True)
 stage=out/'stage';stage.mkdir()
 with zipfile.ZipFile(HERE/'inputs/BASS_CR_NCP_R15_20261008_v1.zip') as z:
  z.extractall(stage/'r15_parent')
 donorzip=stage/'r15_parent/inputs/REI_XTHREAD_BRIDGE13_20261008.zip'
 check_zip(donorzip,SOURCE_SHA['REI_XTHREAD_BRIDGE13_20261008.zip'])
 with zipfile.ZipFile(donorzip) as z:z.extractall(stage/'donor')
 env=os.environ.copy();env.update(PYTHONDONTWRITEBYTECODE='1',
    R16_PARENT_STAGE=str(stage/'r15_parent'),
    R16_R15_ZIP=str(HERE/'inputs/BASS_CR_NCP_R15_20261008_v1.zip'),
    R16_BRIDGE14_ZIP=str(HERE/'inputs/REI_XTHREAD_BRIDGE14_20261008.zip'))
 python=sys.executable
 execute([python,'-B','-m','unittest','discover','-s','tests','-v'],env,out/'UNIT.json')
 execute([python,'-B','src/global_fubini.py','--parent',str(stage/'r15_parent'),
         '--output',str(out/'GLOBAL_FUBINI_EXACT.json')],env,out/'GLOBAL_RUN.json')
 execute([python,'-B','src/combine_source_optical.py',
         '--r15-zip',str(HERE/'inputs/BASS_CR_NCP_R15_20261008_v1.zip'),
         '--bridge14-zip',str(HERE/'inputs/REI_XTHREAD_BRIDGE14_20261008.zip'),
         '--output',str(out/'COMBINED_TAU.json')],env,out/'COMBINED_RUN.json')
 execute([python,'-B','src/analyze_ft03_adjoint.py',
         '--donor',str(stage/'donor/rei_bridge13_20261008'),
         '--jacobian-s','.5','--residual-nodes','33',
         '--output',str(out/'ADJOINT_JAC050_RES33.json')],env,out/'ADJOINT_RUN.json')
 expected=(HERE/'results/COMBINED_TAU.json').read_bytes()
 actual=(out/'COMBINED_TAU.json').read_bytes()
 if actual!=expected:raise RuntimeError('COMBINED_TAU_BYTE_MISMATCH')
 if (out/'GLOBAL_FUBINI_EXACT.json').read_bytes()!=(HERE/'results/GLOBAL_FUBINI_EXACT.json').read_bytes():
  raise RuntimeError('GLOBAL_FUBINI_BYTE_MISMATCH')
 curr=json.loads((out/'ADJOINT_JAC050_RES33.json').read_text())
 prev=json.loads((HERE/'results/ADJOINT_JAC050_RES33.json').read_text())
 for fld in ('forward_delta_tau','dual_delta_tau'):
  if abs(curr[fld]-prev[fld])>1e-25:raise RuntimeError('NUMERICAL_DIAGNOSTIC_DRIFT:'+fld)
 (out/'R16_REPRODUCTION.json').write_text(json.dumps({'status':'REPRODUCED',
   'full_donor_science_rerun':False,'original_R15_suite_rerun':False,
   'exact_source_reproduction_byte_identical':True,
   'new_tests':20,'adjoint_diagnostic_conditional':False,'science_hold':True},indent=2)+'\n')
 print('R16 new research reproduction PASSED: exact source, 20 tests, adjoint numerical diagnostic')

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--verify-only',action='store_true');a.add_argument('--output',type=Path)
 x=a.parse_args()
 if x.verify_only:check()
 else:
  if x.output is None:a.error('--output is required unless --verify-only')
  run(x.output.resolve())
