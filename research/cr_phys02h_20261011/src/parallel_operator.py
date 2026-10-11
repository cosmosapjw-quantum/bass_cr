# SPDX-License-Identifier: GPL-3.0-only
"""New exact-column assembly identity. Shared parent arithmetic is not an oracle.

No inherited SavedGridCascade method identity or previous operator approval is
claimed. The only generator AST change is its outer column iterator. This module
never propagates, solves, or reuses an old operator checkpoint.
"""
from __future__ import annotations
import os
THREAD_VARS = ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS',
               'NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS','BLIS_NUM_THREADS')
for _key in THREAD_VARS:
    os.environ[_key] = '1'
os.environ['OMP_NESTED'] = 'FALSE'
import ast
import copy
from dataclasses import dataclass
import hashlib
import importlib.util
import json
import multiprocessing as mp
from multiprocessing.connection import wait
from pathlib import Path
import platform
import resource
import sys
import time
import traceback
import numpy as np
import scipy
from scipy import sparse
from threadpoolctl import threadpool_limits, threadpool_info

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
CONTRACT = ROOT/'state/SCIENTIFIC_CONTRACT.json'
IDENTITY = 'CR-PHYS02H-AST-OUTER-COLUMN-RESTRICTION-RAW-CSC-CONCAT-v1'


def raw_hash(a):
    if not isinstance(a,np.ndarray) or not a.flags.c_contiguous:
        raise ValueError('ARRAY_NOT_C_CONTIGUOUS')
    return hashlib.sha256(a.tobytes(order='C')).hexdigest()


def checked_sources():
    contract = json.loads(CONTRACT.read_text())
    result = {}
    for key, info in contract['immutable_inputs'].items():
        path = REPO/info['relative_to_repo']; raw = path.read_bytes()
        if len(raw)!=info['bytes'] or hashlib.sha256(raw).hexdigest()!=info['sha256']:
            raise ValueError('SOURCE_IDENTITY_MISMATCH:'+key)
        result[key] = {'path':info['relative_to_repo'],'sha256':info['sha256']}
    result['new_implementation'] = {'path':str(Path(__file__).relative_to(REPO)),
                                    'sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    result['contract_sha256']=hashlib.sha256(CONTRACT.read_bytes()).hexdigest()
    return result


def load_module(key, path):
    if key in sys.modules:
        return sys.modules[key]
    spec=importlib.util.spec_from_file_location(key,path)
    module=importlib.util.module_from_spec(spec);sys.modules[key]=module
    spec.loader.exec_module(module)
    return module


def dependencies(model):
    checked_sources()
    if model=='fullBED':
        atomic_mod=load_module('cr_phys02h_real_fullbed',REPO/'research/cr_phys02c_20261011/src/coherent_bed.py')
        return atomic_mod.parent,atomic_mod.AtomicData()
    if model=='legacy':
        parent=load_module('cr_phys02h_real_legacy',REPO/'research/cr_phys02b_20261010/src/causal_cascade.py')
        return parent,parent.AtomicData()
    raise ValueError('UNKNOWN_MODEL')


def immutable_energy(E):
    if not isinstance(E,np.ndarray) or E.dtype.str!='<f8' or E.ndim!=1 or not E.flags.c_contiguous:
        raise ValueError('INVALID_ENERGY_IDENTITY')
    if not np.all(np.isfinite(E)) or len(E)<20 or not np.all(np.diff(E)>0) or E[0]<=.1 or E[-1]!=900.:
        raise ValueError('INVALID_ENERGY_DOMAIN')
    return np.frombuffer(E.tobytes(),dtype=E.dtype)


def validate_columns(columns,n):
    values=tuple(columns)
    if not values or any(type(j) is not int or j<0 or j>=n for j in values):
        raise ValueError('INVALID_COLUMN_INDEX')
    if values!=tuple(sorted(set(values))):
        raise ValueError('COLUMNS_NOT_SORTED_UNIQUE')
    return values


def partition_columns(columns,workers,n):
    columns=validate_columns(columns,n)
    if type(workers) is not int or not 1<=workers<=len(columns):
        raise ValueError('INVALID_WORKER_COUNT')
    q,r=divmod(len(columns),workers);tiles=[];start=0
    for i in range(workers):
        count=q+(i<r);tiles.append(columns[start:start+count]);start+=count
    validate_partition(columns,tiles,n)
    return tuple(tiles)


def validate_partition(columns,tiles,n):
    expected=validate_columns(columns,n)
    got=tuple(j for tile in tiles for j in validate_columns(tile,n))
    if got!=expected:
        raise ValueError('PARTITION_MISSING_DUPLICATE_OR_OUT_OF_ORDER')
    return True


def restricted_generator(parent):
    """Keep all precomputation, body and sparse return AST byte-for-byte structurally.

    Rename/add the columns argument and replace exactly one top-level For.iter.
    Compile in the ORIGINAL module globals, preserving all original dispatch.
    """
    source=Path(parent.__file__).read_text();tree=ast.parse(source)
    cls=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='Cascade')
    original=next(x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name=='_generator')
    candidate=copy.deepcopy(original)
    loops=[x for x in candidate.body if isinstance(x,ast.For) and
           ast.dump(x.iter,include_attributes=False)==ast.dump(ast.parse('enumerate(self.E)',mode='eval').body,include_attributes=False)]
    if len(loops)!=1 or ast.unparse(loops[0].target)!='(j, energy)':
        raise ValueError('UNEXPECTED_GENERATOR_AST')
    loop=loops[0]
    iterator_before=copy.deepcopy(loop.iter)
    loop.iter=ast.parse('((j, self.E[j]) for j in columns)',mode='eval').body
    candidate.name='_cr_phys02h_restricted_generator'
    candidate.args.args.append(ast.arg(arg='columns'))
    proof=copy.deepcopy(candidate);proof.name=original.name;proof.args.args.pop()
    next(x for x in proof.body if isinstance(x,ast.For) and ast.unparse(x.target)=='(j, energy)').iter=iterator_before
    if ast.dump(proof,include_attributes=False)!=ast.dump(original,include_attributes=False):
        raise ValueError('AST_CHANGE_OUTSIDE_OUTER_ITERATOR')
    module=ast.fix_missing_locations(ast.Module(body=[candidate],type_ignores=[]))
    namespace={};exec(compile(module,str(ROOT/'src/parallel_operator.py')+':source-pinned-AST','exec'),parent.__dict__,namespace)
    function=namespace[candidate.name]
    function.__module__=__name__
    return function,{'original_AST_sha256':hashlib.sha256(ast.dump(original,include_attributes=False).encode()).hexdigest(),
                     'restricted_AST_sha256':hashlib.sha256(ast.dump(candidate,include_attributes=False).encode()).hexdigest(),
                     'change':'function name/columns argument and sole outer For.iter only',
                     'restored_AST_exact':True,'compiled_globals':parent.__name__}


