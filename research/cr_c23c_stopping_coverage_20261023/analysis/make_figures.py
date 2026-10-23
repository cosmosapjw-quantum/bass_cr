"""Saved-result analysis only. No source provider, cutoff solver or ODE is called."""
import argparse
import csv
from fractions import Fraction as F
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import time

ROOT=Path(__file__).resolve().parents[1]


def main(run,cpu):
    os.sched_setaffinity(0,{cpu})
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    from pypdf import PdfReader
    t0=time.perf_counter()
    source=ROOT/"runs/c23c_source_cutoff_binding_20261023_v1/CASES.json"
    cases=json.loads(source.read_text()); selected=[r for r in cases if r["request"]["redshift"]=="2.479"]
    plt.rcParams.update({"font.family":"DejaVu Sans","font.size":8.5,"axes.labelsize":8.5,
        "axes.titlesize":9,"legend.fontsize":7.5,"xtick.labelsize":8,"ytick.labelsize":8,
        "pdf.fonttype":42,"ps.fonttype":42,"axes.spines.top":False,"axes.spines.right":False})
    colors={"3/2":"#3366aa","3":"#c45b14"}
    outputs=[]
    for width in (180,90):
        cols=2 if width==180 else 1; rows=1 if cols==2 else 2
        fig,axes=plt.subplots(rows,cols,figsize=(width/25.4,3.35 if cols==2 else 5.4),layout="constrained")
        a,b=axes.flat
        for chi in ("3/2","3"):
            group=sorted((r for r in selected if r["request"]["chi"]==chi),key=lambda r:F(r["request"]["initial_temperature_K"]))
            x=[float(F(r["request"]["initial_temperature_K"])) for r in group]
            y=[float(F(r["state"]["cutoff"])) for r in group]
            a.loglog(x,y,"o-",color=colors[chi],label=r"$\chi="+("1.5" if chi=="3/2" else "3")+"$")
        a.axhline(10,color="#555555",ls="--",lw=1,label="FS lower edge: 10 eV")
        a.set(xlabel=r"Initial bath $T_0$ [K]",ylabel=r"Caloric cutoff $K_c$ [eV]",title="(a) Distinct energy boundaries")
        a.set_xticks([100,10000,50000],[r"$10^2$",r"$10^4$",r"$5\times10^4$"])
        a.grid(alpha=.18);a.legend(loc="upper left",framealpha=1)
        group=sorted((r for r in selected if r["request"]["chi"]=="3"),key=lambda r:F(r["request"]["initial_temperature_K"]))
        x=np.arange(3);bottom=np.zeros(3)
        names=[("cutoff_thermal","Below caloric cutoff","#6699c7"),("cutoff_active_below_fs","Active, below 10 eV","#ecad63"),("cutoff_active_inside_fs","Active, inside FS band","#98b986"),("cutoff_active_above_fs","Active, above FS band","#b596c8")]
        for key,label,color in names:
            values=[]
            for r in group:
                energy=F(r["primary_kinetic_eV"])
                val=(sum((F(v[1]) for k,v in r["cross_partitions"].items() if k.startswith("cutoff_thermal")),F(0)) if key=="cutoff_thermal" else F(r["cross_partitions"][key][1]))
                values.append(float(val/energy))
            b.bar(x,values,bottom=bottom,color=color,width=.6,label=label);bottom+=values
        b.set_xticks(x,[r"$10^2$",r"$10^4$",r"$5\times10^4$"])
        b.set(xlabel=r"Initial bath $T_0$ [K]",ylabel="Fraction of injected kinetic energy",ylim=(0,1.04),title=r"(b) Source partition, $\chi=3$")
        b.legend(loc="upper center",bbox_to_anchor=(.5,-.22),frameon=False,ncol=1 if width==90 else 2)
        fig.suptitle("C23C: saved PW19 source at z = 2.479",fontsize=10)
        stem=f"cutoff_source_{width}mm"
        for ext in ("png","pdf"):
            f=run/(stem+"."+ext);fig.savefig(f,dpi=190);outputs.append(f)
        plt.close(fig)
        fig,axes=plt.subplots(rows,cols,figsize=(width/25.4,3.35 if cols==2 else 5.4),layout="constrained")
        a,b=axes.flat
        for chi in ("3/2","3"):
            group=sorted((r for r in selected if r["request"]["chi"]==chi),key=lambda r:F(r["request"]["initial_temperature_K"]))
            x=[float(F(r["request"]["initial_temperature_K"])) for r in group]
            y=[-float(F(r["partition_delta_temperature_K"])) for r in group]
            a.loglog(x,y,"o-",color=colors[chi],label=r"$\chi="+("1.5" if chi=="3/2" else "3")+"$")
        a.set(xlabel=r"Initial bath $T_0$ [K]",ylabel=r"Caloric decrease $T_0-T_{cal}$ [K]",title="(a) Particle count enters the EOS")
        a.set_xticks([100,10000,50000],[r"$10^2$",r"$10^4$",r"$5\times10^4$"]);a.grid(alpha=.18);a.legend(frameon=False)
        group=sorted((r for r in selected if r["request"]["chi"]=="3"),key=lambda r:F(r["request"]["initial_temperature_K"]))
        x=np.arange(3);energy=[];number=[];net=[]
        kb=F("1.380649e-23")/F("1.602176634e-19")
        for r in group:
            denom=F(3,2)*kb*F(r["state"]["thermal_count"])
            energy.append(float(F(r["cutoff_classified_source_eV"])/denom))
            number.append(-float(F(3,2)*kb*F(r["initial_temperature_K"])*F(r["cutoff_classified_source_count"])/denom))
            net.append(float(F(r["partition_delta_temperature_K"])))
        b.bar(x-.18,energy,width=.35,color="#c45b14",label="Kinetic term")
        b.bar(x+.18,number,width=.35,color="#3366aa",label="New-particle term")
        b.plot(x,net,"kD",ms=4,label=r"Net $\Delta T_{cal}$")
        b.axhline(0,color="#555555",lw=.8);b.set_yscale("symlog",linthresh=.001)
        b.set_ylim(3*min(number),3*max(energy))
        b.set_xticks(x,[r"$10^2$",r"$10^4$",r"$5\times10^4$"])
        b.set(xlabel=r"Initial bath $T_0$ [K]",ylabel="Signed caloric contribution [K]",title=r"(b) Exact finite difference, $\chi=3$")
        b.legend(loc="upper center",bbox_to_anchor=(.5,-.22),frameon=False,ncol=1 if width==90 else 2)
        fig.suptitle("Caloric classification; physical heating remains null",fontsize=10 if width==180 else 8.5)
        stem=f"caloric_response_{width}mm"
        for ext in ("png","pdf"):
            f=run/(stem+"."+ext);fig.savefig(f,dpi=190);outputs.append(f)
        plt.close(fig)
    pdfchecks=[]
    for p in outputs:
        if p.suffix==".pdf":
            reader=PdfReader(p);page=reader.pages[0];width=float(page.mediabox.width)*25.4/72
            expected=180 if "180mm" in p.name else 90
            assert abs(width-expected)<1e-6 and len(reader.pages)==1
            subprocess.run(["pdftoppm","-singlefile","-scale-to","1600","-png",str(p),str(p.with_name(p.stem+"_pdf_render"))],check=True,capture_output=True,timeout=30)
            pdfchecks.append({"file":p.name,"pages":1,"width_mm":width,"expected_width_mm":expected,"rasterized":True})
    summary={"status":"GENERATED_AWAITING_VISUAL_READ","source":str(source.relative_to(ROOT)),"source_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
             "outputs":[{"path":p.name,"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in outputs],
             "pdf_checks":pdfchecks,"wall_s":time.perf_counter()-t0,"worker_cpu":cpu,"new_science_evaluations":0,"new_ODE":0}
    with (run/"SUMMARY.json").open("x") as f:json.dump(summary,f,indent=2);f.write("\n")
    print(json.dumps({k:v for k,v in summary.items() if k not in ("outputs","pdf_checks")},indent=2))


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--worker",type=Path,required=True);p.add_argument("--cpu",type=int,required=True);a=p.parse_args();main(a.worker,a.cpu)
