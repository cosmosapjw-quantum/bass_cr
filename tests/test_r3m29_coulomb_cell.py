import math

import pytest
from scipy.integrate import tplquad

from scripts import r3m29_coulomb_cell as cell


def test_independent_adaptive_cube_integral_and_scale():
    reference, error = cell.cell_average_reference(0)
    assert error < 1e-8
    assert math.isclose(reference, 1.1900386819897764, rel_tol=1e-10)
    direct, _ = tplquad(lambda z, y, x: 1/math.sqrt(x*x+y*y+z*z),
                        0, 1, lambda _x: 0, lambda _x: 1,
                        lambda _x, _y: 0, lambda _x, _y: 1,
                        epsabs=1e-7, epsrel=1e-7)
    assert abs(direct-reference)/reference < 1e-6
    assert abs(cell.cell_average_gl(0, 256)-reference)/reference < 1e-6
    # The exact vertex-cell integral scales as h^2 and its mean as h^-1.
    for h in (.25, .2):
        integral = reference*h*h
        assert math.isclose(integral/(h**3), reference/h, rel_tol=1e-15)


def test_phase_symmetry_and_midpoint_error_are_distinct():
    for alpha in (0.0, .25, .5):
        a, _ = cell.cell_average_reference(alpha)
        b, _ = cell.cell_average_reference(1-alpha)
        assert math.isclose(a, b, rel_tol=1e-11)
        assert cell.midpoint(alpha) < a


def test_actual_trajectory_phase_histograms_cover_every_step():
    a = cell.phase_counts(.25, 7172, -30, 60, 32)
    b = cell.phase_counts(.2, 7172, -30, 60, 32)
    assert sum(a) == sum(b) == 7172
    assert min(a) > 0 and min(b) > 0
    assert (a[0], a[31]) == (227, 225)
    assert (b[7], b[8]) == (225, 225)
    assert .5*sum(abs(x-y) for x, y in zip(a, b))/7172 < .01


def test_frozen_input_mutation_rejected(monkeypatch, tmp_path):
    original = cell.DESIGN
    try:
        design = tmp_path/'design.json'
        design.write_text(original.read_text().replace('7172', '7173', 1))
        monkeypatch.setattr(cell, 'DESIGN', design)
        with pytest.raises(ValueError, match='unexpected diagnostic design'):
            cell.bind_design()
    finally:
        monkeypatch.setattr(cell, 'DESIGN', original)
