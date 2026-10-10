# Source and claim notice

Primary source: Philip M. Stone, Yong-Ki Kim and J. P. Desclaux,
*Electron-Impact Cross Sections for Dipole- and Spin-Allowed Excitations of
Hydrogen, Helium, and Lithium*, Journal of Research of NIST **107**, 327-337
(2002). https://nvlpubs.nist.gov/nistpubs/jres/107/4/j74sto.pdf

The original PDF is preserved unchanged. `sources/table.json` transcribes the
four 1000/1500/2000/3000 eV rows for H I 1s-2p and He I 1s2 1S-1s2p 1P.
The source gives cross sections in angstrom squared, not cm squared or s^-1.
The quoted excitation energies 10.204 and 21.218 eV follow the printed table.
No DarkHistory code is copied into the provider and no HDF5 dataset is imported.

Piecewise linear interpolation is a separately declared numerical rule, not an
error bound for the true atomic cross section. Source access, exact table parity
and component tests do not establish a physical uncertainty budget. The source
compares scaled Born results with available CCC/experimental results but does
not supply the uniform 1-3 keV error bound required for an integrated claim.

HeI 2^1P is not the old effective 2^3S (23s) channel. Connecting this table to the
old kernel requires a declared model/interface decision. No solver was run.
