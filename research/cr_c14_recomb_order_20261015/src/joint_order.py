"""Contrast global source/opacity/recombination convergence in C13 and C14."""
from __future__ import annotations
import argparse,json,time
from pathlib import Path
import numpy as np
from owner_age_bridge import owner_namespace
from physical_age import Gas
from transport import integrate

def run(root, n_list=(16,32,64,128,256), scale=(0.0,0.05,1.0), initial_T=4000.,q=0.):
    ns=owner_namespace(root)
    result=[]
    for source in scale:
        for mode in ('frozen','midpoint'):
            rows=[]
            for n in n_list:
                start=time.perf_counter()
                r=integrate(ns,q,n,source_scale=source,
                            gas0=Gas(.9,.85,.15,0.,initial_T),
                            recombination=True,rr_ne_method=mode)
                x=r['gas_final']
                row={'n':n,'xHI':x['xhi'],'xHeIII':x['xheiii'],
                     'T':x['temp_K'],'wall':time.perf_counter()-start,
                     'max_ledger':max(abs(r['ledgers']['photon_count_residual']),
                         abs(r['ledgers']['total_local_energy_residual_eV_per_H']))}
                rows.append(row)
                print('source',source,'method',mode,'n',n,'xhi',x['xhi'],
                      'temp_K',x['temp_K'],'time',row['wall'],flush=True)
            result.append({'source_scale':source,'ne_method':mode,'rows':rows})
    return {'schema':'C14_SPLITTING_GLOBAL_DIAGNOSTIC_V1',
            'owner':'actual pinned rei_bianchi C8 Scenario', 'scale':list(scale),
            'initial_T':initial_T,'q':q,'cases':result}

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--owner',type=Path,required=True)
    p.add_argument('--max-n',type=int,default=128)
    args=p.parse_args()
    n=[16,32,64,128,256]
    d=run(args.owner,n_list=tuple(x for x in n if x<=args.max_n))
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(d,indent=2)+'\n')
