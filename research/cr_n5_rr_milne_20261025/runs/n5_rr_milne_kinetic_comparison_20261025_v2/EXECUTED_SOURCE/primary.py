"""Eight saved-chain consumers; exactly 160 planned new RHS; no baseline replay."""
import argparse
import itertools
import time
from pathlib import Path
import numpy as np
import rr_engine as e

def main(unit,out,runid):
    start=time.process_time();c=e.verify(unit);e.need(runid==c['primary_run_id'],'RUN_ID_MISMATCH')
    atom=e.provider(unit);sources={z:e.atoms(unit,z) for z in c['source_z']}
    rows=[];cases=[];actual=0
    def count(n):
        nonlocal actual
        actual+=n
    try:
        for chi,R,N in itertools.product(c['chi'],c['R'],c['grid_N']):
            name=f'chi{chi:g}_R{R}_N{N}'
            with np.load(unit/'inputs/reused/pr104'/(name+'.npz'),allow_pickle=False) as f:
                old={k:f[k] for k in f.files}
            new,checks,ok=e.consume(old,c,atom,count)
            meta=dict(case=name,chi=chi,R=R,N=N,active_nodes=len(old['K_diag']),new_RHS=20,checks=checks,pass_scoped=ok,global_error_bound=None)
            for z,src in sources.items():
                row=dict(case=name,chi=chi,R=R,N=N,z=z,**e.source_average(old,new,src,z,c))
                ok &= row['ledger']['scaled_residual']<=c['tolerances']['energy']
                rows.append(row)
            meta['pass_scoped']=bool(ok)
            with (out/(name+'.npz')).open('xb') as f:
                np.savez_compressed(f,**new)
            e.writej(out/(name+'.json'),meta);cases.append(meta)
            print(f'{name} pass_scoped={ok} new_rhs={actual}',flush=True)
            if not ok:
                e.writej(out/'PARTIAL_RESULTS.json',dict(status='FAILED_RETAINED',cases=cases,source_rows=rows,actual_primary_RHS=actual,process_cpu_s=time.process_time()-start))
                return 1
        comparisons=[]
        names=['P_RR_active','conditional_RR_photon_eV','conditional_RR_time_s','RR_photon_eV_per_selected','RR_internal_eV_per_selected','mean_stop_s_active','P_CE_active','delta_CE_active','delta_time_s_active']
        def find(chi,R,N,z):
            return next(v for v in rows if (v['chi'],v['R'],v['N'],v['z'])==(chi,R,N,z))
        for chi,z in itertools.product(c['chi'],c['source_z']):
            pairs=[('grid',find(chi,R,1024,z),find(chi,R,2048,z)) for R in c['R']]
            pairs.append(('boundary',find(chi,40,2048,z),find(chi,80,2048,z)))
            for kind,a,b in pairs:
                for key in names:
                    scale=max(abs(a[key]),abs(b[key]));diff=abs(a[key]-b[key])/scale if scale else 0.0
                    tol=c['tolerances'][('paired_' if key.startswith('delta_') else '')+kind]
                    comparisons.append(dict(chi=chi,z=z,kind=kind,observable=key,a_case=a['case'],b_case=b['case'],relative_difference=diff,tolerance=tol,pass_scoped=diff<=tol))
        passed=all(v['pass_scoped'] for v in comparisons)
        mapping=(c['REI_electron_mass_kg']/c['electron_mass_kg'])**1.5
        e.writej(out/'SOURCE_WEIGHTED_RESULTS.json',dict(rows=rows,comparisons=comparisons,paired_effect_uncertainty='Stored old PR104 solution uncertainty is inherited; stable responses use saved old solutions; subtraction is diagnostic only.',global_error_bound=None,global_completion_percent=None))
        e.writej(out/'RESULT.json',dict(schema='N5_H1_RR_PRIMARY_V1',status='PASS' if passed else 'FAILED_RETAINED',input_id=c['input_id'],run_id=runid,case_count=len(cases),planned_primary_RHS=160,actual_primary_RHS=actual,physical_RHS=136,response_diagnostic_RHS=24,source_rows=len(rows),comparisons=len(comparisons),comparison_failures=[v for v in comparisons if not v['pass_scoped']],old_primary_replay=0,old_generator_calls=0,old_source_projection_calls=0,source_quadrature=0,thermal_rate_quadrature=0,new_ODE=0,REI_alpha_mass_mapping_factor=mapping,REI_saved_alpha_g_sp_cm3_s=1.5893516133029456e-13,mapped_consumer_alpha_g_sp_cm3_s=1.5893516133029456e-13*mapping,process_cpu_s=time.process_time()-start,global_error_bound=None,global_completion_percent=None,EXECUTION='COMPLETED',PUBLICATION='ROOT_OWNED',BACKUP='ROOT_PENDING',DAG='N5_PARTIAL_OPEN_N6_N7_NOT_ACTIVATED'))
        return 0 if passed else 1
    except Exception as ex:
        e.writej(out/'FAILURE.json',dict(type=type(ex).__name__,message=str(ex),actual_primary_RHS=actual,completed_cases=len(cases),process_cpu_s=time.process_time()-start))
        raise

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--unit',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--run-id',required=True);a=p.parse_args();raise SystemExit(main(a.unit,a.output,a.run_id))
