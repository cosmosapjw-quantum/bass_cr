#!/usr/bin/env python3
"""Independent C21L raw-data/tensor/source-field check; zero ODE calls."""
import os
os.environ['PYTHONDONTWRITEBYTECODE']='1'
os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
import sys,copy,hashlib,json,math,csv
from unittest.mock import patch
import numpy as np
ROOT=Path('/workspace/scratch/10765dc22dcf')
C21L=ROOT/'bass_cr/research/cr_c21l_rei_pilot_20261021'
COMP=C21L/'component_split_20261021'
sys.path.insert(0,str(C21L))
import adapter
raw=C21L/'runs/pilot81'
result=COMP/'results_final_v4'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
with np.load(result/'components81.npz',allow_pickle=False) as z:
    arrays={k:z[k] for k in z.files}
rows=list(csv.DictReader((result/'endpoints_components81.csv').open()))
assert len(rows)==81 and len(arrays['case_ids'])==81
template=adapter.make_template(optimized=False)
maxerr={}
def compare(name,got,expected,atol=0.,rtol=2e-15):
    got=np.asarray(got);expected=np.asarray(expected)
    assert got.shape==expected.shape,(name,got.shape,expected.shape)
    np.testing.assert_allclose(got,expected,rtol=rtol,atol=atol,equal_nan=True,err_msg=name)
    valid=np.isfinite(got)&np.isfinite(expected)
    e=float(np.max(abs(got[valid]-expected[valid]))) if valid.any() else 0.
    maxerr[name]=max(maxerr.get(name,0.),e)

states=0
input_records=[]
with patch.object(adapter.CanonicalFVSpecies,'integrate',side_effect=AssertionError('ODE prohibited')):
    for i,case in enumerate(arrays['case_ids']):
        case=str(case)
        path=raw/'cases'/case/'history.npz'
        receipt=json.loads((path.parent/'RESULT.json').read_text())
        assert sha(path)==receipt['history_sha256']
        with np.load(path,allow_pickle=False) as z: h={k:z[k] for k in z.files}
        assert h['Y'].shape==(40,101) and h['Y'].dtype==np.float64
        assert rows[i]['case_id']==case
        p={x:h[key] for x,key in [('m','Pi_matter_J_m3'),('gamma','Pi_gamma_J_m3'),('nu','Pi_nu_J_m3')]}
        p['r']=p['gamma']+p['nu'];p['tot']=p['m']+p['r']
        for key in ('eta','a','H','s'):
            compare('raw_'+key,arrays[key][i],h[key],rtol=0.)
        sigma=np.zeros((101,3,3))
        for j,fac in enumerate((-1.,-1.,2.)):sigma[:,j,j]=fac*h['s']
        sigma_norm=np.sqrt(np.einsum('tij,tij->t',sigma,sigma))
        compare('Sigma_F',arrays['Sigma_F'][i],sigma_norm/h['H'])
        compare('S_signed_F',arrays['S_signed_F'][i],np.sign(h['s'])*sigma_norm/h['H'])
        compare('Sigma_half',arrays['Sigma_half'][i],np.sqrt(np.einsum('tij,tij->t',sigma,sigma)/2)/h['H'])
        tensors={}
        for sector in ('m','gamma','nu','r','tot'):
            t=np.zeros((101,3,3))
            for j,fac in enumerate((-1.,-1.,2.)):t[:,j,j]=fac*p[sector]
            tensors[sector]=t
            norm=np.sqrt(np.einsum('tij,tij->t',t,t))
            normalized=(8*math.pi*6.67430e-11/299792458.0**4)*norm/(h['H']/299792458.0)**2
            compare('tensor_'+sector,arrays['pi_tensor_diag_'+sector+'_J_m3'][i],np.diagonal(t,axis1=1,axis2=2),rtol=0.)
            compare('physical_norm_'+sector,arrays['pi_norm_F_'+sector+'_J_m3'][i],norm)
            compare('Pi_'+sector,arrays['Pi_'+sector+'_F'][i],normalized)
            compare('signed_'+sector,arrays['P_'+sector+'_signed_F'][i],np.sign(p[sector])*normalized)
            compare('half_'+sector,arrays['Pi_'+sector+'_half'][i],normalized/math.sqrt(2))
            compare('dp_'+sector,arrays['delta_p_'+sector+'_J_m3'][i],t[:,2,2]-t[:,0,0],rtol=0.)
            compare('work_'+sector,arrays['sigma_dot_pi_'+sector+'_J_m3_s'][i],np.einsum('tij,tij->t',sigma,t))
            compare('trace_'+sector,np.trace(t,axis1=1,axis2=2),np.zeros(101),rtol=0.)
            compare('endpoint_'+sector,np.array(float(rows[i]['Pi_'+sector+'_F_end'])),np.array(normalized[-1]))
        compare('tensor_rad_sum',tensors['r'],tensors['gamma']+tensors['nu'],rtol=0.)
        compare('tensor_tot_sum',tensors['tot'],tensors['m']+tensors['r'],rtol=0.)
        denom=abs(p['m'])+abs(p['r'])
        cancel=np.full(101,np.nan)
        valid=denom>0;cancel[valid]=1-abs(p['tot'][valid])/denom[valid]
        compare('cancellation',arrays['cancellation'][i],cancel,rtol=0.)
        assert np.array_equal(arrays['cancellation_defined'][i],valid)
        assert np.array_equal(arrays['opposing_signs'][i],p['m']*p['r']<0)
        assert np.nanmin(cancel)>=-4e-16 and np.nanmax(cancel)<=1+4e-16
        assert np.all(arrays['Pi_tot_F'][i]<=arrays['Pi_m_F'][i]+arrays['Pi_r_F'][i]+2e-18)
        mapping=receipt['mapping'];obj=copy.copy(template)
        obj.Sigma_ref=mapping['source_Sigma_ref'];obj.orientation=mapping['orientation']
        obj.k_gamma=mapping['k_gamma'];obj.k_nu=mapping['k_nu']
        for j in (0,50,100):
            d=obj.fields(float(h['eta'][j]),h['Y'][:,j])
            for key in ('a','b','s','H','Pi_gamma_J_m3','Pi_nu_J_m3','Pi_matter_J_m3','Pi_radiation_J_m3','Einstein_H2'):
                compare('source_field_'+key,np.asarray(h[key][j]),np.asarray(d[key]),rtol=0.)
            for key in ('E_gamma','N_gamma','E_nu','N_nu'):
                compare('source_field_'+key,h[key][j],d[key],rtol=0.)
            states+=1
        input_records.append({'case':case,'raw_sha256':sha(path)})

