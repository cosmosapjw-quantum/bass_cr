# bass_cr C13 → rei_bianchi independent source-born photon transport

2026-10-15 KST. Independent branch from C12 source at
8b516d7321c746eeeef0c56dda35f05d9e1b2896.
Read-only owner rei_bianchi:
0fcb2dddf5de6b583c2e00f150abff0b2afb6315.
No local Codex used. Source, tests, results and theoretical
contracts are in research/cr_c13_transport_20261015.

Core change vs C12: only photons born during the actual interval
a=.1..11 are included. They undergo exact Bianchi-I directional
energy redshift, species-specific photoionization opacity, proper
nH(a)=nH0/a^3, H/He photoevents, owner Grackle-3.4.1 selected Case-A
recombination coefficients, and bounded ideal-gas thermal closure.
This does NOT simulate real inhomogeneous ionization-front radiation
transfer, owner R*J current-frame angular transport, true recombination
emissivity/OTS, full thermal cooling or actual EoR history.

Reproduce with:
  export REI_BIANCHI_ROOT=/home/cosmosapjw/Dropbox/bianchi/rei_bianchi
  export P=$PWD/research/cr_c13_transport_20261015
  export PYTHONPATH="$P/src:$PWD/research/cr_c12_physical_age_20261015/src:$PWD/research/cr_c11_heii_age_20261015/src"
  export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
  python3 -m pytest "$P/tests" -q -p no:cacheprovider
  python3 "$P/src/transport.py" --owner "$REI_BIANCHI_ROOT" --nsteps 32 --out /tmp/cr_c13_q0.json
  python3 "$P/src/validate.py" --owner "$REI_BIANCHI_ROOT" --output /tmp/c13_validation.json
  python3 "$P/src/benchmark.py" --owner "$REI_BIANCHI_ROOT" --nsteps 64 --repeats 3 --out /tmp/c13_benchmark.json

Dependencies: Python3, NumPy, SciPy, pytest, Rustc for the direct
owner Rust rate comparison. Source/source-history/scenario SHA checks
refuse a silently changed owner. Local n32 q0 outcome:
emitted photons/H 0.11243562770570208,
final xHI 0.8021355432672646, HeIII 0.00010189663685082942,
T 6623.831906158636 K,
photon balance ~5.55e-17 photons/H and discrete local energy
balance ~5.00e-16 eV/H. This is a controlled one-zone calculation.

For nsteps64: vectorized chemistry kernel 20.416x relative scalar
reference, same formula and per-packet result; 3 q cases measured
OS 1 process1.5036s, 2 processes1.4077s, 3 processes1.0903s.
These are local kernel/small benchmark claims, not full Rust speedups.
Midpoint source emission integral O2; Gauss2 improves emission integral
but gas xHI/T global convergence remains below production-grade.
Original case-A RR formulas were compiled from the owner Rust source
and checked at seven temperatures. No scientific admission.

See docs/THEORY_KO.md, RUN_RECORD.json, NEXT_DAG.json and
the results directory. Backup receipts and Git remote identity are
recorded separately.
