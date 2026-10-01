"""Research-only, finite-matrix conditioning and covariance audits.

This module starts no native calls, changes no production evaluator, regularizes
no metric, and cannot produce a physical tail certificate.
"""
from decimal import Decimal, localcontext
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import numpy as np
import scipy
from scipy.linalg import cholesky, eigh, solve_triangular

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
PROBE_PATH = REPO/'research/foundation_rebuild/ncp_shared_research_20260928/r4p0a_b0_static_tail_executor_20260930/projector_rate_probe.py'
EPS = np.finfo(float).eps


def adj(a): return a.conj().T


def hermitian_input(a, name):
    a = np.asarray(a, dtype=np.complex128)
    if a.ndim != 2 or a.shape[0] != a.shape[1] or not len(a) or not np.isfinite(a).all():
        raise ValueError(f'{name}: nonempty finite square matrix required')
    size = float(np.linalg.norm(a, 2))
    defect = float(np.linalg.norm(a-adj(a), 2))
    relative = defect/max(size, np.finfo(float).tiny)
    if relative > 500*EPS:
        raise ValueError(f'{name}: Hermiticity defect exceeds explicit 500-eps admission')
    # The returned diagnostics disclose this bounded Hermitian-part projection.
    return (a+adj(a))/2, {'absolute':defect, 'relative':relative,
                         'hermitian_part_adjustment_norm':defect/2}


def eigen_diagnostics(S, W, eigenvalues, vectors):
    ns=float(np.linalg.norm(S,2)); nw=float(np.linalg.norm(W,2))
    residuals=[]; backward=[]; wscaled=[]
    for value, vector in zip(eigenvalues, vectors.T):
        residual=float(np.linalg.norm(W@vector-value*(S@vector),2))
        nv=float(np.linalg.norm(vector))
        residuals.append(residual)
        backward.append(residual/max((nw+abs(value)*ns)*nv,np.finfo(float).tiny))
        wscaled.append(residual/max(nw*nv,np.finfo(float).tiny))
    return {'eigenvalues':eigenvalues.tolist(),
            'rho':float(np.max(np.abs(eigenvalues))),
            'max_absolute_eigen_residual':max(residuals),
            'max_W_scaled_eigen_residual':max(wscaled),
            'max_normwise_backward_error':max(backward),
            'rho_eigenpair_normwise_backward_error':backward[int(np.argmax(np.abs(eigenvalues)))],
            'S_orthogonality_defect':float(np.linalg.norm(adj(vectors)@S@vectors-np.eye(len(S)),2))}


def audit_pencil(S, W):
    S, sd=hermitian_input(S,'S'); W, wd=hermitian_input(W,'W')
    if S.shape != W.shape: raise ValueError('S/W shape mismatch')
    # A failed factorization is propagated. No shifts/clipping/truncation.
    L=cholesky(S,lower=True,check_finite=True)
    ea,va=eigh(W,S,type=1,driver='gvd',check_finite=True)
    left=solve_triangular(L,W,lower=True)
    C=adj(solve_triangular(L,adj(left),lower=True))
    cdef=float(np.linalg.norm(C-adj(C),2))
    eb,y=eigh((C+adj(C))/2,driver='evr',check_finite=True)
    vb=solve_triangular(adj(L),y,lower=False)
    da=eigen_diagnostics(S,W,ea,va); db=eigen_diagnostics(S,W,eb,vb)
    return {'S_condition':float(np.linalg.cond(S)),
            'S_min_eigenvalue_diagnostic':float(np.linalg.eigvalsh(S)[0]),
            'S_hermiticity':sd,'W_hermiticity':wd,
            'whitened_hermiticity_defect_absolute':cdef,
            'whitened_hermiticity_defect_relative':cdef/max(float(np.linalg.norm(C,2)),np.finfo(float).tiny),
            'path_a':da,'path_b':db,
            'rho_relative_discrepancy':abs(da['rho']-db['rho'])/max(da['rho'],db['rho'],np.finfo(float).tiny),
            'estimated_condition_amplifier_eps_condS':EPS*float(np.linalg.cond(S)),
            'diagonal_shift':0., 'metric_rank_truncation':False}


