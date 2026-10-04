"""Read bit-exact observations and inherit a source-pinned exact-real box proof.

This is a diagnostic, not a runtime acceptance or continuous-error certificate.
"""
import dataclasses
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import struct


def decode(v):
    if isinstance(v, dict):
        if set(v) == {'numerator', 'denominator'}:
            return Q(int(v['numerator']), int(v['denominator']))
        return {k: decode(z) for k, z in v.items()}
    if isinstance(v, list):
        return tuple(decode(z) for z in v)
    return v


def encode(v):
    if isinstance(v, Q):
        return {'numerator': str(v.numerator), 'denominator': str(v.denominator)}
    if dataclasses.is_dataclass(v):
        return encode(dataclasses.asdict(v))
    if isinstance(v, dict):
        return {k: encode(z) for k, z in v.items()}
    if isinstance(v, (tuple, list)):
        return [encode(z) for z in v]
    return v


def read_observation(text):
    result = {}
    for line in text.splitlines():
        parts = line.split(',')
        if len(parts) == 2:
            name, n = parts
            if name in result:
                raise ValueError('duplicate scalar')
            result[name] = int(n)
            continue
        name, index, bits, decimal = parts
        value = struct.unpack('>d', bytes.fromhex(bits))[0]
        if not math.isfinite(value):
            raise ValueError('nonfinite observation')
        if struct.pack('>d', float(decimal)).hex() != bits:
            raise ValueError('decimal does not round-trip to observed bits')
        group = result.setdefault(name, [])
        if int(index) != len(group):
            raise ValueError('duplicate or noncontiguous observation')
        group.append(Q.from_float(value))
    return result


