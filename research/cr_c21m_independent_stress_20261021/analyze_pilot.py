"""Read-only analysis of 26 new source-pinned histories plus one C21L reference.

The reference retains its actual tiny initial component offsets. All tensor
decomposition is reused from C21L; neither this module nor that module imports
a solver. Outputs are create-only and contain all 40 source states at 101 times.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path

os.environ.setdefault('MPLBACKEND','Agg')
import numpy as np

HERE=Path(__file__).resolve().parent
C21L=HERE.parent/'cr_c21l_rei_pilot_20261021'
SLICES=(-.012,0.,.012)
STRESSES=(-.0002,0.,.0002)
AXIS_ATOL=2e-13


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def write(path,value):
    with Path(path).open('x') as handle:
        json.dump(value,handle,indent=2,sort_keys=True,allow_nan=False)
        handle.write('\n')


def decomposition():
    spec=importlib.util.spec_from_file_location('c21l_readonly_components', C21L/'component_split_20261021/analyze_components.py')
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_new(run,grid):
    manifest_path=run/'MANIFEST.json'
    run_manifest=json.loads(manifest_path.read_text())
    identity=run_manifest['identity']
    manifest=run_manifest['manifest']
    if canonical_sha(manifest)!=identity or manifest['grid']!=grid:
        raise ValueError('RUN_MANIFEST_CONTENT_OR_GRID_MISMATCH')
    if manifest.get('operational_test_double') is not False:
        raise ValueError('SCIENCE_ANALYSIS_REQUIRES_REAL_SOURCE_EXECUTION')
    if manifest['source']['source_commit']!='3b85dedce84d37b3e165da00685a8a984950aafe':
        raise ValueError('UPSTREAM_PHYSICS_IDENTITY_MISMATCH')
    expected={'n':101,'rtol':3e-11,'atol':3e-13}
    if any(manifest['source']['settings'].get(k)!=v for k,v in expected.items()):
        raise ValueError('SOURCE_SOLVER_SETTINGS_MISMATCH')
    # Match the actual frozen execution code and all vendored source bytes.
    for name,digest in manifest['code_sha256'].items():
        if sha(HERE/name)!=digest:
            raise ValueError('EXECUTION_CODE_CHANGED:'+name)
    for item in manifest['source']['source_files']:
        if sha(C21L/'vendor/rei'/item['path'])!=item['sha256']:
            raise ValueError('VENDORED_SOURCE_CHANGED:'+item['path'])
    for name,key in [('adapter.py','parent_adapter_sha256'),('SOURCE_MANIFEST.json','source_manifest_sha256')]:
        if sha(C21L/name)!=manifest['source'][key]:
            raise ValueError('PARENT_SOURCE_CHANGED:'+name)
    entries=[]
    for case in grid['cases']:
        folder=run/'cases'/case['case_id']
        receipt_path=folder/'RESULT.json'
        raw_path=folder/'history.npz'
        receipt=json.loads(receipt_path.read_text())
        seal=json.loads((folder/'COMPLETE.json').read_text())
        reservation=json.loads((folder/'RESERVATION.json').read_text())
        if (receipt.get('identity')!=identity or receipt.get('case')!=case
                or receipt.get('status')!='COMPLETE' or receipt.get('operational_test_double') is not False
                or seal.get('identity')!=identity or seal.get('case_id')!=case['case_id']
                or reservation.get('identity')!=identity or reservation.get('case')!=case
                or sha(raw_path)!=seal['history_sha256']
                or receipt['history_sha256']!=seal['history_sha256']
                or sha(receipt_path)!=seal['result_sha256']):
            raise ValueError('CASE_RAW_RECEIPT_OR_SEAL_MISMATCH:'+case['case_id'])
        entries.append((case,raw_path,receipt_path,receipt,'NEW_C21M_EXECUTION'))
    return manifest_path,run_manifest,entries


def load_reference(reference_path,reference_root):
    reference=json.loads(reference_path.read_text())
    paths={key:reference_root/relative for key,relative in reference['source_paths_relative_to_C21L'].items()}
    for key,path in paths.items():
        if sha(path)!=reference['source_sha256'][key]:
            raise ValueError('REUSED_REFERENCE_CHANGED:'+key)
    old=json.loads(paths['manifest'].read_text())
    receipt=json.loads(paths['receipt'].read_text())
    if (canonical_sha(old['manifest'])!=reference['source_input_identity']
            or old['identity']!=reference['source_input_identity']
            or receipt['identity']!=old['identity'] or receipt['history_sha256']!=reference['source_sha256']['raw']
            or receipt['case_id']!=reference['source_case_id'] or receipt['status']!='COMPLETE'):
        raise ValueError('REUSED_REFERENCE_IDENTITY_MISMATCH')
    case={'case_id':reference['case_id'],**reference['requested_display_coordinates']}
    return reference,(case,paths['raw'],paths['receipt'],receipt,'REUSED_C21L_TRAJECTORY')


def finite_json(value):
    return None if not np.isfinite(value) else float(value)


def physics_checks(h,d,case):
    if h['Y'].shape!=(40,101) or h['Y'].dtype!=np.float64 or not np.isfinite(h['Y']).all():
        raise ValueError('FULL40_FP64_101_STATE_REQUIRED:'+case['case_id'])
    if (len(d['eta'])!=101 or abs(d['a'][0]-1/21)>2e-15 or abs(d['a'][-1]-.2)>2e-15
            or not np.all(np.diff(d['eta'])>0)):
        raise ValueError('REDSHIFT_RANGE_OR_SAMPLING:'+case['case_id'])
    if not all(k in h for k in ('Einstein_H2','massive_physical_number_norm','massive_min_cell_population','N_gamma','N_nu','E_gamma','E_nu')):
        raise ValueError('MISSING_PHYSICS_DIAGNOSTIC')
    norms=h['massive_physical_number_norm']*np.exp(3*h['eta'])
    checks={
        'Hamiltonian_max_relative':float(np.max(abs(h['Einstein_H2']/h['H']**2-1))),
        'massive_comoving_number_max_relative':float(np.max(abs(norms/norms[0]-1))),
        'radiation_number_max_abs':max(float(np.max(abs(h[k][:,0]-1))) for k in ('N_gamma','N_nu')),
        'minimum_massive_cell_population':float(np.min(h['massive_min_cell_population'])),
        'minimum_radiation_monopole':min(float(np.min(h[k][:,0])) for k in ('E_gamma','E_nu')),
        'initial_axis_max_abs_error':max(abs(float(d[key][0])-case[target]) for target,key in
                                      (('S0','S_signed_F'),('Pm0','P_m_signed_F'),('Pr0','P_r_signed_F'))),
        'signed_component_addition_max_abs':float(np.max(abs(d['P_tot_signed_F']-d['P_m_signed_F']-d['P_r_signed_F']))),
        'tensor_norm_formula_max_abs':max(float(np.max(abs(np.sqrt(np.sum(d['pi_tensor_diag_'+x+'_J_m3']**2,axis=1))-d['pi_norm_F_'+x+'_J_m3']))) for x in ('m','gamma','nu','r','tot'))}
    if (checks['Hamiltonian_max_relative']>2e-13 or checks['massive_comoving_number_max_relative']>2e-13
            or checks['radiation_number_max_abs']>2e-10 or checks['minimum_massive_cell_population']<0
            or checks['minimum_radiation_monopole']<=0 or checks['initial_axis_max_abs_error']>AXIS_ATOL
            or checks['signed_component_addition_max_abs']>2e-15):
        raise ValueError('SCOPED_PHYSICS_GATE_FAILED:'+case['case_id']+':'+repr(checks))
    for x in ('m','gamma','nu','r','tot'):
        if not np.allclose(d['Pi_'+x+'_F'],math.sqrt(2)*d['Pi_'+x+'_half'],rtol=5e-16,atol=1e-30):
            raise ValueError('NORM_CONVENTION_MISMATCH')
    c=d['cancellation'][d['cancellation_defined']]
    if np.any(c < -5e-15) or np.any(c > 1+5e-15):
        raise ValueError('CANCELLATION_OUTSIDE_ROUNDOFF_DOMAIN')
    return checks


def plots(out,rows,arrays):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size':10,'axes.titlesize':11,'pdf.fonttype':42})
    lookup={(r['S0'],r['Pm0'],r['Pr0']):i for i,r in enumerate(rows)}
    # Each square is one sampled initial condition; there is no interpolation.
    matrices=[[],[]]
    for s in SLICES:
        baseline=rows[lookup[s,0.,0.]]['S_signed_F_end']
        matrices[0].append(np.array([[rows[lookup[s,m,r]]['P_tot_signed_F_end'] for m in STRESSES] for r in STRESSES])*1e5)
        matrices[1].append(np.array([[rows[lookup[s,m,r]]['S_signed_F_end']-baseline for m in STRESSES] for r in STRESSES])*1e5)
    fig,axs=plt.subplots(3,2,figsize=(10.5,11.0),constrained_layout=True)
    for j in range(2):
        limit=max(float(np.max(abs(m))) for m in matrices[j]) or 1.
        for i,s in enumerate(SLICES):
            ax=axs[i,j]; matrix=matrices[j][i]
            im=ax.imshow(matrix,origin='lower',cmap='RdBu_r',vmin=-limit,vmax=limit,aspect='equal')
            ax.set(xticks=[0,1,2],xticklabels=['-2','0','2'],yticks=[0,1,2],yticklabels=['-2','0','2'],
                   xlabel=r'Initial signed $P_{m,0}$ ($10^{-4}$)',ylabel=r'Initial signed $P_{r,0}$ ($10^{-4}$)',
                   title=f'S0={s:g}; '+('final signed total stress' if j==0 else 'final signed shear response'))
            for y in range(3):
                for x in range(3):
                    ax.text(x,y,f'{matrix[y,x]:+.3f}',ha='center',va='center',fontsize=10,
                            color='white' if abs(matrix[y,x])>.65*limit else '#101010')
            if s==0:
                ax.plot(1,1,'s',ms=42,mfc='none',mec='#cc9900',mew=2)
        label=(r'$P_{\rm tot}(z=4)$ ($10^{-5}$)' if j==0 else r'$S(z=4)-S_{\rm same\ S_0,\,P_{m,0}=P_{r,0}=0}(z=4)$ ($10^{-5}$)')
        fig.colorbar(im,ax=axs[:,j],shrink=.84,label=label)
    fig.suptitle('C21M: 26 new + 1 reused trajectory; collisionless LRS, z=20 to 4\nSigned full-Frobenius coordinates; gold square = reused C21L reference',fontsize=12)
    fig.savefig(out/'initial_stress_slices.png',dpi=180)
    fig.savefig(out/'initial_stress_slices.pdf',metadata={'CreationDate':None,'ModDate':None})
    plt.close(fig)
    fig,axs=plt.subplots(2,3,figsize=(14.3,7.4),constrained_layout=True)
    for row,sign in enumerate((1,-1)):
        index=lookup[0.,sign*.0002,-sign*.0002]
        z=1/arrays['a'][index]-1
        for x,color,style in (('m','#ad3278','-'),('r','#1684ad','-'),('tot','#171717','--')):
            axs[row,0].plot(z,arrays['P_'+x+'_signed_F'][index]*1e4,color=color,ls=style,lw=1.8,label={'m':r'$P_m$','r':r'$P_r=P_\gamma+P_\nu$','tot':r'$P_{\rm tot}$'}[x])
        axs[row,0].legend(loc='best',fontsize=9)
        axs[row,0].set(ylabel=r'Signed stress ($10^{-4}$)',title=f'Initial Pm={sign*.0002:+g}, Pr={-sign*.0002:+g}')
        axs[row,1].plot(z,arrays['S_signed_F'][index]*1e5,color='#8c4d11',lw=1.8)
        axs[row,1].set(ylabel=r'Signed $S=\sqrt{6}\,s/H$ ($10^{-5}$)',title='Shear generated from initial S0=0')
        axs[row,2].plot(z,arrays['cancellation'][index],color='#3b7b4a',lw=1.8)
        axs[row,2].set(ylabel=r'$1-|\pi_{s,m}+\pi_{s,r}|/(|\pi_{s,m}|+|\pi_{s,r}|)$',ylim=(-.025,1.025),title='Cancellation; undefined points remain gaps')
        for ax in axs[row,:]:
            ax.axhline(0,color='.65',lw=.6)
            ax.set(xlim=(20,4),xlabel='Redshift z')
            ax.grid(alpha=.15)
    fig.suptitle('C21M 26 new + 1 reused pilot: two new opposing-stress histories\nNorms are absolute values of signed coordinates; initial cancellation does not constrain later cancellation',fontsize=12)
    fig.savefig(out/'opposing_stress_histories.png',dpi=180)
    fig.savefig(out/'opposing_stress_histories.pdf',metadata={'CreationDate':None,'ModDate':None})
    plt.close(fig)


def analyze(run,output,grid_path,reference_path,reference_root,make_plots=True):
    run,output=Path(run).resolve(),Path(output).resolve()
    grid=json.loads(grid_path.read_text())
    if grid.get('schema')!='C21M_GRID_V1' or len(grid['cases'])!=26:
        raise ValueError('EXPLICIT26_GRID_REQUIRED')
    manifest_path,manifest,entries=load_new(run,grid)
    if manifest['manifest']['grid_file_sha256']!=sha(grid_path):
        raise ValueError('GRID_FILE_BYTES_CHANGED')
    reference,entry=load_reference(reference_path,reference_root)
    entries.append(entry)
    entries.sort(key=lambda e:(e[0]['S0'],e[0]['Pm0'],e[0]['Pr0']))
    if {(e[0]['S0'],e[0]['Pm0'],e[0]['Pr0']) for e in entries}!={(s,m,r) for s in SLICES for m in STRESSES for r in STRESSES}:
        raise ValueError('COMPLETE27_PHYSICAL_GRID_MISMATCH')
    module=decomposition()
    rows,derived,sources,checks=[],[],[],[]
    raw_before={}
    for case,path,receipt_path,receipt,origin in entries:
        raw_before[path]=sha(path); raw_before[receipt_path]=sha(receipt_path)
        with np.load(path,allow_pickle=False) as archive:
            h={k:archive[k] for k in archive.files}
        d=module.components(h)
        check=physics_checks(h,d,case)
        checks.append({'case_id':case['case_id'],**check})
        for key in ('Y','E_gamma','N_gamma','E_nu','N_nu'):
            d[key]=h[key]
        if derived and not np.array_equal(d['eta'],derived[0]['eta']):
            raise ValueError('SOURCE_SAVED_TIME_GRID_NOT_IDENTICAL')
        derived.append(d)
        row={**case,'origin':origin,'source_case_id':receipt.get('case_id',case['case_id'])}
        for key in ('S_signed_F','Sigma_F','P_m_signed_F','P_gamma_signed_F','P_nu_signed_F','P_r_signed_F','P_tot_signed_F','Pi_m_F','Pi_r_F','Pi_tot_F','cancellation'):
            row[key+'_initial']=finite_json(d[key][0]); row[key+'_end']=finite_json(d[key][-1])
        row.update(check)
        rows.append(row)
        sources.append({'case_id':case['case_id'],'origin':origin,'source_case_id':row['source_case_id'],
                        'history_sha256':sha(path),'receipt_sha256':sha(receipt_path),
                        'source_identity':receipt['identity'],'source_state_shape':[40,101]})
    for target,key in [('S0','S_signed_F'),('Pm0','P_m_signed_F'),('Pr0','P_r_signed_F')]:
        actual=rows[13][key+'_initial']
        if actual!=reference['actual_initial_signed_full_Frobenius'][target]:
            raise ValueError('REFERENCE_OFFSET_CHANGED')
    arrays={k:np.stack([d[k] for d in derived]) for k in derived[0]}
    arrays['case_id']=np.array([r['case_id'] for r in rows])
    arrays['origin']=np.array([r['origin'] for r in rows])
    arrays['requested_signed_full']=np.array([[r[k] for k in ('S0','Pm0','Pr0')] for r in rows])
    output.mkdir(parents=True,exist_ok=False)
    module.deterministic_npz(output/'components27.npz',arrays)
    with (output/'endpoints27.csv').open('x',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    write(output/'INPUT_SOURCES.json',{'run_manifest_sha256':sha(manifest_path),'run_identity':manifest['identity'],
          'grid_sha256':sha(grid_path),'reference_reuse_sha256':sha(reference_path),
          'analyzer_sha256':sha(Path(__file__)),'component_analyzer_sha256':sha(C21L/'component_split_20261021/analyze_components.py'),
          'source_trajectories':sources,'original_raw_writes':0,'global_error_bound':None})
    write(output/'PHYSICS_CHECKS.json',{'status':'PASS_SCOPED','scope':'Saved full40/101 FP64 trajectories: component tensor identities, declared initial-axis residuals, number conservation, Hamiltonian, positive populations. No error bound or convergence campaign.',
          'checks':checks,'global_error_bound':None})
    summary={'status':'COMPLETE_SCOPED_PRELIMINARY','new_executed_cases':26,'reused_cases':1,'plotted_cases':27,
             'new_ODE_solves_by_analysis':0,'source_state_count':40,'saved_samples_per_case':101,
             'full_initial_axes':{'S0':list(SLICES),'Pm0':list(STRESSES),'Pr0':list(STRESSES)},
             'species':{'matter':'massive kinetic sector plus isotropic dust','radiation':'photons plus massless neutrinos','UV':'ABSENT_FROM_MODEL'},
             'coordinate_definition':'Signed S=sqrt(6)*s/H and P_X=sqrt(6)*(8*pi*G/c^2)*pi_s,X/H^2; norm is absolute value; H in s^-1, pi_s in J/m^3.',
             'reference_actual_offsets':reference['actual_initial_signed_full_Frobenius'],
             'endpoint_maxima':{k:float(np.max(arrays[k][:,-1])) for k in ('Sigma_F','Pi_m_F','Pi_r_F','Pi_tot_F')},
             'endpoint_signed_ranges':{k:[float(np.min(arrays[k][:,-1])),float(np.max(arrays[k][:,-1]))] for k in ('S_signed_F','P_m_signed_F','P_r_signed_F','P_tot_signed_F')},
             'all_saved_norm_maxima':{k:float(np.max(arrays[k])) for k in ('Sigma_F','Pi_m_F','Pi_r_F','Pi_tot_F')},
             'initial_axis_max_abs_error':max(c['initial_axis_max_abs_error'] for c in checks),
             'Hamiltonian_max_relative':max(c['Hamiltonian_max_relative'] for c in checks),
             'number_max_relative':max(c['massive_comoving_number_max_relative'] for c in checks),
             'run_identity':manifest['identity'],'global_error_bound':None}
    write(output/'SUMMARY.json',summary)
    if make_plots:
        plots(output,rows,arrays)
    unchanged=all(sha(path)==digest for path,digest in raw_before.items())
    if not unchanged:
        raise ValueError('INPUT_BYTES_CHANGED_DURING_ANALYSIS')
    write(output/'OUTPUT_MANIFEST.json',{'schema':'C21M_ANALYSIS_V1','status':'PASS_SCOPED',
          'original_inputs_unchanged':True,'raw_and_receipt_count_verified':len(raw_before),
          'files':{p.name:{'sha256':sha(p),'size':p.stat().st_size} for p in sorted(output.iterdir()) if p.is_file()},
          'global_error_bound':None})
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--grid',type=Path,default=HERE/'grid_pilot26.json')
    parser.add_argument('--reference',type=Path,default=HERE/'REFERENCE_REUSE.json')
    parser.add_argument('--reference-root',type=Path,default=C21L)
    parser.add_argument('--no-plots',action='store_true')
    args=parser.parse_args()
    print(json.dumps(analyze(args.run,args.output,args.grid,args.reference,args.reference_root,not args.no_plots),indent=2))