def conditioning_cases(dimension=6):
    rng=np.random.default_rng(707+dimension)
    z=rng.normal(size=(dimension,dimension))+1j*rng.normal(size=(dimension,dimension))
    U,_=np.linalg.qr(z)
    z=rng.normal(size=(dimension,dimension))+1j*rng.normal(size=(dimension,dimension))
    fixed_W=(z+adj(z))/2
    for kappa in [1.,1e4,1e8,1e12]:
        S=(U*np.geomspace(1.,1./kappa,dimension))@adj(U); S=(S+adj(S))/2
        yield {'name':f'complex_{dimension}x{dimension}_fixed_W_cond_{kappa:.0e}',
               'target_condition':kappa,'S':S,'W':fixed_W}


def decimal_pencil_eigenvalues(S,W,precision=100):
    """Analytic Hermitian 2x2 generalized roots of exact input float bytes.

    Uses Decimal.from_float and 100-digit arithmetic, rather than an unrounded
    intended generator. This independently measures eigensolver forward error.
    It is a high-precision audit, not directed-rounding interval certification.
    """
    S=np.asarray(S,complex); W=np.asarray(W,complex)
    if S.shape!=(2,2) or W.shape!=(2,2): raise ValueError('2x2 required')
    if not np.array_equal(S,adj(S)) or not np.array_equal(W,adj(W)):
        raise ValueError('exact Hermitian input required for decimal lane')
    D=lambda x: Decimal.from_float(float(x))
    with localcontext() as ctx:
        ctx.prec=precision
        s0,s1=D(S[0,0].real),D(S[1,1].real)
        sr,si=D(S[0,1].real),D(S[0,1].imag)
        w0,w1=D(W[0,0].real),D(W[1,1].real)
        wr,wi=D(W[0,1].real),D(W[0,1].imag)
        a=s0*s1-sr*sr-si*si
        if s0<=0 or a<=0: raise ValueError('exact rounded 2x2 S not SPD')
        b=-(w0*s1+w1*s0-2*(wr*sr+wi*si)); c=w0*w1-wr*wr-wi*wi
        disc=b*b-4*a*c
        if disc<0: raise ValueError('nonreal generalized roots')
        root=disc.sqrt()
        # Cancellation-avoiding quadratic roots, with exact repeated-zero case.
        q=-(b+(root if b>=0 else -root))/2
        roots=[q/a,c/q] if q else [Decimal(0),Decimal(0)]
        return sorted(roots)


def load_historical_probe():
    spec=importlib.util.spec_from_file_location('bass_historical_projector_rate_probe',PROBE_PATH)
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def metric_projected_coupling_norm(S,K,U,V):
    """New diagnostic: ||P_U K restricted to V|| in the S metric.

    U,V must be full-column-rank subspace maps, K a coefficient operator.
    Different diagnostic and name from raw ||K_TP||. It does not by itself
    measure transfer probability or a rate for time-dependent subspaces.
    """
    S,_=hermitian_input(S,'S'); cholesky(S,lower=True)
    Lu=cholesky(adj(U)@S@U,lower=True)
    Lv=cholesky(adj(V)@S@V,lower=True)
    left=solve_triangular(Lu,adj(U)@S@K@V,lower=True)
    coupling=adj(solve_triangular(Lv,adj(left),lower=True))
    return float(np.linalg.norm(coupling,2))


