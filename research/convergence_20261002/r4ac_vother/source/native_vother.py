"""Source-bound, strict binary64 radial evaluator; no cross-scattering entrypoint."""
from __future__ import annotations
from pathlib import Path
import ctypes,hashlib,json,subprocess,math
import numpy as np
from numpy.polynomial.legendre import leggauss
from vother_certificate import validate_arrays

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def build(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    src=Path(__file__).with_name('vother_fixed.f90');lib=out/'libr4ac.so'
    cmd=['gfortran','-O3','-fPIC','-shared','-fno-fast-math','-ffp-contract=off','-fprotect-parens','-ffree-line-length-none','-J'+str(out),str(src),'-o',str(lib)]
    p=subprocess.run(cmd,capture_output=True,text=True,timeout=60)
    (out/'stdout.txt').write_text(p.stdout);(out/'stderr.txt').write_text(p.stderr)
    d={'command':cmd,'exit_code':p.returncode,'source_sha256':sha(src),'compiler':subprocess.check_output(['gfortran','--version'],text=True).splitlines()[0],'threads':1}
    if p.returncode==0:d['library_sha256']=sha(lib)
    (out/'BUILD.json').write_text(json.dumps(d,indent=2)+'\n')
    if p.returncode:raise RuntimeError('native build failed; logs retained')
    return out/'BUILD.json'

class Native:
    def __init__(self,manifest):
        self.manifest=Path(manifest);d=json.loads(self.manifest.read_text());lib=self.manifest.parent/'libr4ac.so'
        if d.get('exit_code')!=0 or sha(lib)!=d['library_sha256'] or sha(Path(__file__).with_name('vother_fixed.f90'))!=d['source_sha256']:raise ValueError('native source/library identity mismatch')
        if any(f not in d['command'] for f in ('-fno-fast-math','-ffp-contract=off','-fprotect-parens')) or any(f in d['command'] for f in ('-Ofast','-ffast-math','-fassociative-math')):raise ValueError('strict FP contract mismatch')
        self.handle=ctypes.CDLL(str(lib.resolve()));self.fn=self.handle.r4ac_radial
        ptr=np.ctypeslib.ndpointer(dtype=np.float64,flags='F_CONTIGUOUS')
        self.fn.argtypes=[ctypes.c_int]*3+[ptr]*3+[ctypes.c_double]+[ptr]*3+[ctypes.POINTER(ctypes.c_int)]
        self.fn.restype=None;self.metadata=d
    def radial(self,edges,endpoints,bubbles,distance,order=32):
        e,p,q=validate_arrays(edges,endpoints,bubbles)
        if isinstance(order,bool) or not isinstance(order,int) or not 5<=order<=64 or not math.isfinite(distance) or distance<=0:raise ValueError('positive radius and integer GL5..64 required')
        x,w=leggauss(order);out=np.zeros((len(p),len(p),3),float,order='F');status=ctypes.c_int(-1)
        self.fn(len(p),len(e)-1,order,np.asfortranarray(e),np.asfortranarray(p),np.asfortranarray(q),distance,np.asfortranarray(x),np.asfortranarray(w),out,ctypes.byref(status))
        if status.value!=0 or not np.isfinite(out).all():raise ArithmeticError('native V radial failure: '+str(status.value))
        return np.moveaxis(out,-1,0).copy()

def angular_matrix(radial,lm,mode_indices,delta,charge=1.):
    d=np.asarray(delta,float)
    if d.shape!=(3,) or not np.isfinite(d).all() or d[1]!=0 or not math.isfinite(charge) or charge<=0:raise ValueError('scoped plane/charge mismatch')
    R=math.sqrt(float(d@d))
    if R<=0:raise ValueError('separated centers required')
    d=d/R;u={-1:d[0]/math.sqrt(2),0:d[2],1:-d[0]/math.sqrt(2)}
    n=len(lm)
    if len(mode_indices)!=n or any(l not in (0,1) or not -l<=m<=l for l,m in lm):raise ValueError('s+p channel map required')
    if np.asarray(radial).ndim!=3 or np.asarray(radial).shape[0]!=3 or not np.isfinite(radial).all() or any(not 0<=i<np.asarray(radial).shape[1] for i in mode_indices):raise ValueError('radial map mismatch')
    out=np.zeros((n,n),complex)
    for a,(la,ma) in enumerate(lm):
        for b,(lb,mb) in enumerate(lm):
            ia,ib=mode_indices[a],mode_indices[b];v=0.
            if la==lb and ma==mb:v+=radial[0,ia,ib]
            if la==0 and lb==1:v+=radial[1,ia,ib]*u[mb]/math.sqrt(3)
            if la==1 and lb==0:v+=radial[1,ia,ib]*u[ma]/math.sqrt(3)
            if la==lb==1:v+=radial[2,ia,ib]*(3*u[ma]*u[mb]-int(ma==mb))/5
            out[a,b]=-charge*v
    return out
