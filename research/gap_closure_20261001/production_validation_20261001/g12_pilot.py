"""Bounded physical-cache DOP853 versus legacy midpoint pilot. No native calls.

The fixed physical scope is R4U B0 z=[32,32.02], e0 normalized once. A successful
local comparison does not close the original G12 collision-window gate or G02.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib
import inspect
import json
import math
from pathlib import Path
import sys
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
PROD = HERE.parent/'production_solver_20261001'
for p in (PROD/'provider', PROD/'runtime'):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
import hpc_provider as hp
import bootstrap_runtime
import numpy as np
import scipy
from scipy.integrate import DOP853
from scipy.linalg import solve, solve_triangular
from metric_transport import candidate_step, metric_frame_generator, phase_aligned_metric_distance
from reference_transport import generalized_rhs
from parallel_bridge import PlannedQuery, query_id, validate_pair
from cache_consistency import validate_cached_cross_binding
from cr_repro.observables import projectile_speed_au

SCHEMA = 'BASS_R4V_G12_LOCAL_PILOT_PLAN_V1'
CLAIMS = dict(production_admission='HOLD', capture=False, all_bound='OPEN',
              b_grid='NO_GO', physical_G12_closed=False, physical_G02_closed=False,
              continuous_trajectory_error_bound=False, ncp64_scaling_measured=False)
BUDGETS = {'endpoint_unaligned_metric_distance_max':1e-8,
           'endpoint_selected_population_difference_max':1e-10,
           'dop853_endpoint_norm_drift_max':1e-9,
           'midpoint_discrete_norm_drift_max':1e-12,
           'initial_metric_distance_max':1e-14}
RTOL = 5e-13
ATOL = 5e-15
MIDPOINT_STEPS = (1, 2, 4)


def _array_identity(a):
    a = np.ascontiguousarray(a)
    return {'dtype':a.dtype.str, 'shape':list(a.shape),
            'sha256':hashlib.sha256(a.tobytes()).hexdigest()}


def dependency_identity():
    if scipy.__version__ != '1.17.0':
        raise ValueError('this exact stage contract requires SciPy 1.17.0')
    names = ('scipy.integrate._ivp.rk', 'scipy.integrate._ivp.common',
             'scipy.integrate._ivp.base', 'scipy.integrate._ivp.dop853_coefficients')
    files = {name:hp.sha(inspect.getsourcefile(importlib.import_module(name))) for name in names}
    from scipy.integrate._ivp import dop853_coefficients as coeff
    arrays = {name:_array_identity(getattr(coeff,name)) for name in ('A','B','C','E3','E5','D')}
    return {'scipy':scipy.__version__, 'numpy':np.__version__, 'python':sys.version,
            'scipy_source_files':files, 'dop853_coefficient_arrays':arrays,
            'dop853_stage_array':_array_identity(DOP853.C),
            'dop853_stage_hex':[float(x).hex() for x in DOP853.C],
            'g12_pilot_source_sha256':hp.sha(__file__),
            'legacy_midpoint_source_sha256':hp.sha(inspect.getsourcefile(candidate_step)),
            'legacy_direct_rhs_source_sha256':hp.sha(inspect.getsourcefile(generalized_rhs))}


def stage_grid(t0, tf):
    t0=float(t0); tf=float(tf)
    if not np.isfinite([t0,tf]).all() or not tf>t0:
        raise ValueError('finite increasing interval required')
    h=tf-t0
    t_new=t0+h
    if t_new>tf:
        t_new=tf
    h=t_new-t0
    if t_new != tf:
        raise ValueError('one exact step does not reach the endpoint')
    dop=[t0]+[t0+float(c)*h for c in DOP853.C[1:]]+[t0+h]
    midpoint=[]
    for n in MIDPOINT_STEPS:
        dt=(tf-t0)/n; steps=[]
        for j in range(n):
            ta=t0+j*dt; tb=ta+dt; tm=.5*(ta+tb)
            if not tb>ta:
                raise ValueError('collapsed midpoint step')
            steps.append({'ta_hex':ta.hex(),'tb_hex':tb.hex(),'tm_hex':tm.hex()})
        midpoint.append({'nstep':n,'steps':steps})
    times={t0.hex(),tf.hex(),*(float(t).hex() for t in dop)}
    times.update(s['tm_hex'] for row in midpoint for s in row['steps'])
    return {'t0_hex':t0.hex(),'tf_hex':tf.hex(),
            'dop853_rhs_time_hex':[float(t).hex() for t in dop],
            'dop853_first_step_hex':h.hex(), 'midpoint':midpoint,
            'times_hex':sorted(times,key=float.fromhex)}


def make_plan(inputs, build, *, backend='fortran', threads=2):
    inputs=Path(inputs).resolve(); build=Path(build).resolve()
    contract=json.loads((inputs/'SCIENCE_CONTEXT.json').read_text())['context']['contract']
    context=hp.prepare_context(inputs,build,contract,backend=backend,threads=threads)
    v=projectile_speed_au(100); grid=stage_grid(32/v,32.02/v)
    if len(grid['times_hex'])!=18 or len(grid['dop853_rhs_time_hex'])!=13:
        raise ValueError('pinned physical 18-query stage grid changed')
    raw=np.zeros(18,dtype=np.complex128); raw[0]=1.
    plan={'schema':SCHEMA,'inputs':str(inputs),'build':str(build),
          'context':context,'dependency_identity':dependency_identity(),
          'scope':{'basis':'archived B0','channels':18,'energy_keV_per_u':100,
                   'b_a0':2,'charges':[1,1],'z_window_a0':[32.,32.02],
                   'initial_state':'e0; normalized exactly once; not an incoming scattering state'},
          'grid':grid,'initial_raw_state_identity':_array_identity(raw),
          'initial_S_query_id':query_id(context['context_id'],grid['t0_hex']),
          'method':{'dop853':{'rtol':RTOL,'atol':ATOL,'steps':1,
                             'first_step_hex':grid['dop853_first_step_hex'],
                             'maximum_rhs_calls':13,'dense_output':False},
                    'midpoint_steps':list(MIDPOINT_STEPS)},
          'acceptance_budgets':dict(BUDGETS),
          'budget_scope':'LOCAL_ENGINEERING_SCREENS_NOT_CERTIFIED_GLOBAL_ERROR_BOUNDS',
          'maximum_raw_attempts':18*len(contract['runtime_reference_resolutions']),
          'operator_interpolation_used':False,'native_fallback_allowed':False,
          'model_routing':'UNAVAILABLE_NO_INFERENCE',**CLAIMS}
    plan['plan_sha256']=hp.digest(plan)
    return plan


def validate_plan(plan):
    expected=make_plan(plan['inputs'],plan['build'],backend=plan['context']['backend'],
                       threads=plan['context']['threads'])
    if plan!=expected:
        raise ValueError('G12 plan/input/source/native/context/dependency identity changed')
    return plan


class ExactUnionCache:
    """One admitted S/H/D pair per planned time; no evaluator exists."""
    def __init__(self, directories, plan):
        validate_plan(plan)
        self.plan=plan; self.context=plan['context']; self.records={}; self._cache={}
        self.reads=0; self.native_calls=0
        directories=[Path(p).resolve() for p in directories]
        if not directories or len(set(directories))!=len(directories):
            raise ValueError('distinct nonempty cache directories required')
        for th in plan['grid']['times_hex']:
            qid=query_id(self.context['context_id'],th)
            candidates=[p for p in directories if (p/(qid+'.json')).exists() or (p/(qid+'.npz')).exists()]
            if len(candidates)!=1:
                raise ValueError('each exact time requires exactly one complete source pair: '+th)
            directory=candidates[0]; query=PlannedQuery(qid,th,None,None)
            record=validate_pair(directory,query,self.context['context_id'],self.context['qualification_contract'])
            validate_cached_cross_binding(directory,qid)
            self.records[th]={'directory':str(directory),'record':record,'query_id':qid}
        self.manifest={'plan_sha256':plan['plan_sha256'],'context_id':self.context['context_id'],
                       'records':self.records,'new_native_calls':0}

    def at(self,t):
        th=float(t).hex()
        if th not in self.records:
            raise KeyError('exact cache miss; no interpolation/native fallback: '+th)
        row=self.records[th]; d=Path(row['directory']); qid=row['query_id']; rec=row['record']
        if hp.sha(d/(qid+'.json'))!=rec['json_sha256'] or hp.sha(d/(qid+'.npz'))!=rec['payload_sha256']:
            raise ValueError('qualified payload changed after admission: '+qid)
        if th not in self._cache:
            with np.load(d/(qid+'.npz'),allow_pickle=False) as data:
                arrays=[np.array(data['selected__'+k],dtype=np.complex128) for k in ('S','H','D')]
            for a in arrays:
                if a.shape!=(18,18) or not np.isfinite(a).all():
                    raise ValueError('invalid 18-channel cached matrix')
                a.setflags(write=False)
            self._cache[th]=SimpleNamespace(S=arrays[0],H=arrays[1],D=arrays[2],identity=qid)
            self.reads+=1
        return self._cache[th]


def _norm(c,S):
    value=np.vdot(c,S@c)
    if not np.isfinite(value) or value.real<=0 or abs(value.imag)>1e-12*max(1.,abs(value.real)):
        raise ArithmeticError('finite positive real metric norm required')
    return float(value.real)


def _distance(a,b,S):
    d=np.asarray(a)-np.asarray(b); value=np.vdot(d,S@d)
    if not np.isfinite(value) or abs(value.imag)>1e-12*max(1.,abs(value.real)) or value.real < -1e-14:
        raise ArithmeticError('endpoint metric distance unresolved')
    return float(np.sqrt(max(0.,value.real)))


def _population(c,S,indices):
    J=np.eye(len(c),dtype=np.complex128)[:,indices]
    gram=J.conj().T@S@J; rhs=J.conj().T@S@c
    value=np.vdot(rhs,solve(gram,rhs,assume_a='pos',check_finite=True))
    if not np.isfinite(value) or abs(value.imag)>1e-12*max(1.,abs(value.real)):
        raise ArithmeticError('selected population unresolved')
    return float(value.real)


def compare_methods(provider, raw_c0, grid, selected_indices):
    """Cache-only core, also exercised by analytic synthetic tests."""
    t0=float.fromhex(grid['t0_hex']); tf=float.fromhex(grid['tf_hex'])
    if grid!=stage_grid(t0,tf):
        raise ValueError('exact stage grid mismatch')
    raw_c0=np.asarray(raw_c0,dtype=np.complex128)
    s0=provider.at(t0); sf=provider.at(tf)
    if raw_c0.shape!=(len(s0.S),) or not np.isfinite(raw_c0).all():
        raise ValueError('finite initial vector must match the metric dimension')
    raw_norm=_norm(raw_c0,s0.S); factor=1./np.sqrt(raw_norm)
    common=raw_c0*factor
    norm0=_norm(common,s0.S)
    if not selected_indices or len(set(selected_indices))!=len(selected_indices) or any(type(i) is not int or not 0<=i<len(common) for i in selected_indices):
        raise ValueError('nonempty unique valid selected indices required')
    initial_receipt={'raw_state':_array_identity(raw_c0),'S0':_array_identity(s0.S),
       'raw_metric_norm':raw_norm,'normalization_factor':float(factor),
       'common_initial_state':_array_identity(common),'common_initial_metric_norm':norm0,
       'normalizations':1,'state_scope':'EXPLICIT_CALLER_VECTOR_NOT_IMPORTED_SCATTERING_STATE'}
    rhs_times=[]
    expected=grid['dop853_rhs_time_hex']
    def rhs(t,c):
        th=float(t).hex(); index=len(rhs_times)
        if index>=len(expected) or th!=expected[index]:
            raise KeyError('unplanned DOP853 RHS stage/rejection; no query expansion: '+th)
        rhs_times.append(th)
        return generalized_rhs(t,c,provider)
    dop_initial=common.copy()
    engine=DOP853(rhs,t0,dop_initial,tf,rtol=RTOL,atol=ATOL,
                  first_step=float.fromhex(grid['dop853_first_step_hex']),
                  max_step=float.fromhex(grid['dop853_first_step_hex']))
    actual_dop_initial=engine.y.copy()
    initial_distance=_distance(actual_dop_initial,common,s0.S)
    if initial_distance>BUDGETS['initial_metric_distance_max']:
        raise ArithmeticError('DOP853 changed the common initial condition')
    message=engine.step()
    if engine.status!='finished' or engine.t!=tf or engine.nfev!=13 or rhs_times!=expected:
        raise ArithmeticError('DOP853 did not accept exactly the preplanned single step')
    dop_final=engine.y.copy()
    if not np.isfinite(dop_final).all():
        raise ArithmeticError('DOP853 nonfinite final state')
    dop_norm=_norm(dop_final,sf.S); dop_p=_population(dop_final,sf.S,selected_indices)
    dop={'method':'DIRECT_COEFFICIENT_DOP853','rtol':RTOL,'atol':ATOL,
         'nfev':int(engine.nfev),'accepted_steps':1,'message':message,
         'rhs_time_hex':rhs_times,'actual_initial_state':_array_identity(actual_dop_initial),
         'initial_metric_distance':initial_distance,'initial_metric_norm':norm0,
         'final_metric_norm':dop_norm,'endpoint_norm_drift':abs(dop_norm-norm0),
         'selected_population':dop_p,'final_state':_array_identity(dop_final),
         'norm_sampling':'INITIAL_AND_FINAL_ONLY','dense_output_used':False}
    midpoint=[]; states={'raw_initial':raw_c0,'common_initial':common,'dop853_final':dop_final}
    g0=metric_frame_generator(s0); rf=metric_frame_generator(sf).R
    for row in grid['midpoint']:
        initial=common.copy(); y=g0.R@initial
        actual=solve_triangular(g0.R,y,lower=False,check_finite=True)
        distance=_distance(actual,common,s0.S)
        if distance>BUDGETS['initial_metric_distance_max']:
            raise ArithmeticError('midpoint coordinate roundoff exceeds common-IVP allowance')
        norms=[float(np.vdot(y,y).real)]; maxdef=g0.antihermitian_defect
        for step in row['steps']:
            y,g=candidate_step(provider,y,float.fromhex(step['ta_hex']),float.fromhex(step['tb_hex']))
            if not np.isfinite(y).all():
                raise ArithmeticError('midpoint nonfinite state')
            norms.append(float(np.vdot(y,y).real)); maxdef=max(maxdef,g.antihermitian_defect)
        final=solve_triangular(rf,y,lower=False,check_finite=True)
        p=_population(final,sf.S,selected_indices); error=_distance(final,dop_final,sf.S)
        result={'method':'UNCHANGED_CHOLESKY_MIDPOINT_RECURRENCE','nstep':row['nstep'],
          'actual_initial_state':_array_identity(actual),'initial_metric_distance':distance,
          'initial_metric_norm':_norm(actual,s0.S),'final_metric_norm':_norm(final,sf.S),
          'discrete_whitened_norm_history':norms,
          'discrete_norm_drift':float(max(abs(x-norms[0]) for x in norms)),
          'maximum_generator_defect':float(maxdef),'selected_population':p,
          'unaligned_metric_distance_to_dop853':error,
          'relative_metric_distance_to_dop853':error/np.sqrt(dop_norm),
          'phase_aligned_metric_distance_to_dop853':phase_aligned_metric_distance(final,dop_final,sf.S),
          'selected_population_difference':abs(p-dop_p),'final_state':_array_identity(final)}
        midpoint.append(result); states['midpoint_'+str(row['nstep'])+'_final']=final
    differences=[_distance(states['midpoint_'+str(a)+'_final'],states['midpoint_'+str(b)+'_final'],sf.S)
                 for a,b in zip(MIDPOINT_STEPS[:-1],MIDPOINT_STEPS[1:])]
    floor=100*np.finfo(float).eps*max(1.,np.sqrt(dop_norm))
    order=math.log2(differences[0]/differences[1]) if min(differences)>floor else None
    fine=midpoint[-1]
    gates={'common_initial_value':max([initial_distance]+[r['initial_metric_distance'] for r in midpoint])<=BUDGETS['initial_metric_distance_max'],
       'endpoint_state':fine['unaligned_metric_distance_to_dop853']<=BUDGETS['endpoint_unaligned_metric_distance_max'],
       'selected_population':fine['selected_population_difference']<=BUDGETS['endpoint_selected_population_difference_max'],
       'dop853_endpoint_norm':dop['endpoint_norm_drift']<=BUDGETS['dop853_endpoint_norm_drift_max'],
       'midpoint_discrete_norm':max(r['discrete_norm_drift'] for r in midpoint)<=BUDGETS['midpoint_discrete_norm_drift_max']}
    result={'schema':'BASS_R4V_G12_LOCAL_COMPARISON_V1','initial_value':initial_receipt,
       'dop853':dop,'midpoint':midpoint,'acceptance_budgets':dict(BUDGETS),
       'acceptance_gates':gates,'local_pilot_passed':all(gates.values()),
       'midpoint_refinement':{'successive_metric_differences':differences,
          'observed_order':order,'floating_floor':floor,
          'order_status':'OBSERVED_NOT_CERTIFIED' if order is not None else 'FLOOR_OR_EXACTNESS_UNRESOLVED'},
       'metric_condition_initial':float(np.linalg.cond(s0.S)),
       'metric_condition_final':float(np.linalg.cond(sf.S)),
       'derivative_scope':'MIDPOINT_USES_D_PLUS_D_DAGGER; INDEPENDENT_SDOT_NOT_VALIDATED_BY_THIS_COMPARISON',
       'operator_error_bound':'NOT_CERTIFIED','dop853_global_error_bound':'NOT_CERTIFIED',
       'observable_scope':'FINITE_SELECTED_SPAN_DIAGNOSTIC_NOT_CAPTURE',
       'new_native_operator_calls':0,**CLAIMS}
    return result,states


def analyze(plan,cache_directories,out):
    validate_plan(plan); out=Path(out).resolve()
    if out.exists():
        raise FileExistsError('create-only G12 output already exists')
    out.mkdir(parents=True,exist_ok=False)
    hp.write_new(out/'PLAN.json',plan)
    try:
        cache=ExactUnionCache(cache_directories,plan)
        hp.write_new(out/'CACHE_MANIFEST.json',cache.manifest)
        raw=np.zeros(18,dtype=np.complex128);raw[0]=1.
        if _array_identity(raw)!=plan['initial_raw_state_identity']:
            raise ValueError('initial raw state identity mismatch')
        result,states=compare_methods(cache,raw,plan['grid'],hp.SELECTED)
        path=out/'STATES.npz'
        with path.open('xb') as f:
            np.savez_compressed(f,**states)
        result.update(plan_sha256=plan['plan_sha256'],context_id=plan['context']['context_id'],
                      dependency_identity=plan['dependency_identity'],states_sha256=hp.sha(path),
                      cache_manifest_sha256=hp.sha(out/'CACHE_MANIFEST.json'),cache_reads=cache.reads,
                      model_routing='UNAVAILABLE_NO_INFERENCE')
        hp.write_new(out/'RESULT.json',result)
        return result
    except Exception as exc:
        hp.write_new(out/'FIRST_FAILURE.json',{'type':type(exc).__name__,'message':str(exc),
                       'new_native_operator_calls':0,**CLAIMS})
        raise


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__,allow_abbrev=False)
    sub=p.add_subparsers(dest='action',required=True)
    q=sub.add_parser('plan',allow_abbrev=False)
    for key in ('inputs','build','out'):
        q.add_argument('--'+key,required=True)
    q.add_argument('--threads',type=int,default=2)
    q=sub.add_parser('analyze',allow_abbrev=False)
    q.add_argument('--plan',required=True);q.add_argument('--plan-sha256',required=True)
    q.add_argument('--cache',action='append',required=True);q.add_argument('--out',required=True)
    a=p.parse_args(argv)
    if a.action=='plan':
        result=make_plan(a.inputs,a.build,threads=a.threads)
        hp.write_new(a.out,result)
        print(json.dumps({'plan':a.out,'file_sha256':hp.sha(a.out),
                          'plan_sha256':result['plan_sha256'],'queries':len(result['grid']['times_hex']),
                          'max_raw_attempts':result['maximum_raw_attempts'],'native_calls':0}))
        return 0
    if hp.sha(a.plan)!=a.plan_sha256:
        raise ValueError('exact plan file SHA mismatch')
    result=analyze(json.loads(Path(a.plan).read_text()),a.cache,a.out)
    print(json.dumps({k:result[k] for k in ('local_pilot_passed','new_native_operator_calls','production_admission')}))
    return 0 if result['local_pilot_passed'] else 2


if __name__=='__main__':
    raise SystemExit(main())
