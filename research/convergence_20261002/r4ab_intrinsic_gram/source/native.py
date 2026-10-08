"""Build/pin the small strict-FP64 radial kernel. No atomic cross backend."""
from pathlib import Path
import ctypes,json,subprocess
import numpy as np
from numpy.polynomial.legendre import leggauss
from gram_exact import validate_arrays,sha
KEYS=('G','J','T','R1','R2')

def build(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    src=Path(__file__).with_name('gram_fixed.f90');lib=out/'libr4ab.so'
    cmd=['gfortran','-O3','-fPIC','-shared','-fno-fast-math','-ffp-contract=off','-fprotect-parens','-ffree-line-length-none','-J'+str(out),str(src),'-o',str(lib)]
    p=subprocess.run(cmd,capture_output=True,text=True,timeout=60)
    (out/'stdout.txt').write_text(p.stdout);(out/'stderr.txt').write_text(p.stderr)
    d={'command':cmd,'exit_code':p.returncode,'source_sha256':sha(src),'compiler':subprocess.check_output(['gfortran','--version'],text=True).splitlines()[0],'kernel_threads':1,'new_cross_calls':0}
    if p.returncode==0:d['library_sha256']=sha(lib)
    (out/'BUILD.json').write_text(json.dumps(d,indent=2)+'\n')
    if p.returncode:raise RuntimeError('native build failed, logs preserved')
    return out/'BUILD.json'

class Native:
    def __init__(self,manifest):
        p=Path(manifest);d=json.loads(p.read_text());lib=p.parent/'libr4ab.so'
        if d.get('exit_code')!=0 or sha(lib)!=d['library_sha256'] or sha(Path(__file__).with_name('gram_fixed.f90'))!=d['source_sha256']:raise ValueError('native source/library identity mismatch')
        for flag in ('-fno-fast-math','-ffp-contract=off','-fprotect-parens'):
            if flag not in d['command']:raise ValueError('strict FP flag missing')
        if any(flag in d['command'] for flag in ('-Ofast','-ffast-math','-fassociative-math')):raise ValueError('unsafe floating-point flags')
        self.handle=ctypes.CDLL(str(lib.resolve()));self.fn=self.handle.r4ab_fixed_radial;ptr=np.ctypeslib.ndpointer(dtype=np.float64,flags='F_CONTIGUOUS')
        self.fn.argtypes=[ctypes.c_int]*3+[ptr]*6+[ctypes.POINTER(ctypes.c_int)];self.fn.restype=None
        self.manifest=p;self.metadata=d
    def moments(self,edges,endpoints,bubbles,order):
        e,p,q=validate_arrays(edges,endpoints,bubbles)
        if isinstance(order,bool) or not isinstance(order,int) or not 5<=order<=64:raise ValueError('Gauss order 5..64 required')
        x,w=leggauss(order);s=np.asfortranarray((x+1)*.5);w=np.asfortranarray(w*.5)
        out=np.zeros((len(p),len(p),5),dtype=np.float64,order='F');status=ctypes.c_int(-1)
        self.fn(len(p),len(e)-1,order,np.asfortranarray(e),np.asfortranarray(p),np.asfortranarray(q),s,w,out,ctypes.byref(status))
        if status.value!=0 or not np.isfinite(out).all():raise ArithmeticError('native radial failure '+str(status.value))
        return {k:out[:,:,i].copy() for i,k in enumerate(KEYS)}