def covariance_case(seed):
    rng=np.random.default_rng(seed); n=6
    z=rng.normal(size=(n,n))+1j*rng.normal(size=(n,n))
    U,_=np.linalg.qr(z); S=(U*np.geomspace(1.,12.,n))@adj(U); S=(S+adj(S))/2
    z=rng.normal(size=(n,n))+1j*rng.normal(size=(n,n)); H=(z+adj(z))/2
    D=.1*(rng.normal(size=(n,n))+1j*rng.normal(size=(n,n)))
    J=np.eye(n,dtype=complex)[:,[0,2]]
    c=rng.normal(size=n)+1j*rng.normal(size=n); c/=np.sqrt(np.vdot(c,S@c).real)
    left,_=np.linalg.qr(rng.normal(size=(n,n))+1j*rng.normal(size=(n,n)))
    right,_=np.linalg.qr(rng.normal(size=(n,n))+1j*rng.normal(size=(n,n)))
    T=(left*np.geomspace(1.,5.,n))@adj(right)
    Sp=adj(T)@S@T; Hp=adj(T)@H@T; Dp=adj(T)@D@T
    cp=np.linalg.solve(T,c); Jp=np.linalg.solve(T,J)
    probe=load_historical_probe(); a=probe.rate_matrices(S,H,D,J,hbar=1.)
    b=probe.rate_matrices(Sp,Hp,Dp,Jp,hbar=1.)
    Pi=np.linalg.solve(S,a['Q']); Pip=np.linalg.solve(Sp,b['Q'])
    eig=eigh(a['W'],S,eigvals_only=True); eigp=eigh(b['W'],Sp,eigvals_only=True)
    Usel=np.eye(n,dtype=complex)[:,:2]; Vsel=np.eye(n,dtype=complex)[:,2:]
    coupling=metric_projected_coupling_norm(S,a['A'],Usel,Vsel)
    couplingp=metric_projected_coupling_norm(Sp,b['A'],np.linalg.solve(T,Usel),np.linalg.solve(T,Vsel))
    def rel(x,y): return float(np.linalg.norm(x-y)/max(np.linalg.norm(x),np.linalg.norm(y),1e-300))
    defects={
        'norm':rel(np.vdot(c,S@c),np.vdot(cp,Sp@cp)),
        'P_selected':rel(np.vdot(c,a['Q']@c),np.vdot(cp,b['Q']@cp)),
        'Q_congruence':rel(b['Q'],adj(T)@a['Q']@T),
        'Qdot_congruence':rel(b['Qdot'],adj(T)@a['Qdot']@T),
        'Pi_similarity':rel(Pip,np.linalg.solve(T,Pi@T)),
        'Pi_idempotence':rel(Pi@Pi,Pi),
        'Pi_S_self_adjointness':rel(adj(Pi)@S,S@Pi),
        'Q_Hermiticity':rel(adj(a['Q']),a['Q']),
        'A_similarity':rel(b['A'],np.linalg.solve(T,a['A']@T)),
        'W_congruence':rel(b['W'],adj(T)@a['W']@T),
        'generalized_spectrum':rel(eig,eigp),
        'rho':rel(a['rho'],b['rho']),
        'metric_projected_coupling':rel(coupling,couplingp)}
    return {'seed':seed,'dimension':n,'T_condition':float(np.linalg.cond(T)),
            'S_condition':float(np.linalg.cond(S)),
            'transformed_S_condition':float(np.linalg.cond(Sp)),
            'relative_defects':defects}


def raw_block_counterexample():
    S=np.eye(2); K=np.array([[0.,1.],[1.,0.]]); T=np.diag([10.,1.])
    Sp=adj(T)@S@T; Kp=np.linalg.solve(T,K@T)
    U=np.eye(2)[:,:1]; V=np.eye(2)[:,1:]
    return {'T':T.tolist(),'K':K.tolist(),'S_transformed':Sp.tolist(),
            'K_transformed':Kp.tolist(),
            'raw_block_before':float(abs(K[0,1])),
            'raw_block_after':float(abs(Kp[0,1])),
            'metric_coupling_before':metric_projected_coupling_norm(S,K,U,V),
            'metric_coupling_after':metric_projected_coupling_norm(Sp,Kp,np.linalg.solve(T,U),np.linalg.solve(T,V))}


def saved_physical_audit():
    bundle=json.loads((HERE/'PHYSICAL_MATRIX_FIXTURES.json').read_text())
    probe=load_historical_probe(); rows=[]
    for item in bundle['fixtures']:
        arrays={}
        for key,data in item['arrays_real_imag'].items():
            parts=np.asarray(data,dtype=float); arrays[key]=parts[...,0]+1j*parts[...,1]
        S,H,D=[arrays[key] for key in ('S','H','D')]
        J=np.eye(len(S),dtype=complex)[:,bundle['selected_indices']]
        result=probe.rate_matrices(S,H,D,J,hbar=1.)
        audit=audit_pencil(S,(result['W']+adj(result['W']))/2)
        e=np.array(audit['path_a']['eigenvalues']); top=np.sort(np.abs(e))[::-1]
        rows.append({'z_a0':item['z_a0'],'query_id':item['query_id'],
                     'npz_sha256':item['npz_sha256'],'npz_bytes':item['npz_bytes'],
                     'archived_rho':item['archived_rho'],'recomputed_probe_rho':result['rho'],
                     'archived_rho_relative_discrepancy':abs(result['rho']-item['archived_rho'])/item['archived_rho'],
                     'probe_W_hermiticity_defect':result['W_hermiticity_defect'],
                     'explicit_roundoff_projection_for_audit':'(W+W_dagger)/2; raw defect separately retained',
                     'top_abs_eigenvalues':top[:4].tolist(),
                     'gap_largest_to_second_abs':float(top[0]-top[1]),
                     'gap_second_to_third_abs':float(top[1]-top[2]),
                     'state_attached':False,'pencil_audit':audit})
    return rows


