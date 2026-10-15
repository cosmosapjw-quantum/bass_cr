"""Plots from C17 actually executed owner species/Radau and timing JSON."""
import json
from pathlib import Path
import argparse
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def plot(root:Path):
    d=json.loads((root/"OWNER_SPECIES_RADAU.json").read_text())
    fig,ax=plt.subplots(figsize=(7.0,4.6))
    styles={-.01:("o-","s-"),0.:("^-","d-"),.01:("x-","v-")}
    for r in d["q_cases"]:
        q=r["q"]
        n=[c["base_intervals"] for c in r["grid_runs"]]
        a=[c["C16_species_total_max_rel_error"] for c in r["grid_runs"]]
        b=[c["C17_species_total_max_rel_error"] for c in r["grid_runs"]]
        old,new=styles[q]
        ax.loglog(n,a,old,label=f"C16 allocation, q={q:+.2f}")
        ax.loglog(n,b,new,label=f"C17 time events, q={q:+.2f}")
    ax.set_xlabel("Base log(a) time intervals")
    ax.set_ylabel("Maximum H/He species-total relative error vs Radau")
    ax.set_title("C17: species-resolved HI/HeI/HeII photoevents")
    ax.grid(which="both",alpha=.22)
    ax.legend(fontsize=7,ncol=2)
    fig.tight_layout()
    fig.savefig(root/"SPECIES_CONVERGENCE.png",dpi=160)
    plt.close(fig)

    b=json.loads((root/"BENCHMARK.json").read_text())
    fig,ax=plt.subplots(figsize=(6.8,4.3))
    keys=["C16_approx","C17_species_32x24","C17_species_64x48"]
    labels=["C16 approximate","C17 32 x 24","C17 64 x 48"]
    values=[b["schemes"][k]["median_s"] for k in keys]
    ax.bar(labels,values)
    ax.set_ylabel("Median seconds for 4096 photon packet update")
    ax.set_title("C17 vectorized integration costs (different accuracy)")
    for i,v in enumerate(values):
        ax.text(i,v,f"{v:.3f} s",ha="center",va="bottom")
    ax.set_ylim(0,max(values)*1.18)
    fig.tight_layout()
    fig.savefig(root/"PACKET_KERNEL_TIMINGS.png",dpi=160)
    plt.close(fig)

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("folder",type=Path)
    plot(parser.parse_args().folder)
