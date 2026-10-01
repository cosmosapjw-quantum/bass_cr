# G02 Richardson supplement — result-blind design

This optional offline supplement consumes the same four saved, independently
admitted overlap pairs as the frozen raw central-FD diagnostic. It makes no new
physical calls. It does not change the original relative target `1e-6`, absolute
target `1e-12`, visible second-order criterion, or their PASS/FAIL outcome.
The production/capture/all-bound/b-grid claim ceilings remain HOLD/false/OPEN/NO_GO.

For `h = (0.4, 0.2, 0.1, 0.05) a0`, define

\[
T_{0,i}=v\frac{S(z+h_i)-S(z-h_i)}{2h_i},\qquad
T_{j,i}=\frac{4^jT_{j-1,i+1}-T_{j-1,i}}{4^j-1}.
\]

Under a sufficiently smooth even-power truncation expansion, the four layers
have formal orders R2/R4/R6/R8. They contain four/three/two/one estimates.
The final R8 weights acting on the four central differences are
`(-1/2835, 4/135, -64/135, 4096/2835)`; their sum is one.
These coefficients are fixed independently of analytic D and observed results.
Neither D, its disagreement, nor a fitted wave number enters construction.

The analytic comparator is `D + D†`, because `z = v t`. The report provides
spectral, Frobenius and elementwise absolute differences and relative scales.
It also reports successive differences and their contraction within each
Richardson layer independently of D. Only R2 and R4 have enough rows to form
contraction ratios. R8 has just one estimate: this ladder cannot empirically
establish eighth-order convergence. Zero differences yield undefined (`null`)
orders, not evidence of infinite order or certification.

For the analytic example `f(z) = exp(i k z)`, the central difference divided by
the exact derivative is `sin(kh)/(kh) = 1 - (kh)^2/6 + O((kh)^4)`.
Consequently, a raw final-step relative target can fail purely because of
truncation while the underlying derivative identity is exact. At `k = 1/a0`
and `h = 0.05 a0`, the relative discrepancy is about `4.17e-4`, exceeding
`1e-6`. This example is a mechanism, not an inferred wave number or diagnosis
for the physical overlap. A reliable result must distinguish these possibilities:

- Raw O(h²) error followed by much smaller extrapolated disagreement is
  consistent with dominant central-stencil truncation.
- Independent estimate differences contracting while disagreement with D
  plateaus is consistent with a nonvanishing discrepancy, but quadrature and
  finite arithmetic must also be considered before blaming analytic D.
- No contraction, or differences at the numerical sensitivity scale, does not
  support an asymptotic inference from these four steps.

The central-difference coefficient L1 norm describes amplification of errors
already present in those four derivatives. The signed sample coefficient L1
norm is `sum_i |w_i| v/h_i` and describes amplification of uniformly bounded
absolute errors in the eight overlap samples. The report also evaluates

\[
\epsilon_{64}\sum_i |w_i|\frac{v}{2h_i}
\bigl(\|S(z-h_i)\|+\|S(z+h_i)\|\bigr).
\]

This last quantity is explicitly a **heuristic** unit-epsilon relative sample
perturbation surrogate. Saved physical overlaps are not known to have only
unit-epsilon errors. This expression excludes uncertain quadrature error,
analytic-D error, coordinate effects, and a complete rounding analysis of the
arithmetic. It is not a rigorous bound or a new tolerance. Qualification's
adjacent-resolution agreement is not silently reinterpreted as an absolute
sample-error bound.

Integration: after the existing source/context/cache loader admits arrays,
call `analyze_ladder(D_center, [(h, S_minus, S_plus), ...], velocity)` and save
the returned JSON as a separate supplement. Preserve the original raw report.
The caller must bind this module's bytes and document whether the supplement
was frozen before physical results became available. This module itself does
not attest that chronology or verify cache provenance.

Synthetic tests check degree-0..8 polynomial differentiation, complex
oscillatory orders, analytic-D independence, coefficients, central sinc ratio,
finite-input rejection, and explicit unchanged claim flags. These tests verify
the offline diagnostic only; they do not provide physical G02 evidence.
