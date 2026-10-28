"""Exact, SMALL-instance cross-bin-budget He event upper frontier.

Fractional event measures, not physical rates/production nonlinear kernels.
Source marginal units are m^-3 s^-2, energy eV; c has the same units.
The exact LP backend (SymPy simplex) has a deliberately narrow atom/edge guard.
"""
from dataclasses import dataclass
from fractions import Fraction
from sympy import Rational, symbols
from sympy.solvers.simplex import lpmax, lpmin


def exact(value):
    if isinstance(value, bool) or type(value) is float:
        raise TypeError("exact rational required; float/bool refused")
    if type(value) in (int, str, Fraction):
        return Fraction(value)
    raise TypeError("expected int, fraction or rational string")


@dataclass(frozen=True)
class Atom:
    key: str
    energy: Fraction
    mass: Fraction
    bin: int

    def __post_init__(self):
        if not isinstance(self.key,str) or not self.key or type(self.bin) is not int or self.bin < 0:
            raise ValueError("nonempty key and nonnegative integer bin required")
        if type(self.energy) is not Fraction or type(self.mass) is not Fraction:
            raise TypeError("energy and mass must be exact Fraction")
        if self.energy < 0 or self.mass < 0:
            raise ValueError("negative energy or marginal mass")

    @classmethod
    def parse(cls, key, energy, mass, bin):
        return cls(key, exact(energy), exact(mass), bin)


def _sym(q):
    q=exact(q)
    return Rational(q.numerator,q.denominator)


def _frac(q):
    numer,denom=Rational(q).as_numer_denom()
    return Fraction(int(numer),int(denom))


def solve(atoms, cap, cross_budget, max_atoms=12, max_edges=48):
    """Solve M(c)=max HL event mass with cross-bin event mass <=c.

    Return exact primal and independently optimized LP dual certificates.
    Small instances only: no claim of native 3201-atom scalability.
    """
    A=tuple(atoms)
    K=exact(cap); c=exact(cross_budget)
    if K<0 or c<0:raise ValueError("negative cap/budget")
    if len(A)>max_atoms:raise ValueError("SMALL_INSTANCE_ONLY: atom cap")
    if len(set(a.key for a in A))!=len(A):raise ValueError("duplicate atom key")
    if any(type(a) is not Atom for a in A):raise TypeError("invalid atom type")
    low=[a for a in A if a.mass>0 and 2*a.energy<=K]
    high=[a for a in A if a.mass>0 and 2*a.energy>K]
    edges=[(h,l) for h in high for l in low if h.energy+l.energy<=K]
    if len(edges)>max_edges:raise ValueError("SMALL_INSTANCE_ONLY: edge cap")
    L=sum((a.mass for a in low),Fraction(0))
    if not edges:
        return {'M_budget':Fraction(0),'d_max':L/2,'cross_used':Fraction(0),
                'primal':(), 'dual':(), 'dual_value':Fraction(0),'gap':Fraction(0),'L':L,
                'scope':'SMALL_FINITE_EXACT_LP_NO_PHYSICAL_KERNEL'}
    x=symbols('x0:'+str(len(edges)))
    cross=[i for i,(h,l) in enumerate(edges) if h.bin!=l.bin]
    cons=[v>=0 for v in x]
    for a in high+low:
        cons.append(sum((x[i] for i,(h,l) in enumerate(edges) if a in (h,l)),Rational(0))<=_sym(a.mass))
    cons.append(sum((x[i] for i in cross),Rational(0))<=_sym(c))
    msol,point=lpmax(sum(x,Rational(0)),cons)
    pf=[_frac(point.get(t,Rational(0))) for t in x]
    M=_frac(msol); Cu=sum((pf[i] for i in cross),Fraction(0))
    assert Cu<=c and sum(pf,Fraction(0))==M
    for a in high+low:
        assert sum((pf[i] for i,(h,l) in enumerate(edges) if a in (h,l)),Fraction(0))<=a.mass
    prices=symbols('p0:'+str(len(high)+len(low)))
    lam=symbols('lam')
    atoms2=high+low
    idx={a.key:i for i,a in enumerate(atoms2)}
    dual_cons=[v>=0 for v in prices]+[lam>=0]
    for h,l in edges:
        dual_cons.append(prices[idx[h.key]]+prices[idx[l.key]]+(lam if h.bin!=l.bin else 0)>=1)
    dval,dp=lpmin(sum((prices[i]*_sym(a.mass) for i,a in enumerate(atoms2)),Rational(0))+lam*_sym(c),dual_cons)
    dv=_frac(dval)
    assert dv==M, 'PRIMAL_DUAL_GAP'
    assert all(bool(q.subs(dp)) for q in dual_cons)
    primal=tuple((h.key,l.key,pf[i]) for i,(h,l) in enumerate(edges) if pf[i]>0)
    residuals={l.key:l.mass-sum((pf[i] for i,(h,z) in enumerate(edges) if z==l),Fraction(0)) for l in low}
    assert all(u>=0 for u in residuals.values())
    # low diagonals are allowed by construction (2E_low<=K), and carry no cross-bin cost
    return {'M_budget':M,'d_max':(L+M)/2,'cross_used':Cu,'primal':primal,
            'low_diagonal':tuple((k,r/2) for k,r in residuals.items() if r>0),
            'dual':tuple((a.key,_frac(dp.get(prices[i],Rational(0)))) for i,a in enumerate(atoms2))+(('lambda',_frac(dp.get(lam,Rational(0)))),),
            'dual_value':dv,'gap':dv-M,'L':L,
            'scope':'SMALL_FINITE_EXACT_LP_NO_PHYSICAL_KERNEL'}


def example_atoms():
    return (Atom.parse('L0',0,1,0),Atom.parse('L1',1,1,1),
            Atom.parse('H0','5/2',1,0),Atom.parse('H1','19/5',1,1))


if __name__=='__main__':
    for c in ('0','1/2','1','3/2','2'):
        z=solve(example_atoms(),4,c)
        print('c=',c,'M=',z['M_budget'],'dmax=',z['d_max'],
              'used=',z['cross_used'],'gap=',z['gap'])
