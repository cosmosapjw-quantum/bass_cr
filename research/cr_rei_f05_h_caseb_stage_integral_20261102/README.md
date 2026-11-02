# Original accepted REI F05 H Case-B native stage source quadrature

Source-locked BASS-CR-only analysis stacked on immutable PR164. Original 26-event F05 HII→HI Case-B flux is `event.flux[:,0,1]` in original destination/source indexing; 46,080 ORIGINAL material cells, accepted epochs 0,64,128,160 only. The original SDIRK2 three-map computation uses original two-half-step native **stage and final** source flux. It computes one 3-interval **stage-quadrature** H-recombination result (plus H-ionizations and MPRK-vs-source mismatch), not a new time-evolved reionization solution or Lyα photons.

Direct output: `ORIGINAL_F05_ACCEPTED_H_CASEB_STAGE_3_INTERVALS.csv` (3 aggregate source-derived rows only), `SCIENCE_RESULT.json`. Input original REI/REC primary state remains private and is not in public Git.

Run on an authorized original source host: `bash research/cr_rei_f05_h_caseb_stage_integral_20261102/REPRODUCE.sh`. The default original-source paths are pinned, or override with REI_F05_REPO, REC195_SOURCE_ZIP and REI_F05_PYTHON. The script runs full original native source 9-map replay and SHA byte verification; public-only Git clone cannot perform this without the private original sources.

**Important physical finding:** On [0,64], stage-flux integrated net HII source does not overlap original MPRK endpoint ∆HII in 336 cells; 9.640425779725532e54 HII-count gap sum, 1.084858508048765e-7 of original absolute change. This is NOT an exact continuous-reaction integral nor proof of a new global energy leak. The original source-owned full/half/half and 14-ledger gates pass. See `THEORY_AND_SCOPE.md` and `SCIENTIFIC_REPORT_KO.md` for result, source identity and limitations.

Canonical REI 28/88, working 33/88, fast 4/7, BASS_CR 0/3, all Δ0. CR-OFF baseline, original REI 26-event worker, source, 14 ledgers, other scientific branches, main and accepted through t160 unchanged. Draft/HOLD, NO_MERGE, NO_FORCE_PUSH. No additional optional atlas after this unit.
