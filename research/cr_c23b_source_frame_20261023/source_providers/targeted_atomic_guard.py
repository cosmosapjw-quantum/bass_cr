"""Targeted C9 correction checks only; no historical spectral-case rerun."""
from dataclasses import fields, replace, FrozenInstanceError
import hashlib
import json
from pathlib import Path
import resource
import time
from spectral_photo_source import ROOT, PW19Spectrum, Verner96, electron_density, photoelectron_atoms

def write(path,value):
    with path.open('x') as f:json.dump(value,f,indent=2,allow_nan=False);f.write('\n')

def validate(run):
    t0,c0=time.perf_counter(),time.process_time();checks=[]
    def rejects(name,callback):
        try:callback();checks.append({'name':name,'pass':False})
        except (ValueError,TypeError,FrozenInstanceError) as error:checks.append({'name':name,'pass':True,'error':str(error)})
    spectrum=PW19Spectrum(2.479)
    for channel in ('HI','HeI','HeII'):
        atom=Verner96.from_table(channel)
        checks.append({'name':channel+'_source_fit_threshold_zero','pass':atom.sigma_cm2(atom.threshold_eV-1e-5)==0.})
        for field in fields(atom):
            if field.name=='channel':continue
            value=getattr(atom,field.name)
            rejects(channel+'_replace_'+field.name,lambda f=field.name,v=value:replace(atom,**{f:v+max(abs(v)*1e-4,1e-6)}))
        values=[getattr(atom,f.name) for f in fields(atom)]
        values[1]=0.;rejects(channel+'_manual_constructor',lambda:Verner96(*values))
        rejects(channel+'_unknown_channel',lambda:replace(atom,channel='DI'))
        rejects(channel+'_nan_coefficient',lambda:replace(atom,P=float('nan')))
        rejects(channel+'_bool_coefficient',lambda:replace(atom,yw=True))
        corrupted=Verner96.from_table(channel)
        object.__setattr__(corrupted,'threshold_eV',0.)
        rejects(channel+'_mutated_sigma_consumer',lambda:corrupted.sigma_cm2(30.))
        rejects(channel+'_mutated_density_consumer',lambda:electron_density(spectrum,corrupted,30.))
        rejects(channel+'_mutated_quadrature_consumer',lambda:photoelectron_atoms(spectrum,corrupted))
    result={'run_id':run.name,'status':'PASS_SCOPED' if all(x['pass'] for x in checks) else 'FAIL','checks':checks,
        'targeted_checks':len(checks),'source':'C9 atomic-parameter identity guard correction',
        'reused_science_run':'c23b_pw19_spectral_source_20261023_v1','new_spectral_cases':0,'new_ODE':0,'historical_reruns':0,
        'global_error_bound':None,'worker_CPU_s':time.process_time()-c0,'worker_wall_s':time.perf_counter()-t0,
        'peak_RSS_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    write(run/'SUMMARY.json',result)
    write(run/'COMPLETE.json',{'status':result['status'],'files':{p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in run.iterdir() if p.is_file()}})
    return result
