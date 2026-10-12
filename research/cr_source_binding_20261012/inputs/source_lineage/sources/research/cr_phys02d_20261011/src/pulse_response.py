"""FP64 frozen-operator pulse, ledger integrals and active resolvent.
No physical constructor is imported here. G uses u=t/T0.
"""
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import expm_multiply, spsolve_triangular

TOL_RESIDUAL=5e-11
TOL_NONNEG=2e-12

def pulse_response(G, sources, n_active, heat_index, energy_weights, time_scale_s=1e10):
    G=sparse.csc_matrix(G,dtype=np.float64); b=np.asarray(sources,dtype=np.float64)
    ef=np.asarray(energy_weights,dtype=np.float64)
    m=G.shape[0]; n=n_active
    if G.shape!=(m,m) or b.ndim!=2 or b.shape[0]!=m or ef.shape!=(m,) or not 0<n<=m or not n<=heat_index<m:
        raise ValueError('INVALID_SHAPES_OR_HEAT_INDEX')
    if not np.isfinite(time_scale_s) or time_scale_s<=0 or not np.all(np.isfinite(G.data)) or not np.all(np.isfinite(b)) or not np.all(np.isfinite(ef)) or np.any(b<0) or np.any(ef<0):raise ValueError('NONFINITE_OR_NEGATIVE_INPUT')
    if np.any(b[heat_index]!=0):raise ValueError('DIRECT_SOURCE_HEAT_FORBIDDEN')
    L=G[:n,:n]; off=L-sparse.diags(L.diagonal())
    if np.any(off.data<0) or np.any(L.diagonal()>=0):raise ValueError('ACTIVE_NOT_METZLER_HURWITZ')
    if sparse.tril(L,k=-1).nnz:raise ValueError('ACTIVE_NOT_EXACT_UPPER_TRIANGULAR')
    if G[:,n:].nnz:raise ValueError('LEDGERS_NOT_ABSORBING')
    if np.any(G[n:,:n].data<0):raise ValueError('NEGATIVE_LEDGER_RATE')
    conservation=np.asarray(ef@G).ravel()
    if np.max(np.abs(conservation),initial=0)>TOL_RESIDUAL*max(np.max(np.abs(G.data),initial=0)*max(np.max(ef,initial=0),1),1):raise ValueError('GENERATOR_ENERGY_NONCONSERVATION')
    A=-L; h=np.asarray(G[heat_index,:n].toarray()).ravel(); ws=[]; residuals=[]; rhs=b[:n].copy()
    for _ in range(3):
        w=np.asarray(spsolve_triangular(A,rhs,lower=False));w=w.reshape(n,b.shape[1])
        denom=np.abs(A)@np.abs(w)+np.abs(rhs)
        r=np.max(np.abs(A@w-rhs)/np.maximum(denom,1e-300),axis=0)
        if np.any(r>TOL_RESIDUAL) or np.any(w < -TOL_NONNEG*max(np.max(np.abs(w),initial=0),1)):raise ArithmeticError('ACTIVE_SOLVE_FAILED')
        ws.append(w);residuals.append(r);rhs=w
    H0=h@ws[0]; numerator1=h@ws[1]; numerator2=2*(h@ws[2])
    heatrow=sparse.csc_matrix(([1.],([0],[heat_index])),shape=(1,m))
    zcol=sparse.csc_matrix((m,1)); zscalar=sparse.csc_matrix((1,1))
    aug=sparse.bmat([[G,zcol,zcol],[heatrow,zscalar,zscalar],[sparse.csc_matrix((1,m)),sparse.csc_matrix([[1.]]),zscalar]],format='csc')
    initial=np.vstack([b,np.zeros((2,b.shape[1]))])
    y=expm_multiply(aug,initial,start=0,stop=1,num=17,endpoint=True)
    scale=max(np.max(np.abs(initial),initial=0),1)
    nonnegative=float(np.min(y))
    energy=np.einsum('i,tij->tj',ef,y[:,:m]); initial_energy=ef@b
    energy_residual=energy-initial_energy
    if nonnegative < -TOL_NONNEG*scale or np.max(np.abs(energy_residual),initial=0)>5e-10*max(np.max(initial_energy,initial=0),1):raise ArithmeticError('PULSE_LEDGER_VALIDATION_FAILED')
    heat=y[:,heat_index]; kernels=np.einsum('i,tij->tj',h,y[:,:n])/time_scale_s
    def summarize(H,first,second,heat_values,kernel_values,j1,j2):
        if H==0:return {'status':'UNDEFINED_ZERO_HEAT_YIELD','H0':0.,'cdf':None,'mean_lag_s':None,'second_moment_s2':None,'variance_s2':None,'kernel_per_s':kernel_values.tolist(),'J1':float(j1),'J2':float(j2)}
        mean=time_scale_s*first/H; sec=time_scale_s**2*second/H; cdf=heat_values/H
        if np.any(cdf < -1e-9) or np.any(cdf>1+1e-9) or np.any(np.diff(cdf)<-1e-9):raise ArithmeticError('CDF_BOUND_FAILED')
        R=j1/H;S=2*j2/H
        if R < -1e-9 or R>1+1e-9 or S<R*R-1e-9 or S>R+1e-9:raise ArithmeticError('MOMENT_BOUND_FAILED')
        variance=sec-mean**2
        if variance < -1e-9*max(sec,mean**2,1):raise ArithmeticError('INFINITE_VARIANCE_BOUND_FAILED')
        return {'status':'DEFINED','H0':float(H),'cdf':cdf.tolist(),'kernel_per_s':kernel_values.tolist(),'mean_lag_s':float(mean),'second_moment_s2':float(sec),'variance_s2':float(variance),'J1':float(j1),'J2':float(j2),'R':float(R),'S':float(S),'clipped_mean_s':float(time_scale_s*(1-R)),'clipped_second_s2':float(time_scale_s**2*(1-2*R+S)),'clipped_variance_s2':float(time_scale_s**2*(S-R*R)),'current_ramp_ancestry_mean_s':float(time_scale_s*(1-S/R)) if R>0 else None}
    columns=[summarize(H0[k],numerator1[k],numerator2[k],heat[:,k],kernels[:,k],y[-1,-2,k],y[-1,-1,k]) for k in range(b.shape[1])]
    selected=summarize(H0.sum(),numerator1.sum(),numerator2.sum(),heat.sum(axis=1),kernels.sum(axis=1),y[-1,-2].sum(),y[-1,-1].sum())
    return {'sample_u':np.linspace(0,1,17).tolist(),'birth_columns':columns,'selected':selected,'active_solve_scaled_residuals':[r.tolist() for r in residuals],'minimum_state':nonnegative,'energy_residuals':energy_residual.tolist(),'pulse_states':y[:,:m],'integrator_states':y[:,-2:],'expm_calls':1}


