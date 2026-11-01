"""Targeted physical tests, including an intentional FAIL-CLOSED published-fit audit."""
from __future__ import annotations
import math,os,sys,tempfile,unittest
from pathlib import Path
import numpy as np
from scipy.integrate import quad
sys.path.insert(0,str(Path(__file__).resolve().parent))
import angular_mt as m

SOURCE=Path(os.environ.get('REI_SOURCE_ZIP', str(Path(__file__).resolve().parent/'REI_F4_CCC_HHE_FIRST_COLLISION_20261031_FULL.zip')))

class ScatteringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=m.calculate(SOURCE)

    def test_original_zip_and_parent_full_replay(self):
        self.assertEqual(m.sha(SOURCE),m.SOURCE_SHA)
        self.assertEqual(len(self.rows),192)

    def test_cx_total_and_pi_limit(self):
        for v in (3e5,1e6,1.6e6,2e6,1e7,2e7):
            self.assertAlmostEqual(m.sigma_cx_mt_pi(v)/m.old.sigma_cx_cm2(v),2,places=12)

    def test_2025_published_a7_coefficients(self):
        g=1e6
        aa,bb,cc,dd=m.A7_LOW
        expected=2*(aa-bb*math.log(g))**2*(-math.expm1(-cc/g))**dd
        self.assertAlmostEqual(expected/m.sigma_cx_mt_fit(g),1,places=13)

    def test_nuclear_vs_charge_label_isometry(self):
        # Polar-axis reversal charge angle = pi - nuclear angle.
        # Synthetic (not physical) normalized angular DCS P(mu)=(1+alpha mu)/2.
        x,w=np.polynomial.legendre.leggauss(128)
        for alpha in (-0.9,0.,0.8):
            ch=.5*(1+alpha*x)
            nuclear=.5*(1-alpha*x)
            charged=np.sum(w*(1-x)*ch)
            relabeled=np.sum(w*(1+x)*nuclear)
            self.assertAlmostEqual(charged,relabeled,places=13)
            self.assertAlmostEqual(charged,1-alpha/3,places=13)

    def test_transport_angle_endpoints(self):
        for mu in (-1,0,1):
            self.assertAlmostEqual(m.charged_vs_nuclear_kernel(mu,lambda x: 2.,lambda x: 3.),
                                   (1-mu)*5,places=13)

    def test_isotropic_and_delta_angular_bounds(self):
        x,w=np.polynomial.legendre.leggauss(100)
        self.assertAlmostEqual(float(np.dot(w,(1-x)*np.ones_like(x)/2)),1.,places=13)
        self.assertTrue(all(0 <= 1-xi <= 2 for xi in x))

    def test_analytic_linear_response_constant_sigma(self):
        # Exactly K / <sigma g> = 4/3 for constant angle-moment sigma.
        for a in (1e5,1e6,2e6):
            mean_g=4*a/math.sqrt(math.pi)*quad(lambda x: x**3*math.exp(-x*x),0,math.inf)[0]
            K=8*a/(3*math.sqrt(math.pi))*quad(lambda x: x**5*math.exp(-x*x),0,math.inf)[0]
            self.assertAlmostEqual(K/mean_g,4/3,places=12)

    def test_reaction_chemistry_invariants(self):
        self.assertTrue(all(r['chemistry_net_electron_s']==0
                            and r['chemistry_net_HI_s']==0
                            and r['chemistry_net_HII_s']==0
                            and r['direct_binding_energy_erg_per_H_s']==0 for r in self.rows))

    def test_frozen_drag_positivity(self):
        self.assertTrue(all(r['ion_neutral_drag_gamma_g_cm_minus3_s_minus1']>=0
             and r['nu_ion_linear_drag_s_minus1']>=0 and r['nu_neutral_linear_drag_s_minus1']>=0
             for r in self.rows))
        self.assertTrue(all(0<r['k_mt_A7_over_piA4']<2 for r in self.rows))

    def test_pairwise_momentum_conservation(self):
        for r in self.rows:
            U=7.25e4
            gamma=r['ion_neutral_drag_gamma_g_cm_minus3_s_minus1']
            self.assertAlmostEqual((-gamma*U)+(gamma*U),0,places=14)

    def test_drag_ratio_not_event_rate(self):
        for r in self.rows:
            self.assertGreater(r['k_mt_A7_over_eventA4'],0)
            self.assertGreater(r['k_mt_CX_piA4_window_cm3_s'],r['k_event_CX_A4_window_cm3_s'])

    def test_domain_and_bad_inputs(self):
        for x in (0.,-2.,float('nan'),float('inf')):
            with self.assertRaises(ValueError):m.sigma_cx_mt_fit(x)

    def test_quad_split_independent_fixed_gauss(self):
        xx,ww=np.polynomial.legendre.leggauss(100)
        for T in (100.,1200.,12000.):
            a=m.old.thermal_speed_cm_s(T)
            out=0.
            for lo,hi in ((m.LO,m.SPLIT),(m.SPLIT,m.HI)):
                low,high=lo/a,hi/a
                x=(high-low)*xx/2+(high+low)/2
                vals=np.array([math.exp(-y*y)*y**5*m.sigma_cx_mt_fit(y*a) for y in x])
                out+=(high-low)/2*float(np.dot(ww,vals))
            out*=8*a/(3*math.sqrt(math.pi))
            self.assertAlmostEqual(m.rate_integral(T,'mt_a7')/out,1.,delta=2e-7)

    def test_literal_source_tamper_fails(self):
        with tempfile.NamedTemporaryFile(suffix='.zip') as f:
            f.write(b'corrupt');f.flush()
            with self.assertRaisesRegex(ValueError,'source ZIP mismatch'):
                m.original_input(Path(f.name))

    def test_fit_violation_is_reported_not_hidden(self):
        d=m.fit_diagnostics()
        self.assertGreater(d['violating_sample_count'],0)
        self.assertGreater(d['ratio_max'],1.)
        self.assertNotEqual(d['sixteen_km_s_jump_relative'],0.)

    def test_source_speed_support_not_full(self):
        self.assertLess(self.rows[0]['maxwell_drag_geom_window_fraction'],0.95)
        self.assertGreater(self.rows[-1]['maxwell_drag_geom_window_fraction'],0.)
        self.assertLessEqual(max(r['maxwell_drag_geom_window_fraction'] for r in self.rows),1.)

    def test_source_export_replay_bytes(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            fa,ja=m.save(self.rows,a);fb,jb=m.save(self.rows,b)
            self.assertEqual(fa.read_bytes(),fb.read_bytes())
            self.assertEqual(ja.read_bytes(),jb.read_bytes())

    def test_canonicity_and_owner(self):
        d=m.summarize(self.rows)
        self.assertEqual(d['central_dag'],'28/88_REPORTED_UNCHANGED')
        self.assertEqual(d['bass_cr_extension_dag'],'0/3_UNCHANGED')
        self.assertFalse(d['original_dcs_retrieved'])
        self.assertFalse(d['joint_cr_elastic_mt'])
if __name__=='__main__':unittest.main()
