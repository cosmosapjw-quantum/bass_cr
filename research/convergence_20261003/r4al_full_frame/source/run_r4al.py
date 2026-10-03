"""One-shot read-only-input calculation of R4AL exact rational certificates."""
from __future__ import annotations
import argparse, hashlib, json, os, platform, resource, sys, time
from pathlib import Path
from fractions import Fraction as F
from full_frame import ContractError, angular_frame, anchor_matrix, make_certificate, json_safe

ROOT = Path(__file__).resolve().parents[1]

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def validate_lock(root, contract):
    for rec in contract['pins']:
        p=(root/rec['path']).resolve()
        if not p.is_relative_to(root.resolve()) or p.is_symlink() or sha(p)!=rec['sha256']:
            raise ContractError('source/input pin or containment mismatch: '+rec['path'])
    if contract['caps']!={'new_cross':0,'new_radial':0,'old_science_replay':0,'stage_attempts':1}:
        raise ContractError('unapproved evaluation scope')
    if contract['halfwidths_a0']!=['1/64','1/128']:
        raise ContractError('unapproved window changes')

def load_inputs(root):
    p=root/'inputs'
    meta=json.loads((p/'BASS_CR_R4AG_CANDIDATE.json').read_text())
    moments=json.loads((p/'BASS_CR_R4AB_GRAM_EXACT.json').read_text())
    enc=json.loads((p/'ANCHOR_S_ENCLOSURE.json').read_text())
    geom=json.loads((p/'ANCHOR_GEOMETRY.json').read_text())
    seal=json.loads((p/'ANCHOR_S_ONLY_SEAL.json').read_text())
    result=json.loads((p/'ANCHOR_RESULT.json').read_text())
    ids=[meta['identity'], moments['candidate'], enc['candidate'],result['candidate']]
    if len(set(ids))!=1 or ids[0]!='17c0215979675e40db364207ce138c5efb58cb24c22824e418f5abe3cfeb49ef':
        raise ContractError('candidate lineage mismatch')
    if sha(p/'BASS_CR_R4AG_CANDIDATE.npz')!=meta['candidate_npz_sha256']:
        raise ContractError('candidate binary mismatch')
    if enc['geometry_sha256']!=sha(p/'ANCHOR_GEOMETRY.json') or seal['sha256']!=sha(p/'ANCHOR_S_ENCLOSURE.json'):
        raise ContractError('anchor geometry or seal mismatch')
    if seal['D_read'] is not False or result['status']!='HIGH_ORDER_POINT_ENCLOSURE_TARGET_MET':
        raise ContractError('anchor authority not the qualified S-only lane')
    g=geom['geometry']
    z=F.from_float(g['actual_z_a0']);v=F.from_float(g['speed_a0_per_ta']);t=F.from_float(g['time_ta'])
    if z!=-32 or g['actual_centers_a0']!=[[0.0,0.0,0.0],[2.0,0.0,-32.0]]:
        raise ContractError('wrong anchor geometry')
    if v!=F(4521571391451241,2251799813685248) or float(g['time_ta']).hex()!=g['time_hex']:
        raise ContractError('speed/epoch representation mismatch')
    if g['trajectory']['charges']!=[1.0,1.0] or g['trajectory']['velocities']!=[[0.0,0.0,0.0],[0.0,0.0,float(v)]]:
        raise ContractError('charges or straight-line kinematics mismatch')
    import numpy as np
    with np.load(p/'BASS_CR_R4AG_CANDIDATE.npz',allow_pickle=False) as a:
        edges,u,q=a['edges'],a['shared_endpoint_values'],a['bubble_coefficients']
        if edges.shape!=(41,) or u.shape!=(5,41) or q.shape!=(5,40,3):
            raise ContractError('candidate representation shape')
        if not all(np.all(np.isfinite(x)) for x in (edges,u,q)):
            raise ContractError('nonfinite candidate')
        if edges[0]!=0 or edges[-1]!=64 or not np.all(np.diff(edges)>0) or np.any(u[:,[0,-1]]!=0):
            raise ContractError('H1 zero extension/endpoints failed')
    frame=angular_frame(moments['matrices_exact']['G'],moments['matrices_exact']['T'],[d['l'] for d in meta['modes']])
    return meta['identity'],frame,anchor_matrix(enc),v,z,t

