# R6 analytic edge cases

These are closed-form review checks, without numerical execution.

## Scalar resolvent check

For scalar K=k>0 and w,r≥0, p∞=wr/k and F(T)=p∞(1−exp(−kT)). Summing the resolvent geometric series gives

A_m(γ)=Σ(j=0,…,m−1) wr γ^j/(k+γ)^(j+1)
=p∞[1−(γ/(k+γ))^m].

Independently, the Erlang Laplace transform is E exp(−kS)=(γ/(k+γ))^m, so this equals E F(S). It checks the recurrence's initial power, factor γ and number of summands. No factorial remains in the final resolvent sum.

## M-matrix is not a unit-probability premise

Let K=[[1,−2],[0,1]], w=(1,0)ᵀ and r=(0,1)ᵀ. K is a nonsingular M-matrix, with witness v=(3,1)ᵀ and Kv=(1,1)ᵀ>0. The semigroup is exp(−Kt)=exp(−t)[[1,2t],[0,1]]. Therefore F(T)=2[1−(1+T)exp(−T)] and p∞=2. All positivity premises of the proposed bracket hold, while p∞≤1 fails. This verifies the need for the p∞ cap and for distinct probability/normalized-count language.

## Limits and non-executed outputs

T=0 gives F=0 without evaluating γ=m/T. A zero pulse or zero reward gives F=A=p∞=0. A zero-width conditional energy denominator gives a null ratio rather than a fabricated zero conditional mean. Fixed δ with m→∞ leaves clocks concentrated at T/(1±δ); convergence specifically to T requires a shrinking δ sequence with mδ²→∞. An interval that remains wide is still an enclosure and must be reported at its actual width.
