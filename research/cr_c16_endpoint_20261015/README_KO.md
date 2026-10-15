# bass_cr C16: endpoint & threshold-aware source-opacity time quadrature

Source base bass_cr C15: ad1441a97cd0c755cd8bdac8ede80900906764a8.
Actual read-only rei_bianchi authority:
0fcb2dddf5de6b583c2e00f150abff0b2afb6315.
C16 focuses on strong-opacity photon survivor temporal order.

Two NEW positive local source/sink algorithms:
- FAST endpoint-weighted positive exponential, smooth/source validity limited.
- 64-node positive optical-age Gauss quadrature, near-exact for
  piecewise-linear time-dependent opacity and source.
Photon-number ledger remains positive/consistent. Species event
allocation under varying rates is positive approximate, not exact.

Physics test uses true owner q-dependent H, Bianchi photon E(a),
Verner H/He cross sections and source-rate epochs, but FROZEN
ion fractions and manufactured 5 fixed birth-energy channel labels.
It is not the true SOURCE07 propagated age-resolved photon spectrum.
A real HI ionization threshold crossing for 14eV source channel
is inserted in log a; this step restores second-order global
photon survivor error relative to independent SciPy Radau:
q0 16/32/64/128/256 base steps, max relative errors
1.1677e-5/2.921e-6/7.32e-7/1.84e-7/4.6e-8.
Other q=-.01 and +.01 show the same scoped convergence.

Reproduce in the authorized Ubuntu checkout:

    export REI_BIANCHI_ROOT=/home/cosmosapjw/Dropbox/bianchi/rei_bianchi
    export C16=$PWD/research/cr_c16_endpoint_20261015
    export PYTHONPATH="$C16/src:$PWD/research/cr_c15_duhamel_20261015/src:$PWD/research/cr_c14_recomb_order_20261015/src:$PWD/research/cr_c13_transport_20261015/src:$PWD/research/cr_c12_physical_age_20261015/src:$PWD/research/cr_c11_heii_age_20261015/src:$PWD/research/cr_c10_source_subcells_20261015/src:$PWD/research/cr_c5_budgeted_cohorts_20261015/src"
    export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
    python3 -m pytest -q -p no:cacheprovider "$C16/tests"
    python3 "$C16/src/owner_ray_benchmark.py" --owner "$REI_BIANCHI_ROOT" --out /tmp/C16_RAY.json
    python3 "$C16/src/benchmark.py" --owner "$REI_BIANCHI_ROOT" --repeats 3 --out /tmp/C16_PERFORMANCE.json

Runtime: Python3, NumPy, SciPy, pytest, optional matplotlib
for plots. Native subagent was unavailable (NOT_RUN);
local Codex was not used.

Expected evidence in results/OWNER_RAY_THRESHOLD_AWARE.json,
BENCHMARK.json, THRESHOLD_TIME_CONVERGENCE.png,
KERNEL_BENCHMARK.png, TEST_RECEIPT.log and RUN_RECORD.json.
The scientific verdict is **PASS only for the scoped photon
source/opacity/spectral-threshold time-integrator subproblem.**
Do not promote to full physical REI_BIANCHI SOURCE07 admission
or claim observed ionization histories.

Important adversarial finding: endpoint FAST kernel differs from
optical quadrature by up to relative 12.2 on a 4096-packet test
with discontinuous threshold interactions. Do not treat
~13x speed advantage as matched-accuracy dominance.

Next: map onto REAL age-tagged SOURCE07 angular ray R*J stocks
and the original Grackle H/He thermal/OTS network. See
THEORY_KO.md, REI_SOURCE07_HANDOFF_KO.md, NEXT_DAG.json.
