"""Bounded same-spatial-Hamiltonian temporal oracle; atomic units throughout.

Dense DFT construction plus full-H eigendecomposition supplies an independent
time evolution for at most 512 grid points. It is NOT a continuum oracle, a
production collision, or an admission test for charge-exchange probabilities.
The historical R3M16 splitter is deliberately reused as the object under test.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
from pathlib import Path

import numpy as np

from cr_repro.r3m11 import ControlledTDLRunner, source_digest
from scripts.r3m16_target_only_hdt import target_only_step

FROZEN_SOURCE = "581ff84930bb862efafdfec5d39d5b25aebf9297ce7ce45f833a5abe125b2a5b"
ABSOLUTE_MAX_POINTS = 512


def _positive(value: float, name: str) -> float:
    value = float(value)
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be positive and finite")
    return value


def _norm(state, dv: float, xp=np) -> float:
    if state.size == 0 or not bool(xp.all(xp.isfinite(state)).item()):
        raise ValueError("nonempty finite states required")
    norm = float((xp.sum(xp.abs(state)**2) * dv).item())
    return _positive(norm, "state probability norm")


def stable_phase_metrics(a, b, dv: float, xp=np) -> dict:
    """Direct differences avoid cancellation in sqrt(2 - 2*sqrt(fidelity)).

    a/b must already be in the SAME Hilbert space and weighting; equal shape
    alone does not establish matching grids, operators, or state authority.
    NumPy is tested here; CuPy is supported through xp but not GPU-verified.
    Ray distance normalizes both states. The separately reported unnormalized
    distance retains probability-norm loss (e.g. CAP loss).
    """
    dv = _positive(dv, "dv")
    a, b = xp.asarray(a, dtype=xp.complex128), xp.asarray(b, dtype=xp.complex128)
    if a.shape != b.shape:
        raise ValueError("state shapes differ; broadcasting is forbidden")
    na, nb = _norm(a, dv, xp), _norm(b, dv, xp)
    u, v = a/math.sqrt(na), b/math.sqrt(nb)
    overlap = complex((xp.sum(xp.conj(u)*v)*dv).item())
    # arg is undetermined for orthogonal rays; any phase gives the same norm.
    phase = overlap.conjugate()/abs(overlap) if abs(overlap) else 1+0j
    ray_distance = float(xp.sqrt(xp.sum(xp.abs(u-phase*v)**2)*dv).item())
    aligned = float(xp.sqrt(xp.sum(xp.abs(a-phase*b)**2)*dv).item())
    unaligned = float(xp.sqrt(xp.sum(xp.abs(a-b)**2)*dv).item())
    return {
        "ray_distance": ray_distance,
        "phase_aligned_state_distance": aligned,
        "unaligned_state_distance": unaligned,
        "norm_first": na, "norm_second": nb,
        "probability_norm_change": nb-na,
        "overlap_abs_normalized": abs(overlap), "fidelity": abs(overlap)**2,
        "alignment_phase": [phase.real, phase.imag],
        "method": "DIRECT_NORMALIZED_PHASE_ALIGNED_DIFFERENCE",
        "fidelity_roundoff_clipped": False,
        "metric_only_no_identity_validation": True,
    }


def _hermitian_matrix(H, size: int):
    H = np.asarray(H, dtype=np.complex128)
    if H.shape != (size, size) or not np.isfinite(H).all():
        raise ValueError("invalid finite Hamiltonian shape")
    scale = max(1.0, float(np.linalg.norm(H, ord="fro")))
    if np.linalg.norm(H-H.conj().T, ord="fro") > 64*np.finfo(float).eps*size*scale:
        raise ValueError("Hamiltonian must be Hermitian; no symmetrization applied")
    return H


def normalized_hamiltonian_moments(psi, H, dv: float) -> dict:
    """E=<psi|H|psi>/<psi|psi>, sigma=||(H-E)psi||/||psi||.

    Matrix action is independent of FFT/splitting. Direct residual evaluation
    avoids subtracting two nearly equal energy-squared moments.
    """
    dv = _positive(dv, "dv")
    psi = np.asarray(psi, dtype=complex).ravel()
    norm = _norm(psi, dv)
    H = _hermitian_matrix(H, psi.size)
    hpsi = H@psi
    energy = complex(np.vdot(psi, hpsi)*dv/norm)
    residual2 = float(np.vdot(hpsi-energy.real*psi, hpsi-energy.real*psi).real*dv/norm)
    return {"energy_Eh": energy.real, "energy_imaginary_roundoff_Eh": energy.imag,
            "variance_Eh2": residual2, "stationary_residual_Eh": math.sqrt(residual2),
            "probability_norm": norm, "normalized_expectation": True}


def _bounded_shape(shape, max_points: int = ABSOLUTE_MAX_POINTS) -> tuple[int, int, int]:
    if len(shape) != 3 or any(isinstance(n, (bool, np.bool_)) or not isinstance(n, (int, np.integer)) or n < 1 for n in shape):
        raise ValueError("shape must contain three positive integers")
    if isinstance(max_points, bool) or not isinstance(max_points, (int, np.integer)) or not 1 <= max_points <= ABSOLUTE_MAX_POINTS:
        raise ValueError("max_points must not exceed hard bound 512")
    points = math.prod(shape)
    if points > max_points:
        raise MemoryError(f"dense oracle refuses {points} points; bounded at {max_points}")
    return tuple(int(n) for n in shape)


def dense_fourier_hamiltonian(shape, spacing: float, potential, *, max_points: int = ABSOLUTE_MAX_POINTS):
    """Construct H=F^dag diag(k^2/2) F+diag(V), without FFT or split products.

    Boundary conditions and wave numbers match the runner's periodic Fourier
    collocation. Translation to cell centers cancels in the kinetic matrix.
    T is separable; V is explicitly real. The 512-point cap is mandatory.
    """
    shape = _bounded_shape(shape, max_points)
    spacing = _positive(spacing, "spacing")
    potential = np.asarray(potential)
    if potential.shape != shape or not np.isfinite(potential).all() or np.iscomplexobj(potential):
        raise ValueError("real finite sampled potential with matching shape required")
    transforms, wave_numbers = [], []
    for n in shape:
        indices = np.arange(n)
        # Explicit signed mode convention, including negative even Nyquist.
        modes = np.where(indices < (n+1)//2, indices, indices-n)
        transforms.append(np.exp(-2j*np.pi*np.outer(modes, indices)/n)/math.sqrt(n))
        wave_numbers.append(2*np.pi*modes/(n*spacing))
    F = np.kron(np.kron(transforms[0], transforms[1]), transforms[2])
    k2 = (wave_numbers[0][:,None,None]**2+wave_numbers[1][None,:,None]**2
          +wave_numbers[2][None,None,:]**2).ravel()
    H = F.conj().T@((0.5*k2)[:,None]*F)+np.diag(potential.ravel())
    return _hermitian_matrix(H, math.prod(shape))


def exact_static_evolution(H, psi, time: float):
    """Full finite-H evolution via eigenpairs; no split operator involved."""
    psi = np.asarray(psi, dtype=complex)
    _norm(psi, 1.0)
    time = float(time)
    if not math.isfinite(time):
        raise ValueError("finite evolution time required")
    H = _hermitian_matrix(H, psi.size)
    energies, basis = np.linalg.eigh(H)
    return (basis@(np.exp(-1j*energies*time)*(basis.conj().T@psi.ravel()))).reshape(psi.shape)


def make_tiny_runner(shape, spacing: float) -> ControlledTDLRunner:
    shape = _bounded_shape(shape)
    spacing = _positive(spacing, "spacing")
    if any(n % 2 for n in shape):
        raise ValueError("tiny Coulomb runner uses even dimensions to avoid a nuclear grid point")
    limits = [[-n*spacing/2, n*spacing/2] for n in shape]
    return ControlledTDLRunner({
        "energy_keV_per_u": 100.0, "b": 2.0, "backend": "numpy", "dt": 0.05,
        "grid": dict(zip(("xlim", "ylim", "zlim"), limits), dx=spacing),
        "z_start": -1.0, "z_stop": 1.0, "absorber_width": 0.0,
        "absorber_power": 0.125, "absorber_reference_dt": 0.05,
        "project_nmax": 1, "capture_plane": 1.0,
        "initial_state": "analytic",
    })


def _array_sha(value) -> str:
    value = np.ascontiguousarray(value)
    digest = hashlib.sha256()
    digest.update(json.dumps({"dtype": value.dtype.str, "shape": value.shape}, sort_keys=True).encode())
    digest.update(value.tobytes())
    return digest.hexdigest()


def run_moving_reference(shape=(4,4,4), spacing=0.7, horizon=0.4, steps=(8,16,32)) -> dict:
    """Tiny moving physical two-center -1/r model, with no CAP.

    DOP853 independently integrates the full dense finite-H Schrödinger ODE.
    This exercises the production runner's midpoint time-dependent potential,
    unlike the autonomous target test. It is still SAME-discretization only.
    Repeating the oracle at tighter tolerance is empirical verification, not a
    rigorous ODE-error certificate. Neither trajectory is production data.
    """
    import scipy
    from scipy.integrate import solve_ivp

    if source_digest() != FROZEN_SOURCE:
        raise ValueError("frozen numerical source digest mismatch")
    horizon = _positive(horizon, "horizon")
    if len(steps) != 3 or any(isinstance(n, bool) or not isinstance(n, (int, np.integer)) or not 1 <= n <= 1024 for n in steps):
        raise ValueError("exactly three positive integer step counts <=1024 required")
    if steps[1] != 2*steps[0] or steps[2] != 2*steps[1]:
        raise ValueError("temporal oracle requires exact factor-two refinement")
    template = make_tiny_runner(shape, spacing)
    cfg = dict(template.cfg)
    cfg.update(b=0.9, z_start=-template.v*horizon/2, z_stop=template.v*horizon/2,
               dt=float(np.nextafter(horizon/steps[0], math.inf)))
    runner = ControlledTDLRunner(cfg)
    Htarget = dense_fourier_hamiltonian(shape, spacing, np.asarray(runner.Vtarget))
    kinetic = Htarget-np.diag(np.asarray(runner.Vtarget).ravel())
    _, U = np.linalg.eigh(Htarget)
    initial = U[:,0]/math.sqrt(runner.dv)
    X,Y,Z = np.meshgrid(*runner.spec.axes(), indexing="ij")
    X,Y,Z = X.ravel(), Y.ravel(), Z.ravel()
    vtarget = -1/np.sqrt(X**2+Y**2+Z**2)
    transverse2 = (X-runner.b)**2+Y**2
    min_transverse = math.sqrt(float(transverse2.min()))
    if min_transverse <= 0:
        raise ValueError("projectile crosses sampled nuclear singularity")
    references = []
    for rtol, atol in ((2e-11, 2e-13), (2e-13, 2e-15)):
        evaluations = 0
        def rhs(t, psi):
            nonlocal evaluations
            evaluations += 1
            if evaluations > 10000:
                raise RuntimeError("bounded DOP853 RHS budget of 10000 exhausted")
            sampled = vtarget-1/np.sqrt(transverse2+(Z-runner.v*t)**2)
            return -1j*(kinetic@psi+sampled*psi)
        solution = solve_ivp(rhs, (runner.t0,runner.tf), initial, method="DOP853",
                             rtol=rtol, atol=atol, t_eval=[runner.tf])
        if not solution.success or solution.t[-1] != runner.tf or not np.isfinite(solution.y).all():
            raise RuntimeError(f"DOP853 reference failed: {solution.message}")
        references.append({"rtol": rtol, "atol": atol, "nfev": solution.nfev,
                           "state": solution.y[:,-1], "status": int(solution.status)})
    exact = references[-1]["state"]
    repeat = stable_phase_metrics(references[0]["state"], exact, runner.dv)
    rows = []
    for nstep in steps:
        local_cfg = dict(cfg, dt=float(np.nextafter(horizon/nstep, math.inf)))
        local = ControlledTDLRunner(local_cfg)
        if local.nstep != nstep or local.t0 != runner.t0 or local.tf != runner.tf:
            raise ValueError("runner dt scheduling does not match preregistered horizon/ladder")
        state = initial.reshape(shape).copy()
        for j in range(local.nstep):
            state = local.step(state, local.t0+(j+0.5)*local.dt_actual)
        metrics = stable_phase_metrics(exact, state.ravel(), runner.dv)
        rows.append({"requested_dt": local_cfg["dt"], "actual_dt": local.dt_actual,
                     "nstep": int(local.nstep), "physical_start_time": local.t0,
                     "physical_end_time": local.tf, "ray_error_vs_reference": metrics["ray_distance"],
                     "unaligned_state_error_vs_reference": metrics["unaligned_state_distance"],
                     "norm_drift": local.norm(state)-float(np.vdot(initial,initial).real*runner.dv),
                     "same_saved_initial_array_sha256": _array_sha(initial)})
    errors = [row["ray_error_vs_reference"] for row in rows]
    orders = [math.log(errors[i]/errors[i+1])/math.log(rows[i]["actual_dt"]/rows[i+1]["actual_dt"])
              if min(errors[i:i+2]) > 1e-13 else None for i in range(2)]
    return {
        "oracle_method": "EXPLICIT_DFT_KINETIC_PLUS_MOVING_COULOMB_DOP853",
        "source_under_test": "ControlledTDLRunner.step", "production_collision": False,
        "continuum_spatial_validation": False, "CAP_included": False,
        "shape": list(shape), "spacing_a0": spacing, "energy_keV_per_u": 100.0,
        "impact_parameter_a0": runner.b, "physical_start_time": runner.t0,
        "physical_end_time": runner.tf, "projectile_speed_au": runner.v,
        "minimum_projectile_transverse_distance_a0": min_transverse,
        "initial": normalized_hamiltonian_moments(initial,Htarget,runner.dv),
        "initial_state_sha256": _array_sha(initial), "target_Hamiltonian_sha256": _array_sha(Htarget),
        "reference_runs": [{k:v for k,v in row.items() if k != "state"} for row in references],
        "oracle_repeat_ray_distance": repeat["ray_distance"],
        "oracle_repeat_unaligned_state_distance": repeat["unaligned_state_distance"],
        "oracle_refinement_resolved": bool(repeat["unaligned_state_distance"] < 1e-3*errors[-1]),
        "oracle_validation_semantics": "TIGHTER_TOLERANCE_REPEAT_EMPIRICAL_NOT_CERTIFIED",
        "oracle_fine_norm_drift": repeat["norm_second"]-float(np.vdot(initial,initial).real*runner.dv),
        "runs": rows, "empirical_orders_vs_reference": orders,
        "scipy_version": scipy.__version__, "numerical_source_digest": source_digest(),
    }


def run_reference_experiment(shape=(4,4,4), spacing=0.7, horizon=0.4, steps=(8,16,32)) -> dict:
    """Compare target splitter to independently exponentiated SAME H_h.

    Exact discrete ground states eliminate preparation-ray drift. A smooth
    periodic control verifies the order oracle. The tiny Coulomb case verifies
    the temporal implementation without resolving continuum Coulomb physics.
    """
    if source_digest() != FROZEN_SOURCE:
        raise ValueError("frozen numerical source digest mismatch")
    horizon = _positive(horizon, "horizon")
    if len(steps) != 3 or any(isinstance(n, bool) or not isinstance(n, (int, np.integer)) or n < 1 or n > 1024 for n in steps):
        raise ValueError("exactly three positive integer step counts <=1024 required")
    if steps[1] != 2*steps[0] or steps[2] != 2*steps[1]:
        raise ValueError("temporal oracle requires exact factor-two refinement")
    runner = make_tiny_runner(shape, spacing)
    shape = tuple(runner.Vtarget.shape)
    x,y,z = runner.spec.axes()
    smooth = (0.4*np.cos(2*np.pi*x[:,None,None]/(shape[0]*spacing))
              +0.3*np.sin(2*np.pi*y[None,:,None]/(shape[1]*spacing))
              +0.2*np.cos(2*np.pi*z[None,None,:]/(shape[2]*spacing)))
    cases = {}
    for name, V in (("cell_centered_coulomb", runner.Vtarget.copy()), ("smooth_periodic", smooth)):
        runner.Vtarget = V
        H = dense_fourier_hamiltonian(shape, spacing, V)
        eig, U = np.linalg.eigh(H)
        initial = U[:,0].reshape(shape)/math.sqrt(runner.dv)
        exact = exact_static_evolution(H, initial, horizon)
        rows = []
        for nstep in steps:
            dt = horizon/nstep
            final = initial.copy()
            for _ in range(nstep):
                final = target_only_step(runner, final, dt)
            metrics = stable_phase_metrics(exact, final, runner.dv)
            moments = normalized_hamiltonian_moments(final, H, runner.dv)
            rows.append({"requested_dt": dt, "actual_dt": dt, "nstep": int(nstep),
                         "physical_end_time": horizon,
                         "ray_error_vs_exact_same_H": metrics["ray_distance"],
                         "norm_drift": metrics["norm_second"]-runner.norm(initial),
                         "energy_drift_Eh": moments["energy_Eh"]-float(eig[0]),
                         "same_saved_initial_array_sha256": _array_sha(initial)})
        errors = [row["ray_error_vs_exact_same_H"] for row in rows]
        orders = [math.log(errors[i]/errors[i+1])/math.log(2) if min(errors[i:i+2]) > 1e-13 else None for i in range(2)]
        cases[name] = {
            "oracle_method": "EXPLICIT_DFT_FULL_H_DENSE_EIGH",
            "initial": normalized_hamiltonian_moments(initial, H, runner.dv),
            "initial_kind": "EXACT_DISCRETE_GROUND_EIGENSTATE",
            "initial_state_sha256": _array_sha(initial), "Hamiltonian_sha256": _array_sha(H),
            "exact_eigenstate_ray_drift": stable_phase_metrics(initial, exact, runner.dv)["ray_distance"],
            "runs": rows, "empirical_orders_vs_exact": orders,
            "order_semantics": "TEMPORAL_ONLY_FIXED_SPATIAL_H_NOT_CAPTURE_ERROR_BOUND",
        }
    return {
        "schema": "BASS_CR_R3M17_DENSE_TEMPORAL_ORACLE_V1", "status": "COMPLETE",
        "claim_scope": "SAME_DISCRETE_PERIODIC_HAMILTONIAN_TEMPORAL_IMPLEMENTATION_CHECK",
        "production_admission": False, "continuum_spatial_validation": False,
        "projectile_included": False, "CAP_included": False,
        "atomic_units": True, "grid_shape": list(shape), "spacing_a0": spacing,
        "dense_max_points": ABSOLUTE_MAX_POINTS,
        "estimated_dense_working_bytes": 10*16*math.prod(shape)**2,
        "numerical_source_digest": source_digest(),
        "instrumentation_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "runtime": {"python": platform.python_version(), "numpy": np.__version__,
                    "backend": "numpy", "platform": platform.platform(),
                    "cupy_execution": "NOT_EXECUTED", "canonical_gpu_runtime_match": False},
        "cases": cases,
    }


def write_new(path: Path, value) -> None:
    data = json.dumps(value, indent=2, allow_nan=False)+"\n"
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        stream.write(data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--shape", nargs=3, type=int, default=[4,4,4])
    parser.add_argument("--spacing", type=float, default=0.7)
    parser.add_argument("--horizon", type=float, default=0.4)
    parser.add_argument("--coarse-steps", type=int, default=8)
    parser.add_argument("--include-moving", action="store_true",
                        help="include tiny moving-two-center DOP853 comparison (not production)")
    args = parser.parse_args()
    # Refuse existing outputs before spending computation; open('x') also
    # enforces create-only semantics if a concurrent process wins the race.
    if args.out.exists():
        raise FileExistsError(args.out)
    result = run_reference_experiment(args.shape, args.spacing, args.horizon,
                                      tuple(args.coarse_steps*2**i for i in range(3)))
    if args.include_moving:
        result["moving_two_center"] = run_moving_reference(args.shape, args.spacing, args.horizon,
                                                          tuple(args.coarse_steps*2**i for i in range(3)))
    write_new(args.out, result)
    print(json.dumps({"status": result["status"], "output": str(args.out),
                      "production_admission": False}))


if __name__ == "__main__":
    main()
