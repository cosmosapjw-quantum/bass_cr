"""Create-only R3M12 controlled single-b configurations; never starts b-grid."""
from pathlib import Path
import argparse,copy,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from cr_repro.grid import GridSpec

def build_plan(out, backend='auto'):
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    root=Path(__file__).resolve().parents[1]
    base=json.loads((root/'configs/tdl_prod_100kevu_b2_baseline.json').read_text())
    base.update(absorber_reference_dt=.05,backend=backend,projection_block_size=65536)
    rows=[]
    def put(name,cfg,action,stage):
        if action in ('initial','tdl'):GridSpec.from_dict(cfg['grid'])
        path=out/(name+'.json');path.write_text(json.dumps(cfg,indent=2)+'\n')
        dest=out/'outputs'/name
        rows.append(dict(name=name,stage=stage,action=action,config=str(path),output=str(dest),
          command=[sys.executable,'-m','cr_repro.r3m11',action,'--config',str(path),'--out',str(dest)]))
    # Fix total imaginary time while reducing the imaginary-time splitting step.
    for dx in [.4,.3125,.25]:
        for tau in [.05,.025,.0125]:
            cfg=copy.deepcopy(base);cfg['grid']['dx']=dx;cfg.update(imag_dt=tau,imag_steps=round(15/tau))
            put('initial_dx'+str(dx)+'_tau'+str(tau),cfg,'initial','A_initial_only')
    # These are candidate configs, NOT automatically cleared for execution.
    # The state-preparation step must be selected/frozen from A, not data fitting.
    base.update(imag_dt=.0125,imag_steps=1200)
    for name,dx,dt in [('base',.4,.05),('dt025',.4,.025),('dx03125',.3125,.05),('dx025',.25,.05)]:
        cfg=copy.deepcopy(base);cfg['grid']['dx']=dx;cfg['dt']=dt
        put('tdl_'+name,cfg,'tdl','B_candidate_after_initial_review')
    for name in ['baseline','basis_large']:
        ac=json.loads((root/f'configs/aocc_prod_100kevu_b2_{name}.json').read_text())
        probe=copy.deepcopy(ac);probe['audit_times_au']=[-6.474164630741937,0.,6.474164630741937]
        put('aocc_audit_'+name,probe,'aocc-audit','A_matrix_only')
        put('aocc_'+name,ac,'aocc','B_controlled_replay_same_old_basis')
        half=copy.deepcopy(ac);half['dt']=ac['dt']/2
        put('aocc_'+name+'_dt_half',half,'aocc','B_controlled_replay_same_old_basis')
    # Isolate radial size from the old simultaneous exponent-range change.
    ac=json.loads((root/'configs/aocc_prod_100kevu_b2_basis_large.json').read_text());ac['alpha_max']=100.
    put('aocc_large_same_range',ac,'aocc','C_radial_ladder_still_s_p_only')
    (out/'PLAN.json').write_text(json.dumps(dict(schema='R3M12_CONTROLLED_SINGLE_B_PLAN_V1',bgrid_admitted=False,rows=rows),indent=2)+'\n')
    import shlex
    (out/'COMMANDS.sh').write_text('# Review stages before execution. No automatic b-grid.\n'+'\n'.join('# '+v['stage']+'\n'+shlex.join(v['command']) for v in rows)+'\n')
    return rows

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True);p.add_argument('--backend',choices=['auto','numpy','cupy'],default='auto');a=p.parse_args()
    print(json.dumps({'created':len(build_plan(a.out,a.backend)),'bgrid_admitted':False}))
