# R3 Definitions and claim alignment

Let I be a finite index set, E_i>=0 exact energies in eV and w_i>=0 exact electron-leg masses. The pure core accepts arbitrary finite nonnegative energies; the PHYS02 adapter restricts these to the independently pinned native atoms, including its exact binary64 cutoff. Let K>=0 be an explicit exact conditional cap. A single uses one leg. An unordered double (i,j) consumes one leg of each distinct atom, or two legs of i when i=j. Doubles are permitted precisely when E_i+E_j<=K. No cross-bin rectangle approximation is made.

Write N=sum_i w_i; L={i:2E_i<=K}; H=I\L; their masses are also denoted Lmass,Hmass. Distinct high energy levels h run in descending order. Define B(h)=sum_{i in H,E_i>=h}w_i and A(h)=sum_{i in L,E_i<=K-h}w_i. Set delta=max({0} union {B(h)-A(h)}). Equal-energy high atoms are included together in B(h), and equality is included in A(h).

The target is the maximum internal double mass d over nonnegative double measures whose incidence is at most w. Remaining legs become singles, so the complete saved marginal is preserved exactly. Its candidate value is dmax=(N-delta)/2. The general algebraic attainable interval is [0,dmax]. This objective differs from cross-partition duplicate C. A reported C belongs to its constructed witness; no energy-support max-C theorem is claimed.

The kernel uses coefficient masses [m^-3 s^-2] for actual PHYS02. The original consumer applies W=(b^2-a^2)/2 [s^2] once on proper0<=a<b<=1e10s. Full selected-support witnesses have p=0, s=N-2d, nu=N-d. Partial selections use the original general p/d bookkeeping. Actual K, exclusive source measure, source uncertainty and physical completion remain input-gated.

The same-state native consumer additionally requires W(N-d)<=Hneutral, Hneutral=(1085/94)*(99/100) m^-3. For W>0 its admissible d interval is [max(0,N-Hneutral/W),dmax], provided the lower endpoint does not exceed dmax. This is a consumer inventory constraint; it does not alter the preceding algebraic theorem. The existing consumer rejects a depleted inventory.

State/nb/isotope/frame/time/support/source bytes and source normalization retain the exact prior binding. No additional target, clock, angle, volume, projectile-speed or729 factor is inserted. Source/RR/photon remain once-only ports.
