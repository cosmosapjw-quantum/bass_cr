# BASS CR R3M14 preflight — production initial-state binding과 preparation-control gate

Parent authority: `d04124e8a1b83f29fd26baa13f11cd68a8f33c15` (R3M13), parent checkpoint-repair merge `02546302a3d6958ea9fa97488a670672e07be178`.
Numerical `cr_repro/*.py` source digest remains `581ff84930bb862efafdfec5d39d5b25aebf9297ce7ce45f833a5abe125b2a5b`.
This preflight does **not** execute the production 0.25 a0 initial pair or collision and does not alter `main`.

## Verdict

`PREFLIGHT_CLOSE__R3M13_IMPORTED__PAIR_TRANSFER_BOUND_RECHECKED__INTERNAL_INITIAL_BYTE_BINDING_REQUIRED_AND_SIDECAR_DESIGNED__ISOLATED_CONTROL_FLOW_FIXTURE_3_PASS__PRODUCTION_R3M14_NOT_RUN__BGRID_NO_GO__R3M12_DRIVE_BACKUP_STILL_1_OF_19`

## 1. Imported durable state

R3M13 is accepted from its dual-backup/publication receipt:

- branch `cr/r3m13-preparation-transfer-20260922`
- commit `d04124e8a1b83f29fd26baa13f11cd68a8f33c15`
- transfer ZIP `BASS_CR_R3M13_PREPARATION_TRANSFER_20260922_v1.zip`
- bytes `2333455`
- SHA-256 `e696f90dc0eb17d69a6fd4419c9bf64f6c2538583c47006c047c2549f2fdf9f1`
- Drive raw readback verified, ID `1mSrjMvSK1J2bwtP7dKznAdlKAfbutx5n`
- Dropbox content-hash/size verified, ID `id:BSpOijBcT10AAAAAADs8lQ`
- production initial pair/collision not run, b-grid `NO_GO`.

The old R3M12 1.231876036 GB archive remains separate. Fresh Drive read of manifest `1XDOKIFQpfOcNFHWpVZ473oMfjfy7Hskj` still reports `complete_chunks=1`, `total_chunks=19`, `BACKUP_PENDING_PARTIAL_NOT_RESTORABLE_FROM_DRIVE_ALONE`. The verified Dropbox original remains present.

## 2. Preparation-step mathematical audit

At fixed finite spatial grid, normalized imaginary-time Strang iteration uses

```
S_tau = exp[-tau V_h/(2 hbar)] exp[-tau T_h/hbar] exp[-tau V_h/(2 hbar)].
```

For finite self-adjoint `T_h,V_h`, `S_tau` is positive Hermitian. With nonzero overlap with a simple dominant eigenspace, normalized iteration converges to the dominant eigenvector of `S_tau`, equivalently the lowest eigenvector of `H_eff(tau)=-(hbar/tau) log S_tau`. For a fixed finite matrix problem, symmetric BCH gives `H_eff=H_h+O(tau^2)`. This does not provide a uniform Coulomb `h -> 0` error constant.

For the R3M13 reduced `32^3`, `h=.4 a0` fixture, residuals at `tau=(.05,.025,.0125)` are
`(0.013638113049666804, 0.003484664337248429, 0.0008762234053475998) Eh`.
Independent Wolfram evaluation gives observed orders
`1.9685524496114083` and `1.9916490371569149`, consistent with second-order splitting bias at this fixed reduced grid. A three-point `r0+c2 tau^2+c4 tau^4` fit gives `r0 ~= 5.14e-7 Eh`, but this is only an empirical diagnostic.

Oppermann, Eicke & Lein, *J. Phys. B* 55 (2022), DOI `10.1088/1361-6455/ac8bb9`, show that Hamiltonian/imaginary-time states need not be exactly stationary under an approximate real-time propagator and motivate propagator-eigenstate diagnostics. This supports keeping Hamiltonian residual and real-time ray defect separate, not direct p-H validation. General Strang convergence depends on regularity; Coulomb singularities make uniform continuum extrapolation unsafe.

## 3. Pair-transfer theorem recheck

For normalized states `a,b`, let
`q=|<a,b>|`, `d=min_phi ||a-exp(i phi)b||=sqrt(2-2q)`.
For common contractive collision propagation `K` and the same Gram-corrected orthogonal finite-span projector `Q`,
`|sqrt(p_b)-sqrt(p_a)| <= d`, where `p_x=||QKx||^2`.
Also `A=K^dagger QK` is an effect, so
`|p_b-p_a| <= D(a,b)=d sqrt(1-d^2/4)`.

For relative screen `s`, a sufficient amplitude-bound criterion is
`d <= d_star = sqrt(p_a) s/(sqrt(1+s)+1)`.
With archived scenario anchor `p_a=0.00775827737938`, `s=.01`, Wolfram returns:

