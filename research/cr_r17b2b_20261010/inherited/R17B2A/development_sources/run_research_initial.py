from pathlib import Path
import argparse,sys,json,time,hashlib,platform
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
import numpy as np
from birth_response import Background
from ft03_point import temperature,TAU_SCALE,TEND

def run(out):
    out.mkdir(parents=True,exist_ok=False)
    t0=time.time();plan=json.loads((ROOT/'inputs/BIRTH_PLAN.json').read_text())
    bg=Background(plan);initial_adj=bg.backward()
    bs=[0.,.1,.35401279938188477,.5,.8,1.]
    bs+=list(bg.births[1:])
    pairs=[]
    for b in sorted(set(bs)):
        f=bg.probe(b); a=bg.probe_adjoint(b)
        if b<1:c=bg.probe(b,memory=False)
        else:c=f
        gap=abs(f['K_tau']-a['K_tau'])/max(abs(f['K_tau']),1e-40)
        pairs.append({'forward':f,'adjoint':a,'local_opacity_only':c,'dual_relative_gap':gap,'memory_relative_correction':(f['K_tau']-c['K_tau'])/f['K_tau'] if f['K_tau'] else 0})
        print('PROBE',b,f['K_tau'],f['delta_temperature_K'],gap,flush=True)
    dose=[bg.positive_dose(.35401279938188477,d) for d in (1e-3,5e-4,2.5e-4)]
    result={'task':'R17B2A_NOMINAL_COUPLED_RESPONSE','status':'NUMERICAL_DIAGNOSTIC_NOT_HOMOTOPY_CERTIFICATE','initial_adj_scaled':initial_adj.tolist(),'base_final':bg.final.tolist(),'base_temperature_final_K':float(temperature(bg.final[:4])),'base_tau_diagnostic':float(TAU_SCALE*bg.final[-1]),'probe_cases':pairs,'positive_dose_checks':dose,'base_nfev':bg.nfev,'adjoint_nfev':bg.adj_nfev,'elapsed_s':time.time()-t0,'fresh_base_histories':1,'certified_source_interval':None}
    (out/'RESPONSE.json').write_text(json.dumps(result,indent=2)+'\n')
    # deterministic numerical arrays for independent source comparison and reproducibility
    nodes=np.linspace(0,1,65);states=[bg.evaluate(float(u)).tolist() for u in nodes]
    (out/'BASE_SAMPLES.json').write_text(json.dumps({'u':nodes.tolist(),'state':states},indent=2)+'\n')
    print('DONE',result['elapsed_s'],flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args();run(Path(a.output))
