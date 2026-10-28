"""Native source bridge. No execution without PR116's exact NPZ byte digest.
Reuses pinned event-union source loader and cross-envelope native atom projection.
No source fit, recombination, transport or cosmological IVP is rerun.
"""
from __future__ import annotations
import hashlib,importlib.util,sys,argparse,json
from pathlib import Path
from fractions import Fraction as F
from samebin_capacity import Atom,solve

PIN_NPZ='1c974c306b50f3deb86df712844f753b4402fb25e5dbc41c9a1de0254bf3ff47'
PIN_DIGEST='2cfca578701a2355fa6f1f3f1f8a27c211e81b9b488f65cef1e1a89e4dbc7690'
PIN_N=F('77906149556394634457/49039857307708443467467104868809893875799651909875269632')
PIN_L3=F('999870389230360121/3064991081731777716716694054300618367237478244367204352')
PIN_D3=F('7455897440411491273/24519928653854221733733552434404946937899825954937634816')
PIN_M3=2*PIN_D3-PIN_L3
W=F(10**20,2)

def _load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    obj=importlib.util.module_from_spec(spec)
    sys.modules[name]=obj
    spec.loader.exec_module(obj)
    return obj

def native_run(repo_root,source_npz,K='3'):
    repo=Path(repo_root);source_npz=Path(source_npz)
    if not source_npz.is_file():raise FileNotFoundError('PINNED_NATIVE_SOURCE_NOT_PRESENT')
    if hashlib.sha256(source_npz.read_bytes()).hexdigest()!=PIN_NPZ:raise ValueError('SOURCE_BYTES_MISMATCH')
    sys.path.insert(0,str(repo/'research/cr_he_energy_cross_20261028/implementation'))
    ce=_load(repo/'research/cr_he_energy_cross_20261028/implementation/cross_envelope.py','cr_cross_envelope')
    eu=ce.native_module()  # preserve the exact consumer module identity used by ce.native_atoms
    s=eu.load_pinned_source(source_npz)
    if s.atom_content_sha256!=PIN_DIGEST:raise ValueError('ATOM_CONTENT_DIGEST_MISMATCH')
    raw=ce.native_atoms(s)
    if len(raw)!=3201:raise ValueError('INVALID_ATOM_COUNT')
    atoms=[Atom(a.key,F(a.energy_eV),F(a.coefficient),a.partition) for a in raw]
    result=solve(atoms,K,True)
    unrestricted=solve(atoms,K,False)
    if F(K)==3:
        if result['N']!=PIN_N or result['L']!=PIN_L3 or unrestricted['S']!=PIN_M3:
            raise ValueError('K3_BASELINE_IDENTITY_MISMATCH')
    return {'unit':'CR_NATIVE_SAME_BIN_CAPACITY_NEXT','source_sha256':PIN_NPZ,
        'digest':PIN_DIGEST,'K':str(result['K']),'N':str(result['N']),
        'L':str(result['L']),'S':str(result['S']),'M':str(unrestricted['S']),
        'D':str((result['L']+unrestricted['S'])/2),'WN':str(W*result['N']),
        'WS':str(W*result['S']),'primal_dual_gap':str(result['S']-result['dual']),
        'per_bin':[{'partition':b['partition'],'S':str(b['S']),
            'H':str(b['H']),'delta':str(b['deficiency']),
            'cut_threshold':str(b['cut_threshold_high_eV']) if b['cut_threshold_high_eV'] is not None else None}
            for b in result['group_certs']],
        'pair_events':[[hi,lo,str(a)] for hi,lo,a in result['pairs']],
        'status':'NATIVE_FINITE_CAPACITY_CERTIFIED_NOT_EXCLUSIVE_KERNEL',
        'physical_activation':False,'full_native25':False}

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--repo',required=True);p.add_argument('--npz',required=True)
    p.add_argument('--K',default='3');p.add_argument('--output',required=True)
    a=p.parse_args()
    v=native_run(a.repo,a.npz,a.K)
    Path(a.output).write_text(json.dumps(v,indent=2)+'\n')
    print('PASS_NATIVE_CAPACITY',v['K'],v['S'],v['primal_dual_gap'])