def check_saved_cdf_bounds(sample_u, selected_cdf, R, S, source_reference):
    """Frozen endpoint inequalities; moments come from saved ramp, not pulse."""
    if not np.isfinite(R) or not np.isfinite(S):raise ValueError('NONFINITE_SAVED_MOMENTS')
    u=np.asarray(sample_u);cdf=np.asarray(selected_cdf);checks=[]
    for point in (.25,.5,.75,1.):
        matches=np.flatnonzero(u==point)
        if len(matches)!=1:raise ValueError('EXACT_CDF_SAMPLE_MISSING')
        actual=float(cdf[matches[0]])
        if point==1.:lower=R*R/S if S>0 else 0.;upper=1.
        else:
            c=1-point;lower=max(0.,(S-c*R)/(1-c));upper=min(1.,((1+c)*R-S)/c)
        lower_slack=actual-lower;upper_slack=upper-actual
        passed=np.isfinite(actual) and lower_slack>=-1e-9 and upper_slack>=-1e-9
        checks.append({'u':point,'lower':float(lower),'upper':float(upper),'actual':actual,'lower_slack':float(lower_slack),'upper_slack':float(upper_slack),'pass':bool(passed)})
    result={'saved_R':float(R),'saved_S':float(S),'source_reference':source_reference,'absolute_tolerance':1e-9,'checks':checks,'pass':all(x['pass'] for x in checks)}
    return result
