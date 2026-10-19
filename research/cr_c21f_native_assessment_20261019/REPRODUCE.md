# Reproduce the new assessment from the existing GitHub evidence

The primary raw source is bass_cr PR82 at c4a502e0c931a201edfa3c7046f7a91230c2278f. The new assessment branch preserves that raw evidence and adds only this directory. The original C21F executable source is f8359232df8d0dd4fe91fcdabeb6701eb06089ba, with all 17 executable-manifest files byte-identical.

Use an existing checkout containing PR82 and this assessment. Neither analyzer imports the solver or invokes the native executable. Do not apply old embedded recovery patches. The archive accompanying this assessment contains new analysis and provenance, not another copy of the 23 MB raw text or old source ZIP.

## Portable commands

Set the two paths to the actual repository and a new, unused scratch output parent.

~~~bash
export C21F_REPO=/absolute/path/to/bass_cr
export C21F_POSTPROCESS_OUT=/absolute/path/to/new-unused-output
export C21F_ASSESS="$C21F_REPO/research/cr_c21f_native_assessment_20261019"
export C21F_SOURCE="$C21F_REPO/research/cr_c21e_event_native_20261018"
export C21F_RAW="$C21F_SOURCE/evidence/C21F_NATIVE_NCP_20261018T1358Z"

python3 "$C21F_ASSESS/analyze_native_evidence.py" \
  --source "$C21F_SOURCE" \
  --evidence "$C21F_RAW" \
  --receipts "$C21F_ASSESS"/inputs/receipts/intake_receipts_0[1-4].json \
  --executable-manifest "$C21F_ASSESS/inputs/authority/C21F_EXECUTABLE_MANIFEST_PR81_249d9.json" \
  --out "$C21F_POSTPROCESS_OUT/assessment"

python3 "$C21F_ASSESS/audit_native_points.py" \
  --snapshot "$C21F_REPO" \
  --receipts-dir "$C21F_ASSESS/inputs/receipts" \
  --out "$C21F_POSTPROCESS_OUT/point-audit"
~~~

Both output directories are create-only. Existing results are rejected. The analysis code uses only Python's standard library.

The input receipts retain the real relative source path, original byte length, SHA256, Git blob SHA1 and actual source commit from the current intake. Their incidental local absolute paths, if present in the results or invocation log, are provenance from this run rather than a requirement for a future checkout.

The exact commands actually executed, UTC times, interpreter path, exit codes and measured wall time are preserved in validation/COMMANDS.md and validation/VALIDATION_RECEIPT.json. The published results/ directory is the final v3 output; v1/v2 were intermediate local postprocessing outputs and did not modify the evidence.

## Targeted tests and plots

The five new analyzer tests verify malformed fixture rejection, missing or corrupted raw input, summary mismatch, sign-cancellation diagnostics and refusal to overwrite existing output. The historical 56 C21F tests are separate evidence and need not be rerun for this postprocessing.

~~~bash
python3 -m unittest discover -s "$C21F_ASSESS/tests" -v

python3 "$C21F_ASSESS/make_figures.py" \
  --evidence "$C21F_RAW" \
  --out "$C21F_POSTPROCESS_OUT/figures"
~~~

Plots require NumPy and Matplotlib. This run used Python 3.12.14, NumPy 2.3.5 and Matplotlib 3.10.8. Figure data comes directly from immutable fixture/result/Radau files and records each input SHA256 in figures/FIGURE_DATA.json.

## Verification coverage

- Whole intake: 167 raw text files received; 166 of 168 immutable manifest entries byte-verified. The other two entries are binaries that were not freshly received. The manifest file itself is separately Git-blob verified.
- Terminal/step analyzer: 126 selected GitHub-identified inputs, including 108 immutable raw payloads and all 17 executable source/dependency/test entries.
- Point auditor: 26 JSONL files, 27,140 request/response pairs; raw-byte and Git-blob correspondence plus original native-wrapper tolerance rules.
- Binary identity: build/process metadata linkage only in this turn. This is not a fresh binary readback or a native replay.

## New native work remains separate

The next bounded native work is a reference-tolerance ladder and, if needed, only new n=128/256 native-source FULLMID/hybrid levels. Existing 8/16/32/64 results remain immutable. Before launching, inspect current NCP resources, other campaigns, dirty files, watchers and checkpoints. The current assessment did not obtain that live inventory because the device-control service reported a monthly quota error.
