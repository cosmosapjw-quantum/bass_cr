import unittest
import numpy as np
import convolution as c

class Controls(unittest.TestCase):
    def test_zero_time(self):
        f,count,s = c.source(0)
        np.testing.assert_array_equal(count,np.zeros(2))
        self.assertEqual(s,1)
        self.assertTrue(np.all(f>0))

    def test_source_off(self):
        for t in (0,c.T):
            f,count,s=c.source(t,False)
            np.testing.assert_array_equal(f,np.zeros(2))
            np.testing.assert_array_equal(count,np.zeros(2))
            self.assertEqual(s,1)

    def test_negative_age(self):
        with self.assertRaisesRegex(ValueError,"OBSERVATION_BEFORE"):
            c.A.age_at(0,1)

    def test_receiver_off_zero_evolution(self):
        g=c.P.assemble(128)
        y=c.fresh_initial(g)
        # Disabled receiver returns exact initial populations; no nonzero physics calls.
        np.testing.assert_array_equal(c.P.evolve(g,y,0,enabled=False),y)
        for j in range(2):
            o=c.cohort_observables(g,y,j)
            self.assertAlmostEqual(float(o["active_energy_eV"]),c.RESIDUAL[j],places=11)
            np.testing.assert_array_equal(o["ionization_counts"],np.zeros(3))

    def test_initial_branch_scaling(self):
        g=c.P.assemble(128)
        y=c.fresh_initial(g)
        f,count,s=c.source(c.T)
        for j in range(2):
            o=c.cohort_observables(g,y,j)
            self.assertAlmostEqual(float(o["active_electron_number"])*count[j],count[j],places=14)
            self.assertAlmostEqual(float(o["active_energy_eV"])*count[j],c.RESIDUAL[j]*count[j],places=11)

if __name__=="__main__": unittest.main()
