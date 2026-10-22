"""Primary-electron ENERGY-DOMAIN accounting, not a beta generator or deposition solver.

Only newly specified conditional moment bounds and F=1 phase-space diagnostics live
here.  No historical reaction, beta lifetime, thermal, or stress solver is imported.
"""
from dataclasses import dataclass
from fractions import Fraction
import math


@dataclass(frozen=True)
class ElectronDomain:
    lower_eV: float
    upper_eV: float

    def __post_init__(self):
        if not (math.isfinite(self.lower_eV) and math.isfinite(self.upper_eV)
                and 0 < self.lower_eV < self.upper_eV):
            raise ValueError('Finite positive ascending electron kinetic-energy domain required')

    def require_source(self, *, carrier, energy_kind, units):
        if carrier != 'electron':
            raise ValueError('FS electron-domain operator rejects non-electron kinetic sources')
        if energy_kind != 'kinetic' or units != 'eV':
            raise ValueError('Explicit electron kinetic energy in eV required; no implicit conversion')
        return True

    def classify(self, energy_eV, *, carrier, energy_kind, units):
        self.require_source(carrier=carrier, energy_kind=energy_kind, units=units)
        if energy_eV is None or not math.isfinite(energy_eV) or energy_eV < 0:
            raise ValueError('Missing or nonphysical energy cannot be replaced by zero')
        if energy_eV < self.lower_eV:
            return 'LOW_TAIL_UNRESOLVED'
        if energy_eV > self.upper_eV:
            return 'HIGH_TAIL_UNRESOLVED'
        return 'IN_ENERGY_DOMAIN_ONLY'


def fraction_text(x):
    return f'{x.numerator}/{x.denominator}'


def moment_bounds(mean, support_ceiling, lower, upper):
    """Sharp conditional bounds over probability measures on [0,Q].

    Inputs must be exact decimal strings or Fraction; missing values fail.
    Bounds are about electron kinetic energy, not total nuclear Q deposition.
    """
    m, Q, L, U = map(Fraction, (mean, support_ceiling, lower, upper))
    if not (0 < L < U < Q and 0 < m < Q):
        raise ValueError('This scoped bound requires 0<L<U<Q and 0<m<Q')
    pmax = min(Fraction(1), m / L, (Q - m) / (Q - U))
    emax = min(Fraction(1), U * (Q - m) / (m * (Q - U)))
    # Exact witnesses establish that the universal lower bound is zero and that
    # equal number/mean/endpoint do not determine the supported-domain fraction.
    t = min(m / 2, (L + U) / 2)
    if not L < t < U:
        raise ValueError('Counterexample center is scoped to the selected n/T inputs')
    q_weight = (m - t) / (Q - t)
    witnesses = [
        [(Fraction(0), 1 - m / Q), (Q, m / Q)],
        [(t, 1 - q_weight), (Q, q_weight)],
    ]
    encoded = []
    for support in witnesses:
        assert sum(w for _, w in support) == 1
        assert sum(x * w for x, w in support) == m
        assert support[-1][0] == Q and support[-1][1] > 0
        pd = sum(w for x, w in support if L <= x <= U)
        ed = sum(x * w for x, w in support if L <= x <= U)
        encoded.append({'support_eV_exact': [fraction_text(x) for x, _ in support],
                        'probability_exact': [fraction_text(w) for _, w in support],
                        'mean_eV_exact': fraction_text(m),
                        'domain_particle_fraction': float(pd),
                        'domain_energy_fraction': float(ed / m),
                        'moments_verified_exact': True})
    return {'assumptions': 'positive probability measure; support subset [0,Q]; fixed central mean m',
            'particle_lower': 0.0, 'particle_upper': float(pmax),
            'particle_upper_exact': fraction_text(pmax),
            'kinetic_energy_fraction_lower': 0.0,
            'kinetic_energy_fraction_upper': float(emax),
            'kinetic_energy_fraction_upper_exact': fraction_text(emax),
            'outside_kinetic_energy_fraction_lower': float(1 - emax),
            'outside_kinetic_energy_fraction_upper': 1.0,
            'evaluated_spectrum_determined': False,
            'conditional_central_values_only': True,
            'same_mean_and_endpoint_counterexamples': encoded}


