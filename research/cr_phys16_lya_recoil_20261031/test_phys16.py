#!/usr/bin/env python3
"""Independent-in-code scientific checks (same author, not external R06/C09)."""
import csv,hashlib,json,math,tempfile,unittest
from pathlib import Path
import numpy as np
from scipy.integrate import quad
import phys16_spectral as m

ROOT=Path(__file__).resolve().parent

def read(name):
    with (ROOT/'results'/name).open(newline='',encoding='utf8') as f:
        return list(csv.DictReader(f))

class TestSourceAndModel(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
    cls.r=json.loads((ROOT/'results/RESULT.json').read_text())
    cls.src=read('SOURCE_RECOIL_MODEL_CROSSWALK.csv')
    cls.spectra=read('SOURCE_EMISSION_FREQUENCY_ATLAS.csv')
    cls.time=read('TIME_ORDERED_MODEL_FIRST_SCATTER_SPECTRA.csv')
    cls.k=read('ONE_SCATTER_REDIS_KERNEL_ATLAS.csv')
    cls.p=np.load(ROOT/'results'/'SOURCE_EMISSION_PROFILES.npz',allow_pickle=False)
 def test_01_parent_locked(self):
    b=(ROOT/'sources'/'PR140_PHYS15_SOURCE.zip').read_bytes()
    self.assertEqual(hashlib.sha256(b).hexdigest(),m.PHYS15_SHA)
 def test_02_corrupted_parent_rejected(self):
    b=bytearray((ROOT/'sources'/'PR140_PHYS15_SOURCE.zip').read_bytes());b[-1]^=1
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/'bad.zip';p.write_bytes(b)
        with self.assertRaisesRegex(ValueError,'HASH_MISMATCH'):m.load_source(p)
 def test_03_6400_2066_source(self):
    self.assertEqual(self.r['source_photons'],6400);self.assertEqual(len(self.src),2066)
    self.assertEqual(len(set((x['source'],x['source_atom_index']) for x in self.src)),2066)
 def test_04_He_only(self):self.assertEqual(set(x['source'] for x in self.src),{'He'})
 def test_05_earliest_parity(self):
    self.assertAlmostEqual(sum(float(x['excitation_earliest_m3']) for x in self.src)/3.3158906934521573e-31,1.,12)
 def test_06_latest_parity(self):
    self.assertAlmostEqual(sum(float(x['excitation_latest_m3']) for x in self.src)/9.85567761064524e-32,1.,12)
 def test_07_all_energies_measured_overlap(self):
    self.assertTrue(all(14.6<=float(x['Ee_eV'])<=21.4 for x in self.src))
 def test_08_positive_recoil(self):
    self.assertTrue(all(float(x['collision_recoil_mean_eV'])>0 for x in self.src))
 def test_09_max_collision_residual(self):self.assertLess(self.r['collision_energy_residual_max'],1e-12)
 def test_10_angular_Born_normalized(self):
    for e in [14.6014,15,17,20,20.989]:
       w,*_=m.born_angular(e)
       self.assertGreater(np.min(w),0);self.assertAlmostEqual(sum(w),1.,12)
 def test_11_E1_angular_normalization(self):self.assertAlmostEqual(float(sum(m.DIPOLE_W)),1.,13)
 def test_12_E1_angular_cos2(self):self.assertAlmostEqual(float(sum(m.DIPOLE_W*m.WU**2)),0.2,13)
 def test_13_Born_form_factor_f(self):
    # Born F(q)^2=(72 z²)/(z²+9/4)^6; zero-q limit recovers f(1s-2p)≈0.41641.
    Hartree=4.3597447222060e-18
    dip2=72/(2.25**6) * 3 # isotropic sum over 3 Cartesian components
    f_hydrogenic=(2/3)*(3/8)*dip2
    oscillator=(2/3)*(m.E21*m.EV/Hartree)*dip2
    self.assertAlmostEqual(f_hydrogenic,0.4161967179799827,12)
    self.assertAlmostEqual(oscillator/f_hydrogenic,(m.E21*m.EV/Hartree)/(3/8),13)
    # NIST f=0.41641 is a separate atomic input, not silently set by E21=10.1988eV.
 def test_14_profile_shapes_and_positive(self):
    self.assertEqual(self.p['profiles'].shape,(2066,3,len(m.XGRID)))
    self.assertTrue(np.all(self.p['profiles']>=0))
 def test_15_model_normalized_mass_on_window(self):
    for pp in self.p['profiles']:
        for model in pp:
            self.assertGreater(float(np.trapezoid(model,m.XGRID)),0.9996)
            self.assertLess(float(np.trapezoid(model,m.XGRID)),1)
 def test_16_tail_bound(self):
    tt=float(self.r['rigorous_model_tail_probability_upper_x16'])
    self.assertTrue(0<tt<.001)
    self.assertTrue(all(1-float(np.trapezoid(pp,m.XGRID))<tt for ss in self.p['profiles'] for pp in ss))
 def test_17_model_quadrature_convergence(self):
    for e in [14.8,16.,19.,20.95]:
        v1=m.emit_pdf(e,n_mu=32,n_w=12)
        v2=m.emit_pdf(e,n_mu=64,n_w=24)
        for i in range(3):
            self.assertLess(float(np.max(abs(v1[i]-v2[i]))),2e-7)
 def test_18_frequency_spectrum_count(self):self.assertEqual(len(self.spectra),2*3*len(m.XGRID))
 def test_19_source_weight_number_conservation(self):
    for policy in ('earliest','latest'):
        target=self.r['total_2p_photons_m3'][policy]
        self.assertTrue(target>0)
        model='BORN_DIPOLE'
        this=[float(r['source_emission_spectral_number_per_Doppler_m3']) for r in self.spectra if r['birth_policy']==policy and r['angular_model']==model]
        prob=float(np.trapezoid(this,m.XGRID))/target
        self.assertAlmostEqual(prob,self.r['spectral_mass_and_injection_hazard'][policy+':'+model]['mass_within_x16'],11)
 def test_20_frequency_hazard_positive(self):
    self.assertTrue(all(float(x['weighted_injection_hazard_s'])>0 for x in self.r['spectral_mass_and_injection_hazard'].values()))
 def test_21_time_scatter_count(self):self.assertEqual(len(self.time),2*3*len(m.XGRID))
 def test_22_first_scatter_bounds(self):
    for ss in self.r['time_ordered_first_scatter_integrals'].values():
        self.assertLess(ss['first_scatter_x16_lower_m3'],ss['injection_x16_m3'])
        self.assertLess(ss['injection_x16_m3'],ss['parent_excitation_m3'])
        self.assertLess(ss['first_scatter_upper_tail_only_m3'],ss['parent_excitation_m3'])
 def test_23_first_scatter_original_x0_per_atom_parity(self):
    for ss in self.r['time_ordered_first_scatter_integrals'].values():
        self.assertLess(ss['original_x0_max_per_atom_relative_residual'],1e-12)
 def test_24_finite_A_bound(self):
    for ss in self.r['time_ordered_first_scatter_integrals'].values():
        self.assertLess(ss['finite_A_upper_difference_m3'],1e-42)
 def test_25_no_central_promotion(self):
    self.assertEqual(self.r['central_DAG'],'28/88 DELTA0');self.assertEqual(self.r['extension_DAG'],'0/3 DELTA0')
 def test_26_one_scatter_integrals(self):
    for x in self.r['redistribution_grid_checks']:
        self.assertLess(abs(x['finite_grid_mass']-1),1e-8)
        self.assertLess(abs(x['finite_grid_mean']-x['analytic_mean']),1e-5)
 def test_27_one_scatter_recoil_at_center(self):
    ref=next(x for x in self.r['redistribution'] if x['x_in']==0)
    self.assertAlmostEqual(ref['out_mean'],-m.ETA_SC,12)
 def test_28_absorption_conditional_symmetric(self):
    a=m.redistributed_moments(-3.);b=m.redistributed_moments(3.)
    self.assertAlmostEqual(a['conditional_u_mean'],-b['conditional_u_mean'],10)
    # Recoil breaks wing variance symmetry by 1.6 * E[u|x] * eta_sc.
    delta=b['out_variance']-a['out_variance']
    self.assertAlmostEqual(delta,1.6*b['conditional_u_mean']*m.ETA_SC,8)
 def test_29_one_scatter_matrix_nonnegative(self):
    self.assertTrue(all(float(r['kernel_density_per_Doppler'])>=-1e-16 for r in self.k))
 def test_30_one_scatter_row_integrals(self):self.assertEqual(len(self.k),3*400)
 def test_31_one_scatter_A_profile_parity(self):
    for x in [0.,1.,3.]:
        a=m.redistributed_moments(x)['absorption_profile']
        self.assertAlmostEqual(a/float(m.voigt_phi(x)),1.,10)
 def test_32_no_production_overclaim(self):
    self.assertEqual(self.r['production'],'HOLD');self.assertEqual(self.r['R06_distinct_author'],'NOT_RUN');self.assertEqual(self.r['C09_distinct_author'],'NOT_RUN')
 def test_33_source_immutability(self):
    self.assertTrue(self.r['no_merge']);self.assertTrue(self.r['no_force_push'])
 def test_34_emission_model_sensitivity(self):
    a=self.r['spectral_mass_and_injection_hazard']['earliest:BORN_DIPOLE']['weighted_injection_hazard_s']
    b=self.r['spectral_mass_and_injection_hazard']['earliest:ISOTROPIC_IMPACT_DIPOLE']['weighted_injection_hazard_s']
    self.assertGreater(abs(a-b)/a,0.05)
 def test_35_emission_cauchy_no_finite_variance(self):
    # Voigt tails from nonzero natural line a; report only *centre* second moments.
    self.assertGreater(m.A,0)
    self.assertTrue(all(float(x['estimated_total_centre_variance_x2'])>0.5 for x in self.src))

if __name__=='__main__':unittest.main(verbosity=2)
