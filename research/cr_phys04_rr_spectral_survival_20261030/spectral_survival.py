#!/usr/bin/env python3
"""Source-locked spectral surviving H/He RR photons and photon-energy absorption.

Frozen-gas, stationary, homogeneous, no redshift / feedback / scattering. Inputs:
immutable PR128 SOURCE ZIP wrapping immutable PR125 photon atomwise NPZ, and PR127
verner implementation, with strict hash locks. The bounds are pointwise sharp.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import importlib.util
import io
import json
import math
import tempfile
from pathlib import Path
import zipfile
import numpy as np

ROOT=Path(__file__).resolve().parent
SOURCE_ARCHIVE=ROOT/'sources'/'PR128_ORIGINAL_SOURCE.zip'
SHA128='a6062e5fa54c51983439e256ffd521f7b25d151952293e0fad7c2b3064ff4819'
SHA125='8e9b58236819146f4929aa4647dafdb1dc21b97b2f129ec4035291bb73a1ed2e'
SHA127='2db17652571465cd2e5f5fde51f60be01fd6d3ae2b11b193addc98dd047f9594'
SHA_TABLE='a9ae2f7e7393de6f9ad89376cf5dd4be84da60cb3dadde3be37a4d3bd5989492'
SHA_NPZ='e171824cf5fc3ba232fbbd4def6fc8cf6c855ca9e7d05506e4e4426c9416688f'
PREFIX_128='research/cr_phys03_rr_time_envelope_20261030/'
PREFIX_127='research/cr_phys02_rr_boundfree_20261030/'
PREFIX_125='research/cr_phys02_rr_ionizing_photons_20261029/'
C=299792458.0
EV_J=1.602176634e-19
ENERGY_EDGES=np.arange(13.,37.,1.)
TIMES=np.arange(9,dtype=float)*1.25e9
SOURCES=('H','He')
TARGETS=('HI','HeI')


def sha256(raw:bytes): return hashlib.sha256(raw).hexdigest()

def fsum(values):return math.fsum(np.ravel(np.asarray(values, dtype=np.float64)))


def source_load(archive=SOURCE_ARCHIVE):
    b=Path(archive).read_bytes()
    if sha256(b)!=SHA128: raise ValueError('SOURCE_PR128_ARCHIVE_SHA256_MISMATCH')
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        if z.testzip() is not None:raise ValueError('SOURCE_PR128_CRC_FAIL')
        nested=z.read('source/ORIGINAL_PR125_SOURCE_IMMUTABLE.zip')
        mod=z.read(PREFIX_127+'rr_boundfree.py')
        table=z.read(PREFIX_127+'source/VERNER1996_HI_HEI_TABLE1.dat')
        oldtotal=json.loads(z.read(PREFIX_128+'results/RESULT.json'))
        oldcsv=z.read(PREFIX_128+'results/TIME_TOTAL.csv').decode('utf-8')
    if (sha256(nested),sha256(mod),sha256(table)) != (SHA125,SHA127,SHA_TABLE):
        raise ValueError('SOURCE_PR125_PR127_BYTE_IDENTITY_MISMATCH')
    with tempfile.TemporaryDirectory(prefix='cr_ph04_parent_') as tmp:
        moddir=Path(tmp)
        (moddir/'source').mkdir()
        (moddir/'rr_boundfree.py').write_bytes(mod)
        (moddir/'source'/'VERNER1996_HI_HEI_TABLE1.dat').write_bytes(table)
        spec=importlib.util.spec_from_file_location('cr_ph04_lock_parent',moddir/'rr_boundfree.py')
        parent=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(parent)
        # The original script itself verifies nested PR110 inventory and NPZ SHA.
        with tempfile.NamedTemporaryFile(prefix='crph04_pr125_',suffix='.zip') as fo:
            fo.write(nested);fo.flush()
            _, arrays, density=parent.read_source(fo.name)
        params,table_sha=parent.load_verner()
        if table_sha!=SHA_TABLE: raise ValueError('TABLE_CHECK_FAILED')
        # Avoid retaining a module dependent on a removed temp directory: evaluate sigma now.
        sigma={ch:{a:parent.verner_sigma(arrays[f'photon_{ch}_eV'],params[a]) for a in TARGETS}
               for ch in SOURCES}
        return arrays,density,params,sigma,oldtotal,list(csv.DictReader(io.StringIO(oldcsv)))


def atom_components(weight,alpha_h,alpha_he,l,r,T):
    """Pointwise extrema as (unborn L/U, survivors L/U, absorbed by two targets L/U).

    An arbitrary exact birth timestamp within [l,r] is admissible. At l<=T<r,
    survivor maximum uses the *interior* birth time s=T, not necessarily endpoints.
    """
    alpha=alpha_h+alpha_he
    if np.any(alpha<=0):raise ValueError('NEED_POSITIVE_TOTAL_OPACITY')
    bh=alpha_h/alpha;be=alpha_he/alpha
    z=np.zeros_like(weight)
    if T<l:
        return (weight.copy(),weight.copy(),z.copy(),z.copy(),
                z.copy(),z.copy(),z.copy(),z.copy())
    if T<r:
        dur=T-l
        f_hi=-np.expm1(-alpha*C*dur)
        return (z.copy(),weight.copy(),z.copy(),weight.copy(),
                z.copy(),weight*f_hi*bh,z.copy(),weight*f_hi*be)
    dur_lo=T-l;dur_hi=T-r
    f_alo=-np.expm1(-alpha*C*dur_hi)
    f_ahi=-np.expm1(-alpha*C*dur_lo)
    return (z.copy(),z.copy(),weight*np.exp(-alpha*C*dur_lo),weight*np.exp(-alpha*C*dur_hi),
            weight*f_alo*bh,weight*f_ahi*bh,weight*f_alo*be,weight*f_ahi*be)


def witness(weight, alpha_h,alpha_he, l,r,T,policy):
    """One explicitly chosen emission-time witness with an exact photon ledger."""
    if policy=='earliest':s=l
    elif policy=='latest':s=r
    elif policy=='just_in_time':s=min(r,max(l,T))
    else:raise ValueError('UNKNOWN_WITNESS_POLICY')
    alpha=alpha_h+alpha_he
    if T<s:
        return weight.copy(),np.zeros_like(weight),np.zeros_like(weight),np.zeros_like(weight)
    frac=-np.expm1(-alpha*C*(T-s))
    return (np.zeros_like(weight), weight*np.exp(-alpha*C*(T-s)),
            weight*frac*(alpha_h/alpha), weight*frac*(alpha_he/alpha))


def bound_arrays(arrays,density,params,sigma,T):
    all_atoms=[]
    for ch in SOURCES:
        E=arrays[f'photon_{ch}_eV']; weights=arrays[f'capture_{ch}_bins_m3']
        h=sigma[ch]['HI']*density['HI'];he=sigma[ch]['HeI']*density['HeI']
        s=[np.zeros_like(E) for _ in range(8)]
        for j in range(4):
            l,r=map(float,arrays['time_edges_s'][j:j+2])
            parts=atom_components(weights[j],h,he,l,r,T)
            for k in range(8):s[k]+=parts[k]
        all_atoms.append((ch,E,s))
    return all_atoms


def compute(arrays,density,params,sigma,parent_total,parent_csv, times=TIMES):
    times=np.asarray(times,dtype=float)
    if times.ndim!=1 or not len(times) or np.any(~np.isfinite(times)) or np.any(times<0) or np.any(np.diff(times)<=0):
        raise ValueError('INVALID_OBSERVATION_GRID')
    if not np.array_equal(arrays['time_edges_s'],[0.,2.5e9,5e9,7.5e9,1e10]):
        raise ValueError('MISMATCHED_PROPER_TIME_GRID')
    energy_rows=[]; absorption_rows=[];total_rows=[];witness_rows=[]
    source_total=fsum([fsum(arrays[f'capture_{ch}_bins_m3']) for ch in SOURCES])
    source_energy=sum(fsum(arrays[f'capture_{ch}_bins_m3'][j]*arrays[f'photon_{ch}_eV'])*EV_J for ch in SOURCES for j in range(4))
    if not np.all((arrays['photon_H_eV']>=ENERGY_EDGES[0])&(arrays['photon_H_eV']<ENERGY_EDGES[-1])) or not np.all((arrays['photon_He_eV']>=ENERGY_EDGES[0])&(arrays['photon_He_eV']<ENERGY_EDGES[-1])):
        raise ValueError('SPECTRAL_ENERGY_GRID_DOES_NOT_COVER_SOURCE')
    hist_cache={ch:np.digitize(arrays[f'photon_{ch}_eV'],ENERGY_EDGES,right=False)-1 for ch in SOURCES}
    for T in times:
        agg=np.zeros(8,dtype=float);enagg=np.zeros(8,dtype=float)
        for ch,E,s in bound_arrays(arrays,density,params,sigma,float(T)):
            idx=hist_cache[ch]
            for k in range(len(ENERGY_EDGES)-1):
                select=(idx==k)
                vec=[fsum(v[select]) for v in s]
                qvec=[fsum(v[select]*E[select])*EV_J for v in s]
                agg+=np.array(vec);enagg+=np.array(qvec)
                row={'T_s':float(T),'source':ch,'Elo_eV':float(ENERGY_EDGES[k]),'Ehi_eV':float(ENERGY_EDGES[k+1]),
                     'unborn_lo_m3':vec[0],'unborn_hi_m3':vec[1],
                     'survive_lo_m3':vec[2],'survive_hi_m3':vec[3],
                     'survive_energy_lo_J_m3':qvec[2],'survive_energy_hi_J_m3':qvec[3],
                     'total_absorbed_lo_m3':vec[4]+vec[6], 'total_absorbed_hi_m3':vec[5]+vec[7]}
                energy_rows.append(row)
                for a,(il,ih) in zip(TARGETS,((4,5),(6,7))):
                    absorption_rows.append({'T_s':float(T),'source':ch,'target':a,
                         'Elo_eV':row['Elo_eV'],'Ehi_eV':row['Ehi_eV'],
                         'absorbed_lo_m3':vec[il],'absorbed_hi_m3':vec[ih],
                         'photon_energy_lo_J_m3':qvec[il],'photon_energy_hi_J_m3':qvec[ih],
                         'threshold_energy_lo_J_m3':vec[il]*params[a][0]*EV_J,
                         'threshold_energy_hi_J_m3':vec[ih]*params[a][0]*EV_J,
                         'primary_electron_excess_lo_J_m3':qvec[il]-vec[il]*params[a][0]*EV_J,
                         'primary_electron_excess_hi_J_m3':qvec[ih]-vec[ih]*params[a][0]*EV_J})
            # One joint all-state, all-energy ledger for each witness at each T.
            h=sigma[ch]['HI']*density['HI'];he=sigma[ch]['HeI']*density['HeI']
            for policy in ('earliest','latest','just_in_time'):
                terms=[np.zeros_like(E) for _ in range(4)]
                for j in range(4):
                    l,r=map(float,arrays['time_edges_s'][j:j+2])
                    witness_parts=witness(arrays[f'capture_{ch}_bins_m3'][j],h,he,l,r,float(T),policy)
                    for ix in range(4):terms[ix]+=witness_parts[ix]
                born=fsum(arrays[f'capture_{ch}_bins_m3']);ener=fsum(arrays[f'capture_{ch}_bins_m3']*E)*EV_J
                if not np.isclose(fsum([fsum(t) for t in terms]),born,rtol=3e-14,atol=1e-92):raise AssertionError('WITNESS_PHOTON_COUNT_LEDGER')
                if not np.isclose(sum(fsum(t*E)*EV_J for t in terms),ener,rtol=3e-14,atol=1e-92):raise AssertionError('WITNESS_PHOTON_ENERGY_LEDGER')
                witness_rows.append({'T_s':float(T),'source':ch,'policy':policy,
                   'unborn_m3':fsum(terms[0]),'survive_m3':fsum(terms[1]),'absorbed_HI_m3':fsum(terms[2]),'absorbed_HeI_m3':fsum(terms[3]),
                   'number_residual_m3':fsum([fsum(t) for t in terms])-born,
                   'energy_residual_J_m3':sum(fsum(t*E)*EV_J for t in terms)-ener})
        # Index order: Ulo Uhi Slo Shi A_Hlo A_Hhi A_Helo A_Hehi
        total_rows.append({'T_s':float(T),'source_photons_m3':source_total,'source_photon_energy_J_m3':source_energy,
          'unborn_lo_m3':agg[0],'unborn_hi_m3':agg[1],
          'survive_lo_m3':agg[2],'survive_hi_m3':agg[3],
          'survive_energy_lo_J_m3':enagg[2],'survive_energy_hi_J_m3':enagg[3],
          'absorbed_HI_lo_m3':agg[4],'absorbed_HI_hi_m3':agg[5],
          'absorbed_HeI_lo_m3':agg[6],'absorbed_HeI_hi_m3':agg[7],
          'absorbed_lo_m3':agg[4]+agg[6],'absorbed_hi_m3':agg[5]+agg[7],
          'absorbed_photon_energy_lo_J_m3':enagg[4]+enagg[6],
          'absorbed_photon_energy_hi_J_m3':enagg[5]+enagg[7]})
    # Reuse frozen PR128 summary as independent full-source comparison for 9 times.
    if len(times)==len(parent_csv) and np.array_equal(times,TIMES):
        for row,old in zip(total_rows,parent_csv):
            if float(old['T_s'])!=row['T_s']:raise AssertionError('PARENT_TIME_ALIGNMENT_MISMATCH')
            for k in ('survive_lo_m3','survive_hi_m3','absorbed_lo_m3','absorbed_hi_m3'):
                if not np.isclose(row[k],float(old[k]),rtol=6e-13,atol=1e-92):
                    raise AssertionError(f'PARENT_PR128_HISTORY_REGRESSION_{k}:{row[k]}:{old[k]}')
    # At final horizon, no un-emitted photons; lower/upper dual survivor versus absorption.
    if times[-1] == float(arrays['time_edges_s'][-1]):
        z=total_rows[-1]
        for surv,absorb in (('survive_lo_m3','absorbed_hi_m3'),('survive_hi_m3','absorbed_lo_m3')):
            if not np.isclose(z[surv]+z[absorb],source_total,rtol=4e-14,atol=1e-92):
                raise AssertionError('FINAL_PHOTON_CONSERVATION_REGRESSION')
        for surv,absorb in (('survive_energy_lo_J_m3','absorbed_photon_energy_hi_J_m3'),('survive_energy_hi_J_m3','absorbed_photon_energy_lo_J_m3')):
            if not np.isclose(z[surv]+z[absorb],source_energy,rtol=4e-14,atol=1e-92):
                raise AssertionError('FINAL_PHOTON_ENERGY_CONSERVATION_REGRESSION')
        for e in energy_rows[-(len(SOURCES)*(len(ENERGY_EDGES)-1)):]:
            if not np.isclose(e['survive_lo_m3']+e['total_absorbed_hi_m3'],
                              e['survive_hi_m3']+e['total_absorbed_lo_m3'],rtol=5e-13,atol=1e-91):
                raise AssertionError('FINAL_SPECTRAL_COMPLEMENT_MISMATCH')
    # Physically forbidden H-produced photon -> HeI absorption must be strictly zero.
    if any(row['absorbed_hi_m3']!=0 for row in absorption_rows if row['source']=='H' and row['target']=='HeI'):
        raise AssertionError('BELOW_HEI_THRESHOLD_ABSORPTION')
    return {'schema':'CR_PHYS04_RR_SPECTRAL_SURVIVAL_V1',
      'physics':'fixed homogeneous 100 K H/He gas, original RR photons at c; primary first absorption only',
      'source_parent_pr':128,'parent_sha256':SHA128,'nested_pr125_zip_sha256':SHA125,
      'pr125_npz_sha256':SHA_NPZ,'pr127_code_sha256':SHA127,'verner_table_sha256':SHA_TABLE,
      'density_m3':density,'time_grid_s':[float(t) for t in times],
      'photon_energy_bin_edges_eV':ENERGY_EDGES.tolist(),
      'source_photons_m3':source_total,'source_photon_energy_J_m3':source_energy,
      'spectral_rows':len(energy_rows),'absorber_spectral_rows':len(absorption_rows),
      'witness_rows':len(witness_rows),'time_rows':len(total_rows),
      'final':total_rows[-1],
      'status':'SCOPED_CONDITIONAL_DATA_INDEPENDENT_REVIEW_HOLD',
      'central_dag':'28/88','extension_dag':'0/3','physical_kernel_K':None,
      'assumptions':['fixed neutral density','no time-evolving chemistry','no cosmic redshift or Bianchi transfer','no scattering/re-emission','unknown within-bin emission time'],
      'no_unique_emission_history':True,'no_physical_flux_without_angular_field':True,
      'no_thermal_deposition_claim':True,'native25':False,'L4':False,'production':False},energy_rows,absorption_rows,total_rows,witness_rows


def save_csv(out,filename,rows):
    if not rows:raise ValueError('NO_ROWS')
    with (out/filename).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)


def run(archive=SOURCE_ARCHIVE,out=ROOT/'results'):
    arrays,density,params,sigma,old_total,old_csv=source_load(archive)
    meta,energy,absorption,totals,wit=compute(arrays,density,params,sigma,old_total,old_csv)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    (out/'RESULT.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False,sort_keys=True)+'\n',encoding='utf-8')
    save_csv(out,'SURVIVING_PHOTON_ENERGY.csv',energy)
    save_csv(out,'ABSORBED_PHOTON_ENERGY.csv',absorption)
    save_csv(out,'TIME_TOTAL.csv',totals)
    save_csv(out,'JOINT_WITNESS_LEDGERS.csv',wit)
    return meta

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--source-zip',type=Path,default=SOURCE_ARCHIVE)
    p.add_argument('--out',type=Path,default=ROOT/'results')
    args=p.parse_args()
    meta=run(args.source_zip,args.out)
    print(json.dumps({'rows':{k:meta[k] for k in ('spectral_rows','absorber_spectral_rows','witness_rows','time_rows')},'final':meta['final']},indent=2))