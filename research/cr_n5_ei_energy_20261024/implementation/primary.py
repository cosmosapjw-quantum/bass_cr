"""Eight new combined matrices, twelve RHS each, no old generator replay."""
import argparse,csv,json,time
from pathlib import Path
import numpy as np
import engine as e

def source_coefficients(unit,out,c):
    rows=[];moments=[];raw={};npairs=0
    for z in c['source_z']:
        src=e.atoms(unit,z);W=src['W_eV'];rate=src['source_count_cm3_s'];pulse=src['pulse_count_cm3'];ee_mu=src['signed_drift_eV_s'];ee_D=src['diffusion_eV2_s']
        e.need(np.allclose(pulse,rate*c['pulse_exposure_s'],rtol=2e-15,atol=0),'PULSE_RATE_CONVENTION')
        mus=[];Ds=[]
        for sp in c['species']:
            mu,D=e.coefficient(W,c,sp);mus.append(mu);Ds.append(D);npairs+=len(W)
        total_mu=sum(mus);total_D=sum(Ds)
        for i in range(len(W)):
            row=dict(z=z,atom=i,W_eV=float(W[i]),source_count_cm3_s=float(rate[i]),pulse_count_cm3=float(pulse[i]),saved_EE_mu_eV_s=float(ee_mu[i]),saved_EE_D_eV2_s=float(ee_D[i]),EI_total_mu_eV_s=float(total_mu[i]),EI_total_D_eV2_s=float(total_D[i]),EI_to_EE_D_ratio=float(total_D[i]/ee_D[i]))
            for j,sp in enumerate(c['species']):row[sp['label']+'_mu_eV_s']=float(mus[j][i]);row[sp['label']+'_D_eV2_s']=float(Ds[j][i])
            rows.append(row)
        for label,mu,D in [('EE_saved',ee_mu,ee_D)]+[(sp['label'],mus[j],Ds[j]) for j,sp in enumerate(c['species'])]+[('EI_total',total_mu,total_D)]:
            fractions={}
            for sign,mask in [('positive',mu>0),('negative',mu<0),('zero',mu==0)]:fractions[sign]=dict(atom_fraction=float(mask.mean()),count_fraction=float(pulse[mask].sum()/pulse.sum()),energy_fraction=float((pulse[mask]@W[mask])/(pulse@W)))
            moments.append(dict(z=z,label=label,source_rate_weighted_mu_eV_s=float(rate@mu/rate.sum()),source_rate_weighted_D_eV2_s=float(rate@D/rate.sum()),source_rate_weighted_bath_gain_eV_cm3_s2=-float(rate@mu),initial_pulse_bath_gain_rate_eV_cm3_s=-float(pulse@mu),signed_drift_fractions=fractions))
        raw['W_'+z]=W;raw['EE_mu_'+z]=ee_mu;raw['EE_D_'+z]=ee_D;raw['EI_mu_'+z]=total_mu;raw['EI_D_'+z]=total_D
    with (out/'PER_ATOM_COEFFICIENTS.csv').open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    e.writej(out/'SOURCE_COEFFICIENT_MOMENTS.json',moments)
    pc=c['coefficient_plot_E_eV'];E=np.geomspace(pc['min'],pc['max'],pc['count']);raw['plot_E_eV']=E
    ee_sp=dict(n_cm3=c['ne_cm3'],Z=1.,r=1.,theta_eV=c['theta_eV'],lnLambda=c['lnLambda_ee'])
    raw['plot_EE_mu'],raw['plot_EE_D']=e.coefficient(E,c,ee_sp)
    for sp in c['species']:raw['plot_'+sp['label']+'_mu'],raw['plot_'+sp['label']+'_D']=e.coefficient(E,c,sp)
    with (out/'COEFFICIENT_PLOT_DATA.npz').open('xb') as f:np.savez_compressed(f,**raw)
    return npairs,len(rows),pc['count']*len(c['species'])

