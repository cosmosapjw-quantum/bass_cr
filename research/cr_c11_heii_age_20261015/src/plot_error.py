"""Reproduce sampled HeII holdout error plot from the source-bound JSON."""
import argparse, json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def plot(source: Path, output: Path):
    data=json.loads(source.read_text())
    q=[r["q_ref"] for r in data["records"]]
    fig,ax=plt.subplots(figsize=(7,4.25))
    for design,label,fmt in (("1","one training gas","o-"),
                              ("3","three training gases","s-")):
        values=[r["designs"][design]["holdout_max_error"] for r in data["records"]]
        ax.plot(q,values,fmt,label=label)
    ax.set_yscale("log")
    ax.set_xlabel("q_ref (Bianchi source-geometry parameter)")
    ax.set_ylabel("Maximum sampled-gas relative error")
    ax.set_title("SOURCE07 C8 HeII age-compression pilot")
    ax.grid(alpha=.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output,dpi=150)
    plt.close(fig)

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("input",type=Path)
    ap.add_argument("output",type=Path)
    x=ap.parse_args()
    plot(x.input,x.output)
