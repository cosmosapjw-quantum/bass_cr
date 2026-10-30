#!/usr/bin/env python3
"""PHYS13 original measured Shah1987 H e-impact table times immutable BASS-CR H/He RR source.

Outputs only experiment-anchored *conditional scenario* first-photon-then-electron
second-ionization capacities, not realized electron trajectories, stopping or K.
The 67%-level point reproducibility and separate 6.8% normalization are not a
rigorous simultaneous uncertainty band. The domain below 14.6 eV is unresolved.
"""
from __future__ import annotations
import argparse,csv,hashlib,importlib.util,json,math,sys,tempfile,zipfile
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
PARENT_SHA='9edcf980e54411ef1a91099419b10b1d0ab4382196b188e395acb916abf98586'
PARENT_HEAD='67d6fe0e973fe3ffb2a8a12b3e9e01075ee50a6a'
ME=9.1093837139e-31
EV_J=1.602176634e-19
SIGMA_UNIT=1e-21 # 10^-17 cm^2 -> m^2
NORM_FRAC=0.068 # separate coherent absolute normalization estimate from original Shah p3509
_GL_X,_GL_W=np.polynomial.legendre.leggauss(24)
_GL_Q=0.5*(_GL_X+1);_GL_WEIGHT=0.5*_GL_W
TIMES=np.arange(9,dtype=float)*1.25e9
POLICIES=('earliest','midpoint','latest')
TARGETS=('HI','HeI')
ENERGY_BINS=list(zip(np.arange(13.,36.,1.),np.arange(14.,37.,1.)))

def sha(b):return hashlib.sha256(b).hexdigest()
def fs(x):return math.fsum(float(y) for y in np.asarray(x).ravel())
def load_original(fullzip):
    raw=Path(fullzip).read_bytes()
    if sha(raw)!=PARENT_SHA: raise ValueError('PHYS12_SOURCE_BYTES_WRONG')
    with zipfile.ZipFile(fullzip) as z:
        if z.testzip():raise ValueError('PHYS12_ZIP_CRC_FAIL')
        mf=json.loads(z.read('SOURCE_MANIFEST.json'))['members']
        if len(mf)!=48:raise ValueError('PHYS12_MANIFEST_COUNT')
        prefix='research/cr_phys12_kim1992_h_eii_20261030/'
        for e in mf:
            b=z.read(prefix+e['path'])
            if len(b)!=e['size'] or sha(b)!=e['sha256']:raise ValueError('PHYS12_MEMBER_IDENTITY_FAIL:'+e['path'])
        code=z.read(prefix+'phys12_h_eii.py')
        zparent=z.read(prefix+'sources/PR136_ORIGINAL_SOURCE.zip')
    with tempfile.TemporaryDirectory(prefix='cr_phys13_owner_') as tmp:
        p=Path(tmp); (p/'phys12_h_eii.py').write_bytes(code);(p/'PHYS11.zip').write_bytes(zparent)
        s=importlib.util.spec_from_file_location('cr_phys12_exact_owner_for_phys13',p/'phys12_h_eii.py')
        mod=importlib.util.module_from_spec(s);sys.modules[s.name]=mod;s.loader.exec_module(mod)
        owner=mod.load_owner(p/'PHYS11.zip')
    _,_,prep,_,dens=owner
    if sum(len(z['energy']) for z in prep)!=6400 or abs(dens['HI']-138.6)>1e-10:raise ValueError('ORIGINAL_OWNER_DRIFT')
    return mod,owner

def load_shah(path):
    with Path(path).open(newline='',encoding='utf8') as f:rows=list(csv.DictReader(f))
    e=np.array([float(r['energy_eV']) for r in rows]); s=np.array([float(r['sigma_1e_minus17_cm2']) for r in rows]); err=np.array([float(r['individual_67pct_error_same_units']) for r in rows])
    if len(rows)!=26 or e[0]!=14.6 or e[-1]!=21.4 or not np.all(np.diff(e)>0):raise ValueError('SHAH_TABLE_IDENTITY_BAD')
    if np.any(s<=0) or np.any(err<=0):raise ValueError('TABLE_NONPOSITIVE')
    return rows,e,s,err

