import numpy as np

from cr_repro.r3m11 import ControlledTDLRunner
from scripts.r3m20_matrix_free import MatrixFreeFullH
from scripts.r3m21_cf4_reference import raw_distance, reference_gate


def test_registered_reference_gate_requires_all_independent_repeats():
    signal = 2e-8
    good = {"outer_16_to_32": 1e-10,
            "inner_16_repeat": 1e-11,
            "substep_8_repeat": 1e-11}
    assert reference_gate(good, signal) == "REFERENCE_RESOLVED_FOR_PRIOR_CF4_4_ERROR_SCALE"
    assert reference_gate({**good, "outer_16_to_32": 2e-10}, signal) == "REFERENCE_UNRESOLVED_ONE_PERCENT_GATE"
    assert reference_gate({"outer_16_to_32": 1e-10}, signal) == "REFERENCE_UNRESOLVED_INCOMPLETE_REPEATS"


def test_cf4_action_substeps_are_separate_from_outer_step_on_tiny_full_h():
    shape = (4, 4, 4)
    spacing = .7
    cfg = dict(energy_keV_per_u=100., b=.9, backend="numpy", dt=.025,
               grid=dict(xlim=[-1.4, 1.4], ylim=[-1.4, 1.4], zlim=[-1.4, 1.4], dx=spacing),
               z_start=-2., z_stop=2., initial_state="analytic", project_nmax=1,
               absorber_width=spacing, absorber_power=.125,
               absorber_reference_dt=.05, capture_plane=0.)
    runner = ControlledTDLRunner(cfg)
    mf = MatrixFreeFullH(runner)
    rng = np.random.default_rng(20260923)
    state = (rng.normal(size=shape) + 1j * rng.normal(size=shape)).astype(complex)
    state /= np.linalg.norm(state)

    def propagate(steps, substeps, tol=1e-12):
        current = state.copy()
        for j in range(steps):
            current, info = mf.step(current, -.08 + j * .16 / steps, .16 / steps,
                                    method="cf4", tol=tol, max_basis=10,
                                    action_substeps=substeps)
            assert all(a["converged"] for a in info["actions"])
        return current

    coarse4 = propagate(4, 4)
    coarse8 = propagate(8, 4)
    divided8 = propagate(8, 8)
    tight8 = propagate(8, 4, 1e-13)
    outer = raw_distance(coarse4, coarse8, runner.dv)
    assert outer > 0
    assert raw_distance(coarse8, divided8, runner.dv) < .01 * outer
    assert raw_distance(coarse8, tight8, runner.dv) < .01 * outer
