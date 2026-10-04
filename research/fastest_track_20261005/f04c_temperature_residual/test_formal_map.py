"""New exact symbolic identities for the actual FT03 source structure."""
import unittest
import sympy as s
from formal_map import build,chain_jacobian

class FormalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.q=build()
    def zero(self,v):self.assertEqual(s.factor(v),0)
    def test_four_row_schur_transport(self):
        q=self.q
        correction=q['h']*q['coupling']*s.diag(*[1/z for z in q['denom']])*q['photon_residual']
        for z in q['reduced']-q['direct']-correction:self.zero(z)
    def test_sixteen_chain_jacobian_entries(self):
        q=self.q;j=q['reduced'].jacobian(list(q['x'])+[q['t']])
        for z in j-chain_jacobian(q):self.zero(z)
    def test_energy_ledger_all_channels(self):
        q=self.q;r=q['stored_rhs'];nh=q['nh'];nhe=q['nhe'];chi=q['chi'];ev=q['ev']
        binding=ev*(nh*chi[0]*r['fractions'][0]+nhe*(chi[1]*r['fractions'][1]+(chi[1]+chi[2])*r['fractions'][2]))
        self.zero(r['thermal']+r['escape']+binding+ev*(q['energy'].dot(r['photon'])))
    def test_electron_photon_inventory_with_dr(self):
        q=self.q;r=q['stored_rhs'];dx=r['fractions']
        self.zero(q['nh']*dx[0]+q['nhe']*(dx[1]+2*dx[2])+sum(r['photon'])-(sum(r['collision'])-sum(r['rr'])-sum(r['dr'])))
    def test_thermal_does_not_use_old_rr_times_u_over_particles(self):
        q=self.q;r=q['reduced_rhs']
        # Source's LambdaRR(T) is independent of alpha until its actual formula is supplied.
        for a in range(3):
            self.zero(s.diff(r['thermal'],q['kinetic'][a])+q['nuclei'][a]*q['x'][a]*q['electron'])
        self.assertTrue(any(s.diff(q['reduced'][i],q['t'])!=0 for i in range(3)))
    def test_photon_elimination_temperature_derivative_is_zero(self):
        q=self.q
        for z in q['eliminated']:self.zero(s.diff(z,q['t']))
        for g in range(3):
            for i in range(3):
                self.zero(s.diff(q['eliminated'][g],q['x'][i])+q['h']*q['old_n'][g]*s.diff(q['opacity'][g],q['x'][i])/q['denom'][g]**2)
    def test_dr_stoichiometry(self):
        q=self.q;r=q['stored_rhs']
        for k in range(2):
            factor=q['x'][1]*q['electron']
            expected=s.Matrix([0,-factor,0])
            for z in r['fractions'].diff(q['dr'][k])-expected:self.zero(z)
    def test_escape_not_dependent_on_photons_at_fixed_x_temperature(self):
        q=self.q
        for z in q['native_n']:self.zero(s.diff(q['stored_rhs']['escape'],z))
    def test_rr_kinetic_log_derivative(self):
        t=s.Symbol('theta',positive=True);alpha=s.Function('alpha')(t);kb=s.Symbol('kb',positive=True)
        g=t*s.diff(alpha,t)/alpha
        kinetic=kb*t*alpha*(s.Rational(3,2)+g)
        expected=kb*alpha*((1+g)*(s.Rational(3,2)+g)+t*s.diff(g,t))
        self.zero(s.diff(kinetic,t)-expected)
    def test_source_fit_log_derivatives(self):
        t,L,A,B,p,r,d,C=s.symbols('theta L A B p r d C',positive=True)
        ell=L/t
        beta=A*t**(-s.Rational(3,2))*s.exp(-ell/2)*ell**p/(1+(ell/C)**r)**d
        v=(ell/C)**r
        self.zero(t*s.diff(beta,t)/beta-(-s.Rational(3,2)+ell/2-p+d*r*v/(1+v)))
        dr=A*t**(-s.Rational(3,2))*s.exp(-B/t)
        self.zero(t*s.diff(dr,t)/dr-(-s.Rational(3,2)+B/t))

if __name__=='__main__':unittest.main(verbosity=2)
