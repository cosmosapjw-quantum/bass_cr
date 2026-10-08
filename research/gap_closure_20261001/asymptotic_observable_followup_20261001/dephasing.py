"""Exact finite Bohr-frequency algebra, not a physical propagation solver.

Energies are exact declared numbers, never tolerance-grouped eigensolver output.
Matrix/state entries are Gaussian rationals. No asymptotic-state estimator is
provided; the caller must supply that state under the separate theorem.
"""
from dataclasses import dataclass
from fractions import Fraction as F


def rat(x):
    if isinstance(x,float):raise TypeError('Exact int/Fraction/string required; no floating degeneracy tolerance')
    return F(x)

@dataclass(frozen=True)
class QComplex:
    re:F=F(0)
    im:F=F(0)
    def __post_init__(self):
        object.__setattr__(self,'re',rat(self.re));object.__setattr__(self,'im',rat(self.im))
    def __add__(self,other):
        other=asq(other);return QComplex(self.re+other.re,self.im+other.im)
    def __mul__(self,other):
        other=asq(other);return QComplex(self.re*other.re-self.im*other.im,self.re*other.im+self.im*other.re)
    def conj(self):return QComplex(self.re,-self.im)

def asq(x):return x if isinstance(x,QComplex) else QComplex(x)

def bohr_coefficients(energies,observable,state):
    """Return exact c_w for <x,exp(iHt) A exp(-iHt)x>, hbar=1.

    The observable must be Hermitian. A need not be a projector: compression of
    the old physical projector to a new reference space is only a contraction.
    This function does not certify positivity/contraction or a physical state.
    """
    e=list(map(rat,energies));n=len(e);x=list(map(asq,state))
    if n==0 or len(x)!=n or len(observable)!=n or any(len(row)!=n for row in observable):raise ValueError('incompatible dimensions')
    A=[[asq(v) for v in row] for row in observable]
    if any(A[i][j]!=A[j][i].conj() for i in range(n) for j in range(n)):raise ValueError('observable must be exactly Hermitian')
    c={}
    for i in range(n):
        for j in range(n):
            frequency=e[i]-e[j]
            c[frequency]=c.get(frequency,QComplex())+x[i].conj()*A[i][j]*x[j]
    return c

def ordinary_limit_exists(coefficients):
    """Exact criterion for the supplied finite trigonometric polynomial only."""
    return all(value==QComplex() for frequency,value in coefficients.items() if frequency!=0)
