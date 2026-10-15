"""Plots measured C16 owner/Radau errors, no extrapolated data."""
from __future__ import annotations
import json,sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def make(folder:Path):
    d=json.loads((folder/"OWNER_RAY_THRESHOLD_AWARE.json").read_text())
    rows=[r for r in d["results"] if r["q"]==0.]
    full=next(r for r in rows if not r["threshold_aware"])
    split=next(r for r in rows if r["threshold_aware"])
    fig,ax=plt.subplots(figsize=(7.2,4.5))
    for row,method,label,style in (
       (full,"C16_optical_quad","No threshold partition","o-"),
       (split,"C16_optical_quad","Split at actual H ionization threshold","s-"),
       (split,"C16_endpoint_weighted","Split, fast endpoint approximation","^-"),
    ):
        curves=row["curves"]
        ax.loglog([c["nsteps"] for c in curves],
          [c["methods"][method]["max_relative_photon_error"] for c in curves],
          style,label=label)
    ax.set_xlabel("Base log(a) time intervals")
    ax.set_ylabel("Max relative photon-stock error vs independent Radau")
    ax.set_title("C16: threshold-resolved time-varying H/He photon source")
    ax.grid(which="both",alpha=.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(folder/"THRESHOLD_TIME_CONVERGENCE.png",dpi=160)
    plt.close(fig)

    b=json.loads((folder/"BENCHMARK.json").read_text())
    fig,ax=plt.subplots(figsize=(6.8,4.4))
    names=("endpoint_weighted","optical_quadrature")
    timings=[b["vectorized_kernels"][k]["median_s"]*1000 for k in names]
    ax.bar(names,timings)
    ax.set_ylabel("Median latency for 4096 packet update (ms)")
    ax.set_title("C16: vectorized speed with DIFFERENT accuracy envelopes")
    for i,t in enumerate(timings):
        ax.text(i,t,format(t,".3f")+" ms",ha="center",va="bottom")
    ax.set_ylim(0,max(timings)*1.22)
    fig.tight_layout()
    fig.savefig(folder/"KERNEL_BENCHMARK.png",dpi=160)
    plt.close(fig)

if __name__=="__main__":
    make(Path(sys.argv[1]))