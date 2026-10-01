"""Relative-residual fits to frozen static rho; never a continuum certificate.

All models minimize sum_i ((prediction_i-rho_i)/rho_i)^2. Linear
models use column-scaled least squares; M2 profiles its amplitude and minimizes
one bounded exponent. Bounds [0,8] are a declared exploration domain only.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy.optimize import minimize_scalar

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
DEFAULT_SAMPLES=REPO/'research/foundation_rebuild/ncp_shared_research_20260928/r4p0a_b0_static_tail_executor_20260930/execution_evidence/R4P0-B0-STATIC-TAIL-20260930-A1/STATIC_TAIL_SNAPSHOTS.csv'
MODELS=('M1','M2','M3','M4')
CANDIDATES=(40,48,64,80,96,128,160,192)
OFF_GRID=(36,44,56,72,112,144)
RREF=24.

def fit_model(model,radii,rates):
    r=np.asarray(radii,float);y=np.asarray(rates,float)
    if r.ndim!=1 or y.shape!=r.shape or not np.isfinite(r).all() or not np.isfinite(y).all() or np.any(r<=0) or np.any(y<=0):
        raise ValueError('finite positive same-length radius and rho vectors required')
    if model not in MODELS:raise ValueError('unknown model')
    k={'M1':1,'M2':2,'M3':2,'M4':3}[model]
    if len(np.unique(r))<k:raise ValueError('insufficient distinct radii')
    result={'model':model,'parameter_count':k,'residual_degrees_of_freedom':len(r)-k,
            'reference_radius_a0':RREF,'training_radii_a0':r.tolist(),
            'objective':'sum_squared_relative_rho_residuals','uncertainty_model':'NONE_EMPIRICAL_FIT'}
    if model=='M2':
        def profile(p):
            x=(RREF/r)**p/y
            a=float(x.sum()/(x@x))
            return a,float(np.sum((a*x-1)**2))
        opt=minimize_scalar(lambda p:profile(p)[1],bounds=(0.,8.),method='bounded',options={'xatol':1e-13})
        if not opt.success:raise ArithmeticError('exponent profile failed')
        p=float(opt.x);a,_=profile(p)
        result.update(amplitude_at_reference=a,exponent=p,C=a*RREF**p,exponent_search_domain=[0.,8.],
                      parameter_units=['atomic_time^-1 at reference radius','dimensionless exponent'],
                      scaled_design_condition=None)
    else:
        X=np.array([(RREF/r)**(2+j) for j in range(k)]).T
        A=X/y[:,None];scale=np.linalg.norm(A,axis=0)
        scaled=A/scale
        coeff,resid,rank,sv=np.linalg.lstsq(scaled,np.ones(len(y)),rcond=None)
        if rank<k:raise ArithmeticError('rank-deficient fit')
        coeff/=scale
        result.update(scaled_coefficients=coeff.tolist(),
                      C_coefficients={f'C{2+j}':float(coeff[j]*RREF**(2+j)) for j in range(k)},
                      scaled_design_condition=float(sv.max()/sv.min()),
                      parameter_units=[f'a0^{2+j}/atomic_time' for j in range(k)])
        if model=='M3':result['a_a0']=None if coeff[0]==0 else float(RREF*coeff[1]/coeff[0])
    pred=predict(result,r);relative=pred/y-1
    result.update(prediction=pred.tolist(),relative_training_residual=relative.tolist(),
                  max_relative_training_residual=float(np.max(abs(relative))),
                  rms_relative_training_residual=float(np.sqrt(np.mean(relative**2))))
    return result

def predict(fit,radii):
    r=np.asarray(radii,float)
    if fit['model']=='M2':return fit['amplitude_at_reference']*(RREF/r)**fit['exponent']
    return sum(a*(RREF/r)**(2+j) for j,a in enumerate(fit['scaled_coefficients']))

def load_samples(path=DEFAULT_SAMPLES):
    with Path(path).open() as f:
        return [{key:float(row[key]) for key in ('z_a0','R_a0','rho_per_atomic_time')}
                for row in csv.DictReader(f)]

def leave_one_out(model,r,y):
    rows=[]
    for i in range(len(r)):
        ix=np.arange(len(r))!=i
        fit=fit_model(model,r[ix],y[ix]);pred=float(predict(fit,r[i]))
        rows.append({'held_out_radius_a0':float(r[i]),'observed':float(y[i]),'predicted':pred,
                     'relative_residual':pred/y[i]-1})
    return {'rows':rows,'max_abs_relative_residual':max(abs(a['relative_residual']) for a in rows)}

def branch_switch_example(radii):
    r=np.asarray(radii,float)
    # W=[[0,B],[B,0]], B=diag(R^-2,3R^-3), S=I: eigenvalues ±diagonal(B).
    return np.maximum(r**-2,3*r**-3)

def analyze(rows):
    groups={s:sorted((a for a in rows if a['z_a0']*sign>0),key=lambda a:abs(a['z_a0']))
            for s,sign in [('incoming',-1),('outgoing',1)]}
    if any(len(a)!=4 for a in groups.values()):raise ValueError('frozen analysis expects exactly four radii per sign')
    signed_fits={};loo={};outer={};slopes={};scaled={};predictions={}
    for s,a in groups.items():
        r=np.array([v['R_a0'] for v in a]);y=np.array([v['rho_per_atomic_time'] for v in a])
        signed_fits[s]={m:fit_model(m,r,y) for m in MODELS}
        loo[s]={m:leave_one_out(m,r,y) for m in MODELS}
        outer[s]={'drop_abs_z_16':{m:fit_model(m,r[1:],y[1:]) for m in MODELS},
                  'outermost_two_M2':fit_model('M2',r[-2:],y[-2:])}
        slopes[s]=(-np.diff(np.log(y))/np.diff(np.log(r))).tolist()
        scaled[s]=(y*r**2).tolist()
        predictions[s]=[]
        for z in sorted(CANDIDATES+OFF_GRID):
            radius=float(np.hypot(z,2)); values={m:float(predict(f,radius)) for m,f in signed_fits[s].items()}
            v=np.array(list(values.values()));pairs=[abs(v[i]-v[j])/((v[i]+v[j])/2) for i in range(4) for j in range(i)]
            predictions[s].append({'abs_z_a0':z,'R_a0':radius,'off_grid':z in OFF_GRID,
                                    'model_predictions':values,'relative_range_over_median':float(np.ptp(v)/np.median(v)),
                                    'minimum_pairwise_relative_separation':float(min(pairs))})
    pair=[]
    for a,b in zip(groups['incoming'],groups['outgoing']):
        if abs(a['z_a0'])!=b['z_a0']:raise ValueError('unmatched signed radii')
        pair.append(abs(a['rho_per_atomic_time']-b['rho_per_atomic_time'])/max(a['rho_per_atomic_time'],b['rho_per_atomic_time']))
    return {'schema':'BASS_CR_G03_OFFLINE_MODELS_V1','sample_count':len(rows),
            'unique_absolute_z_count':len({abs(a['z_a0']) for a in rows}),'samples':rows,
            'signed_symmetry_max_relative_difference':max(pair),'signed_fits':signed_fits,
            'leave_one_radius_out':loo,'outer_sensitivity':outer,'adjacent_log_slopes':slopes,
            'rho_times_R_squared':scaled,'candidate_predictions':predictions,
            'continuous_certificate':False,'confidence_intervals':None,
            'statistical_independence_claim':False,'new_native_operator_evaluations':0}

def evaluate_return(baseline,returned):
    """Score externally provenance-verified ±48 returns before fitting them.

    This function checks numerical scope, not authorization/source receipts.
    It cannot promote a scientific gate or authorize a following batch.
    """
    rows=returned.get('samples',[])
    if len(rows)!=2 or {a.get('z_a0') for a in rows}!={-48.,48.}:
        raise ValueError('exact signed48 pair required')
    for a in rows:
        vals=[a.get(k,float('nan')) for k in ('R_a0','rho_per_atomic_time','adjacent_relative_rho_discrepancy')]
        if (a.get('qualified') is not True or not np.isfinite(vals).all()
                or vals[1]<=0 or vals[2]<0 or not np.isclose(vals[0],np.hypot(48,2),rtol=1e-13,atol=0)):
            raise ValueError('qualified finite scoped return and observed discrepancy required')
    frozen=analyze(baseline);output={}
    for a in rows:
        s='incoming' if a['z_a0']<0 else 'outgoing';r=a['R_a0'];y=a['rho_per_atomic_time']
        threshold=max(.02,10*a['adjacent_relative_rho_discrepancy'])
        all_scores={};outer_scores={}
        for target,fitset in [(all_scores,frozen['signed_fits'][s]),
                              (outer_scores,frozen['outer_sensitivity'][s]['drop_abs_z_16'])]:
            for model,fit in fitset.items():
                pred=float(predict(fit,r));relative=abs(pred/y-1)
                target[model]={'frozen_prediction':pred,'relative_residual':relative,
                               'empirical_screen_pass':relative<=threshold}
        previous=sorted((v for v in baseline if v['z_a0']*a['z_a0']>0 and abs(v['z_a0'])>=20),key=lambda v:abs(v['z_a0']))
        rs=[v['R_a0'] for v in previous]+[r];ys=[v['rho_per_atomic_time'] for v in previous]+[y]
        refit={m:fit_model(m,rs,ys) for m in MODELS}
        p0=frozen['outer_sensitivity'][s]['drop_abs_z_16']['M2']['exponent'];p1=refit['M2']['exponent']
        stable=abs(p1-2)<=.05 and abs(p1-p0)<=.05
        # Recommends a heldout pair only when the simple near-R^-2 class passes.
        supportive=stable and outer_scores['M1']['empirical_screen_pass']
        output[s]={'observed':a,'empirical_screen_threshold':threshold,
                   'all_four_frozen_holdout':all_scores,'outer_three_frozen_holdout':outer_scores,
                   'outer_refit':refit,'exponent_before':p0,'exponent_after':p1,
                   'exponent_stability_screen_pass':stable,
                   'recommended_next_pair_abs_z_a0':44 if supportive else 64,
                   'diagnostics_required_before_followup':not supportive,
                   'next_pair_frozen_predictions':{m:float(predict(f,np.hypot(44 if supportive else 64,2))) for m,f in refit.items()}}
    return {'schema':'BASS_CR_G03_RETURN_OFFLINE_ANALYSIS_V1','per_sign':output,
            'source_receipt_verification':'REQUIRED_EXTERNALLY_NOT_PERFORMED_BY_THIS_ANALYZER',
            'execution_authorized':False,'continuous_certificate':False,'new_native_calls':0,
            'native_followup_rule':'Both signs must support a common decision; mismatch requires diagnosis, never automatic execution.'}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--input',type=Path,default=DEFAULT_SAMPLES)
    parser.add_argument('--output',type=Path,default=HERE/'ASYMPTOTIC_MODELS.json')
    parser.add_argument('--return-json',type=Path,help='Already provenance-verified signed48 return for frozen holdout scoring')
    args=parser.parse_args()
    report=(evaluate_return(load_samples(args.input),json.loads(args.return_json.read_text()))
            if args.return_json else analyze(load_samples(args.input)))
    report['source_csv']={'path':str(args.input.relative_to(REPO)) if args.input.is_relative_to(REPO) else str(args.input),
                          'sha256':hashlib.sha256(args.input.read_bytes()).hexdigest()}
    args.output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'output':str(args.output),'samples':report.get('sample_count',2),'native_calls':0}))

if __name__=='__main__':main()