def shell(parent,atomic,E,mesh):
    obj=parent.Cascade.__new__(parent.Cascade)
    obj.E=E;obj.n=len(E);obj.size=obj.n+len(parent.LEDGERS)
    obj.ix={name:obj.n+k for k,name in enumerate(parent.LEDGERS)}
    obj.atomic=atomic;obj.sharing_order=4;obj.quantum_constant=0.;obj.mesh=tuple(mesh)
    obj.normalization_diagnostics=[]
    return obj


@dataclass
class Payload:
    G: object
    E: np.ndarray
    rates: dict
    diagnostics: list
    columns: tuple
    telemetry: dict
    identity: dict


def runtime_identity():
    return {'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,
            'platform':platform.platform(),'threads':{k:os.environ.get(k) for k in THREAD_VARS},
            'threadpools':threadpool_info(),'start_method':'spawn',
            'sources':checked_sources(),'implementation':IDENTITY}


def guard_size(E,columns):
    if len(E)>240 and len(columns)>16:
        # Prepared full build is rejected on the local small-memory host.
        limit=Path('/sys/fs/cgroup/memory.max').read_text().strip()
        if limit!='max' and int(limit)<32*2**30:
            raise ValueError('FULL_GRID_BUILD_FORBIDDEN_ON_THIS_HOST')


def serial_build(model,E,mesh,columns=None):
    E=immutable_energy(E);requested=validate_columns(tuple(range(len(E))) if columns is None else columns,len(E))
    guard_size(E,requested)
    parent,atomic=dependencies(model);obj=shell(parent,atomic,E,mesh)
    start=time.perf_counter()
    with threadpool_limits(limits=1):
        if columns is None:
            G=parent.Cascade._generator(obj);proof={'unmodified_original_generator':True}
        else:
            function,proof=restricted_generator(parent);G=function(obj,requested)
    elapsed=time.perf_counter()-start
    if np.any(~np.isfinite(G.data)) or any(np.any(~np.isfinite(x)) for x in obj.rates.values()):
        raise ValueError('NONFINITE_OPERATOR_OR_RATE')
    return Payload(G,E,obj.rates,obj.normalization_diagnostics,requested,
                   {'pid':os.getpid(),'wall_s':elapsed,'peakRSS_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
                    'peakRSS_scope':'entire coordinator process lifetime; not per-build delta','generator_invocations':1},proof)


