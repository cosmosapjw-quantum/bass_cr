#!/usr/bin/env python3
"""Render only the already-written diagnostic CSV; no model imports."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','BLIS_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):
    os.environ[key]='1'
os.sched_setaffinity(0,{4})
from pathlib import Path
import csv,json,hashlib,time
base=Path(__file__).resolve().parent
out=base/'c22e_line_admission_20261022_v1'
os.environ['MPLCONFIGDIR']=str(base/'private_plot_cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
rows=list(csv.DictReader((out/'LINE_ADMISSION.csv').open()))
lrs=[r for r in rows if r['tier']=='nominal' and r['case']=='ci_lrs' and r['mesh']=='accepted']
flrw=[r for r in rows if r['tier']=='nominal' and r['case']=='ci_flrw' and r['mesh']=='accepted']
x=[float(r['eta']) for r in lrs]
low=[float(r['H_gamma_min_over_H']) for r in lrs]
high=[float(r['H_gamma_max_over_H']) for r in lrs]
fig,ax=plt.subplots(1,2,figsize=(10,4.1),layout='constrained')
fig.suptitle('C22E line-admission diagnostic: stored C22D states',fontsize=13)
ax[0].fill_between(x,low,high,color='#377eb8',alpha=.18,label='LRS: exact angular range at each sample')
ax[0].plot(x,low,color='#246b9c',lw=1.4,label=r'$(H-s)/H$')
ax[0].plot(x,high,color='#d95f02',lw=1.4,label=r'$(H+2s)/H$')
ax[0].axhline(1,color='#555555',ls='--',lw=1,label='FLRW: 1 at float64 resolution')
ax[0].set(xlim=(0,max(x)),ylim=(.84,1.29),xlabel=r'$\eta=\ln(a/a_{\rm ref})$',ylabel=r'$H_\gamma/H$',title='Every sampled direction has positive redshift rate')
ax[0].legend(fontsize=7,loc='upper right',framealpha=.95)
ax[1].plot(x,[float(r['three_abs_s_over_H']) for r in lrs],color='#6a3d9a',lw=1.6,label='LRS CI on')
ax[1].plot([float(r['eta']) for r in flrw],[float(r['three_abs_s_over_H']) for r in flrw],color='#1b9e77',lw=1.1,label='FLRW numerical residual')
ax[1].set(xlim=(0,max(x)),ylim=(-.012,.395),xlabel=r'$\eta=\ln(a/a_{\rm ref})$',ylabel=r'$3|s|/H$',title='Directional expansion spread')
ax[1].text(.05,.77,'LRS maximum: 0.367423\nLRS final: 0.0191455\nFLRW maximum: 1.42e-20',transform=ax[1].transAxes,fontsize=9,bbox=dict(facecolor='white',edgecolor='#cccccc',alpha=.95))
ax[1].legend(fontsize=8,loc='upper right')
for a in ax:
    a.grid(alpha=.22)
fig.supxlabel('Finite time samples; geometry, atomic line data, and residence/destruction inputs remain open.',fontsize=9)
for suffix in ('png','pdf'):
    path=out/('DIRECTIONAL_EXPANSION.'+suffix)
    if path.exists(): raise FileExistsError(path)
    fig.savefig(path,dpi=160)
plt.close(fig)
receipt={'status':'RENDERED_PENDING_VISUAL_INSPECTION','source_csv_sha256':hashlib.sha256((out/'LINE_ADMISSION.csv').read_bytes()).hexdigest(),
         'no_new_ODE':True,'no_new_RHS_or_rates':True,'scope':'render already-produced algebra diagnostics only'}
with (out/'FIGURE_RENDER_RECEIPT.json').open('x') as f: json.dump(receipt,f,indent=2)
print(json.dumps(receipt))
