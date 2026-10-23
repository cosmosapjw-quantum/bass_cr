"""Independent C23B provider C9: saved bytes and three cell references only.

Does not import/run the producer validation or regenerate the nine cases.
"""
from pathlib import Path
from datetime import datetime, timezone
import csv
import hashlib
import json
import math
import os
import re
import resource
import sys
import time

HERE = Path(__file__).resolve().parent
LIVE = HERE.parents[1] / 'source_providers'
BASE = HERE / 'source_snapshot_v1'
RUN = LIVE / 'runs/c23b_pw19_spectral_source_20261023_v1'
GUARD_RUN = LIVE / 'runs/c23b_atomic_provider_guard_20261023_v2'

def digest(path):
    b=path.read_bytes()
    return {'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}

def write(path,obj):
    with path.open('x') as f:json.dump(obj,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')

def main(out):
    t0,c0=time.perf_counter(),time.process_time()
    import mpmath as mp
    mp.mp.dps=70
    checks={};verified=[]
    source=json.loads((RUN/'SOURCE_IDENTITY.json').read_text())
    for name,pin in source['files'].items():
        actual=digest(BASE/name);assert actual==pin,(name,actual,pin);verified.append({'path':name,**actual})
    identity=hashlib.sha256(json.dumps(source['files'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
    assert identity==source['source_identity_sha256']
    checks['source_pin']=True
    completed=json.loads((RUN/'COMPLETE.json').read_text())
    raw_verified=[]
    for name,pin in completed['files'].items():
        actual=digest(RUN/name);assert actual==pin,(name,actual,pin);raw_verified.append({'path':name,**actual})
    checks['saved_result_pins']=True
    cases=json.loads((RUN/'CASES.json').read_text())
    rows=list(csv.DictReader((RUN/'photoelectron_atoms.csv').open()))
    saved_sums=[]
    for case in cases:
        selected=[r for r in rows if float(r['redshift'])==case['redshift'] and r['channel']==case['channel']]
        pairs=[(float(r['kinetic_eV']),float(r['number_weight_per_target_s'])) for r in selected]
        assert all(k>=0 and w>0 and math.isfinite(k*w) for k,w in pairs)
        count=math.fsum(w for k,w in pairs);kinetic=math.fsum(k*w for k,w in pairs)
        expected=case['result'];assert len(pairs)==expected['atom_count']
        assert count==expected['number_per_target_s'] and kinetic==expected['kinetic_eV_per_target_s']
        saved_sums.append({'z':case['redshift'],'channel':case['channel'],'atoms':len(pairs),'count':count,'kinetic':kinetic})
    checks['saved_atoms_reaggregate']=True
    assert len(rows)==32592 and len(cases)==9

    # Reformat is independently reconstructed from five original Cloudy lines
    # at one z with arbitrary precision, not by executing the upstream converter.
    tab=list(csv.DictReader((BASE/'data/z_02.479000.csv').open()))
    original=(BASE/'taira_v1_0_0/cloudy_formatted_data/pw19/pw19_z_2.4790e+00.out').read_text()
    assert '# E [Ryd] log (J_nu)' in original
    native=re.findall(r'^continue \(([^)]+)\) \(([^)]+)\)',original,re.M)[1:-2]
    assert len(native)==len(tab)==626
    conversions=[]
    for i in [0,143,286,429,625]:
        ryd,logj=map(mp.mpf,native[i]);energy=ryd*mp.mpf('13.605703976')
        nu=energy*mp.mpf('1.602176562e-12')/mp.mpf('6.62606957e-27')
        s=4*mp.pi*nu*10**logj
        se=mp.mpf(tab[i]['I (erg/s/cm**2)']);ee=mp.mpf(tab[i]['E (eV)'])
        conversions.append({'row':i,'energy_relative':float(abs(ee/energy-1)), 'S_relative':float(abs(se/s-1))})
    checks['five_raw_to_S70']=max(x['S_relative'] for x in conversions)<2e-13

    # Independent integrand uses the literal table strings and arbitrary
    # precision in linear photon energy. Only three selected cells are audited.
    row=next(x.split() for x in (BASE/'data/verner_photo.dat').read_text().splitlines() if x.split()[:2]==['1','1'])
    chi,emax,e0,s0,ya,p,yw,y0,y1=map(mp.mpf,row[2:])
    energy=[mp.mpf(x['E (eV)']) for x in tab]
    spectral=[mp.mpf(x['I (erg/s/cm**2)']) for x in tab]
    edges=sorted(set([chi,emax,chi+10,chi+mp.mpf('9937.21')]+[x for x in energy if chi<x<emax]))
    chosen=[0,next(i for i,(a,b) in enumerate(zip(edges,edges[1:])) if a<100<=b),len(edges)-2]
    def sigma(e):
        x=e/e0-y0;y=mp.sqrt(x*x+y1*y1)
        return mp.mpf('1e-18')*s0*((x-1)**2+yw*yw)*y**(p/2-mp.mpf('5.5'))*(1+mp.sqrt(y/ya))**(-p)
    def S(e):
        i=max(i for i,x in enumerate(energy) if x<=e)
        if i==len(energy)-1:return spectral[i]
        slope=mp.log(spectral[i+1]/spectral[i])/mp.log(energy[i+1]/energy[i])
        return spectral[i]*(e/energy[i])**slope
    hi_atoms=[(mp.mpf(x['kinetic_eV']),mp.mpf(x['number_weight_per_target_s'])) for x in rows if x['channel']=='HI' and float(x['redshift'])==2.479]
    cells=[]
    for index in chosen:
        a,b=edges[index:index+2]
        weights=[(k,w) for k,w in hi_atoms if a<k+chi<b]
        assert len(weights)==16,(index,len(weights))
        reference=[];computed=[];relative=[]
        for power in (0,1):
            f=lambda e:S(e)*sigma(e)/(mp.mpf('1.602176634e-12')*e*e)*(e-chi)**power
            val=mp.quad(f,[a,b]);raw=sum((k**power*w for k,w in weights),mp.mpf(0))
            reference.append(str(val));computed.append(str(raw));relative.append(float(abs(raw/val-1)))
        cells.append({'edge_index':index,'photon_interval_eV':[str(a),str(b)],'saved_atoms':16,'reference_count_kinetic':reference,'saved_count_kinetic':computed,'relative_errors':relative})
    checks['three_cells_mp70_linear_E']=max(e for c in cells for e in c['relative_errors'])<2e-11

    # Quarantine audit reads stored bytes only, without repairing the release.
    anomaly=json.loads((BASE/'SOURCE_ANOMALY.json').read_text())
    z0=BASE/anomaly['file'];assert digest(z0)['sha256']==anomaly['sha256']
    vals=[float(x['I (erg/s/cm**2)']) for x in csv.DictReader(z0.open())]
    assert min(vals)==anomaly['intensity_min'] and max(vals)==anomaly['intensity_max']
    contract=json.loads((BASE/'CONTRACT.json').read_text());assert 0.0 not in contract['admitted_redshift_nodes']
    checks['z0_quarantine_preserved']=True

    # Targeted API guard inspection: one deliberately altered provider, no
    # production source/rate quadrature and no broad invalid-input suite replay.
    import importlib.util
    name='provider_c9_pinned'
    spec=importlib.util.spec_from_file_location(name,BASE/'spectral_photo_source.py');mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod)
    from dataclasses import replace
    a=mod.Verner96.from_table('HI'); altered=replace(a,threshold_eV=12.0)
    explicit_guard={'original_threshold_eV':a.threshold_eV,'altered_threshold_eV':altered.threshold_eV,
       'altered_sigma_at_12_eV':altered.sigma_cm2(12.0),
       'isinstance_accepts_altered':isinstance(altered,mod.Verner96),
       'note':'Static photoelectron_atoms type guard accepts this altered instance; full atom generation intentionally not invoked.'}
    checks['source_model_thresholds']=float(chi)==13.6 and a.maximum_eV==50000.

    # Close the author's correction against actual saved v2 guard artifacts.
    # These reads do not rerun the guard suite or the nine spectral cases.
    guard_identity=json.loads((GUARD_RUN/'SOURCE_IDENTITY.json').read_text())
    for name,pin in guard_identity['files'].items():
        assert digest(LIVE/name)==pin,(name,'guard-source-pin-mismatch')
    guard_source_id=hashlib.sha256(json.dumps(guard_identity['files'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
    assert guard_source_id==guard_identity['source_identity_sha256']
    guard_complete=json.loads((GUARD_RUN/'COMPLETE.json').read_text())
    guard_pins=[]
    for name,pin in guard_complete['files'].items():
        actual=digest(GUARD_RUN/name);assert actual==pin,(name,'guard-result-pin-mismatch')
        guard_pins.append({'path':name,**actual})
    guard=json.loads((GUARD_RUN/'SUMMARY.json').read_text())
    assert guard['targeted_checks']==51 and len(guard['checks'])==51
    assert all(x['pass'] for x in guard['checks']) and guard['status']=='PASS_SCOPED'
    assert guard['new_spectral_cases']==guard['new_ODE']==guard['historical_reruns']==0
    assert {x['name'] for x in guard['checks'] if 'source_fit_threshold_zero' in x['name']}=={
        'HI_source_fit_threshold_zero','HeI_source_fit_threshold_zero','HeII_source_fit_threshold_zero'}
    checks['correction_guard_saved_receipt']=True
    correction={'source_identity':guard_source_id,'summary':digest(GUARD_RUN/'SUMMARY.json'),
        'targeted_checks':51,'all_pass':True,'new_spectral_cases':0,'guard_pins':guard_pins,
        'closure':'Canonical row tuple enforced at construction and at all three consuming APIs; source-fit threshold zero terminology in new guard record; original v1 evidence preserved.'}
    result={'schema':'C23B_PROVIDER_C9_V1','status':'PASS_SCOPED_FINDINGS_CLOSED' if all(checks.values()) else 'FAIL',
      'checks':checks,'reviewed_source_identity':identity,'source_pins':verified,'saved_pins':raw_verified,
      'saved_rows_reaggregated':len(rows),'saved_cases_reaggregated':len(cases),'saved_reaggregates':saved_sums,
      'raw_conversion_reference':conversions,'independent_cells':cells,'v1_guard_observation':explicit_guard,
      'v2_correction_closure':correction,
      'quadrature_calls':6,'full_case_integrations':0,'producer_runs':0,'new_ODE':0,'historical_reruns':0,
      'affinity':sorted(os.sched_getaffinity(0)),'thread_env':{k:os.environ.get(k) for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']},
      'CPU_s':time.process_time()-c0,'wall_s':time.perf_counter()-t0,'maxrss_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
      'finished_utc':datetime.now(timezone.utc).isoformat()}
    write(out/'RESULT.json',result)
    print(json.dumps({k:result[k] for k in ['status','checks','quadrature_calls','full_case_integrations','CPU_s','wall_s']}))
    return 0 if all(checks.values()) else 2

if __name__=='__main__':
    os.sched_setaffinity(0,{5})
    raise SystemExit(main(Path(sys.argv[1])))
