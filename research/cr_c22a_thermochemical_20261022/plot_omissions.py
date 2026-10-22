#!/usr/bin/env python3
"""Plot saved omission diagnostics; no ODE or rate reevaluation."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import argparse
import hashlib
import io
import json
from pathlib import Path
import numpy as np
from analyze import plt, axes_time_redshift, SECONDS_PER_MYR, savefig

def read_arrays(path):
    raw=Path(path).read_bytes()
    with np.load(io.BytesIO(raw),allow_pickle=False) as data:
        arrays={key:data[key] for key in data.files}
    return arrays,{'path':str(path),'size_bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--history',type=Path,required=True)
    parser.add_argument('--diagnostics',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    h,hbind=read_arrays(args.history);d,dbind=read_arrays(args.diagnostics)
    if not np.array_equal(h['eta'],d['eta']):
        raise ValueError('HISTORY_DIAGNOSTIC_GRID_MISMATCH')
    args.out.mkdir(parents=True,exist_ok=False)
    t=h['proper_elapsed_s']/SECONDS_PER_MYR
    fig,axes=plt.subplots(1,2,figsize=(13,5.6),constrained_layout=True)
    axes[0].plot(t,h['temperature_K'],color='#b84325',label='Evolved gas: omitted terms OFF')
    axes[0].plot(t,d['CMB_temperature_diagnostic_K'],color='#456b96',ls='--',label='Assumed isotropic CMB bath')
    axes[0].set_yscale('log');axes[0].set_ylabel('Temperature [K]')
    axes[0].set_title('Trajectory used for the diagnostic')
    axes[0].legend(loc='lower left',fontsize=9)
    compton=-d['isotropic_CMB_Compton_over_H_Uthermal']
    if np.any(compton<=0):
        raise ValueError('PLOT_LABEL_REQUIRES_COMPTON_COOLING_ON_THIS_TRAJECTORY')
    axes[1].plot(t,compton,color='#b84325',lw=1.6,label='Compton cooling (omitted)')
    axes[1].plot(t,d['H_collisional_excitation_over_H_Uthermal'],color='#8d5aa7',lw=1.4,label='H excitation (omitted; valid T only)')
    rr=d['included_RR_cooling_eV_per_Href_s']/(h['H']*h['thermal_energy_eV_per_H'])
    axes[1].plot(t,rr,color='#286b65',ls='--',label='RR kinetic cooling (included)')
    axes[1].axhline(1,color='.4',lw=.8,ls=':',label=r'$|Q|=H u_{\rm th}$')
    axes[1].set_yscale('log');axes[1].set_ylabel(r'Cooling rate / $(H u_{\rm th})$')
    axes[1].set_title('Omitted cooling can exceed expansion scale')
    axes[1].legend(loc='lower left',fontsize=8.5)
    for ax in axes: axes_time_redshift(ax,h)
    fig.suptitle('LRS omission diagnostics on the computed trajectory\n'
                 'No thermal feedback from these omitted rates; H CI unavailable on this temperature range',fontsize=12)
    savefig(fig,args.out,'LRS_OMITTED_COOLING')
    receipt={'schema':'C22A_OMISSION_PLOT_V1','source_arrays':[hbind,dbind],
             'points':len(t),'data_policy':'NaN gaps retained; no clipping or extrapolated rates',
             'Compton_assumption':'isotropic blackbody bath; all sampled gas exchange is cooling here',
             'interpretation':'saved-trajectory diagnostic; not a self-consistent corrected solution',
             'new_ODE_runs':0,'global_error_bound':None}
    (args.out/'PLOT_BINDING.json').write_text(json.dumps(receipt,indent=2)+'\n')

if __name__=='__main__':main()
