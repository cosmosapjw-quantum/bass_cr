"""Render saved M2 results only. No scientific evaluator is rerun."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

BASE = Path(__file__).resolve().parent
d = json.loads((BASE / "results/RESPONSE_ERROR_MAP.json").read_text())
r = next(r for r in d["rows"] if r["model"] == "fullBED" and r["representation"] == "selected_record")
v = lambda p: float(p["decimal60"])
names = ["constant", "linear_rise", "convex_rise", "concave_rise", "quadratic_decline", "parabolic_pulse"]
labels = ["Constant", "Linear rise", "Quadratic rise", "Concave rise", "Decline to zero", "Parabolic pulse"]
colors = {"exact": "#162c46", "finite_age_first": "#cd7752", "finite_age_positive": "#248a84"}
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.titleweight": "bold", "axes.titlesize": 11})
fig, axes = plt.subplots(1, 2, figsize=(12.4, 4.9), gridspec_kw={"width_ratios": [1.18, 1]})
ax = axes[0]
x = np.arange(len(names))
for shift, key, label in [(-.17, "exact", "Retained exact quadratic response"),
                          (0, "finite_age_first", "Finite-age first derivative"),
                          (.17, "finite_age_positive", "Conditional mean delay")]:
    y = [100 * v(r["controlled_histories"][n][key]) for n in names]
    ax.plot(x + shift, y, "o", color=colors[key], label=label, markersize=6)
ax.set_xticks(x, labels, rotation=24, ha="right")
ax.set_ylabel(r"Heating / $(H_0 q_*)$  [%]")
ax.set_ylim(-.4, 13.2)
ax.grid(axis="y", color="#dddddd", linewidth=.6)
ax.set_title("(a) Same finite-age source histories", loc="left")
ax.legend(loc="upper left", frameon=False, fontsize=8.2)
ax.text(.03, .61, "Instantaneous reference: 100% for the four rising/onset\nhistories; 0% for both shutoff histories.",
        transform=ax.transAxes, fontsize=8.0, color="#596471")
ax = axes[1]
kappa = np.geomspace(.01, 10, 100)
c1 = v(r["parameters"]["C_first"])
cp = v(r["parameters"]["C_positive"])
ax.loglog(kappa, 100*c1*kappa, color=colors["finite_age_first"], linewidth=2, label="First derivative bound")
ax.loglog(kappa, 100*cp*kappa, color=colors["finite_age_positive"], linewidth=2, label="Conditional mean-delay bound")
ax.axhline(.1, linestyle=":", color="#737f8c", linewidth=1.2, label="Example: 0.1% of reference")
ax.set_xlabel(r"Source curvature $\kappa=T^2\|q''\|_\infty/q_*$")
ax.set_ylabel(r"Absolute error bound / $(H_0 q_*)$  [%]")
ax.set_title("(b) Curvature error budget at fixed age", loc="left")
ax.grid(which="major", color="#dddddd", linewidth=.6)
ax.legend(loc="upper left", frameon=False, fontsize=8.2)
ax.text(.98, .07, f"Bound coefficient reduced by {c1/cp:.4f}\nExample line uses H0 q* / P_ref = 1",
        transform=ax.transAxes, ha="right", fontsize=8.5, color="#596471")
fig.suptitle("CR heating from saved delay moments", x=.07, ha="left", fontsize=16, fontweight="bold")
fig.subplots_adjust(left=.075, right=.985, top=.84, bottom=.23, wspace=.32)
fig.text(.075, .065, "fullBED selected record  |  T = 10^10 s (316.88 yr)  |  Fixed bath, spectrum and causal kernel", fontsize=9)
fig.text(.075, .026, "Arithmetic of retained records; controlled closure diagnostics. Physical input, mesh and cosmological-history errors are not certified here.", fontsize=8.3, color="#596471")
for suffix in ("png", "pdf"):
    p = BASE / "results" / ("RESPONSE_ERROR_MAP." + suffix)
    if p.exists():
        raise FileExistsError("Do not overwrite an existing figure")
    fig.savefig(p, dpi=190)
plt.close(fig)
print("Rendered saved M2 results to PNG and PDF")
