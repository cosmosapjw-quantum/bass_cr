#!/usr/bin/env python3
"""Lightweight evidence: PR150 q adapter; MD14 birth and C20 vs GL8 source bias.

No native Rust run. The C21 bridge reported at NCP commit 807a4602 was not
retrieved from its worktree; this is a conditional independent reference.
"""
from __future__ import annotations
import json
from math import exp,log
from pathlib import Path
import numpy as np
from scipy.integrate import quad
from src.c21_reference import (
    A_REF, BIND, FIT, HEL_Y, H,KB_ERG_K,EV_ERG,
    birth_quadrature, native_spectral_cells, source_rate_per_H,verner_sigma,
    continuum_packet, independent_packet_ivp, fractions, frozen_source_age_step,
)

N_H0 = 1.90e-7 # supplied MANUFACTURED source-normalization fixture, NOT native source checkpoint

def source_integral(x0,x1,observable='N',method='QUAD'):
    target=exp(x1)
    def integrate(x):
        a=exp(x)
        return source_rate_per_H(a,N_H0)/H(a)*(a/target if observable=='U' else 1.0)
    if method=='QUAD':
        return quad(integrate,x0,x1,epsabs=1e-21,epsrel=3e-13)[0]
    terms=birth_quadrature(x0,x1,N_H0,method)
    return sum(w*(a/target if observable=='U' else 1.0) for a,w in terms)


def source_shape_study(n):
    kt=50000*KB_ERG_K/EV_ERG
    z,w=np.polynomial.legendre.leggauss(8)
    c=native_spectral_cells(n)
    sigma0=np.zeros(3);sigma1=np.zeros(3);h0=np.zeros(3);h1=np.zeros(3)
    for cell in c:
        aa,bb=cell['lo'],cell['hi'];E=(aa+bb)/2+(bb-aa)*z/2
        shape=E*E/np.expm1(E/kt)
        wt=w*shape;wt=wt/sum(wt)
        center=cell['centroid_C20']
        for i in range(3):
            s0=verner_sigma(center,i)
            s1=np.array([verner_sigma(v,i) for v in E])
            sigma0[i]+=cell['frac']*s0
            sigma1[i]+=cell['frac']*np.dot(wt,s1)
            h0[i]+=cell['frac']*s0*(center-BIND[i])
            h1[i]+=cell['frac']*np.dot(wt,s1*(E-BIND[i]))
    return {'native_subdivisions':n,'cells':len(c),'mass':sum(p['frac'] for p in c),
            'sigma_centroid_cm2':sigma0.tolist(),
            'sigma_shape_GL8_cm2':sigma1.tolist(),
            'sigma_rel_centroid_minus_GL8':(sigma0/sigma1-1).tolist(),
            'heat_coeff_rel_centroid_minus_GL8':(h0/h1-1).tolist(),
            'max_source_centroid_difference_eV':max(abs(x['centroid_C20']-x['centroid_PR150']) for x in c)}


def packet_checks():
    a0=A_REF;nH0=N_H0/50.; gas=(.3,.2,.1)
    out=[]
    for emission,scale in [(60.,1.20),(25.,1.06),(14.,1.07)]:
        q=a0*emission;n=2e-6;a1=a0*scale
        p=continuum_packet(q,a0,a1,n,nH0,fractions(gas))
        v=independent_packet_ivp(q,a0,a1,n,nH0,fractions(gas))
        out.append({'emission_eV':emission,'a_ratio':scale,'threshold_crossings':p['crossings'],
            'n_end':p['n_end'],'event_per_H':p['event_per_H'].tolist(),
            'heat_eV_H':p['heat_ev_H'].tolist(), 'W_redshift_eV_H':p['work_ev_H'],
            'energy_residual_eV_H':p['energy_defect'],
            'abs_error_vs_independent_Radau':{
                'n_end':abs(p['n_end']-v[0]),
                'species_event':max(abs(p['event_per_H']-v[1:4])),
                'species_heat':max(abs(p['heat_ev_H']-v[4:7])),
                'redshift_work':abs(p['work_ev_H']-v[7])}})
    return out


