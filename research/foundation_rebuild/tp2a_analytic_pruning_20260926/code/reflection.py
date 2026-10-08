"""Exact collision-plane invariant-sector transformation for complete s+p sets.

Planarity and complete magnetic multiplets are mathematical preconditions, not
numerical smallness screens. No diffuse radial state is removed. The four odd
p_y channels decouple only for a reflection-even initial state and no symmetry-
breaking interaction. This is a finite-model symmetry, not basis completeness.
"""
import numpy as np

def sector_transform(channels,trajectory):
    channels=tuple(channels);n=len(channels)
    if any(c.radial.l not in (0,1) for c in channels):raise ValueError('s+p reflection adapter only')
    if not (trajectory.origins[0,1]==trajectory.origins[1,1] and np.all(trajectory.velocities[:,1]==0)):
        raise ValueError('exact fixed collision plane required; odd sector cannot be pruned')
    index={}
    for i,c in enumerate(channels):
        key=(c.center,c.radial.identity)
        if c.m in index.setdefault(key,{}):raise ValueError('duplicate m')
        index[key][c.m]=i
    even=[];odd=[];labels=[];oddlabels=[]
    for (center,radial),ms in index.items():
        ell=channels[next(iter(ms.values()))].radial.l
        if ell==0:
            if set(ms)!={0}:raise ValueError('invalid s multiplet')
            col=np.zeros(n,complex);col[ms[0]]=1;even.append(col);labels.append((center,radial,'s'))
        else:
            if set(ms)!={-1,0,1}:raise ValueError('complete p multiplet required')
            px=np.zeros(n,complex);px[ms[-1]]=1/np.sqrt(2);px[ms[1]]=-1/np.sqrt(2)
            pz=np.zeros(n,complex);pz[ms[0]]=1
            py=np.zeros(n,complex);py[ms[-1]]=1j/np.sqrt(2);py[ms[1]]=1j/np.sqrt(2)
            even.extend([px,pz]);odd.append(py);labels.extend([(center,radial,'px'),(center,radial,'pz')]);oddlabels.append((center,radial,'py'))
    U=np.column_stack(even+odd);ne=len(even)
    if np.linalg.norm(U.conj().T@U-np.eye(n))>1e-13:raise ValueError('invalid sector basis')
    return U,ne,labels+oddlabels

def prune_even(full,c0,channels,trajectory,*,numerical_tolerance=1e-12):
    U,ne,labels=sector_transform(channels,trajectory);c=np.asarray(c0,complex)
    if c.shape!=(len(channels),) or not np.isfinite(c).all():raise ValueError('finite initial vector required')
    transformed=U.conj().T@c
    if np.count_nonzero(transformed[ne:])!=0:
        raise ValueError('initial state has odd-sector support; pruning forbidden even for tiny physical amplitudes')
    matrices={};defects={}
    for name in ('S','H','D'):
        mat=np.asarray(full[name],complex)
        if mat.shape!=(len(c),len(c)) or not np.isfinite(mat).all():raise ValueError('finite full matrices required')
        a=U.conj().T@mat@U;den=max(1.,np.linalg.norm(a))
        defect=max(np.linalg.norm(a[:ne,ne:]),np.linalg.norm(a[ne:,:ne]))/den
        if defect>numerical_tolerance:raise ValueError('operator violates plane symmetry')
        matrices[name]=a[:ne,:ne];defects[name]=float(defect)
    return {'matrices':matrices,'initial_coefficients':transformed[:ne],'embedding':U[:,:ne],
            'metadata':{'full_dimension':len(c),'even_dimension':ne,'odd_dimension':len(c)-ne,
                        'off_sector_relative':defects,'scope':'EXACT_PLANAR_EVEN_FINITE_MODEL_ONLY','capture_execution_allowed':False}}
