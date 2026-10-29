import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path(__file__).resolve().parent
rows=list(csv.DictReader((root/'results'/'TIME_TOTAL.csv').open()))
t=[float(x['T_s'])/1e9 for x in rows]
for lo,hi,scale,ylabel,filename in [
 ('absorbed_lo_m3','absorbed_hi_m3',1e27,r'Cumulative first absorptions ($10^{-27}\,m^{-3}$)','PHOTON_ABSORPTION_TIME.png'),
 ('electron_excess_lo_J_m3','electron_excess_hi_J_m3',1e45,r'Primary photoelectron kinetic energy ($10^{-45}\,J\,m^{-3}$)','ELECTRON_KINETIC_TIME.png')]:
 yl=[float(x[lo])*scale for x in rows];yh=[float(x[hi])*scale for x in rows]
 fig,ax=plt.subplots(figsize=(7,4.2));ax.plot(t,yl,label='Sharp lower');ax.plot(t,yh,label='Sharp upper');ax.fill_between(t,yl,yh,alpha=0.2)
 ax.set_xlabel('Observation proper time (Gs)');ax.set_ylabel(ylabel)
 ax.set_title('Source-locked 100 K H/He RR first absorption: conditional')
 ax.legend();fig.tight_layout();fig.savefig(root/'results'/filename,dpi=150);plt.close(fig)
