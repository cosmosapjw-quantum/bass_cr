#!/usr/bin/env python3
"""Opt-in bounded Galerkin/scout experiments with durable case results."""
import json,argparse,time,sys,platform
from pathlib import Path
import numpy as np
import scipy
from bass_foundations import kernels as k

def write_new(p,data):
 with p.open('x') as f:json.dump(data,f,indent=2,allow_nan=False);f.write('\n')
def main():
 p=argparse.ArgumentParser();p.add_argument('--outdir',required=True);p.add_argument('--modes',nargs='+',type=int,default=[15,31,47,63]);p.add_argument('--embedded',action='store_true');p.add_argument('--skip-moving',action='store_true');p.add_argument('--length',type=float,default=16.);p.add_argument('--radius',type=float,default=7.);a=p.parse_args()
 if any(n>81 for n in a.modes):raise ValueError('this bounded scout caps modes at81')
 out=Path(a.outdir);out.mkdir(parents=True,exist_ok=False)
 write_new(out/'RUN.json',{'argv':sys.argv,'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__,'platform':platform.platform(),'production_admitted':False})
 rows=[]
 for n in a.modes:
  t=time.perf_counter();A=k.cutoff_coulomb_galerkin(n,a.length,a.radius);e,c,res,meta=k.galerkin_ground_preconditioned(A,embedded=a.embedded)
  row={'modes':n,'embedded':a.embedded,'L':a.length,'Rc':a.radius,'E_Eh':e,'abs_E_plus_half':abs(e+.5),'H_residual':res,'effective_spacing_L_over_N':a.length/n,'kmax_axis':float(np.max(abs(A['ks']))),'iterations':meta['iterations'],'seconds':time.perf_counter()-t,'boundary_model':'PERIODIZED_SPHERICALLY_CUTOFF_COULOMB','not_a_capture_probability':True}
  write_new(out/f'GALERKIN_N{n}.json',row);rows.append(row);print(json.dumps(row),flush=True)
 for n in ([] if a.skip_moving else [5,7]):
  r=k.moving_galerkin_probe(k.cutoff_coulomb_galerkin(n,10.,4.),2.0079810665,1.3,[8,16,32,64,128])
  write_new(out/f'MOVING_N{n}.json',r)
 write_new(out/'COMPLETE.json',{'rows':rows,'production_admitted':False})
if __name__=='__main__':main()
