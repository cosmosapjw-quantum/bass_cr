"""Build this report from recorded results and the proved closed forms.

No research solver, old suite, kernel generator or physical ODE is executed.
Requirements: matplotlib/numpy, pandoc, XeLaTeX and the bundled licensed fonts.
"""
from pathlib import Path
from fractions import Fraction as Q
import json,re,subprocess
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
for name in ('latex','figures'):(ROOT/name).mkdir(exist_ok=True)
read=lambda name:json.loads((ROOT/name).read_text())
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.bbox':'tight','pdf.fonttype':42})
r=read('results/REACTION_BRANCH_CHECKS.json')
qb=lambda x:float(Q(x['exact']))
kb=float(Q('1.380649e-23'));ev=float(Q('1.602176634e-19'));cv=1.5*kb;chi=4
g=qb(r['ghost_fraction']);u0=qb(r['background_construction']['U_th']);w0=qb(r['first_node_J']);wc=qb(r['lower_cutoff_J'])
slow=float(r['source_event']['raw_daughters_eV'][0])*ev
extent=np.linspace(0,.5,501)
t0=(u0+g*wc*extent)/(cv*(10+g*extent))
t1=(u0+slow*extent)/(cv*(10+extent))
sdown=qb(r['lower_branch_reentry_extent']);star=qb(r['crossing_extent']);threshold=w0/(chi*kb)
fig,ax=plt.subplots(figsize=(8.5,3.9),layout='constrained')
ax.axvspan(sdown,star,color='#dce9ed',alpha=.7,label='Both branches consistent')
ax.plot(extent,t0,color='#74929d',lw=1.4,ls='--',label=r'Prefix $k=0$')
ax.plot(extent,t1,color='#b78656',lw=1.4,ls='--',label=r'Prefix $k=1$')
left=extent<star;right=extent>=star
ax.plot(extent[left],t0[left],color='#126d82',lw=2.8)
ax.plot(extent[right],t1[right],color='#126d82',lw=2.8,label='Inherited-branch selection')
before=qb(r['rows'][2]['zero_branch']['temperature']);after=qb(r['rows'][2]['selected']['temperature'])
ax.plot([star,star],[before,after],color='#126d82',lw=2)
ax.scatter([star],[before],facecolor='white',edgecolor='#126d82',zorder=5)
ax.scatter([star],[after],color='#126d82',zorder=5)
ax.axhline(threshold,color='#5a6368',lw=.8,ls=':')
ax.annotate(r'$s_*=1/4$'+'\n'+f'{before:.3f} to {after:.3f} K',(star,after),xytext=(.275,after-1.2),fontsize=9)
ax.set(xlabel='Ionization extent s (events)',ylabel='Temperature (K)',xlim=(0,.5),title='A reaction-created atom crosses the thermal cutoff')
ax.grid(alpha=.14);ax.legend(frameon=False,ncol=2,fontsize=8,loc='upper left')
fig.savefig(ROOT/'figures/reaction_branch.pdf');fig.savefig(ROOT/'figures/reaction_branch.png',dpi=180);plt.close(fig)
np.savetxt(ROOT/'figures/reaction_branch_curves.csv',np.column_stack([extent,t0,t1]),delimiter=',',header='extent,T_prefix0_K,T_prefix1_K',comments='')
geo=read('results/GEOMETRY_REBIND_CHECKS.json')['geometry']
energies=[geo['expanded_energy_eV']['float'],geo['supplied_initial_energy_eV']['float'],geo['moved_energy_eV']['float']]
labels=['Isotropic expansion (a_i x 2)','Initial saved-grid parent','Anisotropic map (2, 1, 2/3)']
fig,ax=plt.subplots(figsize=(8.5,3.6),layout='constrained')
colors=['#4b9f9e','#7e939d','#c57c3c']
ax.barh(np.arange(3),energies,color=colors,height=.53)
for i,w in enumerate(energies):ax.text(w+.45,i,f'{w:.6f} eV',va='center',fontsize=9)
ax.axvline(13.6057,color='#3c6479',ls='--',lw=1.2,label='HI threshold')
ax.axvline(24.587,color='#8f5b47',ls=':',lw=1.5,label='HeI threshold')
ax.set(yticks=np.arange(3),yticklabels=labels,xlabel='Kinetic energy (eV)',xlim=(0,45.5),title='Prescribed massive transport changes the event domain')
ax.legend(frameon=False,loc='lower right',fontsize=8);ax.grid(axis='x',alpha=.14)
fig.savefig(ROOT/'figures/geometry_energy.pdf');fig.savefig(ROOT/'figures/geometry_energy.png',dpi=180);plt.close(fig)
(ROOT/'figures/geometry_energy_values.csv').write_text('case,kinetic_energy_eV\n'+'\n'.join(f'{i},{w:.17g}' for i,w in enumerate(energies))+'\n')

