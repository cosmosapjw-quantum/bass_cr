"""Independent MP80 check using Python loops and piecewise pure mpmath expressions."""
import json
import math
from pathlib import Path
import mpmath as mp
import numpy as np
import window_ionization as m
mp.mp.dps=80

def prob(s,k,t0,t1):
    s=mp.mpf(float(s));k=mp.mpf(float(k));t0=mp.mpf(float(t0));t1=mp.mpf(float(t1))
    if s>t1:return mp.mpf(0)
    if s>=t0:return 1-mp.exp(-k*(t1-s))
    return mp.exp(-k*(t0-s))-mp.exp(-k*(t1-s))

def run():
    arr,den,pa,sig,_=m.load_sources()
    max_rel=mp.mpf(0); max_abs=mp.mpf(0); checks=0
    for src in m.SOURCES:
        E=arr[f'photon_{src}_eV'];h=sig[src]['HI']*den['HI'];he=sig[src]['HeI']*den['HeI'];k=(h+he)*m.C
        for j in range(4):
            l=float(arr['time_edges_s'][j]);r=float(arr['time_edges_s'][j+1])
            for t0,t1 in [(0.,1.25e9),(2.5e9,3.75e9),(5e9,6.25e9),(8.75e9,1e10)]:
                # two original source atom indices per birth bin and epoch
                for i in (0,1997):
                    kl=mp.mpf(float(k[i]));
                    values=(prob(l,kl,t0,t1),prob(r,kl,t0,t1),prob(max(l,min(t0,r)),kl,t0,t1))
                    lo=min(values[0],values[1]);hi=values[2]
                    actual=m.time_window_extrema(np.array([float(k[i])]),l,r,t0,t1)
                    for ref,check in ((lo,float(actual[0][0])),(hi,float(actual[1][0]))):
                        err=abs(ref-mp.mpf(check));max_abs=max(max_abs,err)
                        if ref>mp.mpf('1e-20'):max_rel=max(max_rel,err/ref)
                        assert err<mp.mpf('1e-14'),(src,j,i,t0,err)
                        checks+=1
    res={'dps':mp.mp.dps,'samples':checks,'max_absolute':str(max_abs),'max_relative_nonzero':str(max_rel),'source_parent_sha256':m.SHA129}
    (m.ROOT/'results'/'MP80_CHECK.json').write_text(json.dumps(res,indent=2,sort_keys=True)+'\n')
    print(json.dumps(res,indent=2))
    return res
if __name__=='__main__':run()
