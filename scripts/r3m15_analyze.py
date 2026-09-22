"""Recompute bounded matrix comparisons from sealed results, without propagation."""
import argparse
import json
import math
from pathlib import Path
from r3m15_coordinator import SOURCE, sha, verify_seal, validate_config
from r3m15_gate import observable_change, spatial_order

def analyze(root):
    rows={};configs={};environments=[]
    for job in ('A','B','C'):
        p=root/job;complete=json.loads((p/'COMPLETE.json').read_text())
        verify_seal(p/'collision')
        if sha(p/'collision/result.json')!=complete['result_sha256']:raise ValueError('result binding mismatch')
        cfg=json.loads((p/'config.json').read_text());validate_config(job,cfg);configs[job]=cfg
        r=json.loads((p/'collision/result.json').read_text());prep=json.loads((p/'preparation/receipt.json').read_text())
        if prep['source_digest']!=SOURCE or sha(p/'preparation/initial.npy')!=prep['initial_state_sha256']:
            raise ValueError('preparation source/state mismatch')
        witness=json.loads((p/'collision/r3m14_initial_binding.json').read_text())
        if witness['status']!='PASS_BYTE_IDENTICAL_INTERNAL_INITIAL_TO_PREPARED' or witness['actual_source_digest']!=SOURCE:
            raise ValueError('witness failure')
        if sha(p/'preparation/receipt.json')!=witness['prepared_receipt_sha256']:raise ValueError('receipt binding mismatch')
        if {k:v for k,v in r['config'].items() if not k.startswith('_r3m11')}!=cfg:
            raise ValueError('result/config mismatch')
        environments.append(witness['runtime_environment'])
        a=r['analysis']['gram_audit'];nested=a['P_span_by_nmax']
        numeric=[*nested.values(),a['P_region'],a['wavefunction_norm'],a['Gram_condition'],r['dt_actual']]
        if not all(math.isfinite(v) for v in numeric):raise ValueError('nonfinite matrix output')
        rows[job]={'dx':cfg['grid']['dx'],'P1':nested['1'],'P2':nested['2'],'P3':nested['3'],
          'P_region':a['P_region'],'norm':a['wavefunction_norm'],'Gram_condition':a['Gram_condition'],
          'Gram_eigenvalues':a['Gram_eigenvalues'],'Gram_rank':len(a['quantum_numbers']),
          'raw_channel_norms':a['finite_grid_state_norms'],
          'nested_n3_increment':(nested['3']-nested['2'])/nested['3'],
          'Hamiltonian_residual_Eh':prep['initial']['stationary_residual_Eh'],
          'target_only_diagnostics':prep['target_only'],
          'target_energy_Eh':prep['initial']['energy_Eh'],'actual_dt':r['dt_actual'],
          'CAP':{k:cfg[k] for k in ('absorber_width','absorber_power','absorber_reference_dt')},
          'config_sha256':sha(p/'config.json'),'result_sha256':sha(p/'collision/result.json'),
          'initial_sha256':sha(p/'preparation/initial.npy'),'final_sha256':sha(p/'collision/state.npy'),
          'source_digest':SOURCE,'chunks':complete['chunks'],'restarts':complete['restarts'],
          'binding':witness['status'],'support':json.loads((p/'support.json').read_text())}
        if rows[job]['support']['state_sha256']!=rows[job]['final_sha256']:
            raise ValueError('support diagnostic state binding mismatch')
        # Expose the actual transverse nuclear registration of each cell lattice.
        # Different b/h fractions can spoil a single smooth h-power error model.
        h=cfg['grid']['dx'];offsets={}
        for label,position in [('target',0.),('projectile',cfg['b'])]:
            delta=[]
            for axis,pos in [('xlim',position),('ylim',0.)]:
                lo,hi=cfg['grid'][axis]
                delta.append(min(abs(lo+(i+.5)*h-pos) for i in range(round((hi-lo)/h))))
            offsets[label]={'nearest_abs_dx_dy_a0':delta,'offset_in_grid_cells':[v/h for v in delta],
                            'nearest_transverse_radius_a0':math.hypot(*delta)}
        rows[job]['nuclear_grid_registration']=offsets
    if any(e!=environments[0] for e in environments):raise ValueError('runtime identity mismatch')
    if len({r['actual_dt'] for r in rows.values()})!=1:raise ValueError('different actual dt')
    metrics={key:observable_change(rows['B'][key],rows['A'][key]) for key in ('P1','P2','P3')}
    orders={key:spatial_order(rows['C'][key],rows['A'][key],rows['B'][key]) for key in ('P1','P2','P3')}
    for key,value in orders.items():
        value['relative_fine_extrapolation_correction']=(abs(value['extrapolated']-rows['B'][key])/abs(rows['B'][key])
                                                       if value['extrapolated'] is not None and rows['B'][key]!=0 else None)
    return {'schema':'R3M15_MATRIX_ANALYSIS_V1','matrix_completion':'COMPLETE_3_OF_3','new_collision_count':3,
      'rows':rows,'spatial_pair_metrics':metrics,'empirical_order':orders,
      'same_grid_preparation_sensitivity':json.loads((root/'A_sensitivity.json').read_text()),
      'spatial_planning_target_relative':.003,'global_spatial_convergence':'NO_GO',
      'empirical_diagnostics_are_certified_bounds':False,'cross_grid_pair_theorem_used':False,
      'all_bound_completion':'OPEN','bgrid_admission':'NO_GO','physical_rates_evaluated':False,
      'energies_50_225_executed':False,'AOCC_trajectory_executed':False,
      'runtime_environment':environments[0],'historical_files_changed':False}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();result=analyze(a.root)
    with a.out.open('x') as f:json.dump(result,f,indent=2,allow_nan=False)
    print(json.dumps({'metrics':result['spatial_pair_metrics'],'orders':result['empirical_order']},indent=2))
