# bass_cr C14: rei_bianchi numerical time order repair

Date 2026-10-15 KST. Parent source C13 commit
eef456cd3f72b4d8c699e6454e04ed405099b436.
Read-only owner rei_bianchi commit
0fcb2dddf5de6b583c2e00f150abff0b2afb6315.
All new code and output is in isolated C14 worktree.
No local Codex was used.

Main scientific results:
1. Owner H/He Case-A pure-recombination scheme originally first-order
   vs independent DOP853 at initial T4000 and 9000 K.
2. Added self-consistent midpoint electron-density evaluation to
   exactly the same H/He positive Markov exponential. Observed
   second order in both independent reference cases.
3. Constant-source/frozen-opacity local photon equation has an
   exact positive Duhamel time update. Code covers tau=0, small and
   very large, and species-resolved photoevent ledgers.
4. Actual owner Verner proper gas tau for E=13.61eV is ~2308
   per step with 32 steps, still ~72 with 1024 steps. Born-at-midpoint
   misses nearly 100% of the residual photon stock in a carefully
   labelled manufactured uniform-emission experiment.
5. C13 creates unnecessary zero-photon source cohorts when
   source_scale=0. C14 does not allocate these; old scientific
   no-source output is numerically identical. Benchmarked optimization.
6. Fully coupled photo/recomb source case is still first-order-like
   and NOT admitted; thermal Case-A electron escape is a toy closure,
   not owner igm_thermal cooling.

Commands:
    export REI_BIANCHI_ROOT=/home/cosmosapjw/Dropbox/bianchi/rei_bianchi
    export C14=$PWD/research/cr_c14_recomb_order_20261015
    export PYTHONPATH="$C14/src:$PWD/research/cr_c13_transport_20261015/src:$PWD/research/cr_c12_physical_age_20261015/src:$PWD/research/cr_c11_heii_age_20261015/src:$PWD/research/cr_c10_source_subcells_20261015/src:$PWD/research/cr_c5_budgeted_cohorts_20261015/src"
    export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
    python3 -m pytest -q -p no:cacheprovider "$C14/tests"
    python3 "$C14/src/validate.py" --owner "$REI_BIANCHI_ROOT" --out /tmp/C14_VALIDATION.json
    python3 "$C14/src/benchmark.py" --owner "$REI_BIANCHI_ROOT" --base /home/cosmosapjw/chat_research/bass_cr_rei_transport_c13_20261015/research/cr_c13_transport_20261015/src/transport.py --out /tmp/C14_BENCHMARK.json

Results:
- results/VALIDATION.json: RR two temperature independent DOP853
  and actual owner Verner stiff photon-source counterexample.
- results/BENCHMARK.json: matched-formula scalar/vector and actual
  no-source old/current timing.
- results/RR_ORDER.png and DUHAMEL_SOURCE.png.
- tests/test_rr_source.py, THEORY_KO.md, NEXT_DAG.json,
  REI_SOURCE07_HANDOFF_KO.md, RUN_RECORD.json.

Admissible status:
RR-only second order: NUMERICALLY_CHECKED.
Frozen-coefficient Duhamel: mathematically exact and numerically checked.
Full SOURCE07 R*J gas/thermal/history: HOLD.
Entire rei_bianchi owner repository unchanged.
