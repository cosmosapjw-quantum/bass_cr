"""Read-only, source-bound collection. It never evaluates an atomic integral."""
from __future__ import annotations
from pathlib import Path
from fractions import Fraction as F
from common import ROOT,CANDIDATE,ContractError,sha,read,inside,write_new
from runtime_contract import validate_batch
from stencil import assemble_packets,interval,moments

def verify_node_payload(batch,item,root=ROOT):
    out=Path(item['output']);cp=Path(item['contract']);c=read(cp)
    if not out.is_dir():return None
    if any((out/n).exists() for n in ('FAILURE.json','LAUNCH_FAILED.json','LAUNCH_INTERRUPTED.json')):raise ContractError('failed node retained: '+item['node_id'])
    if not (out/'COMPLETED.json').exists():raise ContractError('partial node requires explicit recovery: '+item['node_id'])
    done=read(out/'COMPLETED.json')
    if done.get('state')!='COMPLETE' or not done.get('all_native_exit_zero'):raise ContractError('completion state')
    if sha(out/'RESULT.json')!=done['result_sha256'] or sha(out/'RETURN_MANIFEST.json')!=done['manifest_sha256']:raise ContractError('completion seal')
    manifest=read(out/'RETURN_MANIFEST.json')
    if manifest['node_id']!=item['node_id'] or manifest['contract_sha256']!=item['contract_sha256']:raise ContractError('return scope pin')
    expected={'S_ENCLOSURE.json','S_ONLY_SEAL.json','RESULT.json','RESERVATION.json','CELL_CERTIFICATES.json','GAUSS_RULES.json','NATIVE_INPUT.txt','NATIVE_DISPATCH.json'}
    expected|={f'worker_{i}.{ext}' for i in range(c['resources']['workers']) for ext in ('intervals','stderr')}
    if not expected<=manifest['pins'].keys():raise ContractError('missing mandatory return payload')
    for name,h in manifest['pins'].items():
        if sha(inside(out,name))!=h:raise ContractError('return hash: '+name)
    reservation=read(out/'RESERVATION.json');auth=out.parents[1]/'AUTHORIZATION.json'
    if reservation['contract_sha256']!=item['contract_sha256'] or reservation['authorization_sha256']!=sha(auth):raise ContractError('reservation binding')
    seal=read(out/'S_ONLY_SEAL.json')
    if seal['file']!='S_ENCLOSURE.json' or seal['D_read'] is not False or sha(out/'S_ENCLOSURE.json')!=seal['sha256']:raise ContractError('S-only seal')
    e=read(out/'S_ENCLOSURE.json');r=read(out/'RESULT.json')
    if e.get('schema')!='R4AG_NODE_ENCLOSURE_V1' or r.get('schema')!='R4AG_SHIFTED_POINT_RESULT_V1':raise ContractError('return schema')
    for p in (e,r):
        if p['node_id']!=item['node_id'] or p['candidate']!=CANDIDATE or p['contract_sha256']!=item['contract_sha256'] or p['source_lock_sha256']!=batch['source_lock_sha256']:raise ContractError('result source/node binding')
    if e['geometry_sha256']!=c['geometry_sha256']:raise ContractError('returned wrong geometry')
    if r.get('D')!=0 or r.get('Vother')!=0 or r.get('window_jet')!=0 or r.get('historical_replays')!=0 or r['parent_M9_recomputed']:raise ContractError('forbidden execution scope')
    dispatch=read(out/'NATIVE_DISPATCH.json')
    if dispatch['input_sha256']!=sha(out/'NATIVE_INPUT.txt') or dispatch['executable_sha256']!=c['native_sha256'] or dispatch['workers']!=c['resources']['workers']:raise ContractError('native dispatch binding')
    proof=read(out/'CELL_CERTIFICATES.json');tasks=proof['tasks']
    if proof['complete_triangles']!=1229 or {t['parent_triangle'] for t in tasks}!=set(range(1229)) or [t['id'] for t in tasks]!=list(range(len(tasks))):raise ContractError('incomplete cover')
    if len(tasks)!=r['cell_count']:raise ContractError('cell count')
    # Authenticate native accounting and reconstruct exact rational sums without
    # rerunning the old/native integration or trusting its final radius scalar.
    cells={};workers=c['resources']['workers']
    for worker in range(workers):
        lines=(out/f'worker_{worker}.intervals').read_text().splitlines();seen=0
        if not lines or not lines[-1].startswith('DONE '):raise ContractError('native missing DONE')
        for line in lines[:-1]:
            a=line.split()
            if len(a)!=326 or a[0]!='CELL':raise ContractError('native line format')
            idx=int(a[1])
            if idx in cells or idx%workers!=worker:raise ContractError('duplicate/native worker partition')
            nums=list(map(int,a[2:]));cells[idx]=[(F(nums[j],1<<256),F(nums[j+1],1<<256)) for j in range(0,324,2)]
            if any(lo>hi for lo,hi in cells[idx]):raise ContractError('reversed native interval')
            seen+=1
        if lines[-1].split()!=['DONE',str(seen)]:raise ContractError('native DONE count')
    if set(cells)!=set(range(len(tasks))):raise ContractError('missing native cells')
    total=[[F(0),F(0)] for _ in range(162)];errors=[F(0)]*81;checks=0
    for ix,t in enumerate(tasks):
        u0,u1,w0,w1=map(F,t['box']);hu=(u1-u0)/2;hw=(w1-w0)/2;n=t['n'];rho=F(proof['rho'])
        k=F(64,15)/((rho-1)*rho**(2*n-1))
        if n not in c['degrees'] or hu<=0 or hw<=0:raise ContractError('cell quadrature')
        for j in range(81):
            error=F(t['errors'][j//9][j%9]);mu=F(t['mu'][j//9][j%9]);mw=F(t['mw'][j//9][j%9])
            if min(error,mu,mw)<0 or error<2*hu*hw*k*(mu+mw):raise ContractError('Gaussian remainder inequality')
            errors[j]+=error;checks+=1
        for j,(lo,hi) in enumerate(cells[ix]):total[j][0]+=lo;total[j][1]+=hi
    if len(e['entries'])!=81:raise ContractError('enclosure matrix shape')
    for j in range(81):
        for component,slot in [('re',2*j),('im',2*j+1)]:
            lo,hi=interval(e['raw_quadrature_entries'][j][component])
            if lo>total[slot][0] or hi<total[slot][1]:raise ContractError('raw enclosure does not contain native sum')
            el,eh=interval(e['entries'][j][component])
            if el>total[slot][0]-errors[j] or eh<total[slot][1]+errors[j]:raise ContractError('final enclosure misses error-expanded sum')
            checks+=2
    _,radius,_=moments(e['entries'])
    if F(e['full_cross_radius_upper'])<radius or F(r['full_cross_radius_upper'])<radius:raise ContractError('understated radius')
    if r['target_met']!=(F(r['full_cross_radius_upper'])<=F(c['target_radius'])):raise ContractError('target status inconsistency')
    e['return_review']={'read_only':True,'arithmetic_checks':checks,'not_an_independent_scattering_run':True}
    return e

def collect(batch_path,output,root=ROOT):
    b=validate_batch(batch_path,root);ap=Path(batch_path).parent/'AUTHORIZATION.json'
    if ap.exists():
        a=read(ap)
        if a['batch_sha256']!=sha(batch_path):raise ContractError('authorization hash')
    packets=[];reviews=[]
    for item in b['nodes']:
        p=verify_node_payload(b,item,root)
        if p is not None:
            if not ap.exists() or p['node_id'] not in a['authorized_nodes']:raise ContractError('unauthorized return')
            packets.append(p);reviews.append({'node_id':p['node_id'],**p['return_review']})
    reg=read(Path(root)/'inputs/NODE_REGISTRY.json');result=assemble_packets(reg,packets,root=Path(root))
    result['batch_sha256']=sha(batch_path);result['return_reviews']=reviews
    write_new(output,result);return result
