"""Causal HeIII pulse clock: immutable inputs, native certificates, exact endpoints.

This module does not load scientific files, compile a library, dispatch a worker,
write results, reconstruct a source, or choose an execution budget. The caller
must provide the source-pinned stored arrays and a separately built native library.
"""
from __future__ import annotations

import ctypes as C
from dataclasses import dataclass
from decimal import Context, Decimal, ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_EVEN
from fractions import Fraction
from functools import lru_cache
import math
from pathlib import Path
from typing import Any, Sequence

import numpy as np


class ClockError(RuntimeError):
    """The exact-input or arithmetic-certificate contract was not met."""


_PTR = C.POINTER(C.c_double)
_ERR_CAP = 512
_MAX_N = 20000
_MAX_SOURCE = 16
_MAX_M = 8192


def recommended_build_command(source: str | Path, output: str | Path) -> list[str]:
    """Return a command for the coordinator; never execute it here."""
    return [
        "c++", "-std=c++17", "-O2", "-shared", "-fPIC",
        "-fno-fast-math", "-ffp-contract=off", "-frounding-math",
        "-DCR_STRICT_BUILD=1", "-DCR_LAPACK_LP64=1",
        str(source), "-o", str(output), "-l:liblapack.so.3", "-l:libblas.so.3",
    ]


def _need(condition: bool, message: str) -> None:
    if not condition:
        raise ClockError(message)


def _ptr(a: np.ndarray | None) -> Any:
    return None if a is None else a.ctypes.data_as(_PTR)


def _input_array(value: Any, shape: tuple[int, ...] | None, order: str) -> np.ndarray:
    a = np.asarray(value)
    _need(a.dtype == np.dtype("float64"), "NATIVE_BINARY64_INPUT_REQUIRED")
    if shape is not None:
        _need(a.shape == shape, "INPUT_SHAPE_MISMATCH")
    _need(bool(np.all(np.isfinite(a))), "NONFINITE_INPUT")
    result = np.array(a, dtype=np.float64, order=order, copy=True)
    result.setflags(write=False)
    return result


def _positive_integer(value: Any, name: str, maximum: int) -> int:
    _need(isinstance(value, (int, np.integer)) and not isinstance(value, (bool, np.bool_)),
          name + "_INTEGER_REQUIRED")
    value = int(value)
    _need(1 <= value <= maximum, name + "_OUTSIDE_CONTRACT")
    return value


def _finite_float(value: Any, name: str) -> float:
    _need(not isinstance(value, (bool, np.bool_)) and
          isinstance(value, (int, float, np.integer, np.floating)),
          name + "_EXPLICIT_REAL_REQUIRED")
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError):
        raise ClockError(name + "_FINITE_BINARY64_REQUIRED") from None
    _need(math.isfinite(result), name + "_FINITE_REQUIRED")
    if isinstance(value, (int, np.integer)):
        _need(Fraction.from_float(result) == Fraction(int(value)),
              name + "_INTEGER_NOT_EXACTLY_REPRESENTABLE_IN_BINARY64")
    return result


def _fraction_down(x: Fraction) -> float:
    y = float(x)
    _need(math.isfinite(y), "FRACTION_OUTPUT_OVERFLOW")
    if Fraction.from_float(y) > x:
        y = math.nextafter(y, -math.inf)
    _need(math.isfinite(y) and Fraction.from_float(y) <= x,
          "FRACTION_LOWER_CONVERSION_FAILED")
    return y


def _fraction_up(x: Fraction) -> float:
    y = float(x)
    _need(math.isfinite(y), "FRACTION_OUTPUT_OVERFLOW")
    if Fraction.from_float(y) < x:
        y = math.nextafter(y, math.inf)
    _need(math.isfinite(y) and Fraction.from_float(y) >= x,
          "FRACTION_UPPER_CONVERSION_FAILED")
    return y


def _decimal_up(x: Decimal) -> float:
    y = float(x)
    _need(math.isfinite(y), "DECIMAL_OUTPUT_OVERFLOW")
    if Decimal.from_float(y) < x:
        y = math.nextafter(y, math.inf)
    _need(math.isfinite(y) and Decimal.from_float(y) >= x,
          "DECIMAL_UPPER_CONVERSION_FAILED")
    return y


