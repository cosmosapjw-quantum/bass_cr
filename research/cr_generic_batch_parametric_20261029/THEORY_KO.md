# CR_GENERIC_BATCH_PARAMETRIC_V1: one-pass exact budget frontier

Authority: `cosmosapjw-quantum/bass_cr` PR122 HEAD `f152e28fd4e9a727b23e068603c0359c5e0d1303`, parent PR121. New scope is a finite conditional event-allocation optimization. No claim of physical exclusive He recombination rate, physical K, clock, stopping, donor or partner energy ownership. Original NPZ bytes are immutable.

## Definitions and conservation

Let H and L be disjoint finite atom classes, defined by 2E_h>K and 2E_l<=K, with exact rational E_i in eV and capacity w_i>=0 in m^-3 s^-2. HL arc (h,l) is admissible iff E_h+E_l<=K, with cost chi_hl=1 if birth bins differ and 0 otherwise. Each nonnegative fractional event mass x_hl consumes one unit of both endpoint marginal masses. Set m=sum x and C=sum chi*x, and impose sum_l x_hl<=w_h, sum_h x_hl<=w_l, C<=c. Let Ltot=sum_l w_l. Every unused low mass can enter its allowed diagonal low-low event at half its residual marginal mass. Therefore

  dmax(c)=(Ltot+M(c))/2,  M(c)=max {sum x: x feasible and C<=c}.

All event masses and c have the same dimensions as w_i; K stays an energy in eV. This is not a rate until a genuine physical event kernel/clock/normalization is bound.

## Single-trajectory parametric theorem (derived)

For 0<=m<=M_infinity set C_min(m)=min C among feasible x with sum x=m. Finite fractional network-flow LP duality shows C_min is nondecreasing, convex, continuous and piecewise linear; its exact SSP residual shortest s-t path slopes k are nonnegative integers (0/1 forward costs and 0/-1 reverse costs). Each exact augmentation delta along a residual path of marginal cost k traces an affine optimum segment from (m_j,C_j) to (m_j+delta,C_j+k delta). If k>0 then all query budgets c in [C_j,C_j+k delta] have

  M(c)=m_j+(c-C_j)/k,  lambda=1/k.

To derive the equality, note that the primal candidate is the feasible fractional residual augmentation of size (c-C_j)/k. For an optimal C_min trajectory, a residual potential with no negative cycle for the circulation arc t->s of cost -k gives the matching LP dual. Equivalently the original graph admits nonnegative vertex prices ph,pl such that

  ph+pl+chi_hl >= k for all admissible (h,l),
  sum_h w_h ph + sum_l w_l pl + c = k M(c).

Dividing by k returns the ordinary budgeted dual:

  min_{p>=0,lambda>=0} sum_i w_i p_i+c lambda,
  p_h+p_l+lambda chi_hl>=1.

The integer-scaled C++ construction verifies the stronger integer numerator form and a Python Fraction consumer independently checks every original admissible edge, including zero-capacity vertices. At c=0, the algorithm first follows all k=0 augmentations, then emits the first positive-slope witness; if no positive path remains, the terminal mincut certifies all requested c. At exact kinks either adjacent supporting slope gives a valid dual. For c at/above saturation, lambda=0 and a maximum-flow mincut dual is used.

## Batch computational form

Sort Q exact budgets without changing user-visible query order. Perform ONE SSP path traversal only until the largest requested c or flow saturation. For each positive-cost augmentation interval emit every query within it, using its exact rational fractional path endpoint before mutating the residual. Continue the augmentation only if higher budgets remain. Identical or nonmonotone input budgets are handled by stable indexed ordering. Each query receives its own original-graph primal/dual witness. The cost to compute paths is O(A*(E+V)log V) with A the augmentations needed for largest query, ignoring exact arithmetic bit complexity. Certificate output and independently checking Q full witnesses adds O(Q*(E+V)) plus Python original-edge checks; the residual dual extractor can have worse theoretical complexity. This is not a strong-polynomial or general cost-scaling guarantee, and full sparse witness output grows with Q.

The new finite signed-i128 implementation requires a common scale S=lcm(denominators of all w_i and c_j). It checks maximum exact scaled mass bit length <=105, refuses >128 budget queries, and preserves exact Fraction output including non-dyadic fractional path interpolation. The original source has a dyadic denominator at most 2^185 but scaled masses are far smaller. Integer scaling is a representation change, not a change in event units or source rates.

## Fixed-C joint region remains separate

The max frontier M(c) for C<=c is not the set of all attainable (d,C) when C is fixed. Low-low cross-bin events can consume a C budget without affecting high-low m, so neither budget monotonicity nor M(c) determines that full joint polygon. No fixed-C solver claim is made.

## Evidence and limitations

- Wolfram exact 18-edge LP seven budgets (0,1,3/2,2,5/2,3,4) yields (5,6,13/2,27/4,7,43/6,15/2), exact equality.
- Python `unittest`: six methods normal and six methods `-O`, 75 seeded full-event exact LP oracles, multikink and negative controls.
- Original 3201-atom NPZ three budget witnesses exactly equal PR121/122 original native rational values, 102831 original edge inequalities each, gap=0.
- Matched 120-atom, five-bin synthetic benchmark, eight budgets, three paired repetitions: median batch 0.04909 sec vs repeated PR122 0.18290 sec (ratio 3.7258), same machine/compiler flags/outputs/certificates. Path augmentation 84 vs sum of repeated 610. No claim this ratio carries to original 3201 or physical production.
- A one-shot rerun of PR122 original 3201 batch baseline hit an execution timeout with no valid final record; no matched 3201 speedup is certified.

## Literature boundaries

- Kiraly & Kovacs (2012), *Efficient implementations of minimum-cost flow algorithms*, https://arxiv.org/abs/1207.6381, prior art SSP, residual potentials, cost-scaling and network simplex.
- Kovacs (2015), *Minimum-cost flow algorithms: an experimental evaluation*, https://doi.org/10.1080/10556788.2014.895828, empirical cost-scaling/network-simplex landscape. Neither general MCF theory nor SSP is claimed novel.
- Switzer & Hirata (2008), *Primordial helium recombination II*, https://arxiv.org/abs/astro-ph/0702144, physics of two-photon processes; a literature candidate, not yet source-qualified as this project's exclusive event-pair kernel.