def sigma_models(E,knots,vals,errs):
    E=np.asarray(E,dtype=float)
    covered=(E>=knots[0])&(E<=knots[-1]);ge=E>=13.6
    center=np.interp(E,knots,vals)*SIGMA_UNIT
    lo=np.interp(E,knots,np.maximum(vals-errs,0.))*SIGMA_UNIT*(1-NORM_FRAC)
    hi=np.interp(E,knots,vals+errs)*SIGMA_UNIT*(1+NORM_FRAC)
    # Zero-filled array is only a *measured-domain contribution accounting convention*.
    # Do not interpret these zeros as cross sections outside the measured domain.
    return covered,ge,np.where(covered,center,0.),np.where(covered,lo,0.),np.where(covered,hi,0.)

def velocity(E):return np.sqrt(2*EV_J*np.maximum(np.asarray(E,dtype=float),0.)/ME)

def second_p(ka,k,nu,dt):
    ka=np.asarray(ka);nu=np.asarray(nu)
    if dt<=0:return np.zeros_like(ka)
    u=dt*_GL_Q[:,None]
    result=ka[None,:]*np.exp(-k[None,:]*u)*(-np.expm1(-nu[None,:]*(dt-u)))
    return dt*np.einsum('i,ij->j',_GL_WEIGHT,result)

def second_dlogscale(ka,k,nu,dt):
    ka=np.asarray(ka);nu=np.asarray(nu)
    if dt<=0:return np.zeros_like(ka)
    u=dt*_GL_Q[:,None];r=dt-u
    result=ka[None,:]*np.exp(-k[None,:]*u)*(nu[None,:]*r)*np.exp(-nu[None,:]*r)
    return dt*np.einsum('i,ij->j',_GL_WEIGHT,result)

