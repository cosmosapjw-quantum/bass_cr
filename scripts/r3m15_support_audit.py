"""Read-only slab support diagnostic; no all-bound or continuum inference."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from cr_repro.r3m11 import _state_slab, file_sha, source_digest
from cr_repro.grid import GridSpec
from cr_repro.hydrogen import bound_quantum_numbers
from scripts.r3m15_coordinator import verify_seal, write_new

def audit(run):
    state=verify_seal(run)
    if state['done']!=state['nstep']:raise ValueError('incomplete state')
    result=json.loads((run/'result.json').read_text());cfg=result['config']
    grid=GridSpec.from_dict(cfg['grid']);axes=grid.axes(np)
    p=np.load(run/'state.npy',mmap_mode='r',allow_pickle=False)
    qns=bound_quantum_numbers(3);norm=np.zeros(len(qns));cap=np.zeros(len(qns));statecap=0.
    edges=[(axis<cfg['grid'][key][0]+cfg['absorber_width'])|(axis>cfg['grid'][key][1]-cfg['absorber_width']) for axis,key in zip(axes,['xlim','ylim','zlim'])]
    for i in range(0,grid.shape()[0],2):
        j=min(i+2,grid.shape()[0]);mask=(edges[0][i:j,None,None]|edges[1][None,:,None]|edges[2][None,None,:]).reshape(-1)
        basis=_state_slab(grid,cfg['b'],result['v_au'],cfg['z_stop']/result['v_au'],qns,i,j)
        density=abs(basis)**2;norm+=density.sum(axis=0)*grid.dv;cap+=density[mask].sum(axis=0)*grid.dv
        a=np.asarray(p[i:j]).reshape(-1)
        if not np.isfinite(a).all():raise ValueError('nonfinite state')
        statecap+=float(np.vdot(a[mask],a[mask]).real)*grid.dv
    gram=result['analysis']['gram_audit']
    return dict(schema='R3M15_SUPPORT_AUDIT_V1',source_digest=source_digest(),state_sha256=file_sha(run/'state.npy'),
      result_sha256=file_sha(run/'result.json'),quantum_numbers=qns,raw_channel_norms=norm.tolist(),
      raw_channel_norm_in_CAP_layer=cap.tolist(),channel_CAP_fraction=(cap/norm).tolist(),
      wavefunction_norm_in_CAP_layer=statecap,box=cfg['grid'],absorber_width=cfg['absorber_width'],
      Gram_rank=14 if gram['Gram_eigenvalues'][0]>1e-10*gram['Gram_eigenvalues'][1] else None,
      Gram_rank_threshold_relative=1e-10,Gram_condition=gram['Gram_condition'],
      support_interpretation='GEOMETRIC_SAMPLED_SUPPORT_DIAGNOSTIC_NOT_TAIL_BOUND',nmax4='NOT_RUN',
      all_bound_completion='OPEN',continuum_probability=None,dynamics_rerun=False)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();r=audit(a.run);write_new(a.out,r);print(json.dumps(r,indent=2))
