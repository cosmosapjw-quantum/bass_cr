# C21H independent physical and numerical adapter review

## Decision

**PASS_SCOPED_SOURCE_REVIEW.** The C21H adapter preserves the C21G optical-depth RHS and event loop, applies the fixed diagonal scaling correctly, and supplies the derived photon/passive Jacobian columns. Two material implementation findings were identified and corrected during this single source-review pass. Native chemistry execution, achieved native accuracy, and matched-accuracy timing remain separate unperformed obligations at the time of this review.

Reviewer: `/root/theory_adapter_review`, independent of the Python adapter and Rust bridge implementers. Reviewed Python snapshot: `optical_adapter.py`, SHA256 `5a18ab7766cb0b1ecef8abe0c320ee55a1ff615267a4e44846fd05dee67ed1ed`. This records the reviewed code identity; packaging manifests identify later purely documentary metadata changes, if any.

The primary scientific source is the unchanged C21G `reference_tau.py` SHA256 `714c40a4e3a0577784e6a754b95cdb34b247cb2e529953a375c74a43efafc3e0`, together with its original event-coupler and experiment definitions. VigilODE's source-read head was PR71 `0bab431e1031f86eb3ddb44371240bce49ae2376`; the bridge execution pin is measured Run2 `8a8bd409b1d96c7b7421f496d229e119fd3d284e`. The reviewer checked the norms, problem, adaptive and fast-driver file entries against `READ_SOURCE_MANIFEST.json` and `COMPILE_SOURCE_BINDING.json`; all four Git blobs and SHA256 values agree.

## Material findings and closure

| ID | Observed defect | Consequence | Minimal repair and closure |
|---|---|---|---|
| F1 | The initial `physical()` checked finite scaled input and time, while `partial_t()` returned the flat-epoch zero before entering the original RHS. It therefore lacked the original gas-domain check on that branch; multiplication by the scale could also overflow unchecked. | Invalid thermal/fraction states could receive a derivative value on the flat-time branch. | `physical()` now computes `u=z*D`, requires every physical component finite, and validates the original gas domain before all callbacks. The reviewer executed an isolated negative-thermal-state request at the flat branch: it returned `AdapterError: PHYSICAL_CALLBACK_STATE_DOMAIN`. No provider fallback or state projection was introduced. **CLOSED.** |
| F2 | The initial `nlu` alias looked for `lu_factorizations` or `linear_solver_setups`, neither being the actual emitted key, and defaulted to 0. | The evidence could falsely report zero linear-algebra work. | The required key is now `direct_factorizations` for VigilODE and `number_of_linear_solver_setups` for Diffsol. A missing, negative or non-integer count fails explicitly. The counter description distinguishes factorization attempts from setup counts. Verified against the actual fast-driver factor routine and Diffsol statistics names. **CLOSED.** |

The F1 probe was performed in an isolated Python process using a one-cohort, Y=0 callback wrapper and a negative thermal state at the interval's flat epoch branch. It is an adapter-domain probe, not a native chemistry run. The exact source hash and exception printed by that process are given above. The absence of a full pre-fix executable regression for each finding is preserved; these findings are not labelled uniformly red-first.

A small recording improvement was also communicated to the root: store numerical `fd_relative` and `time_fd_fraction` controls in the result contract, in addition to actual derivative nodes and the source pin. This makes non-default FD sensitivity runs directly reproducible. It does not change the RHS or the repaired source-review decision.

## Physical and algebraic checks

1. **RHS reuse.** The private imported module alone receives a replacement `solve_ivp` binding. Its original `run_reference_tau`, nested reduced RHS, birth order, source ledger, endpoint clamp, domain checks and population reconstruction remain in use. The private reference source is hashed before import and after the job. No historical C21F source file is edited by the adapter.
2. **Coordinate map.** The full state has M optical depths, four gas variables and 15 passive ledgers. For Y=0, the exact two He fraction entries are removed from both the state and fixed scales. Filling those two full-state entries with zero matches the original reduced callback's invariant values. Passive ledgers remain in the integrated state and in the norm dimension.
3. **Scaling.** Physical RHS is divided by D, and physical Jacobian columns are multiplied by their input scale and divided by the output scale. This implements `J_z=D^-1 J_y D`. Scalar alpha maps to the original physical vector alpha D. The independent derivation and symbolic checks are in `theory/C21H_THEORY_KO.md` and `theory/WOLFRAM_VERIFICATION.json`.
4. **Photon columns.** The implementation uses negative cohort rates for species/photo rows, negative heating for the thermal/heat rows, and `-N_i E_i` for photon work. Tau rows and non-photo microphysics rows are zero in these columns. These agree with direct differentiation of the unchanged RHS.
5. **Passive columns.** They are exactly zero because none of the 15 ledger state entries is read by the RHS. This is a mathematical sparsity property, not a finite-difference threshold.
6. **Gas columns.** Finite differences call the original RHS/provider. The allowed gas domain, Y=0 reduction, and one-sided stencils are used directly. No claim of analytic native microphysics derivatives is made.
7. **Nonautonomous derivative.** The actual RHS is evaluated at `chi(x)=min(max(x,L),U)`. Thus the flat-branch partial derivative is zero; the code explicitly adopts that branch convention at the two represented corners. Interior stencils remain strictly between L and U. The original clamped IVP is retained, including its derivative corners.
8. **Represented-node weights.** The three coefficients reproduce constant, linear and quadratic data with actual offsets. The code's `w1*(F1-F0)+w2*(F2-F0)` is algebraically the documented difference form. Nominal gas step is eps^(1/3) times `max(abs(u_j),D_j)`, nominal time step is 1e-4 cell width, and each may undergo at most 24 halving levels. Insufficient distinct admissible nodes produce explicit failure.

