"""Focused C22A checks. No C21O integration is invoked."""
from __future__ import annotations
import os
for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
            "BLIS_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[key] = "1"
import json
from pathlib import Path
import sys
import unittest
import numpy as np
from model import ThermochemicalFactory, K_B_EV_K


class C22ATests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.factory = ThermochemicalFactory()
        cls.model = cls.factory.build({"name":"unit", "signed_sigma":0.3,
                                     "signed_pi_m":2e-4, "signed_pi_r":8e-4})

    def test_event_nuclei_charge_energy(self):
        m = self.model
        for eta, temp in ((0.0,300.0),(0.25,1e4),(0.9,1e5),(1.5,5e3)):
            y=m.initial_state()
            # Populate all modeled charge states without changing nuclei totals.
            x=y[m.ax]
            for name,total in m.atomic.initial_nucleus_totals.items():
                ids=m.atomic.blocks[name]
                if total>0:
                    x[list(ids)]=1/len(ids)
            a=m.atomic.physical_abundances(x)
            y[m.iu]=1.5*K_B_EV_K*temp*(np.sum(a)+m.atomic.q@a)
            dy=m.rhs(eta,y)
            dn=m.atomic.scales*dy[m.ax]
            for name,ids in m.atomic.blocks.items():
                self.assertLessEqual(abs(np.sum(dn[list(ids)])), 3e-15*max(np.sum(abs(dn[list(ids)])),1e-30))
            charge=float(m.atomic.q@dn+dy[m.irr]-dy[m.iabs])
            self.assertLessEqual(abs(charge),3e-15*max(abs(dy[m.irr])+abs(dy[m.iabs]),1e-30))
            photon=float(np.sum(dy[m.gx])+dy[m.iabs])
            self.assertLessEqual(abs(photon),3e-15*max(abs(dy[m.iabs]),1e-30))
            terms=[dy[m.iu],m.binding@dn,m.photon_energies(eta)@dy[m.gx],
                   -m.photon_energies(eta)@y[m.gx],dy[m.iesc],dy[m.iwg],dy[m.iwr]]
            self.assertLessEqual(abs(sum(terms)),3e-15*sum(abs(t) for t in terms))

    def test_temperature_particle_term(self):
        m=self.model;y=m.initial_state();eta=0.15;dy=m.rhs(eta,y)
        a=m.atomic.physical_abundances(y[m.ax]);dcount=float((1+m.atomic.q)@(m.atomic.scales*dy[m.ax]))
        npart=float(np.sum(a)+m.atomic.q@a);temp=m.temperature(y)
        direct=(dy[m.iu]/(1.5*K_B_EV_K)-temp*dcount)/npart
        heat=dy[m.iu]+2*y[m.iu]
        derived=-2*temp-temp*dcount/npart+heat/(1.5*K_B_EV_K*npart)
        self.assertAlmostEqual(direct/derived,1.0,places=14)
        # Central directional EOS difference is independent of the analytic form.
        eps=1e-7/max(np.linalg.norm(dy),1)
        fd=(m.temperature(y+eps*dy)-m.temperature(y-eps*dy))/(2*eps)
        self.assertLess(abs(fd/direct-1),2e-6)

    def test_hydrogenic_RR_capture_is_not_threshold_cooling(self):
        m=self.model
        for p in m.parameters:
            from rr_energy_moment import rr_energy_factor
            f=rr_energy_factor(p,np.array([3.,1e4,1e9]))
            self.assertTrue(np.all((f>0)&(f<1)))

    def test_photon_redshift_and_breakpoints(self):
        m=self.model
        self.assertTrue(np.allclose(m.photon_energies(m.eta_end),m.photon_energies(0)*3/21,rtol=2e-15,atol=0))
        for e in m.atomic.energies_eV:
            for chi in m.thresholds:
                t=np.log(e/chi)
                if 0<t<m.eta_end:
                    self.assertLess(min(abs(t-q) for q in m.transition_times()),1e-14)

    def test_inventory_absence_and_coverage_guard(self):
        m=self.model;y=m.initial_state()
        self.assertEqual(m.size,74)
        self.assertEqual(len(m.atomic.state_labels),21)
        for k in ("n","T"):
            self.assertTrue(np.all(y[m.ax][list(m.atomic.blocks[k])]==0))
        with self.assertRaisesRegex(ValueError,"COVERAGE_MISSING"):
            self.factory.build({"required_processes":["charge_exchange"]})
        with self.assertRaisesRegex(ValueError,"RR_T_DOMAIN"):
            self.factory.build({"temperature_K":2})
        with self.assertRaisesRegex(ValueError,"UNSUPPORTED_INITIAL_OR_MODEL_INPUT"):
            self.factory.build({"initial_neutron_abundance":1e-5})

    def test_LiI_PH1_continuous_redshift_branch_decimal(self):
        m=self.model
        grid=np.r_[np.geomspace(5.392,64.39,51)[:-1],np.geomspace(64.39,150.,51)]
        got=m.atomic.provider.sigma("LiI",grid)
        independent=np.array([m.atomic.provider.sigma_decimal("LiI",float(e)) for e in grid])
        self.assertLess(float(np.max(abs(got/independent-1))),5e-14)
        below=np.array([1.4,3.,5.391999999])
        self.assertTrue(np.array_equal(m.atomic.provider.sigma("LiI",below),np.zeros(3)))

    def test_isotope_equal_charge_fraction_invariance(self):
        m=self.model;y=m.initial_state();dy=m.rhs(0,y)
        h=np.array(m.atomic.blocks["H1"]);d=np.array(m.atomic.blocks["D"])
        self.assertTrue(np.allclose(dy[m.ax][h],dy[m.ax][d],rtol=3e-15,atol=1e-25))
        h3=np.array(m.atomic.blocks["He3"]);h4=np.array(m.atomic.blocks["He4"])
        self.assertTrue(np.allclose(dy[m.ax][h3],dy[m.ax][h4],rtol=3e-15,atol=1e-25))
        l6=np.array(m.atomic.blocks["Li6"]);l7=np.array(m.atomic.blocks["Li7"])
        self.assertTrue(np.allclose(dy[m.ax][l6],dy[m.ax][l7],rtol=3e-15,atol=1e-25))

    def test_signed_components_before_norm(self):
        m=self.factory.build({"signed_sigma":0.0,"signed_pi_m":2e-4,"signed_pi_r":-2e-4})
        h=m.summarize(np.array([0.0]),m.initial_state()[:,None])
        self.assertLess(abs(h['signed_Pi_tot_F'][0]),1e-13)
        self.assertGreater(h['Pi_m_F'][0]+h['Pi_r_F'][0],3.9e-4)
        self.assertAlmostEqual(h['Pi_r_F'][0],abs(h['signed_Pi_gamma_F'][0]+h['signed_Pi_nu_F'][0]),places=14)


if __name__ == '__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(C22ATests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    if len(sys.argv)>1:
        path=Path(sys.argv[1]);path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('x') as f:
            json.dump({'tests_run':result.testsRun,'failures':len(result.failures),
                       'errors':len(result.errors),'successful':result.wasSuccessful(),
                       'scope':'new model invariants, EOS, support, isotope equality, stress sign; old ODE0',
                       'global_error_bound':None},f,indent=2)
    sys.exit(0 if result.wasSuccessful() else 1)
