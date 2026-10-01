"""R4X diagnostic-only continuous endpoint-factored degree-four radial bank.

The stored FP64 arrays define a NEW exact piecewise polynomial.  Original
pre-monomial nodal coefficients are unavailable and are never claimed recovered.
This object deliberately has no polynomial_coefficients attribute and does not
inherit FEMRadial: legacy native providers must fail rather than misread it.
"""
from __future__ import annotations
import ctypes
from dataclasses import dataclass, field
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import os
import shutil
import subprocess
import numpy as np

HERE = Path(__file__).resolve().parent
SCHEMA = 'BASS_R4X_CONTINUOUS_ENDPOINT_BASIS_V1'
ALGORITHM = 'u=(1-s)*left+s*right+s*(1-s)*q(s); degree=4; no renormalization'

def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)

def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()

def _fp64(a, shape=None, name='array'):
    a = np.asarray(a)
    if a.dtype != np.dtype('float64') or (shape is not None and a.shape != shape) or not np.isfinite(a).all():
        raise ValueError(f'{name}: finite float64 of shape {shape} required')
    a = np.array(a, copy=True, order='C'); a.setflags(write=False)
    return a

def _integer(x, lo, hi, name):
    if isinstance(x, (bool, np.bool_)) or not isinstance(x, (int, np.integer)) or not lo <= x <= hi:
        raise ValueError(f'{name}: integer in [{lo},{hi}] required')
    return int(x)

def _mode_record(m):
    required = {'l', 'principal_n', 'energy', 'identity', 'residual'}
    if set(m) != required: raise ValueError('unexpected mode metadata keys')
    _integer(m['l'], 0, 3, 'l')
    if m['principal_n'] is not None: _integer(m['principal_n'], m['l']+1, 4, 'principal_n')
    for k in ('energy', 'residual'):
        if isinstance(m[k], bool) or not isinstance(m[k], (int, float)) or not np.isfinite(m[k]): raise ValueError('invalid mode scalar')
    if m['residual'] < 0: raise ValueError('negative residual')
    if not isinstance(m['identity'], str) or len(m['identity']) != 64 or any(c not in '0123456789abcdef' for c in m['identity']): raise ValueError('invalid mode identity')

def validate_original(npz_path, meta_path, expected_npz_sha256, expected_meta_sha256):
    if sha256(npz_path) != expected_npz_sha256 or sha256(meta_path) != expected_meta_sha256:
        raise ValueError('original input SHA256 mismatch')
    meta = json.loads(Path(meta_path).read_text())
    if meta.get('schema') != 'BASS_TP2A_BASIS_V1' or meta.get('matrix_sha256') != expected_npz_sha256:
        raise ValueError('original bank schema or matrix binding mismatch')
    if not isinstance(meta.get('modes'), list) or not 1 <= len(meta['modes']) <= 32: raise ValueError('invalid modes')
    for m in meta['modes']: _mode_record(m)
    original_payload = dict(meta); original_identity = original_payload.pop('identity', None)
    if digest(original_payload) != original_identity: raise ValueError('original bank identity mismatch')
    with np.load(npz_path, allow_pickle=False) as z:
        if set(z.files) != {'edges', 'coefficients'}: raise ValueError('unexpected original NPZ keys')
        edges = _fp64(z['edges'], name='edges'); coef = _fp64(z['coefficients'], name='coefficients')
    if edges.ndim != 1 or not 3 <= len(edges) <= 121 or edges[0] != 0 or np.any(np.diff(edges) <= 0): raise ValueError('invalid mesh')
    if coef.shape != (len(meta['modes']), len(edges)-1, 5): raise ValueError('R4X supports exactly degree four')
    return edges, coef, meta

def exact_coefficients(mode):
    """Exact rational monomial EXPANSION for audit only, never a native payload."""
    rows = []
    for e in range(len(mode.edges)-1):
        left, right = map(Fraction.from_float, map(float, mode.shared_endpoint_values[e:e+2]))
        q0, q1, q2 = map(Fraction.from_float, map(float, mode.bubble_coefficients[e]))
        rows.append([left, right-left+q0, q1-q0, q2-q1, -q2])
    return rows

