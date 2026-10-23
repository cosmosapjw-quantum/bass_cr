"""New spectral-source scientific audit, intended for an admitted single worker."""
from __future__ import annotations
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import resource
import time

from spectral_photo_source import (PW19Spectrum, Verner96, photoelectron_atoms,
    summarize_atoms, electron_density, EV_ERG, ROOT)


def write(path, value):
    with path.open("x") as f:json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False);f.write("\n")


def relative(a,b):
    return abs(a-b)/max(abs(a),abs(b),1e-300)


def validate(run):
    t0,cpu0=time.perf_counter(),time.process_time()
    import mpmath as mp
    from scipy.integrate import quad
    mp.mp.dps=80
    contract=json.loads((ROOT/"CONTRACT.json").read_text())
    limits=contract['validation_before_execution']
    checks={}
    raw_conversions=[]
    for z in contract['admitted_redshift_nodes']:
        spectrum=PW19Spectrum(z)
        filename=f"pw19_z_{z:.4e}.out"
        path=ROOT/'taira_v1_0_0/cloudy_formatted_data/pw19'/filename
        raw=[(float(a),float(b)) for a,b in re.findall(r'^continue \(([^)]+)\) \(([^)]+)\)',path.read_text(),re.M)][1:-2]
        assert len(raw)==626
        # The published converter used unyt's legacy eV and h values. Preserve
        # that numeric convention rather than silently changing release bytes.
        legacy_EV_ERG=1.602176562e-12
        legacy_H_ERG_S=6.62606957e-27
        errE=errS=0.0
        for (ryd,logj),e,s in zip(raw,spectrum.energy_eV,spectrum.spectral_S):
            eref=ryd*13.605703976
            sref=4*math.pi*(eref*legacy_EV_ERG/legacy_H_ERG_S)*10**logj
            errE=max(errE,relative(e,eref));errS=max(errS,relative(s,sref))
        raw_conversions.append({'redshift':z,'rows':len(raw),'energy_relative_max':errE,'S_relative_max':errS,
            'raw_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'legacy_conversion':{'Ryd_to_eV':13.605703976,'eV_to_erg':legacy_EV_ERG,'h_erg_s':legacy_H_ERG_S}})
    checks['three_original_format_relations']=max(x['S_relative_max'] for x in raw_conversions)<=limits['source_reformat_relative']
    cross=[]
    for channel in ['HI','HeI','HeII']:
        a=Verner96.from_table(channel)
        for e in [a.threshold_eV,1.000001*a.threshold_eV,2*a.threshold_eV,100.,1000.,1e4,5e4]:
            if e<a.threshold_eV:continue
            E,E0,s0,ya,P,yw,y0,y1=map(lambda x:mp.mpf(str(x)),[e,a.E0_eV,a.sigma0_Mb,a.ya,a.P,a.yw,a.y0,a.y1])
            x=E/E0-y0;y=mp.sqrt(x*x+y1*y1)
            reference=mp.mpf('1e-18')*s0*((x-1)**2+yw*yw)*mp.power(y,P/2-mp.mpf('5.5'))*mp.power(1+mp.sqrt(y/ya),-P)
            got=a.sigma_cm2(e);err=float(abs(mp.mpf(got)/reference-1))
            cross.append({'channel':channel,'photon_eV':e,'sigma_cm2':got,'mp80_relative':err})
    checks['Verner_eq1_mp80']=max(x['mp80_relative'] for x in cross)<=limits['crosssection_mp80_relative']
    cases=[];all_atoms=[]
    for z in contract['admitted_redshift_nodes']:
        spectrum=PW19Spectrum(z)
        for channel in ['HI','HeI','HeII']:
            atom=Verner96.from_table(channel)
            atoms8=photoelectron_atoms(spectrum,atom,order=8)
            atoms16=photoelectron_atoms(spectrum,atom,order=16)
            s8,s16=summarize_atoms(atoms8,atom.threshold_eV),summarize_atoms(atoms16,atom.threshold_eV)
            kinetic_edges=[0.,10.,9937.21,atom.maximum_eV-atom.threshold_eV]
            independent=[]
            for klo,khi in zip(kinetic_edges,kinetic_edges[1:]):
                lo,hi=atom.threshold_eV+klo,atom.threshold_eV+khi
                edges=[lo]+[x for x in spectrum.energy_eV if lo<x<hi]+[hi]
                def integrand(e,moment):
                    q=spectrum.evaluate(e)*atom.sigma_cm2(e)/(EV_ERG*e*e)
                    return q*((e-atom.threshold_eV) if moment==1 else 1.)
                v=[];errs=[]
                for moment in (0,1):
                    items=[quad(integrand,a,b,args=(moment,),epsabs=1e-60,epsrel=5e-13,limit=50) for a,b in zip(edges,edges[1:])]
                    v.append(math.fsum(x[0] for x in items));errs.append(math.fsum(x[1] for x in items))
                independent.append({'number_per_target_s':v[0],'kinetic_eV_per_target_s':v[1],'quad_estimates':errs})
            c816=max(relative(s8[k],s16[k]) for k in ['number_per_target_s','kinetic_eV_per_target_s'])
            cq=max(relative(a[k],b[k]) for a,b in zip(s16['bins'],independent) for k in ['number_per_target_s','kinetic_eV_per_target_s'])
            ledger=abs(s16['energy_ledger_residual_eV_per_target_s'])/s16['absorbed_photon_eV_per_target_s']
            s16['bins'][0]['label']='electron_K_below_FS10_eV'
            s16['bins'][1]['label']='FS_energy_domain_10_to_9937.21_eV_only'
            s16['bins'][2]['label']='electron_K_above_FS_upper_within_Verner_domain'
            for row in s16['bins']:
                row['count_fraction_of_finite_atomic_source']=row['number_per_target_s']/s16['number_per_target_s']
                row['kinetic_fraction_of_finite_atomic_source']=row['kinetic_eV_per_target_s']/s16['kinetic_eV_per_target_s']
            cases.append({'redshift':z,'channel':channel,'threshold_eV':atom.threshold_eV,'photon_support_eV':[atom.threshold_eV,atom.maximum_eV],
                'result':s16,'Gauss8_vs16_relative':c816,'Gauss16_vs_independent_quad_relative':cq,'energy_ledger_relative':ledger,
                'independent_quad_bins':independent,
                'radiation_above_atomic_domain':dict(spectrum.photon_flux_moments(atom.maximum_eV,spectrum.energy_eV[-1]),
                    atomic_event_rate=None,reason='cross section outside admitted range')})
            all_atoms.extend({'redshift':z,'channel':channel,'kinetic_eV':k,'number_weight_per_target_s':w} for k,w in atoms16)
    checks['Gauss8_vs16']=max(x['Gauss8_vs16_relative'] for x in cases)<=limits['Gauss8_vs16_relative']
    checks['Gauss16_vs_independent_quad']=max(x['Gauss16_vs_independent_quad_relative'] for x in cases)<=limits['Gauss16_vs_quad_relative']
    checks['binding_plus_kinetic_energy']=max(x['energy_ledger_relative'] for x in cases)<=limits['energy_ledger_relative']
    checks['positive_atoms']=all(x['kinetic_eV']>=0 and x['number_weight_per_target_s']>0 for x in all_atoms)
    # Old D1 table is an independent source identity; compare, never merge.
    d1=[]
    for line in (ROOT/'data/C23A_P19V1_rates_fiducial.txt').read_text().splitlines():
        if line.strip() and not line.lstrip().startswith('#'):d1.append(list(map(float,line.split())))
    comparisons=[]
    for case in cases:
        z=case['redshift'];i=next(i for i in range(len(d1)-1) if d1[i][0]<=z<=d1[i+1][0]);f=(math.log1p(z)-math.log1p(d1[i][0]))/(math.log1p(d1[i+1][0])-math.log1p(d1[i][0]))
        col=1+2*['HI','HeI','HeII'].index(case['channel'])
        old=[math.exp((1-f)*math.log(d1[i][c])+f*math.log(d1[i+1][c])) for c in [col,col+1]]
        comparisons.append({'redshift':z,'channel':case['channel'],'D1_gamma_s_inv':old[0],'D1_heat_eV_s_inv':old[1],
            'new_source_gamma_over_D1':case['result']['number_per_target_s']/old[0],
            'new_source_kinetic_over_D1_heat':case['result']['kinetic_eV_per_target_s']/old[1],
            'interpretation':'Different release/model/threshold/interpolation identities; diagnostic only, no compatibility acceptance test'})
    guards=[]
    spec=PW19Spectrum(2.479);atom=Verner96.from_table('HI')
    calls=[('missing_channel',lambda:Verner96.from_table('DI')),('z0_quarantined',lambda:PW19Spectrum(0.)),('z20',lambda:PW19Spectrum(20.)),
      ('zinterpolation_unadmitted',lambda:PW19Spectrum(2.5)),('nan_z',lambda:PW19Spectrum(float('nan'))),('bool_z',lambda:PW19Spectrum(True)),
      ('negative_E',lambda:atom.sigma_cm2(-1.)),('above_atomic_Emax',lambda:atom.sigma_cm2(50000.1)),('negative_K',lambda:electron_density(spec,atom,-1.)),
      ('infinite_K',lambda:electron_density(spec,atom,float('inf'))),('above_spectral_range',lambda:spec.evaluate(spec.energy_eV[-1]*2)),
      ('duplicate_cuts',lambda:photoelectron_atoms(spec,atom,kinetic_cuts_eV=(10.,10.))),('out_of_range_cut',lambda:photoelectron_atoms(spec,atom,kinetic_cuts_eV=(1e5,))),
      ('wrong_order',lambda:photoelectron_atoms(spec,atom,order=3)),('bool_order',lambda:photoelectron_atoms(spec,atom,order=True))]
    for name,call in calls:
        try:call();guards.append({'case':name,'rejected':False})
        except (ValueError,TypeError) as e:guards.append({'case':name,'rejected':True,'reason':str(e)})
    checks['invalid_input_guards']=len(guards)>=limits['guard_cases_min'] and all(x['rejected'] for x in guards)
    checks['below_threshold_physical_zero']=atom.sigma_cm2(atom.threshold_eV-1e-5)==0.
    with (run/'photoelectron_atoms.csv').open('x',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(all_atoms[0]));writer.writeheader();writer.writerows(all_atoms)
    write(run/'CASES.json',cases);write(run/'D1_SEPARATE_IDENTITY_COMPARISON.json',comparisons)
    write(run/'SOURCE_CONVERSION_AUDIT.json',raw_conversions);write(run/'CROSSSECTION_MP80.json',cross);write(run/'GUARDS.json',guards)
    summary={'run_id':run.name,'status':'PASS_SCOPED' if all(checks.values()) else 'FAIL','checks':checks,'new_spectral_cases':len(cases),
        'positive_electron_atoms':len(all_atoms),'Gauss8_vs16_max_relative':max(x['Gauss8_vs16_relative'] for x in cases),
        'Gauss16_vs_independent_quad_max_relative':max(x['Gauss16_vs_independent_quad_relative'] for x in cases),
        'source_reformat_max_relative':max(x['S_relative_max'] for x in raw_conversions),
        'crosssection_mp80_max_relative':max(x['mp80_relative'] for x in cross),
        'energy_ledger_max_relative':max(x['energy_ledger_relative'] for x in cases),
        'new_ODE':0,'historical_reruns':0,'global_error_bound':None,'worker_CPU_s':time.process_time()-cpu0,'worker_wall_s':time.perf_counter()-t0,
        'peak_RSS_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'finished_utc':datetime.now(timezone.utc).isoformat()}
    write(run/'SUMMARY.json',summary)
    write(run/'COMPLETE.json',{'status':summary['status'],'files':{p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in run.iterdir() if p.is_file()}})
    return summary
