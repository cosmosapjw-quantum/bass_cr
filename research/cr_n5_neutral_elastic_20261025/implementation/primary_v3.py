"""Eight matrices, 112 RHS; no old replay; v3 reconstructed preparation."""
import argparse,csv,json,time
from pathlib import Path
import numpy as np
import engine_v3 as e

def main(unit,out,runid):
    start=time.process_time();c=e.verify(unit);e.need(runid==c['primary_run_id'],'RUN_ID_MISMATCH')
    tables={s['label']:e.parse_mtcs(unit/s['input'],s) for s in c['neutral_species']}
    rows=[];cases=[];peratom=[];matrices=0;rhs_count=0;generators=0;source_pairs=0;edge_pairs=0
    sources={z:e.atoms(unit,z) for z in c['source_z']}
    for chi in c['chi']:
      for R in c['R']:
       for N in c['grid_N']:
        name=f'chi{chi:g}_R{R}_N{N}'
        with np.load(unit/'inputs/reused/pr103'/(name+'.npz'),allow_pickle=False) as f:old={k:f[k] for k in f.files}
        new,meta,ok=e.combined_case(old,c,tables);matrices+=1;rhs_count+=14;generators+=2;edge_pairs+=2*(len(old['E_eV'])-1)
        meta.update(case=name,chi=chi,R=R,N=N,nodes=len(old['E_eV']),RHS_count=14,RHS_types={'probability_time_incoming_energy':6,'conditional_time':2,'bath_reward':6},global_error_bound=None)
        meta['separate_expansion_diagnostics']=[dict(species=s['label'],thermal_speed_parameter_max=1/(s['r']*chi),cold_recoil_second_moment_parameter_max=2*R/s['r'],interpretation='diagnostics only; neither is a proved error bound') for s in c['neutral_species']]
        for z,src in sources.items():
            values=e.source_average(old,new,src,z,c);ok &= values['ledger']['scaled_residual']<=c['tolerances']['energy']
            T=values['new']['no_CE_MFPT_s_active'];T0=values['old']['no_CE_MFPT_s_active'];delta=meta['checks']['delta_max']
            bound=bool(T<=T0*(1+c['tolerances']['bound']) and T>=T0/(1+delta)*(1-c['tolerances']['bound']))
            values['source_MFPT_comparison_bound_pass']=bound;ok &= bound
            rows.append(dict(case=name,chi=chi,R=R,N=N,z=z,**values))
            new['source_'+z]=old['source_'+z];new['active_mask_'+z]=old['active_mask_'+z]
            W=src['W_eV'];active=W>=old['E_eV'][0];coefficients=[]
            for sp in c['neutral_species']:
                mu,D,nu=e.coefficient(W,c,sp,tables[sp['label']],old['E_eV'][0])
                source_pairs+=int(active.sum());coefficients.append((mu,D))
            for i in range(len(W)):
                row=dict(case=name,z=z,atom=i,W_eV=float(W[i]),active_coefficient_domain=bool(active[i]))
                for j,sp in enumerate(c['neutral_species']):
                    row[sp['label']+'_mu_eV_s']=float(coefficients[j][0][i]) if active[i] else None
                    row[sp['label']+'_D_eV2_s']=float(coefficients[j][1][i]) if active[i] else None
                peratom.append(row)
        meta['pass_scoped']=bool(ok)
        with (out/(name+'.npz')).open('xb') as f:np.savez_compressed(f,**new)
        e.writej(out/(name+'.json'),meta);cases.append(meta)
        print(json.dumps(dict(case=name,pass_scoped=bool(ok))),flush=True)
        if not ok:
            e.writej(out/'PARTIAL_RESULTS.json',dict(status='FAILED_RETAINED',cases=cases,source_rows=rows,matrix_count=matrices,primary_RHS_count=rhs_count,new_neutral_generator_count=generators,process_cpu_s=time.process_time()-start))
            return 1
    comparisons=[];ok=True;tol=c['tolerances']
    names=['P_CE_active','mean_stop_s_active','ion_heat_eV_per_selected','neutral_heat_eV_per_selected','no_CE_MFPT_s_active','conditional_CE_energy_eV','conditional_CE_time_s']
    def find(chi,R,N,z):return next(r for r in rows if (r['chi'],r['R'],r['N'],r['z'])==(chi,R,N,z))['new']
    for chi in c['chi']:
      for z in c['source_z']:
       for R in c['R']:
        a=find(chi,R,1024,z);b=find(chi,R,2048,z);changes={k:e.relative(a[k],b[k]) for k in names}
        v=a['neutral_induced_relative_CE_change'];w=b['neutral_induced_relative_CE_change'];ad=abs(v-w)
        good=all(x<=tol['grid'] for x in changes.values()) and ad<=max(tol['grid_ce_absolute_floor'],tol['grid_ce_relative']*max(abs(v),abs(w)))
        comparisons.append(dict(type='grid',chi=chi,z=z,R=R,relative_1024_2048=changes,neutral_induced_relative_CE_change_1024=v,neutral_induced_relative_CE_change_2048=w,CE_change_absolute_difference=ad,pass_scoped=bool(good)));ok &= good
       a=find(chi,40,2048,z);b=find(chi,80,2048,z);changes={k:e.relative(a[k],b[k]) for k in names}
       ad=abs(a['neutral_induced_relative_CE_change']-b['neutral_induced_relative_CE_change'])
       good=all(x<=tol['boundary'] for x in changes.values()) and ad<=tol['boundary_ce_absolute']
       comparisons.append(dict(type='boundary',chi=chi,z=z,N=2048,relative_R40_R80=changes,CE_change_absolute_difference=ad,pass_scoped=bool(good)));ok &= good
    with (out/'PRIVATE_PER_ATOM_NEUTRAL_COEFFICIENTS.csv').open('x',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(peratom[0]));writer.writeheader();writer.writerows(peratom)
    e.writej(out/'SOURCE_WEIGHTED_RESULTS.json',rows);e.writej(out/'MATRIX_CASES.json',cases);e.writej(out/'FINITE_COMPARISONS.json',comparisons)
    result=dict(schema='N5_NEUTRAL_PRIMARY_V3',status='PASS' if ok else 'FAILED_RETAINED',input_id=c['input_id'],run_id=runid,matrix_count=matrices,primary_RHS_count=rhs_count,new_neutral_generator_count=generators,source_rows=len(rows),finite_comparisons=len(comparisons),private_per_atom_rows=len(peratom),active_source_coefficient_pair_count=source_pairs,edge_neutral_coefficient_pair_count=edge_pairs,old_generator_calls=0,old_source_projection_calls=0,old_primary_replay=0,source_quadrature=0,thermal_rate_quadrature=0,new_ODE=0,process_cpu_s=time.process_time()-start,global_error_bound=None,global_completion_percent=None,elastic_event_count=None,elastic_event_hazard=None,EXECUTION='COMPLETED' if ok else 'FAILED_RETAINED',PUBLICATION='ROOT_OWNED',BACKUP='ROOT_PENDING',DAG='N5_PARTIAL_OPEN_N6_N7_NOT_ACTIVATED')
    e.writej(out/'RESULT.json',result);print(json.dumps(result));return 0 if ok else 1
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--unit',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--run-id',required=True)
    a=p.parse_args();raise SystemExit(main(a.unit.resolve(),a.output,a.run_id))

