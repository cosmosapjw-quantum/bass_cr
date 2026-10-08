# State-aware rational rate budget

This is a conditional finite-model theorem and exact arithmetic audit. It is
not a certificate of any physical B0 rate or endpoint state.

For the metric-compatible system in the sibling projector theorem, let N>0 be
the conserved norm, p=P/N, and a bound A on the integral of rho over the interval.
The off-diagonal form gives |p'| <= 2 sqrt(p(1-p)) rho. The integrated theorem is
|asin sqrt(p1) - asin sqrt(p0)| <= A, including the boundary cases p=0 and p=1.
Its rigorous endpoint proof is in `../projector/PROJECTOR_RATE_THEOREM.md`.

For theta=asin sqrt(p0), Taylor's formula with |(sin²)''|<=2 yields

    |p1-p0| <= 2 sqrt(p0(1-p0)) A + A².

This also follows by integrating the second derivative along the actual angle
difference; no differentiability of the angle at population zero is assumed.
If p0 lies in a certified interval [l,u], maximize p(1-p) on that interval at
the point closest to 1/2. For an outward rational square-root bound r, obtain

    |p1-p0| <= min(1, A, 2 r A + A²).

The A term is the old state-independent G01 bound. The sharper state-independent
trigonometric envelope is sin(min(A,pi/2)); the helper retains rational arithmetic
instead of claiming rounded trigonometric floats as rigorous bounds.
The final population belongs to [max(0,l-b),min(1,u+b)] where b is the bound above.
For unnormalized P, multiply endpoints and b by N. This applies to one interval;
incoming and outgoing budgets remain separate.

`sqrt_upper` computes ceil(2^bits sqrt(x))/2^bits using integer square root and
an exact square comparison. Thus every rounding is outward. `admitted_angle`
returns the largest dyadic A at the chosen precision satisfying the sufficient
quadratic 2 r A+A²<=epsilon. This is not the largest angle allowed by the sharper
trigonometric bound and says nothing about the actual dynamical error.

At p0=0 or 1 the resulting budget is A², not A. At a small positive population
the leading coefficient 2 sqrt(p0(1-p0)) can substantially reduce the bound.
This is useful only if the population is known at the same interval endpoint.
The saved +/-12 result must never be attached to the +/-32 static matrices.

`ILLUSTRATIVE_BUDGET.json` uses the exact rational decimal
0.009653428615023815 solely as an illustration of the archived displayed value.
That decimal is not an outward population enclosure, and no state at +/-32 or
any other tail point is supplied. Consequently the displayed approximately
fivefold integral allowance is not a physical error certificate.

All seven focused tests use exact Fraction arithmetic. This tiny calculation
has no quadrature hot loop or reduction to parallelize; converting it to FP64
Fortran would discard the exact proof. R4S OpenMPI/Fortran/SIMD policy continues
to govern expensive physical kernels and independent query batches.
