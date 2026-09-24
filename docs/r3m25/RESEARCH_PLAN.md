# R3M25 physical t=0 event-window contract

Parent: `ddcfd91eca55f9d1a2e1d846737c26e2d9febb45` on the dedicated
R3M24 branch. This is an opt-in successor. The R3M24 two-window result is
`REFERENCE_FOR_STRANG` only; production remains `HOLD`, b-grid `NO_GO`.

Use the sealed B2 `closest/g001152` generation, verified with R3M24's
same-descriptor guard. Advance the frozen fixed-CAP Strang runner exactly 42
B2 steps to step 1194. This warmup costs 42 kinetic FFT pairs, is saved only
as a derived-state digest, and is **not** a historical checkpoint. The
four-B2-step comparison interval is
`[-0.016665231363186095, 0.033330462726373966]` atomic units and
strictly brackets physical t=0. Both methods start from the same derived
state, H/CAP/grid/box/energy/b and complex128 representation.

The primary self-scaled denominator is the physical raw-L2 distance between
CF4 n4 and n8 over the entire event window, fixed before execution. Compare
CF4 n16 to n32, an n8 action-substep 2-to-4 repeat, and an n16 tighter-inner
repeat against **1% of that denominator**. A tighter run with identical
actual work is skipped and does not supply independent evidence. The
same-state Strang S4/S8/S16 minimum distance to CF4 n32 supplies a separate
`REFERENCE_FOR_STRANG` scale; do not substitute it for the self-scaled gate.

For CF4 order, compute `log2(d4,8/d8,16)` and `log2(d8,16/d16,32)` only if all
three distances exceed 100 times the measured changed-work repeat floor and
128 machine eps times the endpoint physical norm. A fourth-order-compatible
local result requires both observed exponents in [3, 5]. Below that floor,
report `UNRESOLVED_FP_FLOOR`; outside that interval, report
`NO_GO_LOCAL_ORDER` for this frozen event window, not a production conclusion.
The empirical repeats are not an absolute floating-point error certificate.

The later owner-directed Host reservation for the resource increase fixes one
fresh GPU attempt, 4,000 kinetic FFT pairs total including probe and warmup,
7,200 s total, 3,600 s event comparison, sampled GPU free >=2 GiB and host
available >=8 GiB. The configured Arnoldi basis ceiling remains 10. The
required worst-case count is 3,879 pairs, including all repeats at basis
dimension 10; it fits the new 4,000-pair cap. The superseded 3,000-pair Host
reservation was not executed and is preserved in routing evidence.

The actual GPU command must be enclosed in a process-group watchdog with a
3,600-second whole-process deadline and a 10-second TERM-to-KILL grace. This
stronger whole-process deadline also bounds the event comparison and includes
CUDA inventory, allocation and cleanup that cooperative kernel checks cannot
interrupt. If it fires, the Host writes a first-failure timeout receipt if the
worker could not, and never retries. The worker also checks free host capacity
for the next endpoint transfer and immediately afterward. A resource stop is
`RESOURCE_LIMITED_NOT_NUMERICAL_NONCONVERGENCE`, not a numerical failure.
No acceptance threshold is loosened.

Pre-run gates: exact source/config/selection bytes, sealed generation intake,
CPU tests, CLI/compile, runtime identity, fresh output reservation and explicit
contract SHA. Outputs are create-only: contract, preflight, warmup receipt,
result/manifest or first failure. No B3 full collision, preparation, finer h,
projection, checkpoint write, main merge or production admission in this work
unit. B3 requires a subsequent new contract even if this local gate succeeds.

## Fresh preflight-residency repair contract

The first SHA-frozen attempt stopped at GPU preflight after one matvec:
`minimum_gpu_free_bytes=1143472128 < 2 GiB`. No warmup or event comparison ran.
Its `ATTEMPT/FIRST_FAILURE.json` and contract remain immutable. The cause was
simultaneous retention of the Strang runner's kinetic phase/mask/half-CAP arrays
and fifteen held basis-sized probe arrays. This is a resource-layout failure,
not a convergence observation.

The successor preflight retires those three split-step arrays before allocating
held full-H probe arrays, as R3M24's proven probe already does. After all three
probe matvecs, it releases that probe runner and state, creates a fresh runner,
then performs the same 42-step warmup and frozen comparisons. The extra setup
does not change the Hamiltonian, CAP, state bytes, timestep, observable, method,
precision, or acceptance thresholds. A CPU regression asserts the arrays are
absent before held-basis allocation. Run at most one new fresh attempt with a
new source commit and contract SHA; never reuse or overwrite `ATTEMPT`.

Pre-run independent review also found that the inherited Strang/parity helper
checks the host reserve only after six large endpoint transfers. The successor
copies its exact operation schedule into a local guarded helper, checking the
next endpoint's bytes before each transfer and sampling host/GPU reserve
immediately afterward. A CPU regression counts all 34 kinetic pairs and six
guarded transfers. Another checks that the probe runner is released before
constructing the warmup runner. The historical helper remains untouched.
