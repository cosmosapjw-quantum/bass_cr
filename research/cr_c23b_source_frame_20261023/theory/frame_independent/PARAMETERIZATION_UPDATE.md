# Adopted momentum-boost parameter

The producer proposes u=gamma*beta>=0 as input. This retains tiny boosts when
gamma itself would round to1. Set gamma=hypot(1,u) and
delta_gamma=u*(u/(gamma+1)). The exact real relation is
u^2=delta_gamma*(delta_gamma+2). Use q=sqrt(K)*sqrt(K+2M),
A=gamma*K+delta_gamma*M and B=u*q.

The independently checked factorization is

\[
(A-B)(A+B)=(K-\delta_\gamma M)^2.
\]

After handling B=0 as a Dirac measure, define d=K-delta_gamma*M,
k_plus=A+B and k_minus=d*(d/k_plus). This is a direct algebraic alternative to
the rapidity expression in FRAME_DERIVATION.md. It requires no transcendental
rapidity subtraction and remains nonnegative without clipping. Wolfram's
factorization of the polynomial difference returned exactly0.

The matched-velocity point is K=delta_gamma*M. Its exact lower endpoint is0.
When K is close, subtraction of the two stored operands may be exact by
Sterbenz while their earlier rounding remains; therefore validation uses
absolute endpoint error relative to a physical total-energy scale, plus
explicit positivity/count/energy checks. It does not demand a relative error
bound with a zero or arbitrarily tiny denominator.

The independent high-precision reference takes the *same floating u,K,M inputs*
as exact real numbers, computes gamma=sqrt(1+u^2) at80digits, and integrates
the rest angular variable. It never infers u from a rounded producer gamma.

This update changes input parameterization and endpoint evaluation, not the
physical isotropy or event normalization assumptions. The other formulas use
G=u. For source rates the physical gamma remains sqrt(1+u^2); floating gamma
is evaluated by hypot.

EXECUTION: symbolic identity COMPLETE_SCOPED. PUBLICATION: PARENT_PENDING.
BACKUP: PARENT_PENDING. DAG: independent derivation -> u-parameterization
verified -> producer C9 numerical review pending.
