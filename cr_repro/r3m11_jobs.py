"""Create a bounded single-b run matrix and record one explicitly chosen job.

This program never launches the whole matrix, a b-grid, or another energy.
Existing numerical source and the historical local return are not rewritten.
"""
from __future__ import annotations
import argparse
import copy
import datetime as dt
import importlib.metadata as metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

from .r3m11 import file_sha, source_digest, audit_saved
from .util import atomic_json


def build_matrix() -> dict:
    t=dict(energy_keV_per_u=100.,b=2.,backend='auto',
        grid=dict(xlim=[-30,40],ylim=[-30,30],zlim=[-30,90],dx=.4),
        dt=.05,z_start=-30.,z_stop=60.,absorber_width=4.,absorber_power=.125,
        absorber_reference_dt=.05,initial_state='imag_time',imag_dt=.05,imag_steps=300,
        project_nmax=3,capture_plane=30.,checkpoint_stride=100,projection_slab_x=2)
    a=dict(energy_keV_per_u=100.,b=2.,zmax=30.,dt=.05,ns=12,np=8,
        alpha_min=.001,alpha_max=100.,pmin=.001,pmax=10.,eps_max=5.)
    jobs={}
    def add(name,lane,cfg,changes,question):
        c=copy.deepcopy(cfg)
        for k,v in changes.items():
            if k=='dx':c['grid']['dx']=v
            else:c[k]=v
        jobs[name]=dict(lane=lane,config=c,question=question,scientific_admission=False)
    add('tdl_cap_base','tdl',t,{},'New symmetric fixed-CAP reference. Not the historical baseline.')
    add('tdl_dt025','tdl',t,dict(dt=.025),'Halve physical step with identical CAP function.')
    add('tdl_dt0125','tdl',t,dict(dt=.0125),'Second step refinement at fixed CAP.')
    add('tdl_imag025','tdl',t,dict(imag_dt=.025,imag_steps=600),'Imaginary-time step at equal preparation duration.')
    add('tdl_imag025_long','tdl',t,dict(imag_dt=.025,imag_steps=1200),'Preparation duration; compare against tdl_imag025.')
    add('tdl_dx03125','tdl',t,dict(dx=.3125),'Grid refinement only at fixed preparation and CAP parameters.')
    add('tdl_dx025','tdl',t,dict(dx=.25),'Grid refinement only; no outcome-based potential adjustment.')
    add('tdl_dx020','tdl',t,dict(dx=.2),'Conditional later grid refinement, not automatically executed.')
    add('tdl_plane25','tdl',t,dict(capture_plane=25.),'Postprocess-only change; prefer reusing saved state rather than propagation.')
    add('aocc_base','aocc',a,{},'Preserved s+p one-electron AOCC baseline.')
    add('aocc_dt025','aocc',a,dict(dt=.025),'Production-basis time refinement only.')
    add('aocc_radial_only','aocc',a,dict(ns=16,np=12),'Radial count only; same exponent endpoints and energy cutoff.')
    add('aocc_exponent_only','aocc',a,dict(alpha_max=1000.),'s-exponent upper endpoint only; fixed counts.')
    add('aocc_window_only','aocc',a,dict(eps_max=10.),'Positive pseudostate energy window only; same primitive basis.')
    return jobs


def write_matrix(destination: Path) -> dict:
    destination=Path(destination)
    destination.mkdir(parents=True,exist_ok=False)
    jobs=build_matrix()
    for name,job in jobs.items():
        atomic_json(destination/f'{name}.json',job['config'])
    out=dict(schema='R3M11_ONE_ENERGY_SINGLE_B_MATRIX_V1',jobs=jobs,
        bgrid_allowed=False,threshold_policy='Retain parent 1% screening; no automatic admission.',
        recommended_order=['audit saved baseline and dx states first',
          'tdl_cap_base','tdl_dt025','tdl_dt0125','tdl_imag025','tdl_imag025_long',
          'tdl_dx03125','tdl_dx025','aocc_base','aocc_dt025','aocc_radial_only','aocc_exponent_only'],
        next_rule='Inspect results before additional jobs; do not infer all-bound or continuum from finite spans.')
    atomic_json(destination/'MATRIX.json',out)
    return out


def environment() -> dict:
    versions={}
    for name in ['numpy','scipy','pytest','cupy-cuda12x','cupy-cuda13x']:
        try:versions[name]=metadata.version(name)
        except metadata.PackageNotFoundError:pass
    return dict(python=sys.version,executable=sys.executable,platform=platform.platform(),
                versions=versions,numerical_source_sha256=source_digest(),
                vendor_gaussian_sha256=file_sha(Path(__file__).resolve().parents[1]/'vendor_w1r/gaussian_cartesian.py'))


