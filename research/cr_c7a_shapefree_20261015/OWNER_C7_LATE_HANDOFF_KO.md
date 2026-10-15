# SOURCE07 C7/C8 intake and reproducible Git test command

## Verified late owner readback, 2026-10-15 KST
Actual authorized Ubuntu owner checkout was read-only. SOURCE07 C7 is already committed in `rei_bianchi` at `9b9a0bb7`, with latest head observed `823b1de0d5ec3ff90ee40d5cb65c8315cb443f62` (other AX08 work advanced meanwhile). Its actual `research/source07_c7_support_20261015/{REPORT_KO.md,NEXT_C8.json}` show a source-age support-tracked q-grid and two-source-age oracle. Do not duplicate its Rust support arrays, production code or old source identity.

The owner q0 nE256 FLRW two-impulse benchmark reports HI relative error **-0.004412548342069722** for pooled N/U positive closure and **-0.004412548342073608** for support-clipped pooled closure; two truly separated age lanes yield **+3.2450997444755103e-10**. This is manufactured equal-count z20/z4 injection plus frozen gas, not a full EoR source history. The support guard does NOT remove age-induced species opacity error. SOURCE07 C8 next requests bounded age/spectral memory, source-specific H I/He I/He II error budgets and time-variable gas; no full coupled H/He/Tg admission.

This bass_cr PR is **complementary and not a second support-guard implementation**. It provides the distribution-free permissible range for each current q-bin species' one-step photoevent/heat from N, U_ref, true bin support and proper gas. Its two-age manufactured test deliberately uses different redshift ratios and prior attenuation; it is not labeled identical to the owner's genuine Bianchi age-impulse setup. C8 may use its bound width as a stop/refine indicator. Not even a very narrow interval certifies source Jacobian, geometric work, evolving H/He chemistry, EOS or global scientific outputs.

## Run the tracked Git version

These original prerequisite modules are already committed in the stacked PR ancestry. The new PR includes actual new source/test files. From an isolated checkout of the PR branch (not in the owner rei_bianchi tree):

```bash
ROOT=research
export PYTHONPATH="$ROOT/cr_c7a_shapefree_20261015/src:$ROOT/cr_c10_source_subcells_20261015/src:$ROOT/cr_c9_curvature_20261015/src:$ROOT/cr_c5_budgeted_cohorts_20261015/src"
python3 -m pytest -q research/cr_c7a_shapefree_20261015/tests/test_moment_envelopes.py
python3 research/cr_c7a_shapefree_20261015/src/moment_benchmark.py --single 64 128 256 512 1024 --preview 10000
python3 research/cr_c7a_shapefree_20261015/src/cold_scaling.py --bins 512 --reps 2
```

Full standalone relocated code, base dependencies, tests and CAS evidence are independently preserved in archive `BASS_CR_MOMENT_ENVELOPES_20261015_SOURCE.zip` SHA256 `baafa2b360f85e08cd2f4c7eba89f80c9395a53d481d45201eb4161a6c6b0502`, Drive `1ds67Q4rlKBHEFoTrs25yo18wzTcKXMxS`, Dropbox `id:BSpOijBcT10AAAAAAD703w`. The ZIP predates this late status-only readback; it remains immutable. Source and tests were actually rerun on both the ChatGPT local runtime and the authorized Ubuntu workstation: 31 PASS each. Native delegated subagents NOT_RUN. Original owner files or Codex process were not modified by this supplier.