def load_reference(path):
    code = path / 'research/f04a.py'
    if hashlib.sha256(code.read_bytes()).hexdigest() != '6c184407638766e2c814de1ecb339adcf05e594537e24617036e19fd327dfbb5':
        raise ValueError('reference source identity mismatch')
    spec = importlib.util.spec_from_file_location('pinned_f04a', code)
    module = importlib.util.module_from_spec(spec)
    import sys
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def analyze(observation, reference):
    f = load_reference(reference)
    o = read_observation(observation)
    inp = decode(json.loads((reference / 'results/INPUTS.json').read_text()))
    cert = decode(json.loads((reference / 'results/point_dt_1e8.json').read_text()))
    nh, nhe, c, kb, ev = o['MODEL']
    m = f.Model(nh, nhe, c, ev, tuple(o['CHI']), tuple(o['ENERGY']),
                tuple(tuple(o[f'SIGMA{a}']) for a in range(3)),
                tuple(o['ALPHA']), tuple(o['BETA']))
    old = f.Old(tuple(o['OLD'][:3]), o['OLD'][3], tuple(o['OLD'][4:7]), o['OLD'][7])
    dt = o['DT'][0]
    if dataclasses.asdict(m) != inp['model']:
        raise ValueError('model differs from inherited proof')
    for name in ('x', 'photons', 'escaped'):
        if getattr(old, name) != inp['old'][name]:
            raise ValueError('fraction/photon/escape input differs from proof')
    if not cert['root_certified'] or cert['dt']['lo'] != dt or cert['dt']['hi'] != dt:
        raise ValueError('point root certificate/dt mismatch')
    x = tuple(o['ENDPOINT'][:3])
    if any(abs(x[i]-cert['center'][i]) > cert['radius'] for i in range(3)):
        raise ValueError('endpoint outside inherited certified cube')
    if o['CONTROL'][0] != Q.from_float(1e-14) or o['MAX_ITERATIONS'] != 80:
        raise ValueError('native control changed')
    # Fractions/root/Jacobian do not depend on old.u in this pinned model.
    # Inherit q,A,E; re-evaluate the thermal box with ACTUAL stored old.u.
    boxes = tuple(f.Interval(z-cert['radius'], z+cert['radius']) for z in cert['center'])
    thermal = f.reconstruct(m, old, boxes, f.Interval(dt))
    if thermal['thermal_numerator'].lo <= 0:
        raise ValueError('native-input thermal box not strictly positive')
    g = f.residual(m, old, x, dt)
    a = cert['preconditioner']
    v = tuple(abs(sum(a[i][k]*g[k] for k in range(3))) for i in range(3))
    q = cert['q']
    if not 0 <= q < 1:
        raise ValueError('noncontracting inherited certificate')
    distance = max(v)/(1-q)
    e = tuple(tuple(max(abs(z['lo']), abs(z['hi'])) for z in row)
              for row in cert['preconditioned_defect'])
    if q != max(sum(row) for row in e):
        raise ValueError('inherited component bound inconsistent')
    component = tuple(v[i]+sum(e[i])*distance for i in range(3))
    reduced = f.reconstruct(m, old, x, dt)
    native_n = tuple(o['ENDPOINT'][4:7])
    lower = (1-x[0], 1-x[1]-x[2], x[1])
    ne = nh*x[0]+nhe*(x[1]+2*x[2]); particles = nh+nhe+ne
    gamma = tuple(sum(c*m.sigma[a][g]*native_n[g] for g in range(3)) for a in range(3))
    j = tuple(lower[a]*(gamma[a]+ne*m.beta[a])-x[a]*ne*m.alpha[a] for a in range(3))
    fx = (j[0], j[1]-j[2], j[2])
    photo = tuple(tuple((nh,nhe,nhe)[a]*lower[a]*c*m.sigma[a][g]*native_n[g]
                        for g in range(3)) for a in range(3))
    collision = reduced['collision']; recomb = reduced['recomb']
    u = o['ENDPOINT'][3]
    heat = sum(photo[a][g]*(m.energy[g]-m.chi[a])*ev for a in range(3) for g in range(3))
    cool = sum(collision[a]*m.chi[a]*ev for a in range(3))
    du = heat-cool-u*sum(recomb)/particles
    dn = tuple(-sum(photo[a][g] for a in range(3)) for g in range(3))
    direct = tuple(x[i]-old.x[i]-dt*fx[i] for i in range(3))+(u-old.u-dt*du,)+tuple(
        native_n[g]-old.photons[g]-dt*dn[g] for g in range(3))
    scales = (Q(1),)*3+(max(old.u,Q.from_float(1e-30)),)+tuple(
        max(z,Q.from_float(1e-30)) for z in old.photons)
    normalized = tuple(direct[i]/scales[i] for i in range(7))
    # Exact projection checks: native photons versus eliminated photons, not zeros.
    jr = f.reduced_parts(m,old,x,dt)[-1]
    fr = (jr[0],jr[1]-jr[2],jr[2])
    projection = tuple(g[i]-direct[i]-dt*(fx[i]-fr[i]) for i in range(3))
    if any(projection):
        raise ArithmeticError('exact residual projection identity failed')
    observed_rhs = tuple(o['RHS'])
    exact_rhs = fx+(du,)+dn
    float_rhs_residual = tuple(o['ENDPOINT'][i]-o['OLD'][i]-dt*observed_rhs[i] for i in range(7))
    escape_rhs = sum(recomb[a]*(ev*m.chi[a]+u/particles) for a in range(3))
    escape_residual = o['ENDPOINT'][7]-old.escaped-dt*escape_rhs
    return dict(status='NATIVE_BITS_BOUND_TO_RESTRICTED_EXACT_REAL_ROOT', model=m, old=old,
        endpoint=tuple(o['ENDPOINT']),dt=dt,old_u_difference_from_reference=old.u-inp['old']['u'],
        endpoint_in_inherited_cube=True,inherited_q=q,preconditioned_residual=v,
        reduced_fraction_residual=g,root_distance_inf=distance,component_root_distance=component,
        photon_elimination_defect=tuple(native_n[g]-reduced['photons'][g] for g in range(3)),
        thermal_elimination_defect=u-reduced['u'],direct_seven_residual=direct,
        normalized_direct_seven_residual=normalized,exact_escape_residual=escape_residual,
        native_reported_residual_norm=o['DIAGNOSTIC'][0],observed_float_rhs_residual=float_rhs_residual,
        rhs_arithmetic_difference=tuple(observed_rhs[i]-exact_rhs[i] for i in range(7)),
        projection_identity=projection,thermal_numerator_lower=thermal['thermal_numerator'].lo,
        thermal_denominator_lower=thermal['thermal_denominator'].lo,
        strictly_positive_native_input_thermal_box=True,
        maximum_iterations=o['MAX_ITERATIONS'],iterations=o['ITERATIONS'],
        native_control_tolerance=o['CONTROL'][0],
        native_implicit_calls=1,adaptive_acceptance_calls=0,parameter_box_expansion=False,
        continuous_flow_verified=False,full_half_acceptance_verified=False,global_F04_closed=False)
