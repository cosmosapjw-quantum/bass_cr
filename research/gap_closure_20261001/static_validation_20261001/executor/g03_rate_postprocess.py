"""Create-only G03 saved-matrix rate diagnostics; no operator/native calls.

Caller first validates qualified provider source/scope receipts. Here each raw
cross resolution is combined with the unchanged order20 same-center blocks.
Sdot=D+D† remains an assumed kinematic identity, not an independent FD test.
"""
from pathlib import Path
import hashlib,json,re,sys
import numpy as np
from scipy.linalg import eigh

HERE=Path(__file__).resolve().parent
SOURCE=HERE.parents[2]/'foundation_rebuild/ncp_shared_research_20260928/r4p0a_b0_static_tail_executor_20260930'
if str(SOURCE) not in sys.path:sys.path.insert(0,str(SOURCE))
from projector_rate_probe import rate_matrices
J=np.eye(18,dtype=complex)[:,[9,10,12,13,14]]

def _sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def _tag(rule):return f"q{rule['order']}_h{rule['subdivisions']}"
def _matrix(a,shape):
    a=np.asarray(a,complex)
    if a.shape!=shape or not np.isfinite(a).all():raise ValueError('finite frozen B0 matrix shape required')
    return a

def _full(arrays,tag):
    result={}
    for name in ('S','H','D'):
        a=_matrix(arrays['selected__'+name],(18,18)).copy()
        a[:9,9:]=_matrix(arrays[tag+'__'+name+'_tp'],(9,9))
        a[9:,:9]=_matrix(arrays[tag+'__'+name+'_pt'],(9,9))
        result[name]=a
    return result

def _analyze(full):
    S,H,D=(full[k] for k in ('S','H','D'));m=rate_matrices(S,H,D,J,hbar=1.)
    W=m['W'];lam,V=eigh(W,S,check_finite=True)
    rho=float(np.max(abs(lam)));metric_eigs=np.linalg.eigvalsh((S+S.conj().T)/2)
    smin=float(metric_eigs[0]);smax=float(metric_eigs[-1])
    if smin<=0 or smin/smax<1e-8:raise ValueError('metric outside frozen positive-definite conditioning screen')
    nw=float(np.linalg.norm(W,2));ns=float(np.linalg.norm(S,2))
    residual=W@V-(S@V)*lam[None,:]
    denominator=(nw+abs(lam)*ns)*np.linalg.norm(V,axis=0)
    relative=np.linalg.norm(residual,axis=0)/np.maximum(denominator,np.finfo(float).tiny)
    # ±lambda form one absolute-rho cluster. Near-degenerate branches remain
    # clustered rather than choosing an unstable single eigenvector.
    tolerance=max(1e-8*rho,128*np.finfo(float).eps*max(rho,np.finfo(float).tiny))
    mask=abs(lam)>=rho-tolerance
    cluster=V[:,mask];P=cluster@cluster.conj().T@S
    next_abs=float(np.max(abs(lam[~mask]))) if np.any(~mask) else None
    arrays={**full,'Q':m['Q'],'W':W,'eigenvalues':lam,'eigenvectors':V,
            'dominant_eigenvalue_indices':np.flatnonzero(mask),
            'dominant_S_orthogonal_projector':P}
    record={'status':'RATE_DIAGNOSTIC_VALID','rho_per_atomic_time':rho,
        'full_generalized_spectrum':lam.tolist(),'cholesky_rho':m['rho'],
        'rho_path_relative_discrepancy':abs(rho-m['rho'])/max(rho,np.finfo(float).tiny),
        'metric_min_eigenvalue':smin,'metric_max_eigenvalue':smax,'metric_condition':smax/smin,
        'input_S_hermiticity_defect':m['input_S_hermiticity_defect'],
        'input_H_hermiticity_defect':m['input_H_hermiticity_defect'],
        'W_hermiticity_defect':m['W_hermiticity_defect'],
        'maximum_generalized_relative_residual':float(np.max(relative)),
        'metric_eigenvector_orthonormality_defect':float(np.linalg.norm(V.conj().T@S@V-np.eye(18),2)),
        'metric_identity_residual':m['metric_identity_residual'],
        'dominant_abs_cluster_dimension':int(mask.sum()),'dominant_abs_cluster_tolerance':tolerance,
        'next_abs_cluster_value':next_abs,'dominant_to_next_abs_cluster_gap':None if next_abs is None else rho-next_abs,
        'dominant_projector_idempotency_defect':float(np.linalg.norm(P@P-P,2)),
        'dominant_projector_S_selfadjoint_defect':float(np.linalg.norm(P.conj().T@S-S@P,2))}
    return arrays,record