- `d_star = 0.0004393098779380350315`
- reduced R3M13 pair `d = 0.00018211061811878535`
- `d/d_star = 0.4145379543331648`
- trace distance `0.00018211061736383947`
- conditional intersection interval `[0.007726229542310674, 0.007790391545003789]`
- maximal relative deviation `0.004139342286103662`.

This rechecks R3M13. Reduced `d` cannot substitute for the production pair.

## 4. Provenance gap found before R3M14

The R3M13 helper writes `initial0125/initial.npy`, but a fresh inherited `ControlledTDLRunner.run()` recomputes `relaxed_initial()`. Matching only energy and Hamiltonian residual does not prove that the pair-tested state bytes are exactly the state propagated by the collision run. Therefore `reference_anchor_verified` cannot be upgraded on that basis alone.

This is a provenance gap, not a physics discrepancy.

## 5. Fail-closed sidecar witness

`scripts/r3m14_collision_initial_witness.py` stays outside `cr_repro/` and overrides only `relaxed_initial()`:

1. call `super().relaxed_initial()`;
2. observe the returned array without substitution or renormalization;
3. hash dtype, shape and numerical bytes;
4. compare with the validated immutable R3M13 prepared array;
5. write `r3m14_initial_binding.json` before any real-time step;
6. return the original `psi` object unchanged;
7. abort before propagation if array digest or backend binding fails.

On restart it requires the prior PASS witness plus unchanged instrumentation SHA, prepared receipt/file/array hashes, source digest and enriched config hash before delegating to the inherited sealed-restart path. `cr_repro/*.py` is unchanged; instrumentation SHA is separate.

### Validation status

Direct public-GitHub clone from the analysis container was blocked by DNS. Reconstructing relevant current runner paths from connector-read SSOT then hit a container-specific SciPy import failure because `scipy.special.eval_genlaguerre` was absent. This is `RUNTIME_ENVIRONMENT_IMPORT_BLOCKER`, not repository failure. Replacing only the unused special-function path by a minimal fixture stub allowed sidecar control-flow tests:

- witness vs plain inherited one-step state: exact array equality;
- changed prepared bytes: fail before resume;
- different but self-consistently rehashed prepared state: fail before first collision step.

Isolated fixture: `3 passed`. This is not a real-repo full-suite, GPU, or production-physics claim. Local Codex must run the new test against the actual checkout before production.

## 6. R3M14 execution contract

Frozen production parameters:

- `dx=.25 a0`
- real requested `dt=.05 t_a`
- fixed CAP, reference dt .05, width 4, power .125
- box x=[-30,40], y=[-30,30], z=[-30,90] a0
- b=2 a0, E=100 keV/u
- Gram-corrected finite projector nmax=3
- preparation A `.025 x 1200`
- preparation B `.0125 x 2400`
- both total imaginary time `30 t_a`.

Required order:

1. run real checkout tests including new witness test, preserving RED;
2. create both production preparations;
3. compare exact normalized arrays and production `d`;
4. evaluate 1% pair screen using archived R3M12 `p_a` only as scenario anchor;
5. irrespective of floating pair-screen PASS, run the `.0125 x 2400` collision;
6. start collision through R3M14 witness so actual internal initial is byte-bound before propagation;
7. continue same sealed directory in bounded checkpoint chunks;
8. compare final `analysis.gram_audit.P_span_nmax` to full-precision R3M12 same-grid result using original denominator.

Stop/gate policy:

- internal initial digest/backend binding FAIL -> `STOP_PROVENANCE_FAIL`, no propagation;
- production pair `d>d_star` -> preparation screen `NO_GO`; preserve evidence, no automatic finer grid;
- collision finite-span change >1% -> preparation control `NO_GO`;
- pair and collision screen <=1% -> only `PREPARATION_CONTROL_PASS_SCOPED`;
- scoped PASS does not overturn inherited spatial `NO_GO` because dx=.3125 -> .25 changed 2.289941%;
- b-grid remains `NO_GO`;
- finite n<=3 span is not promoted to all-bound capture or continuum probability.

## 7. Next DAG

Current next node remains `R3M14_PRODUCTION_DX025_INITIAL_PAIR_AND_COLLISION_RETURN`.

- FAIL: preserve evidence and stop at preparation/provenance diagnosis.
- scoped PASS: move only to `R3M15_SPATIAL_REFINEMENT_DECISION_GATE`; decide whether controlled dx=.20 is justified, but do not launch automatically.
- only after spatial/time/CAP/preparation gates close may a separate b-grid decision be revisited.
- AOCC radial/exponent refinement remains a separate truncation lane.

No physical rate, cross section, full b-grid, 50/225-keV extension, or production-central-selection mutation is authorized by this preflight.
