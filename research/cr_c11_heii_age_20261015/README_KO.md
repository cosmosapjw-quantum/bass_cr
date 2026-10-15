# bass_cr C11: HeII-positive age compression supplier for rei_bianchi

Independent light-weight source-age numerical study with a frozen owner
model. Parent bass_cr source revision:
research/cr-c10-source-subcells-20261015@669cbebe5e0a4383d7999aa354a3f320eff39fd2.
Owner rei_bianchi code read from codex/rux-science-delivery-20261014
at inspected HEAD 0fcb2dddf5de6b583c2e00f150abff0b2afb6315.
The executable verifies SHA-256 of three owner-source inputs before use
and never modifies the owner tree.

Commands (run at this bass_cr branch root):

    export REI_BIANCHI_ROOT=/home/cosmosapjw/Dropbox/bianchi/rei_bianchi
    export PYTHONPATH="$PWD/research/cr_c11_heii_age_20261015/src"
    export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
    python3 -m pytest -q research/cr_c11_heii_age_20261015/tests
    python3 research/cr_c11_heii_age_20261015/src/owner_age_bridge.py --rei-root "$REI_BIANCHI_ROOT" --workers 1 --out /tmp/heii.json
    python3 research/cr_c11_heii_age_20261015/src/benchmark.py --rei-root "$REI_BIANCHI_ROOT" --repeats 3 --out /tmp/heii_benchmark.json

Requires Python 3.12, NumPy, SciPy and pytest. A missing owner
file or owner SHA mismatch is a BLOCK, not a successful fallback.

Context: original 36 manufactured equal-source-count epochs, BB50k
source 13.6–100 eV, 12 angular / 16 threshold-split Gauss, three
signed q values -0.01,0,+0.01; proper gas cm^-3 and dt1e10 seconds.
Train three nonnegative gas compositions; sample 20 holdout
compositions including positive HeII fractions.

Scoped local numerical result on pinned input: one-gas matching
retains 6/36 ages but HeII event error rises to 10.31% and HeII
photoheat error to 13.91% on the unseen-gas set. Three-gas matching
retains 12/36 age nodes and has max sampled relative mismatch
about 5.43e-10 on this same quadrature. All outcomes preserve positive
age weights and have no photoabsorption > emitted photon count.
This is NOT a whole-history, all-opacities, or observational claim.

Matched owner scalar formula vs vectorized one gas/q, three repeated
trials: median 0.1945 s vs 0.0688 s (2.827x kernel speed ratio);
max matched relative discrepancy 3.54e-15.
Three-q evaluation with 2/3 spawned OS processes is slower than
single-worker for this small workload due to process overhead.
No native subagent was dispatched.

Evidence:
- results/REI_HEII_AGE_REFERENCE.json
- results/VECTORIZED_PARALLEL_BENCHMARK.json
- results/HEII_HOLDOUT_ERRORS.png
- results/TEST_RECEIPT.log
- docs/THEORY_KO.md

Next: physically weighted source-age emissivity and independently
evolved H/He/electron/temperature histories; truly independent
continuous integration and full memory/time accounting; owner
science gate before any default Rust solver attachment.
