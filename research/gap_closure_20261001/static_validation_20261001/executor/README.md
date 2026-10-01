# Frozen G02 and G03 native execution adapters

Both adapters are delivered code. Neither is an authorization, and no native call was made while implementing or testing them. They share the unchanged numerical worker, strict input/native verification, atomic attempt ledger, bounded dispatcher and cooperative-host resource checks from the pinned prior source. The new admission, whitelist, producer/return and supervisor modules are separate from the historical eight-query A1 executor.

| Scope | Producer | New queries | Reuse | Raw cap | Max workers | RAM/worker | Wall |
|---|---|---:|---:|---:|---:|---:|---|
| G02 FD | `fd_executor.py` | 66 | 6 saved centers | 726 | 8 | 1GiB | explicitly approved positive limit |
| G03 signed48 | `g03_executor.py` | 2 | 0 | 22 | 2 | 4GiB | ≤900s |

G02 admits only the frozen72-snapshot plan minus its six hash-verified reuse pairs. G03 admits only z=-48 and+48. Either adapter rejects the other's query counts, scope, context and authorization prefix. Scientific controls remain unchanged: full18-channel B0, 100keV/u, b=2, same-center order20 and the existing11-rule ladder/screens. No propagation, automatic follow-up, tolerance relaxation, old nonce reuse or inherited temporal certificate is allowed.

## Prepare on the exact published clean commit

The checkout must contain the delivered source and saved reuse fixtures; the portable checkpoint contains the reused JSON/NPZ bytes. Use the restored frozen `runtime_inputs/` and `native_build/` from the verified A1 preparation, not a regenerated bank or recompiled library. The preparation programs verify these bytes without dlopen. They write a create-only source/input/native package, live resource receipt and **UNAPPROVED** proposal tied to the current commit/tree and exact paths.

From the repository root, using its NumPy2.3.5/SciPy1.17.0 environment, choose a fresh authorization ID and explicit cost/wall scope:

```sh
PYTHON=/absolute/path/to/project/python
EX=research/gap_closure_20261001/static_validation_20261001/executor
env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 "$PYTHON" -I -B "$EX/prepare_fd_authority.py" --inputs /absolute/frozen/runtime_inputs --build /absolute/frozen/native_build --out /absolute/new/G02_package --authorization-id G02-FD-YYYYMMDD-UNUSED_ATTEMPT --workers 4 --wall-seconds 3600 --cost-scope 'Explicit proposed scope for review; no new VM or resize'
```

G03 uses `prepare_g03_authority.py`, a `G03-STATIC48-...` authorization ID, at most2workers and at most900seconds. Those command examples **prepare only**; a live proposal and its exact hash must be reviewed for a genuinely fresh authorization before running the corresponding supervisor. No old approval field or merely setting an environment variable constitutes user approval.

The run command uses the matching supervisor (`supervise_fd.py` or `supervise_g03.py`) with `--proposal`, `--source-pins`, `--inputs`, `--build`, `--out` and `--approved-proposal-sha256`. All arguments must match the approved live proposal exactly. Only after that approval set the matching gate to its exact phrase:

| Supervisor | Environment gate | Exact value |
|---|---|---|
| `supervise_fd.py` | `ALLOW_NEW_NATIVE_G02` | `YES_I_AUTHORIZE_66_G02_STATIC_FD_QUERIES` |
| `supervise_g03.py` | `ALLOW_NEW_NATIVE_G03` | `YES_I_AUTHORIZE_TWO_G03_SIGNED48_STATIC_QUERIES` |

The supervisor repeats nonnative prelaunch validation, starts the isolated child in a dedicated process group, monitors its deadline/first failure, terminates only its own group, verifies teardown and packages partial evidence as needed. Each child rechecks clean commit/tree, exact source closure, bank/native bytes and architecture, NumPy/SciPy versions, all thread limits, CPU/RAM admission, deadline, fresh output and globally unused nonce. Authorization is durably consumed before creating the pool; each worker repeats source/bank/budget checks before the unchanged native constructor. Every raw attempt is reserved before evaluation. No automatic compilation or restart is present.

## Returned evidence

G02 publishes66 qualified new JSON/NPZ pairs, preserves six old pairs, checks exact72-coordinate coverage, and writes `ALL_SNAPSHOTS_MANIFEST.json`, `FD_RESULTS.json` and the provider/execution/supervisor receipts. The offline FD consumer still requires resolved h-order behavior at every signed center; code completion never closes physical G02.

G03 publishes exactly2 qualified new pairs. Its postprocessor reconstructs each saved resolution from the unchanged same-center blocks plus that resolution's raw cross blocks, retaining S/H/D/W and eigensystem diagnostics. It writes `RHO_SAMPLES.json`, per-query diagnostics and `G03_RETURN_ANALYSIS.json`; frozen predictions are scored before refitting. No state is read, so P and Pdot remain unavailable. No following±44/±64 pair is launched.

Both returns preserve capture=false, production=HOLD, all_bound=OPEN, b_grid=NO_GO and all continuous-certificate ceilings. Raw counts and receipt/backup verification levels must be reported separately from scientific validity.

## Focused verification

```sh
python -B -m unittest discover -s research/gap_closure_20261001/static_validation_20261001 -p test_static_validation.py -v
python -B -m unittest discover -s research/gap_closure_20261001/static_validation_20261001/executor -p 'test_*.py' -v
```

Tests use synthetic operators and saved historical bytes, native-load traps, incompatible scope/nonce/resource cases, first-failure cancellation and create-only publication. Actual native orchestration on the external host remains unexecuted until a new live authorization exists.
