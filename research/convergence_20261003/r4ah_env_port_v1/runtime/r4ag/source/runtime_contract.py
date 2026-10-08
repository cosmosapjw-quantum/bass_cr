"""Pinned, one-shot shifted-node execution. Preparation never runs science."""
from __future__ import annotations
import os,sys,platform,uuid,subprocess,time,importlib.metadata
from pathlib import Path
from fractions import Fraction as F
from common import ROOT,CANDIDATE,CEILING,ContractError,inside,sha,read,write_new,verify_lock
from stencil import windows
from resource_reader import observe_resources, assert_same_hierarchy, ResourceError
GiB=1024**3

def validate_registry(registry,root=ROOT):
    if registry['schema']!='R4AG_NODE_REGISTRY_V1' or registry['candidate']!=CANDIDATE or registry['b_a0']!='2' or registry['center_z_a0']!='-32':raise ContractError('registry scope')
    expected_order=[[0,0,0],[1,0,0],[2,0,0],[3,1,-1],[3,1,0],[3,1,1],[4,1,-1],[4,1,0],[4,1,1]]
    if registry['channel_order']!=expected_order or registry['units']!={'coordinate':'a0','time':'ta','overlap':'1','derivative':'ta^-1'}:raise ContractError('channel/units')
    rows=registry['nodes'];offsets=[F(r['offset_a0']) for r in rows]
    expected=sorted({F(x) for w in windows(root) for x in w['nodes']})
    if offsets!=expected or len(rows)!=10 or len({r['node_id'] for r in rows})!=10:raise ContractError('ten unique ordered shifted inputs')
    v=F(windows(root)[0]['speed_a0_per_ta'])
    for r in rows:
        expected_id=('m' if F(r['offset_a0'])<0 else 'p')+str(abs(F(r['offset_a0'])).denominator)
        if r['node_id']!=expected_id:raise ContractError('node label')
        for role in ('geometry','S'):
            p=inside(root,r[role+'_path'])
            if not p.is_file() or sha(p)!=r[role+'_sha256']:raise ContractError(role+' input pin')
        g=read(inside(root,r['geometry_path']))['geometry']
        z=F(float(g['actual_z_a0']));t=F(float(g['time_ta']))
        if z!=F(-32)+F(r['offset_a0']) or z!=F(r['z_a0']) or F(float(g['requested_z_a0']))!=z or F(r['time_ta'])!=t or F(r['v_a0_per_ta'])!=v:raise ContractError('exact geometry/epoch binding')
        if float.fromhex(r['actual_z_hex'])!=g['actual_z_a0'] or float.fromhex(r['time_hex'])!=g['time_ta'] or g['time_hex']!=r['time_hex'] or g['actual_z_hex']!=r['actual_z_hex']:raise ContractError('FP hex identity')
        if F(float(g['speed_a0_per_ta']))!=v or g['actual_centers_a0']!=[[0.0,0.0,0.0],[2.0,0.0,float(z)]]:raise ContractError('centers/speed')
        tr=g['trajectory']
        if tr['origins']!=[[0.0,0.0,0.0],[2.0,0.0,0.0]] or tr['velocities']!=[[0.0,0.0,0.0],[0.0,0.0,float(v)]] or tr['charges']!=[1.0,1.0]:raise ContractError('trajectory model')
    return rows

def observe_environment():
    if any(os.environ.get(k) for k in ('LD_PRELOAD','LD_AUDIT','LD_LIBRARY_PATH')):raise ContractError('unbound dynamic loader override')
    if sys.platform!='linux':raise ContractError('Linux process/affinity contract required')
    try:resources=observe_resources()
    except ResourceError as e:raise ContractError(str(e)) from e
    return {'platform':platform.platform(),'python':sys.version,'python_executable':str(Path(sys.executable).resolve()),'python_sha256':sha(sys.executable),'dependencies':{n:importlib.metadata.version(n) for n in ('numpy','scipy','mpmath')},**resources}

def choose_resources(environment,workers):
    if type(workers) is not int or workers not in (1,2,3):raise ContractError('validated profile supports workers 1..3 only')
    # Reserve one distinct CPU for the Python coordinator; no 64-core claim.
    aff=environment['affinity']
    if len(aff)<workers+1:raise ContractError('affinity requires coordinator reserve')
    if environment['quota']!='unlimited' and F(environment['quota'])<workers+1:raise ContractError('CPU quota includes coordinator')
    native=536870912;reserve=1879048192;required=workers*native+reserve
    if min(environment['memory_limit'],environment['memory_available'])<required:raise ContractError('available memory admission')
    return {'workers':workers,'worker_cpu_ids':aff[:workers],'coordinator_cpu_id':aff[workers], 'native_memory_bytes':native,'coordinator_and_reserve_bytes':reserve,'memory_required':required,'parallel_nodes':1,'wall_seconds':1800,'batch_wall_seconds':19000}

