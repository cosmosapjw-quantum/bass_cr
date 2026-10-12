"""Conservative thermal receiver formulas for the BASS_CR theory loop.

Equation references are to derivations/THERMAL_EXCESS_KO.md (T.6, T.11,
T.17, T.18).  Rates use proper time and proper-volume densities.  Packet
quantities use one common comoving cell.  There is no transport evolution,
source normalization, time quadrature, or production integration here.

Python integers, floats, and fractions.Fraction are accepted.  Rational
inputs with a rational k_B retain exact Fraction arithmetic.  The default
Boltzmann constant is the exact SI value, expressed as a Fraction; no input
is coerced to float.  A different k_B may be supplied for consistent units
or independent algebraic checks.
"""

from dataclasses import dataclass
from fractions import Fraction
from numbers import Real


K_B_SI = Fraction(1380649, 10**29)  # Exactly 1.380649e-23 J K^-1.

__all__ = [
    "K_B_SI",
    "ThermalPacket",
    "thermal_transfer_tdot",
    "total_moment_tdot",
    "advance_thermal_packet",
    "temperature_error_bound",
]


def _finite(name: str, value: Real) -> None:
    """Validate a finite real without converting exact rationals to float."""
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{name} must be a real scalar")
    # For the supported real scalars this rejects both infinities and NaN.
    if value - value != 0:
        raise ValueError(f"{name} must be finite")


def _positive(name: str, value: Real) -> None:
    _finite(name, value)
    if value <= 0:
        raise ValueError(f"{name} must be strictly positive")


def _nonnegative(name: str, value: Real) -> None:
    _finite(name, value)
    if value < 0:
        raise ValueError(f"{name} must be nonnegative")


def _specific_heat(k_B: Real) -> Real:
    _positive("k_B", k_B)
    return Fraction(3, 2) * k_B


def thermal_transfer_tdot(
    n_thermal: Real,
    temperature: Real,
    thermal_energy_rate: Real,
    thermal_number_rate: Real,
    expansion_rate: Real = 0,
    *,
    k_B: Real = K_B_SI,
) -> Real:
    """Return the thermal temperature derivative, equation (T.6).

    n_thermal is the positive number density of all thermal particles
    (nuclei plus thermal electrons), in m^-3.  temperature is in K.
    thermal_energy_rate = Q_d + P_h + J_E is in J m^-3 s^-1;
    thermal_number_rate = S_d + J_N is in m^-3 s^-1.  Both are signed.
    expansion_rate = theta = d(log V)/dt is in s^-1 and may be signed.
    k_B has units J K^-1.  The returned value has units K s^-1.

    The energy rate includes transfers and direct sources once.  In the
    previous stored cutoff totals, source-projection ghost contributions
    are already included.  Expansion pressure work is applied here as
    theta * k_B * n_thermal * temperature.
    """
    _positive("n_thermal", n_thermal)
    _nonnegative("temperature", temperature)
    for name, value in (
        ("thermal_energy_rate", thermal_energy_rate),
        ("thermal_number_rate", thermal_number_rate),
        ("expansion_rate", expansion_rate),
    ):
        _finite(name, value)
    cv = _specific_heat(k_B)
    reference_energy = cv * temperature
    pressure_work = expansion_rate * k_B * n_thermal * temperature
    result = (
        thermal_energy_rate
        - reference_energy * thermal_number_rate
        - pressure_work
    ) / (cv * n_thermal)
    _finite("temperature derivative", result)
    return result


