"""Research reference only: declared rank decisions are new basis identities.

No diagonal shifts, production repair, physical evaluation or certificate reuse.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
from scipy.linalg import eigh, qr, svd, subspace_angles
import scipy

HERE=Path(__file__).resolve().parent
CUTOFFS=(1e-14,1e-12,1e-10,1e-8,1e-6)


def adj(a):return a.conj().T


def checked_metric(S,relative_cutoff):
    S=np.asarray(S,dtype=complex)
    if S.ndim!=2 or S.shape[0]!=S.shape[1] or not len(S) or not np.isfinite(S).all():
        raise ValueError('finite nonempty square metric required')
    if isinstance(relative_cutoff,bool) or not np.isfinite(relative_cutoff) or not 0<relative_cutoff<1:
        raise ValueError('relative cutoff must lie in (0,1)')
    scale=float(np.linalg.norm(S,2))
    if scale==0:raise ValueError('zero metric has no nonzero retained basis')
    roundoff=64*len(S)*np.finfo(float).eps*scale
    defect=float(np.linalg.norm(S-adj(S),2))
    if defect>roundoff:raise ValueError('non-Hermitian metric')
    herm=(S+adj(S))/2;lam,U=eigh(herm)
    if lam[0]<-roundoff:raise ValueError('indefinite metric; cannot truncate it into a valid physical Gram')
    return herm,lam,U,{'input_hermiticity_defect':defect,
                      'explicit_hermitian_part_adjustment':defect/2,
                      'numerical_psd_tolerance':roundoff,
                      'min_eigenvalue':float(lam[0]),
                      'negative_within_roundoff_uncertainty':bool(lam[0]<0),
                      'PSD_status':'NUMERICAL_PSD_SCREEN_ONLY_NOT_CERTIFIED',
                      'high_precision_sign_audit_required_if_material':bool(lam[0]<0),
                      'cutoff_below_numerical_psd_tolerance':bool(relative_cutoff*lam[-1]<roundoff)}


def anchor_phases(T):
    T=T.copy()
    for k in range(T.shape[1]):
        i=int(np.argmax(np.abs(T[:,k])));z=T[i,k]
        T[:,k]*=np.conj(z)/abs(z)
    return T


def canonical_truncation(S,relative_cutoff):
    S,lam,U,diag=checked_metric(S,relative_cutoff)
    threshold=relative_cutoff*lam[-1];keep=lam>threshold
    if not np.any(keep):raise ValueError('no retained canonical directions')
    T=anchor_phases(U[:,keep]/np.sqrt(lam[keep]))
    return {'method':'canonical','relative_cutoff':float(relative_cutoff),
            'absolute_threshold':float(threshold),'rank':int(np.sum(keep)),
            'retained_eigenvalues':lam[keep].tolist(),'T':T,'diagonal_shift':0.,
            'decision_rule':'retain eigenvalues strictly greater than tau*lambda_max(S)',
            'diagnostics':diag}


def pivoted_cholesky_selection(S,relative_cutoff):
    S,lam,U,diag=checked_metric(S,relative_cutoff);n=len(S)
    threshold=relative_cutoff*lam[-1];L=np.zeros((n,0),complex)
    d=S.diagonal().real.copy();pivots=[];clip_total=0.
    for k in range(n):
        # Negative roundoff in the residual diagonal is recorded, not a shift of S.
        if float(np.min(d)) < -diag['numerical_psd_tolerance']:
            raise ValueError('pivoted residual became materially negative')
        clip_total+=float(-np.minimum(d,0.).sum());d=np.maximum(d,0.)
        if float(d.sum())<=threshold:break
        allowed=[i for i in range(n) if i not in pivots]
        if not allowed:break
        p=max(allowed,key=lambda i:d[i])
        if d[p]<=0:break
        column=(S[:,p]-L@np.conj(L[p,:]))/np.sqrt(d[p])
        L=np.column_stack((L,column));pivots.append(p)
        d-=np.abs(column)**2;d[p]=0.
    if not pivots:raise ValueError('no retained pivot directions')
    J=np.eye(n,dtype=complex)[:,pivots]
    gram=adj(J)@S@J;values,vectors=eigh((gram+adj(gram))/2)
    if values[0]<=0:raise ValueError('selected pivot Gram is not numerically positive definite')
    # Orthonormalization of selected columns is explicit and kept in identity.
    T=anchor_phases(J@(vectors/np.sqrt(values)))
    residual=S-L@adj(L)
    return {'method':'pivoted_cholesky','relative_cutoff':float(relative_cutoff),
            'absolute_threshold':float(threshold),'rank':len(pivots),'pivots':pivots,
            'T':T,'diagonal_shift':0.,
            'decision_rule':'stop when nonnegative residual diagonal trace <= tau*lambda_max(S)',
            'diagnostics':{**diag,'residual_trace':float(np.trace(residual).real),
                           'residual_spectral_norm':float(np.linalg.norm(residual,2)),
                           'residual_min_eigenvalue':float(eigh((residual+adj(residual))/2,eigvals_only=True)[0]),
                           'residual_diagonal_roundoff_clipped_total':clip_total,
                           'selected_raw_gram_condition':float(np.linalg.cond(gram))}}


def array_hash(a):
    # Shape + declared little-endian complex128 makes the content digest explicit.
    a=np.ascontiguousarray(a,dtype='<c16')
    return hashlib.sha256(json.dumps(list(a.shape)).encode()+a.tobytes()).hexdigest()


def new_basis_identity(parent_identity,S,decision):
    identity={'schema':'BASS_EXPLICIT_RANK_DECISION_V1','parent_identity':parent_identity,
              'parent_metric_sha256':array_hash(S),'method':decision['method'],
              'relative_cutoff_hex':float(decision['relative_cutoff']).hex(),
              'absolute_cutoff_hex':float(decision['absolute_threshold']).hex(),
              'rank':decision['rank'],'parent_channel_count':len(S),
              'transform_sha256':array_hash(decision['T']),
              'pivots':decision.get('pivots'),
              'transform_policy':'FROZEN_CONSTANT_TRANSFORM_ONLY',
              'decision_rule':decision['decision_rule']}
    digest=hashlib.sha256(json.dumps(identity,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return {**identity,'new_hash':digest,'new_basis_identity':'SYNTHETIC_RANK_AUDIT_'+digest[:24],
            'rank_reduced':decision['rank']<len(S),
            'new_operator_qualification_required':True,'new_temporal_certificate_required':True,
            'old_selected_indices_inheritable':False,
            'semantic_selection_status':'REQUIRES_NEW_SEMANTIC_SUBSPACE_DEFINITION',
            'physical_execution_authorized':False,'old_certificates_inherited':False}


def synthetic_case(name):
    if name not in ('near_spd','exact_psd'):raise ValueError('unknown synthetic case')
    rng=np.random.default_rng(909);n=6
    Z=rng.normal(size=(n,n))+1j*rng.normal(size=(n,n));U,_=qr(Z)
    spectrum=np.array([1.,.2,.01,3e-5,3e-9,3e-12 if name=='near_spd' else 0.])
    B=np.diag(np.sqrt(spectrum))@adj(U);S=adj(B)@B;S=(S+adj(S))/2
    h=rng.normal(size=(n,n))+1j*rng.normal(size=(n,n));h=(h+adj(h))/2
    F=B@np.eye(n)[:,:2]
    c=np.arange(1,n+1)+.3j*np.arange(n,0,-1);y=B@c;y/=np.linalg.norm(y)
    weak=np.zeros(n,complex);weak[5 if name=='near_spd' else 4]=1.
    return {'name':name,'B':B,'S':S,'h':h,'selected_F':F,'regular_state':y,
            'weak_state':weak,'intended_spectrum':spectrum}


def orthonormal_span(A,tolerance=1e-12):
    U,s,Vh=svd(A,full_matrices=False)
    return U[:,s>tolerance*s[0]] if len(s) and s[0] else np.empty((len(A),0),complex)


def physical_diagnostics(case,T):
    # All model diagnostics are synthetic physical-space constructions. The
    # projected selection is an audit prescription, never a semantic approval.
    E=orthonormal_span(case['B']@T);P=E@adj(E)
    Fcoords=adj(E)@case['selected_F'];Forth=orthonormal_span(Fcoords)
    Q=Forth@adj(Forth);h=adj(E)@case['h']@E
    W=1j*(h@Q-Q@h)
    rho=float(np.max(np.abs(eigh((W+adj(W))/2,eigvals_only=True))))
    regular=adj(E)@case['regular_state'];weak=adj(E)@case['weak_state']
    return {'rho':rho,'P_regular_unnormalized':float(np.vdot(regular,Q@regular).real),
            'P_weak_unnormalized':float(np.vdot(weak,Q@weak).real),
            'regular_state_norm_loss':float(1.-np.vdot(regular,regular).real),
            'weak_state_norm_loss':float(1.-np.vdot(weak,weak).real),
            'selected_span_rank_after_projection':Forth.shape[1],
            'physical_retained_basis':E,'physical_selected_projector':E@Q@adj(E)}


def run_case(name):
    case=synthetic_case(name);S=case['S'];n=len(S)
    full=physical_diagnostics(case,np.eye(n));rows=[];last={}
    singular=np.linalg.svd(S,compute_uv=False)
    _,R,piv=qr(case['B'],pivoting=True,mode='economic');rdiag=np.abs(np.diag(R))
    for cutoff in CUTOFFS:
        current={}
        for method in (canonical_truncation,pivoted_cholesky_selection):
            decision=method(S,cutoff);T=decision['T'];metric=adj(T)@S@T
            values=physical_diagnostics(case,T);E=values.pop('physical_retained_basis')
            Q=values.pop('physical_selected_projector');method_name=decision['method']
            identity=new_basis_identity('SYNTHETIC_G09_'+name,S,decision)
            row={k:v for k,v in decision.items() if k!='T'}
            row.update(values)
            row.update({'case':name,'parent_condition':float(np.linalg.cond(S)),
                        'retained_metric_condition':float(np.linalg.cond(metric)),
                        'metric_orthonormality_defect':float(np.linalg.norm(metric-np.eye(decision['rank']),2)),
                        'svd_rank_audit':int(np.sum(singular>cutoff*singular[0])),
                        'pivoted_QR_rank_audit':int(np.sum(rdiag>np.sqrt(cutoff*singular[0]))),
                        'rho_drift_from_full':values['rho']-full['rho'],
                        'P_regular_drift_from_full':values['P_regular_unnormalized']-full['P_regular_unnormalized'],
                        'selected_projector_drift_from_full':float(np.linalg.norm(Q-full['physical_selected_projector'],2)),
                        'rank_loss_from_full':n-decision['rank'],
                        'new_basis_identity':identity,
                        'selected_observable_semantics':'AUDIT_ONLY_PROJECT_ORIGINAL_SYNTHETIC_SELECTED_SPAN; NOT_AUTHORIZED_PHYSICAL_SELECTOR'})
            if method_name in last:
                previous=last[method_name]
                row['principal_angles_to_previous_cutoff_radians']=subspace_angles(previous,E).tolist()
                row['retained_projector_distance_to_previous']=float(np.linalg.norm(previous@adj(previous)-E@adj(E),2))
            else:
                row['principal_angles_to_previous_cutoff_radians']=None
                row['retained_projector_distance_to_previous']=None
            last[method_name]=E;current[method_name]=(row,E);rows.append(row)
        a,Ea=current['canonical'];b,Eb=current['pivoted_cholesky']
        angles=subspace_angles(Ea,Eb).tolist()
        for row in (a,b):
            row['canonical_vs_pivoted_principal_angles_radians']=angles
            row['canonical_vs_pivoted_projector_distance']=float(np.linalg.norm(Ea@adj(Ea)-Eb@adj(Eb),2))
    return rows


def run_audit():
    rows=run_case('near_spd')+run_case('exact_psd')
    result={'schema':'BASS_SYNTHETIC_RANK_POLICY_AUDIT_V1','numpy':np.__version__,
            'scipy':scipy.__version__,'predeclared_relative_cutoffs':list(CUTOFFS),
            'random_seed':909,'scope':'LOCAL_SYNTHETIC_ONLY','results':rows,
            'new_native_calls':0,'new_external_runs':0,'authorizations_consumed':0,
            'physical_B1_B3_rank_decision_made':False,'diagonal_shift_used':False}
    (HERE/'RANK_POLICY_RESULTS.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'cases':2,'decisions':len(rows),'native_calls':0,'physical_basis_changed':False}))


if __name__=='__main__':run_audit()
