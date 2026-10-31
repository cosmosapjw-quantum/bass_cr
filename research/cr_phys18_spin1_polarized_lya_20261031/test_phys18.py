#!/usr/bin/env python3
"""Independent-in-code scoped physics tests. Same author, not a true R06/C09 distinct-author review."""
from __future__ import annotations
import unittest, csv, json, sys
from pathlib import Path
import numpy as np
from scipy.integrate import quad
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT));import phys18_stokes as m

def read(f):
 with (ROOT/'results'/f).open(newline='') as x:return list(csv.DictReader(x))

class Physics18(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.r=json.loads((ROOT/'results/RESULT.json').read_text());cls.events=read('SOURCE_2P_ALIGNMENT_MOMENTS.csv');cls.atlas=read('SOURCE_DIRECTIONAL_STOKES_ATLAS.csv');cls.spec=read('SOURCE_DIRECTIONAL_STOKES_FREQUENCY_ATLAS.csv')
 def test_01_parent_full_sha(self):self.assertEqual(m.sha(m.PARENT_SOURCE_FILE),m.PARENT_SOURCE_SHA)
 def test_02_2p_source_count(self):self.assertEqual(len(self.events),2066)
 def test_03_original_source_owner(self):self.assertEqual({r['source'] for r in self.events},{'He'})
 def test_04_parent_N2p_earliest(self):self.assertAlmostEqual(self.r['source_photon_excitation_density_m3']['earliest']/3.3158906934521573e-31,1.,12)
 def test_05_parent_N2p_latest(self):self.assertAlmostEqual(self.r['source_photon_excitation_density_m3']['latest']/9.85567761064524e-32,1.,12)
 def test_06_electron_energy_source(self):self.assertTrue(all(14.60<float(r['Ee_eV'])<21. for r in self.events))
 def test_07_energy_recoil(self):self.assertLess(self.r['max_nonrel_energy_residual'],1e-12)
 def test_08_alignment_rho_eigenvalue(self):
  for x in m.XI:
   eig=[(1+2*x)/3,(1-x)/3,(1-x)/3];self.assertAlmostEqual(sum(eig),1.,14);self.assertGreaterEqual(min(eig),-1e-14)
 def test_09_alignment_A2_per_source(self):self.assertTrue(all(-.5<=float(r['q_quadrupole_A2'])<=1 for r in self.events))
 def test_10_consistent_A2_geometry(self):
  for en in [14.60140625,16.5,19.58,20.99]:
   p,v,cb,sb,A,err=m.geometry(en);self.assertAlmostEqual(A,1-1.5*float(p@(sb*sb)),12)
 def test_11_angular_stokes_length(self):self.assertEqual(len(self.atlas),2*len(m.XI)*len(m.THETA))
 def test_12_frequency_stokes_length(self):self.assertEqual(len(self.spec),2*3*3*len(m.SPECTRAL_X))
 def test_13_I_nonnegative(self):self.assertTrue(all(float(r['dN_dOmega_m3_sr'])>=0 for r in self.atlas))
 def test_14_cone_integrated(self):self.assertTrue(all(abs(float(r['dQ_dOmega_m3_sr']))<=float(r['dN_dOmega_m3_sr'])*(1+1e-12) for r in self.atlas))
 def test_15_cone_frequency(self):self.assertTrue(all(abs(float(r['d2Q_dOmega_dx_m3_sr']))<=float(r['d2N_dOmega_dx_m3_sr'])*(1+1e-11) for r in self.spec))
 def test_16_UV_zero(self):self.assertTrue(all(float(r['dU_dOmega_m3_sr'])==float(r['dV_dOmega_m3_sr'])==0 for r in self.atlas))
 def test_17_UV_spectra_zero(self):self.assertTrue(all(float(r['d2U_dOmega_dx_m3_sr'])==float(r['d2V_dOmega_dx_m3_sr'])==0 for r in self.spec))
 def test_18_isotropic_rho_I_uniform(self):
  for policy in ['earliest','latest']:
   v=[float(r['dN_dOmega_m3_sr']) for r in self.atlas if r['birth_policy']==policy and float(r['xi_alignment'])==0]
   self.assertLess(max(v)-min(v),max(v)*1e-12)
 def test_19_isotropic_rho_Q_zero(self):self.assertTrue(all(abs(float(r['dQ_dOmega_m3_sr']))<1e-95 for r in self.atlas if float(r['xi_alignment'])==0))
 def test_20_poles_zero_Q(self):self.assertTrue(all(abs(float(r['dQ_dOmega_m3_sr']))<1e-46 for r in self.atlas if float(r['observer_theta_deg']) in (0,180)))
 def test_21_angular_norm(self):
  for A in [0.54585,0.60,0.75]:
   for xi in m.XI:
    f=lambda u:(1-xi*A*(3*u*u-1)/2)/2
    self.assertAlmostEqual(quad(f,-1,1)[0],1.,13)
 def test_22_analytic_90_polarization(self):
  sample=next(x for x in self.events if 16.49<float(x['Ee_eV'])<16.51)
  p,v,cb,sb,A,_=m.geometry(float(sample['Ee_eV']))
  I,Q,*_=m.moments_from_geometry(p,v,cb,sb,90,1.)
  self.assertAlmostEqual(Q/I,3*A/(2+A),12)
 def test_23_negative_alignment_sign(self):
  a=next(r for r in self.atlas if r['birth_policy']=='earliest' and float(r['xi_alignment'])==-0.5 and float(r['observer_theta_deg'])==90)
  self.assertLess(float(a['linear_polarization_QoverI']),0)
 def test_24_positive_alignment_sign(self):
  a=next(r for r in self.atlas if r['birth_policy']=='earliest' and float(r['xi_alignment'])==1 and float(r['observer_theta_deg'])==90)
  self.assertGreater(float(a['linear_polarization_QoverI']),0.6)
 def test_25_forward_backward_I_symmetry(self):
  for p in ['earliest','latest']:
   for xi in m.XI:
    a=next(r for r in self.atlas if r['birth_policy']==p and float(r['xi_alignment'])==xi and float(r['observer_theta_deg'])==0)
    b=next(r for r in self.atlas if r['birth_policy']==p and float(r['xi_alignment'])==xi and float(r['observer_theta_deg'])==180)
    self.assertAlmostEqual(float(a['dN_dOmega_m3_sr'])/float(b['dN_dOmega_m3_sr']),1.,12)
 def test_26_forward_backward_center_shift(self):
  for xi in m.XI:
   a=next(r for r in self.atlas if r['birth_policy']=='earliest' and float(r['xi_alignment'])==xi and float(r['observer_theta_deg'])==0)
   b=next(r for r in self.atlas if r['birth_policy']=='earliest' and float(r['xi_alignment'])==xi and float(r['observer_theta_deg'])==180)
   self.assertAlmostEqual(float(a['pre_natural_line_centre_mean_x'])+float(b['pre_natural_line_centre_mean_x']),-2*m.old.ETA_EM,11)
 def test_27_theta90_center_shift_recoil_only(self):
  for xi in m.XI:
   a=next(r for r in self.atlas if r['birth_policy']=='earliest' and float(r['xi_alignment'])==xi and float(r['observer_theta_deg'])==90)
   self.assertAlmostEqual(float(a['pre_natural_line_centre_mean_x']),-m.old.ETA_EM,12)
 def test_28_centre_variance_lower(self):self.assertTrue(all(float(r['pre_natural_line_centre_variance_x2'])>.5-1e-12 for r in self.atlas))
 def test_29_finite_window_mass(self):self.assertTrue(all(.9995<r['mass_fraction_x12']<=1.00001 for r in self.r['spectral_mass_window']))
 def test_30_spectral_phi_quadrature(self):
  e=16.5;p,v,cb,sb,A,_=m.geometry(e);ph=m.PHI.copy()
  a=m.stokes_spectrum(p,v,cb,sb,90.);m.PHI=(np.arange(32)+.5)*2*np.pi/32
  try:b=m.stokes_spectrum(p,v,cb,sb,90.)
  finally:m.PHI=ph
  self.assertLess(np.max(abs(a-b)),5e-13)
 def test_31_spectral_first_moment_reference(self):
  a=next(r for r in self.r['spectral_mass_window'] if r['policy']=='earliest' and r['xi']==1 and r['theta']==90)
  self.assertTrue(a['mass_fraction_x12']>.999)
 def test_32_source_rate_unchanged(self):self.assertEqual(self.r['original_2p_total_source_rates'],'UNCHANGED')
 def test_33_conditional_axis_scope(self):self.assertIn('NO_SOURCE_DIRECTION_OWNER',self.r['conditional_incident_electron_axis'])
 def test_34_Williams1998_not_injected(self):self.assertIn('NOT_NUMERICALLY_INGESTED',self.r['Williams1998_16p5_DCS_and_lambda_R_I'])
 def test_35_no_central_promotion(self):self.assertEqual(self.r['central_DAG'],'28/88_DELTA0');self.assertEqual(self.r['extension_DAG'],'0/3_DELTA0')
 def test_36_physics_gates(self):self.assertEqual(self.r['production'],'HOLD');self.assertEqual(self.r['physical_sublevel_density_matrix'],'UNBOUND')
 def test_37_unmixed_axes_no_polarization_claim(self):self.assertIn('UNPOLARIZED',self.r['isotropic_electron_axes'])
 def test_38_no_merge_force_push(self):self.assertTrue(self.r['NO_MERGE'] and self.r['NO_FORCE_PUSH'])

if __name__=='__main__':unittest.main(verbosity=2)
