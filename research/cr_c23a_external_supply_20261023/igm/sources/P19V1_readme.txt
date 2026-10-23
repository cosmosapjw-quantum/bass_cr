The content of the ancillary files is as follows:

rate_fiducial.txt
-----------------
Photoionization and photoheating rates in the fiducial UVB model. The first 6 columns contain the same data as in Table D1 in the manuscript. The rates are in units of 1/s and eV/s.

rate_eqeq.txt
-----------------
Photoionization and photoheating rates in the equivalent-equilibrium model. This is the same data that is provided in Table D2 in the manuscript. The rates are in units of 1/s and eV/s.

TREECOOL
-----------------
Photoionization and photoheating rates in the equivalent-equilibrium model in the format expected by the P-Gadget3 code. Simply replace the TREECOOL file in the code directory with this file. The columns contain:

log10(1+z)
Gamma_HI [1/s]
Gamma_HeI [1/s]
Gamma_HeII [1/s]
H_HI [erg/s]
H_HeI [erg/s]
H_HeII [erg/s]
