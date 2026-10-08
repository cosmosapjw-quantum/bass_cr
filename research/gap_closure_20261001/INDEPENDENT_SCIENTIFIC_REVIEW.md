# Bounded independent scientific review

Review date: 2026-10-01. Scope: G01 theorem/kernel/CAS contract; G07/G08
numerical methods, conditioning admission and claimed scope; G10 semantic
selector; G04 Route A conditional theorem and its compatibility with Route B;
the root error-budget note/schema/current B0 state. This was one bounded pass,
not a review-of-review or a replay of previously passing suites.

**Outcome:** no unresolved mathematical contradiction was found in the scoped
G01/G08 closures, G07 limited-domain result, or G04 conditional theorem.
One concrete G10 duplicate-channel admission bug was found and repaired.
The error-budget trajectory hypothesis was clarified. Two minor G07 provenance
wording corrections were also made and inspected. All five findings below are
resolved; exact file pins and dispositions are recorded in the companion JSON.

The reviewer authored Route B. Its own proof/code is therefore **not independently
approved by this report**. The root agent separately owns that review. The
reviewer did correct an obsolete Route B point-data availability statement after
the physical fixture recovery, with root authorization; no Route B code changed.

## Findings and disposition

1. **G10 duplicate physical function admitted under an aliased quantum label —
   medium, resolved.** The original duplicate key included principal_n and kind.
   Append a copy of B0 row 9 with the same center, l, m, energy and radial SHA256,
   but change principal_n from 1 to 5. The original selector returned
   `[9,10,12,13,14,18]`, admitting the identical physical basis function twice.
   The root changed the physical uniqueness key to
   `(center,l,m,radial_identity)`, independently of quantum-label validation.
   The author preserved a failing new regression and a nine-test passing log.
   This reviewer inspected the exact changed predicate and independently reran
   only the alias discriminator; it now raises `ValueError: duplicate physical
   channel identity`. The original B0 mapping stays unchanged.

2. **Error-budget variation-of-constants hypothesis implicit — low, resolved.**
   The displayed bound involving only B−Bhat requires yhat to solve
   yhat′=Bhat yhat exactly. Applying it to an arbitrary numerical interpolant
   also requires its defect r=yhat′−Bhat yhat and an added integral of ||r||.
   The root added both statements; the reviewer read the correction. This
   clarifies a conditional theorem without changing any estimated error or gate.

3. **G07 results labeled synthetic-only despite archived point replay — low, resolved.**
   The initial common `scope` string was `FINITE_SYNTHETIC_MATRICES_ONLY`, but
   the solver artifact correctly contains eight archived physical matrix
   postprocessing records. The numerical results themselves do not claim a new
   physical run. Requested correction: name the finite-matrix research/postprocess
   scope accurately in code and stored metadata. Both now use
   `FINITE_MATRIX_RESEARCH_AUDIT_NO_NEW_NATIVE_RUNS`; the correction was inspected.

4. **G07 environment equivalence wording — low, resolved.** The initial report grouped
   Python 3.12.14, NumPy 2.3.5 and SciPy 1.17.0 as matching the pinned execution
   versions. `evidence/ENVIRONMENT_CURRENT_RUNTIME.json` has Python 3.13.5.
   NumPy/SciPy match; Python does not. Requested correction: explicitly describe
   local Python 3.12 postprocessing and avoid claiming an exact native-environment
   replay. The final report now explicitly distinguishes saved Python 3.13.5 from
   local 3.12.14 while preserving the matching NumPy/SciPy pins.

5. **Route B point-data availability stale after recovery — low, resolved.**
   The earlier report said no locally supplied physical raw matrices. Eight
   verified point fixtures are now present in G07. Route B report/status/candidate
   files now distinguish the recovered point matrices from still-missing
   whole-cell S,S′,W,W′ and operator-error enclosures. Its manifest was refreshed.
   This correction does not change the unresolved continuous physical bound.

## Mathematical assessment

