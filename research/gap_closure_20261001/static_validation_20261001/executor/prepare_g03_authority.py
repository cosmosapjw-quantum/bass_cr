"""Create an UNAPPROVED live G03 proposal. Reads native bytes; never dlopens."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import argparse,datetime,json,os,subprocess,zipfile
import g03_executor as fd


def create(inputs,build,destination,*,authorization_id,workers,wall_seconds,cost_scope,python_path):
    if os.path.abspath(python_path)!=os.path.abspath(sys.executable):raise ValueError('prepare using proposed Python environment')
    destination=Path(destination).resolve();inputs=Path(inputs).resolve();build=Path(build).resolve()
    if destination.exists() or destination.with_suffix('.zip').exists() or destination.is_relative_to(fd.REPO):
        raise FileExistsError('fresh authority package outside worktree required')
    if subprocess.check_output(['git','-C',str(fd.REPO),'status','--porcelain','--untracked-files=all'],text=True):raise ValueError('clean exact commit required')
    head=subprocess.check_output(['git','-C',str(fd.REPO),'rev-parse','HEAD'],text=True).strip()
    tree=subprocess.check_output(['git','-C',str(fd.REPO),'rev-parse','HEAD^{tree}'],text=True).strip()
    contract,plan,native=fd.verify_inputs(inputs,build)
    sources=fd.required_sources()
    pins={'schema':'BASS_G03_SIGNED48_SOURCE_PINS_V1','execution_commit':head,'execution_tree':tree,
       'source_files':{n:fd.sha(fd.REPO/n) for n in sources},'native':native,
       'runtime_inputs':fd.old.BINDING['runtime_inputs'],'basis_identity':fd.old.BINDING['basis_identity'],
       'query_plan_sha256':fd.sha(fd.PLAN_PATH),'binding_inputs_sha256':fd.sha(fd.sv.SOURCE_DIR/'BINDING_INPUTS.json'),
       'resource_policy_sha256':fd.sha(fd.RESOURCE_PATH),'new_native_operator_evaluations':0,'new_authorization_consumed':0}
    fd.verify_source(pins)
    if type(workers) is not int or not 1<=workers<=2:raise ValueError('explicit1..2 workers required')
    cpus=sorted(os.sched_getaffinity(0))[:workers]
    if len(cpus)!=workers:raise ValueError('insufficient allowed CPUs')
    destination.mkdir(parents=True)
    for name in sources:fd._copy_new(fd.REPO/name,destination/'source'/name)
    for name in fd.old.BINDING['runtime_inputs']:fd._copy_new(inputs/name,destination/'runtime_inputs'/name)
    for name in ('BUILD.json','libmoments.so'):fd._copy_new(build/name,destination/'native_build'/name)
    fd.write_new(destination/'SOURCE_PINS.json',pins)
    census=fd.live_resource_census(cpus,workers,4<<30,receipt_path=destination/'LIVE_RESOURCE_CENSUS.json',sharing_policy='COOPERATIVE_SHARED_HOST')
    fd.verify_prior_pool_teardown(set(),run_pgid=os.getpgrp(),receipt_path=destination/'LIVE_OWN_POOL_TEARDOWN.json',settle_seconds=0.)
    deadline=census['checked_unix']+wall_seconds
    out=Path.home()/'.local/state/bass_g03_signed48/runs'/authorization_id/'output'
    authority={k:pins[k] for k in ('execution_commit','execution_tree','query_plan_sha256','binding_inputs_sha256','resource_policy_sha256')}
    authority['source_pins_sha256']=fd.sha(destination/'SOURCE_PINS.json')
    proposal={**fd.fixed_scope(),**authority,'status':'USER_APPROVAL_REQUIRED','authorization_id':authorization_id,
       'workers':workers,'hard_max_workers':2,'approved_cpu_list':cpus,'worker_ram_bytes':4<<30,
       'total_worker_ram_cap_bytes':workers*(4<<30),'minimum_live_available_bytes':(workers*4+4)*(1<<30),
       'wall_seconds':wall_seconds,'deadline_unix':deadline,'termination_grace_seconds':60,
       'deadline_utc':datetime.datetime.fromtimestamp(deadline,datetime.timezone.utc).isoformat(),
       'cost_scope':cost_scope,'cost_limit_enforced_by_code':False,
       'external_cost_control':'User/provider enforcement; no billing API or automatic host creation/resizing.',
       'source_pins_path':str(destination/'SOURCE_PINS.json'),'runtime_inputs_path':str(destination/'runtime_inputs'),
       'native_build_path':str(destination/'native_build'),'out_path':str(out),'python_path':os.path.abspath(python_path),
       'live_census_sha256':fd.sha(destination/'LIVE_RESOURCE_CENSUS.json'),
       'new_native_operator_evaluations':0,'new_authorization_consumed':0}
    nonce=Path.home()/'.local/state/bass_r4c/authorizations'/(authorization_id+'.json')
    fd.validate_scope(proposal,authority,approved=True,unused=not nonce.exists())
    fd.write_new(destination/'AUTHORIZATION_PROPOSAL.json',proposal)
    fd.write_new(destination/'PROPOSAL_PIN.json',{'proposal_sha256':fd.sha(destination/'AUTHORIZATION_PROPOSAL.json'),'status':'UNAPPROVED_NOT_CONSUMED'})
    fd.write_new(destination/'MANIFEST.json',{'schema':'BASS_G03_SIGNED48_AUTHORITY_PACKAGE_V1','files':{
       str(p.relative_to(destination)):{'bytes':p.stat().st_size,'sha256':fd.sha(p)} for p in sorted(destination.rglob('*')) if p.is_file()}})
    archive=destination.with_suffix('.zip')
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(destination.rglob('*')):
            if p.is_file():z.write(p,str(p.relative_to(destination)))
    return {'status':fd.READY,'package':str(archive),'package_sha256':fd.sha(archive),
       'proposal_path':str(destination/'AUTHORIZATION_PROPOSAL.json'),
       'proposal_sha256':fd.sha(destination/'AUTHORIZATION_PROPOSAL.json'),
       'execution_commit':head,'execution_tree':tree,'new_native_operator_evaluations':0,'new_authorization_consumed':0}


def main():
    p=argparse.ArgumentParser(description=__doc__,allow_abbrev=False)
    for name in ('inputs','build','out','authorization-id','cost-scope'):p.add_argument('--'+name,required=True)
    p.add_argument('--workers',type=int,default=2);p.add_argument('--wall-seconds',type=int,required=True)
    args=p.parse_args()
    print(json.dumps(create(args.inputs,args.build,args.out,authorization_id=args.authorization_id,
       workers=args.workers,wall_seconds=args.wall_seconds,cost_scope=args.cost_scope,python_path=sys.executable),indent=2))


if __name__=='__main__':main()
