"""Frozen state heat-kernel mixture; no operator or solver construction."""
import math
import numpy as np
from moment_bounds import bounds
T0 = 1e10
PROB_TOL = 2e-12

class FrontierError(ValueError):
    def __init__(self, reason):
        self.reason = reason
        super().__init__(reason)

def fail(reason):
    raise FrontierError(reason)

def compare(actual, expected, scale=1.0):
    a = np.asarray(actual, dtype=float)/scale
    e = np.asarray(expected, dtype=float)/scale
    d = a-e
    limit = 1e-12+5e-10*np.abs(e)
    row = {'actual_normalized': a.tolist(), 'expected_normalized': e.tolist(),
           'signed_difference': d.tolist(), 'limit': limit.tolist(),
           'pass': bool(np.all(np.abs(d) <= limit))}
    if not row['pass']:
        fail('FRONTIER_SAVED_MOMENT_CROSSCHECK_FAILED '+str(row))
    return row

def prepare(arrays, own, cached, *, n=9600):
    required = {'energy_eV': (n,), 'q0': (n,), 'q1': (n,), 'q2': (n,),
                'xT': (n,2), 'b_active': (n,2)}
    for key, shape in required.items():
        if key not in arrays:
            fail('FRONTIER_REQUIRED_ARRAY_MISSING '+key)
        a = arrays[key]
        if a.dtype != np.dtype('float64') or a.shape != shape or not np.isfinite(a).all():
            fail('FRONTIER_ARRAY_INVALID '+key)
        if key != 'energy_eV' and np.any(a < 0):
            fail('FRONTIER_MOMENT_NOT_PROBABILITY_COMPATIBLE')
    q0, q1, q2 = (arrays[k] for k in ('q0','q1','q2'))
    zero = q0 == 0
    if np.any(q1[zero] != 0) or np.any(q2[zero] != 0):
        fail('FRONTIER_MOMENT_NOT_PROBABILITY_COMPATIBLE')
    active = ~zero
    a = T0*q1[active]/q0[active]
    b = 2*T0*T0*q2[active]/q0[active]
    v = b-a*a
    if not all(np.isfinite(x).all() for x in (a,b,v)) or np.any(v<0) or np.any(a<=0):
        fail('FRONTIER_MOMENT_NOT_PROBABILITY_COMPATIBLE')
    scalars = {'H0':q0@arrays['b_active'], 'H1':T0*(q1@arrays['b_active']),
               'H2':2*T0*T0*(q2@arrays['b_active']), 'Htail':q0@arrays['xT'],
               'Eex1':T0*(q1@arrays['xT']), 'Eex2':2*T0*T0*(q2@arrays['xT'])}
    H = scalars['H0']
    if np.any(H <= 0):
        fail('FRONTIER_NONPOSITIVE_HEAT_YIELD')
    alpha = q0[active,None]*arrays['xT'][active]/H
    selected_alpha = q0[active]*arrays['xT'][active].sum(axis=1)/H.sum()
    mass = alpha.sum(axis=0)
    checks = {'F_own': {}, 'cached': {}, 'state_reconstruction': {}}
    for key, scale in [('H0',1),('H1',T0),('H2',T0*T0),('Htail',1),('Eex1',T0),('Eex2',T0*T0)]:
        checks['F_own'][key] = {'birth':compare(scalars[key],own['scalars'][key],scale),
                                 'selected':compare(scalars[key].sum(),own['selected'][key],scale)}
    cache_rows = cached['birth_columns']+[cached['selected']]
    for i, row in enumerate(cache_rows):
        h, mu, m2, p, R, S = (row[k] for k in ('H0','mu_s','m2_s2','p','R','S'))
        expected = [h,h*mu,h*m2,h*(1-p),h*(mu-T0*(1-R)),h*(m2-2*T0*mu+T0*T0*(1-S))]
        actual = [scalars[k][i] if i<2 else scalars[k].sum() for k in ('H0','H1','H2','Htail','Eex1','Eex2')]
        checks['cached'][str(i)] = compare(actual,expected,np.array([1,T0,T0*T0,1,T0,T0*T0]))
    for key, values, expected, scale in [('mass',mass,scalars['Htail']/H,1),
             ('first',(alpha*a[:,None]).sum(axis=0),scalars['Eex1']/H,T0),
             ('second',(alpha*b[:,None]).sum(axis=0),scalars['Eex2']/H,T0*T0)]:
        checks['state_reconstruction'][key] = compare(values,expected,scale)
    checks['state_reconstruction']['selected_mass'] = compare(selected_alpha.sum(),scalars['Htail'].sum()/H.sum())
    checks['state_reconstruction']['selected_first'] = compare(selected_alpha@a,scalars['Eex1'].sum()/H.sum(),T0)
    checks['state_reconstruction']['selected_second'] = compare(selected_alpha@b,scalars['Eex2'].sum()/H.sum(),T0*T0)
    for i,row in enumerate(cache_rows):
        q = 1-row['p']; actual_mass = mass[i] if i<2 else selected_alpha.sum()
        if abs(actual_mass-q)>PROB_TOL:
            fail('FRONTIER_MASS_PROBABILITY_MISMATCH')
    return {'a':a,'b':b,'alpha':alpha,'selected_alpha':selected_alpha,'H0':H,
            'scalars':scalars,'cached':cached,'checks':checks,
            'zero_q0_states':int(zero.sum()), 'zero_weight_states':int((selected_alpha==0).sum()),
            'state_indices':np.nonzero(active)[0]}

