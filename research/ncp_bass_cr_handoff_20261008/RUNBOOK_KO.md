# NCP local Codex handoff: **bass_cr only** (2026-10-08 KST)

> This is an executable handoff, not approval for merging physics results or changing production defaults. **Only `cosmosapjw-quantum/bass_cr` may be mutated.** Read-only external scientific snapshots may be imported with exact provenance. Do not run, push, merge, or claim ownership of BASS_HE, WU088_HH, or rei_bianchi work.

## P0. Bootstrap and source identity

1. Read `AGENTS.md`, `.codex/readback-policy.json`, `docs/READBACK_POLICY.md`, `docs/HPC_ACCURACY_POLICY_KO.md`, `docs/CHATGPT_CODEX_DIVISION_OF_LABOR_KO.md` from the **actual checked-out** bass_cr commit. Verify current `research/r4q-gap-closure-20261001` remote HEAD and compare with scientific baseline `19d7a61bd1238acabf12932578f5fdf5101462ad`. The HEAD may have advanced by this bootstrap publication. No force push and no merging to main.
2. Verify actual NCP cpuset/cgroups/CPU/RAM/disk/MPI/compiler/Rust/Python and installed local rclone endpoints. Do not assume 64 vCPU/128 GiB are fully admitted. Leave 16–24 GiB RAM and a coordinator CPU reserve. Set OMP/OPENBLAS/MKL threads=1 for independent jobs until measured scaling validates more. `-ffast-math`, `-Ofast`, silent error-tolerance changes and unbounded parallel launches are prohibited.
3. **The four source ZIPs have NOT been pushed as Git binary objects.** Their already-completed independent Drive+Dropbox backups, names, sizes and SHA-256 are pinned in `research/ncp_bass_cr_handoff_20261008/INPUTS.json`. A large binary Git write was blocked by platform safety checks; never pretend a source ZIP is already in Git. Local Codex must call the included `bootstrap_inputs.py` and verify the actual provider-fetched bytes. This works unattended **only if NCP has rclone authentication or public-download access**. Do not infer that ChatGPT connector credentials are available on NCP.
4. Start on a new nonexisting workdir; from the bass_cr checkout run:
   ```bash
   python3 research/ncp_bass_cr_handoff_20261008/bootstrap_inputs.py \
     --workdir "$NCP_RESEARCH_ROOT/input-stage-20261008" --extract
   ```
   Optional env: `NCP_GDRIVE_REMOTE=gdrive:`, `NCP_DROPBOX_REMOTE=dropbox:`; defaults are exactly those names. Optional `--source-dir /verified/mirror` if already staged by the user. `--offline` prohibits network; `--resume` resumes a partial input collection without deleting verified files. If a remote fetch is unavailable, write `SOURCE_INVENTORY.json` with `BLOCKED_INPUT`; continue independent repo-only tasks, never fabricate source files. No password prompts or requests to paste tokens into git.
5. Verify each ZIP exactly by manifest SHA-256/byte count/CRC, reject symlinks and traversal, verify selected internal evidence manifest/source SHA. Do not re-execute complete R6/R13/R14 or donor BRIDGE13 science simply because files were fetched. The only releasable input is the verified bytes, not the historical narrative.

## Task A: CR-XTHREAD-R15, full first-macro **fixed-birth shadow-continuum Thomson optical depth**

This is the principal new numerical/interval lane owned by **bass_cr**, not a restart of the REI donor research.

Authoritative read-only inputs:

