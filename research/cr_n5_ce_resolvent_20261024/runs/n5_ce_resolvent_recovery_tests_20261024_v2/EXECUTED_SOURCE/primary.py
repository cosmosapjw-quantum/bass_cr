"""Recovery v2 new execution identity, one coherent twelve-case finite-chain run."""
import argparse,json,time
from pathlib import Path
import numpy as np
from engine import *

def relative(a,b):
    den=max(abs(a),abs(b));return abs(a-b)/den if den else 0.

def run(unit,out,run_id):
    start=time.process_time();verify_inputs(unit);cfg=validate_case(json.loads((unit/'inputs/CASE_RECOVERY_V2.json').read_text()),run_id)
    ee,ce,channels,calls=providers(unit);anchor=json.loads((unit/'inputs/reused/c23d/APPLICABILITY.json').read_text())['anchor']
    need(anchor['theta_eV']==cfg['theta_eV'] and anchor['loss_anchor_eV_s']==cfg['loss_anchor_eV_s'] and ce.GAP_EV==cfg['gap_eV'],'PHYSICAL_ANCHOR_MISMATCH')
    sources={z:atoms(unit,z) for z in cfg['source_z']};rows=[];case_rows=[];allpass=True;matrix_count=0;rhs_count=0
    for chi in cfg['chi']:
        for N in cfg['grid_N']:
            common=grid(cfg['theta_eV'],chi,N,ce.GAP_EV)
            for R in cfg['R']:
                E=common[common<=R*cfg['theta_eV']];b=matrix(E,ee,anchor);matrix_count+=1
                hs=hazard(E[1:],channels['2S'],ce,cfg['n1s_cm3']);hp=hazard(E[1:],channels['2P'],ce,cfg['n1s_cm3'])
                sol,metrics,ok=solve_case(b,E,hs,hp);rhs_count+=9;allpass &= ok
                raw={'E_eV':E,'hazard_2S_s_inv':hs,'hazard_2P_s_inv':hp,**{k:v for k,v in b.items() if isinstance(v,np.ndarray)},**sol};projection=[]
                for z,(W,m) in sources.items():
                    pop,mask,info=project(E,W,m,ce.GAP_EV);values=averages(pop,info,sol,E,ce.GAP_EV)
                    good=max(info['count_relative_error'],info['energy_relative_error'])<=2e-12 and values['event_energy_relative_residual']<=2e-14
                    for ch in ['2S','2P','sum']:
                        mean=values[ch]['conditional_incoming_eV'];good &= mean is None or mean>=ce.GAP_EV
                    allpass &= good;rows.append({'chi':chi,'R':R,'N':N,'z':z,'projection':info,'values':values,'local_pass':bool(good)})
                    raw['source_'+z]=pop;raw['active_mask_'+z]=mask;projection.append({'z':z,**info})
                name=f'chi{chi:g}_R{R}_N{N}'
                with (out/(name+'.npz')).open('xb') as f:np.savez_compressed(f,**raw)
                case_record=metadata(name,chi,R,N,E,b,metrics,ok,projection)
                writej(out/(name+'.json'),case_record);case_rows.append(case_record)
                print(json.dumps({'case':name,'pass':ok}),flush=True)
    writej(out/'SOURCE_WEIGHTED_RESULTS.json',rows);writej(out/'MATRIX_CASES.json',case_rows)
    def val(chi,R,N,z,ch):return next(r for r in rows if (r['chi'],r['R'],r['N'],r['z'])==(chi,R,N,z))['values'][ch]
    comparisons=[]
    for chi in cfg['chi']:
        for z in cfg['source_z']:
            for ch in ['2S','2P','sum']:
                for R in cfg['R']:
                    fine=val(chi,R,2048,z,ch);mid=val(chi,R,1024,z,ch);coarse=val(chi,R,512,z,ch)
                    changes={k:relative(fine[k],mid[k]) if fine[k] is not None and mid[k] is not None else None for k in ['P_active','conditional_incoming_eV','conditional_event_time_s']}
                    ok=changes['P_active'] is not None and changes['P_active']<=5e-3 and all(changes[k] is not None and changes[k]<=1e-2 for k in ['conditional_incoming_eV','conditional_event_time_s'])
                    comparisons.append({'type':'grid','chi':chi,'z':z,'channel':ch,'R':R,'relative_2048_1024':changes,'coarse_512_probability_relative_change':relative(fine['P_active'],coarse['P_active']),'pass':ok});allpass &= ok
                change=relative(val(chi,40,2048,z,ch)['P_active'],val(chi,80,2048,z,ch)['P_active']);ok=change<=1e-5
                comparisons.append({'type':'boundary','chi':chi,'z':z,'channel':ch,'relative_R40_R80':change,'pass':ok});allpass &= ok
    writej(out/'FINITE_COMPARISONS.json',comparisons)
    writej(out/'PR101_DESCRIPTIVE_COMPARATORS.json',{'interpretation':'Prior uniform-hazard times saved MFPT, not an inequality certified against this discretization','saved_rows':json.loads((unit/'inputs/reused/pr101/CE_FIRST_EVENT_ESTIMATES.json').read_text())})
    result={'schema':'N5_CE_RESOLVENT_RECOVERY_PRIMARY_V2','status':'PASS' if allpass else 'FAILED_RETAINED','physical_input_id':cfg['physical_input_id'],'run_id':run_id,'matrix_count':matrix_count,'linear_RHS_count':rhs_count,'source_weighted_rows':len(rows),'new_ODE':0,'source_quadrature':0,'thermal_rate_quadrature':0,'old_historical_science_replay':0,'repeated_current_failed_attempt_case_count':1,'v1_excluded_from_admission':True,'v1_raw_status':'UNRECOVERED_AFTER_WORKSPACE_LOSS','cumulative_Q_including_failed_v1':matrix_count+2,'cumulative_complete_cases_including_v1':matrix_count+1,'cumulative_RHS_including_v1':rhs_count+9,'constructor_calls':calls,'process_cpu_s':time.process_time()-start,'global_error_bound':None,'global_completion_percent':None,'missing_total_non_EE_bound':None,'N5':'PARTIAL/OPEN','N6_N7':'NOT_ACTIVATED','scope':'conditional finite-state first-event diagnostic; no post-event evolution, thermal assimilation or continuum/global certificate'}
    writej(out/'RESULT.json',result);print(json.dumps(result));return 0 if allpass else 1
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--unit',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--run-id',required=True);a=p.parse_args();raise SystemExit(run(a.unit,a.output,a.run_id))