def run_audits():
    sweep=[]
    for case in conditioning_cases():
        sweep.append({'name':case['name'],'target_condition':case['target_condition'],
                      **audit_pencil(case['S'],case['W'])})
    high_precision=[]
    for case in conditioning_cases(dimension=2):
        r=audit_pencil(case['S'],case['W']); ref=decimal_pencil_eigenvalues(case['S'],case['W'])
        ref_rho=max(abs(float(x)) for x in ref)
        r.update({'name':case['name'],'target_condition':case['target_condition'],
                  'decimal_precision':100,'reference_eigenvalues':[str(x) for x in ref],
                  'reference_rho':ref_rho,
                  'path_a_relative_forward_error':abs(r['path_a']['rho']-ref_rho)/ref_rho,
                  'path_b_relative_forward_error':abs(r['path_b']['rho']-ref_rho)/ref_rho})
        high_precision.append(r)
    boundaries=[]
    for exponent in [8,12,15,16,17,18]:
        delta=10.**(-exponent); S=np.array([[1.,1.],[1.,1.+delta]])
        item={'requested_delta':delta,'represented_diagonal_increment':float(S[1,1]-1.)}
        try: item.update({'status':'SPD_ACCEPTED',**audit_pencil(S,np.eye(2))})
        except (ValueError,np.linalg.LinAlgError) as exc: item.update({'status':'REJECTED','error_type':type(exc).__name__,'error':str(exc)})
        boundaries.append(item)
    whole_probe=[]; probe=load_historical_probe()
    for case in conditioning_cases():
        rng=np.random.default_rng(702); n=len(case['S'])
        z=rng.normal(size=(n,n))+1j*rng.normal(size=(n,n)); H=(z+adj(z))/2
        D=(rng.normal(size=(n,n))+1j*rng.normal(size=(n,n)))*.01
        item={'target_condition':case['target_condition']}
        try:
            result=probe.rate_matrices(case['S'],H,D,np.eye(n,dtype=complex)[:,[0,2]],hbar=1.)
            item.update({'status':'PROBE_ACCEPTED','probe_rho':result['rho'],
                         'probe_W_hermiticity_defect':result['W_hermiticity_defect'],
                         'metric_identity_residual':result['metric_identity_residual'],
                         'probe_W_relative_hermiticity_defect':result['W_hermiticity_defect']/max(float(np.linalg.norm(result['W'],2)),np.finfo(float).tiny),
                         'explicit_roundoff_projection_for_audit':'(W+W_dagger)/2; raw defect separately retained',
                         'pencil_audit':audit_pencil(case['S'],(result['W']+adj(result['W']))/2)})
        except (ValueError,np.linalg.LinAlgError) as exc:
            item.update({'status':'REJECTED','error_type':type(exc).__name__,'error':str(exc)})
        whole_probe.append(item)
    common={'schema_version':1,'scope':'FINITE_SYNTHETIC_MATRICES_ONLY',
            'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__,
            'source_probe_path':str(PROBE_PATH.relative_to(REPO)),
            'source_probe_sha256':hashlib.sha256(PROBE_PATH.read_bytes()).hexdigest(),
            'source_probe_commit':'01ec2ba7e71aefdccab1896acfe5d92c15c6b776',
            'new_native_calls':0,'new_external_runs':0,'saved_physical_matrices_available':True,
            'production_source_modified':False,'new_authorization_consumed':False}
    solver={**common,'conditioning_sweep':sweep,'decimal_reference_sweep':high_precision,
            'cholesky_boundary_sweep':boundaries,'historical_rate_probe_sweep':whole_probe,
            'saved_physical_matrix_postprocessing':saved_physical_audit(),
            'rank_policy':'Reject singular/indefinite metrics; no shift; rank repair delegated to G09',
            'independence_limit':'A and B use different reductions/eigensolver driver paths but both depend on LAPACK; C is independent Decimal analytic 2x2.'}
    covariance={**common,'covariance_cases':[covariance_case(s) for s in range(12)],
                'raw_block_counterexample':raw_block_counterexample(),
                'new_diagnostic':'metric_projected_coupling_norm',
                'existing_K_TP_semantics_changed':False}
    for name,data in [('E_RHO_SOLVER_RESULTS.json',solver),('E_COVARIANCE_RESULTS.json',covariance)]:
        (HERE/name).write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'solver_cases':len(sweep),'decimal_cases':len(high_precision),
                      'covariance_cases':12,'historical_probe':[x['status'] for x in whole_probe]},indent=2))


if __name__=='__main__': run_audits()
