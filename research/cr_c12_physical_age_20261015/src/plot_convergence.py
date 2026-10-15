"""Plot tested, independent-ODE-referenced time convergence, no extrapolated slopes."""
from pathlib import Path
import json,argparse
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def create(src:Path,out:Path):
    data=json.loads(src.read_text())
    fig,ax=plt.subplots(figsize=(6.8,4.4))
    for key,label,fmt in [("frozen","Frozen opacity","o-"),
                          ("midpoint","Midpoint exponential","s-")]:
        group=data["time_convergence"][key]
        xs=[x["nstep"] for x in group]
        ys=[abs(x["error_xHI"]) for x in group]
        ax.loglog(xs,ys,fmt,label=label)
    ax.set_xlabel("Number of proper-time steps")
    ax.set_ylabel("Absolute HI-fraction error vs independent DOP853")
    ax.set_title("Local H/He photon reservoir: time-order check")
    ax.grid(which="both",alpha=.2)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out,dpi=160)
    plt.close(fig)


if __name__=="__main__":
    a=argparse.ArgumentParser();a.add_argument("src",type=Path);a.add_argument("out",type=Path)
    v=a.parse_args();create(v.src,v.out)
