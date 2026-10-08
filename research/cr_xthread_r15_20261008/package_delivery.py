"""Deterministic create-only ZIP from committed source/evidence plus pinned inputs."""
import argparse,hashlib,json,subprocess,zipfile
from pathlib import Path

def sha(b):return hashlib.sha256(b).hexdigest()
def build(repo,commit,stage,out):
    lane='research/cr_xthread_r15_20261008/'
    handoff='research/ncp_bass_cr_handoff_20261008/'
    prefixes=[lane,handoff,'AGENTS.md','docs/READBACK_POLICY.md','docs/HPC_ACCURACY_POLICY_KO.md',
              'docs/CHATGPT_CODEX_DIVISION_OF_LABOR_KO.md',
              'research/gap_closure_20261001/g02_derivative_validation_20261002/TASK_CONTRACT.json',
              'research/gap_closure_20261001/g02_derivative_validation_20261002/evidence/RECOVERY_CONTEXT.json']
    def git(*argv):return subprocess.check_output(['git','-C',str(repo),*argv])
    full=git('rev-parse',commit).decode().strip();tree=git('rev-parse',full+'^{tree}').decode().strip()
    paths=git('ls-tree','-r','--name-only',full,*prefixes).decode().splitlines()
    entries={f'source/{p}':git('show',full+':'+p) for p in paths}
    spec=json.loads(entries['source/'+handoff+'INPUTS.json'])
    for row in spec['packages']:
        b=(stage/'inputs'/row['name']).read_bytes()
        assert len(b)==row['size'] and sha(b)==row['sha256']
        entries['inputs/'+row['name']]=b
    entries['README_KO.md']=('고정 science checkpoint 및 네 원본 ZIP입니다. 배포 receipt는 별도 파일입니다.\n'
        'source/research/cr_xthread_r15_20261008/reproduce.py --stage NEW_STAGE --source-dir inputs --output NEW_RUN --independent\n'
        'Python 의존성 버전은 source/research/cr_xthread_r15_20261008/requirements.txt를 사용합니다.\n').encode()
    manifest={'source_commit':full,'source_tree':tree,'fixed_timestamp':'2026-10-08T00:00:00',
              'members':{n:{'bytes':len(b),'sha256':sha(b)} for n,b in sorted(entries.items())},
              'delivery_receipts':'DETACHED; no future provider success asserted in frozen science checkpoint'}
    entries['PACKAGE_MANIFEST.json']=(json.dumps(manifest,indent=2)+'\n').encode()
    with zipfile.ZipFile(out,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,b in sorted(entries.items()):
            info=zipfile.ZipInfo(name,date_time=(2026,10,8,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            info.create_system=3;info.external_attr=0o100644<<16
            z.writestr(info,b,compresslevel=9)
    with zipfile.ZipFile(out) as z:
        assert z.testzip() is None
        for n,row in manifest['members'].items():assert sha(z.read(n))==row['sha256']
    r={'name':out.name,'bytes':out.stat().st_size,'sha256':sha(out.read_bytes()),'source_commit':full,'source_tree':tree,'members':len(entries),'CRC_and_member_hash_check':True}
    out.with_suffix('.manifest.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--repo',type=Path,required=True);a.add_argument('--source-commit',required=True);a.add_argument('--stage',type=Path,required=True);a.add_argument('--output',type=Path,required=True)
    x=a.parse_args();build(x.repo,x.source_commit,x.stage,x.output)
