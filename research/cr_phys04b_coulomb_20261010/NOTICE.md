# Source and license notice

`coulomb_ledger.py` ports the proton formula in CRIPTIC `Coulomb.H`, by
Mark Krumholz and contributors, commit
`e169dc2e906cf51d5c6a1bba47c10bf3d61c3d92`. This derived component is GPL-3.0-only;
the full license is preserved at
[`../cr_phys01_20261010/src/GPL-3.0.txt`](../cr_phys01_20261010/src/GPL-3.0.txt).
The three exact vendor files preserve their original bytes and author notices.

Modifications: Python port, explicit fixed proper-gas state, selected 1–10 MeV
proton domain, independently evaluated SI/CGS formulas, and a corrected SI
coefficient. Upstream's MKS multiplication by `4*pi*eps0` is retained as an
evidence-only negative control; the dimensional conversion requires division.
Numerical constants are explicitly pinned to CODATA 2018 values in this port;
an unspecified upstream GSL build is not claimed reproduced.
