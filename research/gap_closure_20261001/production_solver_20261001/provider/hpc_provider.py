"""Pinned full-operator adapter for the R4S MPI/Fortran pipeline.

No physics is evaluated on import or during context preparation. A caller must
freeze a fresh execution manifest before constructing PinnedEvaluator. This
module changes the native implementation identity, not quadrature or tolerances.
"""
from pathlib import Path
import hashlib,json,math,os,sys,time

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
FND=REPO/'research/foundation_rebuild'
HPC=HERE.parents[1]/'hpc_optimization_20261001'
RUNTIME=HERE.parent/'runtime'
_PATHS=[REPO,FND/'src',FND/'reaudit_20260925/repair',FND/'full_operator_20260926',
 FND/'tp2a_perf_20260926',FND/'tp2a_derivative_aware_20260926',FND/'tp2a_reference_qualified_20260926',
 FND/'tp2a_analytic_pruning_20260926/code',FND/'tp2d_runtime_self_qualified_transport_20260927',
 FND/'ncp_shared_research_20260928/r4c_temporal_continuation',
 FND/'ncp_shared_research_20260928/r4f_parallel_migration_20260929',RUNTIME,HPC]
for p in _PATHS:
    if str(p) not in sys.path:sys.path.insert(0,str(p))
# Legacy bootstrap's historical standalone default does not point at a restored
# selective checkout. Pin the already identified repository, reject overrides.
if os.environ.get('BASS_ANALYTIC_SOURCE_ROOT',str(REPO))!=str(REPO):
    raise ValueError('external analytic source override forbidden')
os.environ['BASS_ANALYTIC_SOURCE_ROOT']=str(REPO)

import numpy as np
from qualified_provider import ResolutionQualifiedProvider,_atomic_file
from parallel_bridge import PlannedQuery,query_id,validate_pair,publish_pair
from execution_admission import strict_json
from cache_consistency import validate_full_raw_cross,validate_cached_cross_binding

INPUT_SHA='889001a751cd3cae93ad217336587f5fc58db11c0a496843ecc7e7bbd93f83ec'
ARCHIVED_BASIS_IDENTITY='f23267b7214a5e3918866dcece5cb61c79a891578f4dda69dee5a762eb02983a'
ARCHIVED_CONTRACT_SHA256='45688d008edc60a54097cd2907497c75475c44ef168a176333b758b425370cff'
SELECTED=[9,10,12,13,14]

def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write_new(p,x):
    data=(json.dumps(x,indent=2,allow_nan=False)+'\n').encode()
    _atomic_file(p,lambda f:f.write(data))

def validate_contract(contract):
    # Reuse the same legacy contract validation; never instantiate an evaluator.
    ResolutionQualifiedProvider(evaluate=lambda *a:None,
        resolutions=contract['runtime_reference_resolutions'],screens=contract['screens'],context_id='validation')
    return contract

def build_tasks(context_id,times,contract):
    validate_contract(contract)
    if not isinstance(context_id,str) or not context_id:raise ValueError('context required')
    rows=[]
    for t in times:
        if not math.isfinite(t):raise ValueError('finite times required')
        th=float(t).hex();rows.append({'time_hex':th,'query_id':query_id(context_id,th),
                                     'levels':contract['runtime_reference_resolutions']})
    if not rows or len({r['query_id'] for r in rows})!=len(rows):raise ValueError('nonempty unique query times required')
    return rows

def bind_rank(rank,size,threads,cpus,*,get=os.sched_getaffinity,set_=os.sched_setaffinity):
    if any(type(x) is not int for x in (rank,size,threads)) or size<1 or threads<1 or not 0<=rank<size:
        raise ValueError('invalid rank allocation')
    if len(cpus)!=size*threads or len(set(cpus))!=len(cpus) or any(type(c) is not int or c<0 for c in cpus):
        raise ValueError('exact disjoint CPU IDs required for every rank including coordinator')
    if not set(cpus)<=set(get(0)):raise ValueError('requested launch CPUs outside process affinity')
    selected=set(cpus[rank*threads:(rank+1)*threads]);set_(0,selected)
    if set(get(0))!=selected:raise ValueError('OS did not bind rank exactly')
    return {'rank':rank,'cpus':sorted(selected),'threads':threads,'binding_verified':True}

