# R4E — N=768 bridge-rung authorization envelope and post-run decision contract

Status: **R4E_AUTHORIZATION_ENVELOPE_READY__NATIVE_NOT_EXECUTED**

## 1. Authoritative identities

- repository: `cosmosapjw-quantum/bass_cr`
- executable commit: `4c2c0be5171c74a52b4a6e96b04c33fa00c62481`
- executable tree: `2e1a3175a7d20cf9c0218fb15f07f72d4afcb425`
- R4D parent research HEAD observed before this loop:
  `e74fe9c6c6fe7545207c04efcb10566ecd146e94`
- historical resume archive:
  - bytes: `31849212`
  - SHA256: `630a80208331b7b37c02a77eae7435f6317d07439a4ea34b11885455fe53fa35`
  - ZIP CRC: PASS
- numerical context:
  `bb2a6d2cb7b598441e44294ae9d9499e983f6bfebe9ec4dcfdbc29b9ac7f1cda`

No new native build/load/evaluation was performed here.

## 2. Why N=768 remains worth running

R4D proved that N=768 cannot simultaneously satisfy the frozen
candidate-reference and N384->N768 refinement screens. It is nevertheless
required as a **bridge rung** if the project later wants to evaluate the
frozen consecutive-refinement quantity N768->N1536 without silently changing
the gate definition.

The scientific value of N=768 is therefore:

1. measure the actual bridge state at exactly the frozen physics/input;
2. measure the actual observed orders
   `p_ref` and `p_self`;
3. test whether the historic near-second-order regime persists;
4. quantify whether a *separately authorized* N=1536 rung is worth its cost.

N=768 is not a temporal-closure attempt in the strict dual-screen sense.

## 3. Empirical wall-time model from the exact historical archive

The restored historical `PROGRESS.jsonl` was read directly from the
SHA-locked archive. Incremental candidate-rung times were:

| N | new query times | new raw evaluations | incremental wall s | s/query | s/raw |
|---:|---:|---:|---:|---:|---:|
| 24 | 24 | 80 | 818.455 | 34.102 | 10.231 |
| 48 | 48 | 160 | 1650.007 | 34.375 | 10.313 |
| 96 | 96 | 316 | 3161.049 | 32.928 | 10.003 |
| 192 | 192 | 630 | 6138.470 | 31.971 | 9.744 |
| 384 | 384 | 1260 | 12231.598 | 31.853 | 9.708 |

The last-rung resolution pattern has mean 3.28125 raw evaluations per new
query. Nearest-neighbour projection of that resolution pattern to the new
N=768 midpoint grid predicts about `2520` raw evaluations.

Using the last two rung raw-evaluation throughput gives an empirical center
estimate of about `24493 s = 6.80 h`.

This is **historical-host throughput evidence, not a cloud guarantee**.
The current cloud CPU model and sustained performance have not been benchmarked,
and benchmarking native science merely to refine the estimate would defeat the
authorization boundary.

### Recommended wall envelope

For one bridge attempt I recommend:

`R4C_MAX_WALL_SECONDS=36000`  (10 h)

This is about `47.0%` headroom over the empirical 6.80 h center.
It intentionally remains far below the raw-attempt theoretical worst case.
If resolution qualification becomes much harder at the new midpoints, timeout
is an accepted bounded outcome and must not trigger an automatic retry.

The 60-second termination grace remains unchanged.

No KRW cost is inferred here. The code does not enforce a currency limit.
The user/provider must separately authorize a cost scope compatible with one
existing-host N=768 attempt for at most 10 h.

## 4. Post-N768 diagnostic contract

After a healthy run, record

    d_ref  = d(N768, reference)
    d_self = d(N384, N768)

and compute

    p_ref  = log2(d384_ref / d_ref)
    p_self = log2(d192_384 / d_self)

with frozen historical values

    d384_ref = 2.634560877280569e-6
    d192_384 = 7.904769432369909e-6.

Also compute constant-observed-order forecasts

    d_ref_pred_1536  = d_ref^2  / d384_ref
    d_self_pred_1536 = d_self^2 / d192_384.

These are scheduling diagnostics only. They do not change either 1e-6 screen.

Required consistency checks:

- all operator queries qualified;
- both candidate/reference norm-drift screens pass;
- `d_ref`, `d_self` finite and positive;
- triangle check:
  `d384_ref <= d_ref + d_self + numerical_roundoff_allowance`;
- distances decrease relative to the predecessor sequences before any
  extrapolation is interpreted;
- dual PASS at N=768 is classified as
  `METRIC_OR_EVIDENCE_INCONSISTENCY`, not success.

A healthy bridge rung terminates as

`R4E_N768_BRIDGE_COMPLETE__N1536_DECISION_PENDING`.

N=1536 is never launched automatically.

## 5. Literature-supported interpretation

SciSpace retrieval in this loop found literature supporting the use of
a-posteriori error information and asymptotic-order diagnostics for symmetric
or exponential time integrators, while also emphasizing that their reliability
is asymptotic and method/problem dependent:

- Auzinger, Hofstätter & Koch, *A posteriori error estimation for Magnus-type
  integrators*, M2AN (2019), DOI `10.1051/M2AN/2018050`.
- Auzinger, Koch & Thalhammer, *Defect-based local error estimators for
  high-order splitting methods involving three linear operators*,
  Numerical Algorithms (2015), DOI `10.1007/S11075-014-9935-8`.
- Descombes & Thalhammer, *An exact local error representation of exponential
  operator splitting methods ...*, BIT (2010),
  DOI `10.1007/S10543-010-0282-4`.
- Blanes, Casas, González & Thalhammer, convergence analysis of high-order
  commutator-free quasi-Magnus integrators for nonautonomous linear
  Schrödinger equations, IMA J. Numer. Anal. (2021),
  DOI `10.1093/IMANUM/DRZ058`.

These sources support measuring convergence/order rather than inferring it
from norm preservation alone. They do not certify this BASS implementation.

## 6. Wolfram status

The Wolfram connector was explicitly invoked repeatedly in this loop, but all
three available entry points returned an internal tool failure. Therefore the
new wall-time and post-run calculations above are **not claimed as freshly
Wolfram-verified**. They are direct deterministic arithmetic over the
SHA-locked archive evidence. The earlier R4D triangle-inequality result remains
unchanged.

## 7. Claim ceiling

Unchanged:

- capture = false
- production = HOLD
- all_bound = OPEN
- b_grid = NO_GO
- original_capture_gap_resolved = false
- continuous_global_supremum_bound = false
- continuous_trajectory_error_bound = false
