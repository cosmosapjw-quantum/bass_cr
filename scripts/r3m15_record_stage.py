"""Copy small completed evidence into Git and bind large immutable local arrays."""
import argparse
import json
from pathlib import Path
import shutil
from r3m15_coordinator import sha, verify_seal, validate_config, write_new

def record(root,job):
    source=root/job;repo=root/'worktree';dest=repo/'results/R3M15'/job
    completion=json.loads((source/'COMPLETE.json').read_text());verify_seal(source/'collision')
    validate_config(job,json.loads((source/'config.json').read_text()))
    if completion['result_sha256']!=sha(source/'collision/result.json'):raise ValueError('result digest mismatch')
    dest.mkdir(parents=True,exist_ok=False)
    records=[]
    for path in sorted(source.rglob('*')):
        if not path.is_file():continue
        rel=path.relative_to(source)
        row={'path':str(rel),'bytes':path.stat().st_size,'sha256':sha(path)}
        records.append(row)
        if path.suffix=='.npy':continue
        (dest/rel).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,dest/rel)
    write_new(dest/'MANIFEST.json',{'schema':'R3M15_JOB_MANIFEST_V1','job':job,'files':records})
    write_new(dest/'LARGE_ARRAY_POINTERS.json',{'files':[dict(r,local_path=str(source/r['path'])) for r in records if r['path'].endswith('.npy')],
                                             'remote_backup':'SEE docs/r3m15/DELIVERY_RECEIPT.json'})
    result=json.loads((source/'collision/result.json').read_text());audit=result['analysis']['gram_audit']
    print(json.dumps({'job':job,'P':audit['P_span_by_nmax'],'norm':audit['wavefunction_norm'],'Gram_condition':audit['Gram_condition']},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--job',choices=['A','B','C'],required=True)
    a=p.parse_args();record(a.root,a.job)
