# BASS CR R3M14 preflight v2

Parent authority: \`d04124e8a1b83f29fd26baa13f11cd68a8f33c15\` (R3M13). Checkpoint-restart repair ancestry: \`02546302a3d6958ea9fa97488a670672e07be178\`. Numerical \`cr_repro/*.py\` source digest remains \`581ff84930bb862efafdfec5d39d5b25aebf9297ce7ce45f833a5abe125b2a5b\`.

Verdict:

\`PREFLIGHT_CLOSE_V2__R3M13_IMPORTED__PAIR_TRANSFER_BOUND_RECHECKED__CANONICAL_R3M13_LOADER_REUSED__ACTUAL_INTERNAL_INITIAL_BYTE_AND_ENVIRONMENT_BINDING_REQUIRED__ISOLATED_CONTROL_FLOW_FIXTURE_6_PASS__PRODUCTION_R3M14_NOT_RUN__BGRID_NO_GO__R3M12_DRIVE_BACKUP_STILL_1_OF_19\`

## Imported state and backup separation

R3M13 is accepted from branch \`cr/r3m13-preparation-transfer-20260922\`, commit \`d04124e8a1b83f29fd26baa13f11cd68a8f33c15\`. Its transfer ZIP is 2,333,455 bytes with SHA-256 \`e696f90dc0eb17d69a6fd4419c9bf64f6c2538583c47006c047c2549f2fdf9f1\`; Drive raw readback and Dropbox size/content hash were verified. R3M13 did not run the production pair or collision and did not admit a b-grid.

The older R3M12 1,231,876,036-byte archive remains a separate backup problem. Fresh Drive manifest \`1XDOKIFQpfOcNFHWpVZ473oMfjfy7Hskj\` remains \`complete_chunks=1/19\`, \`BACKUP_PENDING_PARTIAL_NOT_RESTORABLE_FROM_DRIVE_ALONE\`. The Dropbox original remains present. Small R3M13/R3M14 transfer backups do not close this older blocker.

## Mathematical and literature audit

At fixed finite spatial grid the normalized imaginary-time Strang map is

\[
S_\tau=e^{-\tau V_h/(2\hbar)}e^{-\tau T_h/\hbar}e^{-\tau V_h/(2\hbar)}.
\]

For finite self-adjoint \`T_h,V_h\`, \`S_tau\` is positive Hermitian. Under the usual nonzero-overlap/simple-dominant-eigenspace assumptions, normalized iteration converges to the dominant eigenvector of \`S_tau\`, equivalently the lowest eigenvector of \`H_eff(tau)=-(hbar/tau) log S_tau\`. Symmetric BCH gives \`H_eff=H_h+O(tau^2)\` at fixed finite discretization. No uniform Coulomb \`h -> 0\` error constant is inferred.

For the R3M13 reduced \`32^3\`, \`h=.4 a0\` fixture, residuals at \`tau=(.05,.025,.0125)\` were \`(0.013638113049666804, 0.003484664337248429, 0.0008762234053475998) Eh\`. Independent Wolfram evaluation gives observed orders \`1.9685524496114083\` and \`1.9916490371569149\`, consistent with fixed-grid second-order splitting bias. A three-point \`r0+c2 tau^2+c4 tau^4\` fit gives \`r0≈5.14e-7 Eh\`, used only as an empirical diagnostic.

Oppermann, Eicke & Lein, *J. Phys. B* 55 (2022), DOI \`10.1088/1361-6455/ac8bb9\`, show that Hamiltonian/imaginary-time states can fail to be exactly stationary under an approximate real-time propagator. This supports retaining Hamiltonian residual and real-time ray-defect diagnostics separately; it is not direct p-H collision validation.

For normalized states \`a,b\`, with \`d=min_phi ||a-exp(i phi)b||\`, common contractive propagation \`K\`, and the same orthogonal Gram-corrected finite-span projector \`Q\`,

\[
|\sqrt{p_b}-\sqrt{p_a}|\le d,\qquad
|p_b-p_a|\le d\sqrt{1-d^2/4}.
\]

For a relative screen \`s\`, a sufficient amplitude-bound condition is

\[
d\le d_\star=\sqrt{p_a}\frac{s}{\sqrt{1+s}+1}.
\]

Using archived scenario anchor \`p_a=0.00775827737938\` and \`s=.01\`, Wolfram independently returns \`d_star=0.0004393098779380350315\`. The reduced R3M13 pair has \`d=0.00018211061811878535\`, \`d/d_star=0.4145379543331648\`, trace distance \`0.00018211061736383947\`, conditional interval \`[0.007726229542310674,0.007790391545003789]\`, and maximal relative deviation \`0.004139342286103662\`. This is not a production-grid bound.

## Provenance gap and v2 repair

R3M13 writes a pair-tested \`initial0125/initial.npy\`, whereas a fresh \`ControlledTDLRunner.run()\` internally recomputes \`relaxed_initial()\`. Matching only energy and Hamiltonian residual does not prove byte identity between the pair-tested state and the state actually propagated. This is a provenance gap, not a physics discrepancy.

The v2 sidecar \`scripts/r3m14_collision_initial_witness.py\` stays outside \`cr_repro\` and leaves the numerical source digest unchanged. Unlike v1, it directly reuses canonical \`scripts/r3m13_initial_state_pair.py::load_prepared()\` as the preparation SSOT. Thus R3M13 status/source, \`dynamics_fingerprint\`, initial-file SHA, grid shape and \`dv\` checks are not reimplemented.

v2 additionally binds:

1. the R3M13 helper source pin and current helper SHA;
2. preparation receipt \`script_sha256\` to that helper SHA;
3. canonical-JSON identity of preparation and collision raw configs;
4. weighted preparation norm with tolerance \`2e-10\`;
5. typed SHA-256 over dtype, shape and numerical bytes of the actual inherited \`relaxed_initial()\` state;
6. its weighted norm;
7. preparation/runtime equality of the fields R3M13 records: Python version, NumPy version and backend;
8. on restart, unchanged instrumentation SHA, helper SHA, prepared receipt/file/array hashes, source/config identity, and full recorded collision runtime environment, including CuPy/CUDA identifiers when available.

The witness is written before the first real-time step. Any mismatch aborts before a checkpoint is created. The sidecar never substitutes, renormalizes, casts, or injects the prepared array; it returns the original inherited \`psi\` object unchanged.

## Validation status

Direct public-GitHub clone from the analysis container was blocked by DNS. A first reconstructed fixture collection also hit a container-specific missing \`scipy.special.eval_genlaguerre\`; that is classified \`RUNTIME_ENVIRONMENT_IMPORT_BLOCKER\`, not repo or physics failure. Keeping the relevant current runner control flow and replacing only the unused special-function path by a fixture stub, the hardened v2 tests report \`6 passed\`.

The six isolated checks cover exact one-step noninterference, stale prepared-byte rejection, self-consistently rehashed but numerically different preparation rejection before propagation, canonical config type-identity failure, R3M13 helper-SHA binding, and preparation/runtime environment mismatch rejection. Scope is \`ISOLATED_CONTROL_FLOW_STATE_IDENTITY_AND_PROVENANCE_GATES_ONLY\`. This is not a real-checkout full-suite, GPU, or production-physics PASS.

## Production contract and gate

Frozen production conditions remain \`dx=.25 a0\`, requested real \`dt=.05 t_a\`, fixed CAP(reference \`.05\`, width 4, power \`.125\`), box \`x=[-30,40], y=[-30,30], z=[-30,90] a0\`, \`b=2 a0\`, \`E=100 keV/u\`, Gram-corrected finite projector \`nmax=3\`, preparation A \`.025 x 1200\`, preparation B \`.0125 x 2400\`, both total imaginary time \`30 t_a\`.

Execution order is: real-checkout regression tests, both production preparations, production pair \`d\`, scenario pair screen, \`.0125 x 2400\` collision launched through the v2 witness, bounded sealed restarts, then final \`analysis.gram_audit.P_span_nmax\` comparison to the full-precision R3M12 same-grid reference.

Gate semantics are unchanged: provenance mismatch -> \`STOP_PROVENANCE_FAIL\`; production \`d>d_star\` -> preparation-pair \`NO_GO\`; final same-grid finite-span change >1% -> preparation-control \`NO_GO\`; both screens <=1% -> only \`PREPARATION_CONTROL_PASS_SCOPED\`.

A scoped PASS does not overturn inherited spatial \`NO_GO\` because \`dx=.3125 -> .25\` changed 2.289941%, does not authorize a b-grid, and does not promote finite \`n<=3\` span to all-bound or continuum probability.

Current next node remains \`R3M14_PRODUCTION_DX025_INITIAL_PAIR_AND_COLLISION_RETURN\`. If it closes scoped-PASS, the following node is only \`R3M15_SPATIAL_REFINEMENT_DECISION_GATE\`; no automatic \`dx=.20\` launch is authorized.
