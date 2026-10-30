# BASS-CR PHYS14 | Next-thread science handoff (pre-publication archive snapshot)

PROJECT=cosmosapjw-quantum/bass_cr
UNIT=CR_PHYS14_NIST_H_1S2P_COMPETING_INELASTIC_FIRST_EVENT
PARENT_PR=138
PARENT_HEAD=9647b3e6a27ec5711c2ba4bfc33acf57a97f1f27
PARENT_FULL_SOURCE_SHA256=fdae18068eb51ae7bdd0785efa371229aa15d33b6f040e0640e0bd65cc66d3a7
NEW_PR=NOT_YET_CREATED_AT_ARCHIVE_TIME

NIST_SOURCE=https://physics.nist.gov/cgi-bin/Ionization/excit_data.php?final=2p&id=HI&initial=1s&ision=E
NIST_CONVENTION=BE_SCALED_BORN_THEORETICAL_NOT_MEASURED
SHAH_SOURCE=ORIGINAL_26_MEASUREMENTS_IN_PARENT
T_FINAL=1e10_SECONDS
SCIENCE_ROWS=6595
SHARED_SOURCE_PHOTONS=6400
SECOND_2P_ENERGY_ELIGIBLE=192

CENTRAL_DAG=28/88_DELTA0
EXTENSION_DAG=0/3_DELTA0
PHYS14_AUXILIARY=1/1_CONDITIONAL_REVIEW_HOLD
R06_DISTINCT_AUTHOR=NOT_RUN
C09_DISTINCT_AUTHOR=NOT_RUN
NATIVE_SUBAGENT=NOT_RUN
PHYSICAL_K=UNBOUND
COMMON_EVOLVING_GAS_RADIATION_CLOCK_GEOMETRY=UNBOUND
SECOND_2P_CROSS_SECTION=NOT_SUPPLIED_BELOW_11EV
HE_GLOBAL_EXCLUSIVE=UNBOUND
PRODUCTION=HOLD
NO_MERGE=true
NO_FORCE_PUSH=true
AUTO_NEXT_NODE=false

The entire source/plots/CSV are in the full PHYS14 SOURCE ZIP. Run bash REPRODUCE.sh after clean extraction. Git-only checkout cannot reproduce without immutable nested PHYS13 ZIP. NIST 1s2p BE vs Shah measured ionization overlap only, physically narrow conditional model. Next actual physical node: source-qualified H 1s2s and 1s3p excitation competition and/or second 2p cross section 10.2..10.79 eV; do not invent absent cross sections or Ly-alpha transport.