def total_moment_tdot(
    n_all: Real,
    n_active: Real,
    temperature: Real,
    total_number_rate: Real,
    total_kinetic_energy_rate: Real,
    active_number_balance: Real,
    active_energy_balance: Real,
    active_pressure_work: Real,
    expansion_rate: Real = 0,
    *,
    k_B: Real = K_B_SI,
) -> Real:
    """Return the equivalent temperature derivative from total moments.

    This is the elimination of the coupled all-free energy-excess
    derivative in equations (T.9)-(T.11).  n_all = n_thermal + n_active
    includes thermal nuclei and every free electron, in m^-3.  n_active
    is nonnegative and n_all - n_active must be strictly positive.

    total_number_rate = S_all is in m^-3 s^-1.
    total_kinetic_energy_rate = Q_kin is in J m^-3 s^-1.
    active_number_balance = D n_active = dot(n_active)+theta*n_active.
    active_energy_balance = D u_active = dot(u_active)+theta*u_active.
    active_pressure_work = K:Pi_active is in J m^-3 s^-1, including its
    anisotropic stress contribution.  Thus the thermal rates are
    S_all - D n_active and Q_kin - D u_active - K:Pi_active.

    All rates and the expansion rate are signed.  This route is useful
    for conservation comparisons; thermal_transfer_tdot uses the direct
    transfer rates when subtraction of large moments loses precision.
    """
    _positive("n_all", n_all)
    _nonnegative("n_active", n_active)
    n_thermal = n_all - n_active
    _positive("n_all - n_active", n_thermal)
    for name, value in (
        ("total_number_rate", total_number_rate),
        ("total_kinetic_energy_rate", total_kinetic_energy_rate),
        ("active_number_balance", active_number_balance),
        ("active_energy_balance", active_energy_balance),
        ("active_pressure_work", active_pressure_work),
    ):
        _finite(name, value)
    return thermal_transfer_tdot(
        n_thermal,
        temperature,
        total_kinetic_energy_rate
        - active_energy_balance
        - active_pressure_work,
        total_number_rate - active_number_balance,
        expansion_rate,
        k_B=k_B,
    )


@dataclass(frozen=True)
class ThermalPacket:
    """Thermal state of one comoving cell: count, energy in J, temperature K."""

    count: Real
    energy: Real
    temperature: Real


def advance_thermal_packet(
    count: Real,
    energy: Real,
    delta_count: Real,
    delta_energy: Real,
    *,
    k_B: Real = K_B_SI,
) -> ThermalPacket:
    """Add an integrated comoving packet and invert the ideal-gas EOS.

    count = V*n_thermal is a positive particle number and energy =
    V*u_thermal is nonnegative energy in J.  delta_count is the integrated
    number source.  delta_energy must be the integrated thermal energy
    change, including expansion pressure work and every chosen source:

        delta_energy = integral V*(Q_thermal - theta*p_thermal) dt.

    The two increments may be signed.  Both the initial and final energy
    must be nonnegative, and both particle counts must be positive.
    The returned temperature is U_new/[(3*k_B/2)*N_new], in K.  This is
    exact EOS algebra for the supplied integrals, as in (T.14), (T.17).
    """
    _positive("count", count)
    _nonnegative("energy", energy)
    _finite("delta_count", delta_count)
    _finite("delta_energy", delta_energy)
    cv = _specific_heat(k_B)
    new_count = count + delta_count
    new_energy = energy + delta_energy
    _positive("final count", new_count)
    _nonnegative("final energy", new_energy)
    temperature = new_energy / (cv * new_count)
    _nonnegative("final temperature", temperature)
    return ThermalPacket(new_count, new_energy, temperature)


def temperature_error_bound(
    energy_error: Real,
    count_error: Real,
    minimum_count: Real,
    reference_temperature: Real,
    *,
    k_B: Real = K_B_SI,
) -> Real:
    """Map thermal energy/count certificates to the (T.18) temperature bound.

    The caller supplies energy_error >= |U-U_hat| in J and count_error >=
    |N-N_hat| in particle number at the same endpoint.  Both states obey
    U,U_hat >= 0 and N,N_hat >= minimum_count > 0.
    reference_temperature = U_hat/[(3*k_B/2)*N_hat] is in K; a certified
    nonnegative upper bound on that temperature may also be supplied.

    Return energy_error/(cv*minimum_count) +
    reference_temperature*count_error/minimum_count, in K.  The energy
    certificate covers thermal energy at the endpoint, including the
    effects of work, cooling and other sources used by the integrator.
    """
    _nonnegative("energy_error", energy_error)
    _nonnegative("count_error", count_error)
    _positive("minimum_count", minimum_count)
    _nonnegative("reference_temperature", reference_temperature)
    cv = _specific_heat(k_B)
    # The combined fraction preserves rational arithmetic for integer inputs.
    result = (
        energy_error + cv * reference_temperature * count_error
    ) / (cv * minimum_count)
    _nonnegative("temperature error bound", result)
    return result
