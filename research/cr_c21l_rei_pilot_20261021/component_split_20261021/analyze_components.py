"""Read-only component decomposition of source-pinned C21L trajectories.

No solver import and no ODE execution. All arrays use float64 and SI stresses.
Source Pi_*_J_m3 is pi_s = (p_parallel-p_perp)/3, not a tensor norm.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
from pathlib import Path
import tempfile
import zipfile

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "bass_cr_c21l_mplconfig"))
import numpy as np

HERE = Path(__file__).resolve().parent
SOURCE_COMMIT = "60a3f1cb0d8f0875820d18c0d10c448d480334c4"
REI_COMMIT = "3b85dedce84d37b3e165da00685a8a984950aafe"
EXPECTED_IDENTITY = "0090e1549b21b07e46001de2bf9cb2eab9bf0cba87ffe3d4d824ba117fecb44a"
G = 6.67430e-11
C = 299792458.0
SQRT6 = math.sqrt(6.0)
SECTORS = ("m", "gamma", "nu", "r", "tot")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    with Path(path).open("x") as f:
        json.dump(value, f, indent=2, sort_keys=True, allow_nan=False)
        f.write("\n")


def components(h):
    """Return signed amplitudes, complete diagonal tensors and both norms."""
    required = ("eta", "a", "H", "s", "Pi_matter_J_m3", "Pi_gamma_J_m3", "Pi_nu_J_m3")
    for key in required:
        if key not in h:
            raise ValueError("MISSING_SOURCE_SECTOR_OR_FIELD:" + key)
    n = len(h["eta"])
    for key in required:
        if np.asarray(h[key]).shape != (n,) or not np.isfinite(h[key]).all():
            raise ValueError("INVALID_SOURCE_ARRAY:" + key)
    if np.any(h["H"] <= 0):
        raise ValueError("NONPOSITIVE_H")
    out = {k: np.asarray(h[k], dtype=np.float64) for k in ("eta", "a", "H", "s")}
    p = {"m": h["Pi_matter_J_m3"], "gamma": h["Pi_gamma_J_m3"], "nu": h["Pi_nu_J_m3"]}
    p["r"] = p["gamma"] + p["nu"]
    p["tot"] = p["r"] + p["m"]
    # H_t has SI units s^-1; H_geom = H_t/c.  kappa=8*pi*G/c^4.
    norm_factor = (8 * math.pi * G / C**2) * SQRT6 / h["H"]**2
    out["H_geom_m_inverse"] = h["H"] / C
    out["S_signed_F"] = SQRT6 * h["s"] / h["H"]
    out["Sigma_F"] = np.abs(out["S_signed_F"])
    out["Sigma_half"] = out["Sigma_F"] / math.sqrt(2)
    out["sigma_tensor_diag_s_inverse"] = h["s"][:, None] * np.array([-1., -1., 2.])
    for x in SECTORS:
        out[f"pi_s_{x}_J_m3"] = p[x]
        out[f"delta_p_{x}_J_m3"] = 3 * p[x]
        out[f"pi_tensor_diag_{x}_J_m3"] = p[x][:, None] * np.array([-1., -1., 2.])
        out[f"pi_norm_F_{x}_J_m3"] = SQRT6 * np.abs(p[x])
        out[f"P_{x}_signed_F"] = norm_factor * p[x]
        out[f"Pi_{x}_F"] = np.abs(out[f"P_{x}_signed_F"])
        out[f"Pi_{x}_half"] = out[f"Pi_{x}_F"] / math.sqrt(2)
        out[f"sigma_dot_pi_{x}_J_m3_s"] = 6 * h["s"] * p[x]
    denom = np.abs(p["m"]) + np.abs(p["r"])
    defined = denom > 0
    cancellation = np.full(n, np.nan)
    cancellation[defined] = 1 - np.abs(p["tot"][defined]) / denom[defined]
    # Preserve the numerical result; neither clipping nor a physical-zero threshold.
    out["cancellation"] = cancellation
    out["cancellation_defined"] = defined
    out["opposing_signs"] = np.sign(p["m"]) * np.sign(p["r"]) < 0
    return out


def deterministic_npz(path, arrays):
    """Fixed entry metadata makes identical analysis byte-reproducible."""
    with Path(path).open("xb") as file, zipfile.ZipFile(file, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for key in sorted(arrays):
            b = io.BytesIO()
            np.lib.format.write_array(b, np.asarray(arrays[key]), allow_pickle=False)
            info = zipfile.ZipInfo(key + ".npy", date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o600 << 16
            z.writestr(info, b.getvalue(), compresslevel=6)


def plots(out, rows, arrays):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import SymLogNorm
    plt.rcParams.update({"font.size": 10, "axes.titlesize": 11, "pdf.fonttype": 42})
    ss = sorted(set(r["requested_S0"] for r in rows))
    ps = sorted(set(r["requested_P0"] for r in rows))
    matrices = [np.array([r[k] for r in rows]).reshape(len(ss), len(ps)) for k in ("P_m_signed_F_end", "P_r_signed_F_end", "P_tot_signed_F_end")]
    lim = max(np.max(np.abs(a)) for a in matrices)
    fig, axs = plt.subplots(1, 3, figsize=(13.2, 4.5), constrained_layout=True)
    for ax, mat, title in zip(axs, matrices, (r"Matter $P_m$", r"Radiation $P_r=P_\gamma+P_\nu$", r"Total $P_{\rm tot}$")):
        im = ax.imshow(mat, origin="lower", aspect="auto", cmap="RdBu_r", norm=SymLogNorm(linthresh=1e-7, vmin=-lim, vmax=lim))
        ax.set(xticks=range(len(ps)), xticklabels=[f"{x*1e3:g}" for x in ps], yticks=range(len(ss)), yticklabels=[f"{x:g}" for x in ss], xlabel=r"Initial signed $P_{\rm tot,0}$ ($10^{-3}$)", title=title)
        ax.tick_params(axis="x", labelrotation=45)
        ax.set_ylabel(r"Initial $S_0=\sqrt{6}\,s_0/H_0$ (sampled rows)")
    fig.colorbar(im, ax=axs, label="Signed full-Frobenius coordinate at z=4", shrink=.82)
    fig.suptitle("C21L: 81 stored LRS collisionless trajectories; A=0 initially", fontsize=12)
    fig.savefig(out / "component_endpoints.png", dpi=180)
    fig.savefig(out / "component_endpoints.pdf", metadata={"CreationDate": None, "ModDate": None})
    plt.close(fig)
    fig, axs = plt.subplots(2, 2, figsize=(11.4, 7.6), constrained_layout=True, sharey="row")
    selected = ("s04_p08", "s04_p00", "s08_p04", "s00_p04")
    for ax, case_id in zip(axs.flat, selected):
        idx = next(i for i, r in enumerate(rows) if r["case_id"] == case_id)
        z = 1 / arrays["a"][idx] - 1
        for x, color, style in (("m", "#ae337a", "-"), ("r", "#1c78a5", "-"), ("tot", "#222222", "--")):
            ax.plot(z, arrays[f"P_{x}_signed_F"][idx], color=color, ls=style, label={"m":r"$P_m$", "r":r"$P_r$", "tot":r"$P_{\rm tot}$"}[x])
        row = rows[idx]
        ax.axhline(0, color=".6", lw=.6)
        ax.set(xlim=(20, 4), xlabel="Redshift z", ylabel="Signed full-Frobenius stress", title=f"S0={row['requested_S0']:g}, Ptot,0={row['requested_P0']:g}")
        ax.set_yscale("symlog", linthresh=1e-7)
        ax.legend(loc="best", ncol=3, fontsize=10)
    for row_axes, limit in zip(axs, (1.2e-3, 1.5e-4)):
        for ax in row_axes:
            ax.set_ylim(-limit, limit)
    fig.savefig(out / "signed_component_histories.png", dpi=180)
    fig.savefig(out / "signed_component_histories.pdf", metadata={"CreationDate": None, "ModDate": None})
    plt.close(fig)
    fig, axs = plt.subplots(1, 2, figsize=(10.8, 4.4), constrained_layout=True)
    sig = np.array([r["Sigma_F_end"] for r in rows])
    pm, pr, pt = [np.abs(a).ravel() for a in matrices]
    for a, lab, color in ((pm, r"$\Pi_m$", "#ae337a"), (pr, r"$\Pi_r$", "#1c78a5"), (pt, r"$\Pi_{\rm tot}$", "#222222")):
        if lab == r"$\Pi_{\rm tot}$":
            axs[0].scatter(sig, a, s=28, label=lab, facecolors="none", edgecolors=color, linewidths=.65)
        else:
            axs[0].scatter(sig, a, s=16, label=lab, color=color, alpha=.7)
    axs[0].set(xlabel=r"$\Sigma$ at z=4", ylabel="Nonnegative full-Frobenius norm")
    axs[0].set_yscale("symlog", linthresh=1e-7)
    axs[0].legend()
    cancel = np.array([r["cancellation_end"] if r["cancellation_end"] is not None else np.nan for r in rows])
    display = (pm + pr) > 1e-12
    points=axs[1].scatter(np.array([r["requested_S0"] for r in rows])[display], cancel[display], c=np.array([r["requested_P0"] for r in rows])[display]*1e3, cmap="RdBu_r", s=28)
    fig.colorbar(points, ax=axs[1], label=r"Initial signed $P_{\rm tot,0}$ ($10^{-3}$)", shrink=.8)
    axs[1].set(xlabel=r"Initial signed $S_0$", ylabel=r"$1-|\pi_{s,m}+\pi_{s,r}|/(|\pi_{s,m}|+|\pi_{s,r}|)$", ylim=(-.03, 1.03), title="Stress cancellation at z=4")
    axs[1].text(.02, .97, r"Display: $\Pi_m+\Pi_r>10^{-12}$", transform=axs[1].transAxes, va="top", fontsize=9)
    fig.savefig(out / "norms_and_cancellation.png", dpi=180)
    fig.savefig(out / "norms_and_cancellation.pdf", metadata={"CreationDate": None, "ModDate": None})
    plt.close(fig)


def analyze(input_dir, output_dir, make_plots=True):
    raw = Path(input_dir).resolve()
    out = Path(output_dir).resolve()
    manifest = json.loads((raw / "MANIFEST.json").read_text())
    if manifest["identity"] != EXPECTED_IDENTITY:
        raise ValueError("C21L_INPUT_IDENTITY_MISMATCH")
    canonical = json.dumps(manifest["manifest"], sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    if hashlib.sha256(canonical).hexdigest() != EXPECTED_IDENTITY:
        raise ValueError("C21L_MANIFEST_CONTENT_MISMATCH")
    histories, rows, sources = [], [], []
    residuals = {"signed_total_vs_original": 0., "Sigma_vs_original": 0., "radiation_scalar_sum": 0., "normalized_tensor_closure": 0.}
    for path in sorted((raw / "cases").glob("*/history.npz")):
        receipt = json.loads((path.parent / "RESULT.json").read_text())
        if receipt["status"] != "COMPLETE" or receipt["identity"] != EXPECTED_IDENTITY or sha(path) != receipt["history_sha256"]:
            raise ValueError("RAW_OR_RECEIPT_IDENTITY_MISMATCH:" + path.parent.name)
        with np.load(path, allow_pickle=False) as archive:
            h = {k: archive[k] for k in archive.files}
        if h["Y"].shape != (40, 101) or h["Y"].dtype != np.float64 or not np.isfinite(h["Y"]).all():
            raise ValueError("ORIGINAL_STATE_SHAPE_OR_DTYPE")
        d = components(h)
        residuals["signed_total_vs_original"] = max(residuals["signed_total_vs_original"], float(np.max(np.abs(d["P_tot_signed_F"] - h["P"]))))
        residuals["Sigma_vs_original"] = max(residuals["Sigma_vs_original"], float(np.max(np.abs(d["Sigma_F"] - h["Sigma_F"]))))
        rs = np.max(np.abs(d["pi_s_r_J_m3"] - h["Pi_radiation_J_m3"]) / np.maximum(np.abs(d["pi_s_r_J_m3"]), 1e-300))
        residuals["radiation_scalar_sum"] = max(residuals["radiation_scalar_sum"], float(rs))
        residuals["normalized_tensor_closure"] = max(residuals["normalized_tensor_closure"], float(np.max(np.abs(d["P_tot_signed_F"] - d["P_m_signed_F"] - d["P_r_signed_F"]))))
        m = receipt["mapping"]
        row = {"case_id":path.parent.name, "requested_S0":m["requested_S0"], "requested_P0":m["requested_P0"], "k_gamma":m["k_gamma"], "k_nu":m["k_nu"], "massive_A":0.}
        for key, arr in d.items():
            if arr.ndim == 1:
                for suffix, i in (("initial", 0), ("end", -1)):
                    v = arr[i]
                    row[key + "_" + suffix] = bool(v) if arr.dtype == bool else (float(v) if np.isfinite(v) else None)
        rows.append(row)
        histories.append(d)
        sources.append({"case_id":path.parent.name,"raw_relative_path":str(path.relative_to(raw)),"history_sha256":sha(path),"receipt_sha256":sha(path.parent/"RESULT.json")})
    if len(rows) != 81:
        raise ValueError("EXPECTED_EXACTLY_81_COMPLETED_CASES")
    if residuals["signed_total_vs_original"] > 2e-17 or residuals["normalized_tensor_closure"] > 2e-17 or residuals["radiation_scalar_sum"] > 2e-14:
        raise ArithmeticError("COMPONENT_CLOSURE_MISMATCH")
    out.mkdir(parents=True, exist_ok=False)
    arrays = {key:np.stack([h[key] for h in histories]) for key in histories[0]}
    arrays["case_ids"] = np.array([r["case_id"] for r in rows])
    deterministic_npz(out / "components81.npz", arrays)
    with (out / "endpoints_components81.csv").open("x", newline="") as f:
        w=csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    summary = {"cases":81,"saved_samples":81*101,"new_physical_ODE_runs":0,"source_content_commit":SOURCE_COMMIT,"rei_source_commit":REI_COMMIT,"input_identity":EXPECTED_IDENTITY,"source_manifest_sha256":sha(raw/"MANIFEST.json"),"closure_residuals":residuals,"endpoint_maxima":{k:max(r[k+"_end"] for r in rows) for k in ("Sigma_F","Pi_m_F","Pi_r_F","Pi_tot_F")},"endpoint_cancellation_max":max(r["cancellation_end"] for r in rows if r["cancellation_end"] is not None),"sector_status":{"massive_nonbaryonic":"present_fm_0.1_M_over_Tref_30","cold_dust":"present_isotropic_by_model","gamma":"present_collisionless","nu":"present_massless_collisionless","UV":"absent_from_source","thermal_reionization_gas":"unavailable_not_evolved"},"conventions":{"metric":"(-,+,+,+)","source_Pi_J_m3":"pi_s = delta_p/3; tensor diag(-pi_s,-pi_s,2*pi_s)","shear":"diag(-s,-s,2s)","Sigma_F":"sqrt(6)*abs(s)/H_t","P_X_signed_F":"sqrt(6)*(8*pi*G/c^2)*pi_s_X/H_t^2","Pi_X_F":"abs(P_X_signed_F)","half_contraction":"Frobenius/sqrt(2)","H_t":"s^-1","H_geom":"H_t/c (m^-1)","kappa":"8*pi*G/c^4","cancellation":"1-abs(pi_m+pi_r)/(abs(pi_m)+abs(pi_r)); undefined at exact zero denominator"},"global_error_bound":None,"result_scope":"preliminary LRS collisionless fixed-A=0 ensemble, z20 to z4","reconstruction":"new postprocessor from published raw; original unposted component file not recovered"}
    write_json(out/"SUMMARY.json",summary)
    write_json(out/"INPUTS.json",sources)
    if make_plots:
        plots(out,rows,arrays)
    write_json(out/"OUTPUT_MANIFEST.json",{"analyzer_sha256":sha(__file__),"files":[{"path":p.name,"bytes":p.stat().st_size,"sha256":sha(p)} for p in sorted(out.iterdir()) if p.is_file()]})
    return summary


if __name__ == "__main__":
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input",type=Path,default=HERE.parent/"runs/pilot81")
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--no-plots",action="store_true")
    args=ap.parse_args()
    print(json.dumps(analyze(args.input,args.output,not args.no_plots),indent=2))
