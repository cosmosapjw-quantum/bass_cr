#!/usr/bin/env python3
"""Explicit optional CPU native build. No package install or source overwrite."""
from pathlib import Path
import argparse,hashlib,json,platform,shutil,subprocess,sys
HERE=Path(__file__).resolve().parent
FLAGS=['-std=c++17','-O3','-fPIC','-shared','-ffp-contract=off','-Wall','-Wextra','-Werror']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def build(out,cxx='g++'):
    out=Path(out).resolve()
    if out.exists():raise FileExistsError('create-only build output exists')
    compiler=shutil.which(cxx)
    if not compiler:raise RuntimeError('compiler unavailable; use --backend numpy or install compiler manually')
    out.mkdir(parents=True)
    src=HERE/'native/ring_sp.cpp';lib=out/'libring_sp.so'
    cmd=[compiler,*FLAGS,str(src),'-o',str(lib)]
    p=subprocess.run(cmd,text=True,capture_output=True)
    (out/'build.stdout').write_text(p.stdout);(out/'build.stderr').write_text(p.stderr)
    if p.returncode:raise RuntimeError('native compilation failed; see build.stderr')
    receipt={'schema':'BASS_TP2A_NATIVE_BUILD_V1','source_sha256':sha(src),'library_sha256':sha(lib),'library_name':lib.name,
             'compiler':compiler,'compiler_version':subprocess.check_output([compiler,'--version'],text=True),
             'command':cmd,'flags':FLAGS,'machine':platform.machine(),'system':platform.system(),'python':sys.version}
    (out/'BUILD.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return receipt
if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',required=True);ap.add_argument('--cxx',default='g++');a=ap.parse_args()
    print(json.dumps(build(a.out,a.cxx),indent=2))
