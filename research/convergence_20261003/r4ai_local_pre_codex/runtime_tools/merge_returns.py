"""Read-only exact R4AG multi-batch collection; never launches native code.

Version 1 is deliberately limited to intact, co-located original runtime trees
and identical native bytes. It is not a relocated-archive or cross-ABI verifier.
A missing runtime identity is a blocker, not permission to weaken verification.
"""
from __future__ import annotations
import argparse,hashlib,importlib,json,sys
from pathlib import Path

LOCK_SHA='9795d7c0bf930978d4383a7e35113f0b1b8da1d5b05ff43be96b9fa9a748530c'
IDS={'m64','m128','m256','m512','m1024','p1024','p512','p256','p128','p64'}

class MergeError(ValueError): pass

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def load(path):
    def pairs(items):
        d={}
        for k,v in items:
            if k in d: raise MergeError('duplicate JSON key')
            d[k]=v
        return d
    return json.loads(Path(path).read_text(),object_pairs_hook=pairs,
        parse_constant=lambda x:(_ for _ in ()).throw(MergeError('nonfinite JSON')))

def combine_verified(groups):
    """Combine packets already authenticated by the original complete verifier.

    This pure helper does NOT authenticate physical packets. Calling it alone
    is insufficient for a certificate. The CLI always calls collect_many.
    """
    result=[];origin={};batches=set()
    for g in groups:
        b=g['batch_sha256']
        if b in batches: raise MergeError('duplicate batch selection')
        batches.add(b)
        for p in g['packets']:
            n=p['node_id']
            if n not in IDS: raise MergeError('unknown shifted node')
            if n in origin: raise MergeError('duplicate node authority')
            result.append(p);origin[n]=b
    return result,origin

def checked_selection(spec):
    if not isinstance(spec,dict) or set(spec)!={'schema','batches'} or spec['schema']!='R4AI_MULTI_BATCH_SELECTION_V1':
        raise MergeError('selection schema')
    if not isinstance(spec['batches'],list) or not 1<=len(spec['batches'])<=10:
        raise MergeError('one to ten batches required')
    ids=set();paths=set()
    for b in spec['batches']:
        if not isinstance(b,dict) or set(b)!={'path','sha256','nodes'}: raise MergeError('batch selection keys')
        if not isinstance(b['path'],str) or not Path(b['path']).is_absolute(): raise MergeError('absolute batch path')
        p=str(Path(b['path']).resolve())
        if p in paths: raise MergeError('duplicate batch path')
        paths.add(p)
        h=b['sha256']
        if not isinstance(h,str) or len(h)!=64 or any(c not in '0123456789abcdef' for c in h): raise MergeError('batch SHA256')
        ns=b['nodes']
        if not isinstance(ns,list) or not ns or len(ns)!=len(set(ns)) or any(n not in IDS for n in ns): raise MergeError('selected nodes')
        if ids.intersection(ns): raise MergeError('duplicate selected node')
        ids.update(ns)
    return spec['batches']

def check_contract(c,b,item,row,auth):
    """Static consumed-contract verification without re-running admission/execution."""
    if auth.get('schema')!='R4AG_BATCH_AUTHORIZATION_V1' or auth.get('batch_id')!=b['batch_id'] or auth.get('output')!=b['output'] or auth.get('attempt_cap_per_node')!=1 or auth.get('explicit_authorization_at_runtime') is not True:
        raise MergeError('authorization scope')
    ns=auth.get('authorized_nodes')
    if not isinstance(ns,list) or not ns or len(ns)!=len(set(ns)) or not set(ns)<=IDS or auth.get('maximum_native_points')!=len(ns) or item['node_id'] not in ns:
        raise MergeError('authorization nodes')
    expected={'schema':'R4AG_SHIFTED_POINT_EXECUTION_V1','batch_id':b['batch_id'],
      'node_id':item['node_id'],'candidate_identity':row['candidate'] if 'candidate' in row else '17c0215979675e40db364207ce138c5efb58cb24c22824e418f5abe3cfeb49ef',
      'z':row['z_a0'],'output':item['output'],'package_root':b['root'],
      'source_lock_sha256':LOCK_SHA,'native_path':b['native'],'native_sha256':b['native_sha256'],
      'precision_bits':256,'rho':'2','degrees':[16,24,32,40,48,56,64],
      'target_radius':'1/10000000000000000','quadrature_budget':'1/1000000000000000000',
      'max_cells':10000,'max_split_depth':5,'epoch':'ACTUAL_STORED',
      'caps':{'point_geometry':1,'window_jet':0,'D':0,'Vother':0,'attempts':1},
      'resources':b['resources'],'shared_library_pins':b['shared_library_pins'],
      'global_ceiling':{'G02':'UNRESOLVED','production':'HOLD','capture':False,'all_bound':'OPEN','b_grid':'NO_GO'}}
    expected.update({k:row[k] for k in ('geometry_path','geometry_sha256','S_path','S_sha256')})
    if any(c.get(k)!=v for k,v in expected.items()): raise MergeError('consumed method/input contract mismatch')

