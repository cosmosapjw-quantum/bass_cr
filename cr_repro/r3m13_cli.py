"""Command-line wrapper for the R3M13 preparation-only audit."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import numpy as np

from .r3m13 import build_preparation_configs, phase_aligned_distance, preparation_certificate


def _atomic_text(path: Path, text: str):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(path.name+'.tmp'); tmp.write_text(text,encoding='utf-8'); tmp.replace(path)


def _atomic_json(path: Path, obj):
    _atomic_text(path,json.dumps(obj,indent=2,sort_keys=True,allow_nan=False)+'\n')


def make_configs(base_path: str, out_dir: str):
    base=json.loads(Path(base_path).read_text())
    ref,new=build_preparation_configs(base)
    out=Path(out_dir); out.mkdir(parents=True,exist_ok=False)
    _atomic_json(out/'prep_ref_imag025x1200.json',ref)
    _atomic_json(out/'prep_new_imag0125x2400.json',new)
    _atomic_json(out/'PAIR.json',{'schema':'R3M13_PREPARATION_CONFIG_PAIR_V1',
        'reference':'prep_ref_imag025x1200.json','candidate':'prep_new_imag0125x2400.json',
        'same_total_imaginary_time':30.0,'collision_propagation_run':False,'bgrid_allowed':False})


def prepare_only(config_path: str, out_dir: str):
    from .r3m11 import ControlledTDLRunner, file_sha, source_digest
    from .backend import asnumpy
    from .util import atomic_npy, atomic_json, config_hash
    cfg=json.loads(Path(config_path).read_text())
    out=Path(out_dir); out.mkdir(parents=True,exist_ok=False)
    runner=ControlledTDLRunner(cfg)
    psi,info=runner.relaxed_initial()
    state=out/'initial_state.npy'
    atomic_npy(state,asnumpy(psi)); atomic_json(out/'initial_info.json',info)
    atomic_json(out/'receipt.json',{'schema':'R3M13_PREPARATION_ONLY_RECEIPT_V1',
        'config_hash':config_hash(cfg),'numerical_source_digest':source_digest(),
        'state_sha256':file_sha(state),'state_bytes':state.stat().st_size,'initial_info':info,
        'collision_propagation_run':False,'physical_rate_evaluated':False,'bgrid_allowed':False})


def compare_states(ref_state: str, new_state: str, config_path: str, p_ref: float,
                   relative_screen: float, out_path: str):
    cfg=json.loads(Path(config_path).read_text())
    dx=float(cfg['grid']['dx']); dv=dx**3
    a=np.load(ref_state,mmap_mode='r',allow_pickle=False)
    b=np.load(new_state,mmap_mode='r',allow_pickle=False)
    if a.shape!=b.shape: raise ValueError('preparation states have different grid shapes')
    d=phase_aligned_distance(a,b,dv)
    cert=preparation_certificate(p_ref,relative_screen,d)
    cert.update({'grid_dx_a0':dx,'grid_dv_a0cubed':dv,'reference_state':str(ref_state),
        'candidate_state':str(new_state),
        'next_action':('NO_CANDIDATE_COLLISION_REQUIRED_FOR_THIS_SCREEN_ONLY'
                       if cert['certified_below_screen'] else
                       'BOUND_INCONCLUSIVE_RUN_CANDIDATE_COLLISION_IF_SCREEN_DECISION_REQUIRED')})
    _atomic_json(Path(out_path),cert)
    print(json.dumps(cert,indent=2))


def main():
    p=argparse.ArgumentParser(description=__doc__); s=p.add_subparsers(dest='command',required=True)
    g=s.add_parser('make-configs');g.add_argument('--base',required=True);g.add_argument('--out',required=True)
    r=s.add_parser('prepare-only');r.add_argument('--config',required=True);r.add_argument('--out',required=True)
    c=s.add_parser('compare');c.add_argument('--ref-state',required=True);c.add_argument('--new-state',required=True)
    c.add_argument('--config',required=True);c.add_argument('--p-ref',type=float,default=0.00775827737938)
    c.add_argument('--screen',type=float,default=.01);c.add_argument('--out',required=True)
    a=p.parse_args()
    if a.command=='make-configs': make_configs(a.base,a.out)
    elif a.command=='prepare-only': prepare_only(a.config,a.out)
    else: compare_states(a.ref_state,a.new_state,a.config,a.p_ref,a.screen,a.out)


if __name__=='__main__': main()
