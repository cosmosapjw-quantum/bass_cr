"""Saved-data-only assembly. There is no cross integrator in this module."""
from pathlib import Path
import json
import numpy as np
from gram_exact import sha,digest,frozen

KEYS=tuple(k+'_'+side for k in ('S','H','D') for side in ('tp','pt'))

def checked(a,shape):
    a=np.asarray(a,complex)
    if a.shape!=shape or not np.isfinite(a).all():raise ValueError('saved block shape/finiteness mismatch')
    return a

def join_metric(st,sp,s_tp,s_pt):
    nt,np_=len(st),len(sp);out=np.empty((nt+np_,nt+np_),complex)
    out[:nt,:nt]=checked(st,(nt,nt));out[nt:,nt:]=checked(sp,(np_,np_))
    out[:nt,nt:]=checked(s_tp,(nt,np_));out[nt:,:nt]=checked(s_pt,(np_,nt))
    return frozen(out)

def join_blocks(tt,pp,cross):
    if set(cross)!=set(KEYS) or not all(k in tt and k in pp for k in ('S','H','D')):raise ValueError('all six raw and both intrinsic blocks required')
    return {k:join_metric(tt[k],pp[k],cross[k+'_tp'],cross[k+'_pt']) for k in ('S','H','D')}

def validate_file(path,expected):
    if sha(path)!=expected:raise ValueError('input SHA mismatch: '+str(path))

def collect_saved(intake,contract):
    """Check identity and prior qualification receipts, without rerunning them."""
    intake=Path(intake);root=intake/'payload/runs_r4aa/offcentral_v1'
    validate_file(intake/'PACKAGE_MANIFEST.json',contract['intake_manifest_sha256'])
    manifest_rows=json.loads((intake/'PACKAGE_MANIFEST.json').read_text())['files']
    derivative_pin=next(x['sha256'] for x in manifest_rows if x['path']=='payload/runs_r4aa/offcentral_v1/analysis/DERIVATIVE_RESULT.json')
    validate_file(root/'STAGE_RESULT.json',contract['parent_result_sha256'])
    validate_file(root/'analysis/DERIVATIVE_RESULT.json',derivative_pin)
    c=json.loads((root/'CONTEXT.json').read_text())
    if c['candidate_basis_identity']!=contract['parent_candidate']:raise ValueError('basis mismatch')
    payload=dict(c);cid=payload.pop('context_id')
    if digest(payload)!=cid:raise ValueError('parent context digest mismatch')
    mapping=json.loads((intake/'CONTEXT_PATH_BINDING.json').read_text())
    mapped={p['original']:p['package_path'] for p in mapping['pins']}
    for p,h in {**c['input_pins'],**c['source_pins']}.items():
        if p not in mapped:raise ValueError('missing parent path binding')
        validate_file(intake/mapped[p],h)
    ledger=[json.loads(p.read_text()) for p in sorted((root/'reservations').glob('*.json'))]
    records=[]
    for gatepath in sorted((root/'gates').glob('*.json')):
        gate=json.loads(gatepath.read_text());group=root/'batches'/gate['batch']
        if gate['pass'] is not True or gate['context_id']!=cid:raise ValueError('unqualified geometry')
        validate_file(group/'SUMMARY.json',gate['summary_sha256'])
        batchdone=json.loads((group/'COMPLETED.json').read_text());manifest=json.loads((group/'MANIFEST.json').read_text())
        if batchdone['summary_sha256']!=gate['summary_sha256'] or batchdone['manifest_id']!=manifest['manifest_id']:raise ValueError('batch binding mismatch')
        for task in manifest['tasks']:
            d=group/'attempts'/f"{task['index']:03}";rec=json.loads((d/'COMPLETED.json').read_text())
            if rec['context_id']!=cid or rec['reservation'] not in ledger or rec['task']!=task or rec['input_pins']!=c['input_pins'] or rec['source_pins_digest']!=digest(c['source_pins']):raise ValueError('saved source/input/reservation mismatch')
            for f,k in [('RAW.npz','raw_sha256'),('FULL.npz','full_sha256'),('RAW.json','raw_metadata_sha256')]:validate_file(d/f,rec[k])
            md=json.loads((d/'RAW.json').read_text())['metadata']
            if md['candidate_basis_identity']!=contract['parent_candidate'] or md['geometry_identity']!=rec['geometry_identity']:raise ValueError('raw candidate/geometry mismatch')
            geo=rec['geometry_identity'];z=task['z_a0'];v=c['speed_a0_per_ta']
            if task['z_hex']!=float(z).hex() or task['time_hex']!=float(z/v).hex() or geo['time_hex']!=task['time_hex']:raise ValueError('actual time mismatch')
            records.append({'key':gate['batch']+'_'+str(task['index']),'path':d,'task':task,'receipt':rec,'geometry':geo})
    if len(records)!=34 or len(ledger)!=34:raise ValueError('expected 34 archived complete queries')
    return c,records

def write_json(path,obj):
    with open(path,'x') as f:json.dump(obj,f,indent=2,allow_nan=False);f.write('\n')

def write_npz(path,arrays):
    with open(path,'xb') as f:np.savez_compressed(f,**arrays)

def verify_seal(out,context_id):
    out=Path(out);s=json.loads((out/'S_ONLY_SEAL.json').read_text())
    if s.get('context_id')!=context_id or s.get('D_read_in_S_phase') is not False:raise ValueError('invalid S-only seal/context')
    validate_file(out/'S_ONLY_DERIVATIVES.npz',s['derivatives_sha256'])
    validate_file(out/'S_ONLY_SAMPLES.npz',s['samples_sha256'])
    return s
