"""One root-authorized native-knot representation; immutable recovery-v2 engine."""
import argparse,datetime,hashlib,json,os,resource,signal,subprocess,sys,time
from pathlib import Path
import numpy as np
import engine as eng
import dispatch as bounded
INPUT_ID='n5_ce_resolvent_native_knot_input_20261024_v3'
RUN_ID='n5_ce_resolvent_native_knot_primary_20261024_v3'

def expected_case():
    cfg=eng.expected_case();cfg.update(schema='N5_CE_RESOLVENT_NATIVE_KNOT_CASE_V3',physical_input_id=INPUT_ID,primary_run_id=RUN_ID,grid_N=[1024,2048],grid_family='GEOMETRIC_PLUS_NATIVE_CE_KNOTS_V1')
    return cfg

def verify(unit,run_id=None):
    manifest=json.loads((unit/'inputs/INPUT_MANIFEST_V3.json').read_text())
    for row in manifest['files']:
        data=(unit/row['path']).read_bytes();eng.need(len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'],'V3_INPUT_OR_DEPENDENCY_IDENTITY:'+row['path'])
    cfg=json.loads((unit/'inputs/CASE_NATIVE_KNOT_V3.json').read_text());eng.need(cfg==expected_case(),'V3_FROZEN_CASE_MISMATCH')
    if run_id is not None:eng.need(run_id==RUN_ID,'V3_RUN_ID_MISMATCH')
    return cfg

def native_grid(cfg,chi,N,channels,gap):
    old=eng.grid(cfg['theta_eV'],chi,N,gap);q=chi*cfg['theta_eV'];U=80*cfg['theta_eV']
    knots=np.concatenate([ch.energy_eV[(ch.energy_eV>=q)&(ch.energy_eV<=U)] for ch in channels.values()])
    return np.unique(np.r_[old,knots])

def control(unit,out):
    start=time.process_time();cfg=verify(unit);ee,ce,channels,calls=eng.providers(unit);checks=[]
    for chi in cfg['chi']:
        base=eng.grid(cfg['theta_eV'],chi,1024,ce.GAP_EV);E=native_grid(cfg,chi,1024,channels,ce.GAP_EV)
        np.testing.assert_array_equal(E[E<=10],base[base<=10]);eng.need(E[0]==chi*cfg['theta_eV'] and E[-1]==80*cfg['theta_eV'],'ENDPOINTS_CHANGED')
        for ch in channels.values():
            knots=ch.energy_eV[(ch.energy_eV>=E[0])&(ch.energy_eV<=E[-1])];eng.need(np.all(np.isin(knots,E)),'NATIVE_KNOT_OMITTED')
        for z in cfg['source_z']:
            W,m=eng.atoms(unit,z);p,mask,info=eng.project(E,W,m,ce.GAP_EV);eng.need(info['mass_above_10eV']==0 and info['mass_on_CE_active_nodes']==0,'SOURCE_SUPPORT_CHANGED')
        checks.append({'chi':chi,'base_nodes':len(base),'native_nodes':len(E),'minimum_spacing_eV':float(np.diff(E).min())})
    result={'status':'PASS','targeted_controls':1,'scope':'native inclusion, unchanged below10/source support, endpoints and immutable v2 dependencies','checks':checks,'provider_constructor_calls':calls,'new_matrices':0,'new_RHS':0,'process_cpu_s':time.process_time()-start}
    eng.writej(out/'TEST_RESULT.json',result);print(json.dumps(result));return 0

def relative(a,b):
    den=max(abs(a),abs(b));return abs(a-b)/den if den else 0.

def primary(unit,out,run_id):
    start=time.process_time();cfg=verify(unit,run_id);ee,ce,channels,calls=eng.providers(unit);anchor=json.loads((unit/'inputs/reused/c23d/APPLICABILITY.json').read_text())['anchor']
    eng.need(anchor['theta_eV']==cfg['theta_eV'] and anchor['loss_anchor_eV_s']==cfg['loss_anchor_eV_s'] and ce.GAP_EV==cfg['gap_eV'],'ANCHOR_CONTEXT_MISMATCH')
    sources={z:eng.atoms(unit,z) for z in cfg['source_z']};rows=[];case_rows=[];passed=True;matrices=0;rhs_count=0
    for chi in cfg['chi']:
        for N in cfg['grid_N']:
            common=native_grid(cfg,chi,N,channels,ce.GAP_EV)
            for R in cfg['R']:
                E=common[common<=R*cfg['theta_eV']];b=eng.matrix(E,ee,anchor);matrices+=1
                hs=eng.hazard(E[1:],channels['2S'],ce,cfg['n1s_cm3']);hp=eng.hazard(E[1:],channels['2P'],ce,cfg['n1s_cm3']);sol,metrics,ok=eng.solve_case(b,E,hs,hp);rhs_count+=9;passed &= ok
                raw={'E_eV':E,'hazard_2S_s_inv':hs,'hazard_2P_s_inv':hp,**{k:v for k,v in b.items() if isinstance(v,np.ndarray)},**sol};projection=[]
                for z,(W,m) in sources.items():
                    p,mask,info=eng.project(E,W,m,ce.GAP_EV);values=eng.averages(p,info,sol,E,ce.GAP_EV);good=max(info['count_relative_error'],info['energy_relative_error'])<=2e-12 and values['event_energy_relative_residual']<=2e-14
                    for ch in ['2S','2P','sum']:
                        mean=values[ch]['conditional_incoming_eV'];good &= mean is None or mean>=ce.GAP_EV
                    passed &= good;rows.append({'chi':chi,'R':R,'N':N,'z':z,'projection':info,'values':values,'local_pass':bool(good)});raw['source_'+z]=p;raw['active_mask_'+z]=mask;projection.append({'z':z,**info})
                name=f'chi{chi:g}_R{R}_N{N}'
                with (out/(name+'.npz')).open('xb') as f:np.savez_compressed(f,**raw)
                case_record=eng.metadata(name,chi,R,N,E,b,metrics,ok,projection);case_record['minimum_spacing_eV']=float(np.diff(E).min());eng.writej(out/(name+'.json'),case_record);case_rows.append(case_record);print(json.dumps({'case':name,'pass':ok}),flush=True)
    eng.writej(out/'SOURCE_WEIGHTED_RESULTS.json',rows);eng.writej(out/'MATRIX_CASES.json',case_rows)
    def values(chi,R,N,z,ch):return next(r for r in rows if (r['chi'],r['R'],r['N'],r['z'])==(chi,R,N,z))['values'][ch]
    comparisons=[]
    for chi in cfg['chi']:
        for z in cfg['source_z']:
            for ch in ['2S','2P','sum']:
                for R in cfg['R']:
                    fine=values(chi,R,2048,z,ch);mid=values(chi,R,1024,z,ch);changes={k:relative(fine[k],mid[k]) if fine[k] is not None and mid[k] is not None else None for k in ['P_active','conditional_incoming_eV','conditional_event_time_s']}
                    ok=changes['P_active'] is not None and changes['P_active']<=5e-3 and all(changes[k] is not None and changes[k]<=1e-2 for k in ['conditional_incoming_eV','conditional_event_time_s']);passed &= ok;comparisons.append({'type':'grid','chi':chi,'z':z,'channel':ch,'R':R,'relative_2048_1024':changes,'pass':ok})
                change=relative(values(chi,40,2048,z,ch)['P_active'],values(chi,80,2048,z,ch)['P_active']);ok=change<=1e-5;passed &= ok;comparisons.append({'type':'boundary','chi':chi,'z':z,'channel':ch,'relative_R40_R80':change,'pass':ok})
    eng.writej(out/'FINITE_COMPARISONS.json',comparisons)
    old=json.loads((unit/'runs/n5_ce_resolvent_recovery_primary_20261024_v2/SOURCE_WEIGHTED_RESULTS.json').read_text());representation=[]
    for row in rows:
        prior=next(r for r in old if (r['chi'],r['R'],r['N'],r['z'])==(row['chi'],row['R'],row['N'],row['z']))
        for ch in ['2S','2P','sum']:representation.append({'chi':row['chi'],'R':row['R'],'N':row['N'],'z':row['z'],'channel':ch,'point_P_active':prior['values'][ch]['P_active'],'native_P_active':row['values'][ch]['P_active'],'relative_difference':relative(prior['values'][ch]['P_active'],row['values'][ch]['P_active']),'interpretation':'representation comparison, not certified physical error'})
    eng.writej(out/'POINT_VS_NATIVE_REPRESENTATION.json',representation)
    result={'schema':'N5_CE_NATIVE_KNOT_PRIMARY_V3','status':'PASS' if passed else 'FAILED_RETAINED','physical_input_id':INPUT_ID,'run_id':run_id,'grid_family':cfg['grid_family'],'matrix_count':matrices,'positive_RHS_count':rhs_count,'source_rows':len(rows),'new_ODE':0,'source_quadrature':0,'thermal_rate_quadrature':0,'old_historical_science_replay':0,'N512_repeats':0,'cumulative_current_Q':matrices+14,'cumulative_complete_cases':matrices+13,'cumulative_RHS':rhs_count+117,'v2_failed_family_retained':True,'independent_reference_target_relative':5e-10,'provider_constructor_calls':calls,'process_cpu_s':time.process_time()-start,'global_error_bound':None,'global_completion_percent':None,'N5':'PARTIAL/OPEN','N6_N7':'NOT_ACTIVATED'}
    eng.writej(out/'RESULT.json',result);print(json.dumps(result));return 0 if passed else 1

def dispatch(unit,runid,mode):
    here=unit/'implementation';out=unit/'runs'/runid;out.mkdir(parents=True,exist_ok=False);lease=here/'.recovery_v2_lease';leased=False;started=False;rc=None;error=None;status='FAILED_RETAINED';start=time.monotonic();cpu0=time.process_time();before=resource.getrusage(resource.RUSAGE_CHILDREN);cpu,wall=(10,30) if mode=='control' else (30,60)
    try:
        with lease.open('x') as f:json.dump({'pid':os.getpid(),'run_id':runid,'mode':mode},f)
        leased=True;state=bounded.snapshot();bounded.writej(out/'RESOURCE_ADMISSION.json',state)
        eng.need(state['memory_admitted'],'MEMORY_ADMISSION_REJECTED');eng.need({0,8}.issubset(state['affinity']),'CPU_UNAVAILABLE');os.sched_setaffinity(0,{8})
        src=out/'EXECUTED_SOURCE';src.mkdir();pins=[]
        for name in ['engine.py','dispatch.py','native_knots_v3.py']:
            data=(here/name).read_bytes();(src/name).open('xb').write(data);pins.append({'path':'implementation/'+name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
        for name in ['CASE_NATIVE_KNOT_V3.json','INPUT_MANIFEST_V3.json']:(src/name).open('xb').write((unit/'inputs'/name).read_bytes())
        bounded.writej(out/'PRE_EXECUTION.json',{'run_id':runid,'mode':mode,'source_pins':pins,'coordinator_cpu':8,'worker_cpu':0,'native_threads':1,'CPU_limit_s':cpu,'wall_limit_s':wall,'RLIMIT_AS_bytes':512*bounded.MIB,'known_worker_subtotal_before_v3':20.694009114,'independent_reference_CPU_separate':.688471,'root_saved_output_analysis_CPU_separate':.054974463,'requested_model':'gpt-6.1-sol','observed_runtime_model':'UNOBSERVED'})
        env=os.environ.copy();env.update({k:'1' for k in bounded.THREADS});env['PYTHONDONTWRITEBYTECODE']='1'
        command=[sys.executable,'-B',str(Path(__file__).resolve()),'--unit',str(unit),'--run-id',runid,'--worker-mode',mode,'--output',str(out)]
        with (out/'stdout.txt').open('x') as stdout,(out/'stderr.txt').open('x') as stderr:
            p=subprocess.Popen(command,cwd=here,env=env,stdout=stdout,stderr=stderr,preexec_fn=lambda:bounded.limits(cpu),start_new_session=True);started=True
            try:rc=p.wait(timeout=wall)
            except subprocess.TimeoutExpired:
                os.killpg(p.pid,signal.SIGTERM)
                try:rc=p.wait(timeout=1)
                except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);rc=p.wait()
                raise RuntimeError('OWNED_WORKER_WALL_LIMIT')
        status='PASS' if rc==0 else 'FAILED_RETAINED'
    except Exception as e:error={'type':type(e).__name__,'message':str(e)}
    finally:
        if leased:lease.unlink()
        after=resource.getrusage(resource.RUSAGE_CHILDREN);receipt={'schema':'N5_NATIVE_KNOT_DISPATCH_V3','run_id':runid,'mode':mode,'status':status,'error':error,'child_started':started,'returncode':rc,'worker_cpu_s':after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,'worker_peak_RSS_KiB':after.ru_maxrss if started else None,'coordinator_cpu_s':time.process_time()-cpu0,'wall_s':time.monotonic()-start,'known_worker_subtotal_before_v3':20.694009114,'global_spend':None,'remaining':None,'currency':None,'requested_model':'gpt-6.1-sol','observed_runtime_model':'UNOBSERVED','EXECUTION':status,'PUBLICATION':'ROOT_OWNED','BACKUP':'ROOT_PENDING','DAG':'N5PARTIAL_OPEN_N6N7notactivated'};bounded.writej(out/'DISPATCH_RECEIPT.json',receipt)
    print(json.dumps({'output':str(out),**receipt}));return 0 if status=='PASS' else 1
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--unit',type=Path,required=True);p.add_argument('--run-id',required=True);p.add_argument('--mode',choices=['control','science']);p.add_argument('--worker-mode',choices=['control','science']);p.add_argument('--output',type=Path);a=p.parse_args();unit=a.unit.resolve()
    if a.worker_mode:raise SystemExit(control(unit,a.output) if a.worker_mode=='control' else primary(unit,a.output,a.run_id))
    eng.need(a.mode is not None,'MODE_REQUIRED');raise SystemExit(dispatch(unit,a.run_id,a.mode))
