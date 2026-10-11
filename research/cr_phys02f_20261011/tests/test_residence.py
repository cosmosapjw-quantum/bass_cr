import importlib.util,sys,pathlib,unittest
from fractions import Fraction as F
import numpy as np
from scipy.sparse import csc_matrix
P=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('residence',P/'src/residence.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def exact(A,b,lower=False):
    n=len(A);x=[F(0)]*n
    for i in (range(n) if lower else range(n-1,-1,-1)):
        x[i]=(b[i]-sum(A[i][j]*x[j] for j in range(n) if j!=i))/A[i][i]
    return x
class ResidenceTests(unittest.TestCase):
    def test_all_five_exact_fraction_and_bins(self):
        A=[[F(2),F(-1),F(-1,2)],[F(0),F(3),F(-1)],[F(0),F(0),F(4)]]
        At=[list(x) for x in zip(*A)];h=[F(1),F(1),F(2)]
        qs=[exact(At,h,True)]
        qs.append(exact(At,qs[-1],True));qs.append(exact(At,qs[-1],True))
        bs=[[F(1),F(2),F(3)],[F(3),F(2),F(1)]];xs=[[F(1,10),F(1,5),F(3,10)],[F(3,10),F(1,5),F(1,10)]]
        G=np.zeros((14,14));G[:3,:3]=-np.array(A,float);G[3,:3]=np.array(h,float)
        b=np.array(bs,float).T;x=np.array(xs,float).T;events=[]
        arrays,result=m.diagnostic(csc_matrix(G),np.array([1.,30.,900.]),b,x,3,on_solve=lambda s,n:events.append((s,n)))
        for k,q in zip(('q0','q1','q2'),qs):np.testing.assert_allclose(arrays[k],np.array(q,float),rtol=1e-14)
        for k,rhs in [('w',bs),('v',xs)]:
            oracle=np.array([exact(A,col) for col in rhs],float).T
            np.testing.assert_allclose(arrays[k],oracle,rtol=1e-14)
        self.assertEqual(len(events),10);self.assertEqual(sum(row['states'] for row in result['bins']),3)
        self.assertEqual([row['states'] for row in result['bins']],[1,0,1,0,0,1])
        for j in range(2):
            first=sum(qs[0][i]*exact(A,bs[j])[i] for i in range(3))
            self.assertEqual(first,sum(qs[1][i]*bs[j][i] for i in range(3)))
            self.assertAlmostEqual(result['scalars']['H1'][j]/m.T0,float(first))
    def test_structure_and_physical_bound_fail(self):
        G=np.zeros((12,12));G[0,0]=-1;G[1,0]=2
        with self.assertRaisesRegex(m.ResidenceError,'Q0_PHYSICAL_BOUND'):m.diagnostic(csc_matrix(G),np.array([1.]),np.ones((1,2)),np.ones((1,2)),1)
    def test_signed_crosscheck_and_G_mismatch(self):
        record=m.crosscheck(np.array([1.-1e-13]),np.array([1.]))
        self.assertLess(record['signed_difference'][0],0)
        a={'G':{'shape':[1,1]},'energy_eV':{},'method_bindings':{'f':{'same_parent_object':True,'qualname':'f','module':'a'}}}
        b={'G':{'shape':[1,1]},'energy_eV':{},'method_bindings':{'f':{'same_parent_object':True,'qualname':'f','module':'b'}}}
        m.operator_parity(a,b);b['G']={'shape':[2,2]}
        with self.assertRaisesRegex(m.ResidenceError,'OPERATOR_IDENTITY_MISMATCH'):m.operator_parity(a,b)
    def test_corrupt_whole_file_before_npz_load(self):
        import tempfile,hashlib
        with tempfile.TemporaryDirectory() as t:
            root=pathlib.Path(t);p=root/'bad';p.write_bytes(b'not npz')
            ids={k:{'path':'bad','bytes':7,'sha256':'0'*64} for k in ('fullBED_9600_npz','legacy_9600_npz','actual_fullBED_pulse','actual_legacy_pulse')}
            with self.assertRaisesRegex(m.ResidenceError,'INPUT_FILE_IDENTITY_MISMATCH'):m.preflight_pulses(root,ids,{})
if __name__=='__main__':unittest.main()
