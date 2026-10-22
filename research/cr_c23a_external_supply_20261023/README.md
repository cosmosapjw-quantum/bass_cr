# C23A — external source contracts and sandbox components

Read [REPORT_KO.md](REPORT_KO.md) first. This is an additive source/component research packet for BASS_CR / REI_BIANCHI. It preserves the C21O–C22D results and all failed attempts; recovery ran no completed scientific job.

## Completed components

- P19 v1 fiducial H/He primary rates: 59 redshifts, exact source nodes, positive photo-only subflow, 826 frozen exposures and 1652 half-step compositions. This is not a cosmological thermal history.
- FS2010 finite electron response: MIT 21cmFAST mirror, explicit source-axis restrictions, positive piecewise-linear spectral integration and precontraction. Construction-inclusive paired timing median 4.91144 for 64 queries. No ODE speedup claim or physical 21-state coupling.
- Historical ENDF neutron/T beta energy-domain coverage: conditional moment bounds plus a separately labelled F=1 illustrative spectrum. This is not evaluated beta transport or nuclear network closure.

## Entry points and evidence

`photo_subflow.py`, `igm/p19_uvb.py`, `deposition/fs2010_operator.py`, and `nuclear/beta_domain_coverage.py` are the reusable components. Source, unit, validity, and ownership contracts are adjacent. `review/integration_cr/consume_mit_mirror_example.py` demonstrates public-only reuse; its one new input actually passed in `review/integration_cr_public_smoke_20261023_v1/`.

Existing audit scripts record old run IDs and some original acquisition paths. Do not run those scripts merely to restore results. Use the saved run evidence. A future scientific execution requires changed input, a new run ID/output path, actual available resources and a cooperative lease; native thread count is 1 per worker. CPU55 is protected and absent from this sandbox.

`run_source_campaign.py` enforces a bounded worker and create-only output. Read its contract before a new campaign. `analyze_saved.py` only consumes saved results; final figures are `analysis_v3/` at 180mm. Direct 90mm reduction was not admitted. Observed package versions are in `ENVIRONMENT.json`; this task installed no dependency.

## Publication and restoration

`PUBLICATION_MANIFEST.json` identifies the exact Git payload (self-excluded). Large audit JSONs have lossless `.json.gz` counterparts for Git; the full delivery ZIP retains the originals. Original v1/v2 figure images and private acquisition evidence are retained in that ZIP. `ARCHIVE_ONLY_MAP.json` records the split. This split does not turn a scoped audit into a full remote audit.

`restore_c23a.py` reads and validates the same memory bytes before opening a ZIP, verifies CRC/member SHA/size, and creates a new destination. It never executes a scientific calculation. Supply the exact size and SHA from the separately delivered final authority:

```bash
python restore_c23a.py --zip PATH_TO_DELIVERY.zip --size EXACT_SIZE --sha256 EXACT_SHA --verify-only
python restore_c23a.py --zip PATH_TO_DELIVERY.zip --size EXACT_SIZE --sha256 EXACT_SHA --dest NEW_DIRECTORY
```

`STAGES.json` and `NEXT_DAG.json` are the immutable pre-publication snapshot. Provider ACKs/readbacks, actual commits and the final C10 state belong to the separately delivered final authority and transport receipt. No triple-backup claim follows from two successful providers.

Full thermochemical/radiative closure remains OPEN; full high-energy nuclear and general triaxial/tilted/polarized CMB remain HOLD. Missing species/rates are never zero-filled. `global_error_bound=null`.