def _bounds(x,a,b):
    row = bounds(a,b,x)
    return row['lower'], row['upper']

def state_bounds(a,b,x):
    """Vector evaluation of the frozen scalar theorem; no state accumulation changes."""
    v=b-a*a
    lower=np.zeros_like(a);upper=np.zeros_like(a)
    deterministic=v==0
    value=x<a
    lower[deterministic]=value[deterministic]
    upper[deterministic]=value[deterministic]
    variable=~deterministic
    below=variable&(x<a)
    d=a[below]-x
    lower[below]=d*d/(v[below]+d*d)
    one=variable&(x<=a);upper[one]=1.
    markov=variable&(x>a)&(x<b/a);upper[markov]=a[markov]/x
    cantelli=variable&(x>a)&~markov
    d=x-a[cantelli]
    upper[cantelli]=v[cantelli]/(v[cantelli]+d*d)
    if not np.isfinite(lower).all() or not np.isfinite(upper).all():fail('FRONTIER_NONFINITE_BOUND_ARITHMETIC')
    return np.column_stack((lower,upper))

def envelope(prepared,t):
    if not math.isfinite(t) or t<T0:
        fail('FRONTIER_TIME_OUTSIDE_RESIDUAL_DOMAIN')
    a,b,alpha = (prepared[k] for k in ('a','b','alpha'))
    x = t-T0
    H = prepared['H0']; weights = H/H.sum(); rows = prepared['cached']['birth_columns']
    selected = prepared['cached']['selected']; selected_alpha = prepared['selected_alpha']
    if x == 0:
        state_birth = np.repeat(alpha.sum(axis=0)[:,None],2,axis=1)
        state = [float(selected_alpha.sum())]*2
    else:
        generic = state_bounds(a,b,x)
        state_birth = alpha.T@generic
        state = (selected_alpha@generic).tolist()
    birth = np.zeros(2)
    for w,row in zip(weights,rows):
        q = 1-row['p']
        if q:
            r = row['tail_residual']; bound = [1.,1.] if x==0 else _bounds(x,r['mean_s'],r['second_s2'])
            birth += w*q*np.array(bound)
    q = 1-selected['p']; r = selected['tail_residual']
    pool = [q,q] if x==0 else ([0.,0.] if q==0 else [q*v for v in _bounds(x,r['mean_s'],r['second_s2'])])
    unconditional = _bounds(t,selected['mu_s'],selected['m2_s2'])
    dominance = {'state_minus_birth_lower':state[0]-birth[0], 'birth_minus_state_upper':birth[1]-state[1],
                 'birth_minus_pool_lower':birth[0]-pool[0], 'pool_minus_birth_upper':pool[1]-birth[1]}
    dominance['pass'] = all(v>=-PROB_TOL for v in dominance.values())
    if not dominance['pass']:
        fail('FRONTIER_ENVELOPE_DOMINANCE_FAILED '+str(dominance))
    lower = max(state[0],float(birth[0]),pool[0],unconditional[0])
    upper = min(state[1],float(birth[1]),pool[1],unconditional[1])
    if x==0:
        lower=upper=q
    if not 0 <= lower <= upper <= 1:
        fail('FRONTIER_INTERSECTION_INVALID '+str({'raw_lower':lower,'raw_upper':upper}))
    return {'t_s':t,'state_birth':state_birth.tolist(),'state':state,'birth':birth.tolist(),
            'pooled':pool,'unconditional':list(unconditional), 'intersection':[lower,upper],
            'dominance':dominance,'endpoint_override':x==0}


