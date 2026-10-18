# C21F native NCP execution — 2026-10-18T13:55:35Z

This is additive execution evidence for `bass_cr` C21F.  The executable
source anchor is `f8359232df8d0dd4fe91fcdabeb6701eb06089ba`; the reviewed PR
#81 release/receipt/DAG head is `249d9b29b0adc5a8cf615a9999065aff26ff6900`.
The native owner is exactly `rei_bianchi@6ea2b1b4b3875c9163cafc45efe720afded43fc4`.

Execution used a new output directory, `taskset -c 62`, and the runner's
`git archive` build path.  It did not alter the owner checkout, production
checkpoint, watcher, or pre-existing worktrees.  CPU 55 was not used.

## Result

`exit_code.txt` is zero.  Python protocol tests: **56 passed**.  The Rust
bridge test binary reports **3 passed**.  Both scoped native matrices completed:

* common explicit IC, 3-energy, opacity 0.001; and
* original native MD14 12-cell centroid source, opacity 1.

Each matrix contains seven delta-point PreparedAbsorption comparisons and
BE/FULLMID/MIDPHOTO_ENDMICRO at 8/16/32/64 subdivisions, with independent
optical-depth-coordinate Radau output.  Raw `accepted_steps.jsonl`,
`native_points.jsonl`, fixture/source export, summary, analysis and Radau
files are retained here.  `MANIFEST.sha256` covers all retained files.

At 64 subdivisions, observed state-order sequences are:

| matrix | BE | FULLMID | MIDPHOTO_ENDMICRO |
| --- | --- | --- | --- |
| common IC | 0.998/0.999/0.999 | 1.995/1.992/1.962 | 0.999/1.000/1.000 |
| native MD14 source | 1.026/1.015/1.008 | 1.896/1.971/1.992 | 2.137/2.652/2.242 |

This is a fixed-source time-refinement observation only.  It is not a full
production-driver parity, full-48-source, source-age, spectral/angular,
Case-B, signed-Bianchi, or full-EoR validation; all of those remain HOLD.

## Provenance

* `build/native_point` SHA-256:
  `1e7265185960cd91c3c589057b3e29d191d83bce95e59d803a399f9eb234ad40`
* owner archive SHA-256 (not included because it is a reproducible 1.94 GB
  git archive):
  `b8296eef807899efc9d11e6c44c0ecc6af63443c72b8f21a56e81edcdfcd7f4c`
* bridge source SHA-256:
  `3812cf4fec625fdec32e47d737bec8e0306cc538372c5a2cf801d2b0cf590e2d`
* toolchain: Rust `1.99.0`, Cargo `1.99.0`, Python dependencies recorded in
  `resources.txt` and runner logs.

No failure file was produced.  The scoped runner reports the exact hold set in
`RETURN_TO_CHATGPT.json`.
