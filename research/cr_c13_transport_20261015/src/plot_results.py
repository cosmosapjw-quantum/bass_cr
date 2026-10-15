"""Create plot from existing checked source integral results."""
import sys,json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def main(folder):
    folder=Path(folder)
    data=json.loads((folder/"VALIDATION.json").read_text())
    x=[row["nsteps"] for row in data["samples"]["0.0"]["convergence"]]
    y=[abs(row["source_relative_error"]) for row in data["samples"]["0.0"]["convergence"]]
    fig,ax=plt.subplots(figsize=(6.4,4.2))
    ax.loglog(x,y,'o-',label="midpoint born-source quadrature")
    ax.set_xlabel("Time intervals")
    ax.set_ylabel("Absolute relative emitted-photon error")
    ax.set_title("C13 source quadrature vs owner QUADPACK")
    ax.grid(which="both",alpha=.3);ax.legend()
    fig.tight_layout();fig.savefig(folder/"SOURCE_CONVERGENCE.png",dpi=160)
    plt.close(fig)
if __name__=="__main__":main(sys.argv[1])
