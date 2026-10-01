"""Public-contract tests for exact rational continuum enclosures."""
import unittest
from fractions import Fraction as F

from validated_majorant import (
    CellBounds, Interval, Proof, assemble_envelope, certify_demo_cell, demo_matrices,
    is_spd, lipschitz_bound, pencil_radius_bounds, tail_p2_enclosure,
)


class IntervalTests(unittest.TestCase):
    def test_float_input_is_rejected(self):
        with self.assertRaises(TypeError):
            Interval(0.1, 0.2)

    def test_interval_product_contains_extrema(self):
        result = Interval(-2, 3) * Interval(-4, 5)
        self.assertEqual((result.lo, result.hi), (F(-12), F(15)))

    def test_interval_division_straddling_zero_rejected(self):
        with self.assertRaises(ZeroDivisionError):
            Interval(1, 2) / Interval(-1, 1)

    def test_square_handles_interior_zero(self):
        self.assertEqual(Interval(-2, 3).square(), Interval(0, 9))


class SpectralTests(unittest.TestCase):
    def test_exact_spd_and_rank_loss(self):
        self.assertTrue(is_spd([[2, 1], [1, 2]]))
        self.assertFalse(is_spd([[1, 1], [1, 1]]))
        self.assertFalse(is_spd([[1, 2], [2, 1]]))

    def test_exact_generalized_pencil_bracket(self):
        lo, hi = pencil_radius_bounds([[2, 0], [0, 3]], [[4, 0], [0, -3]], bits=32)
        self.assertLessEqual(lo, 2)
        self.assertGreaterEqual(hi, 2)
        self.assertLessEqual(hi - lo, F(1, 2**30))

    def test_nondiagonal_metric_pencil_bound(self):
        # W=S times 2 gives rho=2 even with a nondiagonal metric.
        s = [[2, 1], [1, 3]]
        lo, hi = pencil_radius_bounds(s, [[4, 2], [2, 6]])
        self.assertLessEqual(lo, 2)
        self.assertGreaterEqual(hi, 2)

    def test_asymmetry_and_nonspd_rejected(self):
        with self.assertRaises(ValueError):
            pencil_radius_bounds([[1, 0], [0, 1]], [[1, 2], [0, 1]])
        with self.assertRaises(ValueError):
            pencil_radius_bounds([[1, 1], [1, 1]], [[1, 0], [0, 1]])

    def test_zero_pencil(self):
        self.assertEqual(pencil_radius_bounds([[1, 0], [0, 1]], [[0, 0], [0, 0]]), (F(0), F(0)))