@lru_cache(maxsize=256)
def _tail_cached(gamma_hex: str, horizon_hex: str, m: int, side: str) -> tuple:
    """Certified upper of exp(m*(ln(a)+1-a)); a uses encoded gamma and T.

    Decimal ln/exp are correctly rounded HALF_EVEN. One next_plus therefore
    encloses each transcendental from above; rational-to-Decimal and remaining
    scalar operations use explicit directed contexts.
    """
    gamma, horizon = float.fromhex(gamma_hex), float.fromhex(horizon_hex)
    a = Fraction.from_float(gamma) * Fraction.from_float(horizon) / m
    _need(a > 1 if side == "minus" else 0 < a < 1,
          "ENCODED_GAMMA_TAIL_DIRECTION_FAILED")
    floor = Context(prec=80, rounding=ROUND_FLOOR, Emin=-999999, Emax=999999)
    ceil = Context(prec=80, rounding=ROUND_CEILING, Emin=-999999, Emax=999999)
    near = Context(prec=80, rounding=ROUND_HALF_EVEN, Emin=-999999, Emax=999999)
    numerator, denominator = Decimal(a.numerator), Decimal(a.denominator)
    alo = floor.divide(numerator, denominator)
    ahi = ceil.divide(numerator, denominator)
    ln_hi = near.next_plus(near.ln(ahi))
    exponent_hi = ceil.multiply(
        Decimal(m), ceil.add(ln_hi, ceil.subtract(Decimal(1), alo)))
    _need(exponent_hi < 0, "TAIL_EXPONENT_NOT_STRICTLY_NEGATIVE")
    q_decimal = near.next_plus(near.exp(exponent_hi))
    q_upper = _decimal_up(q_decimal)
    _need(0 < q_upper < 1, "TAIL_UPPER_OUTSIDE_OPEN_UNIT_INTERVAL")
    return (str(a.numerator), str(a.denominator), str(exponent_hi),
            str(q_decimal), q_upper)


def tail_upper(gamma: float, horizon: float, m: int, side: str) -> dict[str, Any]:
    """Actual encoded-clock tail bound, not a source-time inference."""
    gamma = _finite_float(gamma, "GAMMA")
    horizon = _finite_float(horizon, "HORIZON")
    m = _positive_integer(m, "ORDER", _MAX_M)
    _need(gamma > 0 and horizon > 0 and side in ("minus", "plus"),
          "INVALID_TAIL_ARGUMENT")
    num, den, exponent_hi, decimal_hi, q = _tail_cached(
        gamma.hex(), horizon.hex(), m, side)
    return {
        "gamma_s_inverse": gamma, "gamma_hex": gamma.hex(),
        "a_numerator": int(num), "a_denominator": int(den),
        "a_fraction": num + "/" + den,
        "tail_upper": q, "tail_upper_hex": q.hex(),
        "tail_decimal_upper": decimal_hi,
        "tail_exponent_decimal_upper": exponent_hi,
        "tail_method": "Decimal80_directed_input_and_operations_ln_exp_next_plus",
    }


@dataclass(frozen=True)
class PreparedProblem:
    diag: np.ndarray
    lower: np.ndarray
    upper: np.ndarray
    rewards: np.ndarray
    weights: np.ndarray
    witness: np.ndarray
    all_time: np.ndarray
    source_ids: tuple[str, ...]
    beta_lower: float
    cw_upper: np.ndarray
    p_nominal: np.ndarray
    p_lower: np.ndarray
    p_upper: np.ndarray
    p_radius: np.ndarray
    all_time_residual_norm_upper: np.ndarray

    @property
    def n(self) -> int:
        return int(self.diag.size)

    @property
    def nsource(self) -> int:
        return int(self.weights.shape[0])


