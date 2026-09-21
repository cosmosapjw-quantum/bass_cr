# START HANDOFF PROMPT — BASS CR R3M10 local reproduction

You are continuing the BASS cosmic-ray charge-exchange thread from canonical checkpoint `R3M10_LOCAL_REPRODUCTION_PACKAGE`. Work only inside this package/repository copy and preserve every existing artifact. The scientific target is **an independent paper-based calculation of H+ + H(1s) bound electron capture at 50, 100, 225 keV/u**, beginning with 100 keV/u single-impact-parameter tests. The original Nichols et al. 2026 code/data are unavailable. **Never claim byte/code reproduction of Nichols.**

Read in this order: `00_READ_FIRST_KO.md`, `docs/CLAIM_POLICY.md`, `docs/LITERATURE_AND_METHOD_LOCK.md`, `docs/LOCAL_RUN_GUIDE.md`, `R3M10_STATUS.json`, then the code. Verify `MANIFEST.sha256` before mutation.

Frozen physics contract:
- target frame; straight-line projectile `R_P(t)=(b,0,v t)`;
- electronic Hamiltonian `H=-1/2∇²-1/r-1/|r-R_P(t)|`;
- projectile bound ket carries Galilean factor `exp(i v z-i v²t/2)` plus its stationary energy phase;
- primary TDL capture is explicit projectile-bound-state projection;
- Nichols-style finite region `z>capture_plane` is a comparator only;
- `sigma=2π∫b P_bound(b)db` only after b-grid convergence;
- at finite separation, combined nonorthogonal channel closure uses Gram projectors;
- no source spread -> covariance and no source voting -> production central.

The package has two independent lanes.

**TDL lane** (`cr_repro/tdl.py`): cell-centered 3D Cartesian grid, second-order split-operator FFT, configurable mask absorber, imaginary-time discrete H(1s) preparation, explicit n<=nmax projectile hydrogen projection, finite-region comparator, checkpoint/restart, NumPy/CuPy backend. The cell-centered grid is an intentional independent discretization to avoid nuclear singularities at nodes. `P_bound_truncated_nmax` is not total all-bound capture.

**one-electron AOCC lane** (`cr_repro/aocc.py`): reuses only provenance-locked analytic Cartesian Gaussian/ETF primitives from W1R (`vendor_w1r/gaussian_cartesian.py`). It is a new one-electron two-center Hamiltonian. Do not import W1R spin S=0/1, H-minus rearrangement, or A3/A4 physics. Target and projectile centers both carry bound+pseudostate expansions. Final capture is the metric projection onto negative-energy projectile states.

Immediate execution protocol:
1. `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && pip install -e .`
2. `pytest -q`. Stop on failure and repair with a regression test before proceeding.
3. Run both smoke configs. Record runtime, backend, hashes, ground-state energy, norm, capture outputs.
4. Run **TDL 100 keV/u b=2 a0 baseline only**, in bounded restartable chunks if needed. Do not launch a full b-grid yet.
5. Run TDL `dt=0.025`, `capture_plane=25`, and `z_stop=75` variants. Add exactly one box/absorber variant and one spatial-grid refinement that fits available VRAM/RAM. Keep capture plane and final propagation time independent, because R3M7 showed the published preprint/final scaling preserved the same effective continuum threshold.
6. For each TDL run, compare `P_bound_truncated_nmax`, `P_region`, norm, discrete initial H energy, finite-grid projector norms, and where available the n=1 `eps_b/eps_c` estimator certificate. Diagnose, do not tune toward Nichols.
7. Run AOCC baseline and large-basis configs at 100 keV/u b=2. If basis difference is not small, expand/repair the symmetric target+projectile pseudostate basis before any b integration. Preserve Toshima-style two-center completeness logic.
8. Only after both single-b lanes are stable, construct a minimal adaptive b-grid for 100 keV/u. Require explicit b-tail extension. Then and only then compute `2π∫bP(b)db`.
9. Compare with the frozen experimental/theoretical authority lanes in the parent CR dossier. Do not choose a production central unless the source-admission thread separately closes that gate.
10. 50 and 225 keV/u come only after the 100 keV/u procedure is frozen.

Required durable outputs per run: immutable config, code hash, environment versions, progress/checkpoint state, result JSON, stdout/stderr, wall time, peak memory if obtainable. Every scientific change gets a test. Keep failed attempts in a failure ledger, not overwritten.

Escalation strategy: use cheaper agents for code navigation/test writing and expensive reasoning agents only for (a) Coulomb/grid convergence pathology, (b) ETF/phase or nonorthogonal-metric algebra, (c) disagreement between TDL and AOCC after each lane is internally converged. Do not spend expensive turns re-reading the full history; this prompt and the package contracts are the working context.

Stop condition for the first local session: return a compact handoff package containing the smoke results, 100-keV/u b=2 TDL convergence table, 100-keV/u b=2 AOCC basis-convergence table, any failures, and an explicit GO/NO-GO for launching the 100-keV/u b-grid. If GO is not established, do not run the b-grid.


Known pre-handoff smoke evidence (do not treat as physics): TDL reduced-grid `dx=1 -> 0.8` changes n=1 capture by 45.48%, while `dt=0.12 -> 0.06` changes it by 1.559%; therefore spatial convergence is the immediate TDL blocker. AOCC small-basis `dt=0.4 -> 0.2` changes projectile-bound probability by 0.0942%, with metric norm conserved to ~1e-14. A larger ns6/np4 trajectory exceeded the current bounded runtime and has no scientific result. The initial state is **NO-GO for b-grid; GO for single-b local refinement only**.
