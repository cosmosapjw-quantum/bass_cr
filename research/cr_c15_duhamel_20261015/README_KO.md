# bass_cr C15 → rei_bianchi continuous source-age photon kinetics

Research date 2026-10-15. Parent bass_cr C14 commit
bf1fa9c36511f27798d4081dd331e74fd33b678a.
Read-only owner rei_bianchi branch
codex/rux-science-delivery-20261014 commit
0fcb2dddf5de6b583c2e00f150abff0b2afb6315.
Owner source/Scenario/Spectrum SHA-256 checked at runtime.

The executable C15 adds a POSITIVE proper-time continuous Duhamel source
to each Bianchi-I birth-frame photon age cohort, with midpoint H/He
gas opacity, existing-photon redshift, species event/heat and owner Case-A
RR midpoint electron density. This replaces C13's point-midpoint
photon birth in a SEPARATE prototype, not in canonical rei_bianchi.

Reproduce on authorized Ubuntu from this new branch repository root:

    export REI_BIANCHI_ROOT=/home/cosmosapjw/Dropbox/bianchi/rei_bianchi
    export C15=$PWD/research/cr_c15_duhamel_20261015
    export PYTHONPATH="$C15/src:$PWD/research/cr_c14_recomb_order_20261015/src:$PWD/research/cr_c13_transport_20261015/src:$PWD/research/cr_c12_physical_age_20261015/src:$PWD/research/cr_c11_heii_age_20261015/src:$PWD/research/cr_c10_source_subcells_20261015/src:$PWD/research/cr_c5_budgeted_cohorts_20261015/src"
    export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
    python3 -m pytest -q -p no:cacheprovider "$C15/tests"
    python3 "$C15/src/validate.py" --owner "$REI_BIANCHI_ROOT" --out /tmp/C15_VALIDATION.json
    python3 "$C15/src/benchmark.py" --owner "$REI_BIANCHI_ROOT" --steps 128 --repeats 3 --out /tmp/C15_BENCHMARK.json

Depend on existing Python3, NumPy, SciPy, pytest. The C15 tests
run the actual owner source; use REI_BIANCHI_ROOT to point at a
restored immutable owner snapshot for offline reproduction.
No local Codex, no native subagent dispatched.

Results in results/VALIDATION.json, BENCHMARK.json,
GAS_CONVERGENCE.png, SURVIVOR_CONVERGENCE.png.
- q=0, nsteps32: xHI=0.8021905024753476; Tg=6627.044382590808 K;
  survivor photons/H=6.670100319137988e-6.
- Same C13 midpoint-birth approximation, nsteps32 survivor
  9.201348291179505e-14/H. These are different numerical source
  definitions, not a direct EoR accuracy measurement.
- Number/energy/nuclei/charge ledgers checked to roundoff.
- Independent owner-source QUADPACK no-opacity N and E
  references give approx second-order source/geometry integration.
- Gas xHI/T successive-grid order approx2 under smooth below/above
  5500K coefficient and with RR disabled; branch-crossing example
  is not uniformly order2.
- Survivor photon number time-grid order approx1 in tested
  strongly opaque cases, so full SOURCE07 time accuracy HOLD.
- At nsteps128 cached+lossless-zero-pruned packet arrays 255920
  bytes and median0.373s, compared with 983040 bytes and 0.776s
  unpruned. 3 independent q jobs using 3 OS processes ~0.816s,
  vs single process ~1.074s median (3 runs).
- Additional exact positive linear-in-time source kernel (frozen
  opacity ONLY) in src/linear_source.py, independently integrated
  with QUADPACK and algebraically checked by Wolfram.

Science gate: NUMERICALLY_CHECKED_LOCAL_SOURCE_HISTORY;
GLOBAL_REI_BIANCHI_RUNTIME_HOLD. Current owner SOURCE07 R*J
transport and full Grackle thermal/OTS not updated. Refer to
THEORY_KO.md and REI_SOURCE07_HANDOFF_KO.md for unit contracts
and next constructive physics obligations.
