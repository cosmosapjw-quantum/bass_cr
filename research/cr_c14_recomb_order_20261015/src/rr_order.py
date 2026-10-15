"""Independent reference and experiments for local recombination electron feedback."""
from __future__ import annotations
import numpy as np
from scipy.integrate import solve_ivp
from physical_age import Gas
from transport import integrate,alpha_owner_rr

def reference(ns, g:Gas, a0=.1, a1=.11, q=0.,rtol=1e-12,atol=1e-13):
    m=ns['model'];y=ns['nhe']/(m.nh*125.)
    n0=m.nh
    def rhs(ln_a,x):
        a=np.exp(ln_a)
        h,he1,he2,he3=x
        # No photons, electron translational escape only, T adiabatic.
        T=g.temp_K*(a0/a)**2
        nH=n0/a**3
        xe=1-h+y*(he2+2*he3)
        r=alpha_owner_rr(T)*nH*xe/m.hubble(a,q)
        return [r[0]*(1-h),r[1]*he2,-r[1]*he2+r[2]*he3,-r[2]*he3]
    sol=solve_ivp(rhs,[np.log(a0),np.log(a1)],
        [g.xhi,g.xhei,g.xheii,g.xheiii],method='DOP853',rtol=rtol,atol=atol)
    if not sol.success:raise RuntimeError(sol.message)
    return sol.y[:,-1],g.temp_K*(a0/a1)**2,sol.nfev

def orders(ns,numbers=(8,16,32,64,128),g=None,q=0.,ne_method="frozen"):
    if g is None:g=Gas(.9,.85,.15,0.,4000.)
    ref,T,nfev=reference(ns,g,q=q)
    rows=[]
    for n in numbers:
        got=integrate(ns,q,n,gas0=g,recombination=True,source_scale=0,
                      rr_ne_method=ne_method)
        v=np.array([got['gas_final'][i] for i in ('xhi','xhei','xheii','xheiii')])
        rows.append({'n':n,'xhi':float(v[0]),'xhi_error':float(v[0]-ref[0]),
                     'heii_error':float(v[2]-ref[2]),
                     'temperature_error':float(got['gas_final']['temp_K']-T),
                     'time_s':got['elapsed_wall_seconds']})
    return {'reference_xhi':float(ref[0]),'reference_heii':float(ref[2]),'reference_T':float(T),
            'nfev':nfev,'rows':rows}
if __name__=='__main__':
  from pathlib import Path
  from owner_age_bridge import owner_namespace
  n=owner_namespace(Path('/home/cosmosapjw/Dropbox/bianchi/rei_bianchi'))
  for T in (4000.,9000.):
      for method in ('frozen','midpoint'):
          print('CASE',T,method,orders(n,g=Gas(.9,.85,.15,0.,T),ne_method=method),flush=True)
