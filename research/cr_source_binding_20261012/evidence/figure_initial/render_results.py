#!/usr/bin/env python3
"""Plot saved source-binding results; no transport calculation."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

root = Path(__file__).parent
d = json.loads((root / "results/SOURCE_BOUND_RESPONSE.json").read_text())
r = d["rows"][0]
b = [b for b in d["birth_rows"] if b["model"] == "fullBED"]
e = d["cumulative_energy_envelope"]
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.titlesize": 12,
                     "axes.spines.top": False, "axes.spines.right": False})
fig, axes = plt.subplots(2, 1, figsize=(9.2, 7.6), gridspec_kw={"height_ratios": [1, 1.55]})
ax = axes[0]
keys = ["injected_energy_weight", "endpoint_heat_share", "cumulative_heat_share"]
labels = ["Injected energy", "Heating power at T", "Heat accumulated by T"]
low = np.array([float(b[0][k]) * 100 for k in keys])
high = np.array([float(b[1][k]) * 100 for k in keys])
y = np.arange(3)
ax.barh(y, low, color="#24587a", height=.53, label="Birth: 0.1-10 eV")
ax.barh(y, high, left=low, color="#d99439", height=.53, label="Birth: 10-900 eV")
for j, (a, c) in enumerate(zip(low, high)):
    ax.text(a / 2, j, f"{a:.2f}%", va="center", ha="center", color="white", fontsize=8.3, fontweight="bold")
    ax.text(a + c / 2, j, f"{c:.2f}%", va="center", ha="center", color="#202020", fontweight="bold")
ax.set_yticks(y, labels)
ax.set_xlim(0, 100)
ax.invert_yaxis()
ax.set_xlabel("Share of each selected-window total (%)")
ax.legend(loc="lower center", bbox_to_anchor=(.5, 1.02), frameon=False, ncol=2)
ax.set_title("A. Low-energy births supply most of the early heat", loc="left", pad=44)

ax = axes[1]
cv = float(d["gas_calorimeter"]["C_V_J_m3_K"])
values = [float(r["calorimetric_delta_T_K"]),
          float(r["cutoff_thermal_join"]["linearized_delta_T_frozen_coeff_K"]),
          float(r["same_operator_prompt_cumulative_J_m3"]) / cv,
          float(e["cutoff_join_plus_all_omitted_delta_T_upper_K"]),
          float(e["all_secondary_delta_T_upper_K"])]
labels = ["Recorded heat / heat capacity", "Cutoff thermal-join candidate",
          "Same-operator prompt heat / heat capacity", "Selected join + omitted birth energy: upper bound",
          "All secondary birth energy: upper bound"]
for j, v in enumerate(values):
    ax.scatter(v, j, s=62, marker="o" if j < 3 else ">", color="#24587a" if j < 2 else ("#a55732" if j == 2 else "#71824a"), zorder=3)
    ax.annotate(f"{v:.4g} K", (v, j), xytext=(9, 0), textcoords="offset points", va="center", fontsize=9)
ax.set_xscale("log")
ax.set_xlim(1.9e-14, 1.5e-11)
ax.set_ylim(4.7, -.65)
ax.set_yticks(range(5), labels, fontsize=8.8)
ax.grid(axis="x", which="major", alpha=.24)
ax.set_xlabel("Source-attributed temperature diagnostic (K; logarithmic scale)")
ax.set_title("B. Absolute thermal scale at the recorded source amplitude", loc="left", pad=16)
fig.text(.02, .018, "Fixed bath: 100 K, nH = 140 m^-3, xi = 0.01.  T = 1e10 s.  Qe(W,t) = t A(W).\nBounds cover secondary kinetic energy from the recorded 1-4 MeV proton source; they are not cosmological-history bounds.", fontsize=8.3, color="#444444")
fig.subplots_adjust(left=.39, right=.98, top=.87, bottom=.125, hspace=.67)
fig.savefig(root / "results/SOURCE_BINDING_SUMMARY.pdf", bbox_inches="tight")
fig.savefig(root / "results/SOURCE_BINDING_SUMMARY.png", dpi=180, bbox_inches="tight")
print(json.dumps({"status": "RENDERED_SAVED_RESULTS", "outputs": ["SOURCE_BINDING_SUMMARY.pdf", "SOURCE_BINDING_SUMMARY.png"]}))
