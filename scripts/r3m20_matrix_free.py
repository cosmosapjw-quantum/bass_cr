"""Opt-in matrix-free actions for the frozen periodic full H_h(t)-iW.

This sidecar does not change the production splitter. Arnoldi's residual is an
inner-action *indicator*, not a certified global or observable error bound.
The caller must compare basis/tolerance refinements against an independent
reference before admitting a large-window result.
"""
from __future__ import annotations

import math
from typing import Callable

import numpy as np
from scipy.linalg import expm

from cr_repro.r3m11 import source_digest
from scripts.r3m19_fullh_diagnostic import CF_A, CF_B, CF_C1, CF_C2, FROZEN_SOURCE


MAX_BASIS = 32
LARGE_STATE_POINTS = 512


def _array_module(value):
    if type(value).__module__.split(".")[0] == "cupy":
        import cupy as cp
        return cp
    return np


def _real_scalar(value):
    return float(value.item() if hasattr(value, "item") else value)


def arnoldi_expm_action(op: Callable, psi, dt: float, *, tol: float,
                        max_basis: int, max_basis_bytes: int | None = None):
    """Compute exp(dt*op) psi with twice reorthogonalized non-Hermitian Arnoldi.

    The Saad phi1 residual is used as an empirical stopping indicator. A caller
    must treat ``converged=False`` as unusable and perform an independent inner
    refinement for its intended error scale. One basis is stored at a time; no
    Hermitian/Lanczos assumption is made.
    """
    if (isinstance(dt, bool) or not math.isfinite(dt) or dt <= 0 or
            isinstance(tol, bool) or not math.isfinite(tol) or tol <= 0 or
            type(max_basis) is not int or not 1 <= max_basis <= MAX_BASIS):
        raise ValueError("finite positive dt/tol and bounded Arnoldi basis required")
    xp = _array_module(psi)
    state = xp.asarray(psi)
    if state.dtype != xp.dtype("complex128") or state.size == 0:
        raise ValueError("nonempty complex128 state required")
    if state.size > LARGE_STATE_POINTS and max_basis_bytes is None:
        raise MemoryError("large action requires explicit basis-byte budget")
    basis_bytes = (max_basis + 1) * int(state.nbytes)
    if max_basis_bytes is not None and (type(max_basis_bytes) is not int or
                                        max_basis_bytes < basis_bytes):
        raise MemoryError("Arnoldi basis exceeds declared byte budget")
    if not bool(xp.all(xp.isfinite(state)).item()):
        raise ValueError("finite state required")
    norm0 = _real_scalar(xp.linalg.norm(state.ravel()))
    if not math.isfinite(norm0) or norm0 <= 0:
        raise ValueError("positive finite state norm required")
    basis = [state / norm0]
    hessenberg = np.zeros((max_basis + 1, max_basis), dtype=np.complex128)
    result = None
    indicator = math.inf
    converged = False
    for j in range(max_basis):
        work = xp.asarray(op(basis[j]), dtype=xp.complex128) * dt
        if work.shape != state.shape:
            raise ValueError("operator changed state shape")
        # Two MGS passes avoid loss of orthogonality in the nonnormal case.
        for _ in range(2):
            for i in range(j + 1):
                projection = complex(xp.vdot(basis[i], work).item())
                hessenberg[i, j] += projection
                work -= projection * basis[i]
        hnext = _real_scalar(xp.linalg.norm(work.ravel()))
        hessenberg[j + 1, j] = hnext
        small = hessenberg[:j + 1, :j + 1]
        e1 = np.zeros(j + 1, dtype=np.complex128)
        e1[0] = 1
        coefficients = expm(small) @ e1
        result = xp.zeros_like(state)
        for k, coefficient in enumerate(coefficients):
            result += (norm0 * coefficient) * basis[k]
        # phi1(H)e1 is the upper-right column of exp([[H,e1],[0,0]]).
        augmented = np.zeros((j + 2, j + 2), dtype=np.complex128)
        augmented[:j + 1, :j + 1] = small
        augmented[:j + 1, j + 1] = e1
        phi1_last = expm(augmented)[j, j + 1]
        indicator = float(norm0 * hnext * abs(phi1_last))
        if not math.isfinite(indicator):
            raise FloatingPointError("nonfinite Arnoldi residual indicator")
        if hnext <= 64 * np.finfo(float).eps * max(1., np.linalg.norm(small)) or indicator <= tol * norm0:
            converged = True
            break
        if j + 1 < max_basis:
            basis.append(work / hnext)
    if not bool(xp.all(xp.isfinite(result)).item()):
        raise FloatingPointError("nonfinite Arnoldi action")
    info = dict(method="ARNOLDI_TWICE_REORTHOGONALIZED_NONHERMITIAN",
                residual_indicator_semantics="EMPIRICAL_PHI1_NOT_GLOBAL_CERTIFICATE",
                converged=converged, relative_tolerance=tol,
                residual_indicator=indicator, basis_dimension=j + 1,
                matvec_count=j + 1, basis_payload_bytes=basis_bytes)
    return result, info


