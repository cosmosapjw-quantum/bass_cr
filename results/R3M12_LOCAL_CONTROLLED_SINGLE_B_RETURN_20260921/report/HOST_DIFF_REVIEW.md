# Scoped Host review — not independent review

Reviewed base 77237751bdd2aed5934bf7fc3bc626d631a09058 to patch commit 0b0090bc217ef62b27f709de803660b13bc64148. All ten patch paths are additions. Existing TDL/AOCC/vendor source bytes remain unchanged. The review agent registration succeeded but dispatch was rejected before execution with CLIENT_WORKTREE_MISMATCH; no independent review completion is claimed.

Fixed CAP: exp(log(M_ref)*dt/dt_ref) is divided equally across the two potential half steps. The midpoint potential and existing FFT kinetic phase retain atomic-unit sign conventions. The supplied semigroup, absorber-rate and no-absorber tests cover the changed mechanism.

Finite span: G=B†W B, c=B†W psi, alpha=solve(G,c), and c†alpha use consistent grid weights and conjugation. Rank loss is rejected rather than hidden by a pseudoinverse. The spatial projector gap uses -eps_b+eps_complement+cross with the matching Cauchy bound. Nested spans are not all-bound or continuum claims. Supplied nonorthogonal, complex basis-transform, dense/slab parity and gap tests are pertinent.

Checkpoint scope: a completed chunk is sealed with source/state/meta hashes. This is not a crash-transaction guarantee; an interruption during state/meta writes remains a preserved failure. New production baseline started fresh and resumed only its completed new-lane chunk. Source/result/state identity is checked separately from numerical convergence.

Current-task concerns: initial discrete stationary residual may depend on both grid and imaginary-time step; a fixed preparation parameter does not guarantee equally converged initial eigenstates. No unconditional spatial error bound follows. AOCC Hermitianization makes metric norm insufficient as a generator/basis convergence criterion. Its s+p negative-energy aggregate is not TDL n<=3 with d channels. Larger n, full b support, tail and continuum closure remain untested.

No additional current-task source repair was identified by this scoped Host review. This is not a merge approval or scientific admission. Optional broader hardening and solver redesign are outside this work unit.
