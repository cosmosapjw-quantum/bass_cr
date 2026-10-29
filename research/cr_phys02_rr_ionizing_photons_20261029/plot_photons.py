"""Plot only source-qualified retained RR photon data, not propagated/observed radiation."""
from pathlib import Path
import json
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

root=Path(__file__).parent/'results'
data=json.loads((root/'PHOTON_RESULT.json').read_text())
with (root/'PHOTON_SPECTRUM.csv').open() as f:
    rows=list(csv.DictReader(f))

fig,ax=plt.subplots(1,2,figsize=(11,4.6),layout='constrained')
for ch in ('H','He'):
    r=[x for x in rows if x['channel']==ch]
    xx=np.array([float(x['E_low_eV']) for x in r if int(x['time_bin'])==4])+.25
    yy=np.array([sum(float(x['N_ph_m3']) for x in r if float(x['E_low_eV'])==E) for E in np.array([float(x['E_low_eV']) for x in r if int(x['time_bin'])==4])])
    ax[0].step(xx, np.maximum(yy,1e-100),where='mid',label=ch)
ax[0].set_yscale('log');ax[0].set_ylim(1e-36,1e-24)
ax[0].set_xlim(12.5,36)
ax[0].set_xlabel('Retained photon energy [eV]')
ax[0].set_ylabel('Emitted photon count per 0.5 eV bin [m$^{-3}$]')
ax[0].set_title('Final proper-time quarter (7.5–10 Gs)')
ax[0].axvline(13.60,ls=':',alpha=.65,label='H I threshold')
ax[0].axvline(24.59,ls='--',alpha=.65,label='He I threshold')
ax[0].legend(fontsize=8)

bins=np.arange(1,5)
H=np.array([d['N_ph_m3'] for d in data['photon_rows'] if d['channel']=='H'])
He=np.array([d['N_ph_m3'] for d in data['photon_rows'] if d['channel']=='He'])
ax[1].bar(bins,H,label='H II to H I ground')
ax[1].bar(bins,He,bottom=H,label='He II to He I ground')
ax[1].set_xlabel('Disjoint proper-time quarter, each 2.5 Gs')
ax[1].set_ylabel('Emitted photon count density [m$^{-3}$]')
ax[1].set_xticks(bins)
ax[1].ticklabel_format(axis='y',style='sci',scilimits=(0,0))
ax[1].set_title('Finite-time source returns, not absorbed photons')
ax[1].legend(fontsize=8)
fig.suptitle('BASS-CR / source-locked PHYS02 finite H-He ground-RR photon product',fontsize=12)
fig.savefig(root/'RR_PHOTON_SOURCE.png',dpi=175)
fig.savefig(root/'RR_PHOTON_SOURCE.svg')
plt.close(fig)
print(root/'RR_PHOTON_SOURCE.png')
