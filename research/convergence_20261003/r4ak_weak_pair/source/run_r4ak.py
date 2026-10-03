"""One bounded exact-tail and synthetic weak-pair execution; no scattering."""
from __future__ import annotations
import argparse, hashlib, json, os, platform, resource, sys, time
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import expm
from weak_pair import (P,I,CQ,matrix,dagger,mmul,mderiv,msub,mscale,exact_pair_certificate,
                       propagate_certificates,ContractError)
from radial_pair import uniform_pair_bound

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x): Path(p).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def evaluate(A,t):
    return np.array([[complex(float(x.value(float(t)).re),float(x.value(float(t)).im)) for x in r] for r in A])
def model(a=F(1,100),k=F(1,4),eps=F(1,1000)):
    M=matrix([[1,0,0],[0,1,0],[P([0,a]),0,1]])
    h=matrix([[0,k,0],[k,0,eps],[0,eps,2]])
    S=mmul(dagger(M),M)
    K=msub(mmul(mmul(dagger(M),h),M),mscale(mmul(dagger(M),mderiv(M)),I))
    return M,h,S,K

def synthetic():
    M,h,S,K=model(); intervals=[(F(i,4),F(i+1,4)) for i in range(4)]
    certs=[exact_pair_certificate(S,K,z) for z in intervals]
    bound=propagate_certificates(certs)
    def rhs(t,d):
        s=evaluate(S,t);kk=evaluate(K,t)
        return -1j*np.linalg.solve(s[:2,:2],kk[:2,:2]@d)
    sol=solve_ivp(rhs,(0,1),np.array([1+0j,0+0j]),method='DOP853',rtol=2e-12,atol=2e-14,dense_output=True)
    if not sol.success: raise RuntimeError(sol.message)
    hh=evaluate(h,0); errors=[]; norms=[]; diffs=[]; pops=[]
    for t in np.linspace(0,1,65):
        mm=evaluate(M,t);ss=evaluate(S,t)
        c=np.linalg.solve(mm,expm(-1j*hh*t)@np.array([1,0,0],complex))
        d=sol.sol(t);approx=np.r_[d,0j];error=c-approx
        errors.append(float(np.sqrt(max(0,(error.conj()@ss@error).real))))
        norms.append(float((approx.conj()@ss@approx).real))
        Jp=np.array([0,1,0],complex);target=mm@Jp;target/=np.linalg.norm(target)
        exact=abs(np.vdot(target,mm@c))**2; reduced=abs(np.vdot(target,mm@approx))**2
        pops.append([float(t),float(exact),float(reduced)])
        diffs.append(float(abs(exact-reduced)))
    emax=max(errors);pmax=max(diffs);bu=float(F(bound['state_error_upper']));pu=float(F(bound['same_observable_error_upper']))
    if not emax<=bu or not pmax<=pu: raise AssertionError('synthetic diagnostic outside analytic envelope')
    if max(abs(x-1) for x in norms)>1e-9: raise AssertionError('synthetic reduced norm drift exceeds contract')
    return {'scope':'SYNTHETIC_EXACT_POLYNOMIAL_MODEL_NOT_ATOMIC_TRAJECTORY',
            'parameters':{'a':'1/100','k':'1/4','eps':'1/1000','t_interval_ta':['0','1'],'hbar_Eh_ta':'1'},
            'model':{'M':[[p.json() for p in row] for row in M],
                     'h':[[p.json() for p in row] for row in h],
                     'S':[[p.json() for p in row] for row in S],
                     'K':[[p.json() for p in row] for row in K]},
            'certificates':certs,'analytic_bound':bound,
            'numeric_diagnostic':{'solver':'DOP853','rtol':2e-12,'atol':2e-14,'nfev':sol.nfev,
                    'max_state_error':emax,'max_population_difference':pmax,
                    'max_reduced_norm_drift':max(abs(x-1) for x in norms),
                    'population_trace':pops,'floating_ODE_is_enclosure':False}}

def main():
    p=argparse.ArgumentParser();p.add_argument('--contract',required=True);args=p.parse_args()
    cp=Path(args.contract).resolve();c=json.loads(cp.read_text());root=Path(c['release_root']).resolve()
    if c['schema']!='R4AK_LIGHT_EXECUTION_CONTRACT_V1' or c['attempt_cap']!=1 or c['cross_cap']!=0:
        raise ContractError('wrong bounded execution contract')
    for rel,h in c['pins'].items():
        path=(root/rel).resolve()
        if not path.is_relative_to(root) or sha(path)!=h: raise ContractError('source/input pin mismatch: '+rel)
    out=Path(c['output_directory']).resolve()
    if not out.is_relative_to(root/'evidence') or out.exists(): raise ContractError('output outside contract or already consumed')
    out.mkdir();write(out/'RESERVATION.json',{'contract_sha256':sha(cp),'attempt':1,'scope':c['scope']})
    resource.setrlimit(resource.RLIMIT_AS,(c['max_address_space_bytes'],c['max_address_space_bytes']))
    start=time.perf_counter()
    try:
        pair=uniform_pair_bound(root/'inputs/BASS_CR_R4AG_CANDIDATE.npz',root/'inputs/BASS_CR_R4AG_CANDIDATE.json',
             root/'inputs/BASS_CR_R4AB_GRAM_EXACT.json',speed=F(c['speed_a0_per_ta']),min_abs_z=12,split_radius=6,impact_b=2)
        write(out/'PAIR_UNIFORM_BOUND.json',pair)
        syn=synthetic();write(out/'SYNTHETIC_WEAK_PAIR.json',syn)
        if time.perf_counter()-start>c['wall_seconds']:raise RuntimeError('wall contract exceeded')
        result={'schema':'R4AK_BOUND_EXECUTION_RESULT_V1','status':'UNIFORM_CANDIDATE_PAIR_AND_REFERENCE_ENVELOPES_COMPLETE',
          'contract_sha256':sha(cp),'pair_result_sha256':sha(out/'PAIR_UNIFORM_BOUND.json'),
          'synthetic_result_sha256':sha(out/'SYNTHETIC_WEAK_PAIR.json'),
          'wall_seconds':time.perf_counter()-start,'maxRSS_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
          'counts':{'new_exact_radial_tail':1,'synthetic_ODE':1,'new_cross':0,'new_M9':0,'old_suite':0,'m64_prepare':0},
          'physical_bridge_upper':None,'full18_metric_lower':None,
          'missing_actual_inputs':['continuous full18 S,K,Sdot enclosures','same-endpoint initial state bound',
             'selector/embedding discrepancy','actual bridge interval error budget'],
          'global_ceiling':{'G02':'UNRESOLVED','production':'HOLD','capture':False,'all_bound':'OPEN','b_grid':'NO_GO'}}
        write(out/'RESULT.json',result);write(out/'COMPLETED.json',{'result_sha256':sha(out/'RESULT.json')})
        print(json.dumps(result,indent=2))
    except Exception as exc:
        write(out/'FAILURE.json',{'type':type(exc).__name__,'message':str(exc),'no_automatic_retry':True});raise
if __name__=='__main__':main()
