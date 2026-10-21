"""Analytic packet-pressure derivatives for the fixed PR147 collisionless source.

This diagnostic does not integrate an ODE, alter a distribution, or replace a
production RHS. `eta` is ln(a/a_ref), `b_eta` is s/H_t. All differentiated
observables are signed; a scalar norm is not differentiable at its zero.

Source pi_s=(p_parallel-p_perp)/3. For SI pressure [J/m^3] and H_t [s^-1],
P=sqrt(6)*(8*pi*G/c^2)*pi_s/H_t^2. This equals the energy-coupling expression
with kappa_E=8*pi*G/c^4 and H_geom=H_t/c.
"""
from __future__ import annotations

import copy
import math

import numpy as np

SOURCE_COMMIT = '3b85dedce84d37b3e165da00685a8a984950aafe'
G_SI = 6.67430e-11
C_SI = 299792458.0
KAPPA_TIME_SI = 8 * math.pi * G_SI / C_SI**2


def packet_derivatives(momentum, eta: float, b: float, b_eta: float):
    """Differentiate conserved-packet mass-shell moments along b'=b_eta.

The undifferentiated moments use the original expression/reduction order.
The derivative is a mathematical derivative of those mass-shell sums; it is
not a derivative of FP rounding, and is not claimed bitwise against a finite
difference. The input packet and grid arrays are only read.
    """
    eta, b, b_eta = map(float, (eta, b, b_eta))
    if not all(map(math.isfinite, (eta, b, b_eta))) or eta < 0 or abs(b) > 1:
        raise ValueError('SOURCE_CHART_OR_NONFINITE_DERIVATIVE_INPUT')
    r = math.exp(-eta)
    u = (r * momentum._q)**2 * math.exp(2*b) * (1-momentum._mu2)
    w = (r * momentum._q)**2 * math.exp(-4*b) * momentum._mu2
    energy = np.sqrt(momentum.mass*momentum.mass + u + w)
    weighted = ((r**3) / momentum.reference_energy_norm) * momentum._numbers
    rho = float(np.sum(weighted * energy))
    pp = float(np.sum(weighted * (u/(2*energy))))
    pa = float(np.sum(weighted * (w/energy)))
    pi_s = (pa-pp)/3
    du = (-2+2*b_eta)*u
    dw = (-2-4*b_eta)*w
    de = (du+dw)/(2*energy)
    drho = float(np.sum(weighted * (-3*energy+de)))
    dpp = float(np.sum(weighted * ((-3*u+du)/(2*energy)-u*de/(2*energy**2))))
    dpa = float(np.sum(weighted * ((-3*w+dw)/energy-w*de/energy**2)))
    dpi_s = (dpa-dpp)/3
    # Direct packet sum: at b_eta=0 this equals pi_s' + 4*pi_s.
    # It remains finite at A=0; there is no division by a small stress.
    mass_release = float(np.sum(weighted *
        (-momentum.mass**2*(w-u/2)/(3*energy**3))))
    pbar = (2*pp+pa)/3
    return {
        'rho': rho, 'pressure_perp': pp, 'pressure_parallel': pa,
        'pi_s': pi_s, 'pbar': pbar,
        'rho_eta': drho, 'pressure_perp_eta': dpp,
        'pressure_parallel_eta': dpa, 'pi_s_eta': dpi_s,
        'physical_number_eta': -3*momentum.total_cell_number*r**3,
        'mass_release_pi_s_at_zero_shear': mass_release,
        'energy_conservation_residual': drho+3*(rho+pbar)+6*b_eta*pi_s,
        'zero_shear_release_identity_residual':
            dpi_s+4*pi_s-mass_release if b_eta == 0 else None,
    }


