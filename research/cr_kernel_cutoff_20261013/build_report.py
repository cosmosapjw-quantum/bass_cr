"""Rebuild the manuscript and figures from frozen derivations and recorded results.

This authoring command performs no scientific test, ODE solve or old-suite rerun.
Requirements: Python matplotlib/numpy, pandoc, XeLaTeX; bundled fonts included.
"""
from pathlib import Path
import json, re, shutil, subprocess
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
for name in ("latex","figures"):
    (ROOT/name).mkdir(exist_ok=True)

# Plot verified closed forms and recorded branch candidates; no research solver run.
tau=np.linspace(.75,1.25,301)
plt.rcParams.update({"font.size":10,"axes.spines.top":False,
    "axes.spines.right":False,"savefig.bbox":"tight","pdf.fonttype":42})
fig,axs=plt.subplots(1,2,figsize=(9.3,3.6),layout="constrained")
cases=[(-3/25,.8,"#207f87",r"Cooling: $\delta=-3/25$"),
       (0,1,"#73818a",r"Reference: $\delta=0$"),
       (2/25,1.2,"#c37331",r"Heating: $\delta=2/25$")]
curves=[]
for delta,root,color,label in cases:
    f=1.5*tau-.5*tau*tau-1-delta
    axs[0].plot(tau,f,color=color,lw=2,label=label)
    axs[0].scatter([root],[0],color=color,s=30,zorder=5)
    curves.append(f)
axs[0].axhline(0,color="#75808a",lw=.8)
axs[0].set(xlabel=r"Temperature $\tau=T/T_*$",ylabel=r"EOS residual $f(\tau)$",
    title="Exact heating and cooling roots",xlim=(.75,1.25))
axs[0].legend(frameon=False,fontsize=8,loc="upper left")
axs[0].grid(alpha=.16)
from fractions import Fraction
record=json.loads((ROOT/"results/THERMAL_CUTOFF_CHECKS.json").read_text())
heat=record['checks'][1]['heating']
k=heat['indices']; temperatures=[float(Fraction(x)) for x in heat['temperatures']]
axs[1].plot(k,temperatures,'o-',color="#176877",lw=2,ms=5)
for ki,ti,label in zip(k,temperatures,[r"$10$",r"$310/33$",r"$82/9$",r"$388/39$"]):
    axs[1].annotate(label,(ki,ti),xytext=(0,9),textcoords="offset points",ha="center",fontsize=10)
axs[1].set(xlabel="Thermal prefix size k",ylabel="Normalized candidate temperature",
    title="Finite classification at one endpoint",xticks=k,xlim=(-.25,3.25),ylim=(8.9,10.3))
axs[1].grid(alpha=.16)
fig.savefig(ROOT/"figures/cutoff_construction.pdf")
fig.savefig(ROOT/"figures/cutoff_construction.png",dpi=180)
plt.close(fig)
np.savetxt(ROOT/"figures/cutoff_curves.csv",np.column_stack([tau]+curves),delimiter=",",
    header="tau,f_cooling,f_reference,f_heating",comments="")
(ROOT/"figures/atomic_prefix_curve.csv").write_text("prefix,normalized_temperature_exact\n"+
    "".join(f"{i},{t}\n" for i,t in zip(k,heat['temperatures'])))

report=(ROOT/"REPORT_KO.md").read_text()
review=json.loads((ROOT/"RESULTS.json").read_text())
report=report.replace("<!-- REVIEW_STATUS -->",review["decision"])
chapters=[(ROOT/"derivations"/name).read_text() for name in [
    "KERNEL_EVENT_ADAPTER_KO.md","THERMAL_CUTOFF_FEEDBACK_KO.md","COVARIANT_CUTOFF_KO.md"]]
merged=report.replace("<!-- DERIVATIONS -->",
    "\n\\clearpage\n\n"+"\n\n".join(chapters)+"\n")
literature=(ROOT/"LITERATURE_KO.md").read_text()
# The report supplies the top-level literature title.
literature=re.sub(r"\A# [^\n]+\n","",literature,count=1)
merged=merged.replace("<!-- LITERATURE -->","\n\\begingroup\n\\small\n"+literature+"\n\\endgroup\n")
merged=re.sub(r"(?m)^(#{2,6})\s+\d+(?:\.\d+)*\.?\s+",r"\1 ",merged)
merged=merged.replace("n_tot=Σ_s n_s+n_e 및 ṅ_e=Σ_s q_s R_s", r"$n_{\rm tot}=\sum_s n_s+n_e$ 및 $\dot n_e=\sum_s q_s R_s$")
# Long source paths and hashes must wrap in narrow evidence tables.
merged=re.sub(r"`([^`\n]{28,})`",lambda m: r"\nolinkurl{"+m.group(1)+"}" if "{" not in m.group(1) and "}" not in m.group(1) and m.group(1).isascii() else m.group(0),merged)
(ROOT/"latex/manuscript.md").write_text(merged)
subprocess.run(["pandoc",str(ROOT/"latex/manuscript.md"),
    "-f","markdown+tex_math_single_backslash+tex_math_dollars+raw_tex",
    "-t","latex","--wrap=none","--no-highlight",
    "-o",str(ROOT/"latex/body.tex")],check=True)
