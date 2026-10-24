#!/usr/bin/env python3
"""Create three narrow central proposals from root-supplied actual status. No science runs."""
import argparse, copy, hashlib, json, pathlib, re, sys, time
CHILD = 'CR_N5_PROVIDER_RATE_SEMANTICS_AND_CE_ENVELOPE'
PARENT = 'CR_N5_ATOMIC_ISOTOPE_COVERAGE'
RETURN_NAME = CHILD + '_20261024.json'
RECEIPT_KEYS = {'documents_commit', 'publication', 'backup', 'delivery_receipts'}

def sha(b): return hashlib.sha256(b).hexdigest()
def readj(p): return json.loads(pathlib.Path(p).read_bytes())
def dump(x): return (json.dumps(x, ensure_ascii=False, indent=2, allow_nan=False)+'\n').encode()
def require(ok, msg):
    if not ok: raise ValueError(msg)
def actual(x):
    return x is not None and str(x).strip() != '' and not re.search(r'PENDING|UNOBSERVED|SYNTHETIC|DRAFT|PLACEHOLDER',str(x),re.I)
def identity(x): return {k: x.get(k) for k in ('child','science_commit','science_tree','PR','run_id')}
def without_receipts(x):
    y=copy.deepcopy(x)
    for k in RECEIPT_KEYS: y.pop(k,None)
    if isinstance(y.get('axes'),dict):
        for k in ('PUBLICATION','BACKUP'): y['axes'].pop(k,None)
    return y

