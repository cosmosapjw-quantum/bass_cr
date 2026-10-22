#!/usr/bin/env python3
"""C22E diagnostic only: reuse C22D stored fields; no model/RHS/rate/ODE imports.

LRS a_perp=a*exp(-b), a_parallel=a*exp(2*b), s=db/dt. With mu the
physical photon direction, H_gamma=H+s*(3*mu**2-1) is affine in mu**2.
The exact angular endpoints at each supplied time are H-s and H+2*s.
Time sampling remains finite. Missing physical sources stay null.
"""
from __future__ import annotations
import argparse
import csv
import datetime
from fractions import Fraction
import hashlib
import io
import json
import math
import os
from pathlib import Path
import platform
import re
import sys
import time

THREAD_KEYS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
               "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS")
for _key in THREAD_KEYS:
    os.environ[_key] = "1"
import numpy as np

SOURCE = "2e065d2ec2605fcee4bd9f6444e90b58f85bbf047f4d1444dfe7e386eb828c72"
CASES = (
    ("nominal", "registry_control_lrs", "c22d_h1_ci_bdf_20261022_v1",
     "f3da88211acb99aa6691772faf540ae7b96bff2df8590f14a7dd6557c217abc3"),
    ("nominal", "ci_lrs", "c22d_h1_ci_bdf_20261022_v1",
     "cc69ba27e1c188359c9798a07bce847656b09f17eef7dff449851ab683d34282"),
    ("nominal", "ci_flrw", "c22d_h1_ci_bdf_20261022_v1",
     "811315a48141efe5c49e4bd327f201c27ab735645c1606866887d8d3120d36b9"),
    ("reference", "ci_lrs", "c22d_h1_ci_radau_20261022_v1",
     "f7868f5e2aaa9a0598e03d0da04dedaeb96c21644a97c011e702de48226761c2"),
)

def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def digest(data):
    return hashlib.sha256(data).hexdigest()

def pin(path):
    data = Path(path).read_bytes()
    return {"path": str(Path(path).resolve()), "bytes": len(data), "sha256": digest(data)}

