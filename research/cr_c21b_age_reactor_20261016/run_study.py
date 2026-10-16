"""Reproducible finite study: source-on original Verner and independent smooth mono."""
from pathlib import Path
import sys,math,json,time,statistics,hashlib
import numpy as np
from scipy.integrate import quad
sys.path.insert(0,str(Path(__file__).resolve().parent/'src'))
from c21b_age_reactor import PhotonReactor,initial_state,md14_rate_per_total_h_s,hubble
from independent_mono import solve_continuous_mono
ROOT=Path(__file__).resolve().parent


def main():
    x0=math.log(1/12)
    out={'schema':'BASS_CR_C21B_SOURCE_AGE_PHOTO_ONLY_LIGHT_STUDY_V1',
      'science_scope':'FLRW scalar positive photo-only; actual Verner and MD14 source; manufactured constant-opacity independent Radau separate',
      'production_Rust_C21':'NOT_RUN','same_epoch_native_parity':'NOT_RUN','time_order':'REFINEMENT_SCOPED_ONLY',
      'cases':{}}
    intervals={"smooth_real_verner":0.0008,"manufactured_const_sigma":.015,
               "native_opacity_stiff":.00015}
    for key,dx in intervals.items():
        vals=[]; start=time.perf_counter()
        steps=(2,4,8,16,32) if key!='native_opacity_stiff' else (2,4,8,16)
        for n in steps:
            state=initial_state(x0,8500.,(0.2,0.2,.01),((80.,.004),))
            model=PhotonReactor(energy_nodes=2,
                  opacity_scale=(.0001 if key!='native_opacity_stiff' else 1.),
                  source_scale=2.)
            if key=='manufactured_const_sigma':
                model.spectrum=[(80.,1.)]
                sg=[1e-18,3e-18,5e-18]
                model.sigma=lambda j,E,sg=sg:sg[j]
            state=model.advance(state,x0+dx,n,source_on=True)
            led=state.ledgers()
            vals.append({'nsteps':n,'N_end':led['photons_per_H'],
              'U_end_ev_H':led['photon_energy_ev_per_H'],'gas_fractions':state.fractions(),
              'thermal_ev_H':state.thermal_ev,'Tgas_K':led['T_K'],
              'species_events_per_H':led['photo_events_per_H'],
              'species_heat_ev_H':led['photoheat_ev_per_H'],
              'number_residual':led['number_residual'],
              'energy_residual_ev_H':led['energy_residual_ev_per_H'],
              'source_N':state.source_n,'source_U_ev_H':state.source_u,
              'photons':led['number_cohorts'],'threshold_crossings':led['crossings']})
        result={'data':vals,'total_wall_s':time.perf_counter()-start}
        if key=='manufactured_const_sigma':
            initial=initial_state(x0,8500.,(0.2,0.2,.01),((80.,.004),))
            radau=solve_continuous_mono(initial,x0+dx)
            ref=radau['final']
            errors=[]
            for v in vals:
                z=[v['N_end'],v['U_end_ev_H'],*[
                  1-v['gas_fractions'][0],v['gas_fractions'][0],
                  (initial.atoms[2]+initial.atoms[3]+initial.atoms[4])*(1-v['gas_fractions'][1]-v['gas_fractions'][2]),
                  (initial.atoms[2]+initial.atoms[3]+initial.atoms[4])*v['gas_fractions'][1],
                  (initial.atoms[2]+initial.atoms[3]+initial.atoms[4])*v['gas_fractions'][2]],
                  v['thermal_ev_H']]
                # Physical independent ODE comparison N,U,atoms,thermal; avoids strong dependence on tiny ledgers.
                err=max(abs(z[j]-ref[j]) for j in range(8))
                errors.append(err)
                v['state_infinity_error_vs_Radau']=err
            result['radau']={'nfev':radau['function_evals'],'state_start':initial.fractions(),
                             'state_reference':ref[:8], 'errors':errors,
                             'last_effective_orders':[
                               math.log(errors[i-1]/errors[i],2) if errors[i]>0 and errors[i-1]>0 else None
                               for i in range(1,len(errors))]}
        # Cauchy differs from continuum; only a diagnostic when no independent reference.
        q=[v['thermal_ev_H'] for v in vals]
        result['adjacent_thermal_differences']=[abs(q[i+1]-q[i]) for i in range(len(q)-1)]
        result['max_abs_number_ledger']=max(abs(v['number_residual']) for v in vals)
        result['max_abs_energy_ledger_ev_H']=max(abs(v['energy_residual_ev_H']) for v in vals)
        out['cases'][key]=result
    # A deliberately isolated source-timing counterexample: same total photon
    # birth count, same monoenergetic birth energy and native Verner cross-section,
    # but two true birth epochs versus one midpoint epoch near the HeII fit cut.
    rate=lambda x:3e-17  # manufactured constant photons/(total H s)
    xbirth_end=x0+.004
    start=initial_state(x0,8500.,(.2,.2,.01))
    agemodel=PhotonReactor(energy_nodes=1,source=rate,opacity_scale=.03)
    agemodel.spectrum=[(54.55,1.)]
    age=agemodel.advance(start.clone(),xbirth_end,1,source_on=True)
    mid=0.5*(x0+xbirth_end)
    midpoint_model=PhotonReactor(energy_nodes=1,source=rate,opacity_scale=.03)
    midpoint_model.spectrum=[(54.55,1.)]
    collapsed=start.clone()
    midpoint_model._segment(collapsed,x0,mid)
    midpoint_model._birth(collapsed,mid,age.source_n*hubble(mid)/rate(mid))
    midpoint_model._segment(collapsed,mid,xbirth_end)
    collapsed.validation()
    out['age_matched_birth_counterexample']={
      'scope':'manufactured time-constant mono54.55eV source; original Verner; photo-only; same birth photon number and energy; different birth-age distribution',
      'a_start':math.exp(x0),'a_end':math.exp(xbirth_end),
      'age_GL2':age.ledgers(),
      'midpoint_collapse':collapsed.ledgers(),
      'delta_HeII_events_per_total_H':age.photo_events[2]-collapsed.photo_events[2],
      'delta_Tgas_K':age.eos_temperature_K()-collapsed.eos_temperature_K(),
      'source_N_diff':age.source_n-collapsed.source_n,
      'source_U_diff':age.source_u-collapsed.source_u
    }
    path=ROOT/'evidence/STUDY.json'
    path.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
    for key,v in out['cases'].items():
        print('CASE',key,'n',[p['nsteps'] for p in v['data']],
           'max Nres',v['max_abs_number_ledger'],'max Eres',v['max_abs_energy_ledger_ev_H'],
           'thermal adjacent differences',v['adjacent_thermal_differences'],
           'wall',v['total_wall_s'])
        if 'radau' in v:print('RADAU_ERRORS',v['radau']['errors'],'ORDERS',v['radau']['last_effective_orders'])
    print('BIRTH_TIMING_DELTA_HEII',out['age_matched_birth_counterexample']['delta_HeII_events_per_total_H'],
          'DELTA_Tgas_K',out['age_matched_birth_counterexample']['delta_Tgas_K'])
    print('OUT',path,'SHA256',hashlib.sha256(path.read_bytes()).hexdigest())
if __name__=='__main__':main()
