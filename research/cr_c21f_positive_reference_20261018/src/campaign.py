"""Failure-isolated C21F execution of the unchanged C21E discrete transaction.

Completed rows remain usable if another independent comparator rejects. Every
failure is durable, the overall status stays partial, and no numeric failure
changes tolerances, grid, microphysical kernel or native implementation.
"""
from __future__ import annotations
from dataclasses import asdict
from pathlib import Path
import argparse
import json
import math
import os
import time
import traceback
import numpy as np
import bootstrap
from positive_reference import run_reference
from run_experiment import (Fixture,make_fixture,fixture_from_native_source,
                            native_point_parity,run_history,write_json,
                            run_reference as number_reference)
from event_coupler import (MODES,ZeroMicro,ManufacturedMicro,DomainError,
                           StepRejected,ProviderFailure)
from native_micro import NativeMicro


def error_record(exc):
    if isinstance(exc,ProviderFailure):kind='PROVIDER_OR_PROTOCOL_FAILURE'
    elif isinstance(exc,StepRejected):kind='NUMERICAL_STEP_REJECTED'
    elif isinstance(exc,DomainError):kind='NUMERICAL_OR_INPUT_DOMAIN_REJECTED'
    else:kind='IMPLEMENTATION_EXCEPTION'
    return {'status':'FAILED','category':kind,'type':type(exc).__name__,
            'error':str(exc),'traceback':traceback.format_exc(),
            'native_accuracy_claim':'NOT_ADMITTED'}


def close_provider(p):
    if p is not None and hasattr(p,'close'):p.close()


def ledger_admission(result):
    """Cumulative cross-check in physical units, not a continuum error bound."""
    checks={'photon_H':(abs(result['number_defect_H']),1e-11),
            'energy_eV_H':(abs(result['energy_defect_eV_H']),1e-9),
            'species_fraction':(max(abs(x) for x in result['species_defect']),1e-10)}
    if any(not math.isfinite(v) or v>limit for v,limit in checks.values()):
        raise StepRejected('CUMULATIVE_LEDGER_ADMISSION '+repr(checks))
    if not all(math.isfinite(v) and v>=0 for v in result['photons']):
        raise StepRejected('OUTPUT_PHOTON_DOMAIN')
    return {key:{'observed':v,'limit':limit} for key,(v,limit) in checks.items()}


def run_matrix(f,cases,provider_factory,out,reference_coordinate='tau',with_reference=True):
    f.validate();out=Path(out)
    if reference_coordinate not in ('tau','number'):raise DomainError('REFERENCE_COORDINATE')
    cases=list(cases)
    if not cases or len(set(cases))!=len(cases):raise DomainError('EMPTY_OR_DUPLICATE_CASES')
    if any(mode not in MODES or not isinstance(n,int) or not 1<=n<=512 for mode,n in cases):
        raise DomainError('MATRIX_CASE_DOMAIN')
    out.mkdir(parents=True,exist_ok=False)
    write_json(out/'fixture.json',asdict(f))
    reference=None;refinfo={'status':'NOT_RUN'};records=[];start=time.monotonic()
    if with_reference:
        p=None;refdir=out/'reference';refdir.mkdir()
        try:
            p=provider_factory(refdir/'process')
            if reference_coordinate=='tau':reference=run_reference(f,p,output=refdir)
            else:reference=number_reference(f,p)
            write_json(out/'radau.json',reference)
            checks=ledger_admission(reference)
            refinfo={'status':'COMPLETED','coordinate':reference_coordinate,'checks':checks}
        except Exception as exc:
            refinfo=error_record(exc);write_json(refdir/'FAILURE.json',refinfo)
            reference=None
        finally:close_provider(p)
    for mode,n in cases:
        directory=out/f'{mode}_{n:04d}';directory.mkdir();p=None;t0=time.monotonic()
        row={'mode':mode,'subdivisions':n,'fixture_sha256':f.digest}
        try:
            p=provider_factory(directory/'process')
            result=run_history(f,n,p,mode,output=directory)
            row.update(status='COMPLETED',result=result,checks=ledger_admission(result))
            if reference is not None:
                delta=np.abs(np.asarray(result['gas'])-reference['gas'])
                row['errors']={'max_fraction':float(delta[:3].max()),
                    'thermal_eV_H':float(delta[3]),
                    'temperature_K':abs(result['temperature_K']-reference['temperature_K']),
                    'normalized_state':float(max(delta[:3].max(),delta[3]/f.gas0[3])),
                    'max_photon_H':float(np.max(abs(np.asarray(result['photons'])-reference['photons']),initial=0))}
            else:row['errors']=None
        except Exception as exc:
            row.update(error_record(exc));write_json(directory/'FAILURE.json',row)
        finally:close_provider(p)
        row['wall_s']=time.monotonic()-t0
        write_json(directory/'OUTCOME.json',row);records.append(row)
    ok=sum(r['status']=='COMPLETED' for r in records)
    complete=ok==len(records) and (not with_reference or refinfo['status']=='COMPLETED')
    summary={'schema':'C21F_FAILURE_ISOLATED_MATRIX_V1','fixture_sha256':f.digest,
             'source_identity':f.source_identity,'reference':refinfo,
             'cases':records,'completed_cases':ok,'requested_cases':len(records),
             'status':'COMPLETE_SCOPED' if complete else 'PARTIAL_WITH_FAILURES',
             'wall_s':time.monotonic()-start,
             'scope':'Identical fixed cohort source and discrete C21E operators; reference variable changed only. No native, source-age or spectral accuracy implied by completion.'}
    write_json(out/'SUMMARY.json',summary)
    return summary


