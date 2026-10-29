#!/usr/bin/env python3
"""Independent scalar mpmath oracle for Verner values and 128 endpoint cases.

Not a distinct-author audit. Avoid sharing production vectorized code path.
"""
import hashlib,json
import mpmath as mp
import numpy as np
from pathlib import Path
from rr_boundfree import read_source,PR125_SOURCE_SHA

mp.mp.dps=65
D=lambda x:mp.mpf(str(x))
P={
 'HI':list(map(D,['13.6','50000','0.4298','54750','32.88','2.963','0','0','0'])),
 'HeI':list(map(D,['24.59','50000','13.61','949.2','1.469','3.188','2.039','0.4434','2.136']))
}


def independent_sigma(E,a):
    eth,emax,e0,s0,ya,p,yw,y0,y1=P[a]
    if E<eth or E>emax:return mp.mpf(0)
    x=E/e0-y0
    yy=mp.sqrt(x*x+y1*y1)
    f=((x-1)*(x-1)+yw*yw)*mp.power(yy,p/2-mp.mpf('5.5'))/mp.power(1+mp.sqrt(yy/ya),p)
    return s0*f*mp.mpf('1e-22')


def run(zip_path,output_json):
    _,arr,density=read_source(zip_path)
    n={k:D(v) for k,v in density.items()}
    edges=[D(v) for v in arr['time_edges_s']]
    T=edges[-1];c=mp.mpf(299792458)
    controls=[]
    for channel in ('H','He'):
        e=arr[f'photon_{channel}_eV']
        w=arr[f'capture_{channel}_bins_m3']
        for j in range(4):
            # 16 predeclared deterministic indexes, including endpoints and mid-range.
            indices=[0,1,17,87,199,511,799,1000,1200,1599,1907,2211,2501,2899,3113,3199]
            for idx in indices:
                E=D(e[idx]);W=D(w[j,idx]); k={a:n[a]*independent_sigma(E,a) for a in ('HI','HeI')}
                kt=k['HI']+k['HeI']
                lo=-mp.expm1(-kt*c*(T-edges[j+1])); hi=-mp.expm1(-kt*c*(T-edges[j]))
                for target in ('HI','HeI'):
                    nlo=W*(k[target]/kt)*lo if kt else mp.mpf(0)
                    nhi=W*(k[target]/kt)*hi if kt else mp.mpf(0)
                    controls.append({'channel':channel,'time_bin':j+1,'atom_index':idx,'target':target,
                          'E_eV':float(E),'sigma_m2':float(independent_sigma(E,target)),
                          'count_lower_m3':float(nlo),'count_upper_m3':float(nhi)})
    result={'precision_dps':mp.mp.dps,'source_zip_sha256':PR125_SOURCE_SHA,'controls':controls,
            'n_controls':len(controls),'implementation_independence':'different scalar mpmath equations & order; same author, not R6/C9'}
    Path(output_json).write_text(json.dumps(result,indent=2)+'\n')
    return result

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--source-zip',required=True);ap.add_argument('--output',required=True)
    args=ap.parse_args()
    r=run(args.source_zip,args.output)
    print(json.dumps({'controls':r['n_controls'],'dps':r['precision_dps']}))
