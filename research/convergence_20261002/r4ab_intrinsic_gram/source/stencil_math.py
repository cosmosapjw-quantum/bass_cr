"""Contact-safe minus32 geometry and S-only numerical constructions.

No D argument, native operator call, interpolation fit to D, or claim of a
physical C9 remainder is provided here. Exact arithmetic is used only for
geometry diagnostics and interpolation coefficient generation.
"""
from fractions import Fraction as F
from decimal import Decimal, localcontext
import math
import numpy as np

CENTER = -32.0
H_LADDER = tuple(2.0**(-k) for k in range(6,11))
Z_VALUES = tuple(sorted({CENTER}|{CENTER+s*h for h in H_LADDER for s in (-1,1)}))
RULES = ((40,24),(48,24),(48,12))
WEIGHTS = (F(-1,2835),F(4,135),F(-64,135),F(4096,2835))
ATOL = 1e-12
CAP = 34


def group_plans():
    order = [CENTER,CENTER-H_LADDER[0],CENTER+H_LADDER[0]]
    order += [CENTER+s*h for h in H_LADDER[1:] for s in (-1,1)]
    groups=[]
    for i,z in enumerate(order):
        tasks=[dict(z_a0=z,order=q,subdivisions=1,moment_backend='fortran',
                    radial_backend='fortran',inner_phase_budget=beta) for q,beta in RULES]
        if i==1:
            tasks.append(dict(z_a0=z,order=40,subdivisions=1,moment_backend='reference',
                              radial_backend='python',inner_phase_budget=24))
        groups.append(dict(batch=f'g{i:03}',tasks=tasks))
    assert len(groups)==11 and sum(len(x['tasks']) for x in groups)==CAP
    return groups


def geometry_certificate(edges, speed):
    values=np.asarray(edges,dtype=np.float64)
    if values.ndim!=1 or len(values)<2 or not np.isfinite(values).all() or np.any(np.diff(values)<=0):
        raise ValueError('finite increasing FP64 edges required')
    ee=[F(float(x)) for x in values]
    contacts=sorted({abs(a-b) for a in ee for b in ee}|{a+b for a in ee for b in ee})
    r2=F(1028)
    below=max(x for x in contacts if x*x<r2)
    above=min(x for x in contacts if x*x>r2)
    if any(x*x==r2 for x in contacts):raise ValueError('center lies on an exact shell contact')
    samples=[]
    for z in Z_VALUES:
        t=float(z/speed); actual=float(speed*t)
        # Squared comparisons avoid treating a rounded square root as a proof.
        nominal_r2=F(4)+F(z)**2; actual_r2=F(4)+F(actual)**2
        samples.append(dict(z_a0=z,z_hex=z.hex(),time_ta=t,time_hex=t.hex(),
                            actual_z_a0=actual,actual_z_hex=actual.hex(),
                            nominal_radius_squared_exact=str(nominal_r2),
                            actual_radius_squared_exact=str(actual_r2),
                            same_contact_cell=bool(below*below<nominal_r2<above*above and
                                                   below*below<actual_r2<above*above)))
    with localcontext() as ctx:
        ctx.prec=70
        d=lambda x:Decimal(x.numerator)/Decimal(x.denominator)
        rp,rm=d(above),d(below)
        near_neg=-(rp*rp-4).sqrt();near_pos=-(rm*rm-4).sqrt()
        result=dict(schema='BASS_R4AA_EXACT_CONTACT_CELL_V1',center_z_a0=CENTER,
          R_squared_exact=str(r2),R_decimal=str(d(r2).sqrt()),
          previous_contact_exact=str(below),next_contact_exact=str(above),
          previous_contact_decimal=str(rm),next_contact_decimal=str(rp),
          negative_z_contact_decimal=str(near_neg),positive_z_contact_decimal=str(near_pos),
          negative_side_clearance_decimal=str(Decimal(-32)-near_neg),
          positive_side_clearance_decimal=str(near_pos+Decimal(32)),
          chosen_max_halfwidth_a0=H_LADDER[0],samples=samples,
          all_samples_in_same_contact_cell=all(x['same_contact_cell'] for x in samples),
          meaning='Exact inequalities on stored FP64 shell edges and FP64 requested/actual z; not a derivative error bound',
          physical_C9_established=False,derivative_error_bound_established=False)
    return result