for entry in json.loads((result/'OUTPUT_MANIFEST.json').read_text())['files']:
    path=result/entry['path'];assert path.stat().st_size==entry['bytes'];assert sha(path)==entry['sha256']
assert json.loads((result/'OUTPUT_MANIFEST.json').read_text())['analyzer_sha256']==sha(COMP/'analyze_components.py')
out={'status':'PASS_SCOPED','reviewer':'independent theory_literature agent, not postprocessor implementer',
    'method':'full 3x3 tensor contractions and SI kappa/Hgeom construction independent of analyzer; direct original source fields from raw Y; no analyzer call',
    'scope':{'cases':81,'all_stored_times':8181,'original_field_reconstructed_states':states,'new_ODE_integrations':0},
    'source_validation':'all 9 parent manifest files verified via original adapter.verify_source',
    'source_files':adapter.verify_source()['files'],'analyzer_sha256':sha(COMP/'analyze_components.py'),
    'verifier_sha256':sha(COMP/'verify_components.py'),'review_script_sha256':sha(Path(__file__)),
    'output_npz_sha256':sha(result/'components81.npz'),'output_manifest_sha256':sha(result/'OUTPUT_MANIFEST.json'),
    'max_absolute_differences':maxerr,'raw_inputs':input_records,'global_error_bound':None,
    'findings':[],
    'visual_review':{'method':'direct view_image inspection of all 3 accepted PNGs',
       'files':['component_endpoints.png','signed_component_histories.png','norms_and_cancellation.png'],
       'status':'PASS_SCOPED',
       'checks':['heatmap labels signed P; common symmetric-log color scale across m,r,total',
           'nonuniform shear values explicitly labeled sampled rows, categorical row position',
           'history positive/negative branches visible and common limits within each row; no legend/curve overlap',
           'norm chart uses nonnegative Pi distinct from signed P and hollow total markers',
           'cancellation mask display Pi_m+Pi_r>1e-12 is explicitly labeled and raw array remains unchanged',
           'PNG labels and legends readable at inspected native rendering; no clipping'],
       'limits':['not a paper-size typography certification','PDF not independently rasterized; same matplotlib figure exports observed']},
    'claim_limits':['postprocessing and source-field reconstruction only; original ODE not rerun',
        'Hamiltonian is constructed algebraically and not an independent global error estimate',
        'fixed-A0 81 ensemble remains preliminary LRS collisionless z20-to-z4']}
dest=COMP/'REVIEW_COMPONENTS.json'
with dest.open('x') as f:json.dump(out,f,indent=2);f.write('\n')
print(json.dumps({'status':out['status'],'scope':out['scope'],'max_source_field_error':max(v for k,v in maxerr.items() if k.startswith('source_field_')),'review':str(dest)},indent=2))