def main(unit,out,run_id):
    start=time.process_time();c=e.verify(unit);e.need(run_id==c['primary_run_id'],'RUN_ID_MISMATCH');pairs,atoms,plotpairs=source_coefficients(unit,out,c)
    rows=[];cases=[];matrices=0;rhs=0;edgepairs=0
    for chi in c['chi']:
      for R in c['R']:
       for N in c['grid_N']:
        name=f'chi{chi:g}_R{R}_N{N}';path=unit/'inputs/reused/native_v3'/(name+'.npz')
        with np.load(path,allow_pickle=False) as f:old={k:f[k] for k in f.files}
        new,meta,ok=e.combined_case(old,c);matrices+=1;rhs+=12;edgepairs+=(len(old['E_eV'])-1)*len(c['species'])
        meta.update(case=name,chi=chi,R=R,N=N,nodes=len(old['E_eV']),RHS_count=12)
        for z in c['source_z']:
            src=e.atoms(unit,z);values=e.source_average(old,new,src,z,c)
            ok &= values['ledger']['scaled_residual']<=c['tolerances']['energy']
            tnew=values['new']['no_CE_MFPT_s_active'];tee=values['old']['no_CE_MFPT_s_active'];delta=meta['checks']['delta_max']
            values['source_MFPT_comparison_bound_pass']=bool(tnew<=tee*(1+c['tolerances']['bound']) and tnew>=tee/(1+delta)*(1-c['tolerances']['bound']))
            ok &= values['source_MFPT_comparison_bound_pass']
            rows.append(dict(case=name,chi=chi,R=R,N=N,z=z,**values))
            new['source_'+z]=old['source_'+z];new['active_mask_'+z]=old['active_mask_'+z]
        meta['pass_scoped']=bool(ok)
        with (out/(name+'.npz')).open('xb') as f:np.savez_compressed(f,**new)
        e.writej(out/(name+'.json'),meta);cases.append(meta);print(json.dumps(dict(case=name,pass_scoped=bool(ok))),flush=True)
        if not ok:
            e.writej(out/'PARTIAL_RESULTS.json',dict(cases=cases,source_rows=rows,matrix_count=matrices,RHS_count=rhs,process_cpu_s=time.process_time()-start,status='FAILED_RETAINED'))
            return 1
    comparisons=[];ok=True;tol=c['tolerances']
    def find(chi,R,N,z):return next(r for r in rows if (r['chi'],r['R'],r['N'],r['z'])==(chi,R,N,z))['new']
    names=['P_CE_active','ion_heat_eV_per_selected','no_CE_MFPT_s_active','conditional_CE_energy_eV','conditional_CE_time_s']
    for chi in c['chi']:
      for z in c['source_z']:
       for R in c['R']:
        a=find(chi,R,1024,z);b=find(chi,R,2048,z);changes={k:e.relative(a[k],b[k]) for k in names};va=a['EI_induced_relative_CE_change'];vb=b['EI_induced_relative_CE_change'];ce_abs=abs(va-vb);ce_rel=e.relative(va,vb)
        good=all(v<=tol['grid'] for v in changes.values()) and ce_abs<=max(tol['grid_ce_absolute_floor'],tol['grid_ce_relative']*max(abs(va),abs(vb)))
        comparisons.append(dict(type='grid',chi=chi,z=z,R=R,relative_1024_2048=changes,EI_induced_relative_CE_change_1024=va,EI_induced_relative_CE_change_2048=vb,EI_change_absolute_difference=ce_abs,EI_change_relative_difference=ce_rel,pass_scoped=good));ok &= good
       a=find(chi,40,2048,z);b=find(chi,80,2048,z);changes={k:e.relative(a[k],b[k]) for k in names};ce_abs=abs(a['EI_induced_relative_CE_change']-b['EI_induced_relative_CE_change']);good=all(v<=tol['boundary'] for v in changes.values()) and ce_abs<=tol['boundary_ce_absolute']
       comparisons.append(dict(type='boundary',chi=chi,z=z,N=2048,relative_R40_R80=changes,EI_change_absolute_difference=ce_abs,pass_scoped=good));ok &= good
    e.writej(out/'SOURCE_WEIGHTED_RESULTS.json',rows);e.writej(out/'MATRIX_CASES.json',cases);e.writej(out/'FINITE_COMPARISONS.json',comparisons)
    result=dict(schema='N5_EI_PRIMARY_V1',status='PASS' if ok else 'FAILED_RETAINED',input_id=c['input_id'],run_id=run_id,matrix_count=matrices,primary_RHS_count=rhs,source_atom_count=atoms,source_per_ion_coefficient_pair_count=pairs,edge_per_ion_coefficient_pair_count=edgepairs,plot_per_ion_coefficient_pair_count=plotpairs,plot_EE_coefficient_pair_count=c['coefficient_plot_E_eV']['count'],source_rows=len(rows),old_generator_calls=0,old_source_projection_calls=0,old_primary_replay=0,source_quadrature=0,thermal_rate_quadrature=0,new_ODE=0,process_cpu_s=time.process_time()-start,global_error_bound=None,global_completion_percent=None,elastic_event_count=None,elastic_event_hazard=None,EXECUTION='COMPLETED' if ok else 'FAILED_RETAINED',PUBLICATION='ROOT_OWNED',BACKUP='ROOT_PENDING',DAG='N5_PARTIAL_OPEN_N6_N7_NOT_ACTIVATED')
    e.writej(out/'RESULT.json',result);print(json.dumps(result));return 0 if ok else 1
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--unit',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--run-id',required=True);a=p.parse_args();raise SystemExit(main(a.unit.resolve(),a.output,a.run_id))