def matrix(x):
    a=np.asarray(x,dtype=np.complex128)
    if a.ndim!=2 or a.shape[0]!=a.shape[1] or not np.isfinite(a).all():
        raise ValueError('finite square complex matrix required')
    return a


def ladder_at_center(samples, hs=H_LADDER):
    # The mapping carries S only; no access to a D field is possible here.
    return [(h,matrix(samples[(CENTER-h).hex()]),matrix(samples[(CENTER+h).hex()])) for h in hs]


def compensated_sum(terms):
    terms=[matrix(t) for t in terms]
    shape=terms[0].shape
    if any(t.shape!=shape for t in terms):raise ValueError('matrix shape mismatch')
    out=np.empty(shape,dtype=np.complex128)
    for idx in np.ndindex(shape):
        out[idx]=complex(math.fsum(t[idx].real for t in terms),math.fsum(t[idx].imag for t in terms))
    return matrix(out)


def r8_nominal(ladder, speed):
    if len(ladder)!=4 or any(ladder[j+1][0]*2!=ladder[j][0] for j in range(3)):
        raise ValueError('four exactly halving offsets required')
    if not math.isfinite(speed) or speed<=0:raise ValueError('positive velocity required')
    return compensated_sum([float(w)*speed*(matrix(plus)-matrix(minus))/(2*h)
                            for w,(h,minus,plus) in zip(WEIGHTS,ladder)])


def r8_recursive(ladder,speed):
    if len(ladder)!=4:raise ValueError('four offsets required')
    rows=[speed*(matrix(p)-matrix(m))/(2*h) for h,m,p in ladder]
    for level in range(1,4):
        factor=4**level
        rows=[(factor*rows[j+1]-rows[j])/(factor-1) for j in range(len(rows)-1)]
    return matrix(rows[0])


def interpolation_weights(nodes, x0):
    """Independent exact Vandermonde solve on stored actual-time FP64 nodes.

    n nodes reproduce derivatives of polynomials through degree n-1. No
    physical smoothness follows. Centering/scaling only conditions coefficient
    generation; exact rational arithmetic makes its error zero.
    """
    nodes=[F(float(x)) for x in nodes]; origin=F(float(x0))
    if len(nodes)<2 or len(set(nodes))!=len(nodes):raise ValueError('distinct nodes required')
    scale=max(abs(x-origin) for x in nodes)
    if not scale:raise ValueError('zero node span')
    x=[(t-origin)/scale for t in nodes];n=len(x)
    a=[[t**k for t in x]+[F(int(k==1))] for k in range(n)]
    for j in range(n):
        p=next((k for k in range(j,n) if a[k][j]),None)
        if p is None:raise ValueError('singular interpolation nodes')
        a[j],a[p]=a[p],a[j];div=a[j][j];a[j]=[v/div for v in a[j]]
        for k in range(n):
            if k==j:continue
            fac=a[k][j]
            if fac:a[k]=[v-fac*u for v,u in zip(a[k],a[j])]
    return [a[j][-1]/scale for j in range(n)]


def actual_time_probe(samples, times, hs, speed):
    positions=[CENTER+s*h for h in hs for s in (-1,1)]
    center=matrix(samples[CENTER.hex()]);t0=times[CENTER.hex()]
    nodes=[times[z.hex()] for z in positions]
    weights=interpolation_weights(nodes,t0)
    # Exact sum(weights)=0 permits subtracting raw S(t0) before accumulation.
    # Raw samples are not altered on disk and D is not consulted.
    if sum(weights)!=0:raise ArithmeticError('constant derivative cancellation failed')
    out=compensated_sum([float(w)*(matrix(samples[z.hex()])-center) for w,z in zip(weights,positions)])
    moments=[sum(w*(F(t)-F(t0))**k for w,t in zip(weights,nodes)) for k in range(len(nodes))]
    return out,dict(nodes_time_hex=[t.hex() for t in nodes],center_time_hex=t0.hex(),
                    weights_exact=[str(w) for w in weights],moments_exact=[str(x) for x in moments],
                    moments_pass=moments==[F(int(k==1)) for k in range(len(nodes))],
                    coefficient_L1_ta_inverse=float(sum(abs(w) for w in weights)),
                    subtraction_of_raw_center_is_algebraic_constant_annihilation=True,
                    physical_error_bound=False)


def amplification(speed,H):
    return float(F(473,35)*F(float(speed))/F(float(H)))
