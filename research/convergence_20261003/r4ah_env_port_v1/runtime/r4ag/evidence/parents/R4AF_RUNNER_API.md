# R4AF portable execution and return contract

The shipped run_v2 is COMPLETE and must NOT be rerun merely to continue the project. The next task concerns shifted-node orchestration; this executable deliberately accepts only the existing z=-32 point. No M9 jet, D, V, capture or basis scan is authorized here.

## Verify the delivery without science

`python verify_package.py .` checks the release payload manifest. It neither loads a solver nor regenerates a bound. The historical absolute output paths in consumed contracts remain unchanged.

## Only when a new environment reproduction is independently needed

Dependencies: Linux, Python with numpy/scipy/mpmath/pytest, C++17 and GMP/GMPXX development headers. The exact successful versions are in evidence/ENVIRONMENT.json and DEPENDENCIES.json. FLINT is not required and was not used. GMP performs integer interval arithmetic; this is not an FP64 mixed-precision approximation.

Work on a copied package directory, not the immutable historical package. Build a NEW executable:

```sh
g++ -std=c++17 -O3 -fno-fast-math -ffp-contract=off source/native_cubature.cpp -lgmpxx -lgmp -o source/native_cubature
export PYTHONPATH="$PWD/source:$PWD/vendor_r4ae"
python source/prepare_external.py --output "$PWD/results/external_new" --workers 1 --authorize-single-existing-geometry
```

The preparer returns the exact new CONTRACT and AUTHORIZATION paths. It observes affinity/quota/memory, pins the newly built native/source/input bytes and binds the output. It does not run science. Use the exact returned values:

```sh
python source/run_pilot.py "$CONTRACT" "$AUTHORIZATION"
```

The cap is one point, 1800 seconds, at most3 workers, 512MiB per native worker, 1.75GiB coordinator/reserve, 10000cells, split depth5. The original completed execution used3 single-core workers. The preparer refuses insufficient quota/memory and existing output directories. No consumed authorization is reusable. A failure retains reservation, source identity, stderr and completed cell outputs. Do not silently restart or copy old outputs into a new success receipt.

Returned evidence must include CONTRACT/AUTHORIZATION, source/input/native hashes, observed environment, RESERVATION, CELL_CERTIFICATES, GAUSS_RULES, native input SHA and every worker output, S_ENCLOSURE/S_ONLY_SEAL, RESULT/COMPLETED or FAILURE, and a read-only return review. The supplied independent_review.py targets the ORIGINAL v2 contract and original path only; a new external return must bind its exact new contract/run mapping in a separately versioned reviewer adapter. Do not edit the old contract to fool that check. All numerical tolerance and channel/geometry semantics remain identical.

No compiler or architecture speedup is claimed. Environment-specific SIMD/MPI/NUMA optimization remains NCP/local Codex work and must preserve integer endpoint correctness or introduce an explicitly verified replacement.