class ClockEngine:
    def __init__(self, library_path: str | Path):
        self.library_path = str(Path(library_path).resolve())
        self._lib = C.CDLL(self.library_path)
        self._lib.cr_native_info.argtypes = [C.POINTER(C.c_int), C.c_char_p, C.c_size_t]
        self._lib.cr_native_info.restype = C.c_int
        self._lib.cr_prepare.argtypes = (
            [C.c_int, C.c_int] + [_PTR] * 14 + [C.c_char_p, C.c_size_t]
        )
        self._lib.cr_prepare.restype = C.c_int
        self._lib.cr_clock.argtypes = (
            [C.c_int, C.c_int] + [_PTR] * 6 +
            [C.c_double, _PTR, C.c_int, C.c_double] +
            [_PTR] * 10 + [C.c_char_p, C.c_size_t]
        )
        self._lib.cr_clock.restype = C.c_int
        info = np.empty(10, dtype=np.int32)
        self._call(self._lib.cr_native_info, info.ctypes.data_as(C.POINTER(C.c_int)))
        self.native_info = {
            "abi_version": int(info[0]), "double_bytes": int(info[1]),
            "long_double_bytes": int(info[2]), "long_double_mantissa_bits": int(info[3]),
            "long_double_max_exponent": int(info[4]), "long_double_min_exponent": int(info[5]),
            "fenv_rounding": int(info[6]), "FE_TONEAREST": int(info[7]),
            "gcc_major": int(info[8]), "gcc_minor": int(info[9]),
            "fenv_mutated": False, "rhs_count": 2,
        }
        _need(info[0] == 1, "NATIVE_ABI_VERSION_MISMATCH")

    @staticmethod
    def _call(function: Any, *args: Any) -> None:
        error = C.create_string_buffer(_ERR_CAP)
        status = function(*args, error, _ERR_CAP)
        if status:
            raise ClockError("NATIVE_CERTIFICATE: " + error.value.decode("utf-8", "replace"))

    def prepare(
        self, diag: Any, lower: Any, upper: Any, rewards: Any, weights: Any,
        witness: Any, all_time: Any, source_ids: Sequence[str] | None = None,
    ) -> PreparedProblem:
        d = _input_array(diag, None, "C")
        _need(d.ndim == 1 and 1 <= len(d) <= _MAX_N, "DIAGONAL_SHAPE")
        n = len(d)
        l = _input_array(lower, (n-1,), "C")
        u = _input_array(upper, (n-1,), "C")
        r = _input_array(rewards, (n, 2), "F")
        h = _input_array(witness, (n,), "C")
        x = _input_array(all_time, (n, 2), "F")
        w = _input_array(weights, None, "C")
        _need(w.ndim == 2 and w.shape[1] == n and 1 <= w.shape[0] <= _MAX_SOURCE,
              "SOURCE_SHAPE")
        ns = w.shape[0]
        ids = tuple(str(s) for s in (source_ids if source_ids is not None else range(ns)))
        _need(len(ids) == ns and len(set(ids)) == ns, "SOURCE_IDS_REQUIRED_UNIQUE")
        beta = np.empty(1, dtype=np.float64)
        cw = np.empty(ns, dtype=np.float64)
        pn, pl, pu, pe = [np.empty((ns, 2), dtype=np.float64) for _ in range(4)]
        eta = np.empty(2, dtype=np.float64)
        self._call(self._lib.cr_prepare, n, ns,
            *map(_ptr, (d, l, u, r, h, w, x, beta, cw, pn, pl, pu, pe, eta)))
        _need(bool(np.all(pl >= 0) and np.all(pl <= pu)), "ALL_TIME_INTERVAL_ORDER")
        for a in (cw, pn, pl, pu, pe, eta):
            a.setflags(write=False)
        return PreparedProblem(d,l,u,r,w,h,x,ids,float(beta[0]),cw,pn,pl,pu,pe,eta)

    def clock(
        self, problem: PreparedProblem, gamma: float, m: int,
        capture: bool = False,
    ) -> dict[str, Any]:
        gamma = _finite_float(gamma, "GAMMA")
        m = _positive_integer(m, "ORDER", _MAX_M)
        _need(gamma > 0, "POSITIVE_GAMMA_REQUIRED")
        _need(isinstance(capture, bool) and (not capture or m <= 16),
              "QUALIFICATION_CAPTURE_ORDER_LIMIT")
        p = problem
        n, ns = p.n, p.nsource
        an, al, au, ae = [np.empty((ns,2),dtype=np.float64) for _ in range(4)]
        stats = np.empty(10,dtype=np.float64)
        if capture:
            zs = np.empty((m,2,n),dtype=np.float64)
            eps = np.empty((m,2),dtype=np.float64)
            zr = np.empty((m,2,n),dtype=np.float64)
            cs = np.empty((2,n),dtype=np.float64)
            cr = np.empty((2,n),dtype=np.float64)
        else:
            zs = eps = zr = cs = cr = None
        self._call(self._lib.cr_clock, n, ns,
            *map(_ptr,(p.diag,p.lower,p.upper,p.rewards,p.witness,p.weights)),
            p.beta_lower,_ptr(p.cw_upper),m,gamma,
            *map(_ptr,(an,al,au,ae,stats,zs,eps,zr,cs,cr)))
        _need(bool(np.all(al >= 0) and np.all(al <= au)), "CLOCK_INTERVAL_ORDER")
        _need(bool(np.all(al <= p.p_upper)), "CLOCK_ALL_TIME_INTERVAL_CONFLICT")
        au = np.minimum(au,p.p_upper)
        _need(bool(np.all(al <= au)), "CLOCK_ALL_TIME_INTERSECTION_EMPTY")
        rows = []
        for s,sid in enumerate(p.source_ids):
            rows.append({
                "source_id": sid,
                "count": {"A_nominal":float(an[s,0]),"A_lower":float(al[s,0]),
                          "A_upper":float(au[s,0]),"A_radius":float(ae[s,0])},
                "kinetic": {"A_nominal":float(an[s,1]),"A_lower":float(al[s,1]),
                            "A_upper":float(au[s,1]),"A_radius":float(ae[s,1])},
            })
        result: dict[str,Any] = {
            "gamma_s_inverse":gamma,"gamma_hex":gamma.hex(),"m":m,
            "source_rows":rows,
            "arithmetic_certificate":{
                "method":"LD_bounded_dots_positive_witness_outward_scalar_recurrence",
                "witness_beta_lower":p.beta_lower,
                "cw_upper":p.cw_upper.tolist(),
                "row_residual_norm_upper_max":stats[0:2].tolist(),
                "epsilon_last_upper":stats[2:4].tolist(),
                "epsilon_sum_upper":stats[4:6].tolist(),
                "minimum_nominal_solution":stats[6:8].tolist(),
                "rounded_shift_diagonal_loss_abs_upper":float(stats[8]),
                "actual_two_rhs_solve_steps":int(stats[9]),
                "exact_target":"stored_binary64_K_plus_encoded_binary64_gamma",
                "physical_model_error_included":False,
            },
        }
        if capture:
            assert zs is not None and eps is not None and zr is not None
            assert cs is not None and cr is not None
            result["qualification"] = {
                "z_steps":zs.transpose(0,2,1).copy(),
                "h":p.witness.copy(),
                "epsilon_steps":eps.copy(),
                "epsilon_steps_hex":[[float(x).hex() for x in row] for row in eps],
                "step_radius":zr.transpose(0,2,1).copy(),
                "cumulative":cs.T.copy(),
                "cumulative_radius":cr.T.copy(),
            }
        return result

    def horizon(
        self, problem: PreparedProblem, T: float, m: int, delta: float,
        capture: bool = False,
    ) -> dict[str, Any]:
        T = _finite_float(T,"HORIZON")
        delta = _finite_float(delta,"DELTA")
        m = _positive_integer(m,"ORDER",_MAX_M)
        _need(T >= 0 and 0 < delta < 1,"HORIZON_OR_DELTA_DOMAIN")
        _need(isinstance(capture,bool) and (not capture or m <= 16),
              "QUALIFICATION_CAPTURE_ORDER_LIMIT")
        p = problem
        all_time = []
        for s,sid in enumerate(p.source_ids):
            all_time.append({
                "source_id":sid,
                "all_time_count_cm3":[float(p.p_lower[s,0]),float(p.p_upper[s,0])],
                "all_time_kinetic_eV_cm3":[float(p.p_lower[s,1]),float(p.p_upper[s,1])],
                "all_time_arithmetic_radius":[float(p.p_radius[s,0]),float(p.p_radius[s,1])],
            })
        base: dict[str,Any] = {
            "horizon_s":T,"horizon_hex":T.hex(),"m":m,"delta_requested":delta,
            "time_units":"proper_s","gamma_units":"s^-1",
            "source_time_history":None,"exposure_s":None,"physical_rate":None,
            "arithmetic_certificate":{
                "witness_beta_lower":p.beta_lower,
                "all_time_residual_norm_upper":p.all_time_residual_norm_upper.tolist(),
                "native_platform":dict(self.native_info),
                "physical_model_error_included":False,
            },
        }
        if T == 0:
            base["clocks"] = {}
            base["source_rows"] = [
                dict(row,count_cm3=[0.0,0.0],kinetic_eV_cm3=[0.0,0.0])
                for row in all_time
            ]
            base["endpoint"] = "exact_zero_RR"
            return base
        tf,df = Fraction.from_float(T),Fraction.from_float(delta)
        encoded_gamma = {
            "minus":float(Fraction(m)*(1+df)/tf),
            "plus":float(Fraction(m)*(1-df)/tf),
        }
        clocks = {}
        for side in ("minus","plus"):
            gamma = encoded_gamma[side]
            _need(math.isfinite(gamma) and gamma > 0,"ENCODED_GAMMA_RANGE")
            tail = tail_upper(gamma,T,m,side)
            clock = self.clock(p,gamma,m,capture=capture)
            clock.update(tail)
            clocks[side] = clock
        qm = Fraction.from_float(clocks["minus"]["tail_upper"])
        qp = Fraction.from_float(clocks["plus"]["tail_upper"])
        rows = []
        for s,at in enumerate(all_time):
            bounds = []
            for j,label in enumerate(("count","kinetic")):
                a_lo = Fraction.from_float(clocks["minus"]["source_rows"][s][label]["A_lower"])
                a_hi = Fraction.from_float(clocks["plus"]["source_rows"][s][label]["A_upper"])
                pu = Fraction.from_float(float(p.p_upper[s,j]))
                lo = max(Fraction(0),(a_lo-pu*qm)/(1-qm))
                hi = min(pu,a_hi/(1-qp))
                _need(lo <= hi,"DETERMINISTIC_HORIZON_INTERSECTION_EMPTY")
                bounds.append([_fraction_down(lo),_fraction_up(hi)])
            rows.append(dict(at,count_cm3=bounds[0],kinetic_eV_cm3=bounds[1]))
        base["clocks"] = clocks
        base["source_rows"] = rows
        base["endpoint"] = "finite_conditional_pulse_response"
        return base

