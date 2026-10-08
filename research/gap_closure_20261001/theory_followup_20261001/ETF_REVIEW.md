# Independent review of the ETF continuum metric certificate

**Decision: accept within the named conforming-reference scope.** The oscillatory overlap proof and the saved exact rational certificate support

\[
\frac{33}{100}I\preceq S_{\rm cc}(R)\preceq\frac{167}{100}I,
\qquad \kappa_2(S_{\rm cc}(R))\le\frac{167}{33}
\]

for every center displacement, including coincident centers, when the relative ETF wavevector is \(v e_z\), \(v\ge2\). These are coordinates in which each center has been separately L2-orthonormalized. The theorem and certificate explicitly preserve this restriction. For saved raw coefficient coordinates, the correct congruence statement is \((33/100)M\preceq S_{\rm raw}\preceq(167/100)M\), with the block-diagonal one-center mass \(M\). Scalar raw-coordinate bounds and condition numbers require its eigenvalue factors.

## Mathematical review

For compactly supported \(H^1\) functions, \(\bar f g\in W^{1,1}\): both product derivatives are L1 by Cauchy–Schwarz. Integrating the derivative of \(e^{ivz}\bar f g\) over physical space therefore gives the displayed integration-by-parts identity. Applying this identity to every unit coefficient pair proves the **operator norm** bound \(\|C\|\le(L_{z,A}+L_{z,B})/|v|\). It is not merely an entrywise overlap estimate. Translation preserves the individual derivative norms, so arbitrary center displacement introduces no extra factor or separation derivative.

The reference repair previously reviewed makes the radial functions exactly C0, with zero exterior traces. The associated three-dimensional functions belong to H1, including at the origin. Piecewise derivative jumps do not invalidate the weak integration-by-parts identity. Literal archived trace jumps would introduce distributional interface terms and are not covered. The theorem expressly excludes that extension.

For each unboosted center, inversion parity makes the l=0/l=1 directional-derivative Gram cross block exactly zero. Within l=0, isotropy gives the full matrix identity \(G_z=G_{\nabla}/3\), including off-diagonal radial entries. On l=1, \(G_z\preceq G_{\nabla}\). The full-gradient radial Gram repeats over orthogonal magnetic sectors, so the preceding radial trace bound does not require an additional factor three. The declared complete s/p span and its mass normalization therefore justify \(L_z^2\le\max(\kappa_0/3,\kappa_1)\).

The saved rational values satisfy

\[
\max(\kappa_0/3,\kappa_1)
=0.448423966032211272\ldots<(67/100)^2.
\]

Thus \(\|C\|\le67/100\) for \(v\ge2\). The joint normalized Gram is \(\left(\begin{smallmatrix}I&C\\C^\dagger&I\end{smallmatrix}\right)\), which proves both eigenvalue endpoints and the condition bound. At zero relative phase, coincident equal center spans instead give \(C=I\); the author includes that negative edge, and the helper rejects nonpositive speed and noncoercive bounds.

## Source velocity and exact arithmetic

The inspected source uses \(\exp(i v_j\cdot x-i|v_j|^2t/2)\); the frozen worker assigns target velocity zero and projectile velocity \((0,0,v)\). Their relative phase is consequently \(e^{ivz_{\rm lab}}\) times a scalar time phase of unit modulus. No center-separation frequency was substituted.

The source-defined 100 keV/u speed is exactly the binary64 rational \(4521571391451241/2251799813685248\), hexadecimal `0x1.01058609d3069p+1`, or approximately 2.00798106651023. The saved constants also give an exact real squared-formula value strictly between 4 and 9. The source hashes and both speed inequalities were checked independently. This binds the declared source model; it does not introduce an experimental velocity uncertainty certificate.

One bounded saved-certificate consistency check used only Python standard-library Fraction arithmetic and hashing. It imported no author helper, reconstructed no physical operator, and ran no suite. It confirmed the exact directional comparison; all three Gram/condition fields; reference and gradient dependency hashes; four source pins; the velocity rational and hexadecimal value; and the updated scalar bridge formulas. All ten pre-ETF nonreport artifacts remain byte-identical, and the original report byte prefix is preserved.

The updated conservative reference bridge values are exactly

\[
G=3463/33,\qquad \int_{32}^{128}\rho\,dz/v\le55408/11.
\]

The integer square-root upper estimates used to obtain them are outward. These values remain far above the per-side target \(1/200000\); `target_certified=false` is correct.

## Review boundary

No unresolved defect was found within the declared theorem or certificate scope. Before final review, the author made the normalized coordinate convention explicit, added the raw congruence statement, and supplied all three exact Gram/condition fields. No historical certificate or result changed.

The two author tests were read with their saved passing log and matching source hashes; they were not rerun. No additional negative-edge execution was needed because the zero-phase failure is immediate and already covered. The Gaussian test is a valid smooth decaying H1 example of the same integration-by-parts bound; the production theorem uses the compactly supported repaired reference.

This review does not certify archived native Gram errors, adopt the reference model, compare archived and reference dynamical states, transfer temporal qualification, or close the finite-bridge accuracy target. Existing physical claim ceilings remain unchanged. New native calls, new physical operator queries, time propagations, and old-suite reruns: **zero**. The reviewer model alias is unresolved and is not guessed.

Exact reviewed-file hashes, dependency pins, and machine-readable scope are recorded in `ETF_REVIEW.json`. Earlier independent review artifacts were left unchanged.
