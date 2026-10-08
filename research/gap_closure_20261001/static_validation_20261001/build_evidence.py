"""Reproduce only local audit evidence; never evaluates a physical operator."""
import csv
import json
import shutil
import sys
from pathlib import Path
import numpy as np
import scipy
import static_validation as sv

HERE=Path(__file__).resolve().parent
ROOT=sv.REPO.parent


def write(name,value):
    (HERE/name).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')


def main():
    plan=sv.make_plan(sv.load_source_plan())
    restoration=ROOT/'restored_static_A1'
    restore_receipt=ROOT/'evidence/STATIC_A1_RESTORE.json'
    recovered_plan=restoration/'EXECUTION_PREPARATION/source'/sv.SOURCE_DIR.relative_to(sv.REPO)/'BOUND_B0_TAIL_QUERY_PLAN.json'
    assert json.loads(recovered_plan.read_text())==sv.load_source_plan()
    outdir=HERE/'reused_snapshots';outdir.mkdir(exist_ok=True)
    desc=[]
    for jp in sorted((restoration/'SCIENCE_RETURN/runtime_queries').glob('*.json')):
        rec=json.loads(jp.read_text());z=float.fromhex(rec['time_hex'])*plan['identity']['velocity_au']
        if z not in sv.CENTERS:continue
        assert rec['context_id']==plan['source_plan_parent_context']
        pp=jp.with_suffix('.npz')
        assert sv.sha(pp)==rec['payload_sha256']
        shutil.copyfile(jp,outdir/jp.name);shutil.copyfile(pp,outdir/pp.name)
        desc.append({'z_a0':z,'z_hex':float(z).hex(),'time_hex':rec['time_hex'],
          'identity':plan['identity'],'units':sv.UNITS,'record':'reused_snapshots/'+jp.name,
          'payload':'reused_snapshots/'+pp.name,'record_sha256':sv.sha(jp),
          'binding_provenance':{'source_plan_sha256':sv.sha(recovered_plan),
             'restoration_receipt_sha256':sv.sha(restore_receipt),
             'original_query_path':str(jp.relative_to(ROOT)),
             'level':'HASH_VERIFIED_SAVED_PHYSICAL_OPERATOR_ONLY_NO_STATE'}})
    manifest={'schema':'BASS_G02_SAVED_MANIFEST_V1','identity':plan['identity'],'snapshots':desc}
    checked=sv.verify_manifest(HERE,manifest,plan)
    finalplan=sv.make_plan(sv.load_source_plan(),checked)
    write('REUSE_MANIFEST.json',manifest);write('E_SDOT_FD_EXECUTION_CONTRACT.json',finalplan)
    observed=sv.analyze(manifest,HERE,finalplan)
    v=plan['identity']['velocity_au'];z=1.1
    S=lambda x:np.diag([2+.1*np.sin(x),3+.2*np.cos(x)])
    D=.5*v*np.diag([.1*np.cos(z),-.2*np.sin(z)])
    ladder=[(h,S(z-h),S(z+h)) for h in sv.H_LADDER]
    correct=sv.compare_ladder(D,ladder,v,relative_target=1e-3)
    wrong=sv.compare_ladder(1.1*D,ladder,v,relative_target=1e-3)
    examples={
      'correlated_bias':sv.three_level([np.array([5+1e-10]),np.array([5+2.5e-11]),np.array([5+6.25e-12])],resolutions=[1,.5,.25]),
      'plateau':sv.three_level([np.array([5.])]*3,resolutions=[1,.5,.25]),
      'preasymptotic_false_agreement':sv.three_level([np.array([1.]),np.array([1+1e-12]),np.array([2.])],resolutions=[1,.5,.25]),
      'alternating_nonmonotone':sv.three_level([np.array([1.1]),np.array([.975]),np.array([1.00625])],resolutions=[1,.5,.25],adjacent_tolerance=.2),
      'roundoff_floor':sv.three_level([np.array([1.]),np.array([1.+np.finfo(float).eps]),np.array([1.])],resolutions=[1,.5,.25])}
    write('STATIC_QUALIFICATION_RESULTS.json',{'status':'INTERNAL_RESOLUTION_CONSISTENCY_NOT_RIGOROUS_ERROR_BOUND',
          'counterexamples':examples,'true_value_correlated_bias_and_plateau':1,
          'physical_three_level_results':'UNAVAILABLE_ONLY_TWO_RESOLUTIONS_SAVED',
          'existing_qualification_changed':False,'native_calls':0})
    pins={}
    files=[sv.SOURCE_DIR/'BOUND_B0_TAIL_QUERY_PLAN.json',sv.SOURCE_DIR/'DEPENDENCY_CLOSURE.json',
      sv.REPO/'research/foundation_rebuild/tp2a_analytic_pruning_20260926/code/assemble.py',
      sv.REPO/'research/foundation_rebuild/tp2a_analytic_pruning_20260926/code/exact_cross.py',
      sv.REPO/'research/foundation_rebuild/tp2a_analytic_pruning_20260926/code/moment_kernel.cpp',
      sv.REPO/'research/foundation_rebuild/full_operator_20260926/full_operator.py',
      sv.REPO/'research/foundation_rebuild/tp2d_runtime_self_qualified_transport_20260927/qualified_provider.py',
      sv.REPO/'research/foundation_rebuild/tp2d_runtime_self_qualified_transport_20260927/transport_policy.py',
      sv.REPO/'research/foundation_rebuild/ncp_shared_research_20260928/r4f_parallel_migration_20260929/worker_runtime.py']
    for f in files:pins[str(f.relative_to(sv.REPO))]=sv.sha(f)
    write('SOURCE_PINS.json',{'source_head':json.loads((ROOT/'evidence/LOCAL_SOURCE_BLOB_VERIFICATION.json').read_text())['source_head'],
        'research_theory_anchor':'432010f2afd5305ca63933056f50584c01e4e524','files_sha256':pins,
        'native_source_sha256':plan['identity']['analytic_source_sha256'],
        'native_library_sha256':plan['identity']['analytic_library_sha256'],'native_loaded':False})
    results={'gap_id':'G02','database_gap_id':'REPORT_GAP_02',
       'status_before':'REPORTED_RECOMMENDATION_NOT_VALIDATED',
       'status_after':'BLOCKED_RESOURCE_POLICY_BLOCKER','physical_G02_closed':False,
       'evidence_status':['DERIVED','NUMERICALLY_CHECKED','IMPLEMENTATION_VERIFIED','BLOCKED'],
       'implemented_scope':'Offline FD postprocessor, exact plan/reuse validator, qualification diagnostic and fresh-scope native admission/worker/supervisor/return adapter',
       'native_execution_code_ready':True,
       'blocker':{'class':'RESOURCE_POLICY_BLOCKER','claim':'Physical independently differentiated S satisfies D+D† across all signed points with resolved h convergence',
          'first_missing_artifact':'Saved qualified S(z±h), all64 shifts, plus centerD at±12',
          'minimum_repair':f"Prepare a live unapproved proposal with executor/prepare_fd_authority.py from the final published clean commit, obtain fresh exact approval, then executor/supervise_fd.py executes the {finalplan['new_query_count']}-query static return; cap726, no transport or rho extension",
          'unverified':'Actual physical FD convergence and residual acceptance'},
       'current_physical_saved_data':observed,'synthetic_correct_D':correct,'synthetic_wrong_D':wrong,
       'synthetic_threshold_note':'1e-3 proves comparator/order detection; physical predeclared target stays1e-6 unchanged.',
       'new_external_runs':0,'new_native_calls':0,'authorization_consumed':0,
       'verified_reused_centers':sorted(float.fromhex(k) for k in checked),
       'new_queries':finalplan['new_query_count'],'raw_attempt_ceiling':finalplan['max_raw_operator_evaluations'],
       'runtime':{'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__},
       'TDD':{'red':{'command':'python -m unittest discover -s research/gap_closure_20261001/static_validation_20261001 -p test_static_validation.py -v','exit':1,'cause':'ModuleNotFoundError: static_validation (new behavior absent)'},
          'green':{'command':'python -m unittest discover -s research/gap_closure_20261001/static_validation_20261001 -p test_static_validation.py -v','exit':0,'tests':8}},
       'claim_gate_change':'G02 physical claim remains open; no capture/window/tail promotion'}
    write('E_SDOT_FD_RESULTS.json',results)
    with (HERE/'SYNTHETIC_FD_CONVERGENCE.csv').open('w',newline='') as f:
        fields=['case','h_a0','spectral_absolute','spectral_relative','frobenius_relative','elementwise_max_normalized']
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for name,data in [('correct',correct),('wrong_10_percent',wrong)]:
            for row in data['rows']:w.writerow({'case':name,**{k:row[k] for k in fields[1:]}})
    print(json.dumps({'reused':len(checked),'new':finalplan['new_query_count'],'raw_cap':finalplan['max_raw_operator_evaluations'],'correct_synthetic':correct['passed'],'wrong_synthetic':wrong['passed']}))


if __name__=='__main__':main()
