# ETF oscillation removes the tiny-metric obstruction

For the exact conforming reference already certified in the sibling folder,
the relative electron-translation factor supplies a uniform metric bound

\[
\boxed{\frac{33}{100}I\preceq S_{\rm cc}(t)
\preceq\frac{167}{100}I,\qquad
\kappa_2(S_{\rm cc})\le\frac{167}{33}.}
\tag{1}
\]

This holds at **every center displacement**, including coincident centers, for
the stated relative ETF speed v≥2 atomic units. S_cc denotes independently
orthonormalized one-center coordinates. It replaces the tiny exclusive-cap
metric lower bound as the useful reference bound; the earlier cap certificate
remains mathematically valid and unchanged.

The frozen source speed for the declared 100 keV/u model is
2.00798106651023, exactly 4521571391451241/2251799813685248 as binary64.
The input certificate binds that value, its source code/constants and the exact
reference polynomial hash. No new native operator was called. This remains a
statement about the named exact reference, not an error bound for archived
native matrices or a change to the accepted model.

## 1. The source supplies a relative spatial phase

`two_center.py:basis_values` uses

\[
\chi_j(x,t)=e^{i v_j\cdot x-i|v_j|^2t/2}\,
\phi_j(x-R_j(t)).
\]

The frozen worker builds a stationary target and a projectile with velocity
(0,0,v). Therefore the target/projectile cross Gram is, up to an irrelevant
time-dependent scalar phase,

\[
C=U_A^\dagger M_v U_B,\qquad (M_v f)(x)=e^{ivz_{\rm lab}}f(x).
\]

Here U_A and U_B are the separately normalized unboosted one-center basis maps,
so U_A†U_A=U_B†U_B=I. Their translations can be arbitrary. The derivative below
is along the **laboratory coordinate** of the relative wavevector, not a
derivative with respect to center separation.

## 2. Integration by parts bounds the entire cross block

For compactly supported H1 functions f,g, the product conj(f)g lies in W1,1.
Its integral derivative vanishes. Thus

\[
iv\langle f,M_vg\rangle
=-\langle\partial_z f,M_vg\rangle
 -\langle f,M_v\partial_zg\rangle.
\]

This can alternatively be proved first for smooth compact functions and passed
to the H1 limit. No omitted FEM interface boundary terms occur for the exact
conforming reference. The literal old bank with nonzero trace jumps would need
explicit jump terms, so it is not silently covered by this proof.

In matrix/operator form,

\[
ivC=-(\partial_zU_A)^\dagger M_vU_B
      -U_A^\dagger M_v(\partial_zU_B),
\qquad
\boxed{\|C\|\le\frac{L_{z,A}+L_{z,B}}{|v|}.}
\tag{2}
\]

The norms of U_A,U_B and M_v are one. Translation leaves each L_z unchanged;
the bound is consequently uniform over all center displacements. It would
fail to prove positive definiteness if the right side were at least one.
In particular, at v=0 coincident identical center spans have C=I and singular
combined Gram. The relative ETF phase is essential here.

These numerical endpoints are not raw-coefficient Gram endpoints. If M is the
block-diagonal one-center mass in the saved coefficient coordinates, congruence
gives (33/100)M <= S_raw <= (167/100)M. Thus scalar raw-coordinate endpoints must
also include certified one-center minimum and maximum mass eigenvalues.

## 3. Parity and s-wave isotropy sharpen the directional derivative

The unboosted l=0 radial functions are even under inversion about their own
center, and l=1 functions are odd. Their directional derivatives have opposite
parities. Hence every l=0/l=1 cross entry of the derivative Gram vanishes
exactly. The one-center mass also separates those two l blocks.

For two l=0 functions, radial symmetry gives

\[
\langle\partial_z f_i,\partial_z f_j\rangle
=\frac13\langle\nabla f_i,\nabla f_j\rangle,
\]

since the angular average of cos²(theta) is 1/3. For the l=1 block,
the directional derivative quadratic form is bounded by the full gradient
form. These facts survive exact one-center orthonormalization, which acts
within the corresponding l blocks. Therefore

\[
L_z^2\le\max\{\kappa_0/3,\kappa_1\}.
\tag{3}
\]

The earlier exact rational gradient certificate gives the following
non-authoritative decimal displays:

\[
\kappa_0\le1.34527189809663382,\qquad
\kappa_1\le0.4434317514\ldots,
\]

and exact rational comparison proves

\[
\max\{\kappa_0/3,\kappa_1\}
\le0.448423966032211272\ldots
<\left(\frac{67}{100}\right)^2.
\]

Thus L_z≤67/100 for each center. With v≥2, (2) gives ||C||≤67/100.
Finally,

\[
S_{\rm cc}=\begin{pmatrix}I&C\\C^\dagger&I\end{pmatrix},
\qquad
(1-\|C\|)I\preceq S_{\rm cc}\preceq(1+\|C\|)I,
\]

which proves (1), including the condition-number bound. The s/p parity and
complete declared one-center span are part of the certificate scope; the helper
does not infer them from arbitrary matrices.

## 4. Exact velocity binding and remaining accuracy issue

The source function uses sqrt(2*(1000*E/HARTREE_EV)/U_OVER_ME). The helper reads
the source constants as their exact binary rationals and proves its real-valued
squared formula at E=100 lies strictly between 4 and 9. It separately evaluates
the existing scalar arithmetic, records the resulting binary64 hexadecimal
value `0x1.01058609d3069p+1`, and verifies that value lies in [2,3]. This is a
scalar source-binding check, not a physical operator evaluation.

The earlier Hardy bridge formula can now use s0=33/100 and v in [2,3]. Keeping
its other deliberately coarse estimates unchanged gives exact bounds

\[
\rho\le\frac{3463}{33}\simeq104.9394,
\qquad
\int_{32}^{128}\rho\,{dz\over v}
\le\frac{55408}{11}\simeq5037.0909.
\]

This improves the previous conservative 6.27×10^57 bridge bound by many orders
of magnitude. It still does not certify 5×10^-6 per side; even the trivial
probability-difference cap of one exceeds the target. The remaining obstacle
is the loss of Hamiltonian/connection/monopole cancellation in the coarse rate
estimate, rather than the absence of a useful uniform reference metric bound.
No further optimization was performed in this bounded follow-up.

Existing cap certificates, helper code and four tests are preserved byte for
byte, with their old hashes in `ETF_PRIOR_ARTIFACT_HASHES.json`. Two new focused
tests pass: exact bound admission/rejection and an independently integrated
Gaussian ETF cross-Gram example including the zero-phase singularity. The old
tests were not rerun. No model adoption, native matrix-error certification or
archived-to-reference dynamical transfer is claimed.
