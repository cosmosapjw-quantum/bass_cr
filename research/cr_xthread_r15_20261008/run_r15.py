"""New bass_cr optical functional only; archived donor endpoint proofs stay frozen."""
import argparse, hashlib, importlib.util, json, os, sys, time
from pathlib import Path
from fractions import Fraction as Q
from goal import cell_goal, native_goal, add, encode, decode, ContractError

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text())
def dump(p,x):Path(p).write_text(json.dumps(encode(x),indent=2)+'\n')

def verify_binding(root):
    binding=load(root/'SOURCE_BINDING.json')
    for rel,expected in binding['immutable_files_sha256'].items():
        if sha(root/rel)!=expected:raise ContractError('SOURCE_HASH_MISMATCH:'+rel)
    return binding

def validate_history(entries, cert, cells):
    if cert['time_s']!=[0,1250000000.] or len(cells)!=31:raise ContractError('CLOCK_CONTRACT')
    birth=[];n=1
    for i in range(32):
        root,point=entries['root'][i],entries['point'][i]
        if point['variant']!=0:raise ContractError('VARIANT_MISMATCH')
        if not root['t0']<root['t1']:raise ContractError('CLOCK_ORDER')
        if i and root['t0']!=entries['root'][i-1]['t1']:raise ContractError('CLOCK_GAP')
        m=len(point['p0'])
        if m not in (n,n+1):raise ContractError('BIRTH_DIMENSION')
        if len(root['parent_photons'])!=m:raise ContractError('BIRTH_PARENT_DIMENSION')
        if m==n+1:
            if root['pre_energy'][-1]!=[13.7,13.7] or root['parent_photons'][-1]!=root['birth_box']:
                raise ContractError('BIRTH_WEIGHT_OR_ENERGY')
            lo,hi=root['birth_box']
            if not lo<=point['p0'][-1]<=hi:raise ContractError('BIRTH_WEIGHT_MISMATCH')
            birth.append((i,Q.from_float(root['t0'])));n=m
        elif i and root['birth']!=0:raise ContractError('UNDECLARED_BIRTH')
        if i and cells[i-1]['time_s']!=[root['t0'],root['t1']]:raise ContractError('CLOCK_EVIDENCE_MISMATCH')
    if len(birth)!=6 or n!=7:raise ContractError('SIX_BIRTHS_REQUIRED')
    if [Q(0)]+[b for _,b in birth]!=list(map(Q,cert['birth_times_s'])):raise ContractError('BIRTH_CLOCK_MISMATCH')
    return birth

