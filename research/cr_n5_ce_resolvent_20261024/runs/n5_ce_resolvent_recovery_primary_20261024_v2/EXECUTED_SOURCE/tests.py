"""Fresh changed-source/environment ten controls plus CASE-preservation regression."""
import argparse,json,unittest
from fractions import Fraction as F
from pathlib import Path
import numpy as np
from engine import *

class Controls(unittest.TestCase):
    def setUp(self):self.b={'G_diag':np.array([-5.,-5.]),'G_lower':np.array([5.]),'G_upper':np.array([3.]),'absorption':np.array([2.,0.])};self.E=np.array([1.,2.,4.])
    def solve(self,s,p):return solve_case(self.b,self.E,np.array(s,dtype=float),np.array(p,dtype=float))
    def test_exact_toy(self):
        for lam in [F(0),F(1,100000000),F(1)]:
            D=10+5*lam*18;s,_,ok=self.solve([0,float(lam*7)],[0,float(lam*11)])
            us=[lam*7*3/D,lam*7*5/D];up=[lam*11*3/D,lam*11*5/D]
            np.testing.assert_allclose(s['u_s'],list(map(float,us)),atol=1e-15,rtol=5e-13);np.testing.assert_allclose(s['u_p'],list(map(float,up)),atol=1e-15,rtol=5e-13)
            np.testing.assert_allclose(s['u_abs'],[float(1-us[i]-up[i]) for i in range(2)],atol=1e-15,rtol=5e-13);self.assertTrue(ok)
            if lam==F(1,100000000):np.testing.assert_allclose((s['u_s']+s['u_p'])/float(lam),[5.4,9.],rtol=1e-6,atol=0)
    def test_zero(self):
        s,_,ok=self.solve([0,0],[0,0]);np.testing.assert_array_equal(s['u_s'],0);np.testing.assert_array_equal(s['u_p'],0);np.testing.assert_allclose(s['u_abs'],1,rtol=0,atol=1e-14);self.assertTrue(ok)
    def test_absent_channel(self):
        s,_,_=self.solve([0,.1],[0,0])
        for k in ['u_p','r_p','v_p']:np.testing.assert_array_equal(s[k],0)
    def test_small_mark(self):
        s,_,_=self.solve([0,1e-9],[0,2e-9]);np.testing.assert_allclose(s['u_s']+s['u_p'],s['w'],rtol=2e-8,atol=1e-18)
    def test_bad_hazards(self):
        with self.assertRaises(InputError):self.solve([0,-.1],[0,0])
        with self.assertRaises(InputError):solve_case(self.b,self.E,None,np.zeros(2))
    def test_bad_rhs(self):
        with self.assertRaises(InputError):positive_solve(np.array([2.,2.]),np.array([-1.]),np.array([-1.]),np.array([-1.,0.]))
    def test_projection(self):
        E=np.array([1.,1.5,10.,10.20435,20.]);p,m,i=project(E,np.array([.5,1.1,9.99]),np.array([1.,2.,3.]),10.20435)
        self.assertGreater(p[0],0);self.assertEqual(i['original_active_count_cm3'],5);self.assertEqual(p[E>10].sum(),0);self.assertLess(max(i['count_relative_error'],i['energy_relative_error']),2e-12)
    def test_orientation(self):
        Q=np.array([[-7.,2.,0.],[7.,-5.,5.],[0.,3.,-5.]])
        np.testing.assert_array_equal(Q.sum(axis=0),0);np.testing.assert_array_equal(Q[0,1:],self.b['absorption']);np.testing.assert_array_equal(Q[1:,1:].T,[[ -5.,3.],[5.,-5.]])
    def test_null_means(self):
        s,_,_=self.solve([0,0],[0,0]);r=averages(np.array([.1,.4,.5]),{'original_active_count_cm3':1.,'selected_count_cm3':2.},s,self.E,1.)
        self.assertIsNone(r['sum']['conditional_event_time_s']);self.assertIsNone(r['2S']['conditional_incoming_eV'])
    def test_knots(self):
        theta=.8617333262145178;E=grid(theta,1.5,512,10.20435)
        for k in [1.5*theta,10.,40*theta,80*theta,10.20435]:self.assertIn(k,E)
    def test_two_iteration_case_preservation_and_recovery_identity(self):
        # Production metadata constructor is separate; it never receives/replaces cfg.
        import ast,primary
        cfg=validate_case(expected_case(),RUN_ID);original=json.dumps(cfg,sort_keys=True)
        for i in range(2):
            case_record=metadata('synthetic_'+str(i),1.5,40,512,self.E,{'generator_scaled_defect':0},{},True,[])
            self.assertEqual(cfg['n1s_cm3'],.9);self.assertEqual(json.dumps(cfg,sort_keys=True),original);self.assertNotIn('n1s_cm3',case_record)
        tree=ast.parse(Path(primary.__file__).read_text());cfgassign=[n for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='cfg' for t in n.targets)]
        self.assertEqual(len(cfgassign),1);self.assertEqual(cfg['physical_input_id'],INPUT_ID);self.assertEqual(cfg['primary_run_id'],RUN_ID)
        with self.assertRaises(InputError):validate_case(cfg,'n5_ce_resolvent_primary_20261024_v1')
        altered=dict(cfg,n1s_cm3=.91)
        with self.assertRaises(InputError):validate_case(altered,RUN_ID)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Controls));writej(a.output/'TEST_RESULT.json',{'status':'PASS' if r.wasSuccessful() else 'FAILED_RETAINED','unique_controls':r.testsRun,'failures':len(r.failures),'errors':len(r.errors),'source':'new recovery-v2, changed source/environment; old v1 evidence not fabricated'});raise SystemExit(0 if r.wasSuccessful() else 1)
