"""Finite orchestration of the unmodified v2 wrapper; stop at first failure."""
import hashlib,json,subprocess,sys
from pathlib import Path
O=Path('/mnt/sn850x2t/bass_cr_r3m14_20260922'); C=O/'collision0125'
sha=lambda p: hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
expected='581ff84930bb862efafdfec5d39d5b25aebf9297ce7ce45f833a5abe125b2a5b'
for i in range(1,17):
    label=f'collision0125.chunk{i:03d}'
    assert not (O/(label+'.stdout')).exists(), 'preserve prior attempt; reconcile instead of replay'
    cmd=['/home/cosmosapjw/cosmo_lab/.venv/bin/python',str(O/'trace_command.py'),label,'/mnt/sn850x2t/bass_cr_r3m11_20260921/.venv/bin/python','scripts/r3m14_collision_initial_witness.py','--config','configs/r3m13/tdl_dx025_imag0125_T30.json','--prepared',str(O/'initial0125'),'--out',str(C),'--max-steps','128']
    with (O/'receipts'/(label+'.trace.log')).open('x') as log:
        rc=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT).returncode
    print(json.dumps({'chunk':i,'returncode':rc}),flush=True)
    if rc: sys.exit(rc)
    witness=json.loads((C/'r3m14_initial_binding.json').read_text())
    assert witness['status']=='PASS_BYTE_IDENTICAL_INTERNAL_INITIAL_TO_PREPARED'
    assert all(witness[k] is True for k in ['array_digest_match','norm_match','environment_match'])
    seal=json.loads((C/'r3m11_checkpoint_seal.json').read_text())
    assert seal['source_digest']==expected
    assert all(sha(C/n)==h for n,h in seal['files'].items())
    names=['state.json','r3m11_checkpoint_seal.json','r3m14_witness_run_receipt.json','r3m14_initial_binding.json']
    record={'chunk':i,'returncode':rc,'files':{n:{'sha256':sha(C/n),'content':json.loads((C/n).read_text())} for n in names}}
    state=record['files']['state.json']['content']
    (O/'receipts'/(label+'.checkpoint.json')).write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({'done':state['done'],'nstep':state['nstep'],'norm':state['norm']}),flush=True)
    if (C/'result.json').exists():
        assert json.loads((C/'result.json').read_text())['status']=='completed'
        assert state['done']==state['nstep']
        break
else: raise RuntimeError('bounded 16-chunk maximum reached')
