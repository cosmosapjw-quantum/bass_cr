"""Bounded analytic fixtures, not an atomic matrix evaluation."""
from pathlib import Path
import sys,json,time,hashlib
from fractions import Fraction as F
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'source'),str(ROOT/'vendor')]
from weak_kernel import Candidate,Context,Cell
from geometry import Triangle,Affine
from cubature import Budget,cell_enclosure,dump_enclosure
from dyadic import I,SCALE

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    contract=json.loads((ROOT/'contracts/LIGHT_FIXTURE_CONTRACT.json').read_text())
    for name,h in contract['source_pins'].items():
        if sha(ROOT/name)!=h:raise ValueError('changed fixture source')
    out=ROOT/'evidence/LIGHT_FIXTURE_RESULT.json'
    if out.exists():raise FileExistsError('fixture run is one shot')
    a=F(1,8);edges=(F(0),a,F(1),F(2),F(4),F(8))
    coeff=tuple((lo,hi-lo,F(0),F(0),F(0)) for lo,hi in zip(edges,edges[1:]))
    cand=Candidate(edges,(coeff,coeff),(0,1),'LOCAL_MANUFACTURED_FIELD_U_EQUALS_R')
    ctx=Context(3,4,0,0)
    tri=Triangle(3,4,((Affine(F(2)),Affine(F(4))),(Affine(F(3)),Affine(F(4))),(Affine(F(3)),Affine(F(5)))),(F(1),F(0),F(0)))
    fixtures=[(Cell('origin_T',0,4),{'S_TP':a**3/3,'H_TP':-a*a/2-a**3/15,'K_TP':-a*a/2-a**3/15,'D_TP':F(0)}),
              (Cell('origin_P',4,0),{'S_TP':a**3/3,'H_TP':-a*a/2-a**3/15,'K_TP':-a*a/2-a**3/15,'D_TP':F(0)}),
              (Cell('regular',3,4,tri),{'S_TP':F(139,240),'H_TP':F(-7,20),'K_TP':F(-7,20),'D_TP':F(0)})]
    start=time.monotonic();budget=Budget(contract['max_evaluations'],start+contract['wall_seconds'])
    records=[]
    for cell,expected in fixtures:
        r=cell_enclosure(cand,cell,ctx,(0,0,0,0),n=contract['degree'],rho=F(contract['rho']),budget=budget)
        for k,x in expected.items():
            assert r['values'][k].re.contains(x) and r['values'][k].im.contains(0),(cell.kind,k)
        radius=max(F(r['values'][k].re.hi-r['values'][k].re.lo,2*SCALE)+F(r['values'][k].im.hi-r['values'][k].im.lo,2*SCALE) for k in ('H_TP','K_TP'))
        assert radius<=F(contract['target_per_complex_entry']),str(radius)
        records.append({'fixture':cell.kind,'expected':{k:str(v) for k,v in expected.items()},'radius_l1_upper':str(radius),'enclosure':dump_enclosure(r)})
    data={'status':'ANALYTIC_FIXTURES_CONTAINED_AND_TARGET_MET','contract_sha256':sha(ROOT/'contracts/LIGHT_FIXTURE_CONTRACT.json'),'fixture_results':records,'wall_seconds':time.monotonic()-start,'evaluations_including_bound_probes':budget.evaluations,'gaussian_nodes':len(fixtures)*contract['degree']**2,'real_atomic_matrix_evaluations':0,'whole_matrix_accuracy_certified':False}
    out.write_text(json.dumps(data,indent=2,sort_keys=True))
    print(json.dumps({'status':data['status'],'wall_seconds':data['wall_seconds'],'gaussian_nodes':data['gaussian_nodes'],'radii':[float(F(x['radius_l1_upper'])) for x in records]}))
if __name__=='__main__':main()
