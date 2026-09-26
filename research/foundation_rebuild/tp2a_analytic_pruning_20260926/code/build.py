from pathlib import Path
import hashlib,json,subprocess,shutil,argparse,platform
HERE=Path(__file__).resolve().parent
FLAGS=['-std=c++17','-O3','-fPIC','-shared','-ffp-contract=off','-Wall','-Wextra','-Werror']
def build(out):
    out=Path(out).resolve()
    if out.exists():raise FileExistsError('create-only build output exists')
    compiler=shutil.which('g++')
    if not compiler:raise RuntimeError('g++ required; no automatic installation')
    out.mkdir(parents=True)
    cmd=[compiler,*FLAGS,str(HERE/'moment_kernel.cpp'),'-o',str(out/'libmoments.so')]
    p=subprocess.run(cmd,capture_output=True,text=True)
    (out/'stdout.txt').write_text(p.stdout);(out/'stderr.txt').write_text(p.stderr)
    if p.returncode:raise RuntimeError(p.stderr)
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    r={'schema':'BASS_ANALYTIC_MOMENTS_BUILD_V1','source_sha256':sha(HERE/'moment_kernel.cpp'),'library_sha256':sha(out/'libmoments.so'),'machine':platform.machine(),'system':platform.system(),'command':cmd,'compiler_version':subprocess.check_output([compiler,'--version'],text=True)}
    (out/'BUILD.json').write_text(json.dumps(r,indent=2)+'\n');return r
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args();print(json.dumps(build(a.out),indent=2))
