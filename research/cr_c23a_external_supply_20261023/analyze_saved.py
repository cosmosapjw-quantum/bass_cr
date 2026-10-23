"""Read-only analysis of new saved C23A source responses; never integrates ODEs."""
from __future__ import annotations
import csv
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import sys
import time

for key in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","BLIS_NUM_THREADS","NUMEXPR_NUM_THREADS"):
    os.environ[key]="1"
ROOT=Path(__file__).resolve().parent
os.environ.setdefault("MPLCONFIGDIR",str(ROOT/"runtime/matplotlib_cache"))

def main():
    start=time.perf_counter();cpu0=time.process_time()
    out=ROOT/"analysis_v3"
    out.mkdir(exist_ok=False)
    lease_dir=Path("/tmp/rei-bianchi-cooperative-leases")
    lease_path=lease_dir/"c23a_saved_analysis_20261023_v1.json"
    with (lease_dir/"leases.lock").open("a+") as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        for p in lease_dir.glob("*.json"):
            doc=json.loads(p.read_text())
            for e in doc.get("leases",[doc]):
                cs=e.get("cpus")
                if not isinstance(cs,list) or any(type(c)is not int or c<0 for c in cs):
                    raise RuntimeError("UNKNOWN_LEASE_WITHHOLDS_WORKER")
                if 1 in cs:raise RuntimeError("CPU1_LEASED")
        lease={"schema":"C21_CPU_LEASES_V1","leases":[{"owner":"c23a_saved_analysis_20261023_v1","cpus":[1],"pid":os.getpid()}]}
        with lease_path.open("x") as f:json.dump(lease,f)
    try:
        if 1 not in os.sched_getaffinity(0):raise RuntimeError("CPU1_UNAVAILABLE")
        memlim=int(Path("/sys/fs/cgroup/memory.max").read_text());memcur=int(Path("/sys/fs/cgroup/memory.current").read_text())
        if memlim-memcur<512*1024**2:raise RuntimeError("MEMORY_HEADROOM_UNAVAILABLE")
        os.sched_setaffinity(0,{1})
        import numpy as np
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from igm.p19_uvb import P19Fiducial
        plt.rcParams.update({"font.size":12,"axes.titlesize":13,"axes.labelsize":12,"legend.fontsize":10,
                             "xtick.labelsize":11,"ytick.labelsize":11,"lines.linewidth":2,
                             "savefig.dpi":180,"pdf.fonttype":42})
        run=ROOT/"runs/c23a_p19_subflow_20261023_v1"
        with (run/"responses.csv").open() as f:raw=list(csv.DictReader(f))
        rows=[{k:(v if k=="initial" else float(v)) for k,v in r.items()} for r in raw]
        file_hash=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
        source_inputs={"run_csv":file_hash(run/"responses.csv"),"run_summary":file_hash(run/"SUMMARY.json"),
                       "analysis_code":file_hash(Path(__file__))}
        files=[]
        def save(fig,name):
            for ext in ("png","pdf"):
                p=out/(name+"."+ext)
                if p.exists():raise FileExistsError(p)
                if name=="p19_frozen_exposures":
                    fig.savefig(p,bbox_inches="tight")
                else:
                    # Preserve already reviewed unaffected render bytes.
                    with p.open("xb") as f:f.write((ROOT/"analysis_v2"/p.name).read_bytes())
                files.append({"path":p.name,"sha256":file_hash(p),"bytes":p.stat().st_size})
            plt.close(fig)
        model=P19Fiducial();z=np.array(model.z_nodes)
        data=np.array([r[1:7] for r in model.rows]);colors=("#0072B2","#D55E00","#009E73")
        fig,axs=plt.subplots(2,1,figsize=(7.1,7.3),sharex=True,layout="constrained")
        for j,(label,c) in enumerate(zip(("H I","He I","He II"),colors)):
            axs[0].semilogy(z,data[:,2*j],label=label,color=c)
            axs[1].plot(z,data[:,2*j+1]/data[:,2*j],color=c)
        axs[0].set(title="(a) P19 v1 fiducial source nodes",ylabel=r"Ionization rate $\Gamma_i$ (s$^{-1}$)")
        axs[0].legend(ncol=3,loc="lower left")
        axs[1].set(title="(b) Supplied mean excess energy",xlabel="Redshift of the imposed background",ylabel=r"$H_i/\Gamma_i$ (eV per event)")
        for ax in axs:ax.grid(alpha=.22);ax.set_xlim(0,15.1)
        save(fig,"p19_source_moments")
        fig,axs=plt.subplots(2,1,figsize=(7.1,7.2),sharex=True,layout="constrained")
        for dose,c in zip((1,10,100),colors):
            s=[r for r in rows if r["initial"]=="neutral" and r["max_rate_duration"]==dose]
            axs[0].plot([r["redshift"] for r in s],[r["temperature_K"]/1000 for r in s],label=rf"$\theta={dose:g}$",color=c)
            axs[1].plot([r["redshift"] for r in s],[r["electron_increment"] for r in s],color=c)
        axs[0].set(title="(a) Independent frozen-source exposures",ylabel="Final gas temperature (1000 K)")
        axs[0].legend(ncol=3,loc="lower right")
        axs[1].set(title="(b) Electron production from the same events",xlabel="Redshift labelling each fixed background",ylabel="Electrons per initial H nucleus")
        for ax in axs:ax.grid(alpha=.22);ax.set_xlim(0,15.1)
        fig.suptitle(r"Initially neutral H/He, $T_0=100$ K; $\theta=\max_i\Gamma_i\,\Delta t$",fontsize=12)
        save(fig,"p19_frozen_exposures")
        dep=ROOT/"deposition/c23a_precontraction_timing_20261023_v1"
        counter=json.loads((dep/"MOMENT_COUNTEREXAMPLE.json").read_text())[0]
        timing=json.loads((dep/"RESULT.json").read_text())
        source_inputs["deposition_counterexample"]=file_hash(dep/"MOMENT_COUNTEREXAMPLE.json")
        source_inputs["deposition_timing"]=file_hash(dep/"RESULT.json")
        fig,axs=plt.subplots(1,2,figsize=(9,4.6),layout="constrained")
        xa=np.arange(2);bottom=np.zeros(2)
        for k,(label,c) in enumerate(zip(("Ionization","Heat","Excitation"),colors)):
            y=np.array([counter["A_energy_ion_heat_exc_eV"][k],counter["B_energy_ion_heat_exc_eV"][k]])
            axs[0].bar(xa,y,bottom=bottom,label=label,color=c,width=.6);bottom+=y
        axs[0].set_xticks(xa,["1 at 100 eV","0.5 at 10 eV\n+ 0.5 at 190 eV"])
        axs[0].set(ylabel="Reported deposition energy (eV)",title=r"(a) Equal count and energy, $\xi=0.1$",ylim=(0,123))
        axs[0].legend(ncol=1,loc="upper left",fontsize=9,framealpha=.9)
        ratios=[p["direct_over_build_plus_queries"] for p in timing["pairs"]]
        axs[1].scatter(range(1,10),ratios,color="#0072B2",s=35)
        axs[1].axhline(1,color="gray",linestyle=":",label="Equal elapsed time")
        axs[1].axhline(timing["median_build_plus_64_queries_ratio"],color="#D55E00",linestyle="--",label="Median 4.91")
        axs[1].set(xlabel="Paired measurement",ylabel="Direct / (prepare + 64 queries)",title="(b) Same-input single-CPU timing",ylim=(0,6.7),xticks=[1,3,5,7,9])
        axs[1].legend(loc="lower right",fontsize=9)
        save(fig,"deposition_moments_and_cost")
        summary={"schema":"C23A_SAVED_ANALYSIS_V1","created_utc":datetime.now(timezone.utc).isoformat(),
                 "source_inputs_sha256":source_inputs,"files":files,"read_only_saved_rows":len(rows),
                 "new_ODE":0,"source_subflow_reexecutions":0,"historical_ODE_reruns":0,
                 "initial_neutral_response_notes":"Temperature curves are independent fixed-source exposures, not IGM thermal histories; no recombination/cooling/expansion included.",
                 "energy_ledger_notes":"Raw FS source fraction defect is preserved; plotted channel sums are not renormalized to 100 eV.",
                 "memory_headroom_before_bytes":memlim-memcur,"worker_cpu":1,"native_threads":1,
                 "wall_s":time.perf_counter()-start,"cpu_s":time.process_time()-cpu0,"global_error_bound":None}
        with (out/"ANALYSIS.json").open("x") as f:json.dump(summary,f,ensure_ascii=False,indent=2,allow_nan=False)
        print(json.dumps(summary,ensure_ascii=False))
    finally:
        with (lease_dir/"leases.lock").open("a+") as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            if lease_path.exists() and json.loads(lease_path.read_text())==lease:lease_path.unlink()

if __name__=="__main__":main()