def write_csv(path,rows):
    with Path(path).open('w',newline='',encoding='utf8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)

def generate(source_zip,shah_csv,out):
    p12,original=load_original(source_zip)
    owner,edges,prep,params,dens=original
    table,Eobs,So,Err=load_shah(shah_csv)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    nH=float(dens['HI']);HI=float(params['HI'][0])
    knots=[]
    for i,row in enumerate(table):
        ek=float(Eobs[i]); kim=float(p12.kim_sigma_m2(np.array([ek]))[0]);ms=So[i]*SIGMA_UNIT
        knots.append(dict(Shah1987_source_page='3508_Table1',point_index=i,E_incident_eV=ek,
           measured_sigma_m2=ms,individual_67pct_error_m2=Err[i]*SIGMA_UNIT,
           additional_common_absolute_normalization_fraction=NORM_FRAC,
           printed_asterisk=int(row['printed_asterisk']),Kim1992_sigma_m2=kim,
           Kim_minus_Shah_percent=100*(kim/ms-1)))
    write_csv(out/'SHAH1987_MEASURED_26.csv',knots)
    atom=[];sourcen=[]
    for pp in prep:
        photon=np.asarray(pp['energy'],float);eps=photon-HI
        covered,eligible,sm,lo,hi=sigma_models(eps,Eobs,So,Err)
        v=velocity(eps);kim=p12.kim_sigma_m2(eps)
        nu=np.array([sm,lo,hi,np.where(covered,kim,0.)])*nH*v[None,:]
        kh=np.asarray(pp['k'])*np.asarray(pp['frac'])[0]
        khe=np.asarray(pp['k'])*np.asarray(pp['frac'])[1]
        info=dict(pp=pp,photon=photon,eps=eps,covered=covered,eligible=eligible,
                  sigma=np.array([sm,lo,hi,kim]),nu=nu,kh=kh,khe=khe,vel=v)
        sourcen.append(info)
        for i,x in enumerate(eps):
            atom.append(dict(source=pp['source'],source_energy_index=i,E_photon_eV=float(photon[i]),
                E_first_H_electron_eV=float(x),EII_H_energy_eligible=int(eligible[i]),
                Shah_measured_domain=int(covered[i]),unmeasured_below_14_6=int(eligible[i] and x<14.6),
                sigma_Shah_interpolated_m2=float(sm[i]) if covered[i] else '',
                sigma_Shah_minus_scenario_m2=float(lo[i]) if covered[i] else '',
                sigma_Shah_plus_scenario_m2=float(hi[i]) if covered[i] else '',
                sigma_Kim_m2=float(kim[i]),v_e_m_s=float(v[i]),
                nu_Shah_interpolated_s_inv=float(nu[0,i]) if covered[i] else '',
                first_H_absorb_hazard_s_inv=float(kh[i])))
    write_csv(out/'SOURCE_ATOM_OBSERVED_CROSSWALK.csv',atom)
    rows=[];channels=[];bins=[]
    for T in TIMES:
      for policy in POLICIES:
        total=np.zeros(9)
        for info in sourcen:
            pp=info['pp'];kt=info['kh']+info['khe'];parts=np.zeros(9)
            for j in range(4):
                birth=owner.bin_birth(float(edges[j]),float(edges[j+1]),policy)
                dt=float(T-birth);w=np.asarray(pp['weights'][j],float)
                firstH=owner.first_probability(info['kh'],info['khe'],dt,0)
                firstHe=owner.first_probability(info['kh'],info['khe'],dt,1)
                cap=firstH*info['eligible'];unc=cap*(~info['covered'])
                bound=np.array([fs(w*second_p(info['kh'],kt,info['nu'][q],dt)) for q in range(4)])
                der=fs(w*second_dlogscale(info['kh'],kt,info['nu'][0],dt))
                parts+=np.array([fs(w*firstH),fs(w*firstHe),fs(w*cap),fs(w*unc),*bound[:3],der,bound[3]])
                # Kim measured coverage is calculated independently in a separate support column.
            channels.append(dict(observation_s=float(T),birth_policy=policy,source=pp['source'],
               first_H_photoabsorptions_m3=parts[0],first_He_photoabsorptions_m3=parts[1],
               PHYS11_kinematic_capacity_m3=parts[2],unmeasured_kinematic_capacity_m3=parts[3],
               Shah_central_observed_coverage_second_m3=parts[4],
               Shah_minus_uncertainty_scenario_m3=parts[5],Shah_plus_uncertainty_scenario_m3=parts[6],
               d_Shah_central_observed_coverage_d_ln_common_norm_m3=parts[7],
               Kim_on_same_Shah_measured_support_second_m3=parts[8]))
            total+=parts
        rows.append(dict(observation_s=float(T),birth_policy=policy,
           first_total_m3=total[0]+total[1],first_H_target_m3=total[0],
           first_He_target_m3=total[1],PHYS11_kinematic_H_capacity_m3=total[2],
           unmeasured_kinematic_capacity_m3=total[3],
           Shah_central_observed_coverage_second_m3=total[4],
           Shah_minus_uncertainty_scenario_m3=total[5],Shah_plus_uncertainty_scenario_m3=total[6],
           Shah_central_log_common_norm_sensitivity_m3=total[7],
           Kim_on_same_Shah_measured_support_second_m3=total[8],
           Shah_over_Kim_same_support=(total[4]/total[8] if total[8] else ''),
           Shah_measured_fraction_of_kinematic_cap=(total[2]-total[3])/total[2] if total[2]>0 else '',
           unexplored_impact_bound_trivial_m3=total[3],
           entire_model_capacity_upper_scenario_m3=total[6]+total[3]))
    write_csv(out/'TIME_CHANNEL_OBSERVED_COVERAGE.csv',channels)
    write_csv(out/'TIME_TOTAL_OBSERVED_COVERAGE.csv',rows)
    tf=float(TIMES[-1])
    for info in sourcen:
      pp=info['pp'];k=info['kh']+info['khe'];eps=info['eps']
      for policy in ('earliest','latest'):
        arr=np.zeros((6,len(eps)))
        for j in range(4):
          dt=tf-owner.bin_birth(float(edges[j]),float(edges[j+1]),policy)
          w=np.asarray(pp['weights'][j],float)
          first=owner.first_probability(info['kh'],info['khe'],dt,0)
          arr[0]+=w*first
          arr[1]+=w*first*info['eligible']
          arr[2]+=w*first*info['eligible']*(~info['covered'])
          for q in range(3): arr[3+q]+=w*second_p(info['kh'],k,info['nu'][q],dt)
        for low,high in ENERGY_BINS:
          mask=(info['photon']>=low)&(info['photon']<high)
          bins.append(dict(source=pp['source'],policy=policy,photon_E_low_eV=float(low),photon_E_high_eV=float(high),
              first_H_m3=fs(arr[0,mask]),energy_capacity_m3=fs(arr[1,mask]),
              unmeasured_capacity_m3=fs(arr[2,mask]),
              Shah_central_observed_second_m3=fs(arr[3,mask]),
              Shah_minus_scenario_m3=fs(arr[4,mask]),Shah_plus_scenario_m3=fs(arr[5,mask])))
    write_csv(out/'FINAL_SOURCE_ENERGY_BINS.csv',bins)
    if (len(knots),len(atom),len(channels),len(rows),len(bins))!=(26,6400,54,27,92):raise AssertionError('ROW_COUNT_DRIFT')
    final={policy:next(r for r in rows if r['observation_s']==tf and r['birth_policy']==policy) for policy in POLICIES}
    selflast=final['earliest']
    kimfit_at_measurement=[r['Kim_minus_Shah_percent'] for r in knots]
    counts=dict(measured_knots=26,source_atoms=6400,time_channels=54,time_totals=27,energy_bins=92,total_rows=6599)
    result={
       'unit':'CR_PHYS13_SHAH1987_DIRECT_MEASUREMENT_SOURCE_BRIDGE',
       'parent_PR':137,'parent_head':PARENT_HEAD,'parent_source_sha256':PARENT_SHA,
       'source_atoms':6400,'rows':counts,'source_shah_page':'3508 Table1','shah_measurement_range_eV':[14.6,21.4],
       'shah_normalization_uncertainty_fraction':0.068,
       'individual_errors':'67% reported reproducibility/statistical; NOT joint simultaneous CI',
       'uncertainty_scenario':'interpolated each (value +/- printed error) times (1 +/- 0.068); NOT rigorous bound',
       'unmeasured_region':'13.6 eV <= incident Ee <14.6 eV; contribution not assigned sigma or measured rate',
       'kim_deviation_max_abs_percent_at_26_knots':max(abs(z) for z in kimfit_at_measurement),
       'kim_deviation_at_14_6_percent':knots[0]['Kim_minus_Shah_percent'],
       'final':final,'central_DAG':'28/88 delta0','extension_DAG':'0/3 delta0','auxiliary':'1/1 CONDITIONAL REVIEW_HOLD',
       'R06_distinct_author':'NOT_RUN','C09_distinct_author':'NOT_RUN','native_subagent':'NOT_RUN',
       'physical_K':'UNBOUND','stopping':'UNBOUND','He_exclusive':'UNBOUND','common_evolving_neutral_radiation_clock_geometry':'UNBOUND',
       'production':'HOLD','merge_ready':False,'auto_next':False}
    (out/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False)+'\n',encoding='utf8')
    print(json.dumps({'rows':counts,'fit_14_6_percent':knots[0]['Kim_minus_Shah_percent'],
       'final_earliest':final['earliest'],'final_latest':final['latest']},indent=2))
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,default=ROOT/'sources/PR137_ORIGINAL_SOURCE.zip');p.add_argument('--shah',type=Path,default=ROOT/'data_shah1987.csv');p.add_argument('--out',type=Path,default=ROOT/'results');a=p.parse_args();generate(a.source,a.shah,a.out)