def run_one(matrix_dir: Path,name: str,out: Path,max_steps: int|None=None) -> dict:
    matrix_dir=Path(matrix_dir);out=Path(out)
    matrix=json.loads((matrix_dir/'MATRIX.json').read_text())
    if name not in matrix['jobs']:raise ValueError('unknown job')
    job=matrix['jobs'][name];cfg=matrix_dir/f'{name}.json'
    if json.loads(cfg.read_text())!=job['config']:raise ValueError('config/matrix changed independently')
    if job['lane']=='aocc' and (out/'result.json').exists():
        raise FileExistsError('refuse to overwrite completed AOCC run')
    if job['lane']=='aocc' and max_steps is not None:
        raise ValueError('AOCC has no verified restart loader; --max-steps applies only to TDL')
    out.mkdir(parents=True,exist_ok=True)
    attempt=out/'attempts'/dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')
    attempt.mkdir(parents=True,exist_ok=False)
    command=[sys.executable,'-m','cr_repro.r3m11' if job['lane']=='tdl' else 'cr_repro.cli',
        'run' if job['lane']=='tdl' else 'aocc','--config',str(cfg.resolve()),'--out',str(out.resolve())]
    if max_steps is not None:command+=['--max-steps',str(max_steps)]
    atomic_json(attempt/'config.json',job['config']);atomic_json(attempt/'environment.json',environment())
    tic=time.monotonic()
    with (attempt/'stdout.log').open('wb') as stdout,(attempt/'stderr.log').open('wb') as stderr:
        proc=subprocess.run(command,stdout=stdout,stderr=stderr,check=False)
    receipt=dict(schema='R3M11_LOCAL_ATTEMPT_V1',name=name,lane=job['lane'],command=command,
        returncode=proc.returncode,seconds=time.monotonic()-tic,source_digest=source_digest(),
        config_sha256=file_sha(cfg),production_admitted=False,bgrid_allowed=False)
    for f in ['state.json','state.npy','result.json','r3m11_checkpoint_seal.json']:
        if (out/f).is_file():receipt.setdefault('output_files',{})[f]=dict(bytes=(out/f).stat().st_size,sha256=file_sha(out/f))
    atomic_json(attempt/'receipt.json',receipt)
    if proc.returncode:raise RuntimeError(f'run failed with {proc.returncode}; see {attempt}')
    return receipt


def audit_return(repo: Path,return_root: Path,out: Path,names: list[str]) -> dict:
    """Use Git-owned external SHA authority; do not trust just the archive filename."""
    repo=Path(repo);return_root=Path(return_root);out=Path(out)
    authority=json.loads((repo/'provenance/RELEASE_ASSETS.json').read_text())
    expected={Path(x['path']).parent.name:x for x in authority['omitted_from_git']}
    # Different archive wrappers are tolerated, not guessed: require one match.
    candidates=[return_root] if (return_root/'runs').is_dir() else []
    if not candidates:
        candidates=sorted(set(p.parent.parent for p in return_root.rglob('tdl_baseline_retry/state.json')))
        candidates=[p.parent if p.name=='runs' else p for p in candidates]
    if len(candidates)!=1:raise ValueError('provide the unique extracted return directory containing runs/')
    root=candidates[0];out.mkdir(parents=True,exist_ok=False)
    summary={}
    for name in names:
        if name not in expected:raise ValueError(f'no source-owned state hash for {name}')
        state=root/'runs'/name/'state.npy'
        if state.stat().st_size!=expected[name]['bytes']:raise ValueError(f'{name}: state size mismatch')
        result=audit_saved(root/'runs'/name,nmax=3,slab_x=2,expected_state_sha256=expected[name]['sha256'])
        atomic_json(out/f'{name}_gram.json',result);summary[name]=result['analysis']
    result=dict(schema='R3M11_POSTPROCESS_RETURN_V1',source_authority_sha256=file_sha(repo/'provenance/RELEASE_ASSETS.json'),
        source_archive_expected_sha256=authority['archive_sha256'],runs=summary,
        bgrid_allowed=False,dynamics_rerun=False,physical_rate_evaluated=False)
    atomic_json(out/'SUMMARY.json',result)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);s=p.add_subparsers(dest='command',required=True)
    g=s.add_parser('generate');g.add_argument('--out',required=True)
    r=s.add_parser('run-one');r.add_argument('--matrix',required=True);r.add_argument('--name',required=True);r.add_argument('--out',required=True);r.add_argument('--max-steps',type=int)
    a=s.add_parser('audit-return');a.add_argument('--repo',default='.');a.add_argument('--return-root',required=True);a.add_argument('--out',required=True);a.add_argument('--names',nargs='+',default=['tdl_baseline_retry','tdl_dx03125'])
    args=p.parse_args()
    if args.command=='generate':o=write_matrix(Path(args.out));print(json.dumps(dict(jobs=len(o['jobs']),bgrid_allowed=False)))
    elif args.command=='run-one':print(json.dumps(run_one(Path(args.matrix),args.name,Path(args.out),args.max_steps),indent=2))
    else:print(json.dumps(audit_return(Path(args.repo),Path(args.return_root),Path(args.out),args.names),indent=2))

if __name__=='__main__':main()
