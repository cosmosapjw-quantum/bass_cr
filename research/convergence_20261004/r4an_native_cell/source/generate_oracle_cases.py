"""Six extra native point evaluations for independent Cartesian validation.
Synthetic fields only. These are not atomic integrals or cubature certificates.
"""
from pathlib import Path
import sys,json
from fractions import Fraction as F
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'source'),str(ROOT/'parent/source'),str(ROOT/'parent/vendor')]
from native_adapter import evaluate,serialize,sha,BINARY
from weak_kernel import Candidate,Context,Cell
from geometry import Triangle,Affine
from dyadic import I
from run_parity import dumpc

def main():
    out=ROOT/'evidence/CARTESIAN_CASES.json'
    if out.exists():raise FileExistsError('one-shot fixture evidence exists')
    edges=(F(0),F(1,8),F(1),F(2),F(4),F(8));rows=[]
    for scale in [F(1),F(2,3)]:
        row=[]
        for lo,hi in zip(edges,edges[1:]):
            d=hi-lo
            row.append((scale*(lo-lo*lo/4+lo**3/64),scale*d*(1-lo/2+3*lo*lo/64),scale*d*d*(-F(1,4)+3*lo/64),scale*d**3/64,F(0)))
        rows.append(tuple(row))
    cand=Candidate(edges,tuple(rows),(0,1),'R4AN_SMOOTH_CARTESIAN_FIXTURE')
    ctx=Context(1,3,F(4,5),F(17,5));u,w=F(3,5),F(2,5)
    tri=Triangle(2,3,((Affine(F(1)),Affine(F(3))),(Affine(F(2)),Affine(F(3))),(Affine(F(2)),Affine(F(4)))),(F(1),F(0),F(0)))
    cells=[Cell('regular',2,3,tri),Cell('origin_T',0,3),Cell('origin_P',3,0)];records=[]
    for cell in cells:
        for entry in [(0,1,0,-1),(1,1,1,0)]:
            samples=[(I(u),I(w),I(1))];text=serialize(cand,cell,ctx,entry,samples)
            vals=evaluate(cand,cell,ctx,entry,samples)
            records.append({'chart':cell.kind,'entry':entry,'u':str(u),'w':str(w),'b':'1','z':'3','v':'4/5','t':'17/5','first_radius':'1/8','regular_vertices':[[1,3],[2,3],[2,4]],'radial_formula':'scale*r*(1-r/8)^2; scale_s=1, scale_p=2/3','native_input_sha256':__import__('hashlib').sha256(text.encode()).hexdigest(),'values':{k:dumpc(x) for k,x in vals.items()}})
    out.write_text(json.dumps({'schema':'R4AN_CARTESIAN_FIXTURE_OUTPUT_V1','native_sha256':sha(BINARY),'new_native_point_evaluations':6,'actual_atomic_integrals':0,'records':records},indent=2))
if __name__=='__main__':main()
