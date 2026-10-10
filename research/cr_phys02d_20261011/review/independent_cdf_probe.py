import os
for key in ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS'): os.environ[key]='1'
import importlib.util,json,pathlib
p=pathlib.Path('/workspace/scratch/584ff08e1634/bass_cr_work/research/cr_phys02d_20261011/src/pulse_response.py')
spec=importlib.util.spec_from_file_location('reviewed_cdf',p);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
# Exact positive measure: 5/32 at tau/T=1/5, 27/32 at 2.
# R=1/8, S=1/10; this is an independent analytic measure, not a transport run.
u=[i/16 for i in range(17)];p_weight=5/32
valid=[p_weight if x>=1/5 else 0. for x in u]
a=mod.check_saved_cdf_bounds(u,valid,1/8,1/10,{'independent_exact_measure':'5/32 delta_1/5 + 27/32 delta_2'})
assert a['pass']
# Still a monotone 0..1 CDF, but it violates the required F(1/2)>=3/40.
invalid=[0. if x<1/5 else (.05 if x<=.5 else p_weight) for x in u]
assert all(0<=x<=1 for x in invalid) and all(x<=y for x,y in zip(invalid,invalid[1:]))
b=mod.check_saved_cdf_bounds(u,invalid,1/8,1/10,{'synthetic_violation':'monotone bounded CDF with F(1/2)=1/20'})
half=next(x for x in b['checks'] if x['u']==.5)
assert not b['pass'] and not half['pass'] and abs(half['lower']-3/40)<1e-15
print(json.dumps({'status':'PASS_INDEPENDENT_POSTPROCESS_PROBE','valid_exact_measure':a,'monotone_range_valid_dual_violation':b,'physical_G_builds':0,'physical_transport_calls':0,'candidate_expm_calls':0,'whole_endpoint_reevaluations':0}))
