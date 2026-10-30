#!/usr/bin/env python3
"""Causal finite-horizon source+frequency first-scatter convolution for PHYS16.

Reuses PHYS15 exact source-event code and positivity-preserving endpoint treatment.
All source owners immutable. The photon emission PDF is conditional on the
not-empirically-verified first-Born electron differential angular closure.
"""
from __future__ import annotations
import argparse,csv,io,importlib.util,json,math,sys,tempfile,zipfile
from pathlib import Path
import numpy as np
from scipy.special import exprel
import phys16_spectral as m

ROOT=Path(__file__).resolve().parent

def calculate(source, out):
    out=Path(out);fp=np.load(out/'SOURCE_EMISSION_PROFILES.npz',allow_pickle=False)
    x=fp['x'];prof=fp['profiles'];indexes=fp['source_index'];types=fp['source_type']
    assert len(indexes)==2066 and set(types)=={'He'}
    raw=Path(source).read_bytes()
    if m.sha(raw)!=m.PHYS15_SHA:raise ValueError('PARENT_SOURCE_CHANGED')
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        nested=z.read(m.PHYS15_PREFIX+'sources/PR139_ORIGINAL_SOURCE.zip')
        code=z.read(m.PHYS15_PREFIX+'phys15_lya.py')
        original_rows=list(csv.DictReader(io.StringIO(z.read(m.PHYS15_PREFIX+'results/FINAL_SOURCE_ATOM_LYA_SCATTER.csv').decode())))
    with tempfile.TemporaryDirectory() as t:
        t=Path(t); (t/'phys15_lya.py').write_bytes(code);(t/'PR139.zip').write_bytes(nested)
        sp=importlib.util.spec_from_file_location('ph15_locked_code',t/'phys15_lya.py')
        ph=importlib.util.module_from_spec(sp);sys.modules[sp.name]=ph;sp.loader.exec_module(ph)
        p14,orig,shah,En,BE,prows=ph.load_parent(t/'PR139.zip')
        info=ph.build_info(p14,orig,shah,En,BE)
    pp=next(p for p in info if p['pp']['source']=='He')
    k=pp['k'][indexes];kh=pp['kh'][indexes];ni=pp['ni'][indexes];nx=pp['nx'][indexes]
    assert np.all(nx>0)
    pp_weight=pp['pp']['weights'];edges=orig[1]
    rates=m.hi_first_scatter_rate(x)
    lag_x,lag_w=np.polynomial.laguerre.laggauss(64)
    leg_x,leg_w=np.polynomial.legendre.leggauss(160)
    tnodes=(leg_x+1)/2;tw=leg_w/2
    # Strict index mapping from original source rows; no new atom identities.
    origmap={(rr['birth_policy'],rr['source'],int(rr['source_atom_index'])):rr for rr in original_rows}
    lines=[];summary={};pnames=['KFB_UB2P_E1','KFB_UB2P_ISOTROPIC_EMISSION','PWBA_E1_PARENT']
    ref_q0=float(m.hi_first_scatter_rate(0))
    tail_strict=float(json.loads((out/'RESULT.json').read_text())['rigorous_model_tail_probability_upper_x16'])
    for policy in ('earliest','latest'):
        source_exc=np.array([float(origmap[(policy,'He',int(i))]['measured_domain_H_2p_excitation_m3']) for i in indexes])
        ref_scat=np.array([float(origmap[(policy,'He',int(i))]['Lyalpha_first_resonant_scatter_x0_m3']) for i in indexes])
        # Time-ordered, source-specific unscattered photon population at each x.
        unsc=np.zeros((len(indexes),len(x)),float)
        for j in range(4):
            birth=orig[0].bin_birth(float(edges[j]),float(edges[j+1]),policy)
            dt=max(0,1.e10-birth)
            if dt<=0:continue
            wj=np.asarray(pp_weight[j],float)[indexes]
            for ix,q in enumerate(rates):
                if q*dt>200:
                    age=dt-lag_x/q
                    good=age>=0
                    v=np.zeros((len(lag_x),len(indexes)))
                    if good.any():
                        ages=age[good,None]
                        v[good]=wj[None,:]*kh[None,:]*nx[None,:]*ages*np.exp(-k[None,:]*ages)*exprel((k-ni-nx)[None,:]*ages)
                    unsc[:,ix] += (lag_w@v)/q
                else:
                    ages=(dt*tnodes)[:,None]
                    v=wj[None,:]*kh[None,:]*nx[None,:]*ages*np.exp(-k[None,:]*ages)*exprel((k-ni-nx)[None,:]*ages)
                    unsc[:,ix] += dt* np.dot(tw*np.exp(-q*(dt-dt*tnodes)),v)
        scat=np.maximum(source_exc[:,None]-unsc,0)
        at0=int(np.argmin(abs(x)))
        max_parity=float(np.max(np.abs(scat[:,at0]-ref_scat)/np.maximum(source_exc,1e-95)))
        assert max_parity<1.e-10,('PHYS15_FIRST_SCATTER_X0_PARITY',policy,max_parity)
        for model_idx,model in enumerate(pnames):
            photons=prof[:,model_idx,:]
            scoped_atlas=float(np.trapezoid(np.sum(scat*photons,axis=0),x))
            inj=float(np.trapezoid(np.sum(source_exc[:,None]*photons,axis=0),x))
            tail_bound=sum(source_exc*(1-np.trapezoid(photons,x,axis=1)))
            assert 0<=scoped_atlas<=inj<=sum(source_exc)*(1+1.e-10)
            summary[policy+':'+model]=dict(first_scatter_x16_lower_m3=scoped_atlas,
                 first_scatter_upper_tail_only_m3=scoped_atlas+float(sum(source_exc))*tail_strict,
                 positive_model_tail_probability_rigorous_bound=tail_strict,
                 unobserved_frequency_tail_count_numerical_estimate_m3=float(tail_bound),
                 tail_upper_excludes_core_quadrature_error=True,
                 injection_x16_m3=inj,parent_excitation_m3=float(sum(source_exc)),
                 original_x0_max_per_atom_relative_residual=max_parity,
                 source_time_order='r2p(u)*[1-exp(-q(x)(T-u))] integrated with source-specific model p_emit(x|Ee)',
                 finite_A_upper_difference_m3=float(sum(source_exc)*ref_q0/m.A21))
            for xi,N in zip(x,np.sum(scat*photons,axis=0)):
                lines.append(dict(policy=policy,model=model,x_Doppler=float(xi),
                   source_qualified_first_scatter_spectral_density_per_x_m3=float(N)))
    m.write_csv(out/'TIME_ORDERED_MODEL_FIRST_SCATTER_SPECTRA.csv',lines)
    result=json.loads((out/'RESULT.json').read_text())
    result['time_ordered_first_scatter_integrals']=summary
    result['source_spectrally_integrated_first_scatter']='SCOPED_MODEL_QUADRATURE_EXECUTED_ON_SOURCE_OWNER'
    (out/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2,ensure_ascii=False)+'\n')
    return summary

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',type=Path,default=ROOT/'sources/PR140_PHYS15_SOURCE.zip')
    ap.add_argument('--output',type=Path,default=ROOT/'results')
    args=ap.parse_args()
    print(json.dumps(calculate(args.source,args.output),indent=2,sort_keys=True))
