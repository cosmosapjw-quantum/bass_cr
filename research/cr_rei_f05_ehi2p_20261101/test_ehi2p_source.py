"""Source-scoped numerical tests; -O must not bypass claims."""
import csv
import gzip
import json
import math
import tempfile
import unittest
from decimal import Decimal,localcontext
from pathlib import Path
import ehi2p_source as m

class AtomicKernels(unittest.TestCase):
    def test_exact_published_knots(self):
        for T,y in m.KNOTS:self.assertEqual(m.upsilon(T),y)

    def test_boundaries_reject_extrapolation(self):
        for T in (4999.,20000.0001,0.,-1.,float('nan'),float('inf')):
            with self.assertRaises(ValueError):m.upsilon(T)

    def test_excitation_monotone_on_grid(self):
        values=[m.q_exc(5000.+15000.*i/200) for i in range(201)]
        self.assertTrue(all(a<b for a,b in zip(values,values[1:])))

    def test_deexcitation_global_upper(self):
        self.assertTrue(all(m.q_deexc(5000.+15000.*i/512) <= m.Q21_GLOBAL_UPPER
                            for i in range(513)))

    def test_detailed_balance(self):
        for T,_ in m.KNOTS:
            lhs=m.q_exc(T)/m.q_deexc(T)
            rhs=m.G2/m.G1*math.exp(-m.E12_EV/(m.KB_EV_K*T))
            self.assertAlmostEqual(lhs/rhs,1.,places=14)

    def test_high_precision_independent_atomic_rate(self):
        with localcontext() as c:
            c.prec=64
            for t,y in m.KNOTS:
                T=Decimal(str(t));Y=Decimal(str(y))
                k=Decimal(str(m.KB_EV_K));e=Decimal(str(m.E12_EV))
                v=Decimal("8.629e-6")*Y*(-e/(k*T)).exp()/(Decimal("2")*T.sqrt())
                # Float64 transcendental exp rounds at several ulps; Decimal64 is independent.
                self.assertLess(abs(m.q_exc(t)/float(v)-1),1e-14)

    def test_ground_state_zero_and_linear_scaling(self):
        T=10000.
        self.assertEqual(m.cell_excitation_rate(1e20,0.3,T,f1s=0.),0.)
        a=m.cell_excitation_rate(1e20,.3,T)
        self.assertAlmostEqual(m.cell_excitation_rate(1e20,.3,T,f1s=.4)/a,.4)
        self.assertAlmostEqual(m.cell_excitation_rate(3e20,.3,T)/a,3.)
        for fraction in (-.001,1.001):
            with self.assertRaises(ValueError):
                m.cell_excitation_rate(1e20,.3,T,f1s=fraction)

    def test_tiny_quench_analytic_limit(self):
        r=m.q_deexc(20000.)*.02/m.A21
        self.assertGreaterEqual(r,0.)
        self.assertLess(r,1e-15)

class OriginalSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory(prefix="bass_cr_ehi2p_tests_")
        cls.folder=Path(cls.tmp.name)
        cls.files,cls.meta=m.generate(cls.folder)
    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_true_original_domain_counts(self):
        a=self.meta
        self.assertEqual(a["original_cells"],46080)
        self.assertEqual(a["source_supported_cells"],12528)
        self.assertEqual(a["source_unsupported_cold_cells"],14832)
        self.assertEqual(a["source_unsupported_hot_cells"],18720)
        self.assertEqual(a["source_unsupported_boundary_cells"],0)
        self.assertAlmostEqual(a["source_supported_neutral_H_fraction"],.7583855556965159,places=13)

    def test_physics_reference_and_interval(self):
        a=self.meta
        self.assertAlmostEqual(a["source_excitation_s_inv_mid"]/5.028316296918783e48,1.,places=12)
        self.assertLessEqual(a["source_excitation_s_inv_lower"],a["source_excitation_s_inv_mid"])
        self.assertLessEqual(a["source_excitation_s_inv_mid"],a["source_excitation_s_inv_upper"])
        self.assertAlmostEqual(a["excitation_over_same_domain_caseB"],.03734346118073599,places=12)
        self.assertLess(a["maximum_ne_q21_over_A21"],1e-15)
        self.assertLess(a["local_ratio_independent_cancel_max_relative_residual"],3e-12)

    def test_source_and_authority_contract(self):
        a=self.meta
        self.assertEqual(a["original_REI_owner_HEAD"],m.orig.LOCKS["owner_git"])
        self.assertEqual(a["original_private_F05_source_SHA256"],m.orig.LOCKS["preview"])
        self.assertEqual(a["original_last_accepted_tick"],160)
        self.assertEqual(a["nonaccepted_candidate_tick"],161)
        self.assertEqual(a["REI_central_DAG"],"28/88_REPORTED_DELTA0")
        self.assertTrue(a["NOT_computed_outside_tabulated_temperature_domain"])
        self.assertTrue(a["NO_REI_MUTATION"])
        self.assertEqual(a["PRODUCTION"],"HOLD")

    def test_data_grain_and_no_original_raw_source(self):
        with gzip.open(self.files[0],"rt") as f:
            r=csv.DictReader(f)
            self.assertEqual(tuple(r.fieldnames),m.FIELDS)
            rows=list(r)
        self.assertEqual(len(rows),12528)
        self.assertEqual(len({int(x["node"]) for x in rows}),12528)
        self.assertTrue(all(float(x["excitation_s_inv_lower"])<=
                            float(x["excitation_s_inv_mid"])<=
                            float(x["excitation_s_inv_upper"]) for x in rows))
        # Even when source quenching is sub-ulp, its conservative lower bound is not rounded to 1.
        self.assertTrue(all(0<float(x["two_level_radiative_branch_lower"])<1 for x in rows))
        self.assertFalse(any(k.startswith(("source_H","tick160_","tick161_"))
                             for k in rows[0]))

    def test_deterministic_same_source_replay(self):
        with tempfile.TemporaryDirectory(prefix="bass_cr_ehi2p_replay_") as t:
            files,meta=m.generate(Path(t))
            self.assertEqual(meta,self.meta)
            for a,b in zip(files,self.files):
                self.assertEqual(m.sha(a),m.sha(b))

    def test_original_source_sha_rejects_tamper(self):
        with tempfile.TemporaryDirectory() as t:
            forged=Path(t)/"original.csv.gz"
            forged.write_bytes(b"FAKE_PRIVATE_OWNER_SOURCE")
            with self.assertRaises(ValueError):
                m.orig.byte_lock(forged,m.orig.LOCKS["preview"])

    def test_parent_source_integrity(self):
        self.assertEqual(m.sha(m.PARENT_CSV),m.PARENT_SHA)
        self.assertEqual(m.orig.sha(m.orig.PREVIEW),m.orig.LOCKS["preview"])

if __name__=="__main__":
    unittest.main()