class MatrixFreeFullH:
    """Same discrete H_h, cell centers, Fourier modes and fixed CAP as runner."""

    def __init__(self, runner, *, velocity_override: float | None = None):
        if source_digest() != FROZEN_SOURCE:
            raise ValueError("frozen numerical source digest mismatch")
        self.runner = runner
        self.xp = runner.xp
        self.matvec_monitor = None
        self.shape = runner.spec.shape()
        self.v = runner.v if velocity_override is None else float(velocity_override)
        if not math.isfinite(self.v):
            raise ValueError("finite projectile speed required")
        reference_dt = float(runner.cfg["absorber_reference_dt"])
        if not math.isfinite(reference_dt) or reference_dt <= 0:
            raise ValueError("positive CAP reference dt required")
        self.W = -self.xp.log(runner.mask) / reference_dt
        if bool(self.xp.any(self.W < 0).item()) or not bool(self.xp.all(self.xp.isfinite(self.W)).item()):
            raise ValueError("finite nonnegative CAP rate required")
        self.rho = self.xp.hypot(runner.X - runner.b, runner.Y)
        if bool(self.xp.any(self.rho <= 0).item()):
            raise ValueError("projectile nuclear grid singularity")

    def _state(self, psi):
        state = self.xp.asarray(psi)
        if state.shape != self.shape or state.dtype != self.xp.dtype("complex128"):
            raise ValueError("matching complex128 grid state required")
        return state

    def _kinetic(self, psi):
        if self.matvec_monitor is not None:
            self.matvec_monitor()
        return self.xp.fft.ifftn(.5 * self.runner.k2 * self.xp.fft.fftn(psi))

    def _potential(self, t):
        if not math.isfinite(float(t)):
            raise ValueError("finite time required")
        return self.runner.Vtarget - 1 / self.xp.hypot(self.rho, self.runner.Z - self.v * t)

    def _integrated_potential(self, t0, dt):
        if not math.isfinite(float(t0)) or not math.isfinite(float(dt)) or dt <= 0:
            raise ValueError("finite ordered interval required")
        q0 = self.runner.Z - self.v * t0
        q1 = self.runner.Z - self.v * (t0 + dt)
        if self.v == 0:
            projectile = -dt / self.xp.hypot(self.rho, q0)
        else:
            rsum = self.xp.hypot(self.rho, q0) + self.xp.hypot(self.rho, q1)
            x = -self.v * dt / rsum
            if bool(self.xp.any(self.xp.abs(x) >= 1).item()):
                raise ValueError("projectile integral unresolved")
            projectile = -2 * dt * self.xp.arctanh(x) / x / rsum
        return dt * self.runner.Vtarget + projectile

    def _linear_matvec(self, psi, potential, kinetic_weight, cap_weight):
        psi = self._state(psi)
        return -1j * (kinetic_weight * self._kinetic(psi) + potential * psi) - cap_weight * self.W * psi

    def generator_matvec(self, psi, t):
        return self._linear_matvec(psi, self._potential(t), 1., 1.)

    def averaged_generator_matvec(self, psi, t0, dt):
        return self._linear_matvec(psi, self._integrated_potential(t0, dt), dt, dt)

    def step(self, psi, t0, dt, *, method: str, tol: float, max_basis: int,
             max_basis_bytes: int | None = None, action_substeps: int = 1):
        """One full generator exponential or two full CF4 actions."""
        psi = self._state(psi)
        if not math.isfinite(float(t0)) or not math.isfinite(float(dt)) or dt <= 0:
            raise ValueError("finite ordered interval required")
        if type(action_substeps) is not int or not 1 <= action_substeps <= 8:
            raise ValueError("bounded full-generator action substeps required")
        if method == "midpoint":
            potential = self._potential(t0 + .5 * dt)
            specs = [(potential, 1., 1., dt)]
        elif method == "average":
            potential = self._integrated_potential(t0, dt)
            specs = [(potential, dt, dt, 1.)]
        elif method == "cf4":
            first = self._potential(t0 + CF_C1 * dt)
            second = self._potential(t0 + CF_C2 * dt)
            specs = [(CF_A * first + CF_B * second, .5, .5, dt),
                     (CF_B * first + CF_A * second, .5, .5, dt)]
            del first, second
        else:
            raise ValueError("method must be midpoint, average or cf4")
        state = psi
        actions = []
        for potential, kinetic_weight, cap_weight, action_dt in specs:
            op = lambda x, p=potential, k=kinetic_weight, w=cap_weight: self._linear_matvec(x, p, k, w)
            for _ in range(action_substeps):
                state, info = arnoldi_expm_action(op, state, action_dt / action_substeps,
                                                   tol=tol / action_substeps,
                                                   max_basis=max_basis, max_basis_bytes=max_basis_bytes)
                actions.append(info)
                if not info["converged"]:
                    raise RuntimeError("Arnoldi inner action unresolved within frozen basis/tolerance")
        return state, dict(method=method, actions=actions,
                           action_substeps=action_substeps,
                           total_fft_matvec=sum(x["matvec_count"] for x in actions),
                           inner_error_semantics="EMPIRICAL_RESIDUAL_PLUS_REQUIRED_REFINEMENT")


