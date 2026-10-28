# K=3 eV native same-bin high-low capacity: exact numerical evidence, resource HOLD

Unit CR_NATIVE_SAME_BIN_CAPACITY_NEXT, fixed K=3 eV, saved PHYS02 He marginal. Predecessor PR116 f9aeacf0736c5c51afaec1629c9270f7cfb54e8f, PR117 7ee33930472ed40b84461e30daad08c2f92101ff; no parent, central or other-owner branch mutation. Central baseline rei_bianchi 4824eec8526185b6b866a5e7e0dabdc624b5543c has 28/88 completed, CR delta0.

## Source and mathematical construction
Original PR116 Drive archive 4690891 bytes SHA256 87ddb7718d37895c3842b710a2af4f6419ffbc8ea38d0a55e0b1093217876311, actual GET, ZIP CRC PASS. Embedded ATTRIBUTION_ARRAYS.npz 233050 bytes SHA256 1c974c306b50f3deb86df712844f753b4402fb25e5dbc41c9a1de0254bf3ff47, 3200 active plus one separate ghost, original atom digest 2cfca578701a2355fa6f1f3f1f8a27c211e81b9b488f65cef1e1a89e4dbc7690. Binary64 inputs lifted exactly to rational weights/energies; no source-fit, RR, transfer, or IVP rerun.

High: 2E_h>K; low: 2E_l<=K. Same-bin high-low edges require E_h+E_l<=K. For bin b and each distinct high-energy t, set U_b(t)=sum_{E_h>=t}w_h and V_b(t)=sum_{low E_l<=K-t}w_l. Weighted Hall deficiency delta_b=max(0,max_t[U_b(t)-V_b(t)]); S_b=H_b-delta_b and S=sum S_b. Neighborhood nesting reduces the full min-cut to these finite high suffixes. Descending-high and ascending-low greedy matching constructs an exact rational primal attaining the cut. This is a classical weighted max-flow/Hall specialization, not a novel general matching theorem.

## Actual saved K=3 native result
3,201 positive atoms, 453 low and 2,748 high. Exact:
N=77906149556394634457/49039857307708443467467104868809893875799651909875269632
L=999870389230360121/3064991081731777716716694054300618367237478244367204352
S=323478918562118325/3064991081731777716716694054300618367237478244367204352
M=3456415883490050789/12259964326927110866866776217202473468949912977468817408.
S/N=0.06643458477237846; M/N=0.17746562514878358; W*S=5.276996081491804e-18 m^-3, W=5e19 s^2. The full-window bound 2d-C<=L+S implies at d=D a necessary C/N>=0.11103104037640514, and at C=0 a necessary d/N<=0.1358916404240498. This is only a NECESSARY outer bound, not sufficient polygon or joint-attainability claim. S>0 only for bin2 in this K3 sample, bin3 has no low vertices.

315 actual positive pairs; source K, bin and per-atom marginal checked exactly, primal/dual gap exactly 0. Parent M,D identities checked against predecessor. No actual physical K, exclusive He kernel, actual C/d, outside partner, donor work, EOS/T, absolute volume, physical native25, L4 or production completion claimed.

## Execution, failures and resource closure
Original 10/10 tests and 460 exact full-flow small fixtures passed, measured 1.77 CPU-s. First native attempt failed ATOM_SOURCE_BUNDLE_REQUIRED due double owner module loading, measured 1.62 CPU-s; preserved original failure. Corrected one-loader native run passed, 1.76 CPU-s, produced 315-pair witness SHA256 a9cfdc5162be6e0017e4b0e4c259a9e88467077c7f8727cceb095359770f29d8. Separate direct raw-NPZ, no-production-import checker independently enumerated Hall thresholds, checked all 3201 atom capacities and 315 pair supports, passed, 8.71 CPU-s; independent report SHA256 cc6622de45ca8f2804e31f003712342f121a3157397aa503be6308069be567a4. This is an independent algorithm, not a nonauthor review.

An additional exact-input audit found direct Atom(... float ...) could bypass Fraction parser. Targeted RED one-test failure took 1.79 CPU-s; guard repaired direct constructor and 11/11 GREEN tests passed in 1.75 CPU-s. Guard does not change rational native algorithm; native on patched code was not replayed. Saved-result-only native chart was visually checked after one render (3.05 CPU-s). Additional synthesis/chart controller cost not measured.

CRITICAL BUDGET: new frozen 20 CPU-s vs minimum observed 20.45 CPU-s, at least 0.45 over. Unmeasured controller/fixture/metadata CPU UNKNOWN_NOT_ZERO. Resource gate FAIL, preventive aggregate hard cap NOT_VERIFIED, new science allowance 0, auto-next OFF. Historical predecessor unused budgets not transferred. Separate nonauthor theory R6 and code C9 are NOT_RUN. Verdict: NUMERICALLY_CHECKED_NATIVE_PRIMAL_DUAL / RESOURCE_BUDGET_FAIL / INDEPENDENT_AUTHOR_REVIEW_PENDING / formal PASS_SCOPED WITHHELD.

Git R1–R5/C1–C7 was posted in grouped historical commits; actual stage-by-stage dual R2 backup ACKs for this new unit do not exist. The already verified dual-backup PR116 SOURCE is NOT a new K3 backup receipt. New archive backups must be verified independently before any dual-backup completion claim; missing receipts will not be retroactively invented. Do not merge or mutate parent. Future fresh budget and independent-author review are separately gated tasks.
