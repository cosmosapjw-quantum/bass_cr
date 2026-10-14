"""Active energy-coordinate adjoint residence; never constructs or propagates G."""
import hashlib, io
import numpy as np
from scipy.sparse import tril
from scipy.sparse.linalg import spsolve_triangular

T0=1.e10
EDGES=np.array([.1,1.,10.,30.,100.,300.,900.])
class ResidenceError(ValueError):
    def __init__(self, reason):
        self.reason=reason
        super().__init__(reason)
def fail(reason): raise ResidenceError(reason)
def raw_hash(a): return hashlib.sha256(a.tobytes(order='C')).hexdigest()
def immutable(a): return np.frombuffer(a.tobytes(order='C'),dtype=a.dtype).reshape(a.shape)

def preflight_pulses(repo, identities, sources, n=9600):
    # Read and verify every whole source/pulse file before loading any pulse.
    raw={}
    for model in ('fullBED','legacy'):
        for key in (model+'_9600_npz','actual_'+model+'_pulse'):
            info=identities[key]; value=(repo/info['path']).read_bytes()
            if len(value)!=info['bytes'] or hashlib.sha256(value).hexdigest()!=info['sha256']:
                fail('INPUT_FILE_IDENTITY_MISMATCH '+key)
            if key.startswith('actual_'): raw[model]=value
    pulses={}; receipts={}
    shapes={'sample_u':(17,), 'pulse_states':(17,n+11,2),
            'integrator_states':(17,2,2),'energy_eV':(n,), 'source_vectors':(n+11,2)}
    for model in ('fullBED','legacy'):
        with np.load(io.BytesIO(raw[model]),allow_pickle=False) as z:
            if set(shapes)-set(z.files): fail('PULSE_FIELDS_MISSING')
            arrays={k:z[k] for k in shapes}
        for k,a in arrays.items():
            if a.shape!=shapes[k] or a.dtype.str!='<f8' or not a.flags.c_contiguous or not np.isfinite(a).all():
                fail('PULSE_FIELD_INVALID '+k)
        if not np.array_equal(arrays['sample_u'],np.linspace(0.,1.,17)): fail('PULSE_TIME_MISMATCH')
        for k in ('energy_eV','source_vectors'):
            if not np.array_equal(arrays[k],sources[model][k]): fail('PULSE_SOURCE_MISMATCH '+k)
        if not np.array_equal(arrays['pulse_states'][0],arrays['source_vectors']) or np.any(arrays['integrator_states'][0]!=0): fail('PULSE_INITIAL_MISMATCH')
        tolerance=2e-12*max(1.,float(np.max(np.abs(arrays['source_vectors']))))
        if np.any(arrays['pulse_states'] < -tolerance) or np.any(arrays['integrator_states'] < -tolerance): fail('PULSE_NEGATIVE')
        pulses[model]={k:immutable(a) for k,a in arrays.items()}
        receipts[model]={k:{'shape':list(a.shape),'dtype':a.dtype.str,'raw_C_sha256':raw_hash(a)} for k,a in arrays.items()}
    return pulses,receipts

def operator_parity(current, reference):
    if current.get('G')!=reference.get('G') or current.get('energy_eV')!=reference.get('energy_eV'): fail('OPERATOR_IDENTITY_MISMATCH')
    c=current.get('method_bindings',{}); r=reference.get('method_bindings',{})
    if not c or set(c)!=set(r) or any(v.get('same_parent_object') is not True for v in list(c.values())+list(r.values())):
        fail('OPERATOR_IDENTITY_MISMATCH')
    # Module names depend on loader aliases; qualnames and actual same-object guards are stable.
    if any(c[k].get('qualname')!=r[k].get('qualname') for k in c): fail('OPERATOR_IDENTITY_MISMATCH')
    return {'status':'EXACT_RAW_CSC_AND_SAVED_GRID_MATCH','method_names':sorted(c)}

def structure(G,n,heat):
    if G.format!='csc' or G.shape!=(n+11,n+11) or not np.isfinite(G.data).all(): fail('INVALID_OPERATOR')
    if G[:,n:].nnz and np.any(G[:,n:].data!=0): fail('LEDGERS_NOT_ABSORBING')
    A=-G[:n,:n]; diagonal=A.diagonal()
    if np.any(diagonal<=0) or np.any(tril(A,k=-1).data!=0): fail('ACTIVE_NOT_UPPER_STABLE')
    coo=A.tocoo()
    if np.any(coo.data[coo.row!=coo.col]>0): fail('ACTIVE_NOT_METZLER')
    h=np.asarray(G[heat,:n].toarray()).ravel()
    if np.any(h<0): fail('NEGATIVE_HEAT_ROW')
    return A,h

