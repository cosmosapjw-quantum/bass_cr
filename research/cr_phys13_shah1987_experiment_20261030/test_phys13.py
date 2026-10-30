import csv,io,json,math,tempfile,unittest,zipfile
from pathlib import Path
import numpy as np
import phys13_shah as P
ROOT=Path(__file__).resolve().parent

class TestShah1987Source(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.table,cls.E,cls.S,cls.err=P.load_shah(ROOT/'data_shah1987.csv')
        cls.result=json.loads((ROOT/'results/RESULT.json').read_text())
    def test_original_sample_size(self):self.assertEqual(len(self.E),26)
    def test_three_primary_anchor_values(self):
        self.assertEqual((self.E[0],self.S[0],self.err[0]),(14.6,0.544,0.025))
        self.assertEqual((self.E[24],self.S[24],self.err[24]),(20.9,3.34,0.02))
        self.assertEqual((self.E[25],self.S[25],self.err[25]),(21.4,3.39,0.04))
    def test_unit_scale(self):
        cov,_,sigma,*_=P.sigma_models(np.array([14.6]),self.E,self.S,self.err)
        self.assertTrue(bool(cov[0]));self.assertAlmostEqual(sigma[0]/1e-21,0.544)
    def test_20_99_is_inside_measured_anchors(self):
        cov,eligible,*_=P.sigma_models(np.array([20.99]),self.E,self.S,self.err)
        self.assertTrue(cov[0]);self.assertTrue(eligible[0])
    def test_sub_14_6_is_not_reported_measured(self):
        cov,eligible,sigma,*_=P.sigma_models(np.array([13.7,14.59]),self.E,self.S,self.err)
        self.assertTrue(np.all(eligible));self.assertFalse(np.any(cov));self.assertEqual(float(sigma.sum()),0.)
    def test_no_nonpositive_measurement(self):self.assertTrue(np.all(self.S>0));self.assertTrue(np.all(self.err>0))
    def test_uncertainty_scenarios_order(self):
        c,_,s,l,u=P.sigma_models(np.linspace(14.6,20.99,100),self.E,self.S,self.err)
        self.assertTrue(np.all(c));self.assertTrue(np.all((l<=s)&(s<=u)))
    def test_bounds_contained_by_kinematic_eligible(self):
        for row in self.result['final'].values():
            self.assertLessEqual(row['Shah_plus_uncertainty_scenario_m3'],row['PHYS11_kinematic_H_capacity_m3'])
            self.assertGreaterEqual(row['unmeasured_kinematic_capacity_m3'],0.)
    def test_measured_fraction_between_0_and_1(self):
        for row in self.result['final'].values():self.assertGreater(row['Shah_measured_fraction_of_kinematic_cap'],0.);self.assertLess(row['Shah_measured_fraction_of_kinematic_cap'],1.)
    def test_causal_t0_zero(self):
        with (ROOT/'results/TIME_TOTAL_OBSERVED_COVERAGE.csv').open() as file:
            rows=list(csv.DictReader(file))
        for x in rows[:3]:
            self.assertEqual(float(x['first_total_m3']),0.)
            self.assertEqual(float(x['Shah_central_observed_coverage_second_m3']),0.)
    def test_ordering_and_sensitivity(self):
        for row in self.result['final'].values():
            a,b,c=[row[k] for k in ['Shah_minus_uncertainty_scenario_m3','Shah_central_observed_coverage_second_m3','Shah_plus_uncertainty_scenario_m3']]
            self.assertTrue(0<=a<=b<=c)
            self.assertTrue(0<=row['Shah_central_log_common_norm_sensitivity_m3']<=b)
    def test_same_support_compare_is_fair(self):
        a=self.result['final']['earliest'];self.assertGreater(a['Kim_on_same_Shah_measured_support_second_m3'],0)
        self.assertAlmostEqual(a['Shah_over_Kim_same_support'],a['Shah_central_observed_coverage_second_m3']/a['Kim_on_same_Shah_measured_support_second_m3'])
    def test_original_archive_sha_rejection(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'bad.zip';f.write_bytes(b'invalid');
            with self.assertRaisesRegex(ValueError,'PHYS12_SOURCE_BYTES_WRONG'):P.load_original(f)
    def test_source_archive_identity_and_6400(self):
        _,res=P.load_original(ROOT/'sources/PR137_ORIGINAL_SOURCE.zip');_,edges,prep,pars,dens=res
        self.assertEqual(sum(len(z['energy']) for z in prep),6400)
        self.assertEqual(float(dens['HI']),138.6)
    def test_integration_limits(self):
        k=np.array([1e-12]);allk=np.array([3e-12]);nu=np.array([1e-12])
        self.assertEqual(float(P.second_p(k,allk,nu,-1)[0]),0.)
        self.assertEqual(float(P.second_p(k,allk,nu,0)[0]),0.)
        self.assertGreater(float(P.second_p(k,allk,nu,1e9)[0]),0.)
    def test_analytic_uniform_sigma_derivative_against_fd(self):
        k=np.array([2e-12,3e-12]);allk=np.array([4e-12,5e-12]);nu=np.array([1e-12,3e-12]);dt=1e9;h=1e-4
        lhs=P.second_dlogscale(k,allk,nu,dt)
        rhs=(P.second_p(k,allk,nu*math.exp(h),dt)-P.second_p(k,allk,nu*math.exp(-h),dt))/(2*h)
        self.assertTrue(np.allclose(lhs,rhs,rtol=2e-8,atol=0.))
    def test_26_measured_rows_and_6400_atoms(self):
        for name,n in [('SHAH1987_MEASURED_26.csv',26),('SOURCE_ATOM_OBSERVED_CROSSWALK.csv',6400),('TIME_TOTAL_OBSERVED_COVERAGE.csv',27),('TIME_CHANNEL_OBSERVED_COVERAGE.csv',54),('FINAL_SOURCE_ENERGY_BINS.csv',92)]:
            with (ROOT/'results'/name).open() as f:self.assertEqual(len(list(csv.DictReader(f))),n)
    def test_all_27_parent_first_and_capacity_rows(self):
        parent=ROOT/'sources/PR137_ORIGINAL_SOURCE.zip'
        with zipfile.ZipFile(parent) as z:
            nested=z.read('research/cr_phys12_kim1992_h_eii_20261030/sources/PR136_ORIGINAL_SOURCE.zip')
        with zipfile.ZipFile(io.BytesIO(nested)) as z:
            raw=z.read('research/cr_phys11_secondary_capacity_20261030/results/TIME_TOTAL_CAPACITY.csv').decode()
        rows_parent=list(csv.DictReader(io.StringIO(raw)))
        with (ROOT/'results/TIME_TOTAL_OBSERVED_COVERAGE.csv').open() as file:
            rows_current=list(csv.DictReader(file))
        self.assertEqual(len(rows_parent),27)
        for a,b in zip(rows_parent,rows_current):
            self.assertEqual((a['observation_s'],a['birth_policy']),(b['observation_s'],b['birth_policy']))
            for k1,k2 in [('total_first_m3','first_total_m3'),('H_secondary_upper_events_m3','PHYS11_kinematic_H_capacity_m3')]:
                self.assertTrue(math.isclose(float(a[k1]),float(b[k2]),rel_tol=1e-14,abs_tol=1e-42), (k1,k2,a,b))
    def test_source_support_maximum_below_last_measured_knot(self):
        _,(owner,edges,prep,params,dens)=P.load_original(ROOT/'sources/PR137_ORIGINAL_SOURCE.zip')
        em=max(float(np.max(z['energy'])) for z in prep)
        self.assertLess(em-float(params['HI'][0]),21.4)
        self.assertGreater(em-float(params['HI'][0]),20.9)
    def test_brackets_not_confidence_claim(self):self.assertIn('NOT rigorous',self.result['uncertainty_scenario'])

if __name__=='__main__':unittest.main(verbosity=2)