def source_pins():
    files=set()
    for d in _PATHS:
        if d==REPO:
            files.update((REPO/'cr_repro').glob('*.py'))
        elif d==HPC:
            files.update(d/n for n in ('kernel.py','build_native.py','mpi_queue.py','resource_profile.py','native/moment_kernel_real.f90'))
        elif d==RUNTIME:files.add(d/'cache_consistency.py')
        elif d==FND/'src':files.update(d.rglob('*.py'))
        else:files.update(d.glob('*.py'))
    files.update(HERE.glob('*.py'))
    return {str(p.relative_to(REPO)):sha(p) for p in sorted(files) if p.is_file() and not p.name.startswith('test_')}

def prepare_context(inputs,build,contract,*,backend='fortran',threads=1):
    """Read/hash only, no CDLL and no full operator calls."""
    validate_contract(contract);inputs=Path(inputs);build=Path(build)
    if backend not in ('fortran','reference') or type(threads) is not int or not 1<=threads<=64:
        raise ValueError('bounded backend/threads required')
    science=strict_json(inputs/'SCIENCE_CONTEXT.json')
    archived=science.get('context',{}).get('contract')
    if (not isinstance(archived,dict) or digest(archived)!=ARCHIVED_CONTRACT_SHA256
        or contract!=archived or digest(contract)!=ARCHIVED_CONTRACT_SHA256):
        raise ValueError('archived qualification contract mismatch; changed contracts require another adapter')
    if sha(inputs/'BASIS.npz')!=INPUT_SHA:raise ValueError('this adapter is pinned to the archived B0 bank')
    basis=json.loads((inputs/'BASIS.json').read_text())
    if (basis.get('identity')!=ARCHIVED_BASIS_IDENTITY
        or digest({k:v for k,v in basis.items() if k!='identity'})!=basis['identity']
        or basis['matrix_sha256']!=INPUT_SHA):
        raise ValueError('basis semantic/byte identity mismatch')
    receipt=json.loads((build/'BUILD_HPC.json').read_text())
    if set(receipt.get('libraries',{}))!={'libreference.so','libmoments_f90.so'}:raise ValueError('complete native manifest required')
    for n,h in receipt['libraries'].items():
        if sha(build/n)!=h:raise ValueError('native hash mismatch')
    expected={'reference':FND/'tp2a_analytic_pruning_20260926/code/moment_kernel.cpp',
              'fortran':HPC/'native/moment_kernel_real.f90'}
    if receipt.get('source_hashes')!={k:sha(v) for k,v in expected.items()}:raise ValueError('native source mismatch')
    core={'schema':'BASS_R4U_HPC_OPERATOR_CONTEXT_V1','basis_identity':basis['identity'],
      'input_files':{n:sha(inputs/n) for n in ('BASIS.npz','BASIS.json','SCIENCE_CONTEXT.json')},
      'physics':{'energy_keV_per_u':100,'b_a0':2,'charges':[1,1],'channels':18,'selected_indices':SELECTED},
      'native_build_sha256':sha(build/'BUILD_HPC.json'),'native_libraries':receipt['libraries'],
      'native_source_hashes':receipt['source_hashes'],'backend':backend,'threads':threads,
      'same_center_order':20,'phase_budget':None,'sector':'full','cross_batch':1024,
      'qualification_contract':contract,'source_pins':source_pins(),
      'old_context_reuse':False,'production_admission':'HOLD','capture':False}
    return {**core,'context_id':digest(core)}