def _worker(connection,model,E,mesh,columns,inject_failure):
    try:
        if inject_failure:
            raise RuntimeError('INJECTED_CHILD_FAILURE')
        payload=serial_build(model,E,mesh,columns)
        connection.send(('ok',payload))
    except BaseException:
        connection.send(('error',traceback.format_exc()))
    finally:
        connection.close()


def admission(workers):
    cpu_raw=Path('/sys/fs/cgroup/cpu.max').read_text().strip();q,p=cpu_raw.split()
    affinity=len(os.sched_getaffinity(0));quota=affinity if q=='max' else int(q)/int(p)
    mem_raw=Path('/sys/fs/cgroup/memory.max').read_text().strip()
    memory=int(mem_raw) if mem_raw!='max' else os.sysconf('SC_PAGE_SIZE')*os.sysconf('SC_PHYS_PAGES')
    current=int(Path('/sys/fs/cgroup/memory.current').read_text())
    reserve=max(2*2**30,memory//8);estimate=(workers+1)*512*2**20
    if workers+1>min(affinity,quota) or current+estimate+reserve>memory:
        raise ValueError('RESOURCE_ADMISSION_FAILED')
    return {'cpu_max':cpu_raw,'affinity_cpus':affinity,'quota_cpus':quota,'workers':workers,
            'coordinator_processes':1,'memory_max_bytes':memory,'memory_current_bytes':current,
            'reserve_bytes':reserve,'estimated_new_peak_bytes':estimate}


def gather(payloads,columns,E):
    columns=validate_columns(columns,len(E))
    payloads=sorted(payloads,key=lambda p:p.columns[0])
    validate_partition(columns,[p.columns for p in payloads],len(E))
    first=payloads[0];parts_data=[];parts_indices=[];indptr=[0];diagnostics=[]
    owners={j:p for p in payloads for j in p.columns}
    for payload in payloads:
        if not exact_array(payload.E,E) or tuple(payload.rates)!=tuple(first.rates):
            raise ValueError('TILE_INPUT_IDENTITY_MISMATCH')
        if any(not exact_array(payload.rates[k],first.rates[k]) for k in first.rates):
            raise ValueError('TILE_RATE_MISMATCH')
        diagnostics.extend(payload.diagnostics)
        for j in range(len(E)):
            if j not in payload.columns and payload.G.indptr[j+1]!=payload.G.indptr[j]:
                raise ValueError('UNREQUESTED_TILE_COLUMN')
    for j in range(first.G.shape[1]):
        if j in owners:
            p=owners[j];lo,hi=p.G.indptr[j:j+2]
            parts_data.append(p.G.data[lo:hi]);parts_indices.append(p.G.indices[lo:hi]);indptr.append(indptr[-1]+int(hi-lo))
        else:
            indptr.append(indptr[-1])
    # Array concatenation and integer pointer construction perform NO FP operations.
    data=np.concatenate(parts_data);indices=np.concatenate(parts_indices)
    pointers=np.asarray(indptr,dtype=first.G.indptr.dtype)
    G=sparse.csc_matrix((data,indices,pointers),shape=first.G.shape,copy=False)
    if not exact_array(G.data,data) or not exact_array(G.indices,indices) or not exact_array(G.indptr,pointers):
        raise ValueError('CSC_CONSTRUCTOR_CHANGED_STORAGE')
    return Payload(G,E,first.rates,diagnostics,columns,{}, {'implementation':IDENTITY,'tiles':[p.identity for p in payloads]})


def parallel_build(model,E,mesh,workers,columns=None,timeout_s=120,*,_fail_tile=None):
    E=immutable_energy(E);columns=validate_columns(tuple(range(len(E))) if columns is None else columns,len(E))
    guard_size(E,columns);tiles=partition_columns(columns,workers,len(E));admitted=admission(workers)
    checked_sources();start=time.perf_counter();ctx=mp.get_context('spawn');children=[];connections={};payloads=[]
    try:
        for i,tile in enumerate(tiles):
            receiver,sender=ctx.Pipe(duplex=False)
            process=ctx.Process(target=_worker,args=(sender,model,E,mesh,tile,i==_fail_tile))
            process.start();sender.close();children.append(process);connections[receiver]=process
        while connections:
            remaining=timeout_s-(time.perf_counter()-start)
            if remaining<=0:raise TimeoutError('CHILD_BUILD_TIMEOUT')
            ready=wait(list(connections),timeout=min(remaining,.25))
            for connection in ready:
                process=connections.pop(connection)
                try:kind,value=connection.recv()
                except EOFError as exc:raise RuntimeError('CHILD_EXIT_WITHOUT_PAYLOAD') from exc
                finally:connection.close()
                if kind!='ok':raise RuntimeError('CHILD_FAILURE:\n'+value)
                payloads.append(value)
            for process in connections.values():
                if process.exitcode is not None and process.exitcode!=0:
                    raise RuntimeError('CHILD_NONZERO_EXIT:'+str(process.exitcode))
        for process in children:
            process.join(timeout=5)
            if process.exitcode!=0:raise RuntimeError('CHILD_BAD_EXIT:'+str(process.exitcode))
        out=gather(payloads,columns,E)
        out.telemetry={'wall_s':time.perf_counter()-start,'admission':admitted,
                       'worker_processes':[p.telemetry for p in sorted(payloads,key=lambda p:p.columns[0])],
                       'actual_generator_invocations':len(payloads),'logical_builds':1,
                       'coordinator_peakRSS_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
                       'peakRSS_scope':'worker lifetime maximum per fresh spawned process; coordinator lifetime maximum; excludes additive summed peak assumption',
                       'exitcodes':[p.exitcode for p in children]}
        return out
    finally:
        for connection in connections:connection.close()
        for process in children:
            if process.is_alive():process.terminate()
        for process in children:
            process.join(timeout=5)
            if process.is_alive():process.kill();process.join(timeout=5)


def exact_array(a,b):
    return a.dtype.str==b.dtype.str and a.shape==b.shape and a.tobytes(order='C')==b.tobytes(order='C')


def parity(reference,candidate):
    checks={name:exact_array(getattr(reference.G,name),getattr(candidate.G,name)) for name in ('data','indices','indptr')}
    checks['energy']=exact_array(reference.E,candidate.E)
    checks['rates']=tuple(reference.rates)==tuple(candidate.rates) and all(exact_array(reference.rates[k],candidate.rates[k]) for k in reference.rates)
    checks['diagnostics']=json.dumps(reference.diagnostics,separators=(',',':'))==json.dumps(candidate.diagnostics,separators=(',',':'))
    checks['columns']=reference.columns==candidate.columns
    if not all(checks.values()):raise ValueError('EXACT_PARITY_FAILED:'+json.dumps(checks))
    return checks


def persist(payload,directory):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=False)
    arrays={'data':payload.G.data,'indices':payload.G.indices,'indptr':payload.G.indptr,'energy':payload.E,
            **{'rate_'+k:np.ascontiguousarray(v) for k,v in payload.rates.items()}}
    metadata={}
    for name,a in arrays.items():
        path=directory/(name+'.npy');np.save(path,a,allow_pickle=False)
        metadata[name]={'dtype':a.dtype.str,'shape':list(a.shape),'raw_sha256':raw_hash(a),
                        'file_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'file_bytes':path.stat().st_size}
    receipt={'schema':'cr-phys02h-persistent-raw-csc.v1','arrays':metadata,'shape':list(payload.G.shape),
             'columns':list(payload.columns),'diagnostics':payload.diagnostics,'telemetry':payload.telemetry,
             'assembly_identity':payload.identity,'runtime':runtime_identity()}
    (directory/'SIDECAR.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return receipt


def load_persisted(directory):
    directory=Path(directory);meta=json.loads((directory/'SIDECAR.json').read_text());arrays={}
    for name,info in meta['arrays'].items():
        path=directory/(name+'.npy')
        if hashlib.sha256(path.read_bytes()).hexdigest()!=info['file_sha256']:
            raise ValueError('PERSISTED_FILE_HASH_MISMATCH')
        a=np.load(path,allow_pickle=False)
        if a.dtype.str!=info['dtype'] or list(a.shape)!=info['shape'] or raw_hash(a)!=info['raw_sha256']:
            raise ValueError('PERSISTED_ARRAY_IDENTITY_MISMATCH')
        arrays[name]=a
    G=sparse.csc_matrix((arrays['data'],arrays['indices'],arrays['indptr']),shape=tuple(meta['shape']),copy=False)
    return Payload(G,arrays['energy'],{k[5:]:v for k,v in arrays.items() if k.startswith('rate_')},
                   meta['diagnostics'],tuple(meta['columns']),meta['telemetry'],meta['assembly_identity'])


def saved_energy():
    checked_sources()
    adapter=load_module('cr_phys02h_saved_input_validation',REPO/'research/cr_phys02e_20261011/src/saved_grid.py')
    study=REPO/'research/cr_phys02e_20261011'
    identities=json.loads((study/'inputs/INPUT_IDENTITIES.json').read_text())['inputs']
    bundles,receipt=adapter.preflight_saved_inputs(study,identities)
    return bundles['legacy']['energy_eV'],receipt
