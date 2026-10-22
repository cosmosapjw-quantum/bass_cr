#!/usr/bin/env python3
"""C22B saved/accepted-array audit and matched C22A reuse. ODE0.

The immutable parent reader checks exact raw bytes, inputs and source identity.
Accepted-state summaries evaluate algebraic observables only. All output is
create-only. Finite mesh checks and one tighter solver comparison are scoped
evidence, not a global numerical or physical error bound.
"""
from __future__ import annotations
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','BLIS_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):
    os.environ[key]='1'
os.environ.setdefault('MPLCONFIGDIR','/tmp/c22b_matplotlib')
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from model import ThermochemicalFactory

HERE=Path(__file__).resolve().parent
A=HERE.parent/'cr_c22a_thermochemical_20261022'
spec=importlib.util.spec_from_file_location('c22b_reused_parent_reader', A/'analyze.py')
reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
sha256=reader.sha256
json_create=reader.json_create
MATCH={'dark_compton':'dark_expansion','finite_uv_compton_flrw':'finite_uv_flrw','finite_uv_compton_lrs':'finite_uv_lrs'}
MYR=365.25*86400*1e6
KEYS=('temperature_K','n_e_cm3','tau_T','H1_ionized_fraction','Sigma_F','Pi_r_F','bath_energy_received_eV_per_H')
LEDGERS=('energy_relative_residual','nucleus_max_relative_residual','charge_photon_relative_residual','photon_number_relative_residual')


def verify_registered_role(run, contract, role):
    registered=contract['new_cosmological_runs'][role]
    expected_cases=registered['cases'] if role=='nominal' else [registered['case']]
    inputs=run['input']
    for key in ('method','rtol','atol'):
        if inputs[key]!=registered[key]:raise ValueError('REGISTERED_'+role.upper()+'_'+key.upper()+'_MISMATCH')
    if inputs['cases']!=expected_cases:raise ValueError('REGISTERED_'+role.upper()+'_CASE_LIST_MISMATCH')
    if inputs['saved_times']!=contract['new_cosmological_runs']['saved_times']:raise ValueError('REGISTERED_SAVED_COUNT_MISMATCH')
    if set(run['rows'])!={x['name'] for x in expected_cases}:raise ValueError('REGISTERED_COMPLETED_CASE_SET_MISMATCH')
    if any(len(row['history']['eta'])!=inputs['saved_times'] for row in run['rows'].values()):raise ValueError('ACTUAL_SAVED_COUNT_MISMATCH')


def mesh_audit(h, model, gates):
    values={k:float(np.max(np.abs(h[k]))) for k in LEDGERS}
    values.update(minimum_scaled_population=float(np.min(h['atomic_scaled'])),
        minimum_UV_count_per_H=float(np.min(h['UV_photons_per_H'])),
        minimum_temperature_K=float(np.min(h['temperature_K'])),
        maximum_temperature_K=float(np.max(h['temperature_K'])),
        maximum_Compton_nonrelativistic_parameter=float(np.max(h['Compton_nonrelativistic_parameter'])),
        n_T_exact_zero=bool(np.all(h['Y'][model.invariant_indices]==0)),
        signed_radiation_sum_max_difference=float(np.max(abs(h['signed_Pi_r_F']-(h['signed_Pi_gamma_F']+h['signed_Pi_nu_F'])))),
        radiation_norm_max_difference=float(np.max(abs(h['Pi_r_F']-abs(h['signed_Pi_r_F'])))),
        total_norm_max_difference=float(np.max(abs(h['Pi_tot_F']-abs(h['signed_Pi_m_F']+h['signed_Pi_r_F'])))))
    checks={
        'energy':values['energy_relative_residual']<=gates['energy_relative_saved_and_accepted_max_abs'],
        'nuclei':values['nucleus_max_relative_residual']<=gates['nucleus_max_relative_residual'],
        'charge':values['charge_photon_relative_residual']<=gates['charge_and_photon_absolute_normalized'],
        'photon_number':values['photon_number_relative_residual']<=gates['charge_and_photon_absolute_normalized'],
        'population':values['minimum_scaled_population']>=gates['minimum_scaled_population'],
        'UV_population':values['minimum_UV_count_per_H']>=gates['minimum_UV_count_per_H'],
        'positive_T':values['minimum_temperature_K']>0,
        'declared_n_T':values['n_T_exact_zero'],
        'nonrelativistic':values['maximum_Compton_nonrelativistic_parameter']<=gates['nonrelativistic_selector_max'],
        'signed_radiation_sum':values['signed_radiation_sum_max_difference']<=1e-15,
        'radiation_norm':values['radiation_norm_max_difference']<=1e-15,
        'total_norm':values['total_norm_max_difference']<=1e-15,
    }
    return {'mesh_points':len(h['eta']),'measurements':values,'checks':checks,
            'status':'PASS_SCOPED' if all(checks.values()) else 'FAIL_PRESERVED',
            'scope':'saved or solver-returned accepted mesh only; no continuous-extremum bound'}


