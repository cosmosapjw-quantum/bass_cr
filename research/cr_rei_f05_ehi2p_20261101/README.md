# REI-F05 original electron-HI 1s→2p excitation source

BASS-CR physical source-conditional extension on top of Draft PR160 (Case-B). This research unit produces ONE new originally sourced Ly-alpha emission *sector* without modifying the original REI solver, accepted state, photon groups or official DAG.

Outputs: 12,528 supported-domain original F05 tick160 material cells. Rates are electron-impact HI(1s)→HI(2p), under MAXWELLIAN electrons with Te=Tgas and f1s=1, plus TWO-LEVEL prompt radiative branching only. Temperatures outside source-table 5,000–20,000 K are explicitly excluded; 33,552/46,080 source cells remain unevaluated for this process. This is NOT the total or escaped Ly-alpha photon production, a full inhomogeneous source integral, measured optical depth, or the complete neutral hydrogen kinetic owner.

Source F05 original state source SHA 713b46a0da8931cc6f5a355912cdd2efa790945c2539ad049c086fd995f3441d. Private owner source and original 26-event state are NOT committed. Source-locked original electron density/proper-volume crosscheck is read from the immutable original REI worktree by the inherited Case-B source module. Frozen parent PR160 Derived Case-B CSV SHA 5aa85017b9bebb11822aca4780e9c3c248aadb87f8175575f1d8f8fd8821c154.

Primary literature: Scholz et al. (1990), MNRAS 242,692; published Pradhan effective collision strength table, 4 temperature knots. Piecewise linear interpolation is a newly explicit and unvalidated interpolation assumption, not a literature-exact continuum function. See THEORY_AND_GATES.md.

Run on the original authorized remote host with private source and frozen original owner checkout:
  bash research/cr_rei_f05_ehi2p_20261101/REPRODUCE.sh
The standalone public Git checkout is intentionally not source-complete.

Code, 12,528-row derived gzip CSV, RESULT.json, tests, evidence, provenance manifest and next-thread handoff are in this directory. PRODUCTION HOLD; REI 28/88, working 33/88, BASS-CR 0/3 unchanged.