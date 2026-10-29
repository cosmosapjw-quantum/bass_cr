# CR_PHYS04_RR_SPECTRAL_SURVIVAL_V1

Source-bound physical photon spectral data product from immutable PR128+PR125+PR127 inputs. No parent or production solver modifications.

Run `bash REPRODUCE.sh` in this directory after restoring the immutable `sources/PR128_ORIGINAL_SOURCE.zip` (SHA256 `a6062e5fa54c51983439e256ffd521f7b25d151952293e0fad7c2b3064ff4819`). Requires Python 3 with numpy, mpmath and matplotlib only for the plot. Reproduces all 9 epochs, 414 survivor spectral rows, 828 absorber spectral rows, 54 joint witness ledgers, 13+13 tests, 64 MP80 controls. Produces source-derived photons per volume; **not an observed photon flux** (no angular distribution / detector cross section), cosmological opacity or an ionization feedback IVP.

Authoritative artifacts: `THEORY_KO.md`, `REPORT_KO.md`, `DAG_DELTA.json`, `results/{RESULT.json,TIME_TOTAL.csv,SURVIVING_PHOTON_ENERGY.csv,ABSORBED_PHOTON_ENERGY.csv,JOINT_WITNESS_LEDGERS.csv,MP80.json}`. Source archive original is immutable and not intended to be checked into GitHub.