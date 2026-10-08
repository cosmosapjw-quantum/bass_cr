"""Small-matrix diagnostic checks for a moving nonorthogonal basis."""
import numpy as np
from .core import ContractError

def metric_defect(S,dotS,H,D,hbar:float):
    mats=[np.asarray(a,dtype=complex) for a in (S,dotS,H,D)]
    S,dotS,H,D=mats
    if S.ndim!=2 or S.shape[0]!=S.shape[1] or any(a.shape!=S.shape for a in mats):
        raise ContractError('square compatible matrices required')
    if not np.isfinite(hbar) or hbar<=0 or any(not np.isfinite(a).all() for a in mats):
        raise ContractError('finite matrices and positive hbar required')
    if not np.allclose(S,S.conj().T,rtol=0,atol=1e-13) or not np.allclose(dotS,dotS.conj().T,rtol=0,atol=1e-13):
        raise ContractError('S and dotS must be Hermitian')
    try: L=np.linalg.cholesky(S)
    except np.linalg.LinAlgError as e: raise ContractError('S is not positive definite') from e
    K=dotS-D-D.conj().T+1j*(H.conj().T-H)/hbar
    left=np.linalg.solve(L,K)
    B=np.linalg.solve(L,left.conj().T).conj().T
    # This is a floating diagnostic at one time, NOT a continuous norm certificate.
    return {'K':K,'relative_spectral_norm':float(np.linalg.norm(B,2)),
            'status':'POINTWISE_FLOATING_DIAGNOSTIC_NOT_A_TIME_ENCLOSURE'}