class PinnedEvaluator:
    def __init__(self,inputs,build,context):
        fresh=prepare_context(inputs,build,context['qualification_contract'],backend=context['backend'],threads=context['threads'])
        if fresh!=context:raise ValueError('fresh operator context mismatch before native load')
        from kernel import HPCMomentKernel
        from runtime import load_bank
        from bass_foundations.two_center import Trajectory,symmetric_channels
        from cr_repro.observables import projectile_speed_au
        self.kernel=HPCMomentKernel(build,backend=context['backend'],threads=context['threads'])
        bank,record=load_bank(inputs);self.channels=symmetric_channels(bank)
        if len(self.channels)!=18 or record['identity']!=context['basis_identity']:raise ValueError('channel identity mismatch')
        speed=projectile_speed_au(100)
        self.trajectory=Trajectory(((0.,0.,0.),(2.,0.,0.)),((0.,0.,0.),(0.,0.,speed)))
        self.context=context

    def __call__(self,t,order,subdivisions):
        from kernel import cross_with_identity
        from full_operator import _bind_cross,assemble_full
        raw=cross_with_identity(self.trajectory,self.channels,float(t),kernel=self.kernel,
          order=int(order),subdivisions=int(subdivisions),phase_budget=None,sector='full',batch=1024)
        raw['metadata']['operator_context_id']=self.context['context_id']
        snap=_bind_cross(self.trajectory,self.channels,float(t),raw,raw['metadata'])
        full=assemble_full(self.trajectory,self.channels,float(t),same_order=20,cross=snap)
        return raw,full

def qualified_task(task,reserve,evaluator,context_id,contract):
    validate_contract(contract)
    th=task.get('time_hex');qid=task.get('query_id')
    if query_id(context_id,th)!=qid or task.get('levels')!=contract['runtime_reference_resolutions']:
        raise ValueError('task is not the bound context/qualification ladder')
    t=float.fromhex(th)
    if not math.isfinite(t):raise ValueError('nonfinite query time')
    dest=Path(reserve.task_dir);attempts=[]
    def evaluate(time_t,order,subdivisions):
        i=len(attempts);rule=contract['runtime_reference_resolutions'][i]
        if rule!={'order':order,'subdivisions':subdivisions}:raise ValueError('qualification order changed')
        number=reserve(i)  # durable global reservation BEFORE any raw physics call
        tic=time.monotonic();raw,full=evaluator(time_t,order,subdivisions)
        arrays={'full__'+k:np.asarray(full[k]) for k in ('S','H','D')}
        arrays.update({'raw__'+k:np.asarray(raw[k]) for k in ('S_tp','S_pt','H_tp','H_pt','D_tp','D_pt')})
        payload=dest/'attempts'/f'{i:03}.npz'
        _atomic_file(payload,lambda f:np.savez_compressed(f,**arrays))
        record={'level_index':i,'resolution':rule,'global_reservation':number,'payload_sha256':sha(payload),
                'wall_seconds':time.monotonic()-tic,'full_metadata':full.get('metadata',{})}
        write_new(payload.with_suffix('.json'),record);attempts.append(record)
        # Preserve the failed raw attempt before rejecting an inconsistent assembly.
        validate_full_raw_cross(full,raw)
        return raw,full
    provider=ResolutionQualifiedProvider(evaluate=evaluate,resolutions=contract['runtime_reference_resolutions'],
      screens=contract['screens'],context_id=context_id,out_dir=dest,max_unique_queries=1)
    provider.at(t)
    checked=validate_pair(dest/'runtime_queries',PlannedQuery(qid,th,None,None),context_id,contract)
    validate_cached_cross_binding(dest/'runtime_queries',qid)
    return {**checked,'task_dir':str(dest),'context_id':context_id,'attempt_records':len(attempts)}

def collect_cache(rows,out,context_id,contract):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);records=[]
    for row in rows:
        item=PlannedQuery(row['query_id'],row['time_hex'],None,None)
        validate_cached_cross_binding(Path(row['task_dir'])/'runtime_queries',item.query_id)
        result=publish_pair(Path(row['task_dir'])/'runtime_queries',out,item,context_id,contract)
        records.append(result)
    receipt={'schema':'BASS_R4U_QUALIFIED_CACHE_V1','context_id':context_id,'qualified_queries':len(records),
             'records':records,'cache_payloads_digest':digest(records),'continuous_bound':False,'capture':False}
    write_new(out/'CACHE_RECEIPT.json',receipt);return receipt

class SerialComm:
    def Get_size(self):return 1
    def Get_rank(self):return 0
    def bcast(self,value,root=0):return value
    def allgather(self,value):return [value]
