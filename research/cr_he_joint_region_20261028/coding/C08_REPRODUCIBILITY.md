# C8 — Numerical interpretation, reproducibility and inspected figure

All acceptance arithmetic is exact Fraction/integer arithmetic on the stored binary64 source values. No epsilon, float LP acceptance, quadrature, grid refinement or physical continuum limit is introduced. Accordingly the zero marginal/primal-dual residual is exact for this finite stored-input problem. It is not a claim that the physical source or its discretization has zero uncertainty. The exact decimal1/5 versus twice-binary-ghost boundary is deliberately preserved.

The build is g++13.3.0, -std=c++17 -O2, single-threaded iterative128-bit integer flow; Python3.12.14, NumPy2.3.5 and Matplotlib3.10.8 are recorded. The executable is42184bytes with SHA256c963a2914d2a0548ce142bd5159fa3ee922110137eb96fc48ca8235ab808d4ba. Current bytes match the actual build_v2 result. The controls/native receipts captured source/input/dependency hashes and actual commands; they did not have a separate prelaunch executable-hash field. C8 adds that explicit check to the runner for future non-build invocations and records it in the actual plot job. This is a provenance improvement, not a retroactive claim about a check that did not run. The independently verified event certificates establish the scientific result without trusting the generator binary.

Every actual attempt has a source snapshot, actual argv, frozen input/dependency manifests, stdout/stderr, exit code and measured receipt. No random seed is needed for these deterministic sorted constructions. The generic rational residual method has finite termination but no claimed native/global polynomial runtime. Native6404node/14931arc K6 flow was embedded in the whole native construction/consumer job; no isolated backend speedup or cross-cap timing comparison is inferred.

## Actual local resource ledger through C8

| Attempt | Status | Measured CPU-s | Charged CPU-s |
|---|---|---:|---:|
| build_v1 | FAIL, PID/procfs watchdog mismatch | 0.079626 | 0.179626 |
| controller metadata diagnostics | recorded, initial missing-path probe retained | unmeasured aggregate | 0.300000 conservative |
| build_v2 | PASS | 0.956505 | 1.056505 |
| controls_v1 | PASS | 0.202852 | 0.302852 |
| native_v1 | PASS | 17.819608 | 17.919608 |
| independent_v1 | PASS | 1.395590 | 1.495591 |
| plot_v1 | PASS | 2.094473 | 2.194473 |

Charged total is23.448655/40CPU-s. The remote R7 Wolfram call had requested5s timeConstraint but unreported CPU. Metadata/provider time and remote CPU are not silently counted as zero in an aggregate hard-cap claim. The local ledger will close at C9 after independent review; unused allowance is nontransferable.

## Saved plot and visual inspection

plot_v1 read only runs/native_v1/SUMMARY.json, SHA256611c34e95cc7535d24431101f5106a30b3e43ac334a22879bb45351923690d00. Solver invocation count is0. Exact fractions are converted to floats only for display. The PNG and SVG show the accepted K2/K6/K20 polygons on common d/N and C/N axes with equal aspect, closed boundaries and vertices. The title, all axis labels, numerical maxima and the conditional-physics footer were visually inspected in the actual rendered1920x720 PNG. No overlap or cropping required a new render.

PNG SHA256d4a2d1c8584412b07d543aac15c7fd7340dceeb3030d0d8b7ff85b7547c8e1a7; SVG SHA256885682222fcfc69c612307fd110ec4aaed334d3ea1165d8816c49a3473e89002. These identify the delivered figures; universal byte-identical plotting across font/library versions is not claimed. Scientific fraction results and event certificates remain the authoritative data.
