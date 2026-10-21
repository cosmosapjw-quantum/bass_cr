# Atomic source reuse

`r9_li_thermal_rates.py` is an unchanged copy from
`cosmosapjw-quantum/rei_bianchi` at
`8a4f5df46f6e3058f5e685b85cc1cf3c20926368`, originally
`research/microphysics_r9_20261015/unit8_remaining_bridges_20261016/code/li_thermal_rates.py`.
The donor repository's MIT notice is preserved in `REI_LICENSE`.

The six numerical source/table files are byte-identical copies of the author
distribution at the University of Kentucky. Original author comments remain:

- D. A. Verner, `phfit2.f`, version2, March25,1996: shell-resolved photoionization
  in Mb (1 Mb = 1e-18 cm^2). The outer-shell fits are Verner, Ferland, Korista,
  Yakovlev1996, ApJ465,487; partial-shell fits are Verner and Yakovlev1995,
  A&AS109,125. The original `photo_table.dat` and `partial_table.dat` independently
  reproduce the selected Fortran coefficients.
- D. A. Verner, `rrfit.f`, version4, June29,1999: cm^3/s total spontaneous
  radiative-recombination coefficients. The adopted H/He/Li branch is Verner and
  Ferland1996, ApJS103,467, DOI10.1086/192284. The original `rr_table.dat` and
  `rr_description.txt` identify the units and both HeI fit rows; the code uses
  `HeI b`, as the frozen author `rrfit` does.

No separate SPDX/license statement was present in the six numerical input
files. The repository MIT notice is not represented as a new license grant for
these author files. Source URLs, lengths and SHA256 are recorded individually in
`../../ATOMIC_SOURCE_MANIFEST.json`.

## Scientific selection

The wrapper calls the unchanged `Provider.sigma` and `Provider.rr` for six
electronic channels. It does not reuse the old R9 early-universe trajectories.
For neutral Li the photo channel is ground2s valence only: the original PH2 fit
below64.39eV and PH1 outer2s partial above that energy. The core1s cross section,
Auger yields and their charge-state outcomes are not inserted into this model.
The all-level spontaneous RR coefficient is used with a Case-A escape closure.
This choice is not a detailed-balance multilevel atom calculation.

The wrapper additionally uses selected historical weak-decay constants:
Gonzalez et al.2021 UCNtau, DOI10.1103/PhysRevLett.127.162501,
neutron **mean** lifetime877.75s; and the tritium laboratory **half-life**12.33yr
quoted by Fuller and Smith2010, DOI10.1103/PhysRevD.82.125017. Neither is labelled
a current world average. Tritium's electronic-charge independence is a declared
approximation. In the illustrative initial conditions both parent totals are
exactly zero; no decay heat is inserted into the prescribed temperature.