def main():
    x0=log(A_REF)
    birth=[]
    for dx in (.02,.12,.20):
        row={'log_scale_interval':dx}
        for m in ('N','U'):
            ref=source_integral(x0,x0+dx,m,'QUAD')
            row[m]={'reference_quad':ref,'mid':source_integral(x0,x0+dx,m,'MID'),
                    'GL2':source_integral(x0,x0+dx,m,'GL2')}
            row[m]['relative_mid_error']=row[m]['mid']/ref-1
            row[m]['relative_GL2_error']=row[m]['GL2']/ref-1
        birth.append(row)
    source=[source_shape_study(n) for n in (4,8,16,32,64)]
    E=np.array([50.,55.,60.]);wa=np.array([.5,0,.5]);wb=np.array([.2,.6,.2]);s=np.array([verner_sigma(x,2) for x in E])
    counter={'energy_eV':E.tolist(),'weights_A':wa.tolist(),'weights_B':wb.tolist(),
        'common_number':sum(wa),'common_mean_energy_eV':float(wa@E),
        'common_support_eV':[50.,60.],
        'HeII_sigma_A_cm2':float(wa@s),'HeII_sigma_B_cm2':float(wb@s)}
    xfull=log(A_REF);xend=xfull+.02
    coupled_toy={mode:{k:(v.tolist() if isinstance(v,np.ndarray) else v)
                     for k,v in frozen_source_age_step(xfull,xend,N_H0,(.3,.2,.1),mode,1).items()}
                 for mode in ('MID','GL2')}
    result={'schema':'C21_COMMON_Q_SOURCE_AGE_SANDBOX_V1','synthetic_source_age_attenuation':coupled_toy,
            'reference_a':A_REF,'owner_C20':'caf587b3edf4e27d038c6a918419be498d7d389c',
            'owner_PR150':'4e2f0682fb605c6aa940bd756d9869e67b6ded0b',
            'unverified_NCP_C21_bridge_user_report':'807a46029cd2ebca16ab58cc3d92669277be3c00',
            'new_execution_scope':'Sandbox Python only, frozen neutral, conditional toy sigma E^-3',
            'native_hydrogen_density':'MANUFACTURED 1.90e-7 cm^-3 comoving; not a native checkpoint',
            'birth_rate_quadrature':birth,'source_cell_shape_comparison':source,
            'constant_sigma_powerlaw_threshold_packet':packet_checks(),
            'matched_moments_HeII_response_counterexample':counter,
            'native_c21_rust_execution':'NOT_RUN',
            'full_EOR_claim':'HOLD'}
    root=Path(__file__).parent
    out=root/'evidence'/'RESULT.json';out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print('SOURCE_BIRTH_QUADRATURE')
    for x in birth:print(x['log_scale_interval'],'N',x['N']['relative_mid_error'],x['N']['relative_GL2_error'],'U',x['U']['relative_mid_error'],x['U']['relative_GL2_error'])
    print('SOURCE_SHAPE_BIAS_16',source[2]['sigma_rel_centroid_minus_GL8'],source[2]['heat_coeff_rel_centroid_minus_GL8'])
    print('ANALYTIC_PACKET_VS_RADAU')
    for x in result['constant_sigma_powerlaw_threshold_packet']:print(x['emission_eV'],x['abs_error_vs_independent_Radau'],x['energy_residual_eV_H'])
    print('SOURCE_AGE_TOY_GL2',coupled_toy['GL2'])
    print('SAME_MOMENT_DIFFERENT_HEII',counter['HeII_sigma_A_cm2'],counter['HeII_sigma_B_cm2'])
    return result

if __name__=='__main__':main()
