"""Deterministic artificial ABI inputs, never an archived B0 physics sample."""
import numpy as np
def inputs(n=1024,nt=9,np_=9,seed=391,moving=False,complex_coefficients=False):
    rng=np.random.default_rng(seed)
    geo=np.column_stack((rng.uniform(.5,5,n),rng.uniform(.5,5,n),rng.uniform(-1,1,n),rng.uniform(0,2,n)))
    radt=rng.normal(size=(n,nt,2));radp=rng.normal(size=(n,np_,2))
    qt=rng.normal(size=(nt,4)).astype(complex);qp=rng.normal(size=(np_,4)).astype(complex)
    if complex_coefficients:qt+=1j*rng.normal(size=qt.shape);qp+=1j*rng.normal(size=qp.shape)
    vel=np.array([.1,-.25,.17,.5,1.1,2.0]) if moving else np.array([0.,0.,0.,.5,1.1,2.0])
    weights=rng.normal(size=(n,6))+1j*rng.normal(size=(n,6));phase=rng.normal(size=n)+1j*rng.normal(size=n)
    return [geo,radt,radp,qt,qp,vel,weights,phase,2.,(1.,1.)]
