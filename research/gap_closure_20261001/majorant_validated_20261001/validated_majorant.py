"""Exact rational finite-domain majorant demonstrator and conditional assembler.

No sampled derivative, float conversion, or numerical eigensolver is used in a
certificate. The generic assembler checks the shape of proof provenance; it
cannot independently prove an arbitrary caller's mathematical assertions.
"""
from dataclasses import dataclass
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path


def rational(value):
    if isinstance(value, float):
        raise TypeError('binary floats are not certified rational input')
    if not isinstance(value, (int, str, F)):
        raise TypeError('use an integer, exact fraction, or decimal/rational string')
    return F(value)


@dataclass(frozen=True)
class Interval:
    lo: F
    hi: F

    def __post_init__(self):
        object.__setattr__(self, 'lo', rational(self.lo))
        object.__setattr__(self, 'hi', rational(self.hi))
        if self.lo > self.hi:
            raise ValueError('reversed interval')

    @staticmethod
    def point(x):
        return Interval(x, x)

    @staticmethod
    def coerce(x):
        return x if isinstance(x, Interval) else Interval.point(x)

    def __add__(self, other):
        y = self.coerce(other)
        return Interval(self.lo+y.lo, self.hi+y.hi)

    __radd__ = __add__

    def __neg__(self):
        return Interval(-self.hi, -self.lo)

    def __sub__(self, other):
        return self + (-self.coerce(other))

    def __rsub__(self, other):
        return self.coerce(other) + (-self)

    def __mul__(self, other):
        y = self.coerce(other)
        products = [a*b for a in (self.lo, self.hi) for b in (y.lo, y.hi)]
        return Interval(min(products), max(products))

    __rmul__ = __mul__

    def reciprocal(self):
        if self.lo <= 0 <= self.hi:
            raise ZeroDivisionError('interval contains zero')
        return Interval(1/self.hi, 1/self.lo)

    def __truediv__(self, other):
        return self * self.coerce(other).reciprocal()

    def __rtruediv__(self, other):
        return self.coerce(other) * self.reciprocal()

    def square(self):
        ends = (self.lo*self.lo, self.hi*self.hi)
        return Interval(0 if self.lo <= 0 <= self.hi else min(ends), max(ends))

    def abs_upper(self):
        return max(abs(self.lo), abs(self.hi))


def _matrix(a):
    n = len(a)
    if n == 0 or any(len(row) != n for row in a):
        raise ValueError('nonempty square matrix required')
    out = [[rational(x) for x in row] for row in a]
    if any(out[i][j] != out[j][i] for i in range(n) for j in range(n)):
        raise ValueError('exact real symmetry required; complex case not implemented')
    return out


def is_spd(a):
    """Exact LDL positivity, without pivoting, shifts, or finite precision."""
    a = _matrix(a)
    n = len(a)
    l = [[F(0) for _ in range(n)] for _ in range(n)]
    d = [F(0)]*n
    for i in range(n):
        l[i][i] = F(1)
        d[i] = a[i][i] - sum(l[i][k]**2*d[k] for k in range(i))
        if d[i] <= 0:
            return False
        for j in range(i+1, n):
            l[j][i] = (a[j][i] - sum(l[j][k]*l[i][k]*d[k] for k in range(i)))/d[i]
    return True


def pencil_radius_bounds(s, w, bits=40):
    """Enclose max |lambda(W,S)| using q*S +/- W positive definiteness.

    Strict SPD at q means rho<q. Failed strict SPD means rho>=q. Bounds are
    mathematical rational bounds for exactly supplied symmetric matrices.
    """
    s, w = _matrix(s), _matrix(w)
    n = len(s)
    if len(w) != n or not is_spd(s):
        raise ValueError('dimension mismatch or non-SPD metric')
    if not isinstance(bits, int) or bits < 1:
        raise ValueError('positive integer bisection count required')
    if all(x == 0 for row in w for x in row):
        return F(0), F(0)

    def above(q):
        return all(is_spd([[q*s[i][j] + sign*w[i][j] for j in range(n)] for i in range(n)])
                   for sign in (-1, 1))

    lo, hi = F(0), F(1)
    for _ in range(4096):
        if above(hi):
            break
        hi *= 2
    else:
        raise ValueError('magnitude exceeds explicit resource ceiling')
    for _ in range(bits):
        mid = (lo+hi)/2
        if above(mid):
            hi = mid
        else:
            lo = mid
    return lo, hi