class ContinuumTests(unittest.TestCase):
    def test_derivative_formula_and_spd_guard(self):
        self.assertEqual(lipschitz_bound(F(2), F(3), F(5), F(7)), F(29, 4))
        with self.assertRaises(ValueError):
            lipschitz_bound(F(0), F(3), F(5), F(7))

    def test_demo_rational_cells_produce_level2_only(self):
        cells = [certify_demo_cell(F(i, 4), F(i+1, 4)) for i in range(4)]
        result = assemble_envelope(cells)
        self.assertEqual(result['level'], 2)
        self.assertEqual(result['domain'], ['0', '1'])
        self.assertFalse(result['infinite_tail_certified'])
        self.assertGreater(F(result['integral_upper']), 0)
        self.assertEqual(result['scope'], 'synthetic_rational_family_v1')

    def test_continuous_join_raises_only_boundary_heights(self):
        cells = [certify_demo_cell(F(i,4), F(i+1,4)) for i in range(4)]
        result = assemble_envelope(cells)
        vertices = result['continuous_envelope_vertices']
        self.assertEqual(len(vertices), 9)
        self.assertEqual(len(set(v['z'] for v in vertices)), 9)
        self.assertGreaterEqual(F(result['integral_upper']), F(result['piecewise_tent_integral_upper']))
        for i, cell in enumerate(cells):
            self.assertGreaterEqual(F(vertices[2*i]['rho_upper']), cell.upper_at(cell.left))
            self.assertEqual(F(vertices[2*i+1]['rho_upper']), cell.center_rho_upper)
            self.assertGreaterEqual(F(vertices[2*i+2]['rho_upper']), cell.upper_at(cell.right))

    def test_demo_encloses_all_exact_rational_spot_checks(self):
        # Additional regression diagnostic; the proof is interval arithmetic,
        # not this finite set of points.
        for k in range(4):
            cell = certify_demo_cell(F(k, 4), F(k+1, 4))
            for j in range(9):
                x = cell.left + (cell.right-cell.left) * F(j, 8)
                s, w = demo_matrices(x)
                _, upper = pencil_radius_bounds(s, w)
                self.assertLessEqual(upper, cell.upper_at(x) + F(1, 2**30))

    def test_sample_fd_provenance_rejected(self):
        with self.assertRaises(ValueError):
            Proof('finite_difference', 'sample.npy', '0'*64, 'fit to samples')

    def test_missing_proof_digest_rejected(self):
        with self.assertRaises(ValueError):
            Proof('analytic_derivation', 'report.md', '', 'lemma 1')

    def test_noncontiguous_cells_rejected(self):
        with self.assertRaises(ValueError):
            assemble_envelope([certify_demo_cell(F(0), F(1, 4)), certify_demo_cell(F(1, 2), F(3, 4))])

    def test_interval_outside_verified_synthetic_domain_rejected(self):
        with self.assertRaises(ValueError):
            certify_demo_cell(F(-1), F(1))

    def test_out_of_cell_point_rejected(self):
        with self.assertRaises(ValueError):
            certify_demo_cell(F(0), F(1, 4)).upper_at(F(1))

    def test_eigenbranch_switch_does_not_require_smooth_rho(self):
        # S=I, W=diag(z,1-z) on [0,1] gives rho=max(z,1-z).
        from hashlib import sha256
        from pathlib import Path
        p = Path(__file__)
        proof = Proof('analytic_derivation', p.name, sha256(p.read_bytes()).hexdigest(),
                      'explicit diagonal affine family in this test')
        cell = CellBounds(F(0), F(1), F(1,2), F(1), F(0), F(1), F(1), F(1,2),
                          'branch_switch_example', proof, proof)
        for z in (F(0), F(1,4), F(1,2), F(3,4), F(1)):
            self.assertEqual(cell.upper_at(z), max(z, 1-z))
        self.assertEqual(cell.integral_upper(), F(3,4))


class TailTests(unittest.TestCase):
    def test_b_zero_exact_limit(self):
        self.assertEqual(tail_p2_enclosure(F(3), F(2), F(0), F(4)), Interval(F(3, 8), F(3, 8)))

    def test_p2_enclosure_contains_independent_integral_series(self):
        # atan(1/2) is bracketed independently with 101/102 terms.
        fine = sum((-1)**k * F(1, 2)**(2*k+1) / (2*k+1) for k in range(101))
        fine_lower = fine - F(1, 2)**203 / 203
        out = tail_p2_enclosure(F(1), F(1), F(1), F(2), terms=12)
        self.assertLessEqual(out.lo, fine_lower)
        self.assertGreaterEqual(out.hi, fine)

    def test_p2_width_and_large_z_no_cancellation(self):
        out = tail_p2_enclosure(F(1), F(1), F(2), F(10**12), terms=4)
        self.assertGreater(out.lo, 0)
        self.assertLessEqual(out.hi, F(1, 10**12))
        self.assertLess(out.hi-out.lo, F(1, 10**90))

    def test_p2_invalid_domain_rejected(self):
        for args in [(1, 0, 1, 2), (-1, 1, 1, 2), (1, 1, -1, 2), (1, 1, 3, 2)]:
            with self.assertRaises(ValueError):
                tail_p2_enclosure(*map(F, args))


if __name__ == '__main__':
    unittest.main()
