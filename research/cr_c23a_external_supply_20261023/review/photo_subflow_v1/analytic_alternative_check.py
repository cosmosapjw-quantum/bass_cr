"""Check the parent's proposed positive K20 decomposition, independently.

This validates a mathematical replacement candidate only. It does not alter,
approve or execute a new production implementation of photo_subflow.py.
"""
import os
for k in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS",
          "BLIS_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ[k]="1"
os.sched_setaffinity(0,{4})
import math,json,time,sys,importlib.util
from pathlib import Path
from datetime import datetime,timezone
import mpmath as mp

mp.mp.dps=80
R=Path(__file__).resolve().parent
start=time.perf_counter()
pairs=[(0.,0.),(0.,1.),(1.,0.),(1e-14,1e-14),(1e-14,1e6),
       (1e6,1e-14),(1.,1.),(1.,math.nextafter(1.,2.)),
       (1e-6,1.00000001e-6),(1e-2,10.),(10.,1e-2),
       (1e6,1e6),(.988,29700.),(.1,20.),(1e6,1e-8)]
rows=[]
for aa,bb in pairs:
    a,b=mp.mpf(aa),mp.mpf(bb)
    m,d=min(a,b),abs(a-b)
    F=-mp.expm1(-m)-m*mp.exp(-m)
    G=1+mp.expm1(-d)/d if d else mp.mpf(0)
    candidate=F+m*mp.exp(-m)*G
    M=mp.matrix([[-a,0,0],[a,-b,0],[0,b,0]])
    reference=mp.expm(M)[2,0]
    rows.append({'a':aa,'b':bb,'candidate_80digit':mp.nstr(candidate,35),
                 'matrix_reference_80digit':mp.nstr(reference,35),
                 'abs_error':mp.nstr(abs(candidate-reference),12),
                 'relative_error':mp.nstr(abs((candidate-reference)/reference),12) if reference else '0',
                 'nonnegative':bool(candidate>=0)})

# The first 60 positive terms are sufficient to compare the stated series on
# the intended small-argument interval [0,1]; truncation remains explicit.
series=[]
for xx in (0.,1e-14,1e-8,1e-3,.1,1.):
    x=mp.mpf(xx)
    F=-mp.expm1(-x)-x*mp.exp(-x)
    Fsum=mp.exp(-x)*x*x*mp.fsum(x**k/mp.factorial(k+2) for k in range(60))
    G=1+mp.expm1(-x)/x if x else mp.mpf(0)
    Gsum=mp.exp(-x)*mp.fsum(n*x**n/mp.factorial(n+1) for n in range(1,61))
    series.append({'x':xx,'F_series_error':mp.nstr(abs(F-Fsum),12),
                   'G_series_error':mp.nstr(abs(G-Gsum),12),
                   'terms_positive':True,'terms':60})

spec=importlib.util.spec_from_file_location('photo_v1_zero_duration',R/'photo_subflow_snapshot.py')
module=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=module
spec.loader.exec_module(module)
zero=module.advance({'HI':.1,'HII':.3,'HeI':.2,'HeII':.15,'HeIII':.25},2.,0.,
                    {'HI':.3,'HeI':.5,'HeII':.7},{'HI':1.,'HeI':2.,'HeII':3.},
                    {'HI':13.6,'HeI':24.6,'HeII':54.4})
result={'status':'PASS_SCOPED','meaning':'algebra and a finite precision numerical spot-check; new production code not reviewed',
        'source_v1_status':'FAIL preserved in EXECUTION.json',
        'mpmath_dps':80,'pairs':rows,'small_argument_series':series,
        'extra_v1_boundary_check':{'positive_rates_zero_duration':{'populations':zero.populations,
                                  'events':zero.events,'thermal_energy_ev':zero.thermal_energy_ev,
                                  'pass':zero.populations=={'HI':.1,'HII':.3,'HeI':.2,'HeII':.15,'HeIII':.25}
                                  and all(v==0 for v in zero.events.values()) and zero.thermal_energy_ev==2.}},
        'cpu_affinity':sorted(os.sched_getaffinity(0)),'native_threads':1,'new_ODE':0,
        'wall_s':time.perf_counter()-start,'created_utc':datetime.now(timezone.utc).isoformat()}
assert all(mp.mpf(r['abs_error'])<mp.mpf('1e-60') and r['nonnegative'] for r in rows)
assert result['extra_v1_boundary_check']['positive_rates_zero_duration']['pass']
with (R/'ANALYTIC_ALTERNATIVE_CHECK.json').open('x') as f:
    json.dump(result,f,indent=2,allow_nan=False)
    f.write('\n')
print(json.dumps({'status':result['status'],'pairs':len(rows),'series_points':len(series),
                  'max_abs_error':max(float(r['abs_error']) for r in rows),
                  'zero_duration_pass':True,'wall_s':result['wall_s']},indent=2))