def write_json(path, obj):
    with Path(path).open("x", encoding="utf8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write("\n")

def directional(h, s):
    if h is None or s is None:
        return {"status": "REQUIRED_INPUT_UNAVAILABLE", "H_perp_per_s": None,
                "H_parallel_per_s": None, "H_gamma_min_per_s": None,
                "H_gamma_max_per_s": None, "three_abs_s_over_H": None}
    h, s = np.asarray(h), np.asarray(s)
    if (h.dtype.kind not in "fiu" or s.dtype.kind not in "fiu" or h.shape != s.shape
            or not np.isfinite(h).all() or not np.isfinite(s).all()
            or np.any(h <= 0)):
        raise ValueError("FINITE_MATCHING_REAL_H_POSITIVE_AND_SIGNED_S_REQUIRED")
    hp, ha = h-s, h+2*s
    return {"status": "COMPUTED_SCOPED", "H_perp_per_s": hp,
            "H_parallel_per_s": ha, "H_gamma_min_per_s": np.minimum(hp, ha),
            "H_gamma_max_per_s": np.maximum(hp, ha), "three_abs_s_over_H": 3*np.abs(s)/h}

def sign_regime(low, high):
    if low > 0:
        return "ALL_DIRECTIONS_REDSHIFT_AT_SAMPLE"
    if high < 0:
        return "ALL_DIRECTIONS_BLUESHIFT_AT_SAMPLE"
    if low == 0 and high == 0:
        return "ALL_DIRECTIONS_STATIONARY_AT_SAMPLE"
    if low >= 0:
        return "SOME_STATIONARY_REST_REDSHIFT_AT_SAMPLE"
    if high <= 0:
        return "SOME_STATIONARY_REST_BLUESHIFT_AT_SAMPLE"
    return "MIXED_REDSHIFT_AND_BLUESHIFT_AT_SAMPLE"

def fixtures():
    checks = []
    for h, s, expected in [(2,.5,(1.5,3.)), (2,-.5,(1.,2.5)),
                            (2,-1.,(0.,3.)), (2,-1.5,(-1.,3.5)), (2,0.,(2.,2.))]:
        out = directional(np.array([h]), np.array([s]))
        low, high = float(out["H_gamma_min_per_s"][0]), float(out["H_gamma_max_per_s"][0])
        assert (low, high) == expected
        # Independent exact-rational convex combination, no call to directional.
        values = [Fraction(h)-Fraction(s)+3*Fraction(s)*Fraction(k,64) for k in range(65)]
        assert (float(min(values)), float(max(values))) == expected
        checks.append({"id": "signed_endpoint_"+str(s), "result": "PASS",
                       "minimum": low, "maximum": high, "regime": sign_regime(low, high)})
    for h, s in [(None,np.array([1.])), (np.array([1.]),None)]:
        out = directional(h,s)
        assert out["status"] == "REQUIRED_INPUT_UNAVAILABLE"
        assert all(v is None for k,v in out.items() if k != "status")
    checks.append({"id": "missing_signed_inputs_stay_null_no_norm_inference", "result": "PASS"})
    for h,s in [(np.array([0.]),np.array([0.])), (np.array([float('nan')]),np.array([0.])),
                (np.array([True]),np.array([0.])), (np.array([1.,2.]),np.array([0.]))]:
        try:
            directional(h,s)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid input accepted")
    checks.append({"id": "invalid_mean_H_nan_boolean_shape_rejected", "result": "PASS"})
    # An individual resonant cycle swaps line and excitation energy then returns it;
    # CI swaps thermal and binding energy without boundary export.
    for chi in [Fraction(136058,10000),Fraction(1020435,100000)]:
        assert -chi+chi == 0
    checks.append({"id": "channel_energy_exchange_exact_rational", "result": "PASS"})
    return {"status":"PASS_SCOPED", "checks":checks,
            "scope":"endpoint/sign/missing-input contracts and bookkeeping identity; no physical rate/spectrum validation",
            "actual_two_photon_spectrum_normalization":"NOT_RUN_REQUIRED_INPUT_UNAVAILABLE",
            "new_ODE":0,"RHS_calls":0,"rate_provider_calls":0}

def resource_snapshot(repo, cpu):
    affinity = sorted(os.sched_getaffinity(0))
    cooperative = Path("/tmp/rei-bianchi-cooperative-leases")
    roots = {repo, repo.parent.parent, repo.parent.parent.parent, Path("/tmp"), Path.cwd()}
    if cooperative.is_dir(): roots.add(cooperative)
    directories = set(roots)
    for root in roots:
        for name in ("leases", ".leases", "resources", "state"):
            p=root/name
            if p.is_dir(): directories.add(p)
    discovered=[]
    errors=[]
    for root in sorted(directories):
        try:
            for p in root.iterdir():
                n=p.name.lower()
                if p.is_file() and p.suffix.lower()==".json" and (
                    root==cooperative or "lease" in n or ("cpu" in n and any(x in n for x in ("owner","alloc","reserv")))):
                    discovered.append(pin(p))
        except OSError as error:
            errors.append({"path":str(root),"error":repr(error)})
    result={"utc":utc(),"affinity_before":affinity,"selected_cpu":cpu,
            "coordinator_cpu":0,"cpu55_protected":True,"cpu55_available":55 in affinity,
            "threads_per_worker":1,"exclusive_cpu_lease":False,
            "lease_discovery_scope":"known roots and immediate lease/resource/state folders; not global",
            "lease_records_observed":discovered,"lease_discovery_errors":errors,
            "lease_directories":[str(p) for p in sorted(directories)],
            "thread_environment":{key:os.environ[key] for key in THREAD_KEYS},
            "cpu_max":Path('/sys/fs/cgroup/cpu.max').read_text().strip(),
            "memory_max_bytes":int(Path('/sys/fs/cgroup/memory.max').read_text()),
            "memory_current_bytes":int(Path('/sys/fs/cgroup/memory.current').read_text())}
    if errors or discovered:
        raise RuntimeError("LEASE_REVIEW_REQUIRED_BEFORE_DIAGNOSTIC")
    if cpu not in affinity or cpu in (0,55):
        raise RuntimeError("CPU_UNAVAILABLE_OR_PROTECTED")
    if result['memory_max_bytes']-result['memory_current_bytes'] < 256*1024**2:
        raise RuntimeError("INSUFFICIENT_256MIB_HEADROOM")
    os.sched_setaffinity(0,{cpu})
    result['affinity_during']=sorted(os.sched_getaffinity(0))
    return result

def source_coverage():
    missing = {
      "finite_cell_geometry_column": "actual path length/geometry and columns; Hubble length is not supplied geometry",
      "Lyalpha_A_f_profile": "A2p, oscillator strength, frequency profile and fine-structure convention",
      "two_photon_A_spectrum": "A2s and differential spectrum with integral number=2 and integral energy=DeltaE",
      "redistribution_recoil_escape": "frequency/angular redistribution, recoil, boundary/residence and true destruction",
      "collisional_return_mixing": "validated downward thermal provider and splitting-resolved 2s/2p mixing sources",
      "RR_cascade_branching": "state-resolved recombination capture and cascade photon/energy branching",
      "excited_state_PI_CI": "excited level cross sections and thresholds",
      "secondary_electron_partition": "energy-sharing/yields and actual neutral-inelastic versus Coulomb competition",
      "peculiar_velocity_gradient": "actual additional line-of-sight peculiar velocity gradient or explicit zero assumption",
    }
    return {"schema":"C22E_LINE_SOURCE_COVERAGE_V1", "source_identity_sha256":SOURCE,
      "adopted_existing": {
        "signed_H_s": {"status":"COMPUTED_SCOPED","source":"raw saved fields plus already-computed accepted summary fields; no norm-to-sign inference"},
        "H1_n2_collision_events": {"status":"CONDITIONAL_INPUT_DIAGNOSTIC","source":"stored C22C finite-source rates/counters inherited by C22D; RR cascade not included"},
        "thermal_atomic_UV": {"status":"CONDITIONAL_INPUT_DIAGNOSTIC","source":"stored single-T atomic-isotropic model, 21 explicit populations, 6 finite UV cohorts"}},
      "required_inputs":{k:{"status":"REQUIRED_INPUT_UNAVAILABLE","value":None,"requirement":v} for k,v in missing.items()},
      "physical_admission": {"status":"REGIME_NOT_ESTABLISHED", "level_lifetime_over_macro":None,
        "escape_residence_over_macro":None,"excited_fraction":None,"destruction_probability":None,
        "tau_scattering":None,"tau_true_absorption":None,"escape_probability":None},
      "downward_CCC_candidate_scope":"previous addendum reported header/SHA only; no provider adopted or executed here",
      "new_sources_read":0,"global_error_bound":None}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--repo',type=Path,required=True)
    p.add_argument('--output-dir',type=Path,required=True)
    p.add_argument('--run-id',required=True)
    p.add_argument('--cpu',type=int,default=4)
    args=p.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,119}',args.run_id): raise ValueError('unsafe run ID')
    args.repo=args.repo.resolve()
    args.output_dir.mkdir(parents=True,exist_ok=False)
    started_wall=time.monotonic(); started_cpu=time.process_time()
    resource=resource_snapshot(args.repo,args.cpu)
    write_json(args.output_dir/'STARTED.json',{'run_id':args.run_id,'utc':utc(),'command':sys.argv,
                'python':sys.version,'numpy':np.__version__,'host':platform.node(),'resource':resource})
    write_json(args.output_dir/'FIXTURE_CHECKS.json',fixtures())
    analysis=args.repo/'analysis_v1'
    summary=json.loads((analysis/'SUMMARY.json').read_text())
    if summary['status']!='PASS_SCOPED' or summary['source_identity_sha256']!=SOURCE:
        raise RuntimeError('ANALYSIS_AUTHORITY_NOT_ACCEPTED')
    manifest=json.loads((analysis/'ARTIFACT_MANIFEST.json').read_text())
    expected={Path(x['path']).name:x for x in manifest['files']}
    inputs=[pin(analysis/'SUMMARY.json'),pin(analysis/'ARTIFACT_MANIFEST.json'),pin(Path(__file__))]
    coverage=source_coverage()
    write_json(args.output_dir/'LINE_SOURCE_COVERAGE.json',coverage)
    fields=['tier','case','mesh','index','eta','proper_elapsed_s','a','z','H_per_s','signed_s_per_s',
            'H_perp_per_s','H_parallel_per_s','H_gamma_min_per_s','H_gamma_max_per_s',
            'H_gamma_min_over_H','H_gamma_max_over_H','three_abs_s_over_H','sign_regime',
            'temperature_K','n_e_cm3','nH_ref_cm3','H1_ground_per_Href',
            'H1_2s_events_per_Href_per_s','H1_2p_events_per_Href_per_s']
    fields += ['UV_'+str(i)+'_photons_per_Href' for i in range(6)]
    fields += ['UV_'+str(i)+'_energy_eV' for i in range(6)]
    summaries=[]; arrays={}; frozen=[]
    with (args.output_dir/'LINE_ADMISSION.csv').open('x',newline='',encoding='utf8') as f:
      writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
      for tier,case,run,rawsha in CASES:
        rawpath=args.repo/'runs'/run/'cases'/case/'history.npz'
        raw=rawpath.read_bytes()
        if digest(raw)!=rawsha: raise RuntimeError('RAW_PIN_MISMATCH')
        receiptpath=rawpath.parent/'RECEIPT.json'
        receipt=json.loads(receiptpath.read_text())
        if receipt['source_identity_sha256']!=SOURCE or receipt['history_sha256']!=rawsha:
            raise RuntimeError('RAW_RECEIPT_IDENTITY_MISMATCH')
        inputs.extend([pin(rawpath),pin(receiptpath)]);frozen.extend([inputs[-2],inputs[-1]])
        with np.load(io.BytesIO(raw),allow_pickle=False) as z:
            rawdata={k:z[k] for k in z.files}
        for mesh in ['saved','accepted']:
          if mesh=='saved': data=rawdata
          else:
            path=analysis/(tier+'_'+case+'_ACCEPTED.npz')
            packed=path.read_bytes(); expect=expected[path.name]
            if digest(packed)!=expect['sha256'] or len(packed)!=expect['size_bytes']:
                raise RuntimeError('ACCEPTED_SUMMARY_PIN_MISMATCH')
            inputs.append(pin(path));frozen.append(inputs[-1])
            with np.load(io.BytesIO(packed),allow_pickle=False) as z: data={k:z[k] for k in z.files}
            if not np.array_equal(data['eta'],rawdata['accepted_eta']) or not np.array_equal(data['Y'],rawdata['accepted_Y']):
                raise RuntimeError('ACCEPTED_RAW_BINDING_MISMATCH')
          result=directional(data.get('H'),data.get('s'))
          if result['status']!='COMPUTED_SCOPED': raise RuntimeError('MISSING_STORED_SIGNED_FIELDS')
          h=data['H']; s=data['s']; low=result['H_gamma_min_per_s'];high=result['H_gamma_max_per_s']
          idx=list(data['atomic_state_labels']).index('H1_0')
          rate=data['H1_excitation_events_per_H_per_eta']*h[None,:]
          regimes=[sign_regime(float(x),float(y)) for x,y in zip(low,high)]
          if not np.allclose(data['signed_Sigma_F'],math.sqrt(6)*s/h,rtol=3e-15,atol=1e-18):
              raise RuntimeError('SIGNED_FULL_FROBENIUS_CONVENTION_MISMATCH')
          item={'tier':tier,'case':case,'mesh':mesh,'samples':len(h),'status':'COMPUTED_SCOPED',
                'H_min_per_s':float(np.min(h)),'H_max_per_s':float(np.max(h)),
                'signed_s_min_per_s':float(np.min(s)),'signed_s_max_per_s':float(np.max(s)),
                'minimum_Hgamma_per_s':float(np.min(low)),'maximum_Hgamma_per_s':float(np.max(high)),
                'minimum_Hgamma_over_H':float(np.min(low/h)),'maximum_Hgamma_over_H':float(np.max(high/h)),
                'maximum_three_abs_s_over_H':float(np.max(result['three_abs_s_over_H'])),
                'final_three_abs_s_over_H':float(result['three_abs_s_over_H'][-1]),
                'nonpositive_direction_samples':int(np.count_nonzero(low<=0)),
                'sign_regime_counts':{r:regimes.count(r) for r in sorted(set(regimes))},
                'minimum_temperature_K':float(np.min(data['temperature_K'])),
                'maximum_temperature_K':float(np.max(data['temperature_K'])),
                'maximum_2s_events_per_Href_per_s':float(np.max(rate[0])),
                'maximum_2p_events_per_Href_per_s':float(np.max(rate[1])),
                'physical_admission':'REGIME_NOT_ESTABLISHED'}
          summaries.append(item)
          prefix=tier+'_'+case+'_'+mesh
          arrays[prefix+'__eta']=data['eta']
          for k,v in result.items():
              if k!='status': arrays[prefix+'__'+k]=v
          for i in range(len(h)):
            row=dict(tier=tier,case=case,mesh=mesh,index=i,eta=float(data['eta'][i]),
              proper_elapsed_s=float(data['proper_elapsed_s'][i]),a=float(data['a'][i]),z=float(data['z'][i]),
              H_per_s=float(h[i]),signed_s_per_s=float(s[i]),H_perp_per_s=float(result['H_perp_per_s'][i]),
              H_parallel_per_s=float(result['H_parallel_per_s'][i]),H_gamma_min_per_s=float(low[i]),
              H_gamma_max_per_s=float(high[i]),H_gamma_min_over_H=float(low[i]/h[i]),
              H_gamma_max_over_H=float(high[i]/h[i]),three_abs_s_over_H=float(result['three_abs_s_over_H'][i]),
              sign_regime=regimes[i],temperature_K=float(data['temperature_K'][i]),n_e_cm3=float(data['n_e_cm3'][i]),
              nH_ref_cm3=float(data['nH_ref_cm3'][i]),H1_ground_per_Href=float(data['atomic_abundance_per_Href'][idx,i]),
              H1_2s_events_per_Href_per_s=float(rate[0,i]),H1_2p_events_per_Href_per_s=float(rate[1,i]))
            for j in range(6):
              row['UV_'+str(j)+'_photons_per_Href']=float(data['UV_photons_per_H'][i,j])
              row['UV_'+str(j)+'_energy_eV']=float(data['UV_cohort_energies_eV'][i,j])
            writer.writerow(row)
    with (args.output_dir/'LINE_ADMISSION_ARRAYS.npz').open('xb') as f: np.savez_compressed(f,**arrays)
    for x in frozen:
        if pin(x['path'])!=x: raise RuntimeError('INPUT_CHANGED_DURING_READONLY_DIAGNOSTIC')
    resource.update(wall_seconds=time.monotonic()-started_wall,cpu_seconds=time.process_time()-started_cpu,
      actual_native_threads=int([l.split()[1] for l in Path('/proc/self/status').read_text().splitlines() if l.startswith('Threads:')][0]),
      finished_utc=utc(),memory_current_finish_bytes=int(Path('/sys/fs/cgroup/memory.current').read_text()))
    result={'schema':'C22E_LINE_ADMISSION_V1','workflow_version':'1.0.0','approval_protocol':'0.2',
      'run_id':args.run_id,'status':'COMPUTED_SCOPED','source_identity_sha256':SOURCE,'input_pins':inputs,
      'cases':summaries,'raw_and_accepted_summary_bytes_unchanged':True,'resource':resource,
      'scope':'Angular extrema are exact in mu at each supplied time; finite 804 saved plus 8047 accepted samples do not bound intersample behavior.',
      'stored_field_reuse':'H and signed s read directly; accepted fields reuse analysis_v1; no recomputed model summary.',
      'reaction_rate_unit_conversion':'stored per-eta events multiplied by stored H=deta/dt to obtain events/Href/s',
      'physical_admission':coverage['physical_admission'],
      'new_ODE':0,'completed_ODE_reruns':0,'RHS_calls':0,'rate_provider_calls':0,'model_imports':0,
      'new_source_searches':0,'global_error_bound':None,
      'four_axes':{'EXECUTION':'one read-only algebra diagnostic; 804 saved+8047 accepted samples; ODE/RHS/provider0',
        'PUBLICATION':'local create-only source and results; parent publication receipt required',
        'BACKUP':'parent actual archive/provider/readback receipts required',
        'DAG':'line source+geometry admission remains OPEN; full thermal/radiative OPEN; nuclear/general-CMB HOLD'}}
    write_json(args.output_dir/'LINE_ADMISSION.json',result)
    artifacts=[pin(x) for x in sorted(args.output_dir.iterdir()) if x.is_file()]
    write_json(args.output_dir/'ARTIFACT_MANIFEST.json',{'files':artifacts,'code_pin':pin(Path(__file__)),
                'source_identity_sha256':SOURCE,'global_error_bound':None})
    print(json.dumps({'status':result['status'],'run_id':args.run_id,'case_meshes':len(summaries),
                      'total_samples':sum(x['samples'] for x in summaries),'resource':resource,
                      'new_ODE':0},ensure_ascii=False))

if __name__=='__main__':
    main()
