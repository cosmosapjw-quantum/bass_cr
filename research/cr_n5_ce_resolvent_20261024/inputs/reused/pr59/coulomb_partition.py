"""Local Maxwellian-bath reference, not the nonlinear BASS_CR production operator.

E and theta=k_B*T/epsilon_eV are in eV. D is in eV**2/s and
Var(dE)=2*D*dt. The running-log option is an explicitly declared
stationarity-preserving divergence-form extension, not an exact
Rosenbluth coefficient for arbitrary screening prescriptions.
"""
from dataclasses import dataclass
import math
import numpy as np
from scipy.special import erf, gammainc


def energy_flux(density, density_derivative, energy, temperature_energy, diffusion):
    """Positive flux points to increasing energy; no absorbing cutoff is applied."""
    if energy <= 0 or temperature_energy <= 0 or diffusion < 0:
        raise ValueError("positive energy/temperature and nonnegative diffusion required")
    return -diffusion*(density_derivative+(1/temperature_energy-1/(2*energy))*density)


@dataclass(frozen=True)
class MaxwellianCoulomb:
    energy_anchor: float
    loss_anchor: float
    temperature_energy: float
    log_anchor: float
    running_log: bool = False

    def __post_init__(self):
        if min(self.energy_anchor,self.loss_anchor,self.temperature_energy,self.log_anchor)<=0:
            raise ValueError("positive local anchor required")

    def coefficients(self, energy):
        E=np.asarray(energy,dtype=float)
        if np.any(E<=0):raise ValueError("E must be positive")
        theta=self.temperature_energy;x=E/theta
        L=self.log_anchor+1.5*np.log(E/self.energy_anchor) if self.running_log else np.full_like(E,self.log_anchor)
        if np.any(L<=0):raise ValueError("running Coulomb logarithm outside declared domain")
        b=self.loss_anchor*np.sqrt(self.energy_anchor/E)*L/self.log_anchor
        # gammainc(3/2,x) is the positive Chandrasekhar numerator A(x).
        A=gammainc(1.5,x)
        dAdx=2*np.sqrt(x)*np.exp(-x)/math.sqrt(math.pi)
        D=theta*b*A
        drift=b*(dAdx-A)
        if self.running_log:drift += D*1.5/(E*L)
        G=A/(2*x)
        nu_angular=b/(4*E)*(erf(np.sqrt(x))-G)
        return drift,D,nu_angular,b

    def maxwell_weight(self, energy):
        E=np.asarray(energy,dtype=float);th=self.temperature_energy
        if np.any(E<=0):raise ValueError("E must be positive")
        return 2*np.sqrt(E)*np.exp(-E/th)/(math.sqrt(math.pi)*th**1.5)


def reversible_generator(centres, model):
    """Reflecting finite-band reference with an exact discrete Maxwell equilibrium.

    pi_i is a declared midpoint-quadrature equilibrium mass. It is not an
    assertion that midpoint quadrature integrates the continuum Maxwellian exactly.
    Q acts on column count vectors. c_i are positive edge conductances.
    """
    E=np.asarray(centres,dtype=float)
    if E.ndim!=1 or len(E)<2 or np.any(E<=0) or np.any(np.diff(E)<=0):
        raise ValueError("at least two ordered positive cell centres required")
    d=np.diff(E)
    widths=np.r_[d[0],(d[:-1]+d[1:])/2,d[-1]]
    raw=model.maxwell_weight(E)*widths;Z=raw.sum();pi=raw/Z
    mid=(E[:-1]+E[1:])/2
    D=model.coefficients(mid)[1]
    c=D*model.maxwell_weight(mid)/(d*Z)
    Q=np.zeros((len(E),len(E)))
    for i,v in enumerate(c):
        Q[i+1,i]+=v/pi[i];Q[i,i]-=v/pi[i]
        Q[i,i+1]+=v/pi[i+1];Q[i+1,i+1]-=v/pi[i+1]
    return Q,pi,c


def bath_energy_rate(centres, count_rhs):
    """Opposite collisional kinetic moment. Do not add an old stopping-heat term."""
    return -float(np.dot(np.asarray(centres),np.asarray(count_rhs)))


def moving_interface(relative_flux, cutoff, tail_collision_flux_integral, core_work, tail_work):
    """Count and energy balances for the SAME kinetic/core interface.

    relative_flux = integral_Omega[j_C+g_E*f-qdot*f] at E=q.
    Returns core/tail count and energy rates before other reaction sources.
    """
    return dict(core_count=-relative_flux,tail_count=relative_flux,
        core_energy=-cutoff*relative_flux-tail_collision_flux_integral+core_work,
        tail_energy=cutoff*relative_flux+tail_collision_flux_integral+tail_work)
