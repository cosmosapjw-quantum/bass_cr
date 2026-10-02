"""Exact identity checks and write-once output helpers for R4AC."""
from __future__ import annotations
from pathlib import Path
import hashlib,json,math
import numpy as np

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def array_digest(a):return digest({'shape':list(a.shape),'dtype':a.dtype.str,'bytes_sha256':hashlib.sha256(a.tobytes(order='C')).hexdigest()})
def write_json(p,x):
    with open(p,'x') as f:json.dump(x,f,indent=2,ensure_ascii=False,allow_nan=False);f.write('\n')
def write_npz(p,arrays):
    with open(p,'xb') as f:np.savez_compressed(f,**arrays)

def verify_pins(root,pins):
    root=Path(root).resolve()
    for name,h in pins.items():
        p=(root/name).resolve()
        if not p.is_relative_to(root) or sha(p)!=h:raise ValueError('pin mismatch: '+name)

def read_inputs(root,contract):
    root=Path(root);inp=root/'inputs';pins=json.loads((root/'contracts/INPUT_PINS.json').read_text())
    if sha(root/'contracts/INPUT_PINS.json')!=contract['required_pins']['input_pins_sha256']:raise ValueError('input manifest identity mismatch')
    verify_pins(root,pins)
    meta=json.loads((inp/'CANDIDATE.json').read_text());body=dict(meta);identity=body.pop('identity')
    if identity!=contract['candidate'] or digest(body)!=identity:raise ValueError('candidate identity mismatch')
    if meta['schema']!='BASS_R4X_CONTINUOUS_ENDPOINT_BASIS_V1' or meta['algorithm']!='u=(1-s)*left+s*right+s*(1-s)*q(s); degree=4; no renormalization':raise ValueError('candidate representation mismatch')
    if any(meta[k] for k in ('production_adopted','legacy_native_compatible','original_nodal_data_recovered')):raise ValueError('candidate role changed')
    with np.load(inp/'CANDIDATE.npz',allow_pickle=False) as z:bank={k:z[k].copy() for k in z.files}
    if {k:array_digest(v) for k,v in bank.items()}!=meta['array_digests']:raise ValueError('candidate typed bytes mismatch')
    if sha(inp/'CANDIDATE.npz')!=meta['candidate_npz_sha256']:raise ValueError('candidate payload mismatch')
    for n,h in meta['source_hashes'].items():
        if sha(root/'evidence'/('parent_'+n))!=h:raise ValueError('historical definition source mismatch')
    cache=json.loads((inp/'R4AB_CACHE_RECORD.json').read_text())
    if cache['candidate']!=identity or sha(inp/'R4AB_INTRINSIC.npz')!=cache['intrinsic_npz_sha256']:raise ValueError('intrinsic cache identity mismatch')
    lm=tuple((m['l'],mm) for m in meta['modes'] for mm in range(-m['l'],m['l']+1))
    ix=tuple(i for i,m in enumerate(meta['modes']) for _ in range(2*m['l']+1))
    if lm!=tuple((r['l'],r['m']) for r in cache['channel_records']):raise ValueError('ordered channel map mismatch')
    records=[];groups={}
    for d in sorted((inp/'records').iterdir()):
        rec=json.loads((d/'RESULT.json').read_text())
        if sha(d/'FULL.npz')!=rec['new_full_sha256'] or rec['cache_sha256']!=cache['intrinsic_npz_sha256'] or rec['diagnostics']['pass'] is not True:raise ValueError('unqualified parent record: '+d.name)
        geo=rec['geometry'];centers=np.array(geo['actual_centers_a0']);zs=float(centers[1,2])
        if centers.shape!=(2,3) or not np.array_equal(centers[0],[0.,0.,0.]) or centers[1,0]!=2. or centers[1,1]!=0. or not -32.02<zs<-31.98:raise ValueError('geometry outside registered slab')
        if geo['actual_z_hex']!=zs.hex() or float(geo['time_ta']).hex()!=geo['time_hex']:raise ValueError('geometry exact binary identity mismatch')
        if geo['trajectory']['charges']!=[1.,1.]:raise ValueError('charge scope mismatch')
        key=d.name.split('_')[0];records.append((d,rec));groups.setdefault(key,[]).append((d,rec))
    if len(records)!=34 or len(groups)!=11:raise ValueError('exact 34 records / 11 geometries required')
    for k,g in groups.items():
        if any(r['geometry']!=g[0][1]['geometry'] for _,r in g):raise ValueError('group geometry mismatch')
    return bank,meta,lm,ix,cache,records,groups
