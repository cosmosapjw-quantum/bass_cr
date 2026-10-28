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


def _inputs(atoms, cap, cross_budget):
    A=tuple(atoms)
    if any(type(a) is not Atom for a in A):raise TypeError("invalid atom type")
    if len(set(a.key for a in A))!=len(A):raise ValueError("duplicate atom key")
    K=exact(cap); c=exact(cross_budget)
    if K<0 or c<0:raise ValueError("negative cap/budget")
    return A,K,c


def verify_certificate(atoms, cap, cross_budget, result):
    """Check a complete witness and LP dual with explicit exact arithmetic.

    This is a verifier, not a second optimizer. It remains active with python -O.
    """
    A,K,c=_inputs(atoms,cap,cross_budget)
    by_key={a.key:a for a in A}
    low={a.key:a for a in A if a.mass>0 and 2*a.energy<=K}
    high={a.key:a for a in A if a.mass>0 and 2*a.energy>K}
    required={'M_budget','d_max','cross_used','primal','low_diagonal','singles',
              'dual_prices','budget_multiplier','dual_value','gap','L','scope'}
    def check(ok,detail):
        if not ok:raise ValueError('INVALID_CERTIFICATE: '+detail)
    check(required.issubset(result),'missing result fields')
    def rational(v):
        check(type(v) is Fraction,'non-Fraction certificate quantity')
        return v
    def nonnegative(v):
        v=rational(v);check(v>=0,'negative certificate quantity');return v
    usage={a.key:Fraction(0) for a in A}
    m=Fraction(0);q=Fraction(0);cross=Fraction(0)
    for h,l,value in result['primal']:
        value=nonnegative(value)
        check(h in high and l in low,'invalid HL support')
        check(high[h].energy+low[l].energy<=K,'energy support')
        usage[h]+=value;usage[l]+=value;m+=value
        if high[h].bin!=low[l].bin:cross+=value
    for key,value in result['low_diagonal']:
        value=nonnegative(value);check(key in low,'invalid low diagonal')
        usage[key]+=2*value;q+=value
    for key,value in result['singles']:
        value=nonnegative(value);check(key in by_key,'invalid singleton')
        usage[key]+=value
    check(all(usage[a.key]==a.mass for a in A),'marginal equality')
    L=sum((a.mass for a in low.values()),Fraction(0))
    check(nonnegative(result['L'])==L,'low mass')
    check(nonnegative(result['M_budget'])==m,'HL objective')
    check(nonnegative(result['d_max'])==m+q==(L+m)/2,'double-event objective')
    check(nonnegative(result['cross_used'])==cross<=c,'cross budget')
    prices={}
    for key,value in result['dual_prices']:
        check(key in by_key and key not in prices,'dual price key')
        prices[key]=nonnegative(value)
    check(set(prices)==set(by_key),'dual price coverage')
    lam=nonnegative(result['budget_multiplier'])
    for h in high.values():
        for l in low.values():
            if h.energy+l.energy<=K:
                check(prices[h.key]+prices[l.key]+(lam if h.bin!=l.bin else 0)>=1,
                      'dual edge inequality')
    dual=sum((a.mass*prices[a.key] for a in A),Fraction(0))+c*lam
    check(nonnegative(result['dual_value'])==dual==m,'dual objective')
    check(rational(result['gap'])==dual-m==0,'primal dual gap')
    check(result['scope']=='SMALL_FINITE_EXACT_LP_NO_PHYSICAL_KERNEL','scope tag')
    return True