def prepare_batch(output,workers=1,root=ROOT):
    """Observe/build/pin only. No old executable or scientific runner is launched."""
    root=Path(root).resolve();verify_lock(root);reg=read(root/'inputs/NODE_REGISTRY.json');rows=validate_registry(reg,root)
    output=Path(output).expanduser()
    if not output.is_absolute():raise ContractError('absolute output path required')
    output=output.resolve()
    if output.exists() or not output.parent.is_dir():raise ContractError('new output under existing parent required')
    env=observe_environment();resources=choose_resources(env,workers)
    output.mkdir();(output/'contracts').mkdir();(output/'runs').mkdir();(output/'build').mkdir()
    try:
        native=output/'build/native_cubature';cmd=['g++','-std=c++17','-O3','-fno-fast-math','-ffp-contract=off',str(root/'vendor_af/native_cubature.cpp'),'-lgmpxx','-lgmp','-o',str(native)]
        build=subprocess.run(cmd,capture_output=True,text=True,timeout=90,check=False)
        (output/'build/BUILD.log').write_text(build.stdout+build.stderr)
        if build.returncode:raise ContractError('native build failed; preparation record retained')
        compiler=subprocess.run(['g++','--version'],capture_output=True,text=True,timeout=10,check=True).stdout
        linked=subprocess.run(['ldd',str(native)],capture_output=True,text=True,timeout=10,check=True).stdout
        (output/'build/COMPILER.txt').write_text(compiler);(output/'build/LDD.txt').write_text(linked)
        # Pin loaded shared-library bytes as well as the native, not only ldd text.
        libraries={}
        for line in linked.splitlines():
            for token in line.split():
                if token.startswith('/') and Path(token).is_file():libraries[token]=sha(Path(token))
        write_new(output/'ENVIRONMENT.json',env)
        batch_id=uuid.uuid4().hex;bindings=[]
        for r in rows:
            cp=output/'contracts'/(r['node_id']+'.json')
            c={'schema':'R4AG_SHIFTED_POINT_EXECUTION_V1','batch_id':batch_id,'node_id':r['node_id'],'candidate_identity':CANDIDATE,'z':r['z_a0'],'geometry_path':r['geometry_path'],'geometry_sha256':r['geometry_sha256'],'S_path':r['S_path'],'S_sha256':r['S_sha256'],'output':str(output/'runs'/r['node_id']),'package_root':str(root),'source_lock_sha256':sha(root/'SOURCE_INPUT_LOCK.json'),'native_path':str(native),'native_sha256':sha(native),'shared_library_pins':libraries,'precision_bits':256,'rho':'2','degrees':[16,24,32,40,48,56,64],'target_radius':'1/10000000000000000','quadrature_budget':'1/1000000000000000000','max_cells':10000,'max_split_depth':5,'caps':{'point_geometry':1,'window_jet':0,'D':0,'Vother':0,'attempts':1},'resources':resources,'epoch':'ACTUAL_STORED','global_ceiling':CEILING.copy()}
            write_new(cp,c);bindings.append({'node_id':r['node_id'],'contract':str(cp),'contract_sha256':sha(cp),'output':c['output']})
        batch={'schema':'R4AG_PREPARED_BATCH_V1','batch_id':batch_id,'root':str(root),'output':str(output),'source_lock_sha256':sha(root/'SOURCE_INPUT_LOCK.json'),'registry_sha256':sha(root/'inputs/NODE_REGISTRY.json'),'environment_sha256':sha(output/'ENVIRONMENT.json'),'nodes':bindings,'resources':resources,'native':str(native),'native_sha256':sha(native),'shared_library_pins':libraries,'status':'PREPARED_NOT_AUTHORIZED_NOT_EXECUTED','max_new_points':10,'center_replay':False,'M9_replay':False}
        write_new(output/'BATCH.json',batch)
        return output/'BATCH.json'
    except BaseException as e:
        write_new(output/'PREPARATION_FAILURE.json',{'type':type(e).__name__,'message':str(e),'scientific_evaluations':0});raise

def validate_batch(path,root=ROOT):
    path=Path(path).resolve();b=read(path)
    if b.get('schema')!='R4AG_PREPARED_BATCH_V1' or Path(b['output']).resolve()!=path.parent or Path(b['root']).resolve()!=Path(root).resolve():raise ContractError('batch location/root')
    verify_lock(root)
    if b['source_lock_sha256']!=sha(Path(root)/'SOURCE_INPUT_LOCK.json') or b['registry_sha256']!=sha(Path(root)/'inputs/NODE_REGISTRY.json'):raise ContractError('batch lock/registry')
    rows=validate_registry(read(Path(root)/'inputs/NODE_REGISTRY.json'),root)
    if [r['node_id'] for r in rows]!=[r['node_id'] for r in b['nodes']]:raise ContractError('batch node mapping')
    if sha(b['native'])!=b['native_sha256']:raise ContractError('native identity')
    runtime_env=read(path.parent/'ENVIRONMENT.json')
    if sha(path.parent/'ENVIRONMENT.json')!=b['environment_sha256'] or sha(sys.executable)!=runtime_env['python_sha256']:raise ContractError('interpreter/environment identity')
    if any(os.environ.get(k) for k in ('LD_PRELOAD','LD_AUDIT','LD_LIBRARY_PATH')):raise ContractError('unbound dynamic loader override')
    if {n:importlib.metadata.version(n) for n in ('numpy','scipy','mpmath')}!=runtime_env['dependencies']:raise ContractError('runtime dependency versions changed')
    for p,h in b['shared_library_pins'].items():
        if sha(p)!=h:raise ContractError('shared library changed: '+p)
    for item in b['nodes']:
        cp=inside(path.parent,Path(item['contract']).relative_to(path.parent))
        if sha(cp)!=item['contract_sha256']:raise ContractError('node contract changed')
        if Path(item['output']).resolve()!=path.parent/'runs'/item['node_id']:raise ContractError('node output changed')
    return b

