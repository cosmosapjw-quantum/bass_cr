"""Build the theory report from reviewed Markdown and recorded toy data."""
from pathlib import Path
import json
import subprocess
import re
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.integrate import quad

ROOT=Path(__file__).resolve().parent
data=np.genfromtxt(ROOT/"results/TOY_EVOLUTION.csv",delimiter=",",names=True)
t=data["time"]
B=data["certificate"]
temp_err=np.abs(data["actual_thermal_energy"]-data["reference_thermal_energy"])/2
temp_bound=np.array([
  (b+quad(lambda s:(2/3)*np.exp(2*s/3)*(1-(s+1)*np.exp(-s)),0,float(tt),
          epsabs=1e-12)[0]/np.exp(2*tt/3))/2 for tt,b in zip(t,B)])
plt.rcParams.update({"font.size":10,"axes.spines.top":False,
                     "axes.spines.right":False,"savefig.bbox":"tight",
                     "pdf.fonttype":42})
fig,axs=plt.subplots(1,2,figsize=(9.4,3.25),layout="constrained")
axs[0].plot(t,data["state_plus_heat_error"],color="#174f78",lw=2,label="State + heat error")
axs[0].plot(t,B,color="#b86223",lw=2,ls="--",label="Duhamel bound")
axs[1].plot(t,temp_err,color="#174f78",lw=2,label="Temperature error")
axs[1].plot(t,temp_bound,color="#b86223",lw=2,ls="--",label="Transferred bound")
for ax in axs:
    ax.set_xlabel("Dimensionless time")
    ax.set_xlim(0,1)
    ax.set_ylim(bottom=0)
    ax.grid(alpha=.16)
    ax.legend(frameon=False,loc="upper left",fontsize=9)
axs[0].set_title("Noncommuting collision response",loc="left",fontsize=11)
axs[1].set_title("Temperature after expansion",loc="left",fontsize=11)
axs[0].set_ylabel("Energy error (dimensionless)")
axs[1].set_ylabel("Temperature error (dimensionless)")
fig.savefig(ROOT/"figures/theory_certificates.pdf")
fig.savefig(ROOT/"figures/theory_certificates.png",dpi=180)
plt.close(fig)

report=(ROOT/"REPORT_KO.md").read_text()
marker="# 새 검산과 독립 검토"
before,after=report.split(marker,1)
chapters=[]
for name in ["MOVING_CUTOFF_KO.md","THERMAL_EXCESS_KO.md","COLLISION_CLOCK_KO.md"]:
    chapters.append((ROOT/"derivations"/name).read_text())
merged=before+"\n\n\\clearpage\n\n"+"\n\n\\clearpage\n\n".join(chapters)
merged+="\n\n\\clearpage\n\n"+marker+after
merged=re.sub(r"(?m)^(#{2,6})\s+\d+\.\s+",r"\1 ",merged)
(ROOT/"latex/manuscript.md").write_text(merged)
subprocess.run(["pandoc",str(ROOT/"latex/manuscript.md"),
    "-f","markdown+tex_math_single_backslash+tex_math_dollars+raw_tex",
    "-t","latex","--wrap=none","--no-highlight",
    "-o",str(ROOT/"latex/body.tex")],check=True)
body=(ROOT/"latex/body.tex").read_text()
body=body.replace(r"\includegraphics{../figures/theory_certificates.pdf}",
                  r"\includegraphics[width=\linewidth]{../figures/theory_certificates.pdf}")
# Long filenames and identifiers are prose data, with a smaller monospace face.
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
\usepackage{xurl}
\usepackage{microtype}
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
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small BASS\_CR · 시간 변화 배경의 전자 열화}
\fancyhead[R]{\small 이론 연구 루프}
\fancyfoot[C]{\thepage}
\titleformat{\section}{\Large\bfseries\color{MidnightBlue}}{\thesection}{.7em}{}
\titleformat{\subsection}{\large\bfseries}{\thesubsection}{.7em}{}
\titleformat{\subsubsection}{\normalsize\bfseries}{\thesubsubsection}{.7em}{}
\setcounter{tocdepth}{1}
\renewcommand{\contentsname}{차례}
\renewcommand{\refname}{참고문헌}
\hypersetup{pdftitle={BASS_CR: moving cutoff, thermal excess and collision-clock theory},
pdfauthor={BASS_CR research record},pdfsubject={CR-THEORY-THERMAL-EVOLUTION-20261012}}
\begin{document}
\begin{titlepage}
{\color{MidnightBlue}\large BASS\_CR 연구노트\par}
\vspace{16mm}
{\Huge\bfseries 시간 변화 배경에서의\\[3mm]전자 열화와 열적 진화\par}
\vspace{8mm}
{\Large 이동 cutoff · 비열적 초과에너지 · 충돌 시계\par}
\vspace{12mm}
{\large 다음 이론 연구 루프\par}
\vspace{4mm}
{2026년 10월 12일 (UTC)\par}
\vspace{12mm}
\begin{minipage}{.96\textwidth}
\large
고정 bath의 source 결속과 cutoff 편입 결과를 출발점으로,
입자수·에너지·비등방 압력 일을 함께 보존하는 방정식을 구성했다.
모든 자유전자를 세는 표현에는 비열적 초과에너지 상태를 도입했고,
충돌 시계와 실제 Coulomb 밀도 보정을 이용해 기존 응답을 재사용하는 조건을 유도했다.
그 잔차를 누적 열, 팽창 후 에너지, 온도 오차로 연결하는 증명을 함께 제시한다.
\end{minipage}
\vfill
\begin{tabular}{@{}ll@{}}
연구 단위 & CR-THEORY-THERMAL-EVOLUTION-20261012\\
방법 & 직접 유도 · source 코드 대응 · 독립 해석 검토\\
새 검산 & 유리수/수치 15개, 기호 대수 21개 통과\\
산출물 & 전체 증명, receiver 코드, DAG, 재현 자료\\
\end{tabular}
\end{titlepage}
\tableofcontents
\clearpage
"""
tail="\n\\end{document}\n"
(ROOT/"latex/report.tex").write_text(head+body+tail)
for i in range(2):
    run=subprocess.run(["xelatex","-interaction=nonstopmode","-halt-on-error","report.tex"],
                       cwd=ROOT/"latex",capture_output=True,text=True)
    (ROOT/f"latex/compile_{i+1}.stdout.txt").write_text(run.stdout)
    (ROOT/f"latex/compile_{i+1}.stderr.txt").write_text(run.stderr)
    if run.returncode:
        print(run.stdout[-6000:])
        raise SystemExit(run.returncode)
print(json.dumps({"pdf":str(ROOT/"latex/report.pdf"),
                  "bytes":(ROOT/"latex/report.pdf").stat().st_size}))

