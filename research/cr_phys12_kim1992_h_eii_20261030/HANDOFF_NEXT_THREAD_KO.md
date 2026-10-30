# BASS-CR PHYS12 full scientific handoff (2026-10-30)

PROJECT=cosmosapjw-quantum/bass_cr
PARENT_PR=136
PARENT_HEAD=d7de61661b718f9968acd4e696510603968e18e7
UNIT=CR_PHYS12_KIM1992_H_EII_FINITE_HORIZON
PARENT_SOURCE_SHA256=afedf6ac708e17e847d086625af47c0cf0a902b8ec2f1c168daf16b198ef050a
PHYS12_ROWS=13173
EARLIEST_TWO_EVENT_FIT_UPPER_M3=1.3345858733024866e-31
LATEST_TWO_EVENT_FIT_UPPER_M3=3.9701495974077453e-32
MODEL=Kim1992_measured_Shah1987_total_fit_nonincreasing_E_frozen_neutrals
R06_DISTINCT_AUTHOR=NOT_RUN
C09_DISTINCT_AUTHOR=NOT_RUN
NATIVE_SUBAGENT=NOT_RUN
CENTRAL_DAG=28/88_DELTA0
EXTENSION_DAG=0/3_DELTA0
PHYS12_AUXILIARY=1/1_CONDITIONAL_REVIEW_HOLD
PHYSICAL_K=UNBOUND
EXCLUSIVE_HE_DOUBLE_EVENT_KERNEL=UNBOUND
COMMON_EVOLVING_NEUTRAL_HISTORY=UNBOUND
SHARED_RADIATION_OWNER=UNBOUND
ELECTRON_STOPPING=UNBOUND
NATIVE25=HOLD
L4=HOLD
PRODUCTION=HOLD
NO_MERGE=true
NO_FORCE_PUSH=true
AUTO_NEXT_NODE=false

Restore the complete SOURCE ZIP and execute `bash REPRODUCE.sh`. This calculation is **not** the actual secondary impact realization nor a gas heating rate. The parent PHYS11 model's 13.60 eV H photoionization threshold differs from Kim's 13.61 eV fit threshold, and the extrapolated 13.61–14.6eV cross-sections are not direct measurements.

Next physical branch: obtain source-authority compatible complete electron stopping/trajectory kernel (including thermal relative speeds) to convert the measured-fit upper into a realized conditional collision probability; or source-owned common dynamic gas/radiation/clock data for central DAG promotion. Read THEORY_KO.md and BLIND_REFEREE_EVIDENCE.json before claims.
