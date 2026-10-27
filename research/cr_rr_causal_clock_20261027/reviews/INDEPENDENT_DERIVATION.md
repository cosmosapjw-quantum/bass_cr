# R6 independent derivation before candidate inspection

This derivation follows the requested mathematical problem without reading `theory_candidate/THEORY_KO.md` or `FORMULA_CONTRACT.json`. It is a review calculation on paper, not a new numerical science run. The current CR and central refs/AGENTS were rechecked in `R6_START_PREFLIGHT.json` at 2026-10-27 06:08:52–53 UTC; both match their frozen inputs.

## 1. Positivity and the deterministic cumulative response

Let the exact mathematical matrix K be the matrix whose entries are the stored finite binary64 numbers interpreted as exact real numbers. Assume K is a real nonsingular M-matrix, w and r are componentwise nonnegative, and all dimensions are finite. In particular, K is a Z-matrix and every eigenvalue has strictly positive real part. Therefore exp(−Kt) and K⁻¹ are componentwise nonnegative, and exp(−Kt) tends to zero.

Define h(T)=∫₀ᵀexp(−Kt)r dt and F(T)=wᵀh(T). Then F(0)=0, F′(T)=wᵀexp(−KT)r≥0, and p∞=lim F(T)=wᵀK⁻¹r is finite. Hence 0≤F(T)≤p∞ for every T≥0. No row-sum, column-sum or substochastic condition is used. In particular, p∞≤1 is not implied. A response can be normalized or interpreted as a probability only if its additional probabilistic conservation/normalization conditions have been separately established. All bounds here use p∞, not a silently inserted unit cap.

For T=0 the deterministic response is exactly zero; formulas involving m/T are not evaluated. If w=0 or r=0, F and p∞ vanish and the zero case is exact.

## 2. Erlang expectation and resolvent recurrence

For integer m≥1 and rate γ>0, let S have an Erlang distribution with shape m and rate γ. Its survival function is P(S>t)=exp(−γt)Σ(j=0,…,m−1)(γt)^j/j!. Tonelli applies to the nonnegative integrand. Thus

E[F(S)] = ∫₀∞ wᵀexp(−Kt)r P(S>t) dt

= Σ(j=0,…,m−1) γ^j wᵀ(K+γI)⁻(j+1)r.

The matrix Laplace integral follows either by differentiating the resolvent in γ or by successive integration by parts; finite-dimensional exponential stability gives the necessary vanishing boundary terms. Symmetry and diagonalizability are not needed.

For B=K+γI, define y₀=B⁻¹r and yⱼ=γB⁻¹yⱼ₋₁ for j≥1. Then A_m(γ)=Σwᵀyⱼ=E[F(S)]. These vectors and scalar summands are nonnegative. The recurrence includes γ in every j≥1 right-hand side. With K and r in s⁻¹, γ is s⁻¹ and yⱼ is dimensionless; w determines the final count/normalization units. An energy reward r_E in J s⁻¹ produces energy rather than event count without changing the proof.

## 3. Independent Chernoff tail check

Fix T>0 and 0<δ<1. For the lower-mean clock, γ₋=m(1+δ)/T and E[S₋]=T/(1+δ). Applying the gamma MGF at the optimizing positive tilt gives

P(S₋>T)≤q₋=exp(m[log(1+δ)−δ]).

For the upper-mean clock, γ₊=m(1−δ)/T and E[S₊]=T/(1−δ). The negative tilt gives

P(S₊<T)≤q₊=exp(m[log(1−δ)+δ]).

Both q values are strictly between zero and one. The lower sign labels the clock's mean, not the sign of its rate change.

Write A₋=E[F(S₋)] and A₊=E[F(S₊)]. Monotonicity yields

A₋≤F(T)P(S₋≤T)+p∞P(S₋>T)

≤F(T)+(p∞−F(T))q₋.

Therefore F(T)≥(A₋−p∞q₋)/(1−q₋). Separately,

A₊≥F(T)P(S₊≥T)≥F(T)(1−q₊),

so F(T)≤A₊/(1−q₊). Combined with 0≤F≤p∞ this proves the requested closed bracket:

max(0,(A₋−p∞q₋)/(1−q₋)) ≤ F(T) ≤ min(p∞,A₊/(1−q₊)).

The first denominator is essential to the sharper lower bound. The first derivation uses the fact p∞−F(T)≥0 when replacing the actual tail probability by q₋. This is why a signed reward cannot be inserted into this argument without a signed decomposition.

For a convergence statement, m→∞ alone with fixed δ does not make both bounds collapse to F(T); the means approach two distinct times. One sufficient coupled choice is δ_m→0 and m δ_m²→∞. Both clock variances then vanish, the means converge to T, both q values vanish, and continuity plus boundedness of F implies convergence of the bracket to F(T). A fixed finite m,δ still provides a valid interval even if wide. Numerical usefulness and a user-selected tolerance require a later result, not an assumption.

## 4. Positive witness for the exact represented matrix

