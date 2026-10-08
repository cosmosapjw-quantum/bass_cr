"""Read-only A1 review: independent beta-moment construction and 80-digit R8.

Imports none of the producer's numerical modules; never evaluates a cross kernel.
"""
from pathlib import Path
from fractions import Fraction as F
import argparse,hashlib,json,math,time
import numpy as np
import mpmath as mp

def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)

def main(a):
    out=Path(a.out);intake=Path(a.intake);context=json.loads(Path(a.context).read_text());checks=[]
    def check(name,value):
        checks.append({'name':name,'pass':bool(value)})
        if not value:raise AssertionError(name)
    for name,value in context['new_sources'].items():check('producer_source_'+name,h(Path(__file__).parent/name)==value)
    done=json.loads((out/'COMPLETED.json').read_text());result=json.loads((out/'RESULT.json').read_text());seal=json.loads((out/'S_ONLY_SEAL.json').read_text());cache=json.loads((out/'CACHE_RECORD.json').read_text())
    check('result_receipt',h(out/'RESULT.json')==done['result_sha256'])
    check('S_seal_binding',h(out/'S_ONLY_SEAL.json')==result['S_only_seal_sha256'])
    check('S_sample_binding',h(out/'S_ONLY_SAMPLES.npz')==seal['samples_sha256'])
    check('S_derivative_binding',h(out/'S_ONLY_DERIVATIVES.npz')==seal['derivatives_sha256'])
    check('intrinsic_cache_binding',h(out/'INTRINSIC.npz')==cache['intrinsic_npz_sha256'])
    check('seal_precedes_D',seal['epoch']<=result['first_D_read_epoch'] and seal['D_read_in_S_phase'] is False)
    src=intake/'payload/archive_base_2/runs_r4x/candidate_v1'
    meta=json.loads((src/'CANDIDATE.json').read_text())
    with np.load(src/'CANDIDATE.npz',allow_pickle=False) as f:e=f['edges'];ep=f['shared_endpoint_values'];q=f['bubble_coefficients']
    nm=len(ep);basis=[{(0,1):F(1)},{(1,0):F(1)},{(1,1):F(1)},{(2,1):F(1)},{(3,1):F(1)}]
    def integral(p,t):
        z=F(0)
        for (sa,ta),ca in p.items():
            for (sb,tb),cb in t.items():
                i,j=sa+sb,ta+tb;z+=ca*cb*F(math.factorial(i)*math.factorial(j),math.factorial(i+j+1))
        return z
    def deriv(p):
        out={}
        for (s,t),c in p.items():
            if s:out[s-1,t]=out.get((s-1,t),F(0))+s*c
            if t:out[s,t-1]=out.get((s,t-1),F(0))-t*c
        return out
    mats={'G':[[integral(x,y) for y in basis] for x in basis],'J':[[integral(x,deriv(y)) for y in basis] for x in basis],'T':[[integral(deriv(x),deriv(y)) for y in basis] for x in basis]}
    exact=json.loads((out/'GRAM_EXACT.json').read_text())['matrices_exact']
    reference={k:[[F(0) for _ in range(nm)] for _ in range(nm)] for k in mats}
    for c in range(len(e)-1):
        width=F(float(e[c+1]))-F(float(e[c]));rows=[[F(float(v)) for v in [ep[k,c],ep[k,c+1],*q[k,c]]] for k in range(nm)]
        for name,mm in mats.items():
            scale=width if name=='G' else (1/width if name=='T' else F(1))
            for i in range(nm):
                for j in range(nm):reference[name][i][j]+=scale*sum((rows[i][k]*rows[j][l]*mm[k][l] for k in range(5) for l in range(5)),F(0))
    for name,values in reference.items():
        for i in range(nm):
            for j in range(nm):check(f'independent_beta_{name}_{i}_{j}',values[i][j]==F(exact[name][i][j]))
    with np.load(out/'INTRINSIC.npz',allow_pickle=False) as f:cache_arrays={k:f[k] for k in f.files}
    with np.load(out/'S_ONLY_SAMPLES.npz',allow_pickle=False) as f:S={k:f[k] for k in f.files}
    with np.load(out/'S_ONLY_DERIVATIVES.npz',allow_pickle=False) as f:derivatives={k:f[k] for k in f.files}
    rows={};assembled=[];max_boost_reassembly_difference=0.
    for b in seal['sample_bindings']:
        key=b['key'];parent=intake/b['source_path'];new=out/'reassembled'/key
        check('raw_identity_'+key,h(parent/'RAW.npz')==b['raw_sha256'])
        nrec=json.loads((new/'RESULT.json').read_text());check('new_full_identity_'+key,h(new/'FULL.npz')==nrec['new_full_sha256'])
        with np.load(parent/'RAW.npz',allow_pickle=False) as f:raw={k:f[k] for k in f.files}
        with np.load(parent/'FULL.npz',allow_pickle=False) as f:old={k:f[k] for k in f.files}
        with np.load(new/'FULL.npz',allow_pickle=False) as f:n={k:f[k] for k in f.files}
        for k in ('S','H','D'):
            check('raw_'+k+'_tp_'+key,np.array_equal(n[k][:9,9:],raw[k+'_tp']))
            check('raw_'+k+'_pt_'+key,np.array_equal(n[k][9:,:9],raw[k+'_pt']))
        for center,label in enumerate(('T','P')):
            check('intrinsic_S_'+label+'_'+key,np.array_equal(n[label+'__S'],cache_arrays['S']))
            check('saved_V_'+label+'_'+key,np.array_equal(n[label+'__V_other'],old[label+'__V_other']))
            v=np.array(b['geometry']['trajectory']['velocities'][center]);av=sum((v[j]*cache_arrays['A'][j] for j in range(3)),np.zeros((9,9),complex));vv=sum(float(x)**2 for x in v)
            expectedH=cache_arrays['H0']+old[label+'__V_other']+.5j*(av.conj().T-av)+.5*vv*cache_arrays['S'];expectedD=-av-.5j*vv*cache_arrays['S']
            for field,expected in [('H',expectedH),('D',expectedD)]:
                error=float(np.max(abs(n[label+'__'+field]-expected)));max_boost_reassembly_difference=max(max_boost_reassembly_difference,error);check('consistent_'+field+'_'+label+'_'+key,error<=2e-15)
        check('sealed_S_'+key,np.array_equal(S[key],n['S']))
        task=nrec['task']
        if task['moment_backend']=='fortran':rows[(task['order'],task['inner_phase_budget'],task['z_a0'])]=(key,n)
    mp.mp.dps=80;weights=[F(-1,2835),F(84,2835),F(-1344,2835),F(4096,2835)];hs=[2.**(-k) for k in range(6,11)];velocity=seal['sample_bindings'][0]['geometry']['speed_a0_per_ta'];mpreal=lambda x:mp.mpf(F(float(x)).numerator)/F(float(x)).denominator
    maximum=0.;residuals={};win_diffs={};review_derivatives={}
    for rule in [(40,24),(48,24),(48,12)]:
        label=f'q{rule[0]}_beta{rule[1]}';dd=[]
        for win in (0,1):
            values=[]
            for w,hv in zip(weights,hs[win:win+4]):
                minus=S[rows[(*rule,-32.-hv)][0]];plus=S[rows[(*rule,-32.+hv)][0]]
                values.append((mp.mpf(w.numerator)/w.denominator*mpreal(velocity)/(2*mpreal(hv)),minus,plus))
            arr=np.empty((18,18),complex)
            for ij in np.ndindex(arr.shape):
                re=mp.fsum(co*(mpreal(p[ij].real)-mpreal(m[ij].real)) for co,m,p in values);im=mp.fsum(co*(mpreal(p[ij].imag)-mpreal(m[ij].imag)) for co,m,p in values);arr[ij]=complex(float(re),float(im))
            error=float(np.linalg.norm(arr-derivatives[f'{label}__w{win}__nominal'],'fro'));maximum=max(maximum,error);check(f'independent_R8_{label}_{win}',error<=1e-16)
            d=rows[(*rule,-32.)][1]['D'];res=arr-d-d.conj().T;rr={'spectral':float(np.linalg.norm(res,2)),'frobenius':float(np.linalg.norm(res,'fro')),'elementwise_max':float(np.max(abs(res)))};residuals[f'{label}_w{win}']=rr;check('independent_residual_'+label+str(win),max(rr.values())<=1e-12);dd.append(arr)
        wd=float(np.linalg.norm(dd[0]-dd[1],'fro'));win_diffs[label]=wd;check('independent_window_'+label,wd<=1e-12)
    review={'schema':'R4AB_INDEPENDENT_REVIEW_V1','status':'PASS','checks':len(checks),'check_results':checks,'reviewer_source_sha256':h(__file__),'independent_beta_moment_entries':75,'high_precision_digits':80,'high_precision_derivative_frobenius_max_difference':maximum,'boost_formula_reassembly_max_difference':max_boost_reassembly_difference,'independent_residuals':residuals,'independent_window_differences':win_diffs,'new_cross_queries':0,'scope':'Independent algorithms in same session/environment; not a separate agent, human or full quadrature certificate','producer_result_sha256':h(out/'RESULT.json')}
    with open(a.report,'x') as f:json.dump(review,f,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps({k:review[k] for k in ['status','checks','independent_beta_moment_entries','high_precision_derivative_frobenius_max_difference','boost_formula_reassembly_max_difference']},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name in ('out','intake','context','report'):p.add_argument('--'+name,required=True)
    main(p.parse_args())
