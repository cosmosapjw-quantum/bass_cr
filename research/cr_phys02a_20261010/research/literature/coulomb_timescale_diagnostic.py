"""Independent FS10 local Coulomb loss-time diagnostic; not a cascade solver."""
import json
import math
from pathlib import Path

q = 1.602176634e-19
me = 9.1093837139e-31
eps0 = 8.8541878188e-12
hbar = 1.054571817e-34
ne = 1.5154
year = 365.25 * 86400
wp = math.sqrt(ne * q * q / (eps0 * me))
rows = []
for Eev in [100, 1000, 4000]:
    E = Eev * q
    v = math.sqrt(2 * E / me)
    loglam = math.log(2 * E / (hbar * wp))
    b = 4 * math.pi * (q * q / (4 * math.pi * eps0)) ** 2 * ne * loglam / (me * v)
    rows.append({"E_eV": Eev, "lnLambda_plasma": loglam, "v_m_s": v,
                 "b_eV_s": b / q, "t_local_E_over_b_s": E / b,
                 "t_local_E_over_b_yr": E / b / year})
result = {
    "schema": "cr-delay-independent-literature-check.v1",
    "status": "numerically checked diagnostic; no physical finite-time deposition claim",
    "assumptions": {"n_e_proper_m3": ne, "n_e_proper_cm3": ne * 1e-6,
                    "source": "FS10 Eq.(5) and explicit plasma-frequency part of Eq.(12)",
                    "E_unit": "eV", "year_s": year,
                    "charge_C": q, "electron_mass_kg": me,
                    "epsilon0_F_m": eps0, "hbar_J_s": hbar},
    "omega_p_s_inverse": wp,
    "zeta_2_hbar_omega_p_eV": 2 * hbar * wp / q,
    "rows": rows,
    "limitations": [
        "Instantaneous Coulomb-only local loss time E/b, not a full stopping time or cascade delay.",
        "Inelastic losses, branching secondaries and radiative propagation are excluded.",
        "Uses plasma-frequency form; does not use printed inconsistent compact zeta density law.",
        "Does not establish exact agreement with FS10 approximate Eq.(8) prefactor.",
        "Does not attribute the project T=100K state to FS10 MC inputs.",
    ],
}
target = Path(__file__).with_suffix(".json")
target.write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