def tiny_independent_case(*, shape=(4, 4, 4), cap_on=True, velocity_sign=1,
                          horizon=.16, counts=(2, 4, 8)):
    """Bounded CPU dense/DOP853 cross-check; never accepts a production grid."""
    import time
    from scipy.integrate import solve_ivp
    from cr_repro.r3m11 import ControlledTDLRunner
    from scripts.r3m17_reference import dense_fourier_hamiltonian
    from scripts.r3m19_fullh_diagnostic import generator as dense_generator, make_model

    if (len(shape) != 3 or any(type(x) is not int or x < 2 or x % 2 for x in shape)
            or math.prod(shape) > 512 or not 0 < horizon <= 2
            or tuple(counts) != (2, 4, 8) or velocity_sign not in (-1, 0, 1)):
        raise ValueError("frozen tiny shape/horizon/ladder/velocity required")
    spacing = .7
    limits = [[-n * spacing / 2, n * spacing / 2] for n in shape]
    cfg = dict(energy_keV_per_u=100., b=.9, backend="numpy", dt=.025,
               grid=dict(zip(("xlim", "ylim", "zlim"), limits), dx=spacing),
               z_start=-2., z_stop=2., initial_state="analytic", project_nmax=1,
               absorber_width=spacing if cap_on else 0., absorber_power=.125,
               absorber_reference_dt=.05, capture_plane=0.)
    runner = ControlledTDLRunner(cfg)
    mf = MatrixFreeFullH(runner, velocity_override=runner.v * velocity_sign)
    target = np.asarray(runner.Vtarget)
    H = dense_fourier_hamiltonian(shape, spacing, target)
    K = H - np.diag(target.ravel())
    X, Y, Z = np.meshgrid(*runner.spec.axes(), indexing="ij")
    rho = np.hypot(X - runner.b, Y).ravel()
    W = -np.log(np.asarray(runner.mask).ravel()) / cfg["absorber_reference_dt"]
    model = make_model(K, target.ravel(), rho, Z.ravel(), mf.v, W)
    rng = np.random.default_rng(20260923)
    initial = rng.normal(size=shape) + 1j * rng.normal(size=shape)
    initial = initial.astype(np.complex128)
    initial /= math.sqrt(float(np.vdot(initial, initial).real) * runner.dv)
    t0 = -.08
    t1 = t0 + horizon
    rhs_total = 0

    def ode(max_step):
        nonlocal rhs_total
        count = 0
        def rhs(t, y):
            nonlocal count
            count += 1
            if count > 20000:
                raise RuntimeError("tiny DOP853 RHS cap exceeded")
            return dense_generator(model, t) @ y
        started = time.perf_counter()
        sol = solve_ivp(rhs, (t0, t1), initial.ravel(), method="DOP853",
                        rtol=4e-14, atol=4e-16, max_step=max_step,
                        t_eval=[t1])
        rhs_total += count
        if not sol.success or not np.isfinite(sol.y).all():
            raise RuntimeError("tiny independent DOP853 failed")
        return sol.y[:, -1], dict(rhs=count, max_step=max_step,
                                  wall_seconds=time.perf_counter() - started)

    coarse_ref, coarse_meta = ode(horizon / 16)
    ref, fine_meta = ode(horizon / 32)
    repeat_distance = float(np.linalg.norm(coarse_ref - ref) * math.sqrt(runner.dv))
    method_rows = []
    for n in counts:
        dt = horizon / n
        row = {"steps": n, "actual_dt": dt, "methods": {}}
        for method in ("midpoint", "average", "cf4"):
            state = initial.copy()
            max_indicator = 0.
            matvecs = 0
            started = time.perf_counter()
            for j in range(n):
                state, info = mf.step(state, t0 + j * dt, dt, method=method,
                                      tol=1e-12, max_basis=32)
                matvecs += info["total_fft_matvec"]
                max_indicator = max(max_indicator, *(a["residual_indicator"] for a in info["actions"]))
            row["methods"][method] = dict(raw_error_vs_ode=float(np.linalg.norm(state.ravel() - ref) * math.sqrt(runner.dv)),
                                            norm_final=float(np.vdot(state, state).real * runner.dv),
                                            maximum_inner_residual_indicator=max_indicator,
                                            fft_matvecs=matvecs,
                                            wall_seconds=time.perf_counter() - started)
        method_rows.append(row)
    # Refinement of the inner action is held at a fixed outer timestep.
    repeats = []
    for tolerance in (1e-11, 1e-13):
        state = initial.copy()
        for j in range(counts[-1]):
            state, _ = mf.step(state, t0 + j * horizon / counts[-1],
                               horizon / counts[-1], method="cf4",
                               tol=tolerance, max_basis=32)
        repeats.append(state)
    inner_repeat = float(np.linalg.norm((repeats[0] - repeats[1]).ravel()) * math.sqrt(runner.dv))
    smallest_error = min(row["methods"]["cf4"]["raw_error_vs_ode"] for row in method_rows)
    oracle_resolved = bool(repeat_distance < .01 * smallest_error and inner_repeat < .01 * smallest_error)
    norm_initial = float(np.vdot(initial, initial).real * runner.dv)
    norm_reference = float(np.vdot(ref, ref).real * runner.dv)
    return dict(scope="TINY_SAME_PERIODIC_H_h_MINUS_iW_TEMPORAL_ONLY",
                shape=list(shape), cap_on=bool(cap_on), velocity_sign=velocity_sign,
                horizon=horizon, initial_norm=norm_initial, reference_norm=norm_reference,
                reference_repeat_raw_distance=repeat_distance, reference_coarse=coarse_meta,
                reference_fine=fine_meta, rhs_total=rhs_total,
                inner_tolerances=[1e-11, 1e-13],
                inner_tolerance_repeat_raw_distance=inner_repeat,
                smallest_cf4_outer_error=smallest_error,
                oracle_resolved_at_one_percent=oracle_resolved,
                rows=method_rows, source_digest=source_digest(),
                production_admission=False, continuum_validation=False)


def main():
    import argparse
    import json
    from pathlib import Path
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tiny_suite", choices=("tiny_suite",))
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    cases = {}
    for label, shape, cap, velocity in (
            ("moving64_cap_off", (4, 4, 4), False, 1),
            ("moving64_cap_on", (4, 4, 4), True, 1),
            ("reverse64_cap_on", (4, 4, 4), True, -1),
            ("rect96_cap_on", (4, 4, 6), True, 1)):
        cases[label] = tiny_independent_case(shape=shape, cap_on=cap, velocity_sign=velocity)
    result = dict(schema="BASS_CR_R3M20_N1_MATRIX_FREE_TINY_V1", cases=cases,
                  all_oracle_resolved=all(x["oracle_resolved_at_one_percent"] for x in cases.values()),
                  large_window_gate="OPEN_PENDING_REVIEW_AND_RESOURCE_PREFLIGHT")
    with args.out.open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
    print(json.dumps({k: v["oracle_resolved_at_one_percent"] for k, v in cases.items()}, sort_keys=True))


if __name__ == "__main__":
    main()