def analyze_query(query_dir,item,query_row,out_dir):
    query_dir=Path(query_dir);qid=item.query_id
    if not isinstance(qid,str) or not re.fullmatch('[0-9a-f]{64}',qid):raise ValueError('exact query digest required')
    jp=query_dir/(qid+'.json');npz=query_dir/(qid+'.npz');rec=json.loads(jp.read_text())
    if (rec.get('query_id')!=qid or rec.get('time_hex')!=item.time_hex
        or query_row.get('time_hex')!=item.time_hex or rec.get('payload_sha256')!=_sha(npz)):
        raise ValueError('saved query identity/payload mismatch')
    qual=rec.get('qualification',{})
    if qual.get('status')!='RUNTIME_QUERY_QUALIFIED':raise ValueError('qualified provider receipt required')
    selected=_tag(qual['selected_resolution']);lower=_tag(qual['lower_resolution'])
    attempts=rec.get('attempts',[]);tags=[_tag(a['resolution']) for a in attempts]
    if len(tags)<2 or len(set(tags))!=len(tags) or tags[-2:]!=[lower,selected]:
        raise ValueError('ordered adjacent qualifying pair required')
    with np.load(npz,allow_pickle=False) as f:arrays={k:np.array(f[k]) for k in f.files}
    selected_full=_full(arrays,selected)
    if any(not np.array_equal(selected_full[k],arrays['selected__'+k]) for k in ('S','H','D')):
        raise ValueError('selected full matrices disagree with raw selected cross blocks')
    # All identities above are checked before any output mutation.
    target=Path(out_dir)/qid;target.mkdir(parents=True,exist_ok=False)
    levels=[]
    for tag,attempt in zip(tags,attempts):
        full=_full(arrays,tag)
        try:payload,row=_analyze(full)
        except (ValueError,np.linalg.LinAlgError) as exc:
            if tag in (lower,selected):raise
            payload=full;row={'status':'PRIOR_LEVEL_RATE_UNAVAILABLE','error':str(exc)}
        path=target/(tag+'.npz')
        with path.open('xb') as stream:np.savez_compressed(stream,**payload)
        levels.append({**row,'resolution':attempt['resolution'],'matrix_file':path.name,'matrix_sha256':_sha(path)})
    a,b=levels[-2:];rhoa=a['rho_per_atomic_time'];rhob=b['rho_per_atomic_time']
    discrepancy=abs(rhoa-rhob)/max(rhoa,rhob,np.finfo(float).tiny)
    record={'schema':'BASS_G03_PER_RESOLUTION_RATE_V1','query_id':qid,'time_hex':item.time_hex,
        'provider_json_sha256':_sha(jp),'provider_payload_sha256':_sha(npz),'levels':levels,
        'same_center_reconstruction':'unchanged selected full 9x9 diagonal blocks; source-pinned same_center_order20',
        'Sdot_source':'ASSUMED_D_PLUS_D_DAGGER_NOT_INDEPENDENT_FD',
        'selected_indices':[9,10,12,13,14],'hbar_atomic_units':1.,
        'adjacent_relative_rho_discrepancy':discrepancy,'qualification_meaning':'INTERNAL_RESOLUTION_CONSISTENCY_NOT_CERTIFIED_OPERATOR_BOUND',
        'new_native_calls':0,'state_used':False}
    with (target/'RATE_DIAGNOSTICS.json').open('x') as stream:json.dump(record,stream,indent=2,allow_nan=False);stream.write('\n')
    return {'z_a0':query_row['z_a0'],'R_a0':query_row['R_a0'],'time_hex':item.time_hex,
        'rho_per_atomic_time':rhob,'qualified':True,'adjacent_relative_rho_discrepancy':discrepancy,
        'dominant_abs_cluster_dimension':b['dominant_abs_cluster_dimension'],
        'dominant_to_next_abs_cluster_gap':b['dominant_to_next_abs_cluster_gap'],
        'P_selected_status':'unavailable_without_state','Pdot_status':'unavailable_without_state',
        'diagnostic_relative_path':str(Path(qid)/'RATE_DIAGNOSTICS.json'),
        'diagnostic_sha256':_sha(target/'RATE_DIAGNOSTICS.json'),'new_native_calls':0}
