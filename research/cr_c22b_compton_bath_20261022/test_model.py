"""Changed-dependency checks for C22B; all tests use algebra/RHS, ODE0."""
from __future__ import annotations
import os
for key in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","BLIS_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ[key]="1"
import hashlib
import json
import math
from pathlib import Path
import sys
import unittest
import numpy as np
from scipy.constants import Boltzmann, Planck, c, electron_mass
from compton import gas_exchange_eV_per_H_s, SIGMA_T_CM2, A_R_CGS, EV_ERG
from model import ThermochemicalFactory, K_B_EV_K


class C22BTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.f=ThermochemicalFactory()
        cls.m=cls.f.build({'name':'checks','signed_sigma':.3,'signed_pi_m':2e-4,
                         'signed_pi_r':8e-4,'photon_scale':1.,'temperature_K':300.})

    def test_independent_SI_units_and_static_bath_relaxation(self):
        # Independent SI volume formula followed by number-volume/energy conversion.
        a_si=8*math.pi**5*Boltzmann**4/(15*Planck**3*c**3)
        for temp,tg,ne,nref in [(300.,57.2355,.02,1e-3),(15.,40.,.9,3e-6),(1e4,20.,.1,.2)]:
            si=4*(SIGMA_T_CM2*1e-4)*c*a_si*tg**4*(ne*nref*1e6)*Boltzmann*(tg-temp)/(electron_mass*c*c)
            expected=si/(nref*1e6*1.602176634e-19)
            got=gas_exchange_eV_per_H_s(temp,tg,ne)
            self.assertLess(abs(got/expected-1),2e-14)
            n_part=1.1+ne
            relaxation=8*(SIGMA_T_CM2*1e-4)*a_si*tg**4/(3*electron_mass*c)*ne/n_part
            self.assertLess(abs(got/(1.5*K_B_EV_K*n_part)/(relaxation*(tg-temp))-1),2e-14)
        self.assertLess(abs(A_R_CGS/(a_si*10)-1),2e-14)

    def test_sign_detailed_balance_and_zero_electron_limit(self):
        self.assertEqual(gas_exchange_eV_per_H_s(30,30,1),0.)
        self.assertEqual(gas_exchange_eV_per_H_s(300,30,0),0.)
        for t,tg in [(10,40),(400,40)]:
            q=gas_exchange_eV_per_H_s(t,tg,.2)
            self.assertGreater(q*(1/t-1/tg),0.)  # Entropy production of gas+bath.
            self.assertEqual(math.copysign(1,q),math.copysign(1,tg-t))

    def test_invariant_restriction_is_exact_and_rejects_nonzero(self):
        m=self.m;y=m.initial_state();z=m.project(y)
        self.assertEqual((m.size,m.solver_size),(75,72))
        self.assertTrue(np.array_equal(m.lift(z),y))
        self.assertTrue(np.array_equal(m.lift(m.solver_rhs(.2,z)),m.rhs(.2,y)))
        for i in m.invariant_indices:
            broken=y.copy();broken[i]=1e-99
            with self.assertRaisesRegex(ValueError,'NONZERO_DECLARED'):
                m.project(broken)
        with self.assertRaisesRegex(ValueError,'UNSUPPORTED_INITIAL'):
            self.f.build({'initial_neutron_abundance':1e-8})

    def test_off_mode_rhs_parity_without_old_ODE(self):
        m=self.f.build({'name':'off','compton_enabled':False,'signed_sigma':.3,
                        'signed_pi_m':2e-4,'signed_pi_r':8e-4})
        y=m.initial_state()
        for eta in [0,.17,.83,1.8]:
            d=m.rhs(eta,y);old=m.base.rhs(eta,y[:-1])
            self.assertTrue(np.array_equal(d[:-1],old))
            self.assertEqual(d[-1],0.)

    def test_off_mode_preserves_parent_domain_at_high_temperature(self):
        m=self.f.build({'name':'off_high_temperature','compton_enabled':False})
        y=m.initial_state();a=m.atomic.physical_abundances(y[m.ax])
        n=float((1+m.atomic.q)@a)
        y[m.iu]=1.5*K_B_EV_K*1e8*n
        old=m.base.rhs(.4,y[:-1]);new=m.rhs(.4,y)
        self.assertTrue(np.isfinite(old).all())
        self.assertTrue(np.array_equal(new[:-1],old))
        self.assertEqual(new[-1],0.)

    def test_same_flux_energy_ledger_and_number_neutrality(self):
        m=self.m;y0=m.initial_state()
        for eta,t in [(0.,300.),(.7,1e4),(1.5,6.)]:
            y=y0.copy();a=m.atomic.physical_abundances(y[m.ax]);n=float((1+m.atomic.q)@a)
            y[m.iu]=1.5*K_B_EV_K*t*n
            d=m.rhs(eta,y);old=m.base.rhs(eta,y[:-1]);q,_=m.compton(eta,y)
            flux=q/m.fields(eta,y)['H']
            self.assertEqual(d[m.ibath],-flux)
            self.assertLess(abs((d[m.iu]-old[m.iu])-flux),3e-15*max(abs(d[m.iu]),abs(old[m.iu]),abs(flux)))
            idx=[i for i in range(m.base.size) if i!=m.iu]
            self.assertTrue(np.array_equal(d[idx],old[idx]))
            terms=[d[m.iu],m.binding@(m.atomic.scales*d[m.ax]),m.photon_energies(eta)@d[m.gx],
                   -m.photon_energies(eta)@y[m.gx],d[m.iesc],d[m.iwg],d[m.iwr],d[m.ibath]]
            self.assertLessEqual(abs(sum(terms)),5e-15*sum(abs(v) for v in terms))

    def test_external_ledger_is_cumulative_not_resident(self):
        m=self.m;y=m.initial_state();d=m.rhs(.4,y)
        shifted=y.copy();shifted[m.ibath]=13.0
        self.assertTrue(np.array_equal(m.rhs(.4,shifted),d))
        self.assertAlmostEqual(m.energy(.4,shifted)-m.energy(.4,y),13.,places=13)
        q0=m.fields(.4,y);q1=m.fields(.4,shifted)
        self.assertEqual(q0['H'],q1['H'])

    def test_summary_energy_and_declared_inventory(self):
        m=self.m;y=m.initial_state();h=m.summarize(np.array([0.]),y[:,None])
        self.assertEqual(h['Y'].shape,(75,1));self.assertEqual(h['atomic_scaled'].shape,(21,1))
        self.assertEqual(h['energy_relative_residual'][0],0.)
        self.assertTrue(np.all(h['Y'][m.invariant_indices]==0.))
        self.assertEqual(h['bath_energy_received_eV_per_H'][0],0.)

    def test_rate_coverage_and_regime_fail_closed(self):
        for invalid in [(0,30,1),(10,-1,1),(10,30,-1),(1e9,30,1)]:
            with self.assertRaises(ValueError):gas_exchange_eV_per_H_s(*invalid)
        with self.assertRaisesRegex(ValueError,'COVERAGE_MISSING'):
            self.f.build({'required_processes':['H_collisional_excitation']})
        with self.assertRaisesRegex(ValueError,'SWITCH_MUST_BE_BOOL'):
            self.f.build({'compton_enabled':2})


if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(C22BTests))
    if len(sys.argv)>1:
        p=Path(sys.argv[1]);p.parent.mkdir(parents=True,exist_ok=True)
        with p.open('x') as f:json.dump({'tests_run':result.testsRun,'errors':len(result.errors),'failures':len(result.failures),
            'status':'PASS_SCOPED' if result.wasSuccessful() else 'FAIL_PRESERVED','ODE_calls':0,
            'scope':'new Compton coefficient units/sign/entropy/limits, external ledger, invariant lift, off RHS parity; no old ODE',
            'test_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'global_error_bound':None},f,indent=2)
    sys.exit(0 if result.wasSuccessful() else 1)
