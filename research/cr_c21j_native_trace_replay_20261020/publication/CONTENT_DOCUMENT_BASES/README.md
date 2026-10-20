# C21J — native trace reconstruction and exact callback replay

C21J consumes the completed C21H/I native return in PR87. It reconstructs the
full physical RHS request stream and re-evaluates the frozen callbacks with
recorded native replies. It performs **no new native chemistry execution and
no new IVP integration**.

The frozen source is C21I content
`fe6bbaec2de5032b938aed0713623b9618ba70e6`. The returned evidence snapshot is
`d3eaf596e46be4f994723fb742237a7399c290ed`. Original H/I source, tests, native
raw, tolerances, and publication histories are inherited without modification.

## Findings

- The captured H base and I vectorized base agree bitwise in all 28 physical
  endpoint coordinates, all ledgers and endpoint diagnostics, all three raw
  segment result objects, and all 39 accepted physical-state records (including
  each cell's initial state).
- Each captured job expanded to 823 original RHS requests. The existing C21I
  full physical `(t,u)` cell LRU-16 has **69 hits and 754 misses**. The smaller
  native EVAL string has 100 hits on the baseline trace; those are a separate
  policy. The additional 31 pairs have different optical depths.
- Actual callback replay passed four cases: original H, I vectorized, and I
  exact on the I base trace, plus I exact on the I FD-half trace. Each case
  checked 472 replies / 40,432 binary64 values, derivative nodes, and physical
  summary reconstruction. Exact mode used 754 recorded table queries; each
  non-cache case used 823. These are not new native calls.
- The captured I vectorized job wall was 1.431935522 s and H was 1.211697710 s.
  This one sequential pair does not establish general performance. Actual
  native exact mode remains `NOT_RUN`; its performance is `NOT_EVALUATED`.
- `global_error_bound=null`. Existing scientific HOLDs remain in force.

The substantive report is [C21J_RESEARCH_REPORT_KO.md](C21J_RESEARCH_REPORT_KO.md).
The derivation, assumptions, literature and CAS checks are in
[theory/NATIVE_TRACE_EXACT_CACHE_NOTE_KO.md](theory/NATIVE_TRACE_EXACT_CACHE_NOTE_KO.md).
Current publication and backup state belong to the later closeout receipt,
not to an archive-time `PENDING` field.

## Input authority

Restore the native return into a new directory from
`C21GHI_NATIVE_EXECUTION_20261020T112300Z.tar.gz`:

```text
bytes   2568680
SHA256  2722e479b6205015a68f1393b8c537d21e63201bb57efd3cf850fe74e4668de3
```

The original compressed bytes were fetched and verified at intake. All 155
payload entries matched. The archive includes a bridge binary and three private
process inventories. The diagnostic programs never read those inventories;
they are excluded from this public C21J tree.

`replay_callbacks.py` requires the exact byte and canonical identities of
`INPUT_PINS.json`, including the complete 24-source/60-return file set. A user
supplied alternative pin map cannot redefine that authority. It also requires
the full successful hello/config/request/reply/terminal/EOF stream, with config
and result equality and exact request counters.

`analyze_native_trace.py` verifies five source hashes and first admits the
archive's fixed `PACKAGE_PAYLOAD_SHA256SUMS.txt`:

```text
bytes   20712
SHA256  40d61253fb5535435373c07150ff554ff708796902076168e171fb1f9301125a
```

Every return file read by the analyzer must occur in that manifest and match
its hash. An internally consistent replacement job receipt is insufficient.

## Reproduce only when an input or diagnostic dependency changes

Python 3.12 with NumPy 2.3.5 and SciPy 1.17.0 was used for callback replay.
The trace analyzer uses the standard library. No Rust compiler is needed for
these two diagnostics. Supply the frozen repository or a materialized source
tree with the exact files listed in `INPUT_PINS.json`; an old scratch checkout
is not assumed.

```bash
python3 research/cr_c21j_native_trace_replay_20261020/analyze_native_trace.py \
  --archive /absolute/path/C21GHI_NATIVE_EXECUTION_20261020 \
  --source-root /absolute/path/frozen_repo/research \
  --out /absolute/path/new_trace_analysis

python3 research/cr_c21j_native_trace_replay_20261020/replay_callbacks.py \
  --repo /absolute/path/frozen_repo \
  --native-return /absolute/path/C21GHI_NATIVE_EXECUTION_20261020 \
  --out /absolute/path/new_callback_replay
```

Outputs are create-only. Missing recorded points, conflicting replies, input
drift or an incomplete RPC stream fail explicitly. No interpolation, native
fallback or solver integration fills missing evidence. The accepted states
are consumed from the captured trace; the callback calculations themselves
are executed from the frozen source.

Focused gate commands are recorded in
`evidence/independent_review/RUN_FOCUSED_GATE_TESTS.md`. Do not treat the separate
9 reconstruction tests, 16 replay-admission tests, 6 archive-admission tests,
and saved-trace cases as a freshly executed complete physics suite.

The deterministic compressed request files in `evidence/trace_requests/`
contain new reconstructed data. Their manifest binds both the gzip bytes and
the original JSONL bytes. They do not replace or alter the PR87 native logs.

## Next NCP node

The next prepared native decision is one `common_ic / vigilode-rodas5p /
vectorized_exact / base` job, with current resource admission, protected CPU55,
one job and one worker, and the original 300 s / 200000-call bounds. Its live
source remains the published C21I content, not this diagnostic's source.
Use the separately supplied NCP packet and the existing H/I publication guards.
G's reference ladder remains an independent contract. The completed H and I
base/FD-half jobs do not need repeating for this node.
