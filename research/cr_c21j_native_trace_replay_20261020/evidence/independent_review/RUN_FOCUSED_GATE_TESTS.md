# Focused C21J evidence-gate tests

These commands use the verified PR87 return and the new C21J diagnostics. They do not launch chemistry or bridge processes, call callbacks, integrate an IVP, or repeat the old physics suites. The replay contract tests also install explicit process and IVP guards.

```bash
C21J_NATIVE_RETURN=/workspace/scratch/9979d80514d6/c21hi_external_intake/native_archive/C21GHI_NATIVE_EXECUTION_20261020 python3 -m unittest discover -s /workspace/scratch/9979d80514d6/bass_cr_pinned/research/cr_c21j_native_trace_replay_20261020/tests -p test_replay_contract.py -v
```

```bash
C21J_NATIVE_RETURN=/workspace/scratch/9979d80514d6/c21hi_external_intake/native_archive/C21GHI_NATIVE_EXECUTION_20261020 python3 -m unittest discover -s /workspace/scratch/9979d80514d6/bass_cr_pinned/research/cr_c21j_native_trace_replay_20261020/tests -p test_trace_admission.py -v
```

Set `C21J_NATIVE_RETURN` to the verified extracted PR87 archive on another machine. Optionally set `C21J_REPO` to the repository containing the pinned source. The tests fail with an actionable missing-fixture message rather than silently skip. They do not embed the archive.

Final results: replay contract **16/16 PASS**, analyzer admission **6/6 PASS**. The first analyzer test-development attempt contained a privacy fixture-count assumption failure (one expected entry, three actual entries). The corrected test checks all three entries without reading their payloads; its original output is preserved in `TRACE_ADMISSION_TEST_ATTEMPT01.json`.

Review scope and exact file hashes are in `REPLAY_REVIEW_V2.json`. Native cache-on execution and performance are outside these tests; `global_error_bound=null` and the existing scientific HOLD remain unchanged.