body=(ROOT/"latex/body.tex").read_text()
body=body.replace(r"\includegraphics{../figures/cutoff_construction.pdf}",
    r"\includegraphics[width=\linewidth]{../figures/cutoff_construction.pdf}")
head=r"""\documentclass[11pt,a4paper]{article}
\usepackage[margin=23mm,headheight=15pt,footskip=12mm]{geometry}
\usepackage{fontspec}
\IfFileExists{fonts/NotoSansCJKkr-Regular.otf}{
\setmainfont{NotoSansCJKkr-Regular.otf}[Path=fonts/,BoldFont=NotoSansCJKkr-Bold.otf,ItalicFont=NotoSansCJKkr-Regular.otf,ItalicFeatures={FakeSlant=0.12}]
\setmonofont{DejaVuSansMono.ttf}[Path=fonts/,Scale=0.75]
}{
\setmainfont{Noto Sans CJK KR}
\setmonofont{DejaVu Sans Mono}[Scale=0.75]
}
\XeTeXlinebreaklocale "ko"
\XeTeXlinebreakskip=0pt plus 0.1em
\usepackage{amsmath,amssymb,mathtools,mathrsfs,graphicx,booktabs,longtable,array}
\usepackage[table,dvipsnames]{xcolor}
\usepackage{enumitem,fancyhdr,titlesec}
\usepackage[unicode,colorlinks=true,linkcolor=MidnightBlue,urlcolor=MidnightBlue,citecolor=MidnightBlue]{hyperref}
\usepackage{xurl,microtype}
\providecommand{\tightlist}{\setlength{\itemsep}{2pt}\setlength{\parskip}{0pt}}
\providecommand{\pandocbounded}[1]{#1}
\setlength{\parindent}{0pt}
\setlength{\parskip}{5pt}
\setlength{\emergencystretch}{3em}
\setlength{\LTpre}{6pt}
\setlength{\LTpost}{8pt}
\setlist{leftmargin=1.6em,itemsep=2pt,topsep=4pt}
\renewcommand{\arraystretch}{1.14}
\linespread{1.08}
\pagestyle{fancy}\fancyhf{}
\fancyhead[L]{\small BASS\_CR · 실제 kernel과 온도 의존 cutoff}
\fancyhead[R]{\small 이론 연구 루프}
\fancyfoot[C]{\thepage}
\titleformat{\section}{\Large\bfseries\color{MidnightBlue}}{\thesection}{.7em}{}
\titleformat{\subsection}{\large\bfseries}{\thesubsection}{.7em}{}
\titleformat{\subsubsection}{\normalsize\bfseries}{\thesubsubsection}{.7em}{}
\setcounter{tocdepth}{1}
\renewcommand{\contentsname}{차례}
\hypersetup{pdftitle={BASS_CR: actual kernel events and temperature-dependent cutoff},
pdfauthor={BASS_CR research record},pdfsubject={CR-THEORY-KERNEL-CUTOFF-20261013}}
\begin{document}
\begin{titlepage}
{\color{MidnightBlue}\large BASS\_CR 연구노트\par}
\vspace{16mm}
{\Huge\bfseries 실제 충돌 kernel과\\[3mm]온도 의존 cutoff의 결합\par}
\vspace{8mm}
{\Large 양의 사건 분해 · 유한 열적 재분류 · 공변 에너지 장부\par}
\vspace{12mm}
{\large 다음 이론 연구 루프\par}
\vspace{4mm}
{2026년 10월 13일 (KST)\par}
\vspace{12mm}
\begin{minipage}{.96\textwidth}
\large
저장된 9600개 에너지 격자와 HI·HeI collision kernel을
보존 사건 열에 연결하고, 온도에 따라 움직이는 cutoff의
유한 count·energy 분할과 양의 해를 구성했다.
연속 spectrum의 오차 certificate, 원자 branch의 유한 알고리즘,
Wolfram·xAct 검산 및 독립 검토를 함께 제공한다.
\end{minipage}
\vfill
\begin{tabular}{@{}ll@{}}
연구 단위 & CR-THEORY-KERNEL-CUTOFF-20261013\\
구성 & 실제 kernel · 유한 cutoff · coupled feedback\\
검산 & 실제 사건 17개 · Wolfram/xAct 28개 그룹\\
도구 & SciSpace · Exa · Wolfram Language · xAct\\
내용 & 전체 유도 · 정확한 사례 · 구현 · DAG · 원출력\\
\end{tabular}
\end{titlepage}
\tableofcontents
\clearpage
"""
(ROOT/"latex/report.tex").write_text(head+body+"\n\\end{document}\n")
for i in range(2):
    run=subprocess.run(["xelatex","-interaction=nonstopmode","-halt-on-error","report.tex"],
        cwd=ROOT/"latex",capture_output=True,text=True)
    (ROOT/f"latex/compile_{i+1}.stdout.txt").write_text(run.stdout)
    (ROOT/f"latex/compile_{i+1}.stderr.txt").write_text(run.stderr)
    if run.returncode:
        print(run.stdout[-7000:])
        raise SystemExit(run.returncode)
print(json.dumps({"pdf":str(ROOT/"latex/report.pdf"),
    "bytes":(ROOT/"latex/report.pdf").stat().st_size},ensure_ascii=False))

