"""Shape-checked, hash-bound optional C++ evaluator. CDLL releases the GIL."""
from pathlib import Path
import ctypes,hashlib,json,platform
import numpy as np

class NativeRing:
    def __init__(self,build_dir):
        build_dir=Path(build_dir).resolve();r=json.loads((build_dir/'BUILD.json').read_text())
        src=Path(__file__).resolve().parent/'native/ring_sp.cpp';lib=build_dir/'libring_sp.so'
        sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
        if r.get('schema')!='BASS_TP2A_NATIVE_BUILD_V1' or r.get('source_sha256')!=sha(src) or r.get('library_sha256')!=sha(lib):
            raise ValueError('native source/binary identity mismatch')
        if r.get('machine')!=platform.machine() or r.get('system')!=platform.system():raise ValueError('native host architecture mismatch')
        self.receipt=r;self.library=ctypes.CDLL(str(lib))
        f=self.library.bass_ring_sp_v1
        ptr=ctypes.POINTER(ctypes.c_double)
        f.argtypes=[ctypes.c_size_t]*3+[ptr]*8;f.restype=ctypes.c_int
        self.function=f
    def __call__(self,r,xyz,channels,velocity):
        from fast_cross import _P,_Y00
        r=np.asarray(r,float);xyz=np.asarray(xyz,float);velocity=np.asarray(velocity,float)
        if (r.ndim!=1 or xyz.ndim!=3 or xyz.shape[0]!=len(r) or xyz.shape[2]!=3 or
            velocity.shape!=(3,) or not np.isfinite(xyz).all() or not np.isfinite(velocity).all() or
            not np.isfinite(r).all() or np.any(r<=0) or not len(channels) or len(channels)>128):
            raise ValueError('invalid native input shape/domain')
        nr,nf,_=xyz.shape;nc=len(channels)
        av=np.empty((nr,nc));ar=np.empty_like(av);q=np.zeros((nc,4),complex);memo={}
        for i,c in enumerate(channels):
            if c.radial.l not in (0,1):raise ValueError('native s+p scope exceeded')
            if c.radial.identity not in memo:memo[c.radial.identity]=c.radial.evaluate(r)
            u,du=memo[c.radial.identity];ell=c.radial.l
            av[:,i]=u/r**(ell+1);ar[:,i]=(du/r**(ell+1)-(ell+1)*u/r**(ell+2))/r
            if ell==0:q[i,0]=_Y00
            else:q[i,1:]=_P[c.m]
        B=np.empty((nr*nf,nc),complex);G=np.empty((3,nr*nf,nc),complex);D=np.empty_like(B)
        arrays=[np.ascontiguousarray(x) for x in (xyz,av,ar,q,velocity,B,G,D)]
        ptr=ctypes.POINTER(ctypes.c_double)
        rc=self.function(nr,nf,nc,*(a.ctypes.data_as(ptr) for a in arrays))
        if rc:raise RuntimeError('native ring evaluator rejected dimensions')
        if not all(np.isfinite(a).all() for a in (B,G,D)):raise ArithmeticError('nonfinite native result')
        return B,G,D
