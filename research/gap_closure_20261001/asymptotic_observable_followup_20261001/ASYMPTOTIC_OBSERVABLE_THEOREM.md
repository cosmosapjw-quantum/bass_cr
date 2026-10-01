# Ordinary limits, asymptotic oscillations and dephased observables

This is a finite-dimensional theorem for a **specified exact reference dynamics**. It explains what a non-invariant archived selection can mean at infinity. It neither installs a new observable nor transfers the archived B0 trajectory to the reference dynamics. No physical/native propagation is performed.

## 1. Remove the scalar long-range phase before using integrability

On a finite-dimensional Hilbert space let

\[
i\hbar\dot\psi(t)=[H_0+s(t)I+V(t)]\psi(t),\qquad H_0=H_0^\dagger,
\]

where s is real and locally integrable, V is Hermitian and locally integrable, and
\(\int_{t_0}^\infty\|V(t)\|dt<\infty\). Assume \(\|\psi\|^2=N\). The scalar s may have a nonintegrable Coulomb 1/t tail. Define

\[
x(t)=e^{iH_0(t-t_0)/\hbar}e^{(i/\hbar)\int_{t_0}^t s(u)du}\psi(t).
\]

Then \(\dot x=-(i/\hbar)V_Ix\), with \(\|V_I\|=\|V\|\). Therefore

\[
\|x(t_2)-x(t_1)\|\le {\sqrt N\over\hbar}\int_{t_1}^{t_2}\|V(u)\|du.
\]

Completeness gives x∞, norm √N, and

\[
\|x(t)-x_\infty\|\le {\sqrt N\over\hbar}\int_t^\infty\|V(u)\|du.
\]

The same argument for the interaction evolution in operator norm gives a unitary limit (in finite dimension limits of the unitary identities hold). Thus arbitrary asymptotic states are possible as the initial state varies. This theorem uses no asserted scattering result from a literature citation.

For a bounded Hermitian observable A,

\[
\langle\psi(t),A\psi(t)\rangle
=f_A(t)+o(1),\quad
f_A(t)=\langle x_\infty,e^{iH_0(t-t_0)/\hbar}A e^{-iH_0(t-t_0)/\hbar}x_\infty\rangle,
\]

and the explicit error is at most
\(2N\|A\|\hbar^{-1}\int_t^\infty\|V(u)\|du\).
This follows by adding and subtracting the two quadratic forms and using the equal norms. The Coulomb scalar phase cancels from every observable.

## 2. Exact ordinary-limit criterion

Let H0=Σλ λEλ use its **distinct exact** eigenvalues, retaining whole degenerate eigenspaces. Group equal Bohr frequencies:

\[
c_\omega=\sum_{(\lambda-\mu)/\hbar=\omega}
\langle x_\infty,E_\lambda A E_\mu x_\infty\rangle,
\qquad f_A(t)=\sum_\omega c_\omega e^{i\omega(t-t_0)}.
\]

Then the observable has an ordinary t→∞ limit **if and only if** every cω with ω≠0 is exactly zero. Sufficiency is immediate. For necessity, if fA tends to L, its long average after multiplication by exp(−iωt) tends to zero for ω≠0. The finite exponential sum instead has that average equal to the corresponding cω, up to the fixed origin phase. Thus cω=0.

For a particular state, [A,H0]≠0 alone does not prove nonconvergence: that state may occupy one eigenspace, or contributions at a repeated Bohr frequency may cancel. The statement that the limit exists for **every** asymptotic state is equivalent to [A,H0]=0. To see necessity choose a superposition of vectors from two eigenspaces with a nonzero off-diagonal A block. The unitary interaction-limit map allows this asymptotic state to correspond to an initial state.

No floating energy tolerance may decide exact degeneracy. Nearly equal eigenvalues are not mathematically degenerate. The helper `dephasing.py` accepts exact declared energies and Gaussian-rational coefficients, groups exact equal frequencies, and performs no eigensolver or estimate of the unavailable physical asymptotic state.

## 3. The long time average always has a limit

Define the energy-dephased observable

\[
\mathcal D_{H_0}(A)=\sum_\lambda E_\lambda A E_\lambda.
\]

Since the average of a nonzero-frequency exponential vanishes and the average of an o(1) remainder vanishes,

\[
\lim_{T\to\infty}{1\over T-t_0}\int_{t_0}^{T}
\langle\psi(t),A\psi(t)\rangle dt
=\langle x_\infty,\mathcal D_{H_0}(A)x_\infty\rangle.
\]

Degenerate coherences remain; deleting all off-diagonal entries in an arbitrary basis would be wrong. If 0≤A≤I then 0≤D(A)≤I, but D(A) is generally not a projector. This is a separate averaged observable, not proof that the original instantaneous observable converges. A finite averaging-time error also depends on nonzero frequency gaps; this note does not identify a physical averaging duration.

## 4. Connection to the certified nearby spectral selector

Let E0 commute with H0 and let ||A−E0||≤δ. Then, for the same reference state,

\[
|P_A(t)-P_{E_0}(t)|\le N\delta.
\]

If the separately derived gapped-tail theorem gives P_E0,∞ and
\(|P_{E_0}(t)-P_{E_0,\infty}|\le N B(t)\), then

\[
|P_A(t)-P_{E_0,\infty}|\le N[\delta+B(t)].
\]

The long average of PA lies within Nδ of that same reference limit, and its limiting oscillation diameter is at most2Nδ. This statement gives a uniform band even when the ordinary PA limit does not exist. It does not integrate a constant selector defect over an infinite time interval.

For the newly defined conforming reference, the archived physical projector acts in a common ambient L2 space. Its compression to the reference span is a Hermitian contraction A, generally **not** an orthogonal projector in that finite space. The physical projector mapping certificate implies the bound above after compression. The formula applies only to the same reference state. An archived numerical state propagated under the old model needs its own dynamical comparison; the static mapping does not supply that comparison.

The theorem applies to the projectile block after exact cross-support vanishing. The full two-center H0 has target/projectile degeneracies, so its rank-five projectile subspace must not be called an isolated global energy cluster.

## 5. Verified exact examples and remaining scope

Six new exact tests cover: persistent two-state oscillation; a noncommuting observable with an eigenstate giving a constant expectation; retained degenerate coherence; cancellation of equal-frequency contributions; complex conjugate frequency pairs; and rejection of tolerance-based energy grouping. A normalized (3/5,4/5) state with A=(1/2)[[1,1],[1,1]] and energies0,2 gives fA=1/2+(12/25)cos(2t), so no ordinary limit exists. Its long average is1/2. These are algebraic examples, not a physical B0 trajectory.

Derived status: the criterion and averaged limit are established under the exact finite-reference hypotheses. Actual B0 asymptotic coefficients are unavailable without a state and dynamics comparison. No named observable, reference dynamics, or long-time average has been adopted for production by this derivation.