Assume the exact stored matrix is verified to have off-diagonal entries ≤0 and there is an exact positive vector v with Kv>0 componentwise. With D=diag(v), D⁻¹KD has strictly positive row sums and nonpositive off-diagonals, hence positive diagonal entries and strict row diagonal dominance. Gershgorin places every eigenvalue in the open right half-plane. This proves K is a nonsingular M-matrix. A floating-point candidate v is admissible if its stored entries and the sign of Kv are evaluated with exact or rigorously enclosed arithmetic. An ordinary rounded positive printout of Kv alone is not a certificate.

The witness also gives Bv=Kv+γv>0 for every γ≥0. For an exact linear problem Bx=b and a represented numerical candidate x̂, define residual ρ=b−Bx̂. If η=maxᵢ |ρᵢ|/(Bv)ᵢ, then |ρ|≤ηBv. Positivity of B⁻¹ gives |x−x̂|≤ηv. Any upward bound for η preserves this inequality.

For the initial recurrence vector, η₀=maxᵢ|r−Bŷ₀|ᵢ/(Bv)ᵢ. If |yⱼ₋₁−ŷⱼ₋₁|≤ηⱼ₋₁v, then one valid inherited-error bound is

ηⱼ=maxᵢ [|γŷⱼ₋₁−Bŷⱼ|ᵢ+γ ηⱼ₋₁ vᵢ]/(Bv)ᵢ.

Consequently |A_m−Σwᵀŷⱼ|≤(wᵀv)Σηⱼ. Every previous recurrence error is included; treating each solve only as a fresh right-hand-side solve would miss propagation. The exact sum of the represented candidate dot products can be computed with rational arithmetic, or its own rounding error must be added.

For p∞, with Kx̂∞≈r, use η∞=maxᵢ|r−Kx̂∞|ᵢ/(Kv)ᵢ and |p∞−wᵀx̂∞|≤η∞wᵀv. The resulting interval can be intersected with [0,∞). This checks a numerical solve against the fixed represented matrix; it does not certify that this matrix equals an unrounded continuum generator.

## 5. Directed enclosure of the final bracket

Let certified intervals be A₋∈[a₋,b₋], A₊∈[a₊,b₊], p∞∈[p_L,p_U] and let q̄₋,q̄₊ be rigorous upper bounds on the exact q values, each strictly below one. A safe output is

L=max(0,(a₋−p_U q̄₋)/(1−q̄₋)),

U=min(p_U,b₊/(1−q̄₊)),

with outward rounding of the displayed divisions and arithmetic. The lower expression decreases with p and with q because its exact A≤p; alternatively its validity follows directly from the tail inequality with a lower A and upper p,q. The upper expression increases with q and A. If an available q upper bound is one, the expression is not evaluated; that side can use the trivial 0 or p_U and report loss of useful sharpness. Underflow to an uncertified zero is not a valid upper bound on a positive tail.

The target γ must be consistent. Either γ=m(1±δ)/T is treated exactly in B and all residuals (a floating-point factorization may approximate it), or the tail bound is recalculated for the actual represented γ and actual threshold. For represented γ₋ one may use δ_eff=γ₋T/m−1>0, and for represented γ₊ use δ_eff=1−γ₊T/m∈(0,1). It is not valid to certify a rounded-shift recurrence while using a different exact clock's tail formula without enclosing that discrepancy.

## 6. Source transpose and histories

The backward response uses exp(−Kt)r. If the initial pulse is a column vector w, the corresponding forward state is n(t)=exp(−Kᵀt)w and its event rate is rᵀn(t). Thus rᵀn(t)=wᵀexp(−Kt)r, which confirms the transpose.

For an actual nonnegative column injection j(s) per unit proper time, the forward equation would be n′=−Kᵀn+j, and integrated events through T would equal

w₀ᵀh(T)+∫₀ᵀ j(s)ᵀh(T−s) ds.

This is a conditional convolution identity. It supplies no missing real history, baryon density, source-volume conversion, or normalization. A declared pulse or manufactured history must retain its status. To obtain a history-level interval one must integrate appropriate componentwise source-age bounds or otherwise prove the scalar weighting is compatible; a single pulse response cannot automatically certify every vector history.

## 7. Energy and boundary interpretation

Positive event, photon-bin and energy rewards can each use the theorem when their weights/reward vectors are nonnegative. For emitted photon energy, the reward at the reaction bin must use the event's photon energy at that bin; weighting only the initial pulse energy is generally a different observable. Signed exchanges require a positive-minus-negative decomposition or direct interval arithmetic after the individual positive bounds.

The fixed old grid, RR/channel definitions, finite-bin projection and boundary rewards remain unchanged. A positive semigroup theorem does not turn a projected finite-bin rate into a full physical stopping law, prove global heating, supply unsupported recoil/angular laws, or repair source domain/isotope mismatches. Conditional count and energy return can be complete at their declared scope while N4/N5 remain partial, N6/N7 gated, global completion/error null and L4 false.

## Independent result

The central mathematical bracket is valid under the stated M-matrix and positivity premises. The meaningful implementation obligations are the exact represented-matrix witness, correct recurrence residual propagation, consistent γ/tail definition, outward tail and arithmetic bounds, and preservation of source/boundary semantics. Candidate-specific findings will be recorded only after inspecting the actual candidate and its frozen hash.
