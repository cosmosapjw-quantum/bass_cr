"""H-only update of a pinned R4AB snapshot, preserving every other array."""
import numpy as np

CHANGED=frozenset(('H','T__H','P__H','T__V_other','P__V_other'))

def reassemble(parent,potentials,velocities):
    if set(potentials)!={'T','P'}:raise ValueError('both centers required')
    v=np.asarray(velocities,float)
    if v.shape!=(2,3) or not np.isfinite(v).all():raise ValueError('velocity shape/finite mismatch')
    new={k:np.array(a,copy=True) for k,a in parent.items()}
    n=new['S'].shape[0]
    if new['S'].shape!=(n,n) or n%2:raise ValueError('even square block layout required')
    nt=n//2
    for c,lab in enumerate(('T','P')):
        sl=slice(c*nt,(c+1)*nt);pot=np.asarray(potentials[lab],complex)
        if pot.shape!=(nt,nt) or not np.isfinite(pot).all():raise ValueError('potential shape/finite mismatch')
        if not np.array_equal(parent[lab+'__indices'],np.arange(c*nt,(c+1)*nt)):raise ValueError('ordered channel indices mismatch')
        S,H0,A=(parent[lab+'__'+k] for k in ('S','H0','A'))
        if S.shape!=(nt,nt) or H0.shape!=(nt,nt) or A.shape!=(3,nt,nt):raise ValueError('intrinsic shape mismatch')
        vA=np.tensordot(v[c],A,axes=(0,0));v2=float(v[c]@v[c])
        H=H0+pot+.5j*(vA.conj().T-vA)+.5*v2*S
        new[lab+'__V_other']=pot.copy();new[lab+'__H']=H;new['H'][sl,sl]=H
    for k in parent:
        if k not in CHANGED and not np.array_equal(new[k],parent[k]):raise ArithmeticError('immutable array changed: '+k)
    for sl1,sl2 in ((slice(0,nt),slice(nt,n)),(slice(nt,n),slice(0,nt))):
        if not np.array_equal(new['H'][sl1,sl2],parent['H'][sl1,sl2]):raise ArithmeticError('cross H changed')
    return new