def lipschitz_bound(s0, s1, w0, w1):
    s0, s1, w0, w1 = map(rational, (s0, s1, w0, w1))
    if s0 <= 0 or min(s1, w0, w1) < 0:
        raise ValueError('strict metric lower bound and nonnegative norm bounds required')
    return w1/s0 + w0*s1/s0**2


@dataclass(frozen=True)
class Proof:
    method: str
    artifact: str
    sha256: str
    reference: str

    def __post_init__(self):
        if self.method not in {'exact_rational_interval', 'analytic_derivation', 'validated_interval'}:
            raise ValueError('derivative/eigenvalue certificates cannot be fits or finite differences')
        if (not self.artifact or not self.reference or len(self.sha256) != 64
                or any(c not in '0123456789abcdef' for c in self.sha256)):
            raise ValueError('identified proof artifact, SHA256, and reference required')


@dataclass(frozen=True)
class CellBounds:
    left: F
    right: F
    center: F
    s0: F
    s1: F
    w0: F
    w1: F
    center_rho_upper: F
    scope: str
    derivative_proof: Proof
    center_proof: Proof

    def __post_init__(self):
        for name in ('left', 'right', 'center', 's0', 's1', 'w0', 'w1', 'center_rho_upper'):
            object.__setattr__(self, name, rational(getattr(self, name)))
        if not self.left < self.right or self.center != (self.left+self.right)/2:
            raise ValueError('positive width and midpoint center required')
        if self.center_rho_upper < 0 or not self.scope:
            raise ValueError('nonnegative spectral bound and explicit scope required')
        if not isinstance(self.derivative_proof, Proof) or not isinstance(self.center_proof, Proof):
            raise ValueError('proof provenance objects required')
        lipschitz_bound(self.s0, self.s1, self.w0, self.w1)

    @property
    def L(self):
        return lipschitz_bound(self.s0, self.s1, self.w0, self.w1)

    def upper_at(self, x):
        x = rational(x)
        if not self.left <= x <= self.right:
            raise ValueError('point outside cell')
        return self.center_rho_upper + self.L*abs(x-self.center)

    def integral_upper(self):
        width = self.right-self.left
        return width*self.center_rho_upper + self.L*width**2/4

    def as_json(self):
        from dataclasses import asdict
        result = asdict(self)
        for key, val in list(result.items()):
            if isinstance(val, F):
                result[key] = str(val)
        result['L'] = str(self.L)
        result['integral_upper'] = str(self.integral_upper())
        return result


def assemble_envelope(cells):
    """Compose conditional certificates; never promote them to infinity."""
    cells = list(cells)
    if not cells or any(not isinstance(c, CellBounds) for c in cells):
        raise ValueError('nonempty sequence of certified cells required')
    for a, b in zip(cells, cells[1:]):
        if a.right != b.left or a.scope != b.scope:
            raise ValueError('same-scope contiguous sorted intervals required')
    # Join neighboring valid tents continuously by raising boundary heights.
    # Each half-cell becomes a line from the center upper bound to a boundary
    # at least as high as the original Lipschitz tent at that boundary.
    ends = [c.upper_at(c.left) for c in cells]
    heights = [ends[0]] + [max(a, b) for a, b in zip(ends, ends[1:])] + [ends[-1]]
    vertices = []
    for i, c in enumerate(cells):
        vertices.extend([{'z': str(c.left), 'rho_upper': str(heights[i])},
                         {'z': str(c.center), 'rho_upper': str(c.center_rho_upper)}])
    vertices.append({'z': str(cells[-1].right), 'rho_upper': str(heights[-1])})
    integral = sum(((c.right-c.left)*(heights[i]+heights[i+1]+2*c.center_rho_upper)/4
                    for i, c in enumerate(cells)), F(0))
    return {
        'level': 2,
        'scope': cells[0].scope,
        'domain': [str(cells[0].left), str(cells[-1].right)],
        'conditional_on': 'validity of identified input proof artifacts; metadata is not a proof checker',
        'infinite_tail_certified': False,
        'integral_units': 'rho_units * z_units; divide by positive v for time integral',
        'integral_upper': str(integral),
        'piecewise_tent_integral_upper': str(sum((c.integral_upper() for c in cells), F(0))),
        'continuous_envelope_vertices': vertices,
        'arithmetic': 'exact rational, no floating point error in certificate',
        'cells': [c.as_json() for c in cells],
    }