def main():
    start=time.process_time(); p=argparse.ArgumentParser(description=__doc__)
    for k in ('status','dag','handoff','expected-sha','variant-id','out'): p.add_argument('--'+k,required=True)
    p.add_argument('--variant',choices=['initial','final'],required=True)
    p.add_argument('--existing-return')
    a=p.parse_args(); status=readj(a.status); r=copy.deepcopy(status.get('return',status))
    require(re.fullmatch('[0-9a-f]{40}',a.expected_sha),'expected SHA must be exact Git commit')
    require(re.fullmatch('[A-Za-z0-9_.-]+',a.variant_id),'variant-id must be explicit and filename-safe')
    require(r.get('child')==CHILD and r.get('node')==PARENT,'wrong child or parent')
    require(r.get('draft') is False and r.get('publishable') is True,'actual publishable return required')
    require(not r.get('draft_reason'),'remove draft_reason')
    for k in ('science_commit','science_tree'):
        require(isinstance(r.get(k),str) and re.fullmatch('[0-9a-f]{40}',r[k]),k+' required')
    for k in ('PR','run_id','results_path','raw_path','status','admission','independent_Astra_review','measured_results','checks'):
        require(actual(r.get(k)),k+' actual required')
    require(re.fullmatch(r'https://github.com/cosmosapjw-quantum/bass_cr/pull/[0-9]+',r['PR']),'actual science PR required')
    require('PASS' in str(r['independent_Astra_review']),'independent PASS required')
    budget=r.get('budget',{})
    for k in ('new_child_cpu_s','new_child_wall_s','known_tracked_lineage_cpu_s'):
        v=budget.get(k); require(isinstance(v,(float,int)) and not isinstance(v,bool) and v>=0,'actual budget '+k+' required')
    axes=r.get('axes',{})
    require(set(axes)=={'EXECUTION','PUBLICATION','BACKUP','DAG'},'four actual axes required')
    require(actual(axes['EXECUTION']) and actual(axes['DAG']),'execution/DAG axes cannot be pending')
    if r.get('documents_commit') is None:
        require('PENDING' in axes['PUBLICATION'].upper(),'null documents requires explicit publication pending axis')
    else: require(re.fullmatch('[0-9a-f]{40}',r['documents_commit']),'invalid documents commit')
    if any(v is None for k,v in r.get('backup',{}).items()):
        require('PENDING' in axes['BACKUP'].upper(),'null backup receipt requires explicit pending axis')
    r['central_base']=a.expected_sha
    original=pathlib.Path(a.dag).read_bytes(); d=json.loads(original); old=copy.deepcopy(d)
    require(len(d['nodes'])==40 and len(d['authorities'])==7 and len(d['integration']['edges'])==17,'central shape changed; return to root')
    ns=[n for n in d['nodes'] if n['id']==PARENT]; require(len(ns)==1,'N5 exact selector ambiguous')
    n=ns[0]; op=n['observed_progress']; children=op.setdefault('additional_children',[])
    matches=[(i,c) for i,c in enumerate(children) if c.get('child',c.get('id'))==CHILD]
    require(len(matches)<=1,'duplicate owned child')
    entry=copy.deepcopy(r)
    if matches:
        i,existing=matches[0]; require(identity(existing)==identity(entry),'existing child science identity differs')
        if a.variant=='initial': require(existing==entry,'initial cannot change existing child')
        else:
            require(a.existing_return,'final requires existing-return')
            prev=readj(a.existing_return)
            # central_base is a patch receipt and naturally changes with the fresh base.
            for obj in (prev,existing): obj.pop('central_base',None)
            check=copy.deepcopy(entry); check.pop('central_base',None)
            require(without_receipts(prev)==without_receipts(check),'final return changes science or non-receipt fields')
            require(without_receipts(existing)==without_receipts(check),'final child changes non-receipt fields')
            children[i]=entry
    else:
        require(a.variant=='initial','final requires an existing owned child')
        children.append(entry)
    # Remove only the owned child from both sides; all concurrent fields remain exact.
    def stripped(obj):
        obj=copy.deepcopy(obj); nn=next(t for t in obj['nodes'] if t['id']==PARENT)
        cc=nn['observed_progress'].get('additional_children',[])
        cc=[c for c in cc if c.get('child',c.get('id'))!=CHILD]
        if cc: nn['observed_progress']['additional_children']=cc
        else: nn['observed_progress'].pop('additional_children',None)
        return obj
    require(stripped(old)==stripped(d),'unowned central content changed')
    for x,y in zip(old['nodes'],d['nodes']): require(x['contract']==y['contract'],'contract changed')
    handoff=pathlib.Path(a.handoff).read_bytes()
    marker='<!-- N5_CE_PUBLICATION_'+a.variant_id+' -->'
    require(marker.encode() not in handoff,'variant already in handoff; use a fresh variant')
    section='\n\n'+marker+'\n## N5 CE child — '+a.variant_id+'\n\n'
    section+='Child: `'+CHILD+'`; parent N5 `PARTIAL/OPEN`; N4 `PARTIAL/OPEN`; N6/N7 predecessor gates remain open.\n\n'
    section+='Science: `'+r['science_commit']+'`; '+r['PR']+'; run `'+r['run_id']+'`. Review: '+str(r['independent_Astra_review'])+'.\n\n'
    section+='Return: `returns/'+RETURN_NAME+'`. Existing C23E: `returns/CR_N5_C23E_D43_SOURCE_BINDING_20261024.json` (preserved).\n\n'
    section+='Conditional finite-band first-CE-event diagnostic with n_H(1s)=0.9 cm^-3. Initial 0<W<10 eV is selection only; CE envelope covers the full admitted R80 path. Thermal target rates and tagged CE hazards remain distinct. Missing rates and total non-EE bound remain null. PHYS84 numerical admission WAIT and HE-ANG full law SOURCE_INPUT_PENDING remain.\n\n'
    section+='\n\n'.join(k+': '+str(axes[k]) for k in ('EXECUTION','PUBLICATION','BACKUP','DAG'))+'\n'
    newhandoff=handoff+section.encode(); require(newhandoff.startswith(handoff),'handoff prefix changed')
    out=pathlib.Path(a.out); require(not out.exists(),'output directory must be create-only'); out.mkdir(parents=True)
    (out/'returns').mkdir()
    outputs={pathlib.Path('returns')/RETURN_NAME:dump(r),pathlib.Path('DAG.json'):dump(d),pathlib.Path('HANDOFF_bass_cr_KO.md'):newhandoff}
    for name,data in outputs.items():
        with (out/name).open('xb') as f:f.write(data)
    print(json.dumps({'schema':'N5_CENTRAL_PRESERVATION_RECEIPT_V1','variant':a.variant,'variant_id':a.variant_id,'expected_sha':a.expected_sha,'original_dag_sha256':sha(original),'handoff_prefix_bytes':len(handoff),'handoff_prefix_sha256':sha(handoff),'all_40_contracts_preserved':True,'other_39_wrappers_preserved':True,'authorities_7_and_integration_17_edges_preserved':True,'N5_unowned_progress_preserved':True,'changed_paths':[str(k) for k in outputs],'outputs':{str(k):{'bytes':len(v),'sha256':sha(v)} for k,v in outputs.items()},'requested_model':'gpt-6.1-sol','observed_runtime_model':'UNOBSERVED','helper_process_cpu_s':time.process_time()-start},ensure_ascii=False,indent=2))
if __name__=='__main__':
    try: main()
    except (ValueError,KeyError,TypeError) as e: sys.exit(str(e))
