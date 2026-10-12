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

# Plot the exact formula already checked in Wolfram (FP7); no research solver run.
x=np.linspace(0,.5,301)
eta=4/17
f=(3+5*x)/2
psi=eta*f/(1+2*eta*f)
plt.rcParams.update({"font.size":10,"axes.spines.top":False,
    "axes.spines.right":False,"savefig.bbox":"tight","pdf.fonttype":42})
fig,axs=plt.subplots(1,2,figsize=(9.3,3.5),layout="constrained")
axs[0].plot(x,psi,lw=2.2,color="#176877",label=r"$\psi_\eta(x)$")
axs[0].plot(x,x,lw=1.4,ls="--",color="#73818a",label=r"$x$")
axs[0].scatter([.25],[.25],s=42,color="#c06829",zorder=5)
axs[0].annotate(r"$x^\star=1/4$",(.25,.25),xytext=(.29,.16),
    arrowprops={"arrowstyle":"-","color":"#c06829"},fontsize=11)
axs[0].set(xlabel="Reaction extent x",ylabel="Updated extent",
    title="Temperature and composition feedback",xlim=(0,.5),ylim=(0,.5))
axs[0].legend(frameon=False,loc="upper left")
axs[0].grid(alpha=.16)
ua=4*(1-x); chem=1+x; thermal=1+3*x
axs[1].stackplot(x,ua,chem,thermal,colors=["#2a6f8e","#ca8850","#69a990"],
    labels=["Active kinetic","Ionization energy","Thermal kinetic"],alpha=.9)
axs[1].axvline(.25,color="#313d47",ls="--",lw=1)
axs[1].set(xlabel="Reaction extent x",ylabel=r"Energy / $E_0$",
    title="One extent closes the energy account",xlim=(0,.5),ylim=(0,6.4))
axs[1].text(.49,6.09,r"Total $=6E_0$",ha="right",fontsize=10)
axs[1].legend(frameon=False,loc="center left",fontsize=9)
fig.savefig(ROOT/"figures/feedback_construction.pdf")
fig.savefig(ROOT/"figures/feedback_construction.png",dpi=180)
plt.close(fig)
np.savetxt(ROOT/"figures/feedback_curve.csv",
    np.column_stack([x,psi,ua,chem,thermal]),delimiter=",",
    header="x,psi_eta,active_energy_over_E0,chemical_energy_over_E0,thermal_energy_over_E0",
    comments="")

report=(ROOT/"REPORT_KO.md").read_text()
chapters=[(ROOT/"derivations"/name).read_text() for name in [
    "EVENT_STEP_DERIVATION_KO.md","FEEDBACK_THEOREMS_KO.md","COVARIANT_GEOMETRY_KO.md"]]
merged=report.replace("<!-- DERIVATIONS -->",
    "\n\\clearpage\n\n"+"\n\n".join(chapters)+"\n")
literature=(ROOT/"LITERATURE_KO.md").read_text()
# The report supplies the top-level literature title.
literature=re.sub(r"\A# [^\n]+\n","",literature,count=1)
merged=merged.replace("<!-- LITERATURE -->","\n\\begingroup\n\\small\n"+literature+"\n\\endgroup\n")
merged=re.sub(r"(?m)^(#{2,6})\s+\d+\.\s+",r"\1 ",merged)
merged=merged.replace("n_tot=Σ_s n_s+n_e 및 ṅ_e=Σ_s q_s R_s", r"$n_{\rm tot}=\sum_s n_s+n_e$ 및 $\dot n_e=\sum_s q_s R_s$")
(ROOT/"latex/manuscript.md").write_text(merged)
subprocess.run(["pandoc",str(ROOT/"latex/manuscript.md"),
    "-f","markdown+tex_math_single_backslash+tex_math_dollars+raw_tex",
    "-t","latex","--wrap=none","--no-highlight",
    "-o",str(ROOT/"latex/body.tex")],check=True)
body=(ROOT/"latex/body.tex").read_text()
body=body.replace(r"\includegraphics{../figures/feedback_construction.pdf}",
    r"\includegraphics[width=\linewidth]{../figures/feedback_construction.pdf}")
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
\usepackage{amsmath,amssymb,mathtools,graphicx,booktabs,longtable,array}
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
\fancyhead[L]{\small BASS\_CR · 온도와 조성의 자기일관적 진화}
\fancyhead[R]{\small 이론 연구 루프}
\fancyfoot[C]{\thepage}
\titleformat{\section}{\Large\bfseries\color{MidnightBlue}}{\thesection}{.7em}{}
\titleformat{\subsection}{\large\bfseries}{\thesubsection}{.7em}{}
\titleformat{\subsubsection}{\normalsize\bfseries}{\thesubsubsection}{.7em}{}
\setcounter{tocdepth}{1}
\renewcommand{\contentsname}{차례}
\hypersetup{pdftitle={BASS_CR: positive conservative temperature and H/He feedback},
pdfauthor={BASS_CR research record},pdfsubject={CR-THEORY-FEEDBACK-20261013}}
\begin{document}
\begin{titlepage}
{\color{MidnightBlue}\large BASS\_CR 연구노트\par}
\vspace{16mm}
{\Huge\bfseries 온도와 H/He 조성의\\[3mm]자기일관적 진화\par}
\vspace{8mm}
{\Large 양의 보존 사건 step과 공변 에너지 장부\par}
\vspace{12mm}
{\large 다음 이론 연구 루프\par}
\vspace{4mm}
{2026년 10월 13일 (KST)\par}
\vspace{12mm}
\begin{minipage}{.96\textwidth}
\large
같은 반응의 입자수와 에너지 증분을 하나의 사건량으로 갱신하고,
경쟁하는 반응들의 총 소비량으로 양의 재고를 유지하는 유한 step을 구성했다.
온도와 H/He 조성에 따른 계수의 피드백을 닫는 조건을 유도하고,
반복 오차 및 실제 시간 이산화 오차를 온도 허용오차로 연결한다.
Wolfram과 xAct의 실제 검산, 독립 검토, reference 구현을 함께 제공한다.
\end{minipage}
\vfill
\begin{tabular}{@{}ll@{}}
연구 단위 & CR-THEORY-FEEDBACK-20261013\\
구성 & 12개 상태 · 10개 H/He 사건 · 공통 extent\\
검산 & Python 11개 · Wolfram 23개 그룹 통과\\
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