def demo_matrices(z):
    """Fixed real-symmetric rational family, certified only on 0<=z<=1."""
    z = rational(z)
    if not 0 <= z <= 1:
        raise ValueError('demo domain is [0,1]')
    d = (1+z)**2
    return ([[F(2), z/8], [z/8, 1+z*z/16]],
            [[1/d, z/(4*d)], [z/(4*d), -1/(2*d)]])


def _norm_upper(matrix):
    # Exact real symmetry supplies ||A||2 <= ||A||infinity.
    return max(sum(x.abs_upper() for x in row) for row in matrix)


def certify_demo_cell(left, right):
    left, right = rational(left), rational(right)
    if not 0 <= left < right <= 1:
        raise ValueError('demo interval must be contained in [0,1]')
    z, zero = Interval(left, right), Interval.point(0)
    one = Interval.point(1)
    denom = (one+z).square()
    cube = denom*(one+z)
    s = [[Interval.point(2), z/8], [z/8, one+z.square()/16]]
    ds = [[zero, Interval.point(F(1, 8))], [Interval.point(F(1, 8)), z/8]]
    w = [[one/denom, z/(4*denom)], [z/(4*denom), -one/(2*denom)]]
    dw = [[-2/cube, (one-z)/(4*cube)], [(one-z)/(4*cube), one/cube]]
    s0 = min(s[i][i].lo-sum(s[i][j].abs_upper() for j in range(2) if j != i) for i in range(2))
    center = (left+right)/2
    _, rho_upper = pencil_radius_bounds(*demo_matrices(center))
    digest = sha256(Path(__file__).read_bytes()).hexdigest()
    proof = Proof('exact_rational_interval', Path(__file__).name, digest,
                  'certify_demo_cell: exact rational interval extensions of explicit family and derivatives')
    center_proof = Proof('exact_rational_interval', Path(__file__).name, digest,
                         'pencil_radius_bounds: exact LDL SPD tests on q*S +/- W')
    return CellBounds(left, right, center, s0, _norm_upper(ds), _norm_upper(w),
                      _norm_upper(dw), rho_upper, 'synthetic_rational_family_v1', proof, center_proof)


def tail_p2_enclosure(coefficient, velocity, impact, start, terms=24):
    """Conditional exact enclosure C/(v*b)*atan(b/Z), for 0<=b<=Z.

    This evaluates an integral; it does not prove rho <= C/(b*b+z*z).
    All arguments denote exact rationals, not uncertain physical measurements.
    """
    c, v, b, z = map(rational, (coefficient, velocity, impact, start))
    if c < 0 or v <= 0 or b < 0 or z <= 0 or b > z:
        raise ValueError('requires C>=0, v>0, Z>0, and 0<=b<=Z')
    if not isinstance(terms, int) or terms < 1:
        raise ValueError('positive integer series count required')
    if b == 0:
        return Interval.point(c/(v*z))
    x = b/z
    partial = sum((F((-1)**k)*x**(2*k+1)/(2*k+1) for k in range(terms)), F(0))
    next_term = F((-1)**terms)*x**(2*terms+1)/(2*terms+1)
    return Interval(min(partial, partial+next_term), max(partial, partial+next_term)) * (c/(v*b))


def write_demo(path):
    result = assemble_envelope([certify_demo_cell(F(i, 4), F(i+1, 4)) for i in range(4)])
    result['certificate_kind'] = 'genuine_finite_continuum_demonstrator'
    result['b0_physical_certificate'] = False
    result['finite_arithmetic_error'] = '0: exact Fraction operations on exact rational inputs'
    result['eigenvalue_bisection_uncertainty'] = 'included by using the upper rational endpoint'
    result['integration_error'] = '0: exact integral of the continuous piecewise-linear envelope'
    result['source_sha256'] = sha256(Path(__file__).read_bytes()).hexdigest()
    Path(path).write_text(json.dumps(result, indent=2)+'\n')
    return result


if __name__ == '__main__':
    result = write_demo(Path(__file__).with_name('SYNTHETIC_CONTINUUM_CERTIFICATE.json'))
    print(json.dumps({key: result[key] for key in ('level', 'domain', 'scope', 'integral_upper', 'infinite_tail_certified')}, indent=2))
