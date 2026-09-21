"""Finite-grid normalized rank-one Gram diagnostic, separate from raw n<=3 sum."""
import json,sys,hashlib
from pathlib import Path
import numpy as np
from cr_repro.hydrogen import orbital
from cr_repro.observables import projectile_speed_au,estimator_gap_bound
from cr_repro.grid import GridSpec
from cr_repro.util import atomic_json
for name in sys.argv[1:]:
 out=Path(name);r=json.loads((out/'result.json').read_text());c=r['config'];g=GridSpec.from_dict(c['grid']);x,y,z=g.axes(np);v=projectile_speed_au(c['energy_keV_per_u']);t=c['z_stop']/v
 psi=np.load(out/'state.npy',mmap_mode='r');st=orbital(1,0,0,x[:,None,None]-c['b'],y[None,:,None],z[None,None,:]-c['z_stop'])*np.exp(1j*v*z[None,None,:]-.5j*v*v*t+.5j*t)
 nrm=float(np.sum(abs(st)**2)*g.dv);a=np.sum(st.conj()*psi)*g.dv;pb=float(abs(a)**2/nrm);bcomp=(a/nrm)*st;resid=psi-bcomp;region=z>c['capture_plane'];eb=float(np.sum(abs(bcomp[:,:,~region])**2)*g.dv);ec=float(np.sum(abs(resid[:,:,region])**2)*g.dv)
 bound=estimator_gap_bound(pb,eb,ec);actual=abs(r['analysis']['P_region']-pb)
 result={'eps_c_interpretation':'all residual states orthogonal to finite-grid 1s, including higher bound states; not continuum alone','definition':'normalized finite-grid rank-one Gram projection, supplemental to raw analytic n<=nmax overlap sum','P_n1_raw':float(abs(a)**2),'P_n1_metric':pb,'state_norm_n1':nrm,'eps_b_n1':eb,'eps_c_n1':ec,'estimator_gap_bound_n1':bound,'absolute_region_gap':actual,'inequality_satisfied':bool(actual<=bound+1e-13),'source_result_sha256':hashlib.sha256((out/'result.json').read_bytes()).hexdigest()}
 atomic_json(out/'n1_diagnostics.json',result);print(json.dumps({'run':out.name,**result}),flush=True)