def solve(atoms, cap, cross_budget, max_atoms=12, max_edges=48):
    """Solve M(c)=max HL event mass with cross-bin event mass <=c.

    Return exact primal and independently optimized LP dual certificates.
    Small instances only: no claim of native 3201-atom scalability.
    """
    A,K,c=_inputs(atoms,cap,cross_budget)
    if type(max_atoms) is not int or not 0<=max_atoms<=12:
        raise ValueError('max_atoms must be an integer in [0,12]')
    if type(max_edges) is not int or not 0<=max_edges<=48:
        raise ValueError('max_edges must be an integer in [0,48]')
    if len(A)>max_atoms:raise ValueError("SMALL_INSTANCE_ONLY: atom cap")
    low=[a for a in A if a.mass>0 and 2*a.energy<=K]
    high=[a for a in A if a.mass>0 and 2*a.energy>K]
    edges=[(h,l) for h in high for l in low if h.energy+l.energy<=K]
    if len(edges)>max_edges:raise ValueError("SMALL_INSTANCE_ONLY: edge cap")
    L=sum((a.mass for a in low),Fraction(0))
    if not edges:
        result={'M_budget':Fraction(0),'d_max':L/2,'cross_used':Fraction(0),
                'primal':(), 'low_diagonal':tuple((a.key,a.mass/2) for a in low),
                'singles':tuple((a.key,a.mass) for a in high),
                'dual_prices':tuple((a.key,Fraction(0)) for a in A),
                'budget_multiplier':Fraction(0),
                'dual_value':Fraction(0),'gap':Fraction(0),'L':L,
                'scope':'SMALL_FINITE_EXACT_LP_NO_PHYSICAL_KERNEL'}
        verify_certificate(A,K,c,result)
        return result
    x=symbols('x0:'+str(len(edges)))
    cross=[i for i,(h,l) in enumerate(edges) if h.bin!=l.bin]
    cons=[v>=0 for v in x]
    for a in high+low:
        cons.append(sum((x[i] for i,(h,l) in enumerate(edges) if a in (h,l)),Rational(0))<=_sym(a.mass))
    cons.append(sum((x[i] for i in cross),Rational(0))<=_sym(c))
    msol,point=lpmax(sum(x,Rational(0)),cons)
    pf=[_frac(point.get(t,Rational(0))) for t in x]
    M=_frac(msol); Cu=sum((pf[i] for i in cross),Fraction(0))
    prices=symbols('p0:'+str(len(high)+len(low)))
    lam=symbols('lam')
    atoms2=high+low
    idx={a.key:i for i,a in enumerate(atoms2)}
    dual_cons=[v>=0 for v in prices]+[lam>=0]
    for h,l in edges:
        dual_cons.append(prices[idx[h.key]]+prices[idx[l.key]]+(lam if h.bin!=l.bin else 0)>=1)
    dval,dp=lpmin(sum((prices[i]*_sym(a.mass) for i,a in enumerate(atoms2)),Rational(0))+lam*_sym(c),dual_cons)
    dv=_frac(dval)
    primal=tuple((h.key,l.key,pf[i]) for i,(h,l) in enumerate(edges) if pf[i]>0)
    residuals={l.key:l.mass-sum((pf[i] for i,(h,z) in enumerate(edges) if z==l),Fraction(0)) for l in low}
    # low diagonals are allowed by construction (2E_low<=K), and carry no cross-bin cost
    atom_prices={a.key:_frac(dp.get(prices[i],Rational(0))) for i,a in enumerate(atoms2)}
    singles=tuple((h.key,h.mass-sum((pf[i] for i,(z,l) in enumerate(edges) if z==h),Fraction(0))) for h in high)
    result={'M_budget':M,'d_max':(L+M)/2,'cross_used':Cu,'primal':primal,
            'low_diagonal':tuple((k,r/2) for k,r in residuals.items() if r>0),
            'singles':tuple((k,r) for k,r in singles if r>0),
            'dual_prices':tuple((a.key,atom_prices.get(a.key,Fraction(0))) for a in A),
            'budget_multiplier':_frac(dp.get(lam,Rational(0))),
            'dual_value':dv,'gap':dv-M,'L':L,
            'scope':'SMALL_FINITE_EXACT_LP_NO_PHYSICAL_KERNEL'}
    verify_certificate(A,K,c,result)
    return result


def example_atoms():
    return (Atom.parse('L0',0,1,0),Atom.parse('L1',1,1,1),
            Atom.parse('H0','5/2',1,0),Atom.parse('H1','19/5',1,1))


if __name__=='__main__':
    for c in ('0','1/2','1','3/2','2'):
        z=solve(example_atoms(),4,c)
        print('c=',c,'M=',z['M_budget'],'dmax=',z['d_max'],
              'used=',z['cross_used'],'gap=',z['gap'])