- `BASS_CR_XTHREAD_R14_20261008_v1.zip` contains `CR_XTHREAD_R14_20261008/src/optical_goal.py`, `results/GOAL.json`, original `inputs/rei_bridge12_20261008/results/final_verified/interval/{CELL_CERTIFICATE.json,RESIDUAL_SLICES.json}`. R14 established a conditional first-cell signed `tau_cont - tau_hat` in `(1.8414e-20,1.8879e-20)` with defined gas-fraction endpoint-linear reconstruction and **dynamic proper nH**. The R14 FIRST-CELL proof is frozen; do not reset its error or claim independent recertification.
- `REI_XTHREAD_BRIDGE13_20261008.zip` is an **external read-only donor** with 32 original event-aligned cells, 6 finite births, 7 cohorts, 31 new Picard tubes, 496 new full-time residual subintervals, and carried signed prefix errors. Inspect `rei_bridge13_20261008/{REPORT_KO.md,CONTINUOUS_CHAIN_CONTRACT.json,SOURCE_BINDING.json,inputs/BRIDGE11_NATIVE.jsonl,results/final_interval/CHAIN_CERTIFICATE.json,results/final_interval/CELL_EVIDENCE.json,results/readout/ENDPOINT_READOUT.json,results/independent_check_v2/INDEPENDENT_CHAIN.json}`. Certificate parent is `9e1bad4daacbe9e313d34b1b645391b90b32b606` at the donor scope. Donor prefix native `variant=0` only; the prior `variant=4` shadowing regression is preserved.
- Donor model is FT03 HG Case A H/He CI/RR/two DR, prescribed FLRW `H=1e-14 s^-1`, `nH(t)=1e-4 exp(-3Ht) cm^-3`, `fHe=0.083`, `HH/RCT/CR OFF`, six fixed Gauss births, same energy/count family. This is *not* the Grackle low-T RHS in R13.
- Donor full first macro interval is `[0,1.25e9]` proper seconds. Conditional terminal state errors (same physical parameter, continuous *fixed-birth shadow* minus discrete): HII `[1.23629759,1.41371014]e-8`; temperature `[-3.51835718,-3.05440137]e-4 K`. **The donor did not certify continuous tau, continuous emission source quadrature, physical atomic-fit error or global operator.**

Implement a **new opt-in** `CR-XTHREAD-R15` in a new additive bass_cr research path. First write focused failing tests (do not label import/environment errors as assertion RED). Define:
```
Xe(t) = h(t) + fHe * (y(t)+2*z(t))
CT = c_SI * sigmaT_SI * 10^6
tau = CT * integral_0^(1.25e9 s) nH(t) * Xe(t) dt
e(t) = z_cont(t) - z_hat(t)
r(t) = z_hat'(t) - F(t,z_hat(t))
```
where `z_hat` is the **actual native endpoint piecewise-linear ionization-state reconstruction** on each donor cell. Retain analytic density and same real-valued source equations. Derive each cell's time-integrated residual goal kernel with nonzero incoming state error. Propagate signed and absolute error intervals through all cells using donor interval Jacobian/tube proofs; where donor bound is insufficient, perform a **new, scoped, actual interval calculation** with proper external verification. **Do not** treat R14's first-cell `e(0)=0` as the starting condition for cells 2–32. At each of six births, gas is continuous and declared cohort photons jump by the matching fixed source weight; identify actual clock location exactly. Optical tau stays accumulated; never reset it at a birth.

Record separate:
```
tau_native_piecewise_defined
tau_fixed_birth_continuum_interval
signed_tau_difference_interval
per_cell_forcing, per_cell_initial_state_coupling, per_cell_nonlinear_remainder
birth_trace_checks, inherited_incoming_error, source and density/clock identity
```
Do not infer a sign if 0 is inside the resulting full interval. Reconcile with first-cell R14 interval as an independent **frozen anchor**. Positive rate or endpoint Xe sign does NOT prove total delta-tau sign. Use actual full-time interval panels, not selected point extrema. Pointwise SciPy DOP853/Radau or high-precision quadrature may independently test enclosure, but **must not be used as certified proof premises**. Include an independent goal-integral check and at least one deliberately failing source/clock/birth-corruption fixture.

The result should be **conditional on the existing Decimal60 directed arithmetic and donor interval proof**; do not call it a new independent proof assistant validation. Continuum *emission* source, source quadrature error, observer tail, Bianchi physics, true astrophysical error, and physical admission remain `null/OPEN`. In particular **do not execute REI BRIDGE14** or change `rei_bianchi`; import future BRIDGE14 evidence read-only only when its exact publication is independently verified.

## Task B: independent bass_cr Grackle IGM extension (only after A is staged)

Use `BASS_CR_XTHREAD_R13_20261008_v1.zip` to read the actual 96 same-spectrum full point/48 nonphoto point code/results. Use `BASS_CR_FASTEST_NEWTON_20261007_v1.zip` for the native crate, opt-in midpoint and R6 Newton-stopping/ledger baseline. **Do not rerun** completed R6 tolerance sweep, R13 96+48 point evaluations, R4/M16 time bias tests. Existing physics is **Grackle-based low-temperature IGM**, not donor FT03. A new task may investigate **validated continuous-time RHS defect/goal response** at a truly matched new owner stage, or scoped receiver opt-in, but only after verifying the actual native owner caller, source and model/clock/initial-parameter identities.

