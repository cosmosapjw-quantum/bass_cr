# SPDX-License-Identifier: GPL-3.0-only
"""Execute only the new PHYS02B acceptance work, preserving every run."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import platform
import sys
import time
import traceback

import numpy as np
import scipy
from scipy.integrate import quad

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import causal_cascade as cc


def relative(a,b):
    return abs(float(a)-float(b))/max(abs(float(b)),1.e-100)


def identity(path):
    data = path.read_bytes()
    return {'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}


def output_vector(model,final,a):
    total = final.sum(axis=1)
    rates = model.G@total+a.sum(axis=1)
    terminal = model.terminal_yields(a).sum(axis=1)
    out = {'active_energy':float(total[:model.n].sum()),
           'active_number':float(np.dot(1/model.E,total[:model.n])),
           'heat_power':float(rates[model.ix['heat']]),
           'terminal_heat_power':float(terminal[model.ix['heat']])}
    for name in cc.LEDGERS:out[name]=float(total[model.ix[name]])
    for name in ('ionizations_HI','ionizations_HeI'):
        out[name+'_rate']=float(rates[model.ix[name]])
    return out


def run(args, result):
    contract=json.loads((ROOT/'state/SCIENTIFIC_CONTRACT.json').read_text())
    tol=contract['tolerances']
    def check(name, passed, detail):
        entry={'id':name,'status':'PASS_SCOPED' if passed else 'FAIL','detail':detail}
        result['checks'].append(entry)
        print(json.dumps(entry,ensure_ascii=False),flush=True)

    source=cc.ElectronSource()
    atomic=cc.AtomicData()
    check('PARENT_SOURCE_AND_ATOMIC_IDENTITY', len(atomic.excitation)==27,
          {'parent_runtime_hash_guard':'PASSED','CCC_runtime_raw_hash_guards':27,
           'NIST_parameter_hash_guard':'PASSED','original_suites_rerun':0})
    coverage=source.coverage()
    result['coverage']=coverage
    direct_errors={}
    for W in (10.,20.,100.,400.,900.):
        direct=0.
        for sp,density in source.parent.densities.items():
            direct+=float(np.dot(source.parent.weights*source.parent.rudd.proton_speed_m_s(source.parent.K)*density,
                              source.parent.rudd.dsigma_dW_m2_per_eV(source.parent.K,W,sp)))
        direct_errors[str(W)]=relative(source.spectrum_A(W),direct)
    source_integral=quad(lambda W:float(W*source.spectrum_A(W))/source.selected_A_energy,
                         cc.CUT,cc.UPPER,epsabs=1.e-12,epsrel=1.e-12)[0]
    source_closure=abs(sum(coverage['band_fractions_of_all_direct'].values())-1)
    check('SOURCE_HIGH_W_AND_COVERAGE',max(direct_errors.values())<tol['source_shape_relative']
          and abs(source_integral-1)<tol['source_energy_relative'] and source_closure<1.e-12,
          {'direct_SDCS_relative_errors':direct_errors,'independent_adaptive_energy_integral':source_integral,
           'coverage_closure_absolute':source_closure,'minimum_sampled_endpoint_eV':source.minimum_endpoint_eV})

    normalization=[]
    for sp,ion in atomic.ionization.items():
        for E in (ion.B_eV*1.0001,30.,100.,400.,900.):
            if E<=ion.B_eV:continue
            raw=ion.raw_integral_m2(E,128)
            raw2=ion.raw_integral_m2(E,256)
            normalization.append({'species':sp,'energy_eV':E,'raw_BED_integral_m2':raw,
                                  'BEB_total_m2':float(ion.total_m2(E)),
                                  'NIST_model_normalization_factor':float(ion.total_m2(E))/raw,
                                  'quadrature_relative':relative(raw,raw2)})
    # The source-completion addendum was fixed before the first transport run.
    # Preserve the unavailable CGI comparison; do not substitute invented data.
    result['unexecuted_external_checks']=[{
        'id':'NIST_CGI_NUMERICAL_COMPARISON','status':atomic.nist_metadata['CGI_numerical_comparison'],
        'tolerance_if_available':tol['NIST_CGI_relative'],
        'replacement_scope':'Published-equation integral consistency only; exact CGI reproduction remains open.'}]
    ref_errors=[]
    for sp,ion in atomic.ionization.items():
        for E in (ion.B_eV*1.0001,30.,100.,400.,900.):
            if E<=ion.B_eV:continue
            t=E/ion.B_eV
            def published_beq(w):
                y=1/(1+w)
                r=1/(t-w)
                return (2-ion.Q)*(y*y+r*r-(y+r)/(t+1))+ion.Q*np.log(t)*(y**3+r**3)
            integral=quad(published_beq,0.,(t-1)/2,epsabs=1e-13,epsrel=1e-12)[0]
            reference=ion.S_m2/(t+ion.U_eV/ion.B_eV+1)*integral
            value=float(ion.total_m2(E))
            ref_errors.append({'species':sp,'T_eV':E,'reference_integrated_BEQ_m2':reference,
                               'computed_NIST_Eq1_m2':value,'relative_error':relative(value,reference)})
    result['ionization_normalization']=normalization
    result['published_equation_reference_comparison']=ref_errors
    check('PUBLISHED_BEQ_TOTAL_AND_BED_SHARING',len(ref_errors)>0
          and max(v['relative_error'] for v in ref_errors)<tol['ionization_quadrature_relative']
          and max(v['quadrature_relative'] for v in normalization)<tol['ionization_quadrature_relative'],
          {'reference_points':len(ref_errors),'max_reference_relative':max([v['relative_error'] for v in ref_errors],default=float('inf')),
           'max_raw_integral_quadrature_relative':max(v['quadrature_relative'] for v in normalization),
           'domain_source':atomic.nist_metadata['sharing_domain_source'],
           'external_CGI_comparison':'NOT_EVALUATED; see SOURCE_COMPLETION_ADDENDUM.json',
           'oscillator_moments':{sp:{'Ni':ion.Ni,'Q_from_df':ion.oscillator_Q,'adopted_Q':ion.Q} for sp,ion in atomic.ionization.items()}})

    grids=[tuple(map(int,v.split(','))) for v in args.grids.split(';')]
    models=[]
    for cells in grids:
        start=time.monotonic()
        print('BUILD_AND_RUN_GRID '+str(cells),flush=True)
        model=cc.Cascade(*cells,atomic=atomic)
        a=model.source_vectors(source)
        z=model.evolve(a,samples=2)[-1]
        metrics=output_vector(model,z,a)
        models.append((model,a,z,metrics))
        result.setdefault('grid_results',[]).append({'cells':list(cells),'nodes':model.n,
            'nnz':model.G.nnz,'seconds':time.monotonic()-start,'metrics_normalized':metrics,
            'final':model.summarize(z,a,source,1.),
            'sharing_quadrature_max_relative':max(row[2] for row in model.normalization_diagnostics)})
        print('GRID_COMPLETE '+json.dumps(result['grid_results'][-1],ensure_ascii=False),flush=True)

    model,a,z,metrics=models[-1]
    result['canonical_mesh']=list(model.mesh)
    ef,nf=model.functionals()
    absolute=abs(model.G)
    energy_scale=np.asarray(absolute.T@abs(ef)).ravel()
    number_scale=np.asarray(absolute.T@abs(nf)).ravel()
    e_col=np.asarray(model.G.T@ef).ravel()
    n_col=np.asarray(model.G.T@nf).ravel()
    energy_error=float(np.max(abs(e_col)/np.maximum(energy_scale,1.e-100)))
    number_error=float(np.max(abs(n_col)/np.maximum(number_scale,1.e-100)))
    final_si=model.summarize(z,a,source,1.)
    result['final']=final_si
    propagated=max(max(abs(v['energy_ledger_relative_residual']),abs(v['number_ledger_relative_residual']))
                   for v in final_si['components'].values())
    check('GENERATOR_ENERGY_AND_NUMBER', max(energy_error,number_error)<tol['generator_energy_number_relative']
          and propagated<tol['propagated_ledger_relative'],
          {'energy_column_relative':energy_error,'number_column_relative':number_error,'propagated_relative':propagated})

    small=models[0][0]
    small_a=models[0][1]
    off=small.evolve(small.source_vectors(source,enabled=False),samples=2)[-1]
    rejected=[]
    calls=[lambda:source.spectrum_A(900.0001),lambda:cc.stopping_eV_s(.099),
           lambda:small.evolve(small_a,time_s=-1),lambda:small.evolve(small_a,time_s=cc.T_END+1),
           lambda:source.parent.spectrum_A(10.01),
           lambda:atomic.ionization['HI'].raw_bed_m2_eV(100.,(100.-atomic.ionization['HI'].B_eV)/2+1e-6)]
    for fun in calls:
        try:fun()
        except ValueError:rejected.append(True)
        else:rejected.append(False)
    offdiagonal=model.G-scipy.sparse.diags(model.G.diagonal())
    min_offdiag=float(np.min(offdiagonal.data)) if offdiagonal.nnz else 0.
    check('CAUSALITY_POSITIVITY_AND_OFF',np.max(abs(off))==0
          and np.min(z)>=-tol['positivity_absolute_normalized'] and min_offdiag>=0
          and all(rejected) and np.max(abs(model.evolve(a,time_s=0)))==0,
          {'minimum_state':float(np.min(z)),'minimum_offdiagonal':min_offdiag,'source_off_max':float(np.max(abs(off))),
           'rejected_domain_cases':rejected,'initial_population':'exact zero'})

    from independent_oracles import run_oracles
    oracle_model=cc.Cascade(80,160,atomic=atomic)
    oracle=run_oracles(oracle_model,oracle_model.source_vectors(source))
    result['independent_oracles']=oracle
    for key in ('EXACT_SINGLE_EVENT_RAMP_ORACLE','INDEPENDENT_TIME_PROPAGATOR'):
        entry=oracle[key]
        check(key,entry['passed'],entry)
    entry=oracle['INDEPENDENT_GENERATOR_FUNCTIONALS']
    check('INDEPENDENT_GENERATOR_FUNCTIONALS',entry['passed'],entry)

    low_ref=source.low.aggregate(source.parent,source.low.CoulombClock(),cc.T_END)
    low=final_si['components']['direct_0p1_10']
    low_diffs={'heat_power':relative(low['heat_power_J_m3_s'],low_ref['stopping_heat_power_J_m3_s']),
               'heat':relative(low['heat_J_m3'],low_ref['deposited_stopping_energy_J_m3']),
               'cutoff':relative(low['cutoff_energy_J_m3'],low_ref['cutoff_residual_kinetic_J_m3'])}
    bdiff=float(np.max(abs(cc.stopping_eV_s(np.geomspace(.1,10.,50))/
                              source.low.CoulombClock().stopping_eV_s(np.geomspace(.1,10.,50))-1)))
    check('INHERITED_LOW_CONTINUUM_LIMIT',max(low_diffs['heat_power'],low_diffs['heat'])<tol['analytic_low_heat_relative']
          and low_diffs['cutoff']<tol['analytic_low_cutoff_relative'] and bdiff<1.e-12,
          {'relative_errors':low_diffs,'classical_low_stopping_agreement':bdiff,
           'reference':'Exact inherited Ei continuum response evaluated for the new discretization comparison; old suite not rerun.'})

    previous=models[-2][3]
    diffs={k:relative(metrics[k],previous[k]) for k in metrics}
    count_fields=('cutoff_number','low_cross_number')
    mesh_ok=all(v<(tol['mesh_cutoff_and_low_boundary_count_relative'] if k in count_fields
                   else tol['mesh_channel_relative']) for k,v in diffs.items())
    check('ENERGY_MESH_REFINEMENT',mesh_ok,{'coarse':list(models[-2][0].mesh),'fine':list(model.mesh),
           'relative_changes':diffs,'interpretation':'Empirical refinement difference, not a certified truncation-error bound.'})

    print('RUN_SHARING_ORDER8',flush=True)
    refined_sharing=cc.Cascade(*small.mesh,sharing_order=8,atomic=atomic)
    refined_a=refined_sharing.source_vectors(source)
    refined_z=refined_sharing.evolve(refined_a,samples=2)[-1]
    qmetrics=output_vector(refined_sharing,refined_z,refined_a)
    qdiff={k:relative(qmetrics[k],models[0][3][k]) for k in qmetrics}
    qnorm=max(row[2] for row in model.normalization_diagnostics)
    check('IONIZATION_PROJECTION_QUADRATURE',max(qdiff.values())<tol['ionization_quadrature_relative']
          and qnorm<tol['ionization_quadrature_relative'],
          {'orders':[4,8],'comparison_mesh':list(small.mesh),'observable_relative_changes':qdiff,
           'canonical_raw_integral_normalization_error_max':qnorm,
           'physical_BEB_to_BED_normalization_factor_range':[
               min(r[3] for r in model.normalization_diagnostics),max(r[3] for r in model.normalization_diagnostics)]})

    terminal=model.terminal_yields(a)
    terminal_energy=np.asarray(ef@terminal).ravel()
    input_energy=np.asarray(ef@a).ravel()
    terminal_number=np.asarray(nf@terminal).ravel()
    input_number=np.asarray(nf@a).ravel()
    terr=float(np.max(abs(terminal_energy-input_energy)/input_energy))
    nerr=float(np.max(abs(terminal_number-input_number)/input_number))
    trates=(model.G@z+a)[[model.ix[k] for k in cc.ENERGY_LEDGERS],:]
    terminal_rates=terminal[[model.ix[k] for k in cc.ENERGY_LEDGERS],:]
    bound=float(np.max(trates-terminal_rates))
    result['same_operator_terminal']={
        'energy_fractions_of_selected_input':{k:float(terminal[model.ix[k]].sum()) for k in cc.ENERGY_LEDGERS},
        'terminal_heat_power_at_T_J_m3_s':float(terminal[model.ix['heat']].sum()*source.energy_scale_eV_m3*cc.EV_J/cc.T_END),
        'finite_to_terminal_heat_power_ratio':float((model.G@z+a)[model.ix['heat']].sum()/terminal[model.ix['heat']].sum()),
        'interpretation':'Integrated kernel of the frozen truncated operator; no physical continuation of the local source to arbitrarily long time.'}
    check('SAME_OPERATOR_TERMINAL_LIMIT',max(terr,nerr)<tol['terminal_ledger_relative'] and bound<1.e-12,
          {'energy_relative':terr,'number_relative':nerr,'max_transient_minus_terminal_absorber_rate':bound,
           **result['same_operator_terminal']})

    print('RUN_COULOMB_PRESCRIPTION_SENSITIVITY',flush=True)
    alt=cc.Cascade(*model.mesh,atomic=atomic,quantum_constant=-.5)
    alt_a=alt.source_vectors(source)
    alt_z=alt.evolve(alt_a,samples=2)[-1]
    alt_metrics=output_vector(alt,alt_z,alt_a)
    sensitivity={k:(alt_metrics[k]-metrics[k])/max(abs(metrics[k]),1.e-100) for k in metrics}
    result['coulomb_sensitivity']={'quantum_log_offset':-.5,'relative_changes':sensitivity,
                                 'interpretation':'Preselected leading-log matching prescription variation, not physical error bound.'}
    check('COULOMB_PRESCRIPTION_SENSITIVITY',all(np.isfinite(v) for v in sensitivity.values()),result['coulomb_sensitivity'])

    print('RUN_CANONICAL_TRAJECTORY',flush=True)
    trajectory=model.evolve(a,samples=21)
    result['time_series']=[model.summarize(trajectory[j],a,source,j/20) for j in range(21)]
    np.savez_compressed(Path(args.run_dir)/'CANONICAL_SPECTRUM.npz',energy_eV=model.E,
                        state_normalized=trajectory,source_vectors=a,
                        physical_energy_scale_eV_m3=source.energy_scale_eV_m3,
                        time_s=np.linspace(0,cc.T_END,21))
    rate_points=[]
    for E in [10.,15.,20.,30.,50.,100.,300.,900.]:
        v=np.sqrt(2*E*cc.EV_J/cc.m_e)
        row={'energy_eV':E,'coulomb_stopping_eV_s':float(cc.stopping_eV_s(E)),
             'local_coulomb_E_over_b_s':float(E/cc.stopping_eV_s(E))}
        for sp in cc.DENSITIES:
            row['ionization_'+sp+'_s']=float(cc.DENSITIES[sp]*v*atomic.ionization[sp].total_m2(E))
            row['excitation_'+sp+'_s']=float(sum(cc.DENSITIES[sp]*v*atomic.excitation_sigma(c,E)
                                    for c in atomic.excitation if c['species']==sp))
        rate_points.append(row)
    result['rate_points']=rate_points


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--run-dir',required=True)
    parser.add_argument('--grids',default='200,400;400,800')
    args=parser.parse_args()
    path=Path(args.run_dir)
    path.mkdir(parents=True,exist_ok=True)
    output=path/'NUMERICAL_RESULT.json'
    if output.exists():raise FileExistsError('PRESERVE_EXISTING_RUN_OUTPUT')
    result={'schema':'cr-phys02b-execution-result.v1','start_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'command':sys.argv,'cwd':str(Path.cwd()),'environment':{'python':platform.python_version(),
               'numpy':np.__version__,'scipy':scipy.__version__,'precision':'FP64'},
            'source_identities':{str(p.relative_to(ROOT)):identity(p) for p in
               [ROOT/'src/causal_cascade.py',Path(__file__),ROOT/'state/SCIENTIFIC_CONTRACT.json',
                ROOT/'inputs/NIST_IONIZATION.json',ROOT/'inputs/CCC_USED_CHANNELS.json',
                ROOT/'state/SOURCE_COMPLETION_ADDENDUM.json',ROOT/'tests/independent_oracles.py']},
            'checks':[],'status':'RUNNING','prior_science_suites_rerun':0}
    start=time.monotonic()
    try:
        run(args,result)
        result['status']='PASS_SCOPED' if all(c['status']=='PASS_SCOPED' for c in result['checks']) else 'FAIL'
    except Exception:
        result['status']='EXECUTION_FAILED'
        result['exception']=traceback.format_exc()
        raise
    finally:
        result['end_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
        result['elapsed_seconds']=time.monotonic()-start
        result['passed_checks']=sum(c['status']=='PASS_SCOPED' for c in result['checks'])
        output.write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print('FINAL_STATUS '+result['status'],flush=True)
    return 0 if result['status']=='PASS_SCOPED' else 1


if __name__=='__main__':
    sys.exit(main())
