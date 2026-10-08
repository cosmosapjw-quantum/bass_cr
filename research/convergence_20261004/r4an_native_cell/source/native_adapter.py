"""Bounded native numerical cell sum. No approval or full atomic batch interface.

Scientific units are inherited from R4AM: a0, Eh, ta=hbar/Eh.
The native program sums real-path nodes only; analytic remainders stay with the
pinned Python reference and must be added before making an accuracy claim.
"""
from pathlib import Path
from fractions import Fraction as F
import subprocess,hashlib,json,os,resource,time
from dyadic import I,SCALE,pi_interval
from complex_box import C
ROOT=Path(__file__).resolve().parents[1]
BINARY=ROOT/'build/weak_cell'
KEYS=('S_TP','H_TP','D_TP','K_TP')

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def build():
    src=ROOT/'source/weak_cell.cpp';lock=ROOT/'build/BUILD.json'
    if BINARY.exists():
        d=json.loads(lock.read_text())
        if d['source_sha256']!=sha(src) or d['native_sha256']!=sha(BINARY):
            raise ValueError('build identity changed; use a fresh build directory')
        return d
    BINARY.parent.mkdir(exist_ok=True)
    cmd=['g++','-std=c++17','-O2','-fno-fast-math','-ffp-contract=off',str(src),'-lgmpxx','-lgmp','-o',str(BINARY)]
    start=time.monotonic();p=subprocess.run(cmd,capture_output=True,text=True,timeout=90)
    (ROOT/'build/COMPILE.stdout').write_text(p.stdout);(ROOT/'build/COMPILE.stderr').write_text(p.stderr)
    if p.returncode:raise RuntimeError('native compile failed: '+p.stderr)
    deps=subprocess.run(['ldd',str(BINARY)],capture_output=True,text=True,check=True).stdout
    libraries={}
    for line in deps.splitlines():
        paths=[x for x in line.split() if x.startswith('/')]
        for x in paths:
            if Path(x).is_file():libraries[x]=sha(x)
    d={'command':cmd,'source_sha256':sha(src),'native_sha256':sha(BINARY),'wall_seconds':time.monotonic()-start,'compiler':subprocess.run(['g++','--version'],capture_output=True,text=True,check=True).stdout,'libraries':libraries}
    lock.write_text(json.dumps(d,indent=2));return d

def serialize(candidate,cell,ctx,entry,samples):
    if candidate.profile!='SYNTHETIC_FIXTURE':raise ValueError('R4AN fixture-only; a new finite-candidate execution contract is required')
    if len(entry)!=4:raise ValueError('four entry indices required')
    a,b,ma,mb=entry
    if any(type(x) is not int for x in entry):raise ValueError('integer entry indices')
    if not(0<=a<len(candidate.ells) and 0<=b<len(candidate.ells)):raise ValueError('mode index')
    if not(-candidate.ells[a]<=ma<=candidate.ells[a] and -candidate.ells[b]<=mb<=candidate.ells[b]):raise ValueError('harmonic m')
    if cell.kind not in ('regular','origin_T','origin_P'):raise ValueError('chart kind')
    if not 1<=len(samples)<=16384:raise ValueError('bounded sample count')
    if not (0<=cell.i<len(candidate.edges)-1 and 0<=cell.j<len(candidate.edges)-1):raise ValueError('panel index')
    if cell.kind=='regular' and (cell.triangle is None or min(cell.i,cell.j)<1):raise ValueError('regular origin cell')
    if cell.kind=='origin_T' and cell.i!=0:raise ValueError('origin_T panel')
    if cell.kind=='origin_P' and cell.j!=0:raise ValueError('origin_P panel')
    out=['R4AN_CELL_V1 256',str(('regular','origin_T','origin_P').index(cell.kind))]
    def put(x):
        q=I(x);out.append(f'{q.lo} {q.hi}')
    for x in (ctx.b,ctx.z,ctx.v,ctx.R,ctx.nu,ctx.t,candidate.edges[1],pi_interval()):put(x)
    for mode,panel,m in ((a,cell.i,ma),(b,cell.j,mb)):
        out.append(f'{candidate.ells[mode]} {m}');lo,hi=candidate.edges[panel:panel+2]
        put(lo);put(hi-lo)
        if len(candidate.coeffs[mode][panel])!=5:raise ValueError('quartic coefficient contract')
        for x in candidate.coeffs[mode][panel]:put(x)
    if cell.kind=='regular':
        for x,y in cell.triangle.vertices:put(x.at(ctx.R));put(y.at(ctx.R))
        put(cell.triangle.det_range(ctx.R))
    else:
        for _ in range(6):put(0)
        put(1)
    out.append(str(len(samples)))
    for u,w,weight in samples:
        u,w,weight=I(u),I(w),I(weight)
        if not (0<=u.lo<=u.hi<=SCALE and 0<=w.lo<=w.hi<=SCALE and weight.lo>=0):raise ValueError('sample domain/weight')
        put(u);put(w);put(weight)
    text='\n'.join(out)+'\n'
    if len(text)>16*1024*1024:raise ValueError('input size cap')
    return text

def _limits():
    resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2))
    resource.setrlimit(resource.RLIMIT_CPU,(120,120))

def invoke(text,timeout=120):
    if not isinstance(text,str) or len(text)>16*1024**2:raise ValueError('bounded text input required')
    build()
    p=subprocess.run([str(BINARY)],input=text,capture_output=True,text=True,timeout=timeout,preexec_fn=_limits)
    if p.returncode:raise RuntimeError(p.stderr.strip())
    lines=p.stdout.splitlines()
    if len(lines)!=5 or not lines[0].startswith('R4AN_NUMERIC_V1 256 '):raise ValueError('native output schema')
    result={}
    for expected,line in zip(KEYS,lines[1:]):
        toks=line.split()
        if len(toks)!=5 or toks[0]!=expected:raise ValueError('native key/order')
        a,b,c,d=map(int,toks[1:]);result[expected]=C(I.raw(a,b),I.raw(c,d))
    return result

def evaluate(candidate,cell,ctx,entry,samples):
    return invoke(serialize(candidate,cell,ctx,entry,samples))
