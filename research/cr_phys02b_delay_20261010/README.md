# CR-PHYS02B absolute-time electron generator

Current status: **PASS_SCOPED numerical repair; independent review pending**.
The single characteristic repair passes all seven original acceptance rows and
the added continuum-arrival oracle. Nine focused tests pass. See
`REPAIR_CONTRACT.json` and `evidence/REPAIR_VALIDATION.json`.
The original donor-cell grid FAIL is retained unchanged in
`evidence/VALIDATION.json`; its history is described below and in the report.

The sidecar evolves an impulse of 10–1000 eV electrons with fixed H/He gas:
nH=140 m^-3, Y=0.248, xHII/H=xHeII/He=0.01, xHeIII=0, T=100 K. It translates
the pinned DarkHistory `old` raw collision cross sections and Coulomb drag into
proper-second rates. The parent source commit/tree and all seven unchanged
upstream payloads, including MIT license, are in `SOURCE_MANIFEST.json`.

For an ionization event the two daughter kinetic energies sum to E-I. The lower
electron follows the normalized conditional old Shull shape; the upper electron
is its paired complement. Barycentric projection preserves both number and
energy. Excitation removes its threshold energy into a separate excitation
reservoir; its spectrum, multiplicity and later radiative fate are not modeled.
Binding energy, Coulomb heat, and <=10 eV unresolved electron count/kinetic
energy are separate. The total expected electron count increases by one per
ionization. Therefore N_active+N_cutoff−N_ionization=N_initial, while active,
cutoff, binding, excitation and heat energies sum to the injected energy.

The collision generator is dimensional and has nonnegative off-diagonal entries.
Continuous Coulomb drag now follows cooling characteristics, with collision
stages assembled at the same moving midpoint energies. Actual energy decreases
in drag substeps enter heat; arrived nodes remain unresolved cutoff electrons.
The state array carries its instantaneous energy grid. This research API takes
an impulse from time zero; resumable history/state handoff is outside its scope.
It is not the source's normalized terminal cooling transfer matrix. The gas
and its free-electron reservoir stay fixed, so there is no gas feedback,
cosmological expansion, full stopping model, photon transport or CR-source
convolution. Current proton secondary support extends above this 1000 eV cap;
the present sidecar is not a complete CR-PHYS02 provider.

Run focused tests:

```sh
python3 -B -m unittest discover -s research/cr_phys02b_delay_20261010/tests -p 'test_*.py' -v
```

The executed numerical command was:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 -B research/cr_phys02b_delay_20261010/validate.py
```

It refuses to overwrite an existing evidence file. For an explicitly authorized
new run, pass a new output path as the first positional argument. Reproducing an
unchanged failed run does not resolve the failure; inspect `FAILURE_LOG.md` first.
No production provider files were modified, and this implementation worker did
not commit, push, or perform its own independent review.

The single authorized repair-closeout command was:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 -B research/cr_phys02b_delay_20261010/validate.py research/cr_phys02b_delay_20261010/evidence/REPAIR_VALIDATION.json
```

It exited 0. Do not repeat it merely to reproduce unchanged evidence.