Photo-rate `Gamma_a` per absorber needs the incident energy moment `Ecal_a` for heat, so Gamma-only E7/E8 data do not establish heat error. Preserve full EOS particle-number term:
```
Xe=h+fHe(y+2*z); D=1+fHe+Xe
Tdot_photo=2/(3*kB) * (Qheat/D-w*Ce/D^2).
```
Same-state quadrature comparisons are **not** temporal one-sided jumps. For distinct gas states, do not cancel CI/RR/DR/cooling/CMB/expansion/RCT. Retain verified R13 full point sources and original numerical floors. Do not introduce an unapproved extra photon-absorption heat moment or silently change 35eV RCT closure. If no new same-model trajectory/owner stage exists, mark this follow-on `BLOCKED_OWNER_INPUT`, keep R13 closed, and do not substitute a manufactured cross-model joint run.

## Task C: separate bass_cr G02/scattering backlog, evidence audit first

Inspect native bank and referenced `AGENTS.md` G02/HPC policies. Produce `G02_READINESS.json` with exact input bank refs, frozen geometry/derivative and branch restrictions. If **and only if** authoritative inputs, expected claim gates and algorithm are actually present, run focused unmatched tests/central derivative consistency on an isolated worker, with RAM admission and independent numerical checks. Otherwise mark `BLOCKED_INPUT`. Never promote original G02=UNRESOLVED or b-grid=NO_GO without direct evidence. No automatic 50/225 keV/u or production release.

## Scheduling and isolation (NCP)

Use `git worktree` or new clone for a **new non-force, bass_cr-only** feature branch starting at current research HEAD. Never modify user's dirty checkout, producer repos, `main`, production defaults, `CURRENT`, original receiver, or attached archives. Read-only provenance queries to external donor repos are permitted, but the scientific calculation **must be scoped to bass_cr**. Reserve coordinator + 16–24 GiB RAM, determine actual cgroup limits, use measured peak RSS, run controlled 1/2/4/8-process pilots before MPI scaling. No nested BLAS/Oversubscription, `Ofast` or tolerance loosening. Compute new science in create-only versioned directories and stop a lane on missing scientific inputs without halting independent work.

## Claim gates and acceptance

- Explicit source hashes, local git HEAD/tree, archived file sizes, ZIP CRC and any donor manifest IDs.
- Dedicated `UNIT/RED_GREEN`, native build, full compiler identity, numeric/interval results, independent verification, failure injection and rollback. Every `PASS` must name its actual criterion and closed source-specific scope.
- Separate **byte identity, signed point residual, interval enclosure, continuum error, parameter-family width, source quadrature, observer-tail and physical-fit** claims. Never promote one from another.
- `CR_OFF_FASTEST`, precision atomic `PARKED`, HH research `ACTIVE`, `G02=UNRESOLVED`, `all_bound=OPEN`, `b_grid=NO_GO`, `capture=false`, `production/physical=HOLD`; owner ACK/global CR counter/observer tail = `null`.
- Branch write: additive commit + nonforce push + PR/return where permitted, never reset an external contributor's HEAD. Backup new **immutable** ZIP create-only to Google Drive parent `1zzbClTE3qzz8gaiQwopXJqVk9ZGBawYZ` and Dropbox `/BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1`. Provider ACK+metadata is R1, not R3 restore. If NCP credentials absent, retain local ZIP, receipt `NOT_UPLOADED` and `BACKUP_BLOCKED_AUTH`.
- For every new slice write `SOURCE_BINDING.json`, `EXECUTION.json`, `VERIFICATION.json`, `RESULTS.json`, `CLAIM_GATE.json`, `RECOVERY_INVENTORY.json`, `NEXT_HANDOFF_KO.md`, detached `DELIVERY_RECEIPT.json`; preserve all failures and raw logs.
- Final `BASS_CR_NCP_RETURN_KO.md` and `BASS_CR_NCP_RETURN.json` must contain **what was actually computed**, exact new scientific bounds, isolated open gates, unit/time/normalization convention, hashes, remote commit/tree, backup IDs, and next actionable research. No cross-thread owner work included.

## Priority / stopping condition

Execute **A (R15)** first and complete as much actual interval/physics work as supported. Then B if same-model actual inputs exist. C is independent and must not starve A/B or claim missing bank as PASS. On missing remote auth, `bootstrap_inputs.py` explicitly reports `BLOCKED_INPUT`; continue source-only tasks and report the exact missing credential *capability*, not secrets. Do not ask the user to retype any previously-known file hashes or equations. Do not claim a complete prompt-only NCP transfer unless all four source ZIPs have been fetched and verified on NCP.