def authorize_batch(batch_path,confirmed_hash,node_ids,root=ROOT):
    b=validate_batch(batch_path,root)
    if sha(batch_path)!=confirmed_hash:raise ContractError('explicit batch SHA required')
    allids=[x['node_id'] for x in b['nodes']]
    ids=allids if node_ids==['all10'] else node_ids
    if not ids or len(ids)!=len(set(ids)) or any(k not in allids for k in ids):raise ContractError('authorization node set')
    ap=Path(batch_path).parent/'AUTHORIZATION.json'
    write_new(ap,{'schema':'R4AG_BATCH_AUTHORIZATION_V1','batch_sha256':confirmed_hash,'batch_id':b['batch_id'],'authorized_nodes':ids,'attempt_cap_per_node':1,'maximum_native_points':len(ids),'output':b['output'],'nonce':uuid.uuid4().hex,'explicit_authorization_at_runtime':True})
    return ap

def validate_point_contract(contract_path,auth_path,root=ROOT):
    ap=Path(auth_path).resolve();b=validate_batch(ap.parent/'BATCH.json',root);auth=read(ap);c=read(contract_path)
    if auth['schema']!='R4AG_BATCH_AUTHORIZATION_V1' or auth['batch_sha256']!=sha(ap.parent/'BATCH.json') or auth['batch_id']!=b['batch_id'] or auth['output']!=b['output'] or auth['attempt_cap_per_node']!=1:raise ContractError('outer authorization binding')
    if c['node_id'] not in auth['authorized_nodes']:raise ContractError('node not authorized')
    item=next((r for r in b['nodes'] if r['node_id']==c['node_id']),None)
    if item is None or Path(item['contract']).resolve()!=Path(contract_path).resolve() or item['contract_sha256']!=sha(contract_path):raise ContractError('outer node pin')
    if c['schema']!='R4AG_SHIFTED_POINT_EXECUTION_V1' or c['batch_id']!=b['batch_id'] or c['candidate_identity']!=CANDIDATE:raise ContractError('point scope')
    row=next(r for r in read(Path(root)/'inputs/NODE_REGISTRY.json')['nodes'] if r['node_id']==c['node_id'])
    for k in ('geometry_path','geometry_sha256','S_path','S_sha256'):
        if c[k]!=row[k]:raise ContractError('shifted input mismatch')
    if c['z']!=row['z_a0'] or c['output']!=item['output'] or c['native_path']!=b['native'] or c['native_sha256']!=b['native_sha256']:raise ContractError('point geometry/output/native')
    if Path(c['output']).exists():raise FileExistsError('consumed point output; no automatic replay')
    if c['caps']!={'point_geometry':1,'window_jet':0,'D':0,'Vother':0,'attempts':1} or c['precision_bits']!=256 or c['rho']!='2' or c['degrees']!=[16,24,32,40,48,56,64]:raise ContractError('method/cap')
    if F(c['target_radius'])!=F(1,10**16) or F(c['quadrature_budget'])!=F(1,10**18) or c['max_cells']!=10000 or c['max_split_depth']!=5:raise ContractError('posthoc target/cell change')
    r=c['resources'];env=observe_environment();choose_resources(env,r['workers'])
    try:assert_same_hierarchy(read(ap.parent/'ENVIRONMENT.json'),env)
    except ResourceError as e:raise ContractError(str(e)) from e
    if len(set(r['worker_cpu_ids']+[r['coordinator_cpu_id']]))!=r['workers']+1 or not set(r['worker_cpu_ids']+[r['coordinator_cpu_id']])<=set(env['affinity']):raise ContractError('bound CPU allocation')
    if c['resources']!=b['resources'] or r['wall_seconds']!=1800 or r['parallel_nodes']!=1:raise ContractError('bound resources')
    # Old numerical core expects these selected fields at top level.
    c.update({k:r[k] for k in ('workers','worker_cpu_ids','native_memory_bytes','coordinator_and_reserve_bytes','wall_seconds')})
    return c,auth
