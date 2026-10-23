"""Revision3 input admission only: one valid assembly plus invalid new inputs."""
from pathlib import Path
from copy import deepcopy
import json,math,os,resource,sys,time
BASE=Path(__file__).resolve().parent
RUN=Path(sys.argv[1]).resolve()
if os.sched_getaffinity(0)!={4}:raise RuntimeError('Reviewer CPU4 required')
THREADS=('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','BLIS_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS')
if any(os.environ.get(k)!='1' for k in THREADS):raise RuntimeError('Native threads must be1')
sys.path.insert(0,str(RUN/'source_snapshot'))
from primary_source_assembly import assemble,API_GUARD_REVISION
START=time.perf_counter()
def write(name,obj):
    with (RUN/name).open('x') as f:json.dump(obj,f,indent=2,allow_nan=False);f.write('\n')

all_cases=json.loads((RUN/'source_snapshot/provider_cases.json').read_text())
all_baselines=json.loads((RUN/'source_snapshot/saved_v2_assemblies.json').read_text())
baseline=all_baselines[0]
cases=[x for x in all_cases if x['redshift']==baseline['redshift']]
population=baseline['populations_per_reference']
valid=assemble(cases,population)
preserved={key:valid[key]==value for key,value in baseline.items() if key!='inventory_label'}
write('ONE_VALID_CHANGED_PATH.json',{'original_baseline':baseline,'revision3_result':valid,'every_existing_field_identical':all(preserved.values()),'field_comparisons':preserved})

mutations=[
    ('negative_redshift','redshift',-1.),
    ('nan_redshift','redshift',math.nan),
    ('infinite_redshift','redshift',math.inf),
    ('absent_redshift','redshift',None),
    ('bool_redshift','redshift',True),
    ('other_H_threshold_13p6058','threshold_eV',13.6058),
    ('zero_threshold','threshold_eV',0.),
    ('absent_threshold','threshold_eV',None),
    ('support_upper_above_domain','photon_support_eV',[13.6,50001.]),
    ('different_finite_support','photon_support_eV',[13.6,49999.]),
    ('support_lower_not_threshold','photon_support_eV',[13.61,50000.]),
    ('negative_support','photon_support_eV',[-1.,50000.]),
    ('infinite_support','photon_support_eV',[13.6,math.inf]),
    ('absent_support','photon_support_eV',None),
    ('nonpair_support','photon_support_eV',[13.6,14.,50000.]),
]
checks=[]
for name,key,value in mutations:
    new=deepcopy(cases);new[0][key]=value
    try:assemble(new,population)
    except (ValueError,TypeError) as exc:checks.append({'guard':name,'result':'REJECTED','exception':type(exc).__name__,'message':str(exc)})
    else:checks.append({'guard':name,'result':'FAIL_ACCEPTED'})
for channel,bad_threshold in [('HeI',24.587),('HeII',54.4)]:
    new=deepcopy(cases);next(x for x in new if x['channel']==channel)['threshold_eV']=bad_threshold
    try:assemble(new,population)
    except (ValueError,TypeError) as exc:checks.append({'guard':channel+'_threshold_identity','result':'REJECTED','exception':type(exc).__name__,'message':str(exc)})
    else:checks.append({'guard':channel+'_threshold_identity','result':'FAIL_ACCEPTED'})
write('NEW_INPUT_GUARDS.json',checks)
result={'schema':'C23B_ASSEMBLY_GUARD_REVISION3_VERIFICATION_V1','status':'PASS_SCOPED' if all(preserved.values()) and all(x['result']=='REJECTED' for x in checks) and API_GUARD_REVISION==3 else 'FAIL','api_guard_revision':API_GUARD_REVISION,'valid_changed_path_assemblies':1,'unchanged_source_assembly_reexecutions':0,'all_existing_valid_result_fields_identical':all(preserved.values()),'new_invalid_input_guards':len(checks),'all_new_invalid_inputs_rejected':all(x['result']=='REJECTED' for x in checks),'old_complete_campaign_reruns':0,'old_boost_FS_suites_rerun':False,'new_ODE_calls':0,'worker_cpu':4,'native_threads_per_worker':1,'wall_s':time.perf_counter()-START,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'EXECUTION':'NEW_INPUT_GUARDS_AND_ONE_CHANGED_VALID_PATH_COMPLETE_SCOPED','PUBLICATION':'PARENT_PENDING','BACKUP':'PARENT_PENDING','DAG':'v2 scientificresult/sourceidentity retained -> revision3 supplier-domain guards -> targeted pass; physical21state/thermal closure remainsopen','global_error_bound':None}
write('COMPLETE.json',result)
print(json.dumps(result))
