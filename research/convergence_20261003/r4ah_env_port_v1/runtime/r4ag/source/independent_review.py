"""Independent, read-only R4AG contract and arithmetic review (no integrals)."""
from fractions import Fraction as F
from pathlib import Path
import sys,json,hashlib
from common import ROOT,read,sha,write_new,CANDIDATE

def derivative_weights(nodes):
    out=[]
    for j,xj in enumerate(nodes):
        p=[F(1)];den=F(1)
        for k,xk in enumerate(nodes):
            if j==k:continue
            q=[F(0)]*(len(p)+1)
            for n,a in enumerate(p):q[n]-=xk*a;q[n+1]+=a
            p=q;den*=xj-xk
        out.append(p[1]/den)
    return out

def review(output):
    count=0
    def check(condition,message):
        nonlocal count
        if not condition:raise AssertionError(message)
        count+=1
    lock=read(ROOT/'SOURCE_INPUT_LOCK.json')
    for name,h in lock['pins'].items():check(sha(ROOT/name)==h,'pin '+name)
    rows=read(ROOT/'inputs/NODE_REGISTRY.json')['nodes']
    check(len(rows)==len({r['node_id'] for r in rows})==10,'unique nodes')
    for r in rows:
        g=read(ROOT/r['geometry_path'])['geometry'];v=F(*float(g['speed_a0_per_ta']).as_integer_ratio())
        check(F(r['z_a0'])==F(*float.fromhex(g['actual_z_hex']).as_integer_ratio()),'z hex')
        check(F(r['time_ta'])==F(*float.fromhex(g['time_hex']).as_integer_ratio()),'epoch hex')
        check(F(r['offset_a0'])==F(r['z_a0'])+32,'offset')
        check(F(r['v_a0_per_ta'])==v,'v exact')
        check(sha(ROOT/r['S_path'])==r['S_sha256'],'S identity')
    coverage=[]
    for den in (64,128):
        w=read(ROOT/f'evidence/parents/STENCIL_H{den}.json');nodes=list(map(F,w['nodes']));v=F(w['speed_a0_per_ta'])
        computed=[v*a for a in derivative_weights(nodes)]
        check(computed==list(map(F,w['weights'])),'independent Lagrange weights')
        for degree in range(9):
            check(sum(a*x**degree for a,x in zip(computed,nodes))==(v if degree==1 else 0),'polynomial response')
        coverage.append(set(nodes))
    check(len(coverage[0]|coverage[1])==10 and len(coverage[0]&coverage[1])==6,'shared node count')
    empty=read(ROOT/'results/UNEXECUTED_STENCIL_STATE.json')
    check(empty['available_nodes']==0,'no actual samples')
    for w in empty['windows']:
        check(w['total_upper'] is None and w['within_final_target'] is None,'missing total null')
        check(w['midpoint'] is None and len(w['missing_nodes'])==8,'missing matrix null')
    check(empty['D_read'] is False and empty['M9_recomputed'] is False,'scope')
    # Verify vendor identity against the parent manifest, not a new numerical replay.
    parent={x['path']:x['sha256'] for x in read(ROOT/'evidence/parents/R4AF_MANIFEST.json')['files']}
    for p in (ROOT/'vendor_af').glob('*'):
        if p.is_file():check(sha(p)==parent['source/'+p.name],'vendor AF '+p.name)
    for p in (ROOT/'vendor_r4ae').glob('*'):
        if p.is_file():check(sha(p)==parent['vendor_r4ae/'+p.name],'vendor AE '+p.name)
    result={'schema':'R4AG_READ_ONLY_REVIEW_V1','status':'PASS','conditions':count,'atomic_integrals':0,'old_tests_or_calculations_replayed':0,'scope':'new source/input identity, independent Lagrange response, shared coverage, and no-result semantics; not numerical validation of the unexecuted shifted batch','independent_human_or_agent':False,'source_lock_sha256':sha(ROOT/'SOURCE_INPUT_LOCK.json')}
    write_new(output,result);print(json.dumps(result,indent=2))
if __name__=='__main__':review(sys.argv[1])