def run(stage,out):
    started=time.monotonic();out.mkdir(parents=True,exist_ok=False)
    rei=stage/'extracted/REI_XTHREAD_BRIDGE13_20261008/rei_bridge13_20261008'
    r14=stage/'extracted/BASS_CR_XTHREAD_R14_20261008_v1/CR_XTHREAD_R14_20261008'
    binding=verify_binding(rei)
    inv=load(stage/'SOURCE_INVENTORY.json')
    if not inv['all_ready']:raise ContractError('UNVERIFIED_SOURCE_ARCHIVES')
    sys.dont_write_bytecode=True
    sys.path[:0]=[str(rei/'research'),str(rei/'source')]
    import chain_defect as ch
    cert=load(rei/'results/final_interval/CHAIN_CERTIFICATE.json')
    evidence=load(rei/'results/final_interval/CELL_EVIDENCE.json')
    births=validate_history(ch.ENTRIES,cert,evidence)
    if sha(rei/'inputs/BRIDGE11_NATIVE.jsonl')!=cert['source_native_SHA256']:
        raise ContractError('NATIVE_CERTIFICATE_HASH')
    frozen=load(r14/'results/GOAL.json')
    if frozen['source_sha256']!=sha(rei/'inputs/BRIDGE12_CELL_CERTIFICATE.json'):
        raise ContractError('FIRST_CELL_ANCHOR_MISMATCH')
    parent2=r14/'inputs/rei_bridge12_20261008/results/final_verified/interval/CELL_CERTIFICATE.json'
    if sha(parent2)!=frozen['source_sha256']:raise ContractError('R14_PARENT_MISMATCH')
    if ch.PARENT['time_s']!=[ch.ENTRIES['root'][0]['t0'],ch.ENTRIES['root'][0]['t1']]:
        raise ContractError('FIRST_CLOCK_MISMATCH')
    for key in ('H','NH0','FHE'):
        field={'H':'H_s','NH0':'nH0_cm3','FHE':'f_he'}[key]
        if Q(getattr(ch,key).lo)!=decode(frozen['constants'][field]):raise ContractError('CONSTANT_MISMATCH:'+key)
    CT=decode(frozen['constants']['C_T_cm3_per_s']);NH=Q(ch.NH0.lo);H=Q(ch.H.lo);fhe=Q(ch.FHE.lo)
    tau=tuple(map(decode,frozen['nominal']));delta=tuple(map(decode,frozen['difference']))
    records=[{'index':0,'time_s':ch.PARENT['time_s'],'provenance':'FROZEN_R14_NOT_REEXECUTED',
              'forcing':tuple(map(decode,frozen['forcing'])),'initial':(Q(0),Q(0)),
              'remainder':decode(frozen['remainder']),'difference':delta,'native':tau,
              'incoming_error_scaled':[(Q(0),Q(0))]*5,
              'endpoint_signed_error_scaled':ch.PARENT['signed_error_continuum_minus_native_point_scaled'],
              'cumulative_native':tau,'cumulative_difference':delta}]
    previous=[ch.IV(*s) for s in ch.PARENT['signed_error_continuum_minus_native_point_scaled']]
    trace=[]
    for idx in range(1,32):
        ev=evidence[idx-1];root=ch.ENTRIES['root'][idx];pt=ch.ENTRIES['point'][idx]
        z0,z1,ein=ch.step_boxes(idx,previous)
        if [v.data() for v in ein]!=ev['initial_error_scaled']:raise ContractError('INCOMING_ERROR_MISMATCH')
        if all(v.lo==v.hi==0 for v in ein[:4]):raise ContractError('ILLEGAL_ERROR_RESET')
        tube,rad=ch.physics_tube(z0,ein)
        if list(map(str,rad))!=ev['Picard']['tube_radii_scaled']:raise ContractError('TUBE_MISMATCH')
        t0=ch.IV(root['t0']);h=ch.IV(root['t1'])-t0;n=len(z0)
        ff,_=ch.gas_photo_rhs(ch.IV(0,1),[ch.AD.var(v,j) for j,v in enumerate(tube)],t0,h,ch.EB[:n-4])
        N=[[x.mag() for x in v.g] for v in ff]
        # Stored validated residual supremum and incoming errors; new optical all-prefix response.
        A=[row+[ch.D(ev['R_max'][j])] for j,row in enumerate(N)]+[[ch.D(0)]*(n+1)]
        env,series=ch.exp_action_upper(A,[e.mag() for e in ein]+[ch.D(1)],ev['positive_envelope_series']['terms'])
        if series!=ev['positive_envelope_series']:raise ContractError('ENVELOPE_SERIES_MISMATCH')
        cp=[ch.usum(ch.UP.multiply(N[j][k],env[k]) for k in range(n)) for j in range(n)]
        slopes=[b-a for a,b in zip(z0,z1)];panels=[];R=[ch.D(0)]*n;ri=[ch.IV(0) for _ in range(n)]
        count=cert['residual_time_panels_per_new_cell']
        for k in range(count):
            s=ch.IV(ch.DOWN.divide(ch.D(k),ch.D(count)),ch.UP.divide(ch.D(k+1),ch.D(count)))
            rhs,_=ch.gas_photo_rhs(s,[a+s*d for a,d in zip(z0,slopes)],t0,h,ch.EB[:n-4])
            rr=[d-v for d,v in zip(slopes,rhs)]
            R=[max(a,b.mag()) for a,b in zip(R,rr)];ri=[a+b/ch.IV(count) for a,b in zip(ri,rr)]
            panels.append({'s':s.data(),'residual':[v.data() for v in rr]})
        if list(map(str,R))!=ev['R_max'] or [v.data() for v in ri]!=ev['integrated_residual']:
            raise ContractError('RESIDUAL_EVIDENCE_MISMATCH')
        # Exact f64 fences, not rounded native dt or midpoint density.
        L=Q.from_float(root['t1'])-Q.from_float(root['t0']);alpha=3*H*L
        density=tuple(map(Q,(-3*ch.H*t0).exp().data()));scale=CT*NH*L
        response=cell_goal(panels,[tuple(map(Q,v.data())) for v in ein[:3]],cp[:3],alpha,density,scale,fhe)
        nominal=native_goal([Q.from_float(v) for v in pt['old'][:3]],
                            [Q.from_float(v) for v in pt['gas'][:3]],alpha,density,scale,fhe)
        tau=add(tau,nominal);delta=add(delta,response['difference'])
        row={'index':idx,'time_s':[root['t0'],root['t1']],'cohorts':n-4,**response,'native':nominal,
             'alpha':alpha,'density_factor':density,'scale':scale,'fhe':fhe,
             'incoming_error_scaled':[v.data() for v in ein],
             'endpoint_signed_error_scaled':ev['endpoint_signed_error_scaled'],
             'all_prefix_abs_error_scaled':list(map(str,env[:n])),
             'jacobian_abs_majorant_scaled':[[str(x) for x in r] for r in N],
             'duhamel_feedback_upper_scaled':list(map(str,cp)),
             'prefix_series':series,'residual_panels':panels,
             'cumulative_native':tau,'cumulative_difference':delta,
             'nonlinear_remainder_semantics':'full nonlinear RHS difference bound N*sup|e|; includes linear feedback, not a Hessian-only remainder'}
        records.append(row)
        if idx in [i for i,_ in births]:
            trace.append({'index':idx,'clock_s':Q.from_float(root['t0']),
                          'source_weight_interval':list(map(Q.from_float,root['birth_box'])),
                          'nominal_birth_photons':Q.from_float(pt['p0'][-1]),
                          'new_photon_error_scaled':ein[-1].data(),
                          'gas_native_interface_delta':[Q.from_float(a)-Q.from_float(b) for a,b in zip(ch.ENTRIES['point'][idx-1]['gas'],pt['old'])],
                          'gas_target_jump':'identity','tau_target_jump':0,'tau_reset':False})
        previous=[ch.IV(*s) for s in ev['endpoint_signed_error_scaled']]
        dump(out/f'cell_{idx:02d}.json',row)
        print('CELL',idx,'incoming_HII',ein[0].data(),'delta_tau',*[f'{float(v):.16e}' for v in response['difference']],flush=True)
    result={'task':'CR-XTHREAD-R15','scope':'fixed-six-birth shadow continuum; first macro only',
            'status':'CONDITIONAL_OPTICAL_INTERVAL_ENCLOSED','time_s':[0,1250000000],
            'tau_native_piecewise_defined':tau,'signed_tau_difference_interval':delta,
            'tau_fixed_birth_continuum_interval':add(tau,delta),
            'signed_difference_strictly_positive':delta[0]>0,
            'birth_trace_checks':trace,'cells':32,'new_optical_residual_panels':31*count,
            'frozen_first_cell_panels':frozen['panels'],'first_cell_reexecuted':False,
            'endpoint_proofs_reexecuted':False,'source_quadrature':None,'observer_tail':None,
            'physical_atomic_fit_accuracy':None,'physical':'HOLD','conditional_arithmetic':'donor Decimal60 directed / outward exp-ln plus exact rational Taylor5/6 goal kernels',
            'wall_seconds':time.monotonic()-started}
    dump(out/'CELL_RESULTS.json',records);dump(out/'RESULTS.json',result)
    dump(out/'SOURCE_BINDING.json',{'donor':binding,'zip_inventory':inv,
        'R14_goal_sha256':sha(r14/'results/GOAL.json'),'donor_cell_evidence_sha256':sha(rei/'results/final_interval/CELL_EVIDENCE.json'),
        'code_sha256':{p.name:sha(p) for p in Path(__file__).parent.glob('*.py')}})
    print('RESULT',json.dumps({k:[float(v) for v in result[k]] for k in ('tau_native_piecewise_defined','signed_tau_difference_interval','tau_fixed_birth_continuum_interval')}),flush=True)

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--stage',type=Path,required=True);a.add_argument('--output',type=Path,required=True)
    x=a.parse_args();run(x.stage,x.output)