**G01:** local absolute continuity and positive definiteness give local coercivity,
locally integrable A, and an AC exact finite-dimensional trajectory. The product
rules, distinction between Pi and Q, norm factor N, Hermitian Rayleigh inequality,
finite integral and Cauchy-tail argument are consistent. Constant nonsingular T
covariance transforms J as T^-1 J, Pi by similarity, Q/W by congruence. The proof
does not assume differentiable eigenvalue branches or transfer a finite-window
certificate to infinity. The 2-by-2 Wolfram checks are labeled as parametric
checks rather than the general proof. Closure is justified for the conditional
finite-model theorem, not a physical continuous-tail certificate.

**G07:** the Cholesky congruence and eigenvector back-transform are correct.
The Decimal 2-by-2 characteristic polynomial uses the exact rounded input values
and a stable quadratic formula. Related LAPACK paths are not presented as fully
independent. The report correctly retains high-condition full-W assembly failures
and the approximately 2.78e-6 forward error that solver agreement alone misses.
Hermitian-part adjustments are explicit; no SPD shifts/truncation are performed.
The condition-number recommendation is screening, not a uniform theorem. The
eight stored B0 pencils are well conditioned, but operator assembly accuracy and
independent Sdot validation remain separate. `RESOLVED_WITH_LIMITATION` is the
appropriate registry category.

**G08:** the constant-basis covariance proof is sound. The raw coefficient-block
norm counterexample uses the correct similarity law. The new metric-projected
coupling norm uses S-orthonormal subspace maps and is separately named. It is
not claimed to equal a physical transfer rate automatically. Keeping the same
numerical J after a general coordinate change is correctly excluded.

**G10:** following the repaired physical uniqueness check, the selector validates
energy sign, channel kind, quantum-label structure, center convention and a radial
SHA256 field; it returns current positions. Reordering preserves the same selected
span and its semantic identity. The B0 coefficient-bank comparison supplies the
current external identity binding. The utility cannot itself authenticate an
arbitrary future caller's digest/energy against coefficient bytes; future basis
registries still need actual source binding and rank/qualification checks. The
selection hash identifies the declared span; it is not a complete operator or
energy-provenance hash. These limits are consistent with the narrow G10 closure.

**G04 Route A:** fixed-J Pidot Pi=0, compatibility and projector off-diagonality
justify the selected/complement leakage identity without an extra factor two.
The same-center source gives the stated H−iD cancellation condition. For exact
conforming compact support and invariant isolated selected span, centering the
Coulomb multiplication operator by its range midpoint yields
Z_target*a/[hbar*(R²−a²)], valid in the disjoint-support regime R>2a.
The conditional atanh/atan tail integrals and units agree with direct elementary
integration. The report explicitly refuses to promote tiny rounded isolated
residuals to exact zero; a nondecaying constant allowance would not be integrable.
The archived radial audit is high precision, not directed interval certification.
An exact reference-model interpretation and validated mapping remain required.
Route B can cover the finite bridge, but its synthetic certificate does not yet
validate physical cells or repair the exact isolated-span assumption. Thus the
two routes are mathematically compatible while physical Level 3 remains open.

**Error budget:** all eight requested components are present; unknown numerical
values stay null. Deterministic triangle sums require simultaneously valid bounds
on a common telescoping chain, not statistical independence. The note separates
fixed-b probability units from cross-section area, avoids double-counting a
window increment and an already enclosing tail, and keeps incoming/outgoing
absolute estimates separate. The 1e-5 total research tail target with 5e-6 per
side is a predeclared future research criterion, not production approval or run
authorization. The certified total remains unavailable.

## Review evidence and limits

The review read proofs, implementation files, test code, reports, claim updates,
saved environment metadata and the relevant same-center operator source. It
performed one new failing alias discriminator and the corresponding focused
post-repair rerun. It did **not** rerun the G01, G07/G08, G10, G04 or physical
operator suites. The parent's supplied passing-suite records were inspected,
not relabeled as independent executions. It did not repeat archive restoration,
raw remote readback, source acquisition, CAS calls, or native computation.

No publication, backup or shared database mutation was performed by this reviewer.
New external/native scientific runs: zero. Review of stored operator matrices is
not PHYSICAL_RUN_VERIFIED for a new run. The companion JSON pins files inspected
and records exact finding states. The physical claim ceilings remain unchanged.
