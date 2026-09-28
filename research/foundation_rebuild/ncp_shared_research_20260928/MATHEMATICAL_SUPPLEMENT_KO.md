# Moving-metric defect and controlled projection: R3 supplement

Evidence labels: derived; exact 2x2 algebra checked with Wolfram; synthetic floating-point probes checked locally. These are not full BASS trajectory certificates.

## Definitions and conventions

Physical time t; retain hbar. Let the columns of B(t) be a linearly independent, differentiable finite basis, S=B†B>0, D=B†dot B and H=B†H_phys B. For a self-adjoint physical Hamiltonian and exact quadrature H=H†. In the existing atomic-unit code one must apply its time/unit adapter explicitly rather than copying a physical-time rate unchanged.

The coefficient equation is

    i*hbar*S*dot c = (H-i*hbar*D)c,
    A = -(i/hbar) S^-1 H - S^-1 D,   dot c=A c.

For an actually represented differentiable overlap S(t),

    d(c†Sc)/dt = c†[actual(dot S)-D-D† + (i/hbar)(H†-H)]c.

Thus H cancels only if Hermiticity is established. A prior symmetrization that changes H or D is not an independent check of this identity.

Choose S=C†C (for example upper Cholesky), y=Cc and

    G=dot C*C^-1 + C*A*C^-1.

Using C*S^-1=C^-†,

    G+G† = C^-† R_total C^-1,
    R_total=actual(dot S)-D-D†+(i/hbar)(H†-H).

This is a congruence, not C^-1 R C^-† in arbitrary order. The spectral norm of the whitened Hermitian defect has units inverse time. A relative Frobenius residual of unwhitened arrays is not interchangeable with that rate.

For H Hermitian, ||G+G†||_2 depends only on overlap/connection data. This can serve as an early rejection diagnostic. The rule is asymmetric: one certified failure rejects a conjunction, but a subset of passes does not certify it.

## Actual versus interpolated derivatives

If S is linearly represented between S0 and S1, its actual derivative is (S1-S0)/h. Independently interpolating tabulated derivatives dS0,dS1 gives an actual-compatible derivative everywhere only if dS0=dS1=(S1-S0)/h. Endpoint algebraic identities do not imply this condition.

The R2 sentinel derivative [S(t+eps)-S(t-eps)]/(2eps) is an independent approximation, not an exact derivative. Its discrepancy includes spatial and difference error. A single eps and five times do not bound the whole interval. Retain unmodified source arrays and report raw, relative and whitened quantities separately.

## How much dynamics can skew projection change?

Write G=K+E, K=(G-G†)/2 skew-Hermitian and E=(G+G†)/2 Hermitian. Let U solve dot U=G U, V solve dot V=K V, both identity initially. V is unitary. With W=V†U,

    dot W=(V†EV)W,  W(t0)=I.

For eta(T)=integral_t0^T ||E(t)||_2 dt, Gronwall and variation of constants give

    ||W(T)||_2 <= exp(eta),
    ||U(T)-V(T)||_2 = ||W(T)-I||_2 <= exp(eta)-1.

For equal initial unit states and a fixed effect 0<=P<=I,

    |y_U†P y_U-y_V†P y_V| <= exp(2 eta)-1.

This last quantity is an unnormalised quadratic observable for U when U is not unitary; it is not automatically a physical probability. The scalar commuting example E=epsilon I saturates the operator bound. The bound is dimensionless, vanishes at eta=0, and assumes integrable E with well-defined finite-dimensional evolution.

Conclusion: forcing skew-Hermiticity guarantees the chosen norm, but fidelity to the original equations still needs a controlled eta. Do not set dot S:=D+D† to make eta appear zero. Do not estimate eta by multiplying five-point maximum residual by interval length without a justified uniform bound.

## Parameter factorization and evidence independence

A cached component may be factored only over variables on which it is proven not to depend. A suitable numerical cache signature includes model/source/basis/trajectory/parameter/dtype/ABI/numeric-runtime/policy identities and the exact time representation. Output directory, execution PID, worker count and scheduling order belong to execution provenance, not automatically to the numerical object.

An explicit import bridge must keep original task IDs, receipts and payload bytes, and record the new consumer and equivalence scope. Removing path metadata from a digest does not by itself prove two engines equivalent. A changed basis, trajectory, quadrature policy or compiled binary requires its own compatibility/admission evidence.

HE common-contour reweighting is conditional on homotopy and identical spectral sheets. Only its common-subexpression idea transfers to CR; its contour or parameter independence does not. Many outputs sharing one cached component have correlated errors, not independent witnesses.

## Cost ordering

For two rejection tests with deterministic costs cA,cB>0 and comparable conditional failure probabilities pA,pB, the expected costs are cA+(1-pA)cB and cB+(1-pB)cA. Their difference is cA*pB-cB*pA. Larger p/c first is preferable under those assumptions. In the real task graph no probabilities were measured, so this is a rule for ordering known cheap structural checks, not an estimated saving.

## Literature relation

Artacho and O'Regan, Quantum mechanics in an evolving Hilbert space, arXiv:1608.05300, explain basis-evolution connection terms and their geometry. Auzinger et al., A posteriori error estimation for Magnus-type integrators, DOI 10.1051/m2an/2018050, address defect-based error estimation for skew-Hermitian non-autonomous systems. These sources support the framework; the project's certificate is not established merely by citation. The additional actual-metric and projection bounds above are direct derivations with stated assumptions.
