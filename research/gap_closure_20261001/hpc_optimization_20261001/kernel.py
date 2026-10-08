"""Explicit new kernel identity; never masquerades as archived MomentKernel."""
from pathlib import Path
import ctypes, hashlib, json, platform
import numpy as np
from build_native import HERE, REFERENCE

class HPCMomentKernel:
    def __init__(self,directory,*,backend='fortran',threads=1):
        if backend not in ('fortran','reference'):raise ValueError('unknown backend')
        if type(threads) is not int or not 1<=threads<=64:raise ValueError('threads must be1..64')
        directory=Path(directory).resolve();rec=json.loads((directory/'BUILD_HPC.json').read_text())
        if rec.get('schema')!='BASS_HPC_STRICT_BUILD_V1' or rec['machine']!=platform.machine() or rec['system']!=platform.system():raise ValueError('build identity/architecture mismatch')
        sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
        for key,p in [('reference',REFERENCE),('fortran',HERE/'native/moment_kernel_real.f90')]:
            if sha(p)!=rec['source_hashes'][key]:raise ValueError('source identity mismatch: '+key)
        if set(rec.get('libraries',{}))!={'libreference.so','libmoments_f90.so'}:raise ValueError('complete exact library manifest required')
        for name,digest in rec['libraries'].items():
            if name not in ('libreference.so','libmoments_f90.so') or sha(directory/name)!=digest:raise ValueError('library identity mismatch')
        self.ref=ctypes.CDLL(str(directory/'libreference.so'));self.lib=ctypes.CDLL(str(directory/'libmoments_f90.so'))
        self.ptr=ctypes.POINTER(ctypes.c_double);types=[ctypes.c_size_t]*3+[self.ptr]*8+[ctypes.c_double]*3+[self.ptr]
        self.generic=self.ref.bass_moment_accumulate_v1;self.real_ref=self.ref.bass_moment_accumulate_real_v1;self.real_f90=self.lib.bass_moment_accumulate_real_f90_v1
        for f in [self.generic,self.real_ref,self.real_f90]:f.argtypes=types;f.restype=ctypes.c_int
        self.lib.omp_set_dynamic.argtypes=[ctypes.c_int];self.lib.omp_set_dynamic(0)
        self.lib.omp_set_num_threads.argtypes=[ctypes.c_int];self.lib.omp_set_num_threads(threads)
        self.lib.omp_set_max_active_levels.argtypes=[ctypes.c_int];self.lib.omp_set_max_active_levels(1)
        self.backend=backend;self.threads=threads;self.receipt=rec
        self.backend_identity='BASS_HPC_F90_REAL_V1_CXX_COMPLEX_FALLBACK' if backend=='fortran' else 'BASS_HPC_CXX_STRICT_REFERENCE_V1'
    def accumulate(self,geo,radt,radp,qt,qp,vel,weights,phase,R,charges,*,real_coefficients=False):
        n=len(geo);nt=len(qt);np_=len(qp)
        if not 0<n<=4096 or not 0<nt<=128 or not 0<np_<=128:raise ValueError('bounded native dimensions required')
        expected=[(n,4),(n,nt,2),(n,np_,2),(nt,4),(np_,4),(6,),(n,6),(n,)]
        arrays=[np.ascontiguousarray(a,dtype=d) for a,d in zip((geo,radt,radp,qt,qp,vel,weights,phase),(float,float,float,complex,complex,float,complex,complex))]
        if any(a.shape!=s or not np.isfinite(a).all() for a,s in zip(arrays,expected)):raise ValueError('shape/finiteness mismatch')
        q=np.asarray(charges,float)
        if q.shape!=(2,) or not np.isfinite([R,*q]).all() or R<=0 or np.any(q<=0) or np.any(arrays[0][:,:2]<=0):raise ValueError('positive distances/charges required')
        if real_coefficients and (np.any(arrays[3].imag!=0) or np.any(arrays[4].imag!=0)):raise ValueError('real branch rejects complex harmonics')
        f=self.generic if not real_coefficients else (self.real_f90 if self.backend=='fortran' else self.real_ref)
        # OpenMP ICVs belong to the calling thread, not this Python instance.
        # Restore this instance's configuration immediately before each call.
        self.lib.omp_set_num_threads(self.threads)
        out=np.zeros((4,nt,np_),complex)
        rc=f(n,nt,np_,*(a.ctypes.data_as(self.ptr) for a in arrays),float(R),float(q[0]),float(q[1]),out.ctypes.data_as(self.ptr))
        if rc or not np.isfinite(out).all():raise ArithmeticError('native contraction failed: '+str(rc))
        return out

def cross_with_identity(*args,kernel,**kwargs):
    """Same geometry/quadrature/assembly; caller supplies the explicit candidate.

    Import only after the existing project bootstrap has initialized its paths.
    This is an adapter, not a physical-run admission function.
    """
    from exact_cross import cross
    result=cross(*args,kernel=kernel,**kwargs)
    result['metadata']['backend']=kernel.backend_identity
    result['metadata']['kernel_build']=kernel.receipt
    result['metadata']['archived_context_compatible']=False
    return result
