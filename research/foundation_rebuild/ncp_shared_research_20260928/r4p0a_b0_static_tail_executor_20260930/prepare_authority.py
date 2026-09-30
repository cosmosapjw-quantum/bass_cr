"""Mechanically seal clean source, frozen inputs and an UNAPPROVED live proposal."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import argparse,datetime,json,os,subprocess,zipfile
from static_tail import HERE,REPO,BINDING,READY,sha,write_new,verify_inputs,verify_source,exact_items,binding_plan
from resource_census import live_resource_census,verify_prior_pool_teardown


def copy_new(source,target):
    target=Path(target);target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('xb') as f:f.write(Path(source).read_bytes())

def python_environment_path(path):
    # Resolving a venv's executable symlink loses the environment selection.
    return os.path.abspath(path)

def create(inputs,build,destination,python_path):
    if python_environment_path(python_path)!=python_environment_path(sys.executable):
        raise ValueError('package must be prepared with the proposed Python environment')
    destination=Path(destination).resolve();inputs=Path(inputs).resolve();build=Path(build).resolve()
    if destination.exists() or destination.with_suffix('.zip').exists():raise FileExistsError('create-only authority package')
    if subprocess.check_output(['git','-C',str(REPO),'status','--porcelain'],text=True):raise ValueError('clean exact commit required')
    head=subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip();tree=subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD^{tree}'],text=True).strip()
    contract,plan,native=verify_inputs(inputs,build)
    dependencies=json.loads((HERE/'DEPENDENCY_CLOSURE.json').read_text())['files']
    pinned=json.loads((REPO/'research/foundation_rebuild/ncp_shared_research_20260928/r4c_temporal_continuation/PINNED_DEPENDENCIES.json').read_text())['files']
    if any(sha(REPO/n)!=value for n,value in pinned.items()):raise ValueError('frozen numerical dependency drift')
    source_names=subprocess.check_output(['git','-C',str(REPO),'ls-files',str(HERE.relative_to(REPO))],text=True).splitlines()
    sources=sorted(set(dependencies)|set(source_names))
    for n,pin in BINDING['delivered_source_sha256'].items():
        if sha(HERE/n)!=pin:raise ValueError('delivered component modified: '+n)
    destination.mkdir(parents=True)
    for n in sources:copy_new(REPO/n,destination/'source'/n)
    # Exact delivered NPZ fixtures stay outside Git but are in the portable closure.
    fixture=HERE/'fixtures/R4P0';fixture_contract=json.loads((fixture/'CONTRACT.json').read_text())
    for n,pin in fixture_contract['input_files'].items():
        original=fixture/'inputs'/n
        if original.stat().st_size!=pin['bytes'] or sha(original)!=pin['sha256']:raise ValueError('delivered fixture pin mismatch: '+n)
        target=destination/'source'/HERE.relative_to(REPO)/'fixtures/R4P0/inputs'/n
        if target.exists():
            if target.read_bytes()!=original.read_bytes():raise ValueError('fixture conflict')
        else:copy_new(original,target)
    for n in BINDING['runtime_inputs']:copy_new(inputs/n,destination/'runtime_inputs'/n)
    for n in ('BUILD.json','libmoments.so'):copy_new(build/n,destination/'native_build'/n)
    pins={'schema':'BASS_R4P0_B0_STATIC_SOURCE_PINS_V1','execution_commit':head,'execution_tree':tree,
          'source_files':{n:sha(REPO/n) for n in sources},'native':native,
          'runtime_inputs':BINDING['runtime_inputs'],'basis_identity':BINDING['basis_identity'],
          'binding_inputs_sha256':sha(HERE/'BINDING_INPUTS.json'),
          'query_plan_sha256':sha(HERE/'BOUND_B0_TAIL_QUERY_PLAN.json'),
          'research_archive_sha256':BINDING['research_archive_sha256'],'a3_archive_sha256':BINDING['a3_archive_sha256'],
          'new_native_operator_evaluations':0,'new_authorization_consumed':0}
    write_new(destination/'SOURCE_PINS.json',pins)
    cpus=sorted(os.sched_getaffinity(0))[:4]
    if len(cpus)!=4:raise ValueError('four allowed CPUs unavailable')
    census=live_resource_census(cpus,4,1<<30,receipt_path=destination/'LIVE_RESOURCE_CENSUS.json',sharing_policy='COOPERATIVE_SHARED_HOST')
    teardown=verify_prior_pool_teardown(set(),run_pgid=os.getpgrp(),receipt_path=destination/'LIVE_OWN_POOL_TEARDOWN.json',settle_seconds=0.)
    auth='R4P0-B0-STATIC-TAIL-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d')+'-A1'
    nonce=Path.home()/'.local/state/bass_r4c/authorizations'/(auth+'.json')
    if nonce.exists():raise ValueError('proposed authorization already consumed; no automatic new ID')
    checked=census['checked_unix'];wall=3600;deadline=checked+wall
    out=Path.home()/'.local/state/bass_r4p0a/runs'/auth/'output'
    proposal={'schema':'BASS_R4P0_B0_STATIC_AUTHORIZATION_PROPOSAL_V1','status':'USER_APPROVAL_REQUIRED',
              'execution_commit':head,'execution_tree':tree,
              'source_pins_sha256':sha(destination/'SOURCE_PINS.json'),'query_plan_sha256':pins['query_plan_sha256'],
              'binding_inputs_sha256':pins['binding_inputs_sha256'],'runtime_inputs':pins['runtime_inputs'],'native':native,
              'basis_identity':BINDING['basis_identity'],'context_id':plan['context_id'],
              'research_archive_sha256':BINDING['research_archive_sha256'],'a3_archive_sha256':BINDING['a3_archive_sha256'],
              'basis':'B0','channels':18,'energy_keV_per_u':100,'b_a0':2,'signed_z_a0':[r['z_a0'] for r in plan['queries']],
              'runtime_query_ids':[q.query_id for q in exact_items(plan)],'time_hex':[q.time_hex for q in exact_items(plan)],
              'authorization_id':auth,'authorization_unused_at_census':True,'approved_cpu_list':cpus,
              'workers':4,'hard_max_workers':8,'automatic_worker_scaling':False,'numerical_threads':1,
              'worker_ram_bytes':1<<30,'total_worker_ram_cap_bytes':4<<30,'minimum_live_available_bytes':8<<30,
              'resource_sharing_policy':'COOPERATIVE_SHARED_HOST','operator_query_count':8,
              'raw_operator_evaluation_cap':88,'parent_raw_attempts':0,
              'native_parity':'NONE','derivative_fd_queries':0,'pilot_queries':0,'transport':False,
              'wall_seconds':wall,'deadline_unix':deadline,
              'deadline_utc':datetime.datetime.fromtimestamp(deadline,datetime.timezone.utc).isoformat().replace('+00:00','Z'),
              'termination_grace_seconds':60,'cost_ceiling_krw_including_vat':10000,
              'cost_scope':'PROPOSED_ONLY: maximum KRW 10000 including VAT for this one existing High CPU-g3 host static-tail attempt; separate new scope, no inherited A3 budget; no new VM or resize',
              'external_cost_control':'USER_OR_PROVIDER_ENFORCEMENT_REQUIRED; no billing API or monetary cap enforcement is included in this code',
              'cost_limit_enforced_by_code':False,'source_pins_path':str(destination/'SOURCE_PINS.json'),
              'runtime_inputs_path':str(destination/'runtime_inputs'),'native_build_path':str(destination/'native_build'),
              'out_path':str(out),'python_path':python_environment_path(python_path),
              'launcher':'bash run_b0_tail_science.sh OUT','launcher_git_mode':'100644',
              'live_census_sha256':sha(destination/'LIVE_RESOURCE_CENSUS.json'),'claim_ceiling':BINDING['claim_ceiling'],
              'new_native_operator_evaluations':0,'new_authorization_consumed':0}
    write_new(destination/'AUTHORIZATION_PROPOSAL.json',proposal)
    write_new(destination/'PROPOSAL_PIN.json',{'proposal_sha256':sha(destination/'AUTHORIZATION_PROPOSAL.json'),'proposal_bytes':(destination/'AUTHORIZATION_PROPOSAL.json').stat().st_size,'status':'UNAPPROVED_NOT_CONSUMED'})
    manifest={'schema':'BASS_R4P0_B0_STATIC_PREPARATION_PACKAGE_V1','execution_commit':head,'execution_tree':tree,
              'native_authorization_consumed':False,'files':{str(p.relative_to(destination)):{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(destination.rglob('*')) if p.is_file()}}
    write_new(destination/'MANIFEST.json',manifest)
    archive=destination.with_suffix('.zip')
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(destination.rglob('*')):
            if p.is_file():z.write(p,str(p.relative_to(destination)))
    return {'status':READY,'execution_commit':head,'execution_tree':tree,'package':str(archive),'package_bytes':archive.stat().st_size,
            'package_sha256':sha(archive),'proposal_path':str(destination/'AUTHORIZATION_PROPOSAL.json'),
            'proposal_sha256':sha(destination/'AUTHORIZATION_PROPOSAL.json'),'source_pins_sha256':sha(destination/'SOURCE_PINS.json'),
            'new_native_operator_evaluations':0,'new_authorization_consumed':0}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('inputs','build','out','python'):p.add_argument('--'+n,required=True)
    a=p.parse_args();print(json.dumps(create(a.inputs,a.build,a.out,a.python),indent=2))
