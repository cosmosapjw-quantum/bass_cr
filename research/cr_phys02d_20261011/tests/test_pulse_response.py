import importlib.util,pathlib,unittest
import numpy as np
from scipy import sparse
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('pulse',ROOT/'src/pulse_response.py');pulse=importlib.util.module_from_spec(spec);spec.loader.exec_module(pulse)
class PulseTests(unittest.TestCase):
    def run_toy(self,a=2.,b=None,T=7.,cutoff=0.):
        if b is None:
            G=np.array([[-a,0,0],[a,0,0],[0,0,0.]])
            source=np.array([[1.,.5],[0,0],[cutoff,cutoff]])
            return pulse.pulse_response(G,source,1,1,[1,1,1],T)
        G=np.array([[-b,a,0],[0,-a,0],[b,0,0.]])
        return pulse.pulse_response(G,[[0,0],[1,.5],[0,0]],2,2,[1,1,1],T)
    def test_one_pole(self):
        r=self.run_toy();u=np.array(r['sample_u']);s=r['selected']
        np.testing.assert_allclose(s['cdf'],1-np.exp(-2*u),rtol=2e-10,atol=5e-13)
        np.testing.assert_allclose(s['kernel_per_s'],2*np.exp(-2*u)/7*1.5,rtol=2e-10,atol=5e-13)
        self.assertAlmostEqual(s['mean_lag_s'],7/2);self.assertAlmostEqual(s['second_moment_s2'],2*49/4)
        self.assertAlmostEqual(s['J1']/1.5,1-(1-np.exp(-2))/2)
        self.assertAlmostEqual(s['J2']/1.5,.5-.5+(1-np.exp(-2))/4)
    def test_two_stage_unequal(self):
        s=self.run_toy(a=2,b=3)['selected'];u=np.arange(17)/16
        np.testing.assert_allclose(s['cdf'],1-(3*np.exp(-2*u)-2*np.exp(-3*u)),rtol=2e-10,atol=5e-13)
        self.assertAlmostEqual(s['mean_lag_s'],7*(1/2+1/3))
        self.assertAlmostEqual(s['second_moment_s2'],49*(2/4+2/9+2/6))
    def test_equal_erlang(self):
        s=self.run_toy(a=2,b=2)['selected'];u=np.arange(17)/16
        np.testing.assert_allclose(s['cdf'],1-np.exp(-2*u)*(1+2*u),rtol=2e-10,atol=5e-13)
        self.assertAlmostEqual(s['mean_lag_s'],7);self.assertAlmostEqual(s['second_moment_s2'],49*6/4)
    def test_direct_cutoff_preserved(self):
        r=self.run_toy(cutoff=.25);np.testing.assert_array_equal(r['pulse_states'][0,2,:],np.full(2,.25));np.testing.assert_allclose(r['pulse_states'][:,2,:],np.full((17,2),.25),rtol=2e-10,atol=5e-13);self.assertLess(np.max(np.abs(r['energy_residuals'])),5e-13)
    def test_time_scaling(self):
        a=self.run_toy(T=7)['selected'];b=self.run_toy(T=14)['selected']
        self.assertEqual(b['mean_lag_s'],2*a['mean_lag_s']);self.assertEqual(b['second_moment_s2'],4*a['second_moment_s2']);np.testing.assert_allclose(b['kernel_per_s'],np.array(a['kernel_per_s'])/2)
    def test_saved_cdf_bounds_and_violation(self):
        r=self.run_toy();R=1-(1-np.exp(-2))/2;S=2*(.5-.5+(1-np.exp(-2))/4)
        result=pulse.check_saved_cdf_bounds(r['sample_u'],r['selected']['cdf'],R,S,{'synthetic_toy_reference':True})
        self.assertTrue(result['pass']);self.assertEqual(len(result['checks']),4)
        invalid=np.array(r['selected']['cdf']);invalid[-1]=1.1
        self.assertFalse(pulse.check_saved_cdf_bounds(r['sample_u'],invalid,R,S,{'synthetic_toy_reference':True})['pass'])
    def test_invalid_and_zero_yield(self):
        for G,source,n,heat,ef in [([[1,0],[0,0]],[[1],[0]],1,1,[1,1]),([[-1,0],[1,0]],[[1],[.1]],1,1,[1,1]),([[-2,-1,0],[0,-1,0],[2,2,0]],[[0],[1],[0]],2,2,[1,1,1])]:
            with self.assertRaises(ValueError):pulse.pulse_response(G,source,n,heat,ef)
        r=pulse.pulse_response([[-1,0,0],[0,0,0],[1,0,0]],[[1],[0],[0]],1,1,[1,1,1]);self.assertEqual(r['selected']['status'],'UNDEFINED_ZERO_HEAT_YIELD')
if __name__=='__main__':unittest.main()
