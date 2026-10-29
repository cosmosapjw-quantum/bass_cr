"""Independent plot inputs from exact 10-atom fixture; no physical source inference."""
from fractions import Fraction as F
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from native_budget import Atom
from potentials_bridge import run_exact
r=[('h0','19/2','1/2',1),('h1','7','2',0),('h2','9','2',1),('h3','13/2','5/2',2),('h4','6','1/2',1),('l0','0','1',0),('l1','7/2','1',1),('l2','3/2','5/2',2),('l3','0','5/2',0),('l4','3/2','1/2',2)]
a=tuple(Atom.parse(*v) for v in r)
cs=[F(i,20) for i in range(0,101)]
# No need for 101 C++ subprocesses; exact source-verified piecewise values:
def exact_curve(c):
 if c<=F(3,2):return 5+c
 if c<=F(5,2):return F(13,2)+(c-F(3,2))/2
 if c<=4:return 7+(c-F(5,2))/3
 return F(15,2)
# Reproducible independent backend controls at the exact breakpoints.
for c in [F(0),F(3,2),F(5,2),F(4)]:
 assert run_exact(a,F(10),c)['M']==exact_curve(c)
ms=[float(exact_curve(c)) for c in cs]
fig,ax=plt.subplots(figsize=(7.0,4.2))
ax.plot(list(map(float,cs)),ms,linewidth=2,label=r'Exact $M(c)$, 10-atom conditional graph')
for c,m,txt in [(0,5,'0'),(F(3,2),F(13,2),'1'),(F(5,2),7,'1/2'),(4,F(15,2),'1/3')]:
 ax.plot([float(c)],[float(m)],'o')
 ax.annotate(f'({c}, {m})',(float(c),float(m)),xytext=(5,10),textcoords='offset points',fontsize=8)
ax.set_xlabel(r'cross-bin budget $c$ (conditional event-mass units)')
ax.set_ylabel(r'maximum high-low mass $M(c)$')
ax.set_title('Exact multi-kink frontier: slopes 1, 1/2, 1/3, then 0')
ax.set_xlim(-0.12,5.15);ax.set_ylim(4.75,7.85);ax.grid(alpha=.2)
fig.tight_layout()
p=Path(__file__).with_name('GENERIC_POTENTIALS_FRONTIER.png');fig.savefig(p,dpi=170)
print(p)
