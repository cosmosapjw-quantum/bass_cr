# CR_PHYS02_RR_BOUNDFREE_ENVELOPE_V1 | 다음 대화 handoff

$physmath-research-loop $scispace $exa $wolfram

PROJECT=cosmosapjw-quantum/bass_cr
UNIT=CR_PHYS02_RR_BOUNDFREE_ENVELOPE_V1
PARENT_PR=125
PARENT_HEAD=acf34ccb4229c002d9ad80a06a6d88cefb66d2fd
CHILD_PR=PENDING_POST_PUBLICATION_READBACK
PARENT_SOURCE_ZIP_SHA256=8e9b58236819146f4929aa4647dafdb1dc21b97b2f129ec4035291bb73a1ed2e
PARENT_PR110_NESTED_ZIP_SHA256=5392bc1bf159d0b23d7530a541f894e201231c3df874d6c547474b7517654c58
PARENT_PHOTON_NPZ_SHA256=e171824cf5fc3ba232fbbd4def6fc8cf6c855ca9e7d05506e4e4426c9416688f
VERNER_HI_HEI_TABLE_SHA256=a9ae2f7e7393de6f9ad89376cf5dd4be84da60cb3dadde3be37a4d3bd5989492
CENTRAL_DAG=28/88
EXTENSION_DAG=0/3
NEW_SCOPED_AUX=1/1_REVIEW_HOLD
NEW_WORKFLOW=18/20
R6=NOT_RUN_DISTINCT_AUTHOR
C9=NOT_RUN_DISTINCT_AUTHOR
AUTO_NEXT_NODE=false

## Restore / reproduce
1. Verify parent PR125 HEAD unchanged and no owner branches moved, then restore complete SOURCE archive including original nested parent source ZIP.
2. In isolated directory, run `python rr_boundfree.py --source-zip BASS_CR_PHYS02_RR_IONIZING_PHOTON_SOURCE_20261029.zip --output results`.
3. `python -m unittest -v test_boundfree` and `python -O -m unittest -v test_boundfree`, then `python independent_reference.py` and `python validate_and_plot.py` (inspect resulting two PNGs).
4. Compare emitted source `2.729441124610644e-25 m^-3`, first absorption lower `6.536559924836170e-27`, upper `1.719391366604854e-26 m^-3`, 256 mpmath checks, 16 CSV time×emission×target rows and byte source locks.
5. Do not silently replace PR125 fixed 100K source with REI radiation bath, REC HD data, BASS_HE nuclear DD cross section or Bianchi E-Vlasov history. These are distinct physical frames/sources.

## Physics limitations
- Verner 1996 original H I and He I Table-1 fits, with `((x-1)^2+yw^2)` and `1 Mb=1e-22 m²`; threshold 13.60/24.59eV.
- Frozen homogeneous stationary density and straight line at c to T=1e10s; source has four integrated time bins with unknown emission-time distribution, hence only endpoint envelopes.
- This is model-derived first absorption diagnostic, not physical cosmic optical depth, actual ionization, transport, deposition or heating. Photoelectron excess is *available initial energy*.
- Do not promote `native25`, `L4`, `production`, missing exclusive He kernel/K/clock/normalization/ownership/stopping; aggregate CPU cap unverified; old PR118 resource fail.
- Distinct-author R6/C9 still needed for any review release. No automatic next node. Central 28/88 unchanged.
