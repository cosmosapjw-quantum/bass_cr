import numpy as np
import pytest
from reassemble_saved import join_blocks

def fixture():
    tt={k:np.array([[i+1.]]) for i,k in enumerate(('S','H','D'))}
    pp={k:np.array([[i+4.]]) for i,k in enumerate(('S','H','D'))}
    raw={k:np.array([[complex(j,-j)]]) for j,k in enumerate(('S_tp','S_pt','H_tp','H_pt','D_tp','D_pt'),1)}
    return tt,pp,raw

def test_reassembly_preserves_six_raw_blocks_without_projection():
    tt,pp,raw=fixture();out=join_blocks(tt,pp,raw)
    for k in ('S','H','D'):
        assert out[k][0,0]==tt[k][0,0] and out[k][1,1]==pp[k][0,0]
        assert out[k][0,1]==raw[k+'_tp'][0,0]
        assert out[k][1,0]==raw[k+'_pt'][0,0]
        assert not out[k].flags.writeable

def test_reassembly_rejects_missing_raw_and_nonfinite():
    tt,pp,raw=fixture();bad=dict(raw);bad.pop('D_pt')
    with pytest.raises(ValueError):join_blocks(tt,pp,bad)
    raw['S_tp'][0,0]=float('nan')
    with pytest.raises(ValueError):join_blocks(tt,pp,raw)

def test_seal_tamper_is_rejected(tmp_path):
    import json
    from gram_exact import sha
    from reassemble_saved import write_npz,write_json,verify_seal
    write_npz(tmp_path/'S_ONLY_SAMPLES.npz',{'S':np.eye(2)})
    write_npz(tmp_path/'S_ONLY_DERIVATIVES.npz',{'dS':np.zeros((2,2))})
    write_json(tmp_path/'S_ONLY_SEAL.json',{'context_id':'a','D_read_in_S_phase':False,'samples_sha256':sha(tmp_path/'S_ONLY_SAMPLES.npz'),'derivatives_sha256':sha(tmp_path/'S_ONLY_DERIVATIVES.npz')})
    assert verify_seal(tmp_path,'a')['D_read_in_S_phase'] is False
    with pytest.raises(ValueError):verify_seal(tmp_path,'b')
    (tmp_path/'S_ONLY_DERIVATIVES.npz').write_bytes(b'changed')
    with pytest.raises(ValueError):verify_seal(tmp_path,'a')

def test_real_parent_stage_hash_maps_to_stage_not_derivative():
    import os,json
    from pathlib import Path
    from gram_exact import sha
    from reassemble_saved import collect_saved
    w=Path(os.environ['R4AB_WORK'])
    c=json.loads((w/'contracts/EXECUTION_CONTRACT.json').read_text())
    c['intake_manifest_sha256']=sha(w/'intake/r4aa/PACKAGE_MANIFEST.json')
    parent,records=collect_saved(w/'intake/r4aa',c)
    assert len(records)==34
    assert parent['candidate_basis_identity']==c['parent_candidate']
