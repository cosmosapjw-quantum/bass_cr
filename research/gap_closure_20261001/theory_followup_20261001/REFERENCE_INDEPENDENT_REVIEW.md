# Independent review of the R4R conforming-reference certificate

**Accepted for the named finite, nine-channel, weak-Galerkin reference and the
same-state projector comparison.** The bound is supported by exact rational
mass integrals, rigorously enclosed Coulomb-form integrals, certified block
separation and an equal-rank projector argument. No unresolved mathematical or
implementation defect was found in this scope.

The authoritative inequality is

\[
 \|Q_{\mathrm{archived\ selected}}-E_{\mathrm{reference},-}\|
 \le 2.76856\times10^{-14}.
\]

Here E is the negative spectral projector of the **finite compressed reference
operator**. It is not the negative spectral projector of the full Coulomb
Hamiltonian. The inequality compares exact Hilbert-space observables on the
same state; it does not by itself bound an archived numerical population,
Hamiltonian error, a newly evolved state, or a trajectory difference.

The review used only the new `reference_certificate_followup_20261001/` source,
proof and saved certificate artifacts. Input pin agreement between the saved
certificate and execution receipt was inspected; raw `BASIS` files outside
that directory were not reread. Their canonical archive binding remains the
root agent's provenance check. The model alias remains unresolved and was not
guessed.

## Mathematical checks

The linear endpoint correction gives exactly matching internal traces and zero
traces at 0 and 64. Piecewise polynomials with those properties lie in
H¹₀(0,64). Near the origin each repaired u is O(r), so u²/r and u²/r² are
integrable. With normalized spherical harmonics, u(r)Y_lm/r has finite H¹
energy and zero outer trace. Strong-operator-domain membership or pointwise
smoothness at the origin is unnecessary and is not asserted. Derivative jumps
at element interfaces and the outer zero extension preclude interpreting the
small compressed residual as a strong full-space Schrödinger residual.

Local mass and derivative products are rational polynomial integrals. Exact
conversion from local t to global r coordinates correctly accounts for cell
widths and derivative factors. Coulomb and centrifugal integrals contain only
rational primitives and logarithms. At the first cell, the zero constant term
makes potentially singular product coefficients exactly zero; the implementation
rejects nonzero singular origin terms rather than discarding them.

The atanh-series logarithm bound is sound: after 128 terms the remaining power
is z²⁵⁷, with tail bounded by `2*z**257/(257*(1-z*z))` for 0≤z≤1/3. Exact
powers-of-two range reduction also handles negative integer exponents correctly.
Interval operations use outward rounding only; exact rational point intervals
remain exact. The integer-square-root construction encloses the positive square
root without floating-point arithmetic. Decimal display fields are explicitly
non-authoritative; the seven simple summary bounds are exact conservative
rationals.

The complementary coordinates X=S_AA⁻¹S_AB and Z=(-X,I) give exactly
S-orthogonal selected and complementary spaces and the correct Schur metric K.
The implemented complementary Hamiltonian and residual expressions have the
correct cross-term signs. Gershgorin bounds enclose the actual symmetric form
matrices; dividing by the Gram upper bounds gives the negative and positive
generalized sign margins. The residual's Frobenius bound, divided by the two
Gram lower bounds, validly bounds the normalized coupling.

Min-max gives exactly five negative and four positive angular eigenvalues, with
the stated gap. The Sylvester integral then bounds leakage by r/(a+d).
Equal finite ranks justify converting this leakage to the operator norm of the
projector difference. The l=1 sectors are repeated orthogonal copies: their
norm is a maximum, not a sum. Thus neither the radial residual bound nor the
repair-map bound is missing an angular multiplicity factor.

For the archived-to-repaired comparison, both selected synthesis maps have rank
five. The one-sided gap is bounded by the repair synthesis norm divided by the
square root of the original selected Gram eigenvalue lower bound. Equal ranks again
identify it with the projector norm. The angular block trace bound and final
triangle inequality are valid. No small-difference Hamiltonian or state-map
assumption is smuggled into this projector comparison.

## Finding and focused evidence

One exposition error was found and corrected by the author before this review
was frozen. Section 3 originally wrote the squared upper bound in the wrong
direction. The corrected statement is

\[
 \|R\|^2\le
 \frac{\sum_{ij}|(R_0)_{ij}|_{\rm interval}^2}{s_-k_-}
 \le r_{\rm upper}^2.
\]

The implementation and saved numerical certificate already used the correct
upper square-root endpoint; neither changed.

One bounded exact-arithmetic discriminator was run, motivated by that finding.
It independently checked saved reference/selector identities, all 39 internal
interfaces per radial mode and external traces, and reconstructed the complete
5×5 radial mass matrix from local monomial integrals. It also checked the
residual and repair square-root bound directions, projector-sum formula,
angular ranks 5/4 and all seven outward summary inequalities. Every check
passed. The source hash matches the actual execution receipt.

The author's saved log records nine passing focused tests; these were read,
not rerun. The prior 114-test suite, the actual certificate construction and
native calculations were not rerun. New native calls, two-center queries,
propagations and authorizations consumed by this review are all zero.

The source, proof, certificate and summary identities are pinned in the paired
JSON review. The reference remains unadopted. Finite bridge/tail control,
state/dynamics comparison, original fixed-selector limit existence and the
capture/production/all-bound/b-grid gates remain outside this certificate.
