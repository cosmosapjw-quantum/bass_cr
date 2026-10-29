# Copyable handoff: BASS-CR CR_PHYS03_RR_TEMPORAL_FIRST_ABSORPTION_V1

```text
PROJECT=cosmosapjw-quantum/bass_cr
UNIT=CR_PHYS03_RR_TEMPORAL_FIRST_ABSORPTION_V1
PARENT_PR=127
PARENT_HEAD=631130bb0210a2fd6ec385b17f32ac99c64950ed
NEW_BRANCH=research/cr-phys03-rr-time-envelope-20261030
NEW_PR=TBD_AFTER_VERIFIED_PUBLICATION
NEW_PR_HEAD=TBD_AFTER_VERIFIED_PUBLICATION
SRC_PR125_SHA256=8e9b58236819146f4929aa4647dafdb1dc21b97b2f129ec4035291bb73a1ed2e
SRC_PR125_NPZ_SHA256=e171824cf5fc3ba232fbbd4def6fc8cf6c855ca9e7d05506e4e4426c9416688f
SOURCE_RR_PARENT_PR127_PY_GITBLOB=19beccce93e91e98c771c04d04d220a9cde45504
SOURCE_VERNER_TABLE_GITBLOB=4990865d7c314c26ebcb7d5a66d3cb4cf2e0511f
CENTRAL_DAG=28/88_DELTA0
EXTENSION_DAG=0/3_DELTA0
NEW_AUX=1/1_SCOPED_REVIEW_HOLD
RC_WORKFLOW=18/20
R06=NOT_RUN_DISTINCT_AUTHOR
C09=NOT_RUN_DISTINCT_AUTHOR
NATIVE_SUBAGENT=NOT_AVAILABLE
PHYSICAL_K=NULL
EXCLUSIVE_HE_EVENT_KERNEL=NULL
COSMOLOGICAL_TRANSFER=HOLD
NATIVE25=L4=PRODUCTION=HOLD
AUTO_NEXT_NODE=false

Original PR125 source gives two photon parent channels x four proper-time bins x 3200 atom energies, with UNKNOWN intra-bin birth times. Preserve 100K frozen H I/He I densities and the exact Verner1996 fits. Derived tight pointwise first absorption envelopes, survival envelope and source-target primary-electron excess-energy 1 eV spectra for 9 proper-time checkpoints. Do not treat endpoint bounds as fitted cosmic τ, net heating, H/He evolving chemistry, rates or observed data.

Restore original PR125 source ZIP; in isolated child of PR127 run:
bash research/cr_phys03_rr_time_envelope_20261030/REPRODUCE.sh /absolute/PR125_SOURCE.zip
Expected: Python 14/14 standard and 14/14 -O, independent MP75 120 controls, compileall. Snapshot outputs 9, 36, 792 rows. Final absorption [6.536559924836172e-27,1.7193913666048543e-26] m^-3 reproduces PR127.

Next scientific dependency: source-owner same-clock, same-inventory time-dependent neutral densities, cosmological redshift/geometry and radiative transfer. Need distinct-author R6/C9 before approval. No automatic next node, no main merge, no source rewrite or prefix_exact default promotion.
```
