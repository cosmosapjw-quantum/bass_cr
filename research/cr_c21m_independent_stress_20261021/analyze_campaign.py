"""Combine completed C21M run directories without replaying any ODE.

Repeated --run arguments may include the original 26 and future 98 refinement
cases. An optional fixed C21L center yields 27 or 125 unique physical targets.
The original pilot analyzer retains its strict 26+1 contract unchanged.
"""
from __future__ import annotations

import argparse
import csv
import itertools
import json
from pathlib import Path

import numpy as np

import analyze_pilot as pilot

HERE=Path(__file__).resolve().parent


def equal_grid_plots(output,rows):
    """Optional actual-cell maps for complete Cartesian equal-stress grids."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    axes=[sorted({r[key] for r in rows}) for key in ('S0','Pm0','Pr0')]
    table={(r['S0'],r['Pm0'],r['Pr0']):r for r in rows}
    if set(table)!=set(itertools.product(*axes)):
        raise ValueError('PLOT_REQUIRES_COMPLETE_CARTESIAN_GRID')
    if len(axes[0])>8:
        raise ValueError('PLOT_SUPPORTS_AT_MOST8_SHEAR_SLICES')
    for axis in axes[1:]:
        differences=np.diff(axis)
        if len(differences)>1 and not np.allclose(differences,differences[0],rtol=1e-12,atol=1e-15):
            raise ValueError('PLOT_REQUIRES_EQUAL_STRESS_SPACING')
    plt.rcParams.update({'font.size':10,'pdf.fonttype':42})
    fig,panels=plt.subplots(len(axes[0]),2,squeeze=False,figsize=(11,3.65*len(axes[0])+.5),constrained_layout=True)
    for column,channel in enumerate(('P_tot_signed_F_end','S_signed_F_end')):
        matrices=[np.array([[table[s,m,r][channel] for m in axes[1]] for r in axes[2]]) for s in axes[0]]
        limit=max(float(np.max(abs(matrix))) for matrix in matrices) or 1.
        for row,(s,matrix) in enumerate(zip(axes[0],matrices)):
            ax=panels[row,column]
            im=ax.imshow(matrix,origin='lower',cmap='RdBu_r',vmin=-limit,vmax=limit,aspect='equal')
            ax.set(xticks=range(len(axes[1])),xticklabels=[f'{v:g}' for v in axes[1]],
                   yticks=range(len(axes[2])),yticklabels=[f'{v:g}' for v in axes[2]],
                   xlabel=r'Initial signed $P_{m,0}$',ylabel=r'Initial signed $P_{r,0}$',
                   title=f'S0={s:g}; '+('final signed total stress' if column==0 else 'final signed shear'))
            ax.tick_params(axis='x',labelrotation=25)
            for y in range(len(axes[2])):
                for x in range(len(axes[1])):
                    ax.text(x,y,f'{matrix[y,x]:+.2e}',ha='center',va='center',fontsize=8,
                            color='white' if abs(matrix[y,x])>.65*limit else '#101010')
        fig.colorbar(im,ax=panels[:,column],shrink=.8,label=(r'$P_{\rm tot}(z=4)$' if column==0 else r'$S(z=4)$'))
    reused=sum(r['origin']=='REUSED_C21L_TRAJECTORY' for r in rows)
    fig.suptitle(f'C21M campaign: {len(rows)-reused} completed run cases + {reused} reused reference\nFull Frobenius signed coordinates; collisionless LRS, z20 to 4; actual cells only')
    fig.savefig(output/'campaign_endpoints.png',dpi=170)
    fig.savefig(output/'campaign_endpoints.pdf',metadata={'CreationDate':None,'ModDate':None})
    plt.close(fig)


def analyze(runs,output,reference=None,reference_root=pilot.C21L,make_plots=False):
    runs=[Path(path).resolve() for path in runs]
    output=Path(output).resolve()
    if len(runs)!=len(set(runs)):
        raise ValueError('DUPLICATE_RUN_DIRECTORY')
    if output.exists():
        raise FileExistsError('CREATE_ONLY_OUTPUT_EXISTS')
    entries=[];run_bindings=[];sources_identity=None
    for run in runs:
        envelope=json.loads((run/'MANIFEST.json').read_text())
        manifest_path,verified,new_entries=pilot.load_new(run,envelope['manifest']['grid'])
        manifest=verified['manifest']
        if sources_identity is None:
            sources_identity=manifest['source']
        elif manifest['source']!=sources_identity:
            raise ValueError('CAMPAIGN_PHYSICS_SOURCE_SETTINGS_OR_BUILDER_DIFFER')
        run_id=manifest['grid']['run_id']
        run_bindings.append({'run_id':run_id,'run_identity':verified['identity'],
                             'manifest_sha256':pilot.sha(manifest_path),
                             'observed_run_path':str(run),
                             'software':manifest['software'],'execution_site':manifest['execution_site'],
                             'case_count':len(new_entries)})
        entries.extend((*entry,run_id) for entry in new_entries)
    if not entries:
        raise ValueError('AT_LEAST_ONE_COMPLETE_C21M_RUN_REQUIRED')
    reference_binding=None
    if reference is not None:
        reference=Path(reference).resolve()
        reference_binding,entry=pilot.load_reference(reference,Path(reference_root).resolve())
        if (reference_binding['source_case_id']!='s04_p04'
                or reference_binding['source_input_identity']!='0090e1549b21b07e46001de2bf9cb2eab9bf0cba87ffe3d4d824ba117fecb44a'
                or reference_binding['upstream_source_commit']!=sources_identity['source_commit']):
            raise ValueError('ONLY_FIXED_C21L_CENTER_REFERENCE_IS_SUPPORTED')
        entries.append((*entry,'C21L_pilot81_reference'))
    entries.sort(key=lambda entry:tuple(entry[0][k] for k in ('S0','Pm0','Pr0')))
    coordinates=[]
    for case,*_ in entries:
        current=np.array([case[k] for k in ('S0','Pm0','Pr0')])
        if any(float(np.max(abs(current-old)))<=pilot.AXIS_ATOL for old in coordinates):
            raise ValueError('DUPLICATE_PHYSICAL_COORDINATE_WITHIN_2e-13:'+case['case_id'])
        coordinates.append(current)
    module=pilot.decomposition()
    derived=[];rows=[];checks=[];sources=[];before={}
    for case,path,receipt_path,receipt,origin,run_id in entries:
        before[path]=pilot.sha(path);before[receipt_path]=pilot.sha(receipt_path)
        with np.load(path,allow_pickle=False) as archive:
            h={key:archive[key] for key in archive.files}
        d=module.components(h)
        check=pilot.physics_checks(h,d,case)
        for key in ('Y','E_gamma','N_gamma','E_nu','N_nu'):
            d[key]=h[key]
        if derived and not np.array_equal(d['eta'],derived[0]['eta']):
            raise ValueError('CAMPAIGN_SAVED_TIME_GRID_DIFFERS')
        derived.append(d)
        row={**case,'origin':origin,'source_case_id':receipt.get('case_id',case['case_id'])}
        for key in ('S_signed_F','Sigma_F','P_m_signed_F','P_gamma_signed_F','P_nu_signed_F','P_r_signed_F','P_tot_signed_F','Pi_m_F','Pi_r_F','Pi_tot_F','cancellation'):
            row[key+'_initial']=pilot.finite_json(d[key][0]);row[key+'_end']=pilot.finite_json(d[key][-1])
        row.update(check)
        row['source_run_id']=run_id;row['source_identity']=receipt['identity']
        row['campaign_case_key']=run_id+'::'+case['case_id']
        rows.append(row)
        checks.append({'campaign_case_key':row['campaign_case_key'],**check})
        sources.append({'campaign_case_key':row['campaign_case_key'],'case_id':case['case_id'],
                        'origin':origin,'source_case_id':row['source_case_id'],'source_run_id':run_id,
                        'history_sha256':before[path],'receipt_sha256':before[receipt_path],
                        'source_identity':receipt['identity'],'source_state_shape':[40,101]})
    if len({r['campaign_case_key'] for r in rows})!=len(rows):
        raise ValueError('DUPLICATE_CAMPAIGN_CASE_KEY')
    arrays={key:np.stack([d[key] for d in derived]) for key in derived[0]}
    for key in ('case_id','origin','source_run_id','source_identity','campaign_case_key'):
        arrays[key]=np.array([r[key] for r in rows])
    arrays['requested_signed_full']=np.array(coordinates)
    if reference_binding is not None:
        row=next(r for r in rows if r['origin']=='REUSED_C21L_TRAJECTORY')
        for requested,actual in [('S0','S_signed_F'),('Pm0','P_m_signed_F'),('Pr0','P_r_signed_F')]:
            if row[actual+'_initial']!=reference_binding['actual_initial_signed_full_Frobenius'][requested]:
                raise ValueError('REFERENCE_ACTUAL_INITIAL_OFFSET_CHANGED')
    output.mkdir(parents=True,exist_ok=False)
    module.deterministic_npz(output/'components_campaign.npz',arrays)
    with (output/'endpoints_campaign.csv').open('x',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    axes={k:sorted({r[k] for r in rows}) for k in ('S0','Pm0','Pr0')}
    complete=len(rows)==np.prod([len(axis) for axis in axes.values()])
    summary={'status':'COMPLETE_SCOPED_PRELIMINARY','analysis_type':'READONLY_MULTIRUN_CAMPAIGN',
             'loaded_run_cases':sum(binding['case_count'] for binding in run_bindings),
             'reused_C21L_references':int(reference_binding is not None),'total_unique_cases':len(rows),
             'new_ODE_solves_by_analysis':0,'original_raw_writes':0,
             'duplicate_coordinate_axis_absolute_tolerance':pilot.AXIS_ATOL,
             'source_state_count':40,'saved_samples_per_case':101,'full_initial_axes':axes,
             'complete_Cartesian_grid':bool(complete),
             'endpoint_maxima':{key:float(np.max(arrays[key][:,-1])) for key in ('Sigma_F','Pi_m_F','Pi_r_F','Pi_tot_F')},
             'endpoint_signed_ranges':{key:[float(np.min(arrays[key][:,-1])),float(np.max(arrays[key][:,-1]))] for key in ('S_signed_F','P_m_signed_F','P_r_signed_F','P_tot_signed_F')},
             'all_saved_norm_maxima':{key:float(np.max(arrays[key])) for key in ('Sigma_F','Pi_m_F','Pi_r_F','Pi_tot_F')},
             'initial_axis_max_abs_error':max(c['initial_axis_max_abs_error'] for c in checks),
             'Hamiltonian_max_relative':max(c['Hamiltonian_max_relative'] for c in checks),
             'massive_comoving_number_max_relative':max(c['massive_comoving_number_max_relative'] for c in checks),
             'coordinate_definition':'Signed S=sqrt(6)*s/H and P_X=sqrt(6)*(8*pi*G/c^2)*pi_s,X/H^2, H in s^-1 and pi_s in J/m^3; norms are absolute values. Photons and massless neutrinos remain separate.',
             'actual_reference_initial_offsets':reference_binding['actual_initial_signed_full_Frobenius'] if reference_binding else None,
             'global_error_bound':None}
    pilot.write(output/'SUMMARY.json',summary)
    pilot.write(output/'INPUT_SOURCES.json',{'analyzer_sha256':pilot.sha(Path(__file__)),
                'pilot_analyzer_sha256':pilot.sha(HERE/'analyze_pilot.py'),
                'component_analyzer_sha256':pilot.sha(pilot.C21L/'component_split_20261021/analyze_components.py'),
                'runs':run_bindings,'source_identity':sources_identity,
                'reference_sha256':pilot.sha(reference) if reference else None,
                'source_trajectories':sources,'global_error_bound':None})
    pilot.write(output/'PHYSICS_CHECKS.json',{'status':'PASS_SCOPED','checks':checks,
                'scope':'Reuse pilot saved-trajectory checks; no new ODE, no convergence or error-bound claim.',
                'global_error_bound':None})
    if make_plots:
        equal_grid_plots(output,rows)
    if not all(pilot.sha(path)==digest for path,digest in before.items()):
        raise ValueError('ORIGINAL_INPUTS_CHANGED_DURING_ANALYSIS')
    pilot.write(output/'OUTPUT_MANIFEST.json',{'status':'PASS_SCOPED','original_inputs_unchanged':True,
                'raw_and_receipt_count_verified':len(before),'new_ODE_solves':0,
                'files':{p.name:{'sha256':pilot.sha(p),'size':p.stat().st_size} for p in sorted(output.iterdir())},
                'global_error_bound':None})
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,action='append',required=True,
                        help='Completed source-pinned run directory; repeat for multiple runs.')
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--reference',type=Path,help='Optional fixed REFERENCE_REUSE.json for the C21L center.')
    parser.add_argument('--reference-root',type=Path,default=pilot.C21L)
    parser.add_argument('--plots',action='store_true',help='Plot actual cells of a complete equal-stress Cartesian grid.')
    args=parser.parse_args()
    print(json.dumps(analyze(args.run,args.output,args.reference,args.reference_root,args.plots),indent=2))
