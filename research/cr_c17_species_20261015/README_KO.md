# bass_cr C17: HI/HeI/HeII exact-positive time photoevent moments

Independent Bianchi-I SOURCE07 numerical supplier built on
bass_cr C16 df39cd31447a405e4dbaac273369e34c57b7ed72.
Read-only original rei_bianchi:
0fcb2dddf5de6b583c2e00f150abff0b2afb6315.
No Codex; native subagent NOT_RUN.

C16 is accurate at total photon-stock survival but its effective
opacity fraction can misassign HI vs HeI species photoionizations
while photon-number conservation remains exact. C17 replaces the
species allocation only, with explicit positive time-ordered
H/He reaction integrals for affine source and species opacity.
The same C16 photon-survivor integral is retained.

The implementation also evaluates species-wise photoevent time
moments for linear-in-time photon energy and computes positive
photoelectron heat when E(t) stays above all active species'
physical binding energies. Ionization-threshold crossings must
be partitioned before applying an affine-step model.

Run on Ubuntu from this bass_cr branch repo root:

    export REI_BIANCHI_ROOT=/home/cosmosapjw/Dropbox/bianchi/rei_bianchi
    export C17=$PWD/research/cr_c17_species_20261015
    export PYTHONPATH="$C17/src:$PWD/research/cr_c16_endpoint_20261015/src:$PWD/research/cr_c15_duhamel_20261015/src:$PWD/research/cr_c14_recomb_order_20261015/src:$PWD/research/cr_c13_transport_20261015/src:$PWD/research/cr_c12_physical_age_20261015/src:$PWD/research/cr_c11_heii_age_20261015/src:$PWD/research/cr_c10_source_subcells_20261015/src:$PWD/research/cr_c5_budgeted_cohorts_20261015/src"
    export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
    python3 -m pytest -q -p no:cacheprovider "$C17/tests"
    python3 "$C17/src/owner_species_benchmark.py" --owner "$REI_BIANCHI_ROOT" --out /tmp/C17_SPECIES.json
    python3 "$C17/src/benchmark.py" --owner "$REI_BIANCHI_ROOT" --repeats 3 --out /tmp/C17_BENCHMARK.json

Dependent software: Python3, NumPy, SciPy, pytest and Matplotlib
only for plots. Authentication or local Codex is not needed to run
the numerical kernels; source access must be to an exact owner
snapshot or the runtime rejects changed owner contracts.

Headline reproducible results:
- photon total exact but C16 species swap error ±0.9702 photon/H
  under changing HI/HeI opacity with constant sum Lambda=100.
- q0 owner anchored fixed-gas benchmark: C16 species max relative
  error 0.0002535 at n128, C17 2.6066e-7.
- signed q=-.01,0,+.01 C17 species error converges ~O(dt²),
  while C16 species event allocation is first-order-like.
- sampled high-resolution C17 64x48 vs 32x24 tradeoff stored in
  results/QUADRATURE_SWEEP.json and BENCHMARK.json.
- radiation stock conservation/physical heat moment validated,
  no full evolving gas/temperature/OTS history yet.

Evidence locations in results include:
OWNER_SPECIES_RADAU.json, QUADRATURE_SWEEP.json,
BENCHMARK.json, SPECIES_CONVERGENCE.png,
PACKET_KERNEL_TIMINGS.png, TEST_RECEIPT.log, RUN_RECORD.json.
Handoff and next node in NEXT_DAG.json. Scientific gate
PASS_SCOPED_SPECIES_EVENTS and GLOBAL_REI_BIANCHI_EOR_HOLD.
