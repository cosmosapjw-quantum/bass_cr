"""Read-only identity/resource/P2/P3 audit; no historical science replay."""
import argparse,hashlib,json,os,platform,shutil,subprocess
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def command(argv):
    p=subprocess.run(argv,capture_output=True,text=True)
    return {'argv':argv,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr}

def audit(stage,out,repo):
    out.mkdir(exist_ok=True,parents=True)
    tools={k:shutil.which(k) for k in ('python3','gcc','gfortran','cmake','mpirun','rustc','cargo','rclone','gdown')}
    cg=Path('/sys/fs/cgroup');rel=Path(Path('/proc/self/cgroup').read_text().split('::')[1].strip())
    chain=[];p=cg/str(rel).lstrip('/')
    while p.is_relative_to(cg):
        chain.append({'path':str(p),'limits':{k:(p/k).read_text().strip() if (p/k).exists() else 'NOT_EXPOSED' for k in ('cpu.max','memory.max','cpuset.cpus.effective')}})
        if p==cg:break
        p=p.parent
    memory={v.split(':')[0]:v.split(':')[1].strip() for v in Path('/proc/meminfo').read_text().splitlines()}
    resource={'host':platform.platform(),'affinity_cpu_ids':sorted(os.sched_getaffinity(0)),
        'memory':memory,'cgroup_ancestors':chain,'disk':dict(zip(('total','used','free'),shutil.disk_usage(repo))),
        'tools':tools,'versions':[command([x,'--version']) for x in ('python3','gcc','gfortran','cmake','mpirun')],
        'cpu':command(['lscpu']),'git_status_original':command(['git','-C','/root/bass_cr','status','--short']),
        'admission':{'workers':1,'coordinator_cpu_reserve':1,'RAM_reserve_bytes':24*1024**3,
            'thread_environment':{'OMP_NUM_THREADS':1,'OPENBLAS_NUM_THREADS':1,'MKL_NUM_THREADS':1},
            'MPI_execution':False,'NCP64_scaling':'NOT_RUN','parallel_pilots':'NOT_NEEDED_FOR_SERIAL_OPTICAL_LANE'},
        'rclone_remote_status':'BLOCKED_INPUT_AUTH_LOCAL_RCLONE_ABSENT',
        'connector_input_status':'FOUR_ARCHIVES_RECOVERED_FROM_EXISTING_DROPBOX_BY_TEMPORARY_LINK',
        'missing_contract_file':'.codex/readback-policy.json; docs/READBACK_POLICY.md read and applied'}
    write(out/'ENVIRONMENT.json',resource)
    rei=stage/'extracted/REI_XTHREAD_BRIDGE13_20261008/rei_bridge13_20261008'
    r14=stage/'extracted/BASS_CR_XTHREAD_R14_20261008_v1/CR_XTHREAD_R14_20261008'
    seed=load(r14/'inputs/rei_bridge12_20261008/inputs/NEXT_CELL_INPUT.json')
    rows=[json.loads(s) for s in (rei/'inputs/BRIDGE11_NATIVE.jsonl').read_text().splitlines()]
    pt=next(r for r in rows if r.get('kind')=='point' and r['index']==0 and r.get('variant')==0)
    assert seed['source_point']==pt,'R14_FIRST_NATIVE_POINT_MISMATCH'
    assert seed['time_s']==load(rei/'inputs/BRIDGE12_CELL_CERTIFICATE.json')['time_s']
    r13=stage/'extracted/BASS_CR_XTHREAD_R13_20261008_v1/CR_XTHREAD_R13_20261008'
    selected=load(r13/'inputs/SELECTED_INPUTS.json')
    checks=[]
    for row in selected:
        p=r13/row['path'];ok=p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
        assert ok,row['path'];checks.append({'path':row['path'],'sha256':sha(p),'verified':ok})
    r6=stage/'extracted/BASS_CR_FASTEST_NEWTON_20261007_v1/BASS_CR_FASTEST_NEWTON_20261007'
    binding=load(r6/'SOURCE_BINDING.json');r6_checks=[]
    for row in binding['all_library_source_unchanged']:
        p=r6/row['path'];assert sha(p)==row['sha256'],row['path']
        r6_checks.append({'path':row['path'],'sha256':sha(p)})
    write(out/'GRACKLE_READINESS.json',{'status':'BLOCKED_OWNER_INPUT','R13_selected_checks':checks,
        'R6_library_checks':r6_checks,'R13_binding_sha256':sha(r13/'SOURCE_BINDING.json'),
        'R6_binding_sha256':sha(r6/'SOURCE_BINDING.json'),'new_native_point_runs':0,'new_time_runs':0,
        'reason':'Verified archives contain completed point/native Newton evidence; no new same-model owner-accepted temporal stage plus full-time state/moment reconstruction is supplied.',
        'needed':['same Grackle low-T source/config/owner caller identity','actual new accepted trajectory with exact proper-clock/ln(a) mapping and incoming error','time-wide state and Gamma plus incident-energy moments, including branch/event data'],
        'preserved':['R13 closed','CI/RR/DR/cooling/CMB/expansion/RCT included for distinct states','full EOS particle-number term','35 eV RCT closure','FT03 donor is separate']})
    context=repo/'research/gap_closure_20261001/g02_derivative_validation_20261002/evidence/RECOVERY_CONTEXT.json'
    contract=repo/'research/gap_closure_20261001/g02_derivative_validation_20261002/TASK_CONTRACT.json'
    c=load(context);t=load(contract)
    pins=[{'historical_path':p,'expected_sha256':h,'accessible_here':Path(p).is_file()} for p,h in c['input_pins'].items()]
    write(out/'G02_READINESS.json',{'status':'BLOCKED_INPUT','authoritative_input_pins':pins,
        'context_sha256':sha(context),'contract_sha256':sha(contract),'geometry':t['geometry'],
        'fixed_derivative_contract':t['derivative_validation'],'candidate_basis_identity':t['basis_identity'],
        'needed':['exact BASIS.npz/BASIS.json/SCIENCE_CONTEXT.json with pinned hashes','separately bound CANDIDATE.npz/CANDIDATE.json','portable native sources/build manifests and new NCP source/native qualification','unmatched geometry with source-specific authority; historical completed central tests are not repeated'],
        'scientific_PASS':False,'new_operator_calls':0,'claim_ceiling':t['claim_ceiling'],
        'branch_restrictions':['bass_cr additive research only','no main merge','no force push','no 50/225 keV/u','no production release']})
    write(out/'INPUT_AUDIT.json',{'R14_first_native_point_exact_match':True,'R13_selected_payloads':len(checks),
        'R6_source_files':len(r6_checks),'source_only_checks':True,'donor_modifications':0})
    print('SOURCE_AUDIT PASS',len(checks),len(r6_checks),'P2 BLOCKED_OWNER_INPUT; P3 BLOCKED_INPUT')

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--stage',type=Path,required=True);a.add_argument('--output',type=Path,required=True);a.add_argument('--repo',type=Path,required=True)
    x=a.parse_args();audit(x.stage,x.output,x.repo)
