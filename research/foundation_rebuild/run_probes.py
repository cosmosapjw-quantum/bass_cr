#!/usr/bin/env python3
"""Bounded reproducible probes. A run writes a fresh result, never overwrites."""
import argparse,sys,json,time,platform,os
from pathlib import Path
import numpy as np
from scipy import linalg
import scipy
from bass_foundations import kernels as k

def plain(x):
 if isinstance(x,np.ndarray):return x.tolist()
 if isinstance(x,np.generic):return x.item()
 raise TypeError(type(x).__name__)

def main():
 p=argparse.ArgumentParser();p.add_argument('kind',choices=['atom','split','radial','galerkin']);p.add_argument('--n',type=int,default=32);p.add_argument('--length',type=float,default=16.);p.add_argument('--phase',type=float,default=0.);p.add_argument('--solver',choices=['arpack','lobpcg'],default='arpack');p.add_argument('--out',required=True);a=p.parse_args()
 out=Path(a.out)
 if out.exists():raise FileExistsError(out)
 out.parent.mkdir(parents=True,exist_ok=True)
 t=time.perf_counter(); rows=[]
 if a.kind=='atom':
  for rep in ['point','cell']:
   t0=time.perf_counter();A=k.atom_collocation(a.n,a.length,center=(0.,0.,a.phase*a.length/a.n),representation=rep)
   e,c,res=(k.ground_state(A) if a.solver=='arpack' else k.ground_state_preconditioned(A)[:3])
   rows.append({'representation':rep,'solver':a.solver,'n':a.n,'L':a.length,'h':A['h'],'phase_z':a.phase,'E_Eh':e,'E_plus_half':e+.5,'relative_ground_energy_error':abs(e+.5)/.5,'H_residual_Eh':res,'boundary_norm':float(np.sum(c[0]**2)+np.sum(c[-1]**2)+np.sum(c[:,0]**2)+np.sum(c[:,-1]**2)+np.sum(c[:,:,0]**2)+np.sum(c[:,:,-1]**2)),'seconds':time.perf_counter()-t0})
   # Durable row written before beginning the next operator solve.
   with out.with_name(out.stem+'_'+rep+'_PARTIAL.json').open('x') as f:json.dump(rows[-1],f,indent=2,default=plain,allow_nan=False)
 elif a.kind=='split':
  A=k.atom_collocation(a.n,a.length,representation='point');e,c,res=(k.ground_state(A) if a.solver=='arpack' else k.ground_state_preconditioned(A)[:3])
  for tau in [.05,.025,.0125,.00625]:
   b=(k.split_fixed_point(A,tau) if a.solver=='arpack' else k.split_fixed_point_preconditioned(A,tau));v=b.pop('state');b.update({'E_exact_Hh':e,'ground_Hh_residual':res,'state_distance_to_Hh_ground':float(np.linalg.norm(v-c)),'overlap_infidelity':float(1-abs(np.vdot(c,v))**2),'n':a.n,'L':a.length,'h':A['h']});rows.append(b)
   with out.with_name(out.stem+'_tau'+str(tau)+'_PARTIAL.json').open('x') as f:json.dump(b,f,indent=2,default=plain,allow_nan=False)
 elif a.kind=='radial':
  for R,ne,pq in [(64.,40,12),(96.,40,12),(128.,40,12),(128.,60,12),(128.,60,16)]:
   for ell in range(3):
    H,M,meta=k.radial_fem(R,ne,4,l=ell,quad_order=pq);e,c=linalg.eigh(H,M,subset_by_index=[0,3])
    for j in range(4):
     n=ell+j+1;exact=-.5/n**2;cc=c[:,j]
     # Include centrifugal energy as angular kinetic for virial diagnostic.
     Vc=k.radial_fem(R,ne,4,l=0,quad_order=pq)[2]['potential'] if ell else meta['potential']
     expV=float(cc@Vc@cc);expT=float(e[j]-expV)
     rows.append({'R':R,'elements':ne,'degree':4,'quadrature':pq,'dof':meta['ndof'],'l':ell,'n':n,'E_Eh':e[j],'exact_infinite_R_Eh':exact,'abs_error_Eh':abs(e[j]-exact),'generalized_residual':float(np.linalg.norm(H@cc-e[j]*M@cc)),'mass_norm':float(cc@M@cc),'virial_2T_plus_V':2*expT+expV})
 elif a.kind=='galerkin':
  for n in [3,5,7]:
   A=k.cutoff_coulomb_galerkin(n,10.,4.);rng=np.random.default_rng(2049);c=rng.normal(size=(n,n,n))+1j*rng.normal(size=(n,n,n))
   r=(.31,-.28,.43);d=k.translation_phase(A,r);err=np.linalg.norm(k.galerkin_action(d*c,A,center=r)-d*k.galerkin_action(c,A))/np.linalg.norm(k.galerkin_action(c,A))
   e0=linalg.eigh(k.dense_galerkin(A),eigvals_only=True,subset_by_index=[0,0])[0];e1=linalg.eigh(k.dense_galerkin(A,center=r),eigvals_only=True,subset_by_index=[0,0])[0]
   rows.append({'N_modes_per_axis':n,'L':10,'Rc':4,'E0_Eh':e0,'shifted_E0_Eh':e1,'translation_energy_difference':abs(e1-e0),'translation_operator_relative_residual':float(err),'boundary_model':'PERIODIZED_SPHERICALLY_TRUNCATED_COULOMB_NOT_FREE_SPACE_PRODUCTION'})
 result={'scope':'BOUNDED_FOUNDATION_PROBE_NOT_COLLISION','kind':a.kind,'rows':rows,'wall_seconds':time.perf_counter()-t,'environment':{'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__,'platform':platform.platform(),'OMP_NUM_THREADS':os.getenv('OMP_NUM_THREADS'),'OPENBLAS_NUM_THREADS':os.getenv('OPENBLAS_NUM_THREADS')},'production_admitted':False}
 out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2,default=plain,allow_nan=False)+'\n');print(json.dumps(result,indent=2,default=plain))
if __name__=='__main__':main()