def axis(ax, x_label='Elapsed proper time from z=20 [Myr]'):
    ax.set_xscale('symlog',linthresh=1e-5,linscale=.6)
    ax.set_xlabel(x_label+'\nsymlog; linear below 10 years')
    ax.grid(alpha=.22)


def savefig(fig, output, stem):
    fig.savefig(output/(stem+'.png'),dpi=170,bbox_inches='tight',facecolor='white')
    fig.savefig(output/(stem+'.pdf'),bbox_inches='tight',facecolor='white',
                metadata={'Title':'C22B prescribed CMB bath scoped pilot','CreationDate':None,'ModDate':None})
    plt.close(fig)


def comparison_figure(name,h,a,output):
    tb=h['proper_elapsed_s']/MYR;ta=a['proper_elapsed_s']/MYR
    fig,axes=plt.subplots(2,3,figsize=(15.5,8.7),constrained_layout=True)
    titles=['Gas temperature','Free electrons','Cumulative Thomson depth','H1 ionized fraction']
    labels=['Temperature [K]',r'Electron density [cm$^{-3}$]',r'$\tau_T$',r'$N_{H1^+}/N_{H1}$']
    for ax,key,title,label in zip(axes.flat,KEYS[:4],titles,labels):
        ax.plot(ta,a[key],color='.45',ls='--',lw=1.5,label='C22A stored baseline')
        ax.plot(tb,h[key],color='#007c91',lw=1.5,label='C22B coupled gas')
        if key=='temperature_K':
            ax.plot(tb,h['prescribed_CMB_temperature_K'],color='#b96628',ls=':',label='Prescribed CMB bath')
        if np.all(h[key]>0) and np.all(a[key]>0):ax.set_yscale('log')
        ax.set_title(title);ax.set_ylabel(label);ax.legend(fontsize=8)
    ax=axes[1,1]
    for key,label in [('temperature_K','T'),('n_e_cm3','n_e'),('tau_T','tau_T')]:
        valid=a[key]!=0
        change=np.full(a[key].shape,np.nan);change[valid]=(h[key][valid]/a[key][valid]-1)*100
        ax.plot(tb,change,label=label)
    ax.axhline(0,color='.4',lw=.7);ax.set_ylabel('Matched-eta change from C22A [%]')
    ax.set_title('Conditional effect of active Compton exchange');ax.legend()
    ax=axes[1,2]
    ax.plot(tb,h['bath_energy_received_eV_per_H'],color='#8d4ca5')
    ax.axhline(0,color='.4',lw=.7);ax.set_ylabel('Signed cumulative bath receipt [eV/Href]')
    ax.set_title('Positive: gas exports energy to thermostat')
    for ax in axes.flat:axis(ax);ax.set_xlim(0,max(ta[-1],tb[-1]))
    fig.suptitle(name+'\nPrescribed isotropic CMB thermostat + finite initial UV + photo / Case-A RR; full closure OPEN',fontsize=13)
    savefig(fig,output,'COMPARISON_'+name)


