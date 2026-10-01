"""Audit new rate factorization on hash-pinned saved physical matrices.

No operator evaluator or propagation is imported. Sdot is constructed only to
compare algebraic formulas, and is not an independent derivative validation.
"""
import os
for key in ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS'):
    os.environ[key]='1'
import sys,json,hashlib
from pathlib import Path
import numpy as np
from scipy.linalg import eigvalsh

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'projector'))
from projector_rate import cancellation_rate

def replay():
    snap=ROOT.parent/'static_validation_20261001'/'reused_snapshots'
    rows=[]
    for p in sorted(snap.glob('*.npz')):
        meta=json.loads(p.with_suffix('.json').read_text())
        sha=hashlib.sha256(p.read_bytes()).hexdigest()
        if sha!=meta['payload_sha256']: raise ValueError('saved payload hash mismatch')
        with np.load(p,allow_pickle=False) as z:
            rawS,rawH,D=(z['selected__'+k].copy() for k in ('S','H','D'))
        # Explicit machine-roundoff Hermitian projection used in BOTH paths.
        S=(rawS+rawS.conj().T)/2; H=(rawH+rawH.conj().T)/2
        Sd=D+D.conj().T
        J=np.eye(18,dtype=complex)[:,[9,10,12,13,14]]
        new=cancellation_rate(S,H,D,Sd,J,hbar=1.0)
        # Independently implement the ORIGINAL fixed-J Qdot + A†Q + QA.
        G=J.conj().T@S@J
        P=J@np.linalg.solve(G,J.conj().T@S)
        Q=S@P
        Qd=Sd@P+P.conj().T@Sd-P.conj().T@Sd@P
        A=np.linalg.solve(S,-1j*H-D)
        W=Qd+A.conj().T@Q+Q@A
        old=float(np.max(np.abs(eigvalsh((W+W.conj().T)/2,S))))
        delta=abs(new.rho-old)
        rel=delta/max(old,np.finfo(float).tiny)
        err=float(np.linalg.norm(new.W-W,2))
        if rel>2e-10 or err>2e-12:
            raise AssertionError((p.name,rel,err))
        rows.append({'query_id':meta['query_id'],'payload_sha256':sha,
          'context_id':meta['context_id'],'time_hex':meta['time_hex'],
          'time_au_display':float.fromhex(meta['time_hex']),
          'original_rho':old,'cancellation_rho':new.rho,
          'absolute_difference':delta,'relative_difference':rel,
          'W_spectral_difference':err,
          'S_projection_change_norm':float(np.linalg.norm(S-rawS,2)),
          'H_projection_change_norm':float(np.linalg.norm(H-rawH,2)),
          'singular_values_E':np.linalg.svd(new.E,compute_uv=False).tolist()})
    if len(rows)!=6: raise ValueError('expected six recovered snapshots')
    return {'schema':'BASS_R4T_SAVED_MATRIX_REPLAY_V1','status':'PASS',
      'scope':'new factorization numerical parity on Hermitian parts of six saved original-model matrices',
      'new_physical_queries':0,'new_physical_propagations':0,
      'Sdot_policy':'D+Ddag ONLY FOR ALGEBRAIC COMPARISON; G02 NOT VALIDATED',
      'tolerances':{'relative_rho':2e-10,'W_absolute_spectral':2e-12},
      'continuous_bound':False,'state_available':False,
      'rows':rows,'max_relative_rho_difference':max(r['relative_difference'] for r in rows)}

if __name__=='__main__':
    out=replay()
    (ROOT/'SAVED_MATRIX_REPLAY.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='rows'},indent=2))
