"""Focused new postprocessor checks; no physical ODE execution."""
import json
import math
from pathlib import Path
import tempfile
import unittest

import numpy as np
from analyze_components import components, deterministic_npz, G, C


def fixture(pm=0., pg=0., pn=0.):
    return {"eta":np.array([0.,1.]),"a":np.array([1.,2.]),"H":np.array([2.,3.]),"s":np.array([-.2,.3]),"Pi_matter_J_m3":np.full(2,pm),"Pi_gamma_J_m3":np.full(2,pg),"Pi_nu_J_m3":np.full(2,pn)}


class ComponentChecks(unittest.TestCase):
    def test_full_tensor_and_units(self):
        raw=fixture(1.,2.,-1.)
        d=components(raw)
        kappa=8*math.pi*G/C**4
        for sector, p in (("m",1.),("gamma",2.),("nu",-1.),("r",1.),("tot",2.)):
            tensor=np.diag([-p,-p,2*p])
            self.assertEqual(float(np.trace(tensor)),0.)
            norm=math.sqrt(float(np.einsum("ij,ij",tensor,tensor)))
            expected=kappa*norm/(raw["H"]/C)**2
            np.testing.assert_allclose(d[f"Pi_{sector}_F"],expected,rtol=5e-16)
            np.testing.assert_allclose(d[f"Pi_{sector}_F"],math.sqrt(2)*d[f"Pi_{sector}_half"],rtol=5e-16)
            np.testing.assert_allclose(d[f"sigma_dot_pi_{sector}_J_m3_s"],6*raw["s"]*p,rtol=0,atol=0)

    def test_opposite_stress_not_sum_of_norms(self):
        d=components(fixture(1.,-.6,-.4))
        np.testing.assert_array_equal(d["P_tot_signed_F"],0)
        self.assertTrue(np.all(d["Pi_m_F"]+d["Pi_r_F"]>0))
        np.testing.assert_array_equal(d["cancellation"],1)
        self.assertTrue(np.all(d["opposing_signs"]))

    def test_zero_and_missing_are_distinct(self):
        d=components(fixture())
        self.assertTrue(np.isnan(d["cancellation"]).all())
        self.assertFalse(d["cancellation_defined"].any())
        raw=fixture();del raw["Pi_nu_J_m3"]
        with self.assertRaisesRegex(ValueError,"MISSING_SOURCE_SECTOR"):
            components(raw)

    def test_sign_and_invalid_H(self):
        a=components(fixture(1.,2.,3.)); b=components(fixture(-1.,-2.,-3.))
        for sector in ("m","gamma","nu","r","tot"):
            np.testing.assert_array_equal(a[f"Pi_{sector}_F"],b[f"Pi_{sector}_F"])
            np.testing.assert_array_equal(a[f"P_{sector}_signed_F"],-b[f"P_{sector}_signed_F"])
        raw=fixture(); raw["H"][0]=0
        with self.assertRaisesRegex(ValueError,"NONPOSITIVE_H"):
            components(raw)

    def test_deterministic_npz_and_create_only(self):
        with tempfile.TemporaryDirectory() as td:
            a,b=Path(td)/"a.npz",Path(td)/"b.npz"
            deterministic_npz(a,{"x":np.arange(5.),"unicode":np.array(["s00"])})
            deterministic_npz(b,{"unicode":np.array(["s00"]),"x":np.arange(5.)})
            self.assertEqual(a.read_bytes(),b.read_bytes())
            with np.load(a,allow_pickle=False) as z:
                np.testing.assert_array_equal(z["x"],np.arange(5.))
            with self.assertRaises(FileExistsError):
                deterministic_npz(a,{"x":np.arange(5.)})


if __name__=="__main__":
    unittest.main(verbosity=2)
