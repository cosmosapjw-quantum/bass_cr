"""Explicit opt-in successor: freeze intent on CPU; execute only by exact SHA.

Examples from repository root:
  python -m scripts.r3m24_cross_window freeze --contract /fresh/contract.json
  python -m scripts.r3m24_cross_window design --out /fresh/design.json
  python -m scripts.r3m24_cross_window run --contract /fresh/contract.json \
      --approve-sha256 <printed-contract-sha> --out /fresh/attempt
No command starts a new full collision. Historical entrypoints remain unchanged.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import platform
import json
import math
from pathlib import Path
import subprocess

import numpy as np

from .r3m24_guard import file_sha, object_sha, publish_json, read_json, safe_path
from .r3m24_execution import execute
from .r3m24_gpu import GPUBackend
from .r3m24_metrics import discriminator_design, state_budget

BASE='381b00e800bf1e7e2a78b5c0e9a56cbed5db56a5'
FROZEN='581ff84930bb862efafdfec5d39d5b25aebf9297ce7ce45f833a5abe125b2a5b'
ROOT=Path(__file__).resolve().parents[1]
CONFIG='configs/r3m17/B2.json'
SELECTION='results/R3M20_N1/windows/SELECTION.json'
STRICT='results/R3M22/CPU_ORACLE_STRICT.json'
SCIENTIFIC_SETTINGS=dict(inner_budget=1e-14,tight_budget=1e-15,
                         calibration_limit=2.103970853068276e-14,max_basis=10)
CORE_KEYS=('config','sources','runtime_identity','probe','windows','scope','scientific_settings')


def runtime_identity():
    packages={}
    for name in ('scipy','cupy','cupy-cuda11x','cupy-cuda12x','cupy-cuda13x'):
        try:
            packages[name]=importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            pass
    return dict(python=platform.python_version(),numpy=np.__version__,packages=packages)


def computation_key(plan):
    return object_sha({k:plan[k] for k in CORE_KEYS})


def canonical_specs(cfg,selection):
    if cfg.get('backend')!='cupy': raise ValueError('no implicit CPU fallback')
    shape=[]
    for axis in ('xlim','ylim','zlim'):
        n=(cfg['grid'][axis][1]-cfg['grid'][axis][0])/cfg['grid']['dx']
        if not math.isfinite(n) or n < 2 or not math.isclose(n,round(n),rel_tol=0,abs_tol=1e-10):
            raise ValueError('positive integer grid extent required')
        shape.append(round(n))
    dt=selection['actual_dt_au']; nstep=selection['nstep']
    if (not math.isfinite(dt) or dt <= 0 or type(nstep) is not int or nstep <= 0 or
            not math.isfinite(cfg['dt']) or cfg['dt'] <= 0 or
            math.ceil(nstep*dt/cfg['dt'])!=nstep):
        raise ValueError('actual/requested time discretization mismatch')
    initial=cfg['z_start']/(cfg['z_stop']-cfg['z_start'])*nstep*dt
    enriched=dict(cfg,_r3m11_controls='FIXED_CAP_SYMMETRIC_V1',_r3m11_source_digest=FROZEN)
    cfg_hash=hashlib.sha256(json.dumps(enriched,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    specs=[dict(row,nstep=nstep,config_hash=cfg_hash,source_digest=FROZEN,shape=shape,
                dtype=np.dtype('complex128').str,backend='cupy',actual_dt_au=dt,initial_time_au=initial)
           for row in selection['windows']]
    if [s['label'] for s in specs]!=['incoming','closest','outgoing']:
        raise ValueError('unexpected selected windows')
    return specs


def validate_contract(plan):
    # Pin the actual config handed to the runner, not just an independent
    # config-hash string inside a checkpoint descriptor.
    if (plan.get('base_commit')!=BASE or Path(plan['root']).resolve()!=ROOT or
            plan.get('scope')!='REFERENCE_FOR_STRANG' or plan.get('production_admission') is not False or
            plan.get('scientific_settings')!=SCIENTIFIC_SETTINGS or
            plan.get('runtime_identity')!=runtime_identity()):
        raise ValueError('contract base/scope/scientific settings mismatch')
    cfg=read_json(ROOT/CONFIG); selection=read_json(ROOT/SELECTION)
    if (selection['B2_config_sha256']!=file_sha(ROOT/CONFIG) or plan['config']!=cfg or
            read_json(ROOT/STRICT).get('all_oracle_resolved') is not True):
        raise ValueError('runner config/selection/strict CPU gate mismatch')
    specs=canonical_specs(cfg,selection)
    if plan['probe']!=specs[0] or plan['windows']!=specs[1:]:
        raise ValueError('run descriptor differs from the authoritative selection/config')
    limits=plan['limits']
    for key,maximum in [('kinetic_matvecs',5000),('total_seconds',7200),('window_seconds',1800)]:
        value=limits[key]
        if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or not 0 < value <= maximum:
            raise ValueError('resource cap exceeds successor contract ceiling')
    if type(limits['kinetic_matvecs']) is not int:
        raise ValueError('integer matvec cap required')
    if source_snapshot()!=plan['sources'] or computation_key(plan)!=plan['computation_key']:
        raise ValueError('source/computation key mismatch')



def _git(*args):
    proc=subprocess.run(['git','-C',str(ROOT),*args],capture_output=True,check=True)
    return proc.stdout


def source_snapshot():
    """Read-only Git base binding plus all new successor source bytes."""
    entries=_git('ls-tree','-rz',BASE,'--','cr_repro','scripts').split(b'\0')
    sources={}
    for entry in entries:
        if not entry: continue
        meta,name=entry.split(b'\t',1); path=name.decode('utf-8')
        if not path.endswith('.py'): continue
        raw=safe_path(ROOT/path).read_bytes()
        expected=meta.split()[2].decode()
        actual=hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()
        if actual!=expected: raise ValueError(f'frozen base source changed: {path}')
        sources[path]=hashlib.sha256(raw).hexdigest()
    if not sources: raise ValueError('base source tree missing')
    for path in (ROOT/'scripts').glob('r3m24_*.py'):
        sources[str(path.relative_to(ROOT))]=file_sha(path)
    for path in (CONFIG,SELECTION,STRICT): sources[path]=file_sha(ROOT/path)
    return sources


def freeze(reuse: list[str]) -> dict:
    sources=source_snapshot(); cfg=read_json(ROOT/CONFIG); selection=read_json(ROOT/SELECTION)
    if read_json(ROOT/STRICT).get('all_oracle_resolved') is not True:
        raise ValueError('strict historical CPU oracle is not admitted')
    if selection['B2_config_sha256']!=file_sha(ROOT/CONFIG):
        raise ValueError('selection/config byte identity mismatch')
    specs=canonical_specs(cfg,selection)
    for spec in specs:
        manifest=read_json(Path(spec['generation_directory'])/'r3m17_generation_manifest.json',spec['manifest_sha256'])
        if manifest.get('config_hash')!=spec['config_hash'] or manifest.get('done')!=spec['done']:
            raise ValueError('generation config/step mismatch')
    plan=dict(schema='BASS_CR_R3M24_SAFE_RESTART_V1',root=str(ROOT),base_commit=BASE,
              config=cfg,sources=sources,runtime_identity=runtime_identity(),probe=specs[0],windows=specs[1:],reuse={},
              scope='REFERENCE_FOR_STRANG',production_admission=False,
              limits=dict(kinetic_matvecs=5000,total_seconds=7200,window_seconds=1800),
              scientific_settings=SCIENTIFIC_SETTINGS.copy(),
              execution_policy='EXPLICIT_CONTRACT_SHA_ONLY_NO_AUTOMATIC_DISPATCH',
              git_provenance=dict(head=_git('rev-parse','HEAD').decode().strip(),
                                  status_porcelain=_git('status','--porcelain').decode()))
    plan['computation_key']=computation_key(plan)
    for directory in reuse:
        root=safe_path(directory); manifest=read_json(root/'MANIFEST.json')
        label=manifest['label']
        if label in plan['reuse']: raise ValueError('duplicate reuse label')
        plan['reuse'][label]=dict(directory=str(root),manifest_sha256=file_sha(root/'MANIFEST.json'))
    return plan


def design() -> dict:
    cfg=read_json(ROOT/CONFIG); selection=read_json(ROOT/SELECTION)
    result=discriminator_design(selection['actual_dt_au'],selection['nstep'],cfg['z_start'],cfg['z_stop'],
                                selection['windows'][1]['done'])
    data=read_json(ROOT/'results/R3M18/B_TEMPORAL_ANALYSIS.json')['rows']['B2']
    result['reference_for_target_Q']={q:dict(probability=data[q],relative_budget=.001,
        absolute_probability_budget=.001*data[q],sufficient_state_budget=state_budget(data[q],.001*data[q]),
        semantics='ONE_ERROR_COMPONENT_ONLY_NOT_CLOSED_GATE') for q in ('P1','P2','P3')}
    result['canonical_node']='N1_TDL_PRODUCTION_H_CF4_SELF_SCALED_REFERENCE_AND_TIME_REFINEMENT'
    result['automatic_execution']=False
    return result


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('freeze'); p.add_argument('--contract',type=Path,required=True)
    p.add_argument('--reuse-window',action='append',default=[])
    p=sub.add_parser('design'); p.add_argument('--out',type=Path,required=True)
    p=sub.add_parser('run'); p.add_argument('--contract',type=Path,required=True)
    p.add_argument('--approve-sha256',required=True); p.add_argument('--out',type=Path,required=True)
    args=parser.parse_args(argv)
    if args.command=='freeze':
        plan=freeze(args.reuse_window); publish_json(args.contract,plan)
        print(json.dumps(dict(contract=str(args.contract),sha256=file_sha(args.contract),gpu_work=0)))
    elif args.command=='design':
        publish_json(args.out,design()); print('DESIGN_ONLY: no propagation executed')
    else:
        plan=read_json(args.contract,args.approve_sha256)
        if Path(plan['root']).resolve()!=ROOT: raise ValueError('contract repository root changed')
        # Recheck base identity before crossing the GPU boundary, including after
        # an explicit approved contract was frozen in a dirty local workspace.
        validate_contract(plan)
        summary=execute(plan,args.out,GPUBackend)
        print(json.dumps(dict(status=summary['status'],work=summary['work'],production_admission=False)))


if __name__=='__main__':
    main()
