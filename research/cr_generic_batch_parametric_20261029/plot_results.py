from pathlib import Path
import matplotlib.pyplot as plt
from fractions import Fraction as F
import json
p=Path(__file__).parent
# Source-independent exact synthetic 10-atom frontier
pts=[(0,5),(F(3,2),F(13,2)),(F(5,2),7),(4,F(15,2))]
fig,ax=plt.subplots(figsize=(6.8,4.1))
ax.plot([float(q) for q,m in pts],[float(m) for q,m in pts], marker='o', label=r'$M(c)$ exact')
for j,(x,y) in enumerate(pts[:-1]):
 nx,ny=pts[j+1];ax.text((float(x)+float(nx))/2,(float(y)+float(ny))/2+0.07,rf'$1/{j+1}$',ha='center',fontsize=10)
ax.set_xlabel(r'cross-bin budget $c$ (synthetic event-mass units)');ax.set_ylabel(r'maximum HL mass $M(c)$')
ax.set_title('Exact piecewise-linear 10-atom frontier');ax.grid(alpha=.24);fig.tight_layout();fig.savefig(p/'FRONTIER_EXACT.png',dpi=170);plt.close(fig)
r=json.loads((p/'BENCHMARK_MATCHED_SYNTHETIC.json').read_text())
fig,ax=plt.subplots(figsize=(6.8,4.1))
b=[x['batch_s'] for x in r['measurements']];s=[x['repeated_s'] for x in r['measurements']]
ax.plot(range(1,len(b)+1),b,'o-',label='one batch')
ax.plot(range(1,len(s)+1),s,'s-',label='repeated PR122')
ax.set_xlabel('run number');ax.set_ylabel('end-to-end wall time (s)');ax.set_title('Matched 120-atom, 8-budget exact certificate comparison');ax.set_xticks(range(1,len(b)+1));ax.legend();ax.grid(alpha=.24)
fig.tight_layout();fig.savefig(p/'BENCHMARK_MATCHED.png',dpi=170);plt.close(fig)
print('Saved plots')