def scipy_dimensionless_moment(k, lo, hi, Q, M):
    """I_k / Q**(k+5), after T/Q=u^2. Units cancel before quadrature."""
    from scipy.integrate import quad
    if k not in (0, 1, 2) or not 0 <= lo < hi <= Q or not 0 < M:
        raise ValueError('Moment or support outside the scoped diagnostic')
    r = M / Q
    def integrand(u):
        return 2 * u**(2*k+2) * math.sqrt(u*u + 2*r) * (u*u+r) * (1-u*u)**2
    return quad(integrand, math.sqrt(lo/Q), math.sqrt(hi/Q),
                epsabs=1e-13, epsrel=2e-13, limit=100)


def mp_dimensionless_moment(k, lo, hi, Q, M):
    """Independent direct x=T/Q quadrature; no square-root substitution."""
    import mpmath as mp
    q, mass = mp.mpf(str(Q)), mp.mpf(str(M))
    r = mass / q
    a, b = mp.mpf(str(lo)) / q, mp.mpf(str(hi)) / q
    return mp.quad(lambda x: x**k * mp.sqrt(x*(x+2*r)) * (x+r) * (1-x)**2,
                   [a, (a+b)/2, b])


def analytic_dimensionless_moment(k, lo, hi, Q, M):
    """Closed primitive recurrence for x=T+M, independently of quadrature."""
    import mpmath as mp
    q, mass = mp.mpf(str(Q)), mp.mpf(str(M))
    A = q + mass
    coeffs = {}
    for j in range(k + 1):
        base = math.comb(k, j) * (-mass)**(k-j)
        for power, coeff in ((1, A*A), (2, -2*A), (3, mp.mpf(1))):
            coeffs[j+power] = coeffs.get(j+power, mp.mpf(0)) + base*coeff
    def primitive(T):
        if T == 0:
            return mp.mpf(0)
        x = T + mass
        root = mp.sqrt(x*x - mass*mass)
        J = [(x*root - mass*mass*mp.acosh(x/mass))/2, root**3/3]
        for n in range(2, max(coeffs)+1):
            J.append((x**(n-1)*root**3 + (n-1)*mass*mass*J[n-2])/(n+2))
        return mp.fsum(coeff * J[power] for power, coeff in coeffs.items())
    return (primitive(mp.mpf(str(hi))) - primitive(mp.mpf(str(lo)))) / q**(k+5)


def diagnostic_segments(Q, M, domain):
    """F=1 illustrative beta electron segments. No evaluation mean is fitted."""
    if not domain.upper_eV < Q:
        raise ValueError('This scoped diagnostic expects the endpoint above the FS domain')
    intervals = [('low_tail', 0.0, domain.lower_eV),
                 ('in_domain', domain.lower_eV, domain.upper_eV),
                 ('high_tail', domain.upper_eV, Q)]
    totals = [scipy_dimensionless_moment(k, 0.0, Q, Q, M) for k in range(3)]
    rows = []
    for label, lo, hi in intervals:
        moments = [scipy_dimensionless_moment(k, lo, hi, Q, M) for k in range(3)]
        rows.append({'interval': label, 'lower_eV': lo, 'upper_eV': hi,
                     'particle_fraction': moments[0][0]/totals[0][0],
                     'kinetic_energy_per_primary_eV': Q*moments[1][0]/totals[0][0],
                     'kinetic_energy_fraction': moments[1][0]/totals[1][0],
                     'kinetic_energy_second_moment_per_primary_eV2': Q*Q*moments[2][0]/totals[0][0],
                     'dimensionless_moments': [x[0] for x in moments],
                     'scipy_local_error_estimates': [x[1] for x in moments],
                     'deposition_heat_eV': None, 'deposition_ionization_eV': None,
                     'deposition_status': ('ENERGY_DOMAIN_ONLY_OTHER_FS_GATES_OPEN' if label == 'in_domain'
                                           else 'UNRESOLVED_TAIL_NO_AUTOMATIC_HEAT_OR_ZERO_FILL')})
    return {'model': 'ILLUSTRATIVE_ALLOWED_FERMI_ONE_NOT_EVALUATED_BETA_SPECTRUM',
            'mean_kinetic_eV': Q*totals[1][0]/totals[0][0],
            'second_moment_eV2': Q*Q*totals[2][0]/totals[0][0],
            'toy_antineutrino_complement_eV': Q - Q*totals[1][0]/totals[0][0],
            'neutrino_note': 'Only the recoil-free massless-neutrino toy complement; no physical channel ownership inferred',
            'total_dimensionless_moments': [x[0] for x in totals],
            'segments': rows}
