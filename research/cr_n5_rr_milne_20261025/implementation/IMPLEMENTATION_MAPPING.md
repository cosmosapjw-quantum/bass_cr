# Frozen implementation map

Preparation status: **SUPPORTED_PENDING_REVIEW**. Root owns scientific admission
and publication. Input and code pins are in `PREPARED.json`; the immutable input
manifest includes all eight saved PR104 chains, three original384-atom tables,
the unchanged native C23B module/table/contract and saved REI thermal reference.

| Contract | Code and observable |
|---|---|
| C1 contribution and immutable reuse | `rr_engine.verify`, INPUT_MANIFEST and copied private NPZ/source atoms; no old generator/primary/source projection calls |
| C2 channel units, density, weights, source support | `rr_coefficients` calls unchanged native `Verner96.sigma_cm2` pointwise; target HII density0.1; d1; native13.6eV; heavy stationary target |
| C3 finite-chain map | `consume`: six old first RHS + RR probability/energy + six baths; three new conditional moments; two stable paired responses; one K0 response; 20 per case |
| C4 exact finite-chain identities | Per-RHS backward residuals; positive partition; six-bath/entry/CE/RR signed energy; rare relative resolvent bounds; source q/inactive terms preserved |
| C5 frozen controls and comparison map | `controls.py`: adapter rejection, units/scaling, zero density, mutations, RR-scale energy and analytic two-state chain. `primary.py`: prescribed grid and upper-domain comparisons |
| Contract7 rounded operator diagnostic | Intended operator K0+lambda; binary64 addition loss logged separately. Independent Decimal70 review reconstructs the real sum, rather than copying rounded diagonal |
| Resource and raw evidence | Minimal adaptation of saved v3 `dispatch.py`; CPU0 worker/CPU8 coordinator/CPU1 reviewer; native threads1,512MiB limit, cumulative60CPU accounting incl failed attempts/preflight; task-owned lease only |
| Saved-only figure | `plot_saved.py`: six R80,N2048 source rows, RR probability/photon energy/stable CE and time changes; no dense arrays or MTCS reconstruction |

Saved old solution uncertainty is inherited. Stable paired CE/time responses
use the accepted stored old solutions. Direct subtraction is diagnostic only.
Diagnostic electron-removal energy is not added as a third final RR reservoir.
Emitted photons remain retained radiation; atomic internal reward is negative.
No stimulation, PI feedback, composition feedback, total all-level RR or
sub-q continuation is activated.

## Bounded commands

From workspace root, with the frozen unit path:

```sh
python3 -B research/cr_n5_rr_milne_20261025/implementation/dispatch.py --unit research/cr_n5_rr_milne_20261025 --mode test --run-id n5_rr_milne_controls_20261025_v1
python3 -B research/cr_n5_rr_milne_20261025/implementation/dispatch.py --unit research/cr_n5_rr_milne_20261025 --mode science --run-id n5_rr_milne_primary_20261025_v1
python3 -B research/cr_n5_rr_milne_20261025/implementation/dispatch.py --unit research/cr_n5_rr_milne_20261025 --mode review --run-id n5_rr_milne_c9_20261025_v1
python3 -B research/cr_n5_rr_milne_20261025/implementation/dispatch.py --unit research/cr_n5_rr_milne_20261025 --mode plot --run-id n5_rr_milne_saved_plot_20261025_v1
```

The review command consumes independent `review/c9_independent.py`; it does
not import production modules. Each output directory is create-only. A failed
run remains intact and is charged. Prescribed controls precede the primary;
root receives any substantive failure without criterion changes.