def ledger_figure(h,ha,output):
    t=h['proper_elapsed_s']/MYR;ta=ha['proper_elapsed_s']/MYR
    fig,axes=plt.subplots(2,2,figsize=(14,9),constrained_layout=True)
    ax=axes[0,0]
    for key,label in [('thermal_energy_eV_per_H','thermal'),('ionization_energy_eV_per_H','ionization'),
        ('UV_energy_eV_per_H','finite UV'),('escaped_energy_eV_per_H','cumulative RR export'),
        ('gas_work_eV_per_H','gas expansion work'),('UV_work_eV_per_H','UV redshift work'),
        ('bath_energy_received_eV_per_H','signed bath receipt')]:ax.plot(t,h[key],label=label,lw=1.2)
    ax.set_ylabel('Energy accounting [eV/Href]');ax.set_title('Resident energy and accumulated transfers');ax.legend(ncol=2,fontsize=8)
    ax=axes[0,1]
    ratio=ha['Compton_gas_per_eta']/ha['thermal_energy_eV_per_H']
    ax.plot(ta,ratio,color='#b04e30');ax.axhline(0,color='.4',lw=.7)
    ax.set_ylabel(r'$Q_C/(H U_{thermal}^{volume})$');ax.set_title('Signed active gas heating rate / expansion scale')
    ax.set_yscale('symlog',linthresh=1e-3)
    ax=axes[1,0]
    ax.plot(ta,ha['energy_relative_residual'],color='#72539c',label='Accepted mesh',lw=1)
    ax.plot(t,h['energy_relative_residual'],'.',ms=3,color='#e09822',label='201 saved times')
    ax.axhline(0,color='.4',lw=.7);ax.axhline(1e-8,color='.5',ls='--',lw=.7);ax.axhline(-1e-8,color='.5',ls='--',lw=.7)
    ax.set_yscale('symlog',linthresh=1e-13);ax.set_ylabel('Signed relative energy residual');ax.set_title('Preregistered acceptance: absolute residual <= 1e-8');ax.legend(fontsize=8)
    ax=axes[1,1]
    for key,label in [('signed_Pi_gamma_F','P_gamma'),('signed_Pi_nu_F','P_nu'),('signed_Pi_r_F','P_r=P_gamma+P_nu'),('signed_Pi_m_F','P_m (Vlasov)'),('signed_Pi_tot_F','P_tot=P_m+P_r')]:ax.plot(t,h[key],label=label,lw=1.2)
    ax.set_yscale('symlog',linthresh=1e-9);ax.axhline(0,color='.4',lw=.7)
    ax.set_ylabel('Signed full-Frobenius amplitudes');ax.set_title('Signed addition precedes scalar norm');ax.legend(fontsize=8)
    for ax in axes.flat:axis(ax);ax.set_xlim(0,t[-1])
    fig.suptitle('LRS C22B energy and stress accounting\nBath receipt is a cumulative external transfer; no extra resident CMB or Einstein source',fontsize=13)
    savefig(fig,output,'LRS_ENERGY_AND_STRESS')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--nominal',type=Path,required=True);p.add_argument('--reference',type=Path,required=True)
    p.add_argument('--baseline',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    args=p.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    contract=json.loads((HERE/'CONTRACT.json').read_text());gates=contract['preregistered_gates']
    nominal=reader.read_run(args.nominal);reference=reader.read_run(args.reference);baseline=reader.read_run(args.baseline)
    frozen=json.loads((HERE/'evidence/SOURCE_FREEZE.json').read_text())
    if nominal['source']!=frozen or reference['source']!=frozen:raise ValueError('SOURCE_IDENTITY_MISMATCH')
    for row in frozen['files']:
        path=HERE.parent.parent/row['path']
        if path.stat().st_size!=row['size_bytes'] or sha256(path)!=row['sha256']:raise ValueError('CURRENT_FROZEN_SOURCE_DRIFT:'+row['path'])
    verify_registered_role(nominal,contract,'nominal');verify_registered_role(reference,contract,'reference')
    if baseline['source']['identity_sha256']!=contract['parent_C22A_source_identity']:raise ValueError('BASELINE_IDENTITY_MISMATCH')
    factories={};report={};accepted={};endpoints=[];baseline_comparison={}
    for role,run in [('nominal',nominal),('reference',reference)]:
        for name,row in run['rows'].items():
            ell=row['case'].get('ellmax',8)
            if ell not in factories:factories[ell]=ThermochemicalFactory(ellmax=ell)
            m=factories[ell].build(row['case']);h=row['history']
            ha=m.summarize(h['accepted_eta'],h['accepted_Y']);accepted[(role,name)]=ha
            with (out/(role+'_'+name+'_ACCEPTED.npz')).open('xb') as f:np.savez_compressed(f,**ha)
            checks={'saved':mesh_audit(h,m,gates),'accepted':mesh_audit(ha,m,gates)}
            report[role+':'+name]={'raw_history_sha256':row['history_sha256'],'source_identity':frozen['identity_sha256'],
                'meshes':checks,'status':'PASS_SCOPED' if all(v['status']=='PASS_SCOPED' for v in checks.values()) else 'FAIL_PRESERVED'}
            endpoint={'role':role,'name':name,'z':float(h['z'][-1]),'elapsed_Myr':float(h['proper_elapsed_s'][-1]/MYR)}
            endpoint.update({k:float(h[k][-1]) for k in KEYS});endpoints.append(endpoint)
            if role=='nominal':
                old=baseline['rows'][MATCH[name]];a=old['history']
                if not np.array_equal(h['eta'],a['eta']):raise ValueError('BASELINE_ETA_GRID_MISMATCH')
                if any(row['case'][k]!=old['case'][k] for k in ('signed_sigma','signed_pi_m','signed_pi_r','photon_scale','temperature_K')):
                    raise ValueError('MATCHED_BASELINE_PHYSICAL_INPUT_MISMATCH')
                measures={}
                for key in KEYS[:-1]:
                    valid=a[key]!=0;relative=np.full(a[key].shape,np.nan)
                    relative[valid]=h[key][valid]/a[key][valid]-1
                    measures[key]={'old_endpoint':float(a[key][-1]),'new_endpoint':float(h[key][-1]),
                        'endpoint_relative_change':float(relative[-1]) if valid[-1] else None,
                        'max_absolute_matched_eta_change':float(np.max(abs(h[key]-a[key]))),
                        'max_absolute_relative_change_on_nonzero_baseline':float(np.nanmax(abs(relative))) if valid.any() else None,
                        'zero_baseline_samples':int((~valid).sum())}
                baseline_comparison[name]={'old_name':MATCH[name],'old_history_sha256':old['history_sha256'],
                    'new_history_sha256':row['history_sha256'],'measurements':measures,'old_ODE_reruns':0}
                comparison_figure(name,h,a,out)
    ref={};all_ref=True
    fig,ax=plt.subplots(figsize=(11.5,5.7),constrained_layout=True)
    for name,row in reference['rows'].items():
        n=nominal['rows'][name];r=row
        if n['case']!=r['case'] or not np.array_equal(n['history']['eta'],r['history']['eta']):raise ValueError('REFERENCE_INPUT_OR_GRID_MISMATCH')
        vals={}
        for key in gates['reference_fields']:
            nn=n['history'][key];rr=r['history'][key];peak=float(np.max(abs(rr)))
            scale=np.full_like(rr,max(peak,1e-30)) if key=='bath_energy_received_eV_per_H' else np.maximum(abs(rr),max(1e-8*peak,1e-30))
            error=abs(nn-rr)/scale;maximum=float(np.max(error));passed=maximum<=gates['reference_scaled_max_difference'];all_ref &= passed
            vals[key]={'max_scaled_difference':maximum,'max_absolute_difference':float(np.max(abs(nn-rr))),
                       'reference_peak_scale':peak,'pass':bool(passed)}
            ax.plot(n['history']['proper_elapsed_s']/MYR,error,label=key,lw=1.2)
        ref[name]=vals
    ax.axhline(gates['reference_scaled_max_difference'],color='black',ls='--',label='Preregistered gate: 2e-7')
    ax.set_yscale('symlog',linthresh=1e-14);axis(ax);ax.set_ylabel('Absolute difference / registered field scale')
    ax.set_xlim(0,max(n['history']['proper_elapsed_s'][-1],r['history']['proper_elapsed_s'][-1])/MYR)
    ax.set_title('Same-input BDF versus tighter Radau: LRS saved grid only');ax.legend(fontsize=8,ncol=2)
    savefig(fig,out,'LRS_TIGHTER_REFERENCE')
    ledger_figure(nominal['rows']['finite_uv_compton_lrs']['history'],accepted[('nominal','finite_uv_compton_lrs')],out)
    with (out/'ENDPOINTS.csv').open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(endpoints[0]));w.writeheader();w.writerows(endpoints)
    scalars=(*KEYS,*LEDGERS,'thermal_energy_eV_per_H','Compton_gas_rate_eV_per_H_s','Compton_gas_per_eta','prescribed_CMB_temperature_K')
    with (out/'HISTORY.csv').open('x',newline='') as f:
        w=csv.writer(f);w.writerow(['role','name','eta','z','elapsed_Myr',*scalars])
        for role,run in [('nominal',nominal),('reference',reference)]:
            for name,row in run['rows'].items():
                h=row['history']
                for i in range(len(h['eta'])):w.writerow([role,name,h['eta'][i],h['z'][i],h['proper_elapsed_s'][i]/MYR,*[h[k][i] for k in scalars]])
    summary={'schema':'C22B_SAVED_ACCEPTED_ANALYSIS_V1','created_utc':datetime.now(timezone.utc).isoformat(),
        'status':'PASS_SCOPED' if all(x['status']=='PASS_SCOPED' for x in report.values()) and all_ref else 'FAIL_PRESERVED',
        'source_identity_sha256':frozen['identity_sha256'],'analyzer_sha256':sha256(__file__),
        'parent_reader_sha256':sha256(A/'analyze.py'),'contract_sha256':sha256(HERE/'CONTRACT.json'),
        'provenance_gates':{'current_frozen_files_checked':len(frozen['files']),'registered_nominal_method_tolerance_cases_saved_count':'PASS','registered_reference_method_tolerance_cases_saved_count':'PASS'},
        'runs':{role:{'path':run['path'],'input_sha256':run['runtime']['input_sha256'],'source_identity_sha256':run['source']['identity_sha256']} for role,run in [('nominal',nominal),('reference',reference),('baseline',baseline)]},
        'mesh_acceptance':report,'endpoints':endpoints,'matched_baseline_comparison':baseline_comparison,
        'tighter_reference':ref,'preregistered_gates':gates,'new_ODE_in_analysis':0,'old_ODE_reruns':0,
        'CSV_history_rows':sum(len(row['history']['eta']) for run in (nominal,reference) for row in run['rows'].values()),
        'plot_contract':{'x':'elapsed proper time, symlog linear below10years; each solution uses own stored proper time','baseline_comparison':'matched identical eta grid','zero_and_negative_values':'retained; no clipping or absolute-value replacement','residual_axis':'signed energy residual; zero retained','redshift_secondary_axis':'NONE'},
        'limitations':['prescribed isotropic external CMB thermostat','finite selected saved and accepted mesh; no global bound','one LRS tighter solver reference','atomic omitted processes remain OPEN','no inherited CMB spectral energy backreaction'],
        'global_error_bound':None}
    json_create(out/'SUMMARY.json',summary)
    artifacts=[{'name':p.name,'size_bytes':p.stat().st_size,'sha256':sha256(p)} for p in sorted(out.iterdir()) if p.is_file()]
    json_create(out/'ARTIFACTS.json',{'files':artifacts,'ODE_calls':0,'global_error_bound':None})
    print(json.dumps({'status':summary['status'],'analysis':str(out),'cases':len(report),'CSV_rows':summary['CSV_history_rows'],'new_ODE':0}))


if __name__=='__main__':main()
