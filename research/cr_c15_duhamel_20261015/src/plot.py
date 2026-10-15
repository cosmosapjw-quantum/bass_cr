"""Evidence plots made only from executed C15 VALIDATION.json."""
import json,sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

def make(folder:Path):
    d=json.loads((folder/"VALIDATION.json").read_text())
    fig,ax=plt.subplots(figsize=(7,4.4))
    for name,label,fmt in (
        ("weak_below5500","Weak source, T<5500 K","o-"),
        ("strong_cross5500","Heating across 5500 K","s-"),
        ("hot_above5500","Hot gas, T>5500 K","^-"),
        ("strong_no_rr","No recombination","d-"),
    ):
        r=d["controlled_gas_convergence"][name]["runs"]
        n=np.array([x["n"] for x in r])
        diffs=np.abs(np.diff([x["xHI"] for x in r]))
        ax.loglog(n[:-1],diffs,fmt,label=label)
    ax.set_xlabel("N time intervals (difference against 2N)")
    ax.set_ylabel("|xHI(N)-xHI(2N)|")
    ax.set_title("C15: conditional gas time-convergence check")
    ax.grid(which="both",alpha=.25);ax.legend(fontsize=8)
    fig.tight_layout();fig.savefig(folder/"GAS_CONVERGENCE.png",dpi=160)
    plt.close(fig)

    fig,ax=plt.subplots(figsize=(7,4.4))
    rows=d["controlled_gas_convergence"]["strong_no_rr"]["runs"]
    n=np.array([x["n"] for x in rows])
    photons=[x["photons"] for x in rows]
    diffs=np.abs(np.diff(photons))
    ax.loglog(n[:-1],diffs,'o-',label="Remaining-photon-stock difference")
    ax.set_xlabel("N time intervals (difference against 2N)")
    ax.set_ylabel("|N_gamma(N)-N_gamma(2N)| photons/H")
    ax.set_title("C15: photon survivor retains first-order-like residual")
    ax.grid(which="both",alpha=.25);ax.legend()
    fig.tight_layout();fig.savefig(folder/"SURVIVOR_CONVERGENCE.png",dpi=160)
    plt.close(fig)

if __name__=="__main__":
    make(Path(sys.argv[1]))