def collect_many(root,selection_path,output):
    root=Path(root).resolve();output=Path(output).resolve()
    if output.exists(): raise FileExistsError('create-only return')
    if sha(root/'SOURCE_INPUT_LOCK.json')!=LOCK_SHA: raise MergeError('original R4AG lock identity')
    selection=load(selection_path);selections=checked_selection(selection)
    # This command must be run in a fresh interpreter to avoid module shadowing.
    for name in ('common','runtime_contract','stencil','collect'):
        if name in sys.modules: raise MergeError('preloaded provider module: '+name)
    sys.path.insert(0,str(root/'source'))
    common=importlib.import_module('common')
    common.verify_lock(root)
    rc=importlib.import_module('runtime_contract');col=importlib.import_module('collect');st=importlib.import_module('stencil')
    for m in (common,rc,col,st):
        if not Path(m.__file__).resolve().is_relative_to(root/'source'): raise MergeError('module provenance')
    reg=common.read(root/'inputs/NODE_REGISTRY.json');rows={r['node_id']:r for r in reg['nodes']}
    groups=[];native=None;provenance=[]
    for spec in selections:
        p=Path(spec['path']).resolve()
        if sha(p)!=spec['sha256']: raise MergeError('batch input identity')
        b=rc.validate_batch(p,root)
        if native is None: native=b['native_sha256']
        if native!=b['native_sha256']: raise MergeError('different native needs separate reviewed intake')
        a=common.read(p.parent/'AUTHORIZATION.json')
        if a.get('batch_sha256')!=spec['sha256']: raise MergeError('authorization batch SHA')
        items={it['node_id']:it for it in b['nodes']};packets=[]
        for n in spec['nodes']:
            it=items[n];c=common.read(it['contract']);check_contract(c,b,it,rows[n],a)
            packet=col.verify_node_payload(b,it,root)
            if packet is None: raise MergeError('selected node missing: '+n)
            if packet.get('test_fixture',False): raise MergeError('fixture is not a physical return')
            packets.append(packet)
            provenance.append({'node_id':n,'batch_sha256':spec['sha256'],
                'authorization_sha256':sha(p.parent/'AUTHORIZATION.json'),
                'contract_sha256':it['contract_sha256'],'native_sha256':b['native_sha256'],
                'return_manifest_sha256':sha(Path(it['output'])/'RETURN_MANIFEST.json'),
                'enclosure_sha256':sha(Path(it['output'])/'S_ENCLOSURE.json')})
        groups.append({'batch_sha256':spec['sha256'],'packets':packets})
    packets,origin=combine_verified(groups)
    result=st.assemble_packets(reg,packets,root=root)
    result['multi_batch_collection']={'schema':'R4AI_READ_ONLY_MULTI_BATCH_RETURN_V1',
      'source_lock_sha256':LOCK_SHA,'selection_sha256':sha(selection_path),
      'node_origins':origin,'evidence':provenance,'native_executions':0,
      'original_runtime_paths_required':True,'same_native_bytes_required':True,
      'collector_sha256':sha(__file__)}
    common.write_new(output,result)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--r4ag-root',required=True);p.add_argument('--selection',required=True);p.add_argument('--output',required=True)
    args=p.parse_args()
    try:
        r=collect_many(args.r4ag_root,args.selection,args.output)
        print(json.dumps({'output':str(Path(args.output).resolve()),'native_executions':0,'status':r.get('status')},sort_keys=True))
    except (ValueError,KeyError,TypeError,OSError,ImportError) as e:
        print(type(e).__name__+': '+str(e),file=sys.stderr);sys.exit(2)