def run(root,contract_path,out):
    root,contract_path,out=Path(root).resolve(),Path(contract_path).resolve(),Path(out).resolve()
    contract=json.loads(contract_path.read_text());validate_lock(root,contract)
    if out!=root/contract['output'] or not out.is_relative_to(root):
        raise ContractError('output not bound to this release root')
    if out.exists():raise ContractError('one-shot output already exists')
    out.mkdir(parents=True)
    reservation={'schema':'R4AL_RESERVATION_V1','contract_sha256':sha(contract_path),'output':str(out),'pid':os.getpid()}
    (out/'RESERVATION.json').write_text(json.dumps(reservation,indent=2)+'\n')
    start=time.monotonic()
    try:
        cid,f,a,v,z,t=load_inputs(root)
        c=make_certificate(f,a,v,z,t,[F(x) for x in contract['halfwidths_a0']])
        c.update(candidate=cid,scope='exact finite s+p H1 weak model; b=2, v pinned; existing two z=-32 windows',
                 unit_convention={'length':'a0','time':'ta=hbar/Eh','energy':'Eh','hbar_numeric':1},
                 provenance={'contract_sha256':sha(contract_path),'point_result_sha256':sha(root/'inputs/ANCHOR_RESULT.json')})
        wall=time.monotonic()-start; rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        if wall>contract['wall_seconds'] or rss*1024>contract['peak_rss_limit_bytes']:
            raise ContractError('light calculation exceeded declared resource cap')
        c['execution']={'wall_seconds':wall,'maxRSS_KiB':rss,'python':sys.version,'platform':platform.platform(),
                        'm64_resource_admission_retries':0,'numpy_used_for_npz_validation_only':True}
        raw=json.dumps(json_safe(c),indent=2,ensure_ascii=False)+'\n';(out/'CERTIFICATE.json').write_text(raw)
        summary={'schema':'R4AL_SUMMARY_V1','status':'FULL18_LOCAL_GRAM_AND_COARSE_WEAK_TUBES_CERTIFIED',
                 'candidate':cid,'windows':[{ 'halfwidth':str(x['halfwidth_a0']),
                   'gram_lower':str(x['gram']['lower']), 'gram_upper':str(x['gram']['upper']),
                   'condition_upper':str(x['gram']['condition_upper']),
                   'S_radius':str(x['S_constant_reference_error_operator_upper']),
                   'K_radius_Eh':str(x['K_zero_reference_error_operator_upper_Eh']),
                   'Sdot_radius_per_ta':str(x['Sdot_zero_reference_error_operator_upper_per_ta'])} for x in c['windows']],
                 'physical_bridge_upper':None,'precise_K_cubature_error':None,'full_stencil_total_upper':[None,None],
                 'new_cross':0,'new_radial':0,'old_science_replays':0,
                 'certificate_sha256':sha(out/'CERTIFICATE.json')}
        (out/'RESULT.json').write_text(json.dumps(summary,indent=2)+'\n')
        (out/'COMPLETED.json').write_text(json.dumps({'result_sha256':sha(out/'RESULT.json'),'exit_code':0},indent=2)+'\n')
        print(json.dumps({**summary,'windows':[{k:float(F(y)) if k!='halfwidth' else y for k,y in w.items()} for w in summary['windows']]},indent=2))
    except BaseException as e:
        (out/'FAILURE.json').write_text(json.dumps({'type':type(e).__name__,'message':str(e)},indent=2)+'\n')
        raise

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--contract',default=str(ROOT/'contracts/LIGHT_EXECUTION_CONTRACT.json'));a.add_argument('--output',required=True)
    ns=a.parse_args();run(ROOT,ns.contract,ns.output)
