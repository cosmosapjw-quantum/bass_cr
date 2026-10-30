#!/usr/bin/env python3
"""Targeted tests against published Kim fit, exact source, and finite-horizon bound."""
import unittest, numpy as np, math, tempfile, zipfile
from pathlib import Path
import phys12_h_eii as p

HERE=Path(__file__).resolve().parent
SOURCE=HERE/'sources/PR136_ORIGINAL_SOURCE.zip'

class PhysicsTests(unittest.TestCase):
    def test_source_locked(self):
        mod,edges,prep,params,dens=p.load_owner(SOURCE)
        self.assertEqual(sum(len(x['energy']) for x in prep),6400)
        self.assertEqual(float(dens['HI']),138.6)
        self.assertEqual(float(params['HI'][0]),13.60)
    def test_bad_source_hash_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            f=Path(td)/'broken.zip';f.write_bytes(SOURCE.read_bytes()+b'corrupt')
            with self.assertRaisesRegex(ValueError,'SOURCE_SHA256_MISMATCH'):p.load_owner(f)
    def test_zero_below_fit_threshold(self):
        r=p.kim_sigma_m2(np.array([0.,13.6,13.6099999,13.61]))
        np.testing.assert_array_equal(r,np.zeros(4))
    def test_published_fit_values(self):
        sigma=p.kim_sigma_m2(np.array([14.6,15.6,17.6,20.99]))
        values=np.array([5.86548668811338e-22,1.1244913540162464e-21,2.0542560947664455e-21,3.268196090912976e-21])
        np.testing.assert_allclose(sigma,values,rtol=5e-13,atol=0)
    def test_sigma_positive_and_monotone_in_scope(self):
        Es=np.linspace(13.61,20.99,4000)
        s=p.kim_sigma_m2(Es)
        self.assertTrue(np.all(s>=0))
        self.assertTrue(np.all(np.diff(s)>=0))
        v=p.velocity_m_s(Es)
        self.assertTrue(np.all(np.diff(s*v)>=0))
    def test_units_at_20_99(self):
        s,v,k,kap,nu=p.eii_micro(np.array([20.99]),138.6)
        self.assertAlmostEqual(v[0],2717264.5059270244,delta=2e-5)
        self.assertAlmostEqual(kap[0],4.529719782005384e-19,delta=4e-30)
        self.assertAlmostEqual(nu[0],1.2308446785438729e-12,delta=1e-22)
    def test_zero_time(self):
        v=np.array([1e-11,2e-11])
        np.testing.assert_array_equal(p.bound_probability(v,v,np.array([1e-12,2e-12]),0),np.zeros(2))
        np.testing.assert_array_equal(p.bound_probability(v,v,np.array([1e-12,2e-12]),-1),np.zeros(2))
    def test_second_without_first_zero(self):
        v=np.array([0.,0.])
        np.testing.assert_array_equal(p.bound_probability(v,np.array([1e-11,4e-11]),np.array([1e-12,1e-12]),1e10),np.zeros(2))
    def test_first_without_second_zero(self):
        v=np.array([1e-11,4e-11])
        np.testing.assert_array_equal(p.bound_probability(v,v,np.zeros(2),1e10),np.zeros(2))
    def test_probability_dominated_by_first(self):
        ka=np.array([1e-11,3e-11]);kb=np.array([1e-12,4e-11]);nu=np.array([1e-12,2e-12]);dt=1e10
        two=p.bound_probability(ka,ka+kb,nu,dt)
        first=ka/ (ka+kb)*(-np.expm1(-(ka+kb)*dt))
        self.assertTrue(np.all(two>=0));self.assertTrue(np.all(two<=first))
    def test_closed_form_independent(self):
        # Independent closed-form integration, not the quadrature algorithm.
        for ka,khe,nu,dt in [(2.51e-11,1.3e-11,1.1e-12,1e10),(1e-11,5e-12,5e-13,2.5e9), (1e-13,1.5e-13,2e-15,7.5e9)]:
            k=ka+khe
            direct=ka*((-math.expm1(-k*dt))/k-(math.exp(-nu*dt)-math.exp(-k*dt))/(k-nu))
            actual=p.bound_probability(np.array([ka]),np.array([k]),np.array([nu]),dt)[0]
            self.assertAlmostEqual(actual,direct,delta=max(abs(direct)*2e-9,3e-14))
    def test_gradient_H_matches_finite_difference(self):
        ka=np.array([1e-11,2e-11]);he=np.array([1.5e-11,8e-12]);nu=np.array([2e-13,9e-13]);dt=7.5e9;h=1e-5
        A=p.bound_gradient_uniform(ka,he,nu,dt,'HI')
        plus=p.bound_probability(ka*np.exp(h),ka*np.exp(h)+he,nu*np.exp(h),dt)
        minus=p.bound_probability(ka*np.exp(-h),ka*np.exp(-h)+he,nu*np.exp(-h),dt)
        np.testing.assert_allclose(A,(plus-minus)/(2*h),rtol=2e-8,atol=1e-12)
    def test_gradient_He_matches_finite_difference(self):
        ka=np.array([1e-11,2e-11]);he=np.array([1.5e-11,8e-12]);nu=np.array([2e-13,9e-13]);dt=7.5e9;h=1e-5
        A=p.bound_gradient_uniform(ka,he,nu,dt,'HeI')
        plus=p.bound_probability(ka,ka+he*np.exp(h),nu,dt)
        minus=p.bound_probability(ka,ka+he*np.exp(-h),nu,dt)
        np.testing.assert_allclose(A,(plus-minus)/(2*h),rtol=3e-8,atol=1e-12)
    def test_monotone_in_time(self):
        ka=np.array([1e-11,2e-11]);he=np.array([1.5e-11,8e-12]);nu=np.array([2e-13,9e-13])
        vals=[p.bound_probability(ka,ka+he,nu,x) for x in np.linspace(0,1e10,8)]
        self.assertTrue(np.all(np.diff(vals,axis=0)>=-1e-16))
    def test_parent_kinematic_threshold_retained(self):
        self.assertEqual(p.KM_I_EV,13.61)
        self.assertNotEqual(p.KM_I_EV,13.60)
    def test_no_stage_production_claim(self):
        self.assertIn('Kim',p.SOURCE_REF)

if __name__=='__main__':unittest.main()