def reconstructed_nodes(endpoints, bubbles):
    """Rounded exact samples of the candidate; NOT original lost nodal data."""
    nodes = np.empty((len(endpoints)-1)*4+1, dtype=np.float64)
    for e, q in enumerate(bubbles):
        left, right = map(Fraction.from_float, map(float, endpoints[e:e+2]))
        qq = list(map(Fraction.from_float, map(float, q)))
        for j in range(4):
            s = Fraction(j, 4)
            value = (1-s)*left+s*right+s*(1-s)*(qq[0]+s*(qq[1]+s*qq[2]))
            nodes[4*e+j] = float(value)
    nodes[-1] = endpoints[-1]
    return nodes

def _array_digest(a):
    return digest({'shape': list(a.shape), 'dtype': a.dtype.str, 'bytes_sha256': hashlib.sha256(a.tobytes(order='C')).hexdigest()})

def _source_identity():
    return {name: sha256(HERE/name) for name in ('basis_representation.py', 'continuous_kernel.f90')}

def _mode_identity(m, edges, endpoints, bubbles, nodes):
    return digest({'schema':SCHEMA,'algorithm':ALGORITHM,'original_mode':m,
                   'arrays':{k:_array_digest(a) for k,a in [('edges',edges),('shared_endpoint_values',endpoints),('bubble_coefficients',bubbles),('reconstructed_nodal_values',nodes)]}})

def validate_continuous_radial(mode):
    if not isinstance(mode,ContinuousRadial): raise TypeError('ContinuousRadial required')
    m={'l':mode.l,'principal_n':mode.principal_n,'energy':mode.energy,'identity':mode.original_identity,'residual':mode.residual}
    actual=_mode_identity(m,mode.edges,mode.shared_endpoint_values,mode.bubble_coefficients,mode.reconstructed_nodal_values)
    if actual!=mode.identity: raise ValueError('candidate payload identity mismatch')
    return actual