## Backend norm and counter interpretation

Pinned VigilODE uses an old/new maximum state denominator and RMS. Diffsol 0.17.1 delegates Faer vector norms to diffsol-la 0.2.0; its actual implementation divides the squared weighted sum by n and uses the current state. The general trait's displayed formula omits the 1/n factor, so the actual Faer source was used. Both conventions respect fixed diagonal coordinate scaling within their own norm. Their error estimates, state denominators, stage formulas and controllers differ, so identical tolerance numbers do not imply identical trajectories or achieved errors.

Python `nfev` counts RHS RPC requests; actual original-RHS calls also include gas and time FD work. Native provider call counts remain separate. The repaired `nlu` alias is a labelled convenience for the inherited schema, with raw method-specific statistics retained. An execution success is not used as a physical-balance or convergence result.

## Accepted-state observer review

The reviewer read the pinned VigilODE `Workspace::attempt` fresh-Jacobian branch and the complete `integrate_fast` accept/reject loop. The dense callback sees the driver's current base `(t,y)`. Only acceptance changes `(t,y)` and resets `fresh_state=false`, so the first attempt after an accepted step invokes the Jacobian at that new accepted endpoint. Rejected attempts may repeat the same base; an explicit requirement that repeated times have bit-identical states preserves this distinction. Appending the final successful endpoint supplies the last accepted state, and `internal_steps+1` checks completeness.

This inference is specific to the selected pinned dense fast driver and the observer local to that one solve. It does not extend to unrelated Jacobian diagnostics or a banded callback route. A failed/min-step/max-attempt run may stop before its last accepted endpoint is observed; its trace is an observed prefix with `accepted_grid_complete=false`. The source-level argument and the bridge's counter/grid checks support the implementation; execution of the bridge's source tests is recorded separately in the Rust validation receipt.

Diffsol obtains its accepted path directly from `state()` after each completed step. Its version has no absolute maximum-step configuration field, so the bridge explicitly sets a rolling stop, rounds a representably oversized stop downward, and checks actual accepted step widths. That mechanism is part of the recorded method contract. Requested output interpolation and accepted-step samples are different arrays.

## Remaining scientific obligations

- Run the frozen C21H backend candidates with the native owner and actual source/fixture/binary receipts on an admitted host.
- Compare physical budgets and gas/photon/log-survivor differences on a common output contract; inspect all returned accepted states and actual step widths.
- Use reference, tolerance and mesh sensitivity evidence for the existing numerical questions. Finite-difference sensitivity is a separate diagnostic when needed by the actual native results.
- Establish equal achieved accuracy and an identical host/output protocol before making a solver speed ranking.

`global_error_bound` remains `null`. The Schur reduction in the theory file is an exact future optimization identity, with no present implementation or speed claim. This review introduces no Full48, spectral/angular, Case B, Bianchi or full-EoR promotion.

## Primary references read

- [Steinebach 2023, Rodas5P, equations 1.2–1.3 and order-condition discussion](https://link.springer.com/article/10.1007/s10543-023-00967-x)
- [Diffsol 0.17.1 BDF implementation](https://docs.rs/diffsol/0.17.1/src/diffsol/ode_solver/bdf.rs.html)
- [Diffsol 0.17.1 Cargo dependency metadata](https://docs.rs/crate/diffsol/0.17.1/source/Cargo.toml)
- [diffsol-la 0.2.0 Faer vector norm implementation](https://docs.rs/diffsol-la/0.2.0/src/diffsol_la/vector/faer_serial.rs.html)

The original paper and official package sources support only the cited method/API properties. C21H's physical equivalence is established by the source map and the explicit derivation above.
