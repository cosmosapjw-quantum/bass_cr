#!/usr/bin/env python3
"""Source-locked *causal neutral-opacity response*, not a coupled chemical IVP.

Original 100 K H/He RR photon source; frozen neutral opacity; all quantities
conditioned on the original birth-bin weights and original Verner cross sections.
"""
from __future__ import annotations
import argparse, csv, hashlib, importlib.util, json, math, tempfile, zipfile
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'sources/PR133_ORIGINAL_SOURCE.zip'
SOURCE_SHA='16d0b7c9e2540777ea0e360511e502303e6ea887ae0ecd658282d14d79923ae4'
PREV_SOURCE_SHA='ff48de4e951e63da4c6a5624bed3975ec22ad43513b67b8c355fc6237fabde98'
PARENT_HEAD='7386c9e707405438f1b2f69ad13c5900a575f99e'
TIMES=np.arange(9,dtype=float)*1.25e9
WINDOWS=list(zip(TIMES[:-1],TIMES[1:]))
POLICIES=('earliest','midpoint','latest')
TARGETS=('HI','HeI')
ENERGY_BINS=np.arange(13.,37.,1.)
C=299792458.0

def sha(p:bytes): return hashlib.sha256(p).hexdigest()
def fsum(a): return math.fsum(float(x) for x in np.asarray(a).ravel())

