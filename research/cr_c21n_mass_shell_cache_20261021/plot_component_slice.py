"""Read-only component plot of the accepted S0=0 slice, no ODE or interpolation."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/c21n_mplconfig')
os.environ.setdefault('MPLBACKEND','Agg')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

HERE=Path(__file__).resolve().parent
DEFAULT=HERE.parent/'cr_c21m_independent_stress_20261021/analysis_campaign125_20261021/components_campaign.npz'


def main():
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,default=DEFAULT)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise FileExistsError('CREATE_ONLY_COMPONENT_PLOT')
    with np.load(a.input,allow_pickle=False) as archive:
        data={key:archive[key] for key in archive.files}
    requested=data['requested_signed_full']
    chosen=np.flatnonzero(requested[:,0]==0.)
    if len(chosen)!=25:raise ValueError('EXPECTED_EXISTING_25_ZERO_SHEAR_SLICE')
    coords=np.array([-2.,-1.,0.,1.,2.])*1e-4
    rows=[];indices=np.full((5,5),-1,dtype=int)
    for i in chosen:
        col=np.flatnonzero(coords==requested[i,1]);row=np.flatnonzero(coords==requested[i,2])
        if len(col)!=1 or len(row)!=1:raise ValueError('OFF_AXIS_ACCEPTED_INPUT')
        if indices[row[0],col[0]]!=-1:raise ValueError('DUPLICATE_CELL')
        indices[row[0],col[0]]=i
        rows.append({'case_key':str(data['campaign_case_key'][i]),'Pm0':requested[i,1],'Pr0':requested[i,2],
            **{key:float(data[key][i,-1]) for key in ('S_signed_F','Sigma_F','P_m_signed_F','Pi_m_F',
                'P_r_signed_F','Pi_r_F','P_tot_signed_F','Pi_tot_F','cancellation')},
            'cancellation_defined':bool(data['cancellation_defined'][i,-1]),
            'isotropic_reference_FP_cell':bool(np.all(requested[i]==0.))})
    if np.any(indices<0):raise ValueError('MISSING_CELL')
    for signed,norm in [('S_signed_F','Sigma_F'),('P_m_signed_F','Pi_m_F'),
                        ('P_r_signed_F','Pi_r_F'),('P_tot_signed_F','Pi_tot_F')]:
        if not np.array_equal(np.abs(data[signed][chosen,-1]),data[norm][chosen,-1]):
            raise ValueError('SIGNED_NORM_MISMATCH:'+norm)
    a.output.mkdir(parents=True,exist_ok=False)
    with (a.output/'endpoints_S0_zero.csv').open('x',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    panels=[('S_signed_F',r'Signed $S_f$',True),('P_m_signed_F',r'Signed $P_{m,f}$',True),
            ('P_r_signed_F',r'Signed $P_{r,f}$',True),('P_tot_signed_F',r'Signed $P_{\mathrm{tot},f}$',True),
            ('Pi_tot_F',r'Norm $\Pi_{\mathrm{tot},f}=|P_{\mathrm{tot},f}|$',False),
            ('cancellation',r'$C_f=1-|P_m+P_r|/(|P_m|+|P_r|)$',False)]
    plt.rcParams.update({'font.size':10,'pdf.fonttype':42})
    fig,axes=plt.subplots(2,3,figsize=(13.2,8.2),constrained_layout=True)
    for ax,(key,title,signed) in zip(axes.flat,panels):
        values=np.array(data[key][indices,-1],copy=True)
        if key=='cancellation':
            # Preserve the raw values in CSV; do not infer physical cancellation
            # from the isotropic reference's tiny FP residual stresses.
            masked=np.ma.array(values,mask=~data['cancellation_defined'][indices,-1])
            masked.mask[2,2]=True
            im=ax.imshow(masked,origin='lower',vmin=0,vmax=1,cmap='viridis',interpolation='nearest')
            ax.add_patch(Rectangle((1.5,1.5),1,1,fill=False,hatch='///',edgecolor='gray',lw=.5))
        else:
            limit=float(np.max(np.abs(values)))
            im=ax.imshow(values,origin='lower',vmin=-limit if signed else 0,vmax=limit,
                         cmap='RdBu_r' if signed else 'magma',interpolation='nearest')
        for row in range(5):
            for col in range(5):
                value=values[row,col]
                text='FP' if key=='cancellation' and row==col==2 else (
                    f'{value:.2f}' if key=='cancellation' else f'{value:+.1e}' if signed else f'{value:.1e}')
                rgba=im.cmap(im.norm(value));lum=.2126*rgba[0]+.7152*rgba[1]+.0722*rgba[2]
                color='black' if lum>.55 or text=='FP' else 'white'
                ax.text(col,row,text,ha='center',va='center',fontsize=7.8,color=color)
        ax.set(xticks=range(5),yticks=range(5),xticklabels=['-2','-1','0','1','2'],
               yticklabels=['-2','-1','0','1','2'],xlabel=r'$P_{m,0}$ ($10^{-4}$)',
               ylabel=r'$P_{r,0}$ ($10^{-4}$)',title=title)
        fig.colorbar(im,ax=ax,shrink=.85,pad=.02)
    fig.suptitle('Existing C21M125: 25 actual cells at initial signed S = 0; endpoints at z = 4\n'
                 'Full Frobenius convention; photon + massless neutrino radiation; no interpolation or new ODE\n'
                 'FP = isotropic reference: raw tiny stresses retained, cancellation inference omitted',fontsize=12)
    fig.savefig(a.output/'component_slice_S0_zero.png',dpi=180)
    fig.savefig(a.output/'component_slice_S0_zero.pdf',metadata={'CreationDate':None,'ModDate':None})
    plt.close(fig)
    receipt={'schema':'C21N_COMPONENT_SLICE_V1','status':'GENERATED_PENDING_VISUAL_REVIEW',
             'input_path':str(a.input.resolve()),'input_sha256':hashlib.sha256(a.input.read_bytes()).hexdigest(),
             'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             'cases':25,'signed_norm_exact_array_equality':True,'new_ODE_integrations':0,
             'interpolation':False,'original_data_modified':False,
             'FP_center_cancellation':'retained in CSV; hatched and omitted for physical inference in plot',
             'global_error_bound':None,'files':[{'path':x.name,'size':x.stat().st_size,
                'sha256':hashlib.sha256(x.read_bytes()).hexdigest()} for x in sorted(a.output.iterdir())]}
    with (a.output/'RECEIPT.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
    print(json.dumps({'cases':25,'new_ODE_integrations':0,'output':str(a.output)}))


if __name__=='__main__':main()
