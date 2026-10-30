#!/usr/bin/env python3
"""Scientific plot from original-source generated causal response table."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path(__file__).resolve().parent
rows=list(csv.DictReader((root/'results'/'TIME_CHEMISTRY_JACOBIAN.csv').open()))
fig,ax=plt.subplots(figsize=(8.8,5.2))
for policy in ('earliest','latest'):
 data=[r for r in rows if r['birth_policy']==policy]
 x=[float(r['observation_s'])/1e9 for r in data]
 for key,label in [('grad_HI_lnHI_m3','HI response to HI'),('grad_HeI_lnHeI_m3','HeI response to HeI'),('grad_HI_lnHeI_m3','HI response to HeI competition')]:
  y=[float(r[key])/1e-26 for r in data]
  ax.plot(x,y,marker='o',label=label+' ('+policy+')')
ax.set_xlabel('Observation proper time (10^9 s)')
ax.set_ylabel('Density susceptibility (10^-26 m^-3 per unit ln neutral density)')
ax.set_title('H/He RR first photoionization: source-locked density sensitivity')
ax.axhline(0,linewidth=0.5)
ax.legend(fontsize=8)
fig.tight_layout()
fig.savefig(root/'results'/'NEUTRAL_CAUSAL_SUSCEPTIBILITY.png',dpi=145)
print('wrote figure')
