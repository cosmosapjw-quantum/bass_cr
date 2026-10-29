#!/usr/bin/env python3
"""Source-bound photoabsorption *endpoint envelopes*, not coupled photon transport.

H/He ground RR atomwise photon products from immutable bass_cr PR125;
Verner+1996 photoionization cross sections from the author-hosted Table 1.
No event times are imputed within the source's four time bins.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import zipfile
import numpy as np

PR125_SOURCE_SHA = '8e9b58236819146f4929aa4647dafdb1dc21b97b2f129ec4035291bb73a1ed2e'
PR110_NESTED_SHA = '5392bc1bf159d0b23d7530a541f894e201231c3df874d6c547474b7517654c58'
PR125_NPZ_SHA = 'e171824cf5fc3ba232fbbd4def6fc8cf6c855ca9e7d05506e4e4426c9416688f'
PR125_RESULT_SHA = '4a8cafd27bb78086842fc213fec6cc1f61dae0e62d3939c23be6df00fe32a538'
TABLE = Path(__file__).with_name('source')/'VERNER1996_HI_HEI_TABLE1.dat'
ARCHIVE_PREFIX='research/cr_phys02_rr_ionizing_photons_20261029/'
C_M_S=299792458.0
EV_J=1.602176634e-19
HI='HI'
HEI='HeI'


def sha256(b:bytes)->str:
    return hashlib.sha256(b).hexdigest()


def load_verner(table=TABLE):
    """Strict source data: two rows, H I (Z=1,N=1), He I (Z=2,N=2)."""
    parsed={}
    raw=Path(table).read_bytes()
    for ln in raw.decode('ascii').splitlines():
        if not ln.strip() or ln.lstrip().startswith('#'):
            continue
        cols=ln.split()
        if len(cols)!=11:
            raise ValueError('VERNER_TABLE_COLUMNS')
        z,n=map(int,cols[:2])
        f=tuple(map(float,cols[2:]))
        if (z,n) not in ((1,1),(2,2)) or (z,n) in parsed:
            raise ValueError('VERNER_TABLE_SPECIES_DUPLICATE_OR_WRONG')
        if not (f[0]>0 and f[1]>f[0] and f[2]>0 and f[3]>0 and f[4]>0 and f[5]>0):
            raise ValueError('VERNER_TABLE_PARAMS_INVALID')
        parsed[(z,n)]=f
    if set(parsed)!={(1,1),(2,2)}:
        raise ValueError('VERNER_TABLE_MISSING')
    # Prevent a silent threshold/parameter change from changing the physical source.
    if parsed[(1,1)]!=(13.6,50000.,.4298,54750.,32.88,2.963,0.,0.,0.):
        raise ValueError('VERNER_HI_NOT_SOURCE_LOCKED')
    if parsed[(2,2)]!=(24.59,50000.,13.61,949.2,1.469,3.188,2.039,.4434,2.136):
        raise ValueError('VERNER_HEI_NOT_SOURCE_LOCKED')
    return {HI:parsed[(1,1)],HEI:parsed[(2,2)]}, sha256(raw)


def verner_sigma(energy_eV, params):
    """Total ground-state cross-section in m2. Eq.(1): (x-1)^2, not (y-1)^2."""
    E=np.asarray(energy_eV,dtype=np.float64)
    if np.any(~np.isfinite(E)) or np.any(E<0):
        raise ValueError('PHOTON_ENERGY_INVALID')
    eth,emax,e0,sigma0,ya,P,yw,y0,y1=params
    x=E/e0-y0
    y=np.sqrt(x*x+y1*y1)
    if np.any((y==0)&(E>=eth)&(E<=emax)):
        raise ValueError('VERNER_FIT_SINGULAR')
    with np.errstate(divide='ignore',over='raise',invalid='ignore'):
        y_safe=np.where(y>0,y,1.)
        val=(sigma0*1e-22)*((x-1.)**2+yw*yw)*np.power(y_safe,0.5*P-5.5)*np.power(1+np.sqrt(y_safe/ya),-P)
    out=np.where((E>=eth)&(E<=emax),val,0.0)
    if np.any(~np.isfinite(out)) or np.any(out<0):
        raise ValueError('VERNER_SIGMA_INVALID')
    return out


def read_source(source_zip):
    b=Path(source_zip).read_bytes()
    if sha256(b)!=PR125_SOURCE_SHA:
        raise ValueError('PR125_SOURCE_ZIP_SHA256_MISMATCH')
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        if z.testzip() is not None:
            raise ValueError('PR125_SOURCE_ZIP_CRC_FAIL')
        raw=z.read(ARCHIVE_PREFIX+'results/PHOTON_ATOMWISE.npz')
        result_bytes=z.read(ARCHIVE_PREFIX+'results/PHOTON_RESULT.json')
        prior=z.read(ARCHIVE_PREFIX+'BASS_CR_LOW_BIRTH_SOURCE_20261027_2eed7ef835c5.zip')
    if sha256(raw)!=PR125_NPZ_SHA or sha256(result_bytes)!=PR125_RESULT_SHA or sha256(prior)!=PR110_NESTED_SHA:
        raise ValueError('PR125_NESTED_INPUT_BYTE_IDENTITY_MISMATCH')
    result=json.loads(result_bytes)
    if result['scope']['photon_transport'] or result['scope']['conditional_frozen_100K_model'] is not True:
        raise ValueError('INCOMPATIBLE_SOURCE_PHYSICS_SCOPE')
    if result['authority']['source_PR'] != 110 or result['scope']['birth_tag'] != 'direct_0p1_10':
        raise ValueError('INCOMPATIBLE_SOURCE_IDENTITY')
    # Recover source-neutral inventories from PR110 rather than inventing an abundance.
    with zipfile.ZipFile(io.BytesIO(prior)) as z:
        source_result=json.loads(z.read('research/cr_low_birth_causal_rr_20261027/runs/primary_v1/RESULT.json'))
    n=source_result['inventory']['values']
    if source_result['inventory']['source_state_id']!='PHYS02_T100K_nH140m3_YHe0.248_xHII0.01_xHeII0.01_xHeIII0_FIXED':
        raise ValueError('INVENTORY_SOURCE_STATE_MISMATCH')
    density={HI:n['n_H_m3']-n['n_HII_m3'],HEI:n['n_He_m3']-n['n_HeII_m3']-n['n_HeIII_m3']}
    if any(v<=0 for v in density.values()):
        raise ValueError('NEGATIVE_NEUTRAL_DENSITY')
    with np.load(io.BytesIO(raw), allow_pickle=False) as f:
        arrays={k:f[k].copy() for k in f.files}
    edges=arrays['time_edges_s']
    if not np.array_equal(edges,[0.,2.5e9,5.e9,7.5e9,1.e10]):
        raise ValueError('PROPER_TIME_GRID_MISMATCH')
    for ch,thr in [('H',13.60),('He',24.59)]:
        E=arrays[f'photon_{ch}_eV'];w=arrays[f'capture_{ch}_bins_m3']
        if E.shape!=(3200,) or w.shape!=(4,3200):
            raise ValueError('SOURCE_ATOM_SHAPE_MISMATCH')
        if not np.all(np.isfinite(E)) or not np.all(np.isfinite(w)) or np.any(w<0):
            raise ValueError('SOURCE_ARRAY_INVALID')
        if not (E.min()>=thr and E.max()<=thr+10. and E.min()>thr):
            raise ValueError('SOURCE_PHOTON_ENERGY_SCOPE_INVALID')
        old_total=result['totals'][f'N_{ch}_m3']
        if abs(math.fsum(w.flat)-old_total)>2e-12*old_total:
            raise ValueError('SOURCE_COUNTS_MISMATCH')
    return result,arrays,density


def evaluate(arrays,density,params):
    """Exact measure-order enclosures for ANY emission times within source time bins."""
    times=arrays['time_edges_s']
    T=float(times[-1])
    rows=[]
    opaque=[]
    output_npz={}
    summed={ch:{a:{'lo':0.0,'hi':0.0} for a in (HI,HEI)} for ch in ('H','He')}
    total_emi=0.0
    for ch in ('H','He'):
        E=arrays[f'photon_{ch}_eV']
        weights=arrays[f'capture_{ch}_bins_m3']
        if E.shape!=(3200,) or weights.shape!=(4,3200) or np.any(~np.isfinite(E)) or np.any(~np.isfinite(weights)) or np.any(weights<0):
            raise ValueError('SOURCE_ARRAY_INVALID')
        alph={a:density[a]*verner_sigma(E,params[a]) for a in (HI,HEI)}
        alpha=alph[HI]+alph[HEI]
        if not np.all(alpha>0):
            raise AssertionError('NO_OPACITY_UNEXPECTED_FOR_SOURCE')
        branch={a:alph[a]/alpha for a in (HI,HEI)}
        if not np.allclose(branch[HI]+branch[HEI],1.,rtol=0,atol=1e-15):
            raise AssertionError('BRANCH_PARTITION_INVALID')
        output_npz[f'alpha_{ch}_total_m_inv']=alpha
        for a in (HI,HEI):
            output_npz[f'alpha_{ch}_{a}_m_inv']=alph[a]
        for j in range(4):
            w=weights[j]
            total_emi+=math.fsum(w)
            optical_depth_lo=alpha*C_M_S*(T-times[j+1])
            optical_depth_hi=alpha*C_M_S*(T-times[j])
            absorbed_frac_lo=-np.expm1(-optical_depth_lo)
            absorbed_frac_hi=-np.expm1(-optical_depth_hi)
            if np.any(absorbed_frac_lo>absorbed_frac_hi+1e-15):
                raise AssertionError('MONOTONE_BOUNDS_INVALID')
            lo_tot=math.fsum(w*absorbed_frac_lo)
            hi_tot=math.fsum(w*absorbed_frac_hi)
            for a in (HI,HEI):
                p_lo=branch[a]*absorbed_frac_lo
                p_hi=branch[a]*absorbed_frac_hi
                output_npz[f'abs_{ch}_{a}_bin{j+1}_lo_m3']=w*p_lo
                output_npz[f'abs_{ch}_{a}_bin{j+1}_hi_m3']=w*p_hi
                nlo=math.fsum(w*p_lo)
                nhi=math.fsum(w*p_hi)
                ulo=math.fsum(w*p_lo*E)*EV_J
                uhi=math.fsum(w*p_hi*E)*EV_J
                qionlo=nlo*params[a][0]*EV_J
                qionhi=nhi*params[a][0]*EV_J
                qelo=math.fsum(w*p_lo*(E-params[a][0]))*EV_J
                qehi=math.fsum(w*p_hi*(E-params[a][0]))*EV_J
                tol=max(1e-90,3e-12*max(ulo,uhi))
                if abs(ulo-(qionlo+qelo))>tol or abs(uhi-(qionhi+qehi))>tol:
                    raise AssertionError('PHOTOIONIZATION_ENERGY_OWNERSHIP_FAIL')
                if not (0<=nlo<=nhi<=math.fsum(w)*(1+1e-14)):
                    raise AssertionError('NEGATIVE_OR_INVALID_BOUND')
                summed[ch][a]['lo']+=nlo
                summed[ch][a]['hi']+=nhi
                rows.append(dict(source_channel=ch,time_bin=j+1,target=a,
                  t0_s=float(times[j]),t1_s=float(times[j+1]),
                  photons_emitted_m3=math.fsum(w),absorbed_lower_m3=nlo,absorbed_upper_m3=nhi,
                  first_absorbed_photon_energy_lower_J_m3=ulo,first_absorbed_photon_energy_upper_J_m3=uhi,
                  ionization_threshold_energy_lower_J_m3=qionlo,ionization_threshold_energy_upper_J_m3=qionhi,
                  photoelectron_excess_avail_lower_J_m3=qelo,photoelectron_excess_avail_upper_J_m3=qehi))
            if abs((math.fsum(w)-lo_tot)-math.fsum(w*np.exp(-optical_depth_lo)))>2e-12*math.fsum(w):
                raise AssertionError('SURVIVAL_LOWER_OBSERVABLE_MISMATCH')
            if abs((math.fsum(w)-hi_tot)-math.fsum(w*np.exp(-optical_depth_hi)))>2e-12*math.fsum(w):
                raise AssertionError('SURVIVAL_UPPER_OBSERVABLE_MISMATCH')
        for ix in np.linspace(0,len(E)-1,9,dtype=int):
            opaque.append(dict(channel=ch,index=int(ix),E_eV=float(E[ix]),
              sigma_HI_m2=float(alph[HI][ix]/density[HI]),sigma_HeI_m2=float(alph[HEI][ix]/density[HEI]),
              alpha_HI_m_inv=float(alph[HI][ix]),alpha_HeI_m_inv=float(alph[HEI][ix]),
              alpha_total_m_inv=float(alpha[ix]),mean_free_path_m=float(1/alpha[ix]),
              target_HI_fraction=float(branch[HI][ix]),target_HeI_fraction=float(branch[HEI][ix])))
    for ch in ('H','He'):
        for a in (HI,HEI):
            if a==HEI and ch=='H':
                if summed[ch][a]['hi']!=0:
                    raise AssertionError('H_BELOW_HEI_THRESHOLD_BUT_HEI_ABSORBS')
    totals={bound:math.fsum(summed[ch][a][bound] for ch in ('H','He') for a in (HI,HEI)) for bound in ('lo','hi')}
    if not (0<=totals['lo']<=totals['hi']<=total_emi):
        raise AssertionError('TOTAL_BOUND_INVALID')
    meta=dict(schema='CR_PHYS02_RR_BOUNDFREE_ENVELOPE_V1',source_pr=125,
       source_sha256=PR125_SOURCE_SHA,photon_atomwise_sha256=PR125_NPZ_SHA,
       source_photons_m3=total_emi,absorbed_lower_m3=totals['lo'],absorbed_upper_m3=totals['hi'],
       absorption_fraction_lower=totals['lo']/total_emi,absorption_fraction_upper=totals['hi']/total_emi,
       surviving_lower_m3=total_emi-totals['hi'],surviving_upper_m3=total_emi-totals['lo'],
       densities_m3=density,channels=summed,time_grid_s=times.tolist(),
       assumptions=['prescribed_100K_gas_rest_frame','constant_neutral_HI_HeI_densities',
       'stationary_homogeneous_medium','straight_line_at_c','no_cosmic_redshift',
       'first_photoionization_only','no_scattering','no_cascade','no_emission_time_distribution_within_bins'],
       valid_uses=['local_ground_state_opacity','finite_horizon_conditional_first_absorption_envelope'],
       held=['true_absorption_history','photoelectron_thermal_deposition','transport','full_chemistry','exclusive_He_kernel','physical_K','native25','L4','production'],
       central_dag='28/88',extension_dag='0/3',scoped_auxiliary='1/1_REVIEW_HOLD',
       author_R6='NOT_RUN_DISTINCT_AUTHOR',author_C9='NOT_RUN_DISTINCT_AUTHOR')
    return meta,rows,opaque,output_npz


def save(outdir:Path,meta,rows,sample,atoms,table_sha):
    outdir.mkdir(parents=True,exist_ok=True)
    meta['verner_table_two_rows_sha256']=table_sha
    (outdir/'BOUND_FREE_RESULT.json').write_text(json.dumps(meta,indent=2,sort_keys=True)+'\n')
    for filename,records in [('BOUND_FREE_TIME_CHANNEL_TARGET.csv',rows),('BOUND_FREE_OPACITY_SAMPLES.csv',sample)]:
        with (outdir/filename).open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
    np.savez_compressed(outdir/'BOUND_FREE_ATOMWISE.npz',**atoms)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--source-zip',required=True)
    p.add_argument('--output',required=True)
    p.add_argument('--table',default=str(TABLE))
    ns=p.parse_args()
    params,tabhash=load_verner(ns.table)
    _,arrays,density=read_source(ns.source_zip)
    meta,rows,opaque,atoms=evaluate(arrays,density,params)
    save(Path(ns.output),meta,rows,opaque,atoms,tabhash)
    print(json.dumps({'source_atoms':6400,'bins':4,'target_rows':len(rows),
      'absorbed_lower_m3':meta['absorbed_lower_m3'], 'absorbed_upper_m3':meta['absorbed_upper_m3'],
      'fraction_bracket':[meta['absorption_fraction_lower'],meta['absorption_fraction_upper']],
      'table_sha256':tabhash},indent=2))

if __name__=='__main__':
    main()