def horizon_brackets(prepared,f):
    """Refined Q_f enclosing interval, using strict lower and closed upper tests."""
    if not math.isfinite(f) or not 0<f<1:fail('FRONTIER_INVALID_FRACTION')
    selected=prepared['cached']['selected'];eps=1-f
    if f<=selected['p']:
        return {'fraction':f,'status':'KNOWN_T_ANCHOR_ONLY','lower_s':0.,'upper_s':T0,'threshold':eps}
    def get(t,i):return envelope(prepared,t)['intersection'][i]
    means=[selected['mu_s'],T0]+(prepared['a']+T0).tolist()
    means += [T0+row['tail_residual'].get('mean_s',0) for row in prepared['cached']['birth_columns']+[selected]]
    lo=T0;hi=2*max(means);doubles=0
    while get(hi,0)>eps:
        if doubles>=64:fail('FRONTIER_HORIZON_SEARCH_EXHAUSTED_LOWER')
        hi*=2;doubles+=1
    initial=[lo,hi];iterations=0
    for _ in range(80):
        mid=(lo+hi)/2
        if mid==lo or mid==hi:break
        if get(mid,0)>eps:lo=mid
        else:hi=mid
        iterations+=1
    lower=lo
    lower_bisection={'initial':initial,'final':[lo,hi],'iterations':iterations,'doublings':doubles,'endpoint_values':[get(lo,0),get(hi,0)]}
    lo=T0;hi=max(2*selected['mu_s']/eps,math.nextafter(T0,math.inf));doubles=0
    while get(hi,1)>eps:
        if doubles>=64:fail('FRONTIER_HORIZON_SEARCH_EXHAUSTED_UPPER')
        hi*=2;doubles+=1
    initial=[lo,hi];iterations=0
    for _ in range(80):
        mid=(lo+hi)/2
        if mid==lo or mid==hi:break
        if get(mid,1)<=eps:hi=mid
        else:lo=mid
        iterations+=1
    upper=hi
    upper_bisection={'initial':initial,'final':[lo,hi],'iterations':iterations,'doublings':doubles,'endpoint_values':[get(lo,1),get(hi,1)]}
    lower_value=get(lower,0);upper_value=get(upper,1)
    if not lower_value>eps or not upper_value<=eps or lower>upper:fail('FRONTIER_HORIZON_ENDPOINT_FAILURE')
    return {'fraction':f,'status':'ENCLOSING_FRONTIER_MOMENT_BRACKET','threshold':eps,'lower_s':lower,'upper_s':upper,
            'lower_value':lower_value,'upper_value':upper_value,'lower_bisection':lower_bisection,'upper_bisection':upper_bisection}
