# BASS CR R3M12 local start

Continue repository `cosmosapjw-quantum/bass_cr` from branch `cr/r3m11-controlled-refinement-20260921`. The scientific parent is main commit `77237751bdd2aed5934bf7fc3bc626d631a09058` and its immutable `results/R3M10_LOCAL_RETURN_20260921/report/DECISION.json`. This task is the one-electron H+ + H(1s) CR branch, not P0/H-H/host chemistry. Original Nichols author code/data are unavailable and are NOT a prerequisite. Never claim Nichols implementation reproduction.

Fetch the branch into a clean worktree without discarding local changes:

```bash
git fetch origin cr/r3m11-controlled-refinement-20260921
git worktree add ../bass_cr_r3m12 -b work/r3m12-controlled-local origin/cr/r3m11-controlled-refinement-20260921
cd ../bass_cr_r3m12
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
pip install -e .
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
python -m pytest -q tests -p no:cacheprovider
python scripts/r3m11_plan.py --out runs/R3M12_plan --backend auto
```

When already on this branch or when worktree names exist, use another clean path rather than deleting/replacing anything. Record `git rev-parse HEAD`, `git status`, Python, pip freeze, NumPy/SciPy/CuPy/CUDA/driver versions and the resolved backend. Do not change a working CUDA installation automatically. Use the user's existing verified GPU environment if available. GPU parity is required locally; CPU-only skips are not GPU PASS.

Read `docs/r3m11/REPORT_KO.md`, `cr_repro/r3m11.py`, `tests/test_r3m11_controlled.py`, and generated `runs/R3M12_plan/PLAN.json` before physics. All historical R3M10 code/results/failures remain immutable. Root MANIFEST is historical; R3M11 has a separate payload manifest. The generated COMMANDS.sh is a menu, not permission to launch every stage blindly. It never launches b-grid.

## Implemented changes, no new implementation needed to start

1. `python -m cr_repro.r3m11 initial ...` runs isolated-target preparation and records energy and the normalized discrete residual ||(H-E)psi||. Spatial accuracy and stationarity are separate.
2. `python -m cr_repro.r3m11 tdl ...` uses a fixed CAP-equivalent absorber at reference dt=0.05 atomic time, symmetric damping and a streaming finite-grid Gram projector. It returns raw legacy overlap sum, selected-subspace Gram probability, rank/condition, and a selected-complement gap diagnostic.
3. `python -m cr_repro.r3m11 aocc-audit ...` evaluates fixed-Boys AOCC matrices without propagation.
4. `python -m cr_repro.r3m11 aocc ...` executes the unchanged one-electron AOCC dynamics with the corrected complex Boys evaluation in an isolated module namespace. Original vendor bytes are untouched.

A known production fixture has z=-3.3168887925160937+21.984297833631878i. Legacy SciPy1.17.0 hyp1f1 F0 differs from independent reference by 49.4016%. Opt-in erf/upward recurrence restores sampled Hermiticity. Do not replace raw H with its Hermitian average as a substitute for diagnosing primitive integrals. Legacy propagator Hermitianization is still present and is NOT a convergence certificate.

## Stage A: cheap diagnosis first

Run generated `initial_dx0.4_tau0.05`, `initial_dx0.4_tau0.025`, `initial_dx0.4_tau0.0125` initial-only commands. They fix total imaginary time15. Then run the same ladder at dx0.3125 and dx0.25 if useful. Check both the energy and residual. If residual stagnates, increase total imaginary duration separately and preserve that comparison. Do not call a state converged merely because E is close to -0.5 Eh.

Run both `aocc_audit_*` cases. Verify the bad-time raw-H/generator defects and independently evaluate the known Boys fixture in the actual local SciPy environment. No production rerun is admitted until the new tests pass and matrix defects are understood. The observed ~1e-13 matrix defects are sampled evidence, not a uniform bound.

## Stage B: controlled single-b runs

Freeze an initial-preparation setting from A before running the candidate TDL configs; record any config change as new immutable bytes. Candidate defaults use imag_dt=.0125, total imaginary time15. This is not a pre-certified initial state.

Start with exactly 100keV/u, b=2a0. Example:

```bash
python -m cr_repro.r3m11 tdl --config runs/R3M12_plan/tdl_base.json --out runs/R3M12_plan/outputs/tdl_base --max-steps 100
python -m cr_repro.r3m11 tdl --config runs/R3M12_plan/tdl_base.json --out runs/R3M12_plan/outputs/tdl_base --resume
```

The new atomic `checkpoint.npz` contains config/code/environment identity. Never resume old `state.npy/state.json` with this method. Use a new output directory for changed settings. Interrupted AOCC propagation has no certified restart: preserve partial output, do not relabel it completed.

Run candidate TDL dt025, dx03125 and dx025 only after baseline and initial review. All retain absorber_reference_dt=.05. Compare **P_selected_bound_gram** on matching nmax and geometry; raw overlap sum is diagnostic. Independently test preparation time/imag_dt effects on capture. Then repeat final-time and box/absorber controls as needed with valid cell grids. Altering final time may require an enlarged box; retain both effects as explicitly labelled until separated.

Run AOCC baseline and larger basis with controlled Boys, plus dt/2 for each. `aocc_large_same_range` isolates the ns/np increase from the old simultaneous alpha_max increase. Keep s+p-only and finite negative-state sum labels; these are not all-bound limits. No H-minus/spinS0/S1 physics from the old two-electron branch is allowed.

## Decisions and prohibited inferences

- Current b-grid decision remains NO_GO until a new reviewed single-b bundle exists. Do not launch b-grid, bmax/tail, integrated cross sections or 50/225keV/u in this first return.
- Preserve baseline-denominator 1% screening; do not loosen it after seeing results. It is screening, not a rigorous physical uncertainty.
- Finite n<=3 projection complement includes omitted bound and target bound. Never call it pure continuum. Region probability need not equal truncated bound probability; do NOT make that equality a mandatory gate for valid selected-bound capture.
- AOCC s+p total and TDL n<=3 total have different truncation. Do not force equality. A future matched 1s/2s/2p projector comparison requires explicit observable matching.
- No source voting, no covariance from method spread, no unmeasured cross-energy error model, no production central or CR physical rate.
- An actual cosmological G(p) packet is NOT needed for the atomic single-b benchmark; it is needed later for a physical integrated CR rate.

## Durable return

Write `R3M12_RETURN/` with immutable configs, environment, source SHA/tree, commands, stdout/stderr, timings and memory, each complete result, all failures, initial-state table, fixed-CAP TDL refinement table, fixed-Boys AOCC matrix/basis/dt table, masks/reference_dt/nmax labels, and explicit GO/NO_GO per lane. Distinguish implementation repair from spatial/basis/asymptotic convergence. Keep all-bound admission false unless independently proved.

Create a non-self-referential manifest, archive and detached SHA receipt. Push code/docs/results to the work branch; do not merge or force-update main. Use release assets for large wavefunction arrays rather than Git blobs. Upload create-only copies to the existing Google Drive and Dropbox BASS dossier destinations when connected. Count dual backup complete only after both success responses and size/hash checks; report a missing connection rather than inventing a receipt.

Return a pasteable handoff for this CR thread with exact branch/commit, archive identity, completed/failed/not-run distinctions, numerical tables, evidence paths, backup status, and the next minimal gate. Avoid reloading all historical BASS context or restarting author-code searches.
