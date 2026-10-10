"""Block linearization for instantaneous gas and existing photons."""
import numpy as np

def blocks(j_nonphoto, photons, kappa, grad_kappa, yield_vectors):
    ng=len(j_nonphoto); n=len(photons)
    J=np.zeros((ng+n,ng+n))
    J[:ng,:ng]=j_nonphoto+np.einsum('j,ij,jk->ik',photons,yield_vectors,grad_kappa)
    J[:ng,ng:]=yield_vectors*kappa
    J[ng:,:ng]=-photons[:,None]*grad_kappa
    J[ng:,ng:]=-np.diag(kappa)
    return J
