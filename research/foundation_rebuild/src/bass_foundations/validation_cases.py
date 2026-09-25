"""Fixed R2 diagnostic cases. Produces matrices/scalars, never a collision run."""
from __future__ import annotations
import argparse,json,time
from pathlib import Path
import numpy as np
from scipy import linalg,integrate,special
from .two_center import Trajectory,Quadrature,assemble,hydrogen_channels,symmetric_channels,basis_values,prolate_grid
from .radial_basis import RadialSpec,atomic_bank


def write(path,value):
    with Path(path).open('x') as f:json.dump(value,f,indent=2,allow_nan=False);f.write('\n')


def run(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);rows=[]
    for R in (.5,2.,6.):
        snap=assemble(Trajectory(((0,0,0),(R,0,0))),hydrogen_channels(1),0.,Quadrature(40,32,24,2.))
        S=np.exp(-R)*(1+R+R*R/3);J=(1-(1+R)*np.exp(-2*R))/R;K=np.exp(-R)*(1+R)
        refS=np.array([[1,S],[S,1]]);refH=np.array([[-.5-J,-.5*S-K],[-.5*S-K,-.5-J]])
        row={'case':'analytic_1s','separation':R,'S_error':float(np.max(abs(snap.S-refS))),
             'H_error':float(np.max(abs(snap.H-refH))),'identity':snap.identity,'metadata':snap.metadata}
        row['passed']=row['S_error']<3e-11 and row['H_error']<3e-10
        with (out/f'analytic_R{R}.npz').open('xb') as f:np.savez(f,S=snap.S,H=snap.H,D=snap.D)
        write(out/f'analytic_R{R}.json',row);rows.append(row)
    tr=Trajectory(((0,0,0),(2,0,0)),((0,0,0),(0,0,2.0079810665)));basis=hydrogen_channels(2)
    ladder=[];previous=None
    for nr,ne,np_ in [(24,20,24),(40,32,48),(64,48,64)]:
        start=time.perf_counter();snap=assemble(tr,basis,.31,Quadrature(nr,ne,np_,1.))
        row={'quadrature':[nr,ne,np_],'seconds':time.perf_counter()-start,'identity':snap.identity,
             'min_metric_eigenvalue':float(np.linalg.eigvalsh(snap.S)[0]),'basis_size':len(basis)}
        if previous is not None:
            row['relative_change']={name:float(np.linalg.norm(getattr(snap,name)-getattr(previous,name))/max(1.,np.linalg.norm(getattr(snap,name)))) for name in ('S','H','D')}
        with (out/f'quadrature_{nr}.npz').open('xb') as f:np.savez(f,S=snap.S,H=snap.H,D=snap.D)
        write(out/f'quadrature_{nr}.json',row);ladder.append(row);previous=snap
    # Fixed diagnostic allowance, not an admission of the 0.30% capture budget.
    quad_pass=max(ladder[-1]['relative_change'].values())<3e-6
    rows.append({'case':'quadrature_ladder_nmax2','passed':quad_pass,'ladder':ladder,'capture_error_estimate':None})
    bank=atomic_bank(RadialSpec(radius=128.,elements=40,degree=4,lmax=3,bound_nmax=4,positive_per_l=1,positive_emax=2.))
    modes=[{'l':m.l,'n':m.principal_n,'energy':m.energy,'residual':m.residual,'identity':m.identity,
            'kind':'BOUND_FINITE_DOMAIN' if m.principal_n is not None else 'POSITIVE_FINITE_DOMAIN_PSEUDOSTATE'} for m in bank]
    worst=max(abs(m.energy+.5/m.principal_n**2) for m in bank if m.principal_n is not None)
    row={'case':'radial_bank','modes':modes,'symmetric_angular_channels':len(symmetric_channels(bank)),
         'worst_bound_energy_error':worst,'passed':worst<2e-7,'all_bound_complete':False}
    write(out/'radial_bank.json',row);rows.append(row)
    result={'schema':'BASS_FND_R2_FIXED_DIAGNOSTICS_V1','passed':all(r['passed'] for r in rows),'cases':rows,
      'scope':'BOUNDED_TWO_CENTER_OPERATOR_AND_ATOMIC_BASIS_TESTS','production_admission':'HOLD','all_bound':'OPEN',
      'capture_gap_resolved':False,'full_fem_cross_center_convergence':'NOT_ESTABLISHED',
      'common_capture_pilot':'CONTRACT_ONLY_NOT_EXECUTED','collision_runs':0}
    write(out/'RESULT.json',result);return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True);a=p.parse_args()
    r=run(a.out);print(json.dumps({'passed':r['passed'],'production_admission':'HOLD','out':str(Path(a.out).resolve())}))
    raise SystemExit(0 if r['passed'] else 1)