def diagnostic(G,E,b,xT,heat,*,solve=spsolve_triangular,on_solve=None):
    n=len(E); A,h=structure(G,n,heat)
    if b.shape!=(n,2) or xT.shape!=(n,2) or not all(np.isfinite(a).all() for a in (E,b,xT)): fail('INVALID_ACTIVE_INPUT')
    if np.any(np.diff(E)<=0) or np.any(E<=EDGES[0]) or np.any(E>EDGES[-1]): fail('BIN_PARTITION_INVALID')
    records=[]
    def call(M,rhs,lower,name):
        if on_solve: on_solve('RESERVED',name)
        result=solve(M,rhs,lower=lower)
        if on_solve: on_solve('COMPLETED',name)
        if not np.isfinite(result).all(): fail('NONFINITE_SOLVE')
        residual=M@result-rhs
        denominator=np.asarray(abs(M)@abs(result))+abs(rhs)
        scaled=float(np.max(np.abs(residual)/np.maximum(denominator,np.finfo(float).tiny)))
        records.append({'name':name,'scaled_residual':scaled,'signed_residual_min':float(np.min(residual)),'signed_residual_max':float(np.max(residual))})
        if scaled>5e-11: fail('SOLVE_RESIDUAL_FAILED')
        if np.min(result)<-2e-12*max(1.,float(np.max(np.abs(result)))): fail('SOLVE_NEGATIVE')
        return result
    q0=call(A.T,h,True,'q0')
    if np.min(q0)<-2e-12 or np.max(q0)>1+2e-12: fail('Q0_PHYSICAL_BOUND_FAILED')
    q1=call(A.T,q0,True,'q1');q2=call(A.T,q1,True,'q2')
    w=call(A,b,False,'w');v=call(A,xT,False,'v')
    arrays={'energy_eV':E,'q0':q0,'q1':q1,'q2':q2,'w':w,'v':v,'xT':xT,'b_active':b,
            'per_state_first_moment':T0*q0[:,None]*w,
            'per_state_remaining_first_moment':T0*q0[:,None]*v,
            'per_state_tail_heat':q0[:,None]*xT}
    scalars={'H0':q0@b,'H1':T0*(q1@b),'H2':2*T0*T0*(q2@b),
             'Htail':q0@xT,'Eex1':T0*(q1@xT),'Eex2':2*T0*T0*(q2@xT)}
    bins=[]
    for lo,hi in zip(EDGES[:-1],EDGES[1:]):
        mask=(E>lo)&(E<=hi)
        bins.append({'lo_eV':float(lo),'hi_eV':float(hi),'states':int(mask.sum()),
                     **{k:arrays[k][mask].sum(axis=0).tolist() for k in ('per_state_first_moment','per_state_remaining_first_moment','per_state_tail_heat')}})
    checks={}
    for field,target,scale in [('per_state_first_moment','H1',T0),('per_state_remaining_first_moment','Eex1',T0),('per_state_tail_heat','Htail',1.)]:
        checks[field]=crosscheck(arrays[field].sum(axis=0)/scale,scalars[target]/scale)
    bin_checks={}
    for field,target,scale in [('per_state_first_moment','H1',T0),('per_state_remaining_first_moment','Eex1',T0),('per_state_tail_heat','Htail',1.)]:
        aggregate=np.array([row[field] for row in bins]).sum(axis=0)/scale
        expected=scalars[target]/scale
        bin_checks[field]={'birth':crosscheck(aggregate,expected),'selected':crosscheck(np.array(aggregate.sum()),np.array(expected.sum()))}
    result={'schema':'cr-phys02f-residence.v1','solve_calls':5,'solve_residuals':records,
            'scalars':{k:v.tolist() for k,v in scalars.items()},'selected':{k:float(v.sum()) for k,v in scalars.items()},'bins':bins,'per_state_checks':checks,'bin_checks':bin_checks,
            'units':{'q0':'eventual heat per unit active energy','q1':'dimensionless delay weighted heat','q2':'dimensionless second resolvent heat','w':'dimensionless integrated energy residence','v':'dimensionless future integrated energy residence','per_state_first_moment':'normalized heat seconds','per_state_remaining_first_moment':'normalized heat seconds','per_state_tail_heat':'normalized heat'},
            'claim':'same frozen operator heat-weighted residence, not deposition or particle lifetime'}
    return arrays,result

def crosscheck(actual,expected):
    a=np.asarray(actual); e=np.asarray(expected); d=a-e
    rel=np.divide(d,np.abs(e),out=np.zeros_like(d),where=e!=0)
    passed=bool(np.all(np.abs(d)<=1e-12+5e-10*np.abs(e)))
    record={'actual':a.tolist(),'expected':e.tolist(),'signed_difference':d.tolist(),'absolute_difference':np.abs(d).tolist(),'signed_relative_difference':rel.tolist(),'relative_defined':(e!=0).tolist(),'pass':passed}
    if not passed: fail('PHYSICAL_SCALAR_CROSSCHECK_FAILED '+str(record))
    return record

def check_saved(result,saved):
    rows=saved['birth_columns']+[saved['selected']]; checks=[]
    for i,row in enumerate(rows):
        s={k:(v[i] if i<2 else sum(v)) for k,v in result['scalars'].items()}
        H=row['H0'];mu=row['mean_lag_s']/T0;m2=row['second_moment_s2']/T0**2;p=row['cdf'][-1];R=row['R'];S=row['S']
        actual=[s['H0'],s['H1']/T0,s['H2']/T0**2,s['Htail'],s['Eex1']/T0,s['Eex2']/T0**2]
        expected=[H,H*mu,H*m2,H*(1-p),H*(mu-(1-R)),H*(m2-2*mu+1-S)]
        checks.append(crosscheck(actual,expected))
    result['saved_scalar_checks']=checks
    for i,H in enumerate(result['scalars']['H0']):
        if H<=0: fail('NONPOSITIVE_HEAT_YIELD')
    result['normalized_bins']=[]
    for bin in result['bins']:
        row=dict(bin)
        for field,den in [('per_state_first_moment','H0'),('per_state_remaining_first_moment','Htail'),('per_state_tail_heat','H0')]:
            row[field+'_normalized']=[value/divisor if divisor>0 else {'status':'UNDEFINED_ZERO_EVENT_PROBABILITY'} for value,divisor in zip(bin[field],result['scalars'][den])]
            divisor=result['selected'][den];row[field+'_selected_normalized']=sum(bin[field])/divisor if divisor>0 else {'status':'UNDEFINED_ZERO_EVENT_PROBABILITY'}
        result['normalized_bins'].append(row)
    return result

def diagnostic_after_parity(current,reference,reserve,**kwargs):
    parity=operator_parity(current,reference)
    reserve()
    arrays,result=diagnostic(**kwargs)
    return arrays,result,parity