def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--micro',choices=('zero','manufactured','native'),default='manufactured')
    p.add_argument('--native',type=Path)
    p.add_argument('--reference-coordinate',choices=('tau','number'),default='tau')
    p.add_argument('--no-reference',action='store_true')
    p.add_argument('--a0',type=float,default=.09);p.add_argument('--dx',type=float,default=.0001)
    p.add_argument('--opacity-scale',type=float,default=1.)
    p.add_argument('--source',choices=('manufactured3','native-centroid','native-gl8'),default='manufactured3')
    p.add_argument('--source-subdivisions',type=int,default=4)
    p.add_argument('--steps',type=int,nargs='+',default=[8,16,32,64])
    p.add_argument('--modes',choices=tuple(MODES),nargs='+',default=list(MODES))
    p.add_argument('--fixture',type=Path);p.add_argument('--cpu',type=int)
    p.add_argument('--max-native-calls',type=int,default=20000)
    args=p.parse_args(argv)
    needs_native=args.micro=='native' or args.source.startswith('native-')
    if needs_native and (args.native is None or not args.native.is_file()):p.error('native route requires compiled --native')
    if args.cpu is not None:
        if not hasattr(os,'sched_getaffinity') or args.cpu not in os.sched_getaffinity(0):p.error('CPU outside allowed affinity')
        os.sched_setaffinity(0,{args.cpu})
    # Any setup/owner-identity failure blocks this whole input, not only a lane.
    if args.out.exists():p.error('output exists; use a new create-only run path')
    preflight=args.out.with_name(args.out.name+'_preflight')
    preflight.mkdir(parents=True,exist_ok=False)
    try:
        if args.fixture:f=Fixture(**json.loads(args.fixture.read_text())).validate()
        elif args.source.startswith('native-'):
            f=fixture_from_native_source(args.native,args.a0,args.dx,args.source_subdivisions,args.source.split('-')[1],preflight)
        else:f=make_fixture(args.a0,args.dx,args.opacity_scale)
        if args.micro=='native':native_point_parity(args.native,f,preflight)
        def provider(path):
            if args.micro=='native':return NativeMicro([str(args.native.resolve())],path,max_calls=args.max_native_calls)
            return ManufacturedMicro() if args.micro=='manufactured' else ZeroMicro()
        result=run_matrix(f,[(m,n) for m in args.modes for n in args.steps],provider,args.out,
                          args.reference_coordinate,not args.no_reference)
        print(json.dumps({k:result[k] for k in ('status','completed_cases','requested_cases')}))
        return 0 if result['status']=='COMPLETE_SCOPED' else 2
    except Exception as exc:
        write_json(preflight/'FAILURE.json',error_record(exc));raise

if __name__=='__main__':raise SystemExit(main())
