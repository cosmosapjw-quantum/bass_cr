"""Opt-in contractive Arnoldi action for the frozen full discrete H-iW.

The upper bound is a theorem for exact arithmetic and nonexpansive generators.
Finite-precision FFT/orthogonalization effects require independent repeats.
This module does not alter R3M20/R3M21 or the frozen production splitter.
"""
from __future__ import annotations

import math

import numpy as np
from scipy.linalg import expm

from scripts.r3m19_fullh_diagnostic import CF_A, CF_B, CF_C1, CF_C2
from scripts.r3m20_matrix_free import MatrixFreeFullH, _array_module, _real_scalar


def bounded_arnoldi_action(op, psi, dt, *, physical_scale, physical_budget,
                           max_basis, max_basis_bytes=None):
    """Approximate exp(dt*op) psi with a contractive exact-arithmetic bound.

    Caller must prove the generator's Hermitian part is nonpositive.  For
    B=dt*op and t=1, Jawecki et al. Theorem 1 gives beta*h_(m+1,m)*
    product(h_(j+1,j), j=1..m-1)/m!.  We separately test roundoff empirically.
    """
    if (type(max_basis) is not int or not 1 <= max_basis <= 32
            or not math.isfinite(float(dt)) or dt <= 0
            or not math.isfinite(float(physical_scale)) or physical_scale <= 0
            or not math.isfinite(float(physical_budget)) or physical_budget <= 0):
        raise ValueError("positive bounded action parameters required")
    xp = _array_module(psi)
    state = xp.asarray(psi)
    if state.size == 0 or state.dtype != xp.dtype("complex128"):
        raise ValueError("nonempty complex128 state required")
    basis_bytes = (max_basis + 1) * int(state.nbytes)
    if state.size > 512 and (max_basis_bytes is None or max_basis_bytes < basis_bytes):
        raise MemoryError("large action exceeds declared basis budget")
    if not bool(xp.all(xp.isfinite(state)).item()):
        raise ValueError("finite state required")
    beta = _real_scalar(xp.linalg.norm(state.ravel()))
    if not math.isfinite(beta) or beta <= 0:
        raise ValueError("positive finite state norm required")
    basis = [state / beta]
    hessenberg = np.zeros((max_basis + 1, max_basis), dtype=np.complex128)
    result = None
    upper = math.inf
    for j in range(max_basis):
        work = xp.asarray(op(basis[j]), dtype=xp.complex128) * dt
        if work.shape != state.shape:
            raise ValueError("operator changed state shape")
        for _ in range(2):
            for i in range(j + 1):
                coefficient = complex(xp.vdot(basis[i], work).item())
                hessenberg[i, j] += coefficient
                work -= coefficient * basis[i]
        hnext = _real_scalar(xp.linalg.norm(work.ravel()))
        if not math.isfinite(hnext):
            raise FloatingPointError("nonfinite Arnoldi subdiagonal")
        hessenberg[j + 1, j] = hnext
        m = j + 1
        small = hessenberg[:m, :m]
        e1 = np.zeros(m, dtype=np.complex128)
        e1[0] = 1
        coefficients = expm(small) @ e1
        result = xp.zeros_like(state)
        for k, coefficient in enumerate(coefficients):
            result += (beta * coefficient) * basis[k]
        gamma = math.prod(float(hessenberg[k + 1, k].real) for k in range(m - 1))
        upper = float(beta * physical_scale * hnext * gamma / math.factorial(m))
        if not math.isfinite(upper):
            raise FloatingPointError("nonfinite contractive action bound")
        if upper <= physical_budget:
            if not bool(xp.all(xp.isfinite(result)).item()):
                raise FloatingPointError("nonfinite Arnoldi action")
            return result, dict(converged=True, basis_dimension=m, matvec_count=m,
                                physical_upper_bound=upper,
                                requested_physical_budget=float(physical_budget),
                                bound_semantics="NONEXPANSIVE_EXACT_ARITHMETIC_THEOREM_1_NOT_ROUNDOFF_CERTIFICATE",
                                basis_payload_bytes=basis_bytes)
        if hnext == 0:
            raise RuntimeError("inner action unresolved: zero subdiagonal with nonzero bound")
        if hnext <= 32 * np.finfo(float).eps * max(1., np.linalg.norm(small)):
            raise RuntimeError("inner action unresolved at roundoff floor")
        if m < max_basis:
            basis.append(work / hnext)
    raise RuntimeError("inner action unresolved within bounded Arnoldi basis")


class BoundedMatrixFreeFullH(MatrixFreeFullH):
    """CF4 full-generator stages with an explicit physical global inner budget."""

    def cf4_step(self, psi, t0, dt, *, physical_step_budget, action_substeps,
                 max_basis=10, max_basis_bytes=None):
        state = self._state(psi)
        if (not math.isfinite(float(t0)) or not math.isfinite(float(dt)) or dt <= 0
                or type(action_substeps) is not int or not 1 <= action_substeps <= 8
                or not math.isfinite(float(physical_step_budget)) or physical_step_budget <= 0):
            raise ValueError("finite ordered CF4 step and positive inner budget required")
        first = self._potential(t0 + CF_C1 * dt)
        second = self._potential(t0 + CF_C2 * dt)
        specs = (CF_A * first + CF_B * second,
                 CF_B * first + CF_A * second)
        del first, second
        local_budget = physical_step_budget / (2 * action_substeps)
        actions = []
        for potential in specs:
            op = lambda x, p=potential: self._linear_matvec(x, p, .5, .5)
            for _ in range(action_substeps):
                state, info = bounded_arnoldi_action(op, state, dt / action_substeps,
                                                      physical_scale=math.sqrt(self.runner.dv),
                                                      physical_budget=local_budget,
                                                      max_basis=max_basis,
                                                      max_basis_bytes=max_basis_bytes)
                actions.append(info)
        return state, dict(actions=actions, total_fft_matvec=sum(a["matvec_count"] for a in actions),
                           accumulated_exact_arithmetic_upper_bound=sum(a["physical_upper_bound"] for a in actions),
                           action_substeps=action_substeps,
                           budget_semantics="CONTRACTIVE_EXACT_ARITHMETIC_PLUS_SEPARATE_ROUNDOFF_REPEAT")
