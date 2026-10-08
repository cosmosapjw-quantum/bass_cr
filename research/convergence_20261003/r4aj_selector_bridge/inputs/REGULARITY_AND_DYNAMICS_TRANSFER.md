# Strong-domain obstruction and a finite-metric dynamics comparison

**Derived; exact archived-coefficient checks completed.** The repaired reference
is a legitimate H¹ quadratic-form Galerkin reference. None of its five distinct
radial modes belongs to the full strong Coulomb operator domain. This does not
invalidate its finite weak Hamiltonian or previously proved selector map. It
invalidates substituting an L² strong residual for its weak residual. A separate
finite-matrix transfer theorem below supplies a valid route between the archived
and repaired coefficient evolutions without making that substitution.

The exact data are `EXACT_REGULARITY_OBSTRUCTION.json`; rational entries are
authoritative and decimal displays are explanatory. The input coefficient and
certificate identities are checked against the existing R4R certificate before
any calculation. No two-center operator query or physical propagation is used.
Physical equations below retain ħ and mass m. The saved basis numbers use the
project's existing atomic units. Set α=ħ²/(2m), and normalize Y_lm to unit angular
L² norm. Inner products are conjugate-linear in their first argument.

## 1. Why the repaired functions need not admit Hφ in L²

Let φ(x)=u(r)Y_lm(Ω)/r, with continuous piecewise-polynomial u, u(0)=u(a)=0,
zero-extended outside radius a. Write [u']_j=u'(r_j+)-u'(r_j−), including
[u']_a=−u'(a−). Across an internal shell the jump in normal derivative is
[u']_j Y_lm/r_j. Distributionally,

\[
 \Delta\phi=(\Delta\phi)_{\rm bulk}
       +\sum_j\frac{[u']_j}{r_j}Y_{lm}\,\delta(r-r_j).
\]

Here δ(r−r_j) is the surface delta distribution in the three-dimensional volume
measure: its action is the integral over the sphere. This formula follows from
twice integrating by parts in every cell; continuity removes derivative-of-delta
terms. Hence the kinetic strong residual contains −α[u']_jY_lmδ(r−r_j)/r_j.
A nonzero surface measure cannot be represented by an L² function. A Coulomb
multiplication potential has no shell delta and cannot cancel it. Subtracting
any finite linear combination of the basis functions cannot cancel it either.

The exact saved reference has the following nonzero derivative jumps. Counts
include its 39 internal interfaces and outer zero-extension interface:

| Radial mode | l | Nonzero derivative-jump shells | Maximum derivative jump magnitude (display only) |
|---|---:|---:|---:|
| 0 | 0 | 40 | 1.8189780828254246×10⁻⁵ |
| 1 | 0 | 40 | 4.221618248739683×10⁻⁶ |
| 2 | 0 | 40 | 3.880326074514229×10⁻² |
| 3 | 1 | 40 | 1.8273239782380669×10⁻⁶ |
| 4 | 1 | 40 | 4.914089269016828×10⁻² |

There is an additional origin obstruction in both l=1 modes. Their exact
u'(0) values are nonzero, with displays 4.602892015020259×10⁻¹⁰ and
9.234233657676864×10⁻¹¹. If u(r)=cr+O(r²), c≠0, then φ=cY_1m+O(r), which
is H¹ locally because its angular gradient scales as 1/r. Its centrifugal
Laplacian term instead scales as −l(l+1)cY_lm/r², whose squared L² radial
integral diverges like ∫₀ r⁻²dr. A Coulomb potential times φ scales only as 1/r
and cannot cancel that leading singularity. This is independent of the shell
obstruction. No point-value change at the origin repairs it.

The archived, unrepaired radial functions have nonzero value jumps in 39,40,40,
40,40 interfaces respectively. Their largest value jumps are approximately
1.588×10⁻¹⁴,1.071×10⁻¹⁴,5.052×10⁻¹⁵,9.603×10⁻¹⁵,7.661×10⁻¹⁵.
The discontinuities are tiny in amplitude but exactly nonzero under the saved
binary-rational interpretation. Thus those physical functions are not H¹.
The report's exact cellwise derivative-difference integrals are **broken radial
H¹ quantities**, not distances in the global H¹ space. Their smallness cannot
supply a global H¹ transfer assumption.

A translating jump also prevents strong L² differentiability of the archived
synthesis columns. Locally a displaced interface sweeps volume proportional to
|dt| and contributes |jump φ|² times that volume to the squared translation
difference. The difference quotient's L² norm grows as |dt|⁻¹/² whenever the
normal velocity is nonzero on a positive-area part of a nonzero jump shell.
The smooth ETF phase does not remove that jump. In particular, the old
cellwise connection must not silently be identified with F†Ḟ for a strongly
differentiable L² frame. Its finite-matrix metric compatibility needs its own
certificate.

## 2. Two exact counterexamples and the form-level alternative

Take the triangular function τ(x)=max(1−|x−1|,0). For every ε≠0,
ετ has H¹ norm squared (8/3)ε², but its distributional second derivative
contains nonzero Dirac masses. Thus arbitrarily small H¹ perturbations can
leave the strong operator domain. Even requiring smooth perturbations cannot
bound the strong residual by H¹ distance: on the 2π circle set

\[
 f_k(x)=k^{-3}\sin(k^2x)/\sqrt\pi.
\]

Then ||f_k||²=k⁻⁶, ||f'_k||²=k⁻², whereas
||−αf''_k||²=α²k². Hence ||f_k||_{H¹}→0 while ||Hf_k||₂→∞.
These counterexamples rule out the proposed type of implication, not every
possible dynamics comparison.

The Coulomb form itself remains continuous on V=H¹(R³). Introduce a fixed
length ℓ>0 and ||w||²_V=||w||²₂+ℓ²||∇w||²₂. For point Coulomb strengths
κ_j (energy×length), Hardy's three-dimensional inequality gives

\[
 |h(w,f)|\le\alpha\|\nabla w\|\|\nabla f\|
 +2\sum_j|\kappa_j|\min(\|\nabla w\|\|f\|,\|w\|\|\nabla f\|)
 \le C_h\|w\|_V\|f\|_V,
 \quad C_h=\alpha/\ell^2+2\sum_j|\kappa_j|/\ell.
\]

Consequently h(·,f) is in V*, even when Hf is not in L². If two synthesis
maps F₀,F₁: Cᵈ→V genuinely satisfy this common-domain assumption, then

\[
 \|H_1-H_0\|\le C_h\|F_1-F_0\|_{2\to V}
       (\|F_1\|_{2\to V}+\|F_0\|_{2\to V}).
\]

This follows by adding/subtracting h(F₁a,F₀b). It gives a computable form-matrix
comparison on a finite span. It does not apply to the literal archived frame,
which fails F₀:Cᵈ→V. The archived broken-form ODE can instead be compared as a
finite matrix model using the next theorem, provided its metric defect is kept.
No strong residual is needed.

## 3. Finite-metric transfer theorem

Fix a finite time interval [t₀,t₁]. For k=0,1, let S_k(t)>0 be C¹ Hermitian
matrices, H_k,D_k be continuous, and define

\[
 i\hbar S_k\dot c_k=(H_k-i\hbar D_k)c_k,\qquad
 L_k=-\frac{i}{\hbar}S_k^{-1}H_k-S_k^{-1}D_k.
\]

Allow numerical or model metric defects explicitly:

\[
 \Gamma_k=\dot S_k+L_k^\dagger S_k+S_kL_k
 =\dot S_k-D_k-D_k^\dagger
       +\frac{i}{\hbar}(H_k^\dagger-H_k),
 \quad
 a_k(t)\ge\max\{0,\tfrac12\lambda_{\max}
       (S_k^{-1/2}\Gamma_kS_k^{-1/2})\}.
\]

The right side is real since Γ_k is Hermitian. A convenient conservative
choice is a_k=||S_k⁻¹/²Γ_kS_k⁻¹/²||/2. Exact Hermitian form matrices and a
strongly differentiable conforming frame imply Γ_k=0. They are sufficient,
not silently presumed for the archived model.

Choose any C¹ coefficient comparison map T(t):C^{d₀}→C^{d₁}. Define

\[
 R=L_1T-TL_0-\dot T,\quad
 r(t)\ge\|S_1^{1/2}R S_0^{-1/2}\|,
 \quad e=c_1-Tc_0,\quad E=\|e\|_{S_1}.
\]

Then, with A_k(t,s)=∫ₛᵗa_k(τ)dτ,

\[
 \boxed{E(t)\le e^{A_1(t,t_0)}E(t_0)
   +\int_{t_0}^{t}e^{A_1(t,s)}r(s)\|c_0(s)\|_{S_0}\,ds},
 \qquad
 \|c_0(s)\|_{S_0}\le e^{A_0(s,t_0)}\|c_0(t_0)\|_{S_0}.
\]

Proof: differentiation gives ė=L₁e+Rc₀ and
(d/dt)E²=e†Γ₁e+2Re(e†S₁Rc₀). Cauchy–Schwarz yields
Ė≤a₁E+r||c₀||_{S₀}; regularize E by a positive ε at zeros and take ε→0.
Scalar variation of constants gives the formula. The same calculation with
R=0 gives the old norm bound. No exponential of ||H|| appears. A common scalar
energy shift cancels from L₁T−TL₀ exactly. A changing gauge must retain −Ṫ.

If both Γ vanish, the useful special case is simply
E(t)≤E(t₀)+||c₀(t₀)||_{S₀}∫r(s)ds. This is the finite-model state-transfer
bound that a same-state projector certificate alone cannot provide.

### A computable residual without differentiating a square root

Let K_k=H_k−iħD_k and

\[
 B=K_1T-S_1T S_0^{-1}K_0-i\hbar S_1\dot T.
\]

Then R=−iS₁⁻¹B/ħ, so
r=||S₁⁻¹/² B S₀⁻¹/²||/ħ. Certified lower metric bounds
S_k≥s_kI and interval enclosures for B give

\[
 r\le\frac{\|B\|_F}{\hbar\sqrt{s_1s_0}},
 \qquad
 a_k=\frac{\|\Gamma_k\|_F}{2s_k}\quad\text{is a sufficient choice}.
\]

For T=I, writing ΔK=K₁−K₀, ΔS=S₁−S₀,

\[
 B=\Delta K-\Delta S S_0^{-1}K_0,\qquad
 r\le\frac{\|\Delta H\|+\hbar\|\Delta D\|
 +\|\Delta S\|(\|H_0\|+\hbar\|D_0\|)/s_0}
 {\hbar\sqrt{s_1s_0}}.
\]

The direct B enclosure can retain cancellations that this norm-separated last
bound discards. This theorem compares finite ODEs; it does not certify that the
archived broken-form ODE approximates a full-space Coulomb evolution.

## 4. From coefficient comparison to a physical observable

Let F_k be L² synthesis maps with S_k=F_k†F_k, and define

\[
 \beta(t)=\|(F_1T-F_0)S_0^{-1/2}\|.
\]

Then for ψ_k=F_kc_k,
||ψ₁−ψ₀||₂≤E+β||c₀||_{S₀}. L² continuity is enough for this algebraic
embedding bound; the archived frame's H¹ failure does not invalidate it.
The difference Gram of F₁T−F₀ supplies β² through a generalized eigenvalue
bound or trace/metric bound. Complete channel multiplicities must be retained.

For orthogonal selectors Q₀,Q₁ with ||Q₁−Q₀||≤δ, and state distance ε,

\[
 |\langle\psi_1,Q_1\psi_1\rangle-
   \langle\psi_0,Q_0\psi_0\rangle|
 \le (\|\psi_1\|+\|\psi_0\|)\epsilon
       +\delta\|\psi_0\|^2.
\]

With equal conserved squared norms N this is 2√N ε+Nδ. If only
||ψ₀||=√N is known, use 2√N ε+ε²+Nδ. The earlier δ≤2.76856×10⁻¹⁴
can enter only after the distinct state-distance term is certified. Neither
that δ nor the present regularity computations instantiate ε for B0.

## 5. Inputs still required for an actual B0 transfer

1. Exact archived and reference context identities, physical time interval,
   common channel ordering and a specified T(t), including Ṫ and initial map.
2. Continuous-in-time lower bounds for both S matrices, enclosures of H,D,Ṡ
   or directly K,B,Γ, and their quadrature/rounding errors. Isolated static
   matrices or a finite time grid alone cannot supply interval suprema.
3. The archived finite ODE's metric defect, or a proof that its exact intended
   operator model has none; do not replace it by zero because its jumps are small.
4. A common-L² embedding difference Gram and initial coefficient mismatch.
5. A validated integral of r and, where nonzero, a₀,a₁. Add any saved-state
   temporal residual/error separately, within its qualified time window. The
   old N1536 temporal result applies only to the original ±12 interval.

`TRANSFER_INPUT_CONTRACT.json` records these requirements in machine-readable
form. Seven focused exact-algebra tests passed; the actual five-mode trace
analysis is separate deterministic Fraction computation. No previous suite was
rerun. The exact calculation establishes domain obstructions and a usable
comparison formula, while the actual state/dynamics bound remains **unresolved**.

`capture=false`, `production=HOLD`, `all_bound=OPEN`, `b_grid=NO_GO`,
`original_capture_gap_resolved=false`, `continuous_global_supremum_bound=false`,
and `continuous_trajectory_error_bound=false` are unchanged.
