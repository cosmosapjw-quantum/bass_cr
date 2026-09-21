from __future__ import annotations

def get_backend(name='auto'):
    name=str(name).lower()
    if name not in {'auto','numpy','cupy'}:
        raise ValueError('backend must be auto/numpy/cupy')
    if name in {'auto','cupy'}:
        try:
            import cupy as cp
            if cp.cuda.runtime.getDeviceCount()>0:
                return cp, 'cupy'
        except Exception:
            if name=='cupy':
                raise
    import numpy as np
    return np, 'numpy'

def asnumpy(x):
    try:
        import cupy as cp
        if isinstance(x,cp.ndarray): return cp.asnumpy(x)
    except Exception: pass
    return x
