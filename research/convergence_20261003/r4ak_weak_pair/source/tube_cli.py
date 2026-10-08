"""Bounded file interface for exact-model weak-pair tube evaluation.

A hash binds the input object, not the truth of its physical premises. Outputs
are always reference/conditional and never promote the atomic claim registry.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from weak_pair import P,CQ,Remainders,ContractError,exact_pair_certificate,propagate_certificates

def _number(s):
    if not isinstance(s,str) or not s.strip():raise ContractError('exact rational strings required')
    from weak_pair import rat
    return rat(s)
def _matrix(A):
    if not isinstance(A,list) or not 3<=len(A)<=64:raise ContractError('3..64 rows required')
    n=len(A);out=[]
    for row in A:
        if not isinstance(row,list) or len(row)!=n:raise ContractError('square matrix required')
        new=[]
        for cell in row:
            if not isinstance(cell,list) or not 1<=len(cell)<=13:raise ContractError('0..12 polynomial degree required')
            cs=[]
            for c in cell:
                if not isinstance(c,list) or len(c)!=2:raise ContractError('complex rational coefficient pair required')
                cs.append(CQ(_number(c[0]),_number(c[1])))
            new.append(P(cs))
        out.append(new)
    return out

def evaluate_packet(d):
    if d.get('schema')!='R4AK_POLYNOMIAL_OPERATOR_TUBE_INPUT_V1':raise ContractError('unknown tube input schema')
    if d.get('units')!={'energy':'Eh','time':'ta','hbar':'Eh*ta'}:raise ContractError('unsupported units')
    if d.get('frame_connection_in_K') is not True:raise ContractError('complete K=H-i*hbar*D required')
    if d.get('model_origin') not in ('EXACT_POLYNOMIAL_REFERENCE','POLYNOMIAL_PLUS_ASSUMED_UNIFORM_REMAINDERS'):
        raise ContractError('sampled fits are not operator envelopes')
    candidate=d.get('candidate_or_fixture_identity')
    if not isinstance(candidate,str) or not candidate.strip():raise ContractError('missing candidate/fixture identity')
    S,K=_matrix(d['S']),_matrix(d['K']);hb=_number(d['hbar']);R=d['retained_indices']
    slabs=d['slabs']
    if not isinstance(slabs,list) or not 1<=len(slabs)<=256:raise ContractError('1..256 bounded time slabs required')
    result=[]
    for row in slabs:
        if not isinstance(row.get('interval'),list) or len(row['interval'])!=2:raise ContractError('interval endpoints required')
        interval=tuple(_number(v) for v in row['interval']);rem=row.get('remainders')
        if d['model_origin']=='POLYNOMIAL_PLUS_ASSUMED_UNIFORM_REMAINDERS':
            if rem is None:raise ContractError('missing assumed uniform error; not zero')
            rem=Remainders(_number(rem['epsilon_S']),_number(rem['epsilon_K']),_number(rem['epsilon_Sdot']),rem['evidence_id'])
        elif rem is not None:raise ContractError('exact reference must not hide remainder inputs')
        result.append(exact_pair_certificate(S,K,interval,R,hb,rem))
    initial=d.get('initial_state_bounds')
    propagation=None if initial is None else propagate_certificates(result,_number(initial['error_S']),_number(initial['retained_norm_G']))
    # Check adjacency even when the initial state is unavailable.
    for a,b in zip(result,result[1:]):
        if a['interval_ta'][1]!=b['interval_ta'][0]:raise ContractError('noncontiguous slabs')
    return {'schema':'R4AK_OPERATOR_TUBE_RESULT_V1',
       'input_sha256':hashlib.sha256(json.dumps(d,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
       'candidate_or_fixture_identity':candidate,'tubes':result,'propagation':propagation,
       'initial_state_missing':initial is None,'physical_bridge_upper':None,'physical_admission':False}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--input',required=True);parser.add_argument('--output',required=True)
    a=parser.parse_args();src=Path(a.input);dst=Path(a.output)
    if dst.exists() or not dst.parent.is_dir():raise ContractError('new output in existing directory required')
    if src.stat().st_size>16*1024*1024:raise ContractError('input exceeds 16MiB contract')
    out=evaluate_packet(json.loads(src.read_text()))
    with dst.open('x') as f:json.dump(out,f,indent=2);f.write('\n')
if __name__=='__main__':main()
