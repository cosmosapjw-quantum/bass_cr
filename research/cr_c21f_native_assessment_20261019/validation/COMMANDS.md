# Reproduce the v3 postprocessing validation

The commands below are the exact commands executed. The analyzer reads existing raw evidence and does not run a solver. Choose a new output directory for a further invocation; existing results are create-only.

## tests

```bash
/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest discover -s /workspace/scratch/4d2e4c44b70c/c21f_assessment_work/tests -v
```

## analyzer

```bash
/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3 /workspace/scratch/4d2e4c44b70c/c21f_assessment_work/analyze_native_evidence.py --source /workspace/scratch/4d2e4c44b70c/bass_cr_snapshot/research/cr_c21e_event_native_20261018 --evidence /workspace/scratch/4d2e4c44b70c/bass_cr_snapshot/research/cr_c21e_event_native_20261018/evidence/C21F_NATIVE_NCP_20261018T1358Z --receipts /workspace/scratch/4d2e4c44b70c/intake_receipts_01.json /workspace/scratch/4d2e4c44b70c/intake_receipts_02.json /workspace/scratch/4d2e4c44b70c/intake_receipts_03.json /workspace/scratch/4d2e4c44b70c/intake_receipts_04.json --executable-manifest /workspace/scratch/4d2e4c44b70c/bass_cr_snapshot/authority_pr81/C21F_EXECUTABLE_MANIFEST.json --out /workspace/scratch/4d2e4c44b70c/c21f_assessment_work/results_v3
```

`--source` is the work-unit directory in the GitHub snapshot. `--evidence` points to the existing native NCP evidence. The PR81 executable manifest is a separately retained source authority; the four intake receipts bind local raw files to GitHub bytes, Git blob IDs, and source refs. These are independent from the evidence MANIFEST.sha256 and canonical fixture digests.
