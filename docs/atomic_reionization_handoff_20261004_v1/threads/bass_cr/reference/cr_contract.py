"""Portable bookkeeping reference, not a physical cross-section provider.

Frames: local gas tetrad, nonrelativistic laboratory projectile kinetic energy.
number_rate uses N(E,Omega) [cm^-3 erg^-1 sr^-1], dE dOmega [erg sr],
v [cm/s], sigma [cm^2], n_target [cm^-3]; output [cm^-3 s^-1].
No interpolation, atomic kernel, cosmological transport or native execution.
"""
from fractions import Fraction
import math

SPECIES=('p_fast','H_gas','H_fast','p_gas','e_free')
CHANNELS={
    'resonant_cx_1s':(-1,-1,1,1,0),
    'target_ionization':(0,-1,0,1,1),
    'fast_neutral_stripping':(1,0,-1,0,1),
    'target_excitation':(0,0,0,0,0),
    'elastic':(0,0,0,0,0),
}

def _nonnegative(value):
    if isinstance(value,bool) or not isinstance(value,(int,float,Fraction)):
        raise ValueError('real scalar required')
    if (isinstance(value,float) and not math.isfinite(value)) or value<0:
        raise ValueError('finite nonnegative scalar required')
    return value

def conservation(channel):
    if channel not in CHANNELS:raise ValueError('unsupported process identity')
    d=CHANNELS[channel]
    return sum(d[:4]),d[0]+d[3]-d[4]

def event_delta(channel,events):
    if channel not in CHANNELS:raise ValueError('unsupported process identity')
    q=_nonnegative(events)
    return dict(zip(SPECIES,(q*x for x in CHANNELS[channel])))

def ecm_from_lab(kinetic_energy,projectile_mass,target_mass):
    E,mp,mt=map(_nonnegative,(kinetic_energy,projectile_mass,target_mass))
    if mp==0 or mt==0:raise ValueError('positive masses required')
    return E*mt/(mp+mt)

def number_rate(n_target,N,v,sigma,weights):
    """Fixed supplied quadrature only; caller owns support/tail/error proof."""
    n=_nonnegative(n_target)
    arrays=tuple(tuple(a) for a in (N,v,sigma,weights))
    if len({len(a) for a in arrays})!=1:raise ValueError('quadrature lengths differ')
    result=0
    for row in zip(*arrays):
        a,b,c,d=map(_nonnegative,row);result+=a*b*c*d
    return n*result

def cr_sources(enabled,event_rate_provider):
    if type(enabled) is not bool:raise ValueError('enabled must be boolean')
    result=dict.fromkeys(SPECIES,0)
    if not enabled:return result
    for channel,rate in event_rate_provider().items():
        for species,delta in event_delta(channel,rate).items():result[species]+=delta
    return result

def close_energy(projectile_loss,*,heat=0,ion_potential=0,excitation=0,radiation=0,nonthermal=0,escape=0):
    """Exact/fixed arithmetic diagnostic; components must be disjoint.

    Nonthermal includes net target/recoil kinetic storage outside heat. Photons
    still stored as excitation cannot simultaneously appear in radiation.
    Float roundoff is not a certified enclosure; caller must assess its budget.
    """
    loss=_nonnegative(projectile_loss)
    parts=tuple(map(_nonnegative,(heat,ion_potential,excitation,radiation,nonthermal,escape)))
    residual=loss-sum(parts)
    if residual<0:raise ValueError('overallocated energy; double count or invalid partition')
    return residual
