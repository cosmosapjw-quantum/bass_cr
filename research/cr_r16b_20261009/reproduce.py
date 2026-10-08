"""Create-only offline reproduction of new R16B science; no parent suites."""
import argparse,hashlib,json,os,subprocess,sys,zipfile
from pathlib import Path,PurePosixPath
HERE=Path(__file__).resolve().parent
PIN='b6a537d87e626831073ced6354ac20c13a6dc180f9fa846cef6a1d5b434d45d5'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def verify_manifest(root,name,key):
    manifest=json.loads((root/name).read_text())
    for name,v in manifest[key].items():
        p=root/name
        if not p.is_file() or p.stat().st_size!=v['bytes'] or sha(p)!=v['sha256']:raise ValueError('MANIFEST:'+name)
    return len(manifest[key])
def unpack(zpath,dest):
    dest.mkdir(parents=True,exist_ok=False)
    with zipfile.ZipFile(zpath) as z:
        if z.testzip():raise ValueError('CRC')
        if sum(v.file_size for v in z.infolist())>300_000_000:raise ValueError('UNPACK_LIMIT')
        seen=set()
        for v in z.infolist():
            p=PurePosixPath(v.filename)
            if p.is_absolute() or '..' in p.parts or '\\' in v.filename or v.filename in seen or ((v.external_attr>>16)&0o170000)==0o120000:raise ValueError('UNSAFE_MEMBER')
            seen.add(v.filename)
        z.extractall(dest)
def execute(cmd,cwd,env,log,timeout=900):
    p=subprocess.run(cmd,cwd=cwd,env=env,capture_output=True,text=True,timeout=timeout)
    log.write_text(json.dumps({'command':cmd,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr},indent=2)+'\n')
    if p.returncode:raise RuntimeError('FAILED:'+str(log))
def main(archive,out,workers,verify_only):
    if sha(archive)!=PIN:raise ValueError('R16_ARCHIVE_IDENTITY')
    out.mkdir(parents=True,exist_ok=False)
    bundle=HERE.parents[1]
    if (bundle/'PACKAGE_MANIFEST.json').is_file():verify_manifest(bundle,'PACKAGE_MANIFEST.json','members')
    unpack(archive,out/'r16');r16=out/'r16/BASS_CR_R16_THEORY_20261009'
    verify_manifest(r16,'MANIFEST.json','files')
    stage=out/'stage';stage.mkdir();unpack(r16/'inputs/BASS_CR_NCP_R15_20261008_v1.zip',stage/'r15')
    verify_manifest(stage/'r15','PACKAGE_MANIFEST.json','members')
    unpack(stage/'r15/inputs/REI_XTHREAD_BRIDGE13_20261008.zip',stage/'donor')
    unpack(stage/'r15/inputs/BASS_CR_XTHREAD_R14_20261008_v1.zip',stage/'r14')
    env=os.environ.copy();env.update(R16B_STAGE=str(stage),PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
    execute([sys.executable,'-B','reproduce.py','--verify-only'],r16,env,out/'PARENT_MANIFEST_ONLY.json')
    execute([sys.executable,'-B','-m','unittest','-v','test_validated','test_contract','test_finalize'],HERE,env,out/'NEW_UNIT.json')
    if verify_only:
        print('PASS_VERIFY_ONLY_NEW_TESTS_NO_PARENT_SCIENCE');return
    aff=len(os.sched_getaffinity(0));avail=int(next(l.split()[1] for l in Path('/proc/meminfo').read_text().splitlines() if l.startswith('MemAvailable:')))*1024
    if workers>min(8,aff-1) or avail<25*1024**3:raise ValueError('RESOURCE_RESERVE_1CPU_24GiB')
    execute([sys.executable,'-B','run_certificate.py','--stage',str(stage),'--output',str(out/'new_science'),'--workers',str(workers),'--panels','64'],HERE,env,out/'NEW_SCIENCE.json')
    execute([sys.executable,'-B','mpfr_check.py','--prepared',str(out/'new_science'),'--output',str(out/'MPFR256_CHECK.json')],HERE,env,out/'MPFR_RUN.json')
    execute([sys.executable,'-B','finalize_math.py','--result',str(out/'new_science'),'--r16root',str(r16),'--mpfr',str(out/'MPFR256_CHECK.json'),'--output',str(out/'math')],HERE,env,out/'FINALIZE_RUN.json')
    expected=json.loads((HERE/'results/final_v2/R16B_RESULTS.json').read_text());actual=json.loads((out/'new_science/R16B_RESULTS.json').read_text())
    for key in ('signed_optical_depth_interval','dimension_progression','full_time_panels','status'):
        if actual[key]!=expected[key]:raise ValueError('REPRODUCTION_DRIFT:'+key)
    if (out/'math/COMBINED_TAU_R16B.json').read_bytes()!=(HERE/'results/final_math/COMBINED_TAU_R16B.json').read_bytes():raise ValueError('SOURCE_COMBINATION_DRIFT')
    print('PASS_NEW_R16B_SCIENCE_NO_PARENT_SUITE')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--archive',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--workers',type=int,default=8);p.add_argument('--verify-only',action='store_true');a=p.parse_args()
    if not 1<=a.workers<=8:p.error('BOUNDED_WORKERS')
    main(a.archive.resolve(),a.output.resolve(),a.workers,a.verify_only)