def build_candidate(npz_path, meta_path, output_dir, expected_npz_sha256, expected_meta_sha256):
    edges, coef, original = validate_original(npz_path, meta_path, expected_npz_sha256, expected_meta_sha256)
    out = Path(output_dir); out.mkdir(parents=True, exist_ok=True)
    if (out/'CANDIDATE.npz').exists() or (out/'CANDIDATE.json').exists(): raise FileExistsError('candidate outputs are create-only')
    endpoints = np.concatenate([coef[:, :, 0], np.zeros((len(coef), 1))], axis=1)
    endpoints[:, 0] = 0.
    bubbles = np.empty((len(coef), len(edges)-1, 3), dtype=np.float64)
    bubble_rounding = []
    for k in range(len(coef)):
        largest = Fraction(0)
        for e, c in enumerate(coef[k]):
            cf = list(map(Fraction.from_float, map(float, c)))
            for j in range(3):
                exact = -sum(cf[j+2:], Fraction(0)); bubbles[k,e,j] = float(exact)
                largest = max(largest, abs(Fraction.from_float(float(bubbles[k,e,j]))-exact))
        bubble_rounding.append({'max_absolute_exact_bubble_rounding': str(largest), 'float': float(largest)})
    nodes = np.array([reconstructed_nodes(ep, q) for ep, q in zip(endpoints, bubbles)])
    arrays = {'edges': edges, 'shared_endpoint_values': endpoints, 'bubble_coefficients': bubbles, 'reconstructed_nodal_values': nodes}
    np.savez(out/'CANDIDATE.npz', **arrays)
    result = {'schema': SCHEMA, 'algorithm': ALGORITHM, 'production_adopted': False,
              'legacy_native_compatible': False, 'original_nodal_data_recovered': False,
              'original_inputs': {'BASIS.npz': expected_npz_sha256, 'BASIS.json': expected_meta_sha256},
              'original_basis_identity': original['identity'], 'modes': original['modes'],
              'source_hashes': _source_identity(), 'array_digests': {k: _array_digest(a) for k,a in arrays.items()},
              'candidate_npz_sha256': sha256(out/'CANDIDATE.npz'), 'bubble_rounding': bubble_rounding}
    result['identity'] = digest(result)
    (out/'CANDIDATE.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    return result

@dataclass(frozen=True)
class ContinuousRadial:
    l: int
    principal_n: int | None
    energy: float
    edges: np.ndarray
    shared_endpoint_values: np.ndarray
    bubble_coefficients: np.ndarray
    reconstructed_nodal_values: np.ndarray
    original_identity: str
    identity: str
    residual: float  # inherited original-bank metadata, NOT candidate residual
    backend: str = 'python'
    native: object = field(default=None, repr=False, compare=False)
    threads: int = 1
    degree: int = 4

    def __post_init__(self):
        _mode_record({'l': self.l, 'principal_n': self.principal_n, 'energy': self.energy, 'identity': self.original_identity, 'residual': self.residual})
        edges = _fp64(self.edges, name='edges')
        if edges.ndim != 1 or not 3 <= len(edges) <= 121 or edges[0] != 0 or np.any(np.diff(edges) <= 0): raise ValueError('invalid candidate mesh')
        n = len(edges)-1
        for name, shape in [('shared_endpoint_values', (n+1,)), ('bubble_coefficients', (n,3)), ('reconstructed_nodal_values', (4*n+1,))]:
            object.__setattr__(self, name, _fp64(getattr(self,name), shape, name))
        object.__setattr__(self, 'edges', edges)
        if self.shared_endpoint_values[0] != 0 or self.shared_endpoint_values[-1] != 0: raise ValueError('nonzero Dirichlet endpoint')
        if not np.array_equal(reconstructed_nodes(self.shared_endpoint_values,self.bubble_coefficients), self.reconstructed_nodal_values): raise ValueError('candidate nodal samples mismatch')
        _integer(self.threads,1,64,'threads')
        if self.degree != 4 or self.backend not in ('python','fortran') or (self.backend == 'fortran' and self.native is None): raise ValueError('invalid evaluator backend')
        if not isinstance(self.identity,str) or len(self.identity)!=64: raise ValueError('invalid candidate identity')
        validate_continuous_radial(self)

    def payload_fingerprint(self):
        return validate_continuous_radial(self)

    def evaluate(self, r):
        validate_continuous_radial(self)
        raw = np.asarray(r)
        if np.iscomplexobj(raw) or raw.dtype.kind not in 'fiu': raise ValueError('real numeric radii required')
        rr = np.asarray(raw,dtype=np.float64)
        if np.any(rr < 0) or not np.isfinite(rr).all(): raise ValueError('nonnegative finite radii required')
        flat = rr.ravel(); u = np.zeros_like(flat); du = np.zeros_like(flat)
        active = flat < self.edges[-1]; x = flat[active]
        cells = np.searchsorted(self.edges,x,side='right')-1
        h = self.edges[cells+1]-self.edges[cells]; s = (x-self.edges[cells])/h
        if self.backend == 'fortran':
            uv, dv = self.native.evaluate(self, cells, s, h, self.threads)
        else:
            left = self.shared_endpoint_values[cells]; right = self.shared_endpoint_values[cells+1]
            q0,q1,q2 = self.bubble_coefficients[cells].T
            q = (q2*s+q1)*s+q0; dq = (2*q2)*s+q1
            uv = (1-s)*left+s*right+(s*(1-s))*q
            dv = ((right-left)+(1-2*s)*q+(s*(1-s))*dq)/h
        # At literal mesh boundaries choose the stored shared endpoint exactly.
        # This agrees with the exact function trace; du uses the right cell.
        boundary = x == self.edges[cells]
        uv[boundary] = self.shared_endpoint_values[cells[boundary]]
        if not np.isfinite(uv).all() or not np.isfinite(dv).all(): raise ArithmeticError('evaluator returned nonfinite')
        u[active] = uv; du[active] = dv
        return u.reshape(rr.shape), du.reshape(rr.shape)

def load_candidate(directory, backend='python', native_manifest=None, threads=1):
    directory = Path(directory); meta = json.loads((directory/'CANDIDATE.json').read_text())
    payload = dict(meta); identity = payload.pop('identity', None)
    if digest(payload) != identity or meta.get('schema') != SCHEMA or meta.get('algorithm') != ALGORITHM: raise ValueError('candidate metadata identity mismatch')
    if meta.get('production_adopted') is not False or meta.get('legacy_native_compatible') is not False or meta.get('original_nodal_data_recovered') is not False: raise ValueError('candidate scope mismatch')
    if meta.get('source_hashes') != _source_identity(): raise ValueError('candidate source identity mismatch; rebuild explicitly')
    if sha256(directory/'CANDIDATE.npz') != meta['candidate_npz_sha256']: raise ValueError('candidate NPZ SHA mismatch')
    expected = {'edges','shared_endpoint_values','bubble_coefficients','reconstructed_nodal_values'}
    with np.load(directory/'CANDIDATE.npz',allow_pickle=False) as z:
        if set(z.files) != expected: raise ValueError('unexpected candidate NPZ keys')
        a = {k:_fp64(z[k],name=k) for k in z.files}
    if {k:_array_digest(v) for k,v in a.items()} != meta['array_digests']: raise ValueError('candidate array identities mismatch')
    modes = meta.get('modes')
    if not isinstance(modes,list) or not 1<=len(modes)<=32: raise ValueError('invalid candidate modes')
    ne = len(a['edges'])-1
    shapes = {'shared_endpoint_values':(len(modes),ne+1),'bubble_coefficients':(len(modes),ne,3),'reconstructed_nodal_values':(len(modes),4*ne+1)}
    for k,s in shapes.items():
        if a[k].shape != s: raise ValueError('candidate bank shape mismatch')
    native = NativeEvaluator(native_manifest) if backend == 'fortran' else None
    return tuple(ContinuousRadial(m['l'],m['principal_n'],m['energy'],a['edges'],a['shared_endpoint_values'][k],a['bubble_coefficients'][k],a['reconstructed_nodal_values'][k],m['identity'],_mode_identity(m,a['edges'],a['shared_endpoint_values'][k],a['bubble_coefficients'][k],a['reconstructed_nodal_values'][k]),m['residual'],backend,native,threads) for k,m in enumerate(modes))

def compile_kernel(output_dir, compiler='gfortran'):
    out=Path(output_dir).resolve(); out.mkdir(parents=True,exist_ok=True)
    manifest=out/'NATIVE_BUILD.json'
    if manifest.exists() or (out/'libcontinuous.so').exists(): raise FileExistsError('native build outputs are create-only')
    fc=shutil.which(compiler)
    if fc is None: raise RuntimeError('Fortran compiler unavailable; no build claimed')
    cmd=[fc,'-O3','-fPIC','-shared','-fno-fast-math','-ffp-contract=off','-fprotect-parens','-fopenmp','-ffree-line-length-none','-fopt-info-vec-optimized='+str(out/'VECTORIZATION.txt'),str(HERE/'continuous_kernel.f90'),'-o',str(out/'libcontinuous.so')]
    result=subprocess.run(cmd,capture_output=True,text=True,check=False)
    (out/'BUILD.stdout').write_text(result.stdout);(out/'BUILD.stderr').write_text(result.stderr)
    rec={'schema':'BASS_R4X_CONTINUOUS_NATIVE_V1','command':cmd,'exit_code':result.returncode,'compiler_version':subprocess.check_output([fc,'--version'],text=True).splitlines()[0], 'compiler_entrypoint_sha256':sha256(fc), 'source_hashes':_source_identity(), 'physical_admission':False}
    frontend=subprocess.check_output([fc,'-print-prog-name=f951'],text=True).strip()
    rec['compiler_frontend']={'path':str(Path(frontend).resolve()),'sha256':sha256(frontend)}
    if result.returncode == 0: rec['library_sha256']=sha256(out/'libcontinuous.so')
    manifest.write_text(json.dumps(rec,indent=2)+'\n')
    if result.returncode: raise RuntimeError('Fortran compilation failed; logs preserved')
    return rec

def admitted_cpus():
    count=len(os.sched_getaffinity(0)) if hasattr(os,'sched_getaffinity') else (os.cpu_count() or 1)
    p=Path('/sys/fs/cgroup/cpu.max')
    if p.exists():
        q,period=p.read_text().split()
        if q!='max': count=min(count,max(1,int(q)//int(period)))
    return count

class NativeEvaluator:
    def __init__(self,manifest):
        if manifest is None: raise ValueError('native manifest required')
        p=Path(manifest);m=json.loads(p.read_text());lib=p.parent/'libcontinuous.so'
        if m.get('schema')!='BASS_R4X_CONTINUOUS_NATIVE_V1' or m.get('exit_code')!=0 or m.get('source_hashes')!=_source_identity() or sha256(lib)!=m.get('library_sha256'): raise ValueError('native identity mismatch')
        cmd=m.get('command',[])
        for flag in ('-O3','-fno-fast-math','-ffp-contract=off','-fprotect-parens','-fopenmp'):
            if flag not in cmd: raise ValueError('strict compiler flags missing')
        if any(x in cmd for x in ('-Ofast','-ffast-math','-fassociative-math')): raise ValueError('unsafe compiler flags')
        self.library=ctypes.CDLL(str(lib.resolve()));self.fn=self.library.continuous_eval
        pointer=np.ctypeslib.ndpointer(dtype=np.float64,flags='C_CONTIGUOUS');ints=np.ctypeslib.ndpointer(dtype=np.int32,flags='C_CONTIGUOUS')
        self.fn.argtypes=[ctypes.c_int,ctypes.c_int,ints,pointer,pointer,pointer,pointer,ctypes.c_int,pointer,pointer,ctypes.POINTER(ctypes.c_int)]
        self.fn.restype=None;self.last_observed_threads=0

    def evaluate(self,mode,cells,s,h,threads):
        _integer(threads,1,min(64,admitted_cpus()),'threads')
        validate_continuous_radial(mode)
        cells=np.asarray(cells);s=np.asarray(s);h=np.asarray(h)
        if cells.ndim!=1 or cells.dtype.kind not in 'iu' or s.dtype!=np.dtype('float64') or h.dtype!=np.dtype('float64') or s.shape!=cells.shape or h.shape!=cells.shape:
            raise ValueError('native input vector shapes/dtypes invalid')
        if len(s)>2147483647 or np.any(cells<0) or np.any(cells>=len(mode.edges)-1) or not np.isfinite(s).all() or not np.isfinite(h).all() or np.any(s<0) or np.any(s>1) or np.any(h<=0):
            raise ValueError('native input values invalid')
        n=len(s);u=np.empty(n);du=np.empty(n);observed=ctypes.c_int(0)
        self.fn(n,len(mode.edges)-1,np.ascontiguousarray(cells,dtype=np.int32),np.ascontiguousarray(s),np.ascontiguousarray(h),mode.shared_endpoint_values,mode.bubble_coefficients,threads,u,du,ctypes.byref(observed))
        self.last_observed_threads=observed.value
        if n and observed.value!=threads: raise RuntimeError('actual OpenMP thread count differs from requested')
        if not np.isfinite(u).all() or not np.isfinite(du).all(): raise ArithmeticError('native evaluator returned nonfinite')
        return u,du