def source_derivatives(obj, eta: float, y):
    """Derivative diagnostic on one existing full source state.

Only the collisionless massive PR147 lane is admitted. A shallow private
source copy confines its RHS evaluation counter; state and distribution are
never modified. The Einstein forcing built from normalized source fields is
retained separately from the SI component sum to expose FP grouping offsets.
    """
    if obj.fm <= 0 or obj.ne_source is not None or obj.nu_visc != 0:
        raise ValueError('DIAGNOSTIC_REQUIRES_COLLISIONLESS_MASSIVE_PR147_LANE')
    eta = float(eta)
    state = np.array(y, dtype=np.float64, copy=True)
    if state.shape != (4+4*obj.n,) or not np.isfinite(state).all():
        raise ValueError('INVALID_FULL_SOURCE_STATE')
    private = copy.copy(obj)
    fields = private.fields(eta, state)
    dy = private.rhs(eta, state)
    h, s, a = map(float, (fields['H'], fields['s'], fields['a']))
    h2 = h*h
    b_eta = s/h
    shell = packet_derivatives(private.momentum, eta, float(fields['b']), b_eta)
    n = obj.n
    eg, en = fields['E_gamma'], fields['E_nu']
    deg, den = dy[4:4+n], dy[4+2*n:4+3*n]
    rad_energy_eta = (obj.omega_gamma*(deg[0]-4*eg[0]) +
                      obj.omega_nu*(den[0]-4*en[0]))/a**4
    s_eta = float(dy[2])*obj.source.href
    h2_eta = obj.source.h0**2 * (
        -3*fields['dust_energy_norm'] + obj._mass_pref*shell['rho_eta'] +
        rad_energy_eta) + 2*s*s_eta
    hlog = float(h2_eta/(2*h2))
    pi_norm = {
        'm': float(fields['Pi_matter_norm']),
        'r': float(fields['Pi_radiation_norm']),
    }
    dpi_norm = {
        'm': obj._mass_pref*shell['pi_s_eta'],
        'r': (obj.omega_gamma*(deg[2]-4*eg[2]) +
              obj.omega_nu*(den[2]-4*en[2]))/(3*a**4),
    }
    pi = {sector: float(fields[key]) for sector, key in (
        ('m','Pi_matter_J_m3'), ('gamma','Pi_gamma_J_m3'), ('nu','Pi_nu_J_m3'))}
    dpi = {
        'm': obj.source.rhocrit_j_m3*dpi_norm['m'],
        'gamma': obj.source.rhocrit_j_m3*obj.omega_gamma/a**4*(deg[2]-4*eg[2])/3,
        'nu': obj.source.rhocrit_j_m3*obj.omega_nu/a**4*(den[2]-4*en[2])/3,
    }
    pi['r'] = pi['gamma']+pi['nu']
    pi['tot'] = pi['m']+pi['r']
    dpi['r'] = dpi['gamma']+dpi['nu']
    dpi['tot'] = dpi['m']+dpi['r']
    factor = math.sqrt(6)*KAPPA_TIME_SI/h2
    signed = {key: factor*value for key, value in pi.items()}
    signed_eta = {key: factor*(dpi[key]-2*hlog*pi[key]) for key in pi}
    signed_s = math.sqrt(6)*s/h
    signed_s_eta = math.sqrt(6)/h*(s_eta-s*hlog)
    forcing_factor = math.sqrt(6)*3*obj.source.h0**2/h2
    forcing = forcing_factor*(pi_norm['m']+pi_norm['r'])
    forcing_eta = forcing_factor*(dpi_norm['m']+dpi_norm['r']-
                                 2*hlog*(pi_norm['m']+pi_norm['r']))
    release = factor*obj.source.rhocrit_j_m3*obj._mass_pref * \
        shell['mass_release_pi_s_at_zero_shear']
    # hlog' cancels from S'' exactly at s=0. No threshold substitutes s=0.
    s_eta2_at_zero = forcing_eta-(3+hlog)*signed_s_eta if s == 0 else None
    return {
        'eta': eta, 'b': float(fields['b']), 'H_t_s_inv': h,
        'H_log_eta': hlog, 'b_eta': b_eta,
        'source_rhs': dy,
        'packet': shell,
        'pi_s_J_m3': pi, 'pi_s_eta_J_m3': dpi,
        'signed_P': signed, 'signed_P_eta': signed_eta,
        'signed_S': signed_s, 'signed_S_eta': signed_s_eta,
        'source_forcing_P': forcing, 'source_forcing_P_eta': forcing_eta,
        'source_forcing_minus_SI_component_sum': forcing-signed['tot'],
        'signed_S_identity_residual':
            signed_s_eta-(signed['tot']-(3+hlog)*signed_s),
        'signed_S_eta2_if_exact_zero_s': s_eta2_at_zero,
        'mass_release_P_at_zero_shear': release,
        'radiation_energy_conservation_residual':
            float(rad_energy_eta+4*fields['rad_energy_norm']+
                  6*b_eta*fields['Pi_radiation_norm']),
    }


def initial_cancellation_jet(obj, y0):
    """Return actual and ideal jets only for the admitted s0=b0=0 slice.

The ideal coefficient retains the massive distribution but imposes exact
total-stress cancellation analytically. The actual tiny component offsets
are reported independently and remain in the actual source derivatives.
No eta^3 coefficient, error bound or finite-window accuracy is claimed.
    """
    d = source_derivatives(obj, 0., y0)
    if float(y0[1]) != 0 or float(y0[2]) != 0:
        raise ValueError('INITIAL_JET_REQUIRES_EXACT_B0_S0_ZERO')
    eps = d['signed_P']['tot']
    hlog = d['H_log_eta']
    release = d['mass_release_P_at_zero_shear']
    predicted_p1 = release-(4+2*hlog)*eps
    predicted_s2 = release-(7+3*hlog)*eps
    return {
        'actual_Pm0': d['signed_P']['m'], 'actual_Pr0': d['signed_P']['r'],
        'actual_Ptot0': eps,
        'actual_S0': d['signed_S'],
        'actual_Sprime0': d['signed_S_eta'],
        'actual_Ptot_prime0': d['signed_P_eta']['tot'],
        'actual_Ssecond0': d['signed_S_eta2_if_exact_zero_s'],
        'actual_S_eta2_coefficient': .5*d['signed_S_eta2_if_exact_zero_s'],
        'H_log_eta0': hlog,
        'mass_shell_release_direct': release,
        'ideal_exact_cancellation_Ptot_prime0': release,
        'ideal_exact_cancellation_Ssecond0': release,
        'ideal_exact_cancellation_S_eta2_coefficient': .5*release,
        'actual_offset_Pprime_formula_residual': d['signed_P_eta']['tot']-predicted_p1,
        'actual_offset_Ssecond_formula_residual':
            d['signed_S_eta2_if_exact_zero_s']-predicted_s2,
        'actual_Sprime_minus_Ptot0': d['signed_S_eta']-eps,
        'source_forcing_minus_SI_component_sum':
            d['source_forcing_minus_SI_component_sum'],
        'actual_offsets_preserved': True,
        'ideal_constraint_is_distinct_from_actual_FP_state': True,
        'third_order_coefficient': None,
        'finite_window_remainder_bound': None,
        'new_ODE_integrations': 0,
        'global_error_bound': None,
    }
