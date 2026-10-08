"""New optical augmented IVP and mpmath Fubini quadrature; diagnostic only."""
import argparse, importlib.util, json, os, sys
from pathlib import Path
import mpmath as mp
import numpy as np
from scipy.integrate import solve_ivp

def calc(stage,result,out):
    sys.dont_write_bytecode=True;mp.mp.dps=80
    rei=stage/'extracted/REI_XTHREAD_BRIDGE13_20261008/rei_bridge13_20261008'
    sys.path[:0]=[str(rei/'research'),str(rei/'source')]
    import independent_chain as ref
    ref.mp.mp.dps=80
    ch=ref.chain
    records=json.loads((result/'CELL_RESULTS.json').read_text())
    summary=json.loads((result/'RESULTS.json').read_text())
    def rational(d):return mp.mpf(d['num'])/mp.mpf(d['den'])
    def pair(v):return [rational(x) for x in v]
    fhe=mp.mpf(float(.083));CT=mp.mpf(299792458)*mp.mpf(float(6.6524587e-29))*10**6
    nh0=mp.mpf(float(1e-4));H=mp.mpf(float(1e-14))
    def xe(g):return g[0]+fhe*(g[1]+2*g[2])
    native_total=mp.mpf(0);quadrature_checks=[]
    for i,cell in enumerate(records):
        root=ch.ENTRIES['root'][i];point=ch.ENTRIES['point'][i]
        t0=mp.mpf(float(root['t0']));L=mp.mpf(float(root['t1']))-t0
        x0=xe([mp.mpf(float(v)) for v in point['old'][:3]])
        x1=xe([mp.mpf(float(v)) for v in point['gas'][:3]])
        nt=CT*nh0*L*mp.quad(lambda s:mp.exp(-3*H*(t0+L*s))*((1-s)*x0+s*x1),[0,1])
        lo,hi=pair(cell['native']);assert lo<=nt<=hi,('NATIVE_QUADRATURE',i)
        native_total+=nt
        if i:
            alpha=rational(cell['alpha']);scale=rational(cell['scale']);dens=sum(pair(cell['density_factor']))/2
            flo=fhi=mp.mpf(0)
            for p in cell['residual_panels']:
                a,b=map(mp.mpf,p['s'])
                # Separate nested integral, not polynomial kernel implementation.
                J=mp.quad(lambda u:mp.quad(lambda s:mp.exp(-alpha*s),[u,1]),[a,b])
                lo=[mp.mpf(x[0]) for x in p['residual'][:3]]
                hi=[mp.mpf(x[1]) for x in p['residual'][:3]]
                flo-=xe(hi)*J;fhi-=xe(lo)*J
            flo*=scale*dens;fhi*=scale*dens
            lo,hi=pair(cell['forcing']);assert lo<=flo<=fhi<=hi,('FORCING_QUADRATURE',i)
            inc=cell['incoming_error_scaled'][:3]
            il=xe([mp.mpf(v[0]) for v in inc]);ih=xe([mp.mpf(v[1]) for v in inc])
            W=mp.quad(lambda s:mp.exp(-alpha*s),[0,1])
            lo,hi=pair(cell['initial']);assert lo<=scale*dens*il*W<=scale*dens*ih*W<=hi,('INITIAL_QUADRATURE',i)
            quadrature_checks.append({'cell':i,'forcing_80dps':[str(flo),str(fhi)],'incoming_80dps':[str(scale*dens*il*W),str(scale*dens*ih*W)],'contained':True})
    lo,hi=pair(summary['tau_native_piecewise_defined']);assert lo<=native_total<=hi
    # One newly augmented optical trajectory; existing donor endpoint suites are not rerun.
    pt=ch.ENTRIES['point'][0]
    z=np.array([float(v)/float(sc) for v,sc in zip(pt['old']+pt['p0'],ref.SCALE+[ref.P0])]+[0.])
    ivp=[];ct=float(CT);f=float(fhe)
    for i in range(32):
        root=ch.ENTRIES['root'][i];pt=ch.ENTRIES['point'][i];n=len(pt['p0'])
        if len(z)-1<4+n:z=np.concatenate([z[:-1],[pt['p0'][-1]/.05],z[-1:]])
        t0,t1=root['t0'],root['t1'];L=t1-t0
        g0=np.array(pt['old'][:3]);g1=np.array(pt['gas'][:3])
        def fun(s,v):
            t=t0+L*s
            rhs=ref.f_target(t,v[:-1],ref.chain.BIRTH)*L
            err=v[:3]-((1-s)*g0+s*g1)
            goal=ct*float(nh0)*np.exp(-3*float(H)*t)*L*(err[0]+f*(err[1]+2*err[2]))
            return np.concatenate([rhs,[goal]])
        sol=solve_ivp(fun,(0,1),z,method='DOP853',rtol=2.5e-13,atol=[5e-16]*(len(z)-1)+[1e-28],max_step=1/4)
        assert sol.success and sol.t[-1]==1
        z=sol.y[:,-1]
        lo,hi=pair(records[i]['cumulative_difference']);inside=float(lo)<=z[-1]<=float(hi)
        assert inside,('AUGMENTED_OPTICAL',i,z[-1],str(lo),str(hi))
        ivp.append({'cell':i,'delta_tau_prefix':float(z[-1]),'nfev':sol.nfev,'posthoc_inside':inside})
    ans={'status':'PASS_DIAGNOSTIC_NOT_PROOF','native_tau_80dps':str(native_total),
         'mpmath_dps':80,'independent_Fubini_checks':quadrature_checks,
         'DOP853_augmented_optical_delta_tau':float(z[-1]),'new_optical_IVP_segments':32,
         'prefix_checks':ivp,'shares_archived_nonphoto_coefficient_source':True,
         'certificate_premise':False,'not_physical_fit_validation':True}
    out.write_text(json.dumps(ans,indent=2)+'\n');print(json.dumps({k:ans[k] for k in ('status','native_tau_80dps','DOP853_augmented_optical_delta_tau','new_optical_IVP_segments')}))

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--stage',type=Path,required=True);a.add_argument('--result',type=Path,required=True);a.add_argument('--output',type=Path,required=True)
    x=a.parse_args();calc(x.stage,x.result,x.output)