def original_source(zip_path:Path=SOURCE):
    raw=Path(zip_path).read_bytes()
    if sha(raw)!=SOURCE_SHA: raise ValueError('ORIGINAL_PHYS08_SOURCE_SHA_MISMATCH')
    with zipfile.ZipFile(zip_path) as z:
        if z.testzip(): raise ValueError('ORIGINAL_PHYS08_ZIP_CRC_FAIL')
        manifest=json.loads(z.read('SOURCE_MANIFEST.json'))['files']
        if len(manifest)!=45: raise ValueError('ORIGINAL_45_PAYLOADS')
        for f in manifest:
            x=z.read(f['path'])
            if sha(x)!=f['sha256'] or len(x)!=f['size']: raise ValueError('ORIGINAL_PAYLOAD_MISMATCH:'+f['path'])
        prefix='research/cr_phys08_rr_freeflight_20261030/'
        parent_code=z.read(prefix+'flight_delay.py')
        parent_source=z.read(prefix+'sources/PR132_ORIGINAL_SOURCE.zip')
    if sha(parent_source)!=PREV_SOURCE_SHA:raise ValueError('ORIGINAL_NESTED_PHYS07_SOURCE_MISMATCH')
    with tempfile.TemporaryDirectory(prefix='cr_ph09_owner_') as d:
        d=Path(d); (d/'flight_delay.py').write_bytes(parent_code)
        (d/'original.zip').write_bytes(parent_source)
        spec=importlib.util.spec_from_file_location('phys08_immutable_source', d/'flight_delay.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        edges,prep,params,dens,prev=module.owner_loader(d/'original.zip')
    assert len(prep)==2 and all(len(pp['energy'])==3200 for pp in prep)
    return np.asarray(edges),prep,params,dens,prev

def bin_birth(a,b,policy):
    return {'earliest':a,'midpoint':0.5*(a+b),'latest':b}[policy]

def first_probability(ka,kb,delta,selected):
    """Baseline first absorption by target selected=0/1 for one photon."""
    ka=np.asarray(ka,dtype=float);kb=np.asarray(kb,dtype=float);kt=ka+kb
    out=np.zeros_like(kt)
    if delta<=0:return out
    positive=kt>0
    out[positive]=(ka if selected==0 else kb)[positive]/kt[positive]*(-np.expm1(-kt[positive]*delta))
    return out

def log_response(ka,kb,s,T,u,v,absorber,parameter):
    """Exact derivative d P_absorber(T) / d ln(n_parameter) for a neutral
    perturbation supported only in proper-time window [u,v].

    Constant source gas is basepoint; no assumption on the realized perturbation.
    No absorption before photon birth; all cases return dimensionless derivative.
    """
    ka=np.asarray(ka,dtype=float);kb=np.asarray(kb,dtype=float)
    if not np.isfinite([s,T,u,v]).all() or u>v: raise ValueError('INVALID_TEMPORAL_DOMAIN')
    if (ka<0).any() or (kb<0).any():raise ValueError('NEGATIVE_OPACITY')
    k=ka+kb
    out=np.zeros_like(k)
    lo=max(s,u);hi=min(T,v)
    if T<=s or hi<=lo:return out
    length=hi-lo
    # Stable equivalent to ∫_lo^hi exp[-k(t-s)] dt.
    A=np.empty_like(k)
    positive=k>0
    A[positive]=np.exp(-k[positive]*(lo-s))*(-np.expm1(-k[positive]*length))/k[positive]
    A[~positive]=length
    ktarg=(ka,kb)[absorber]
    kpert=(ka,kb)[parameter]
    out[positive]=(1. if absorber==parameter else 0.)*kpert[positive]*A[positive] - (
        ktarg[positive]*kpert[positive]/k[positive])*(A[positive]-length*np.exp(-k[positive]*(T-s)))
    return out

def integrated_response(prep,edges,T,policy,source=None,absorber=0,parameter=0,window=(0.,1.e10),energy_range=None):
    vals=[]
    for pp in prep:
        if source is not None and pp['source']!=source:continue
        E=pp['energy'];k=pp['k'];frac=pp['frac'];w=pp['weights']
        kH=k*frac[0];kHe=k*frac[1]
        mask=np.ones(E.size) if energy_range is None else ((E>=energy_range[0])&(E<energy_range[1])).astype(float)
        for j in range(4):
            s=bin_birth(edges[j],edges[j+1],policy)
            resp=log_response(kH,kHe,s,T,*window,absorber,parameter)
            vals.append(fsum(resp*w[j]*mask))
    return math.fsum(vals)

def baseline_by_target(prep,edges,T,policy,source=None,target=0):
    vals=[]
    for pp in prep:
        if source is not None and pp['source']!=source:continue
        k=pp['k'];f=pp['frac'];E=pp['energy']
        ka=k*f[0];kb=k*f[1]
        for j in range(4):
            s=bin_birth(edges[j],edges[j+1],policy)
            vals.append(fsum(pp['weights'][j]*first_probability(ka,kb,T-s,target)))
    return math.fsum(vals)

def born_by_source(prep,edges,T,policy,source):
    return math.fsum(fsum(pp['weights'][j]) for pp in prep if pp['source']==source for j in range(4) if bin_birth(edges[j],edges[j+1],policy)<=T)

def uniform_log_response(ka,kb,delta,absorber,parameter):
    """Independent homogeneous-density derivative for a single original atom."""
    ka=np.asarray(ka,dtype=float);kb=np.asarray(kb,dtype=float)
    k=ka+kb;z=np.zeros_like(k)
    if delta<=0:return z
    pos=k>0
    q=(ka,kb)[absorber];r=(ka,kb)[parameter]
    survival=np.exp(-k[pos]*delta)
    first=-np.expm1(-k[pos]*delta)
    weighted_time=first-k[pos]*delta*survival
    z[pos]=(1 if absorber==parameter else 0)*r[pos]/k[pos]*first-q[pos]*r[pos]/k[pos]**2*weighted_time
    return z

def output(out:Path,source_zip:Path=SOURCE):
    edges,prep,params,dens,parent=original_source(source_zip)
    out.mkdir(parents=True,exist_ok=True)
    rows=[];totals=[]
    for T in TIMES:
        for policy in POLICIES:
            base=[baseline_by_target(prep,edges,float(T),policy,target=a) for a in range(2)]
            born=[born_by_source(prep,edges,float(T),policy,pp['source']) for pp in prep]
            grad=np.zeros((2,2),dtype=float)
            for pp in prep:
                for a in range(2):
                    for b in range(2):
                        for iw,window in enumerate(WINDOWS):
                            response=integrated_response(prep,edges,float(T),policy,pp['source'],a,b,window)
                            rows.append(dict(observation_s=float(T),birth_policy=policy,source=pp['source'],absorber=TARGETS[a],neutral_parameter=TARGETS[b],parameter_window=iw,
                                window_start_s=float(window[0]),window_end_s=float(window[1]),d_first_absorbed_dln_neutral_m3=response))
                            grad[a,b]+=response
            neu_H=born[0]-base[0];neu_He=born[1]-base[1]
            dln=np.array([neu_H/dens['HI'],neu_He/dens['HeI']])
            delta=grad@dln
            totals.append(dict(observation_s=float(T),birth_policy=policy,source_RR_H_m3=born[0],source_RR_He_m3=born[1],abs_HI_m3=base[0],abs_HeI_m3=base[1],abs_total_m3=sum(base),
                               grad_HI_lnHI_m3=grad[0,0],grad_HI_lnHeI_m3=grad[0,1],grad_HeI_lnHI_m3=grad[1,0],grad_HeI_lnHeI_m3=grad[1,1],
                               grad_total_lnHI_m3=grad[:,0].sum(),grad_total_lnHeI_m3=grad[:,1].sum(),
                               formal_net_neutral_H_m3=neu_H,formal_net_neutral_He_m3=neu_He,
                               formal_delta_lnHI= float(dln[0]),formal_delta_lnHeI=float(dln[1]),
                               formal_first_order_delta_abs_HI_m3=float(delta[0]),formal_first_order_delta_abs_HeI_m3=float(delta[1]),formal_first_order_delta_abs_total_m3=float(delta.sum())))
    final_bins=[];T=float(TIMES[-1]);
    for pp in prep:
        for policy in ('earliest','latest'):
            for a in range(2):
                for b in range(2):
                    for l,h in zip(ENERGY_BINS[:-1],ENERGY_BINS[1:]):
                        total=integrated_response(prep,edges,T,policy,pp['source'],a,b,(0,T),(l,h))
                        final_bins.append(dict(source=pp['source'],birth_policy=policy,absorber=TARGETS[a],neutral_parameter=TARGETS[b],energy_lo_eV=float(l),energy_hi_eV=float(h),d_first_absorbed_dln_neutral_m3=total))
    def write_csv(name,items):
        with (out/name).open('w',newline='',encoding='utf-8') as fh:
            writer=csv.DictWriter(fh,fieldnames=list(items[0]),lineterminator='\n');writer.writeheader();writer.writerows(items)
    write_csv('CAUSAL_RESPONSE.csv',rows)
    write_csv('TIME_CHEMISTRY_JACOBIAN.csv',totals)
    write_csv('FINAL_ENERGY_RESPONSE.csv',final_bins)
    earliest=next(x for x in totals if x['observation_s']==T and x['birth_policy']=='earliest')
    latest=next(x for x in totals if x['observation_s']==T and x['birth_policy']=='latest')
    if not math.isclose(earliest['abs_total_m3'],1.719391366604854e-26,rel_tol=2e-13):raise AssertionError('SOURCE_ABSORPTION_BASELINE_DRIFT')
    if not math.isclose(latest['abs_total_m3'],6.536559924836172e-27,rel_tol=2e-13):raise AssertionError('SOURCE_ABSORPTION_BASELINE_DRIFT_LATEST')
    if len(rows)!=1728 or len(totals)!=27 or len(final_bins)!=368:raise AssertionError('DATA_GRAIN_CONTRACT')
    result=dict(unit='CR_PHYS09_FROZEN_NEUTRAL_CAUSAL_SUSCEPTIBILITY_V1',parent_pr=133,parent_git_head=PARENT_HEAD,parent_original_source_sha256=SOURCE_SHA,
                original_source_atoms=6400,source_birth_bins=4,observation_epochs=9,neutral_perturbation_windows=8,original_fixed_neutral_m3=dens,
                causal_rows=len(rows),time_jacobian_rows=len(totals),final_energy_rows=len(final_bins),endpoints={'earliest':earliest,'latest':latest},
                response_def='partial first-absorbed photon number / partial ln neutral density restricted to a physical proper-time interval',
                caveat='Frozen 100K source linear causal response; formal first order neutral source displacement is NOT an evolving chemistry solution; no event K, He exclusive kernel, redshift or heat.',
                central_dag={'completed':28,'total':88,'delta':0},extension_dag={'completed':0,'total':3,'delta':0},auxiliary={'completed':1,'total':1,'review':'HOLD'},
                review_R06='NOT_RUN_DISTINCT_AUTHOR',review_C09='NOT_RUN_DISTINCT_AUTHOR',native_subagent='NOT_RUN_TOOL_UNAVAILABLE',production=False,L4=False,native25=False,auto_next_node=False)
    (out/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'unit':result['unit'],'rows':(len(rows),len(totals),len(final_bins)),'earliest':{k:v for k,v in earliest.items() if k.startswith(('grad_','formal_'))},'latest':{k:v for k,v in latest.items() if k.startswith(('grad_','formal_'))}},indent=2))
    return result

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--source-zip',type=Path,default=SOURCE);ap.add_argument('--out',type=Path,default=ROOT/'results');a=ap.parse_args();output(a.out,a.source_zip)
