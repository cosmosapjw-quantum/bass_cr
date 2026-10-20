# Plan evidence portability addendum

SUMMARY_v2.json supersedes SUMMARY.json for the final test-source identity
and execution count. Original raw receipts/logs and the initial summary are
retained unchanged as history.

After all 13 pilot methods passed, the one plan method was corrected so that
INPUT_IDENTITY.manifest_path remains recorded host-location provenance.
Its absolute-path form is checked; every other identity field, including the
full manifest SHA and every pinned file record, still compares exactly.
This permits the existing completed plan evidence to be inspected from a
different host directory. No runtime or execution manifest was changed.
The earlier tested source is preserved in main_test_source.py.

Only the affected plan method was rerun: PASS, exit 0, wrapper wall time
1.000009431 s. This is a current-sandbox contract test; execution on a second
host is not claimed. No native process, ODE, or affinity mutation occurred.
Existing plan payload hashes were unchanged.

Final unique coverage remains 13 pilot methods plus 1 newly added optical
method. Across the initial helper/optical run, 3-method main run, and 1-method
portability recheck, 15 method executions occurred. There was no failure in
these receipts and no fresh all-method rerun. The historical 12-method optical
summary and prior targeted return-trace receipt remain separate.