report=(ROOT/'REPORT_KO.md').read_text().replace('<!-- REVIEW_STATUS -->',read('RESULTS.json')['decision'])
names=['COUPLED_BRANCH_KO.md','REACTION_BRANCH_KO.md','COVARIANT_GEOMETRY_KO.md','GEOMETRY_REBIND_KO.md']
chapters=[(ROOT/'derivations'/name).read_text() for name in names]
report=report.replace('<!-- DERIVATIONS -->','\n\n'+'\n\n\\clearpage\n\n'.join(chapters))
literature=(ROOT/'derivations/LITERATURE_KO.md').read_text()
literature=re.sub(r'\A# [^\n]+\n','',literature,count=1)
report=report.replace('<!-- LITERATURE -->','\n\\begingroup\n\\small\n'+literature+'\n\\endgroup\n')
report=re.sub(r'(?m)^(#{2,6})\s+\d+(?:\.\d+)*\.?\s+',r'\1 ',report)
report=re.sub(r'`([^`\n]{28,})`',lambda m:r'\nolinkurl{'+m.group(1)+'}' if m.group(1).isascii() and not any(x in m.group(1) for x in '{}') else m.group(0),report)
(ROOT/'latex/manuscript.md').write_text(report)
subprocess.run(['pandoc',str(ROOT/'latex/manuscript.md'),'-f','markdown+tex_math_single_backslash+tex_math_dollars+raw_tex','-t','latex','--wrap=none','--no-highlight','-o',str(ROOT/'latex/body.tex')],check=True)
body=(ROOT/'latex/body.tex').read_text()
body=re.sub(r'\\includegraphics\{([^}]+)\}',r'\\includegraphics[width=\\linewidth]{\1}',body)
head=r'''\documentclass[11pt,a4paper]{article}
\usepackage[margin=23mm,headheight=15pt,footskip=12mm]{geometry}
\usepackage{fontspec}
\IfFileExists{fonts/NotoSansCJKkr-Regular.otf}{
\setmainfont{NotoSansCJKkr-Regular.otf}[Path=fonts/,BoldFont=NotoSansCJKkr-Bold.otf,ItalicFont=NotoSansCJKkr-Regular.otf,ItalicFeatures={FakeSlant=0.12}]
\setmonofont{DejaVuSansMono.ttf}[Path=fonts/,Scale=0.74]
}{\setmainfont{Noto Sans CJK KR}\setmonofont{DejaVu Sans Mono}[Scale=0.74]}
\XeTeXlinebreaklocale "ko"
\XeTeXlinebreakskip=0pt plus 0.1em
\usepackage{amsmath,amssymb,mathtools,mathrsfs,graphicx,booktabs,longtable,array}
\usepackage[table,dvipsnames]{xcolor}
\usepackage{enumitem,fancyhdr,titlesec}
\usepackage[unicode,colorlinks=true,linkcolor=MidnightBlue,urlcolor=MidnightBlue,citecolor=MidnightBlue]{hyperref}
\usepackage{xurl,microtype}
\providecommand{\tightlist}{\setlength{\itemsep}{2pt}\setlength{\parskip}{0pt}}
\providecommand{\pandocbounded}[1]{#1}
\setlength{\parindent}{0pt}\setlength{\parskip}{5pt}
\setlength{\emergencystretch}{3em}
\setlength{\LTpre}{6pt}\setlength{\LTpost}{8pt}
\setlist{leftmargin=1.6em,itemsep=2pt,topsep=4pt}
\renewcommand{\arraystretch}{1.13}\linespread{1.08}
\pagestyle{fancy}\fancyhf{}
\fancyhead[L]{\small BASS\_CR · 반응 branch와 Bianchi geometry}
\fancyhead[R]{\small 이론 연구 루프}\fancyfoot[C]{\thepage}
\titleformat{\section}{\Large\bfseries\color{MidnightBlue}}{\thesection}{.7em}{}
\titleformat{\subsection}{\large\bfseries}{\thesubsection}{.7em}{}
\titleformat{\subsubsection}{\normalsize\bfseries}{\thesubsubsection}{.7em}{}
\setcounter{tocdepth}{1}\renewcommand{\contentsname}{차례}
\hypersetup{pdftitle={BASS_CR: coupled atomic branches and massive Bianchi geometry},pdfauthor={BASS_CR research record},pdfsubject={CR-THEORY-BRANCH-GEOMETRY-20261013}}
\begin{document}
\begin{titlepage}
{\color{MidnightBlue}\large BASS\_CR 연구노트\par}
\vspace{15mm}
{\Huge\bfseries 실제 반응 branch와\\[3mm]Bianchi geometry의 결합\par}
\vspace{8mm}
{\Large 자기일관 endpoint · 생성 원자의 cutoff 교차\\[2mm]질량 있는 에너지 이동과 kernel 재결속\par}
\vspace{12mm}
{\large 다음 이론 연구 루프\par}
\vspace{4mm}{2026년 10월 13일 (KST)\par}
\vspace{12mm}
\begin{minipage}{.96\textwidth}\large
실제 원자 kernel의 반응률을 넣은 유한 endpoint를 구성하고,
반응이 생성한 원자가 열적 경계를 넘는 선택 규칙을 증명했다.
지정된 Bianchi I의 massive momentum 이동 뒤 kernel을 다시
결속하며, 보존 장부와 명시적인 표현 오차를 함께 제시한다.
\end{minipage}
\vfill
\begin{tabular}{@{}ll@{}}
연구 단위 & CR-THEORY-BRANCH-GEOMETRY-20261013\\
도구 & SciSpace · Exa · Wolfram Language · 실제 xAct\\
검산 & 새 tensor 8개 · scalar 24개 · 부등식 4개\\
내용 & 전체 유도 · 실제 사례 · 구현 · 오차 · DAG\\
기준 & 직전 KC1–KC7의 채택 source와 근거 재사용\\
\end{tabular}
\end{titlepage}
\tableofcontents\clearpage
'''
(ROOT/'latex/report.tex').write_text(head+body+'\n\\end{document}\n')
for i in range(2):
    run=subprocess.run(['xelatex','-interaction=nonstopmode','-halt-on-error','report.tex'],cwd=ROOT/'latex',capture_output=True,text=True)
    (ROOT/f'latex/compile_{i+1}.stdout.txt').write_text(run.stdout)
    (ROOT/f'latex/compile_{i+1}.stderr.txt').write_text(run.stderr)
    if run.returncode:print(run.stdout[-7000:]);raise SystemExit(run.returncode)
print(json.dumps({'pdf':str(ROOT/'latex/report.pdf'),'bytes':(ROOT/'latex/report.pdf').stat().st_size}))
