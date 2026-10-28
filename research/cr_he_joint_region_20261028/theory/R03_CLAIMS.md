# R3 — Quantifiers, source conventions and claims

## Finite event model

For a finite set I, each atom has a distinct key, nonnegative rational mass a_i, nonnegative rational energy E_i and integer birth-bin label b_i. K is a nonnegative rational parameter, not an inferred physical input. Positive-mass atoms define the effective graph. Zero-mass atoms remain harmless entries in the marginal vector.

An event measure consists of single coefficients s_i and unordered double coefficients p_ij (i<=j), all nonnegative real numbers for the polytope statement. Rational construction and implementation realize its rational points. Off-diagonal p_ij is permitted precisely when E_i+E_j<=K; a diagonal p_ii requires 2E_i<=K. Every such pair is available; no additional masking, integer-particle indivisibility or exclusion rule is imposed. The exact marginal equations are

    a_i = s_i + 2 p_ii + sum_{j != i} p_min(i,j),max(i,j).

Define N=sum a_i, d=sum_{i<=j}p_ij, and C=sum_{i<j,b_i!=b_j}p_ij. These are coefficient masses in the same units as a_i. A double event contributes one to d and two to the electron marginal. Cross-bin means unequal labels; spatial position, charge or symmetry labels are not substituted for birth bins.

Set Lset={i:2E_i<=K}, Hset={i:2E_i>K}, and L=sum_{Lset}a_i. No high-high double is allowed, while every low-low pair and every low diagonal is allowed. The additional domain assumption is:

    for all a_l>0,a_h>0 with l in Lset,h in Hset and E_l+E_h<=K,
    b_l != b_h.

This is tested from actual atom data. Calling a cap a bin boundary does not itself discharge the condition. Define M as the maximum capacity-limited bipartite high-low matching mass. Define X as the maximum cross-bin double mass over the full permitted cross graph. The feasible sets are finite-dimensional closed bounded polytopes, so both optima exist; finite rational input permits rational maximizing vertices. D=(L+M)/2 is the exact d maximum proved and certified by PR114 for the present energy graph.

## Claims and obligations

J1, to prove: under the assumptions above the exact projection is

    0<=d<=D, 0<=C<=X, C<=d, 2d-C<=L.

J2, to prove constructively: the two individual maxima D and X have a common event witness. Every rational point of J1 admits a rational marginal-preserving event measure. Duplicated vertices at M=0, X=0, X=M or X=D must not lead to division by zero.

J3, derived physical map: in the unchanged fully selected p=0 source-return convention, this projection determines the joint attainable source-parent and cross-bin chemical correction returns. It does not identify the actual exclusive event measure.

J4, coding obligation: evaluate the support predicate for the 3201 original atoms, recover PR114/115 exact bounds by identity, construct native vertex/interior measures, and verify both pair support and the complete atom marginals before using the unchanged consumer. The expected valid and invalid native caps listed in CONTRACT are test targets, not already asserted fresh computational results.

The restricted theorem is a sufficient domain theorem. Failure of its predicate means OUTSIDE_DECLARED_DOMAIN; it is not proof that its polygon fails for every such dataset. An explicit counterexample can refute an unrestricted extension, without being a universal physical no-go.

## Physical-variable correspondence

With all source atoms selected, there are no partially selected doubles (p=0 in the original consumer). Since N=s+2d, the source coefficient vector for (He0,He+,He++) is (-N+d,N-2d,d), the number of source parents is N-d, and ionic charge is N. Chemical energy in this convention is

    U_union = I1*N + (I2-I1)*d,
    U_partition_sum = U_union + (I1+I2)*C,
    Delta U = -(I1+I2)*C = -79.01 eV*C.

Here I1=24.59 eV, I2=54.42 eV are the pinned consumer constants. The correction to the partition-summed ion vector is (C,0,-C), and its charge correction is -2C. The final union charge remains N; a correction to duplicated partition claims is not a removal of actual emitted electrons.

For q_i(t)=t*a_i on the bound proper-time interval, W=integral t dt is applied once. Densities equal coefficient expressions times W, native abundance changes equal those densities divided once by nb=8750/47 m^-3. Energies E_i and K are eV, a_i are m^-3 s^-2, and W has s^2. Per-volume recipient chemical return is therefore eV m^-3. No absolute volume is required or inferred.

The neutral-He source inventory requires W*(N-d)<=n_He0, hence d>=max(0,N-n_He0/W) for W>0. Intersect the mathematical polygon with this d>=d_min half-space; the intersection is empty when the lower bound exceeds D. The original source consumer performs its own same-state inventory check. W=0 is handled without division. Kinetic source energy is W*sum E_i*a_i and is unchanged by pairing. Saved RR and retained-photon contributions attach once according to their own contracts.

The general partial-selection formula contains I2*p in addition to I1*N+(I2-I1)*d, where selected N=s+p+2d, and its ionic charge is N+p. Its correction uses only cross events with both legs selected. Applying the p=0 expression or the global C to a partial selection would be a scientific error. The consumer's inventory check is per call; previous_windows prevents overlap but is not a cumulative inventory-depletion solver. This unit uses the single bound full window. Actual K, exclusive He kernel, outside partners, donor work, EOS/temperature and physical native25 remain open inputs and are not promoted by these coefficient identities.
