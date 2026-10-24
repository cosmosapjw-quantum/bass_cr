"""Mechanical source-safe science publication assembly; no Git or science execution."""
import argparse,datetime,hashlib,json,re,time
from pathlib import Path

BASE='b2a305b0897c51d47aedeaf293e10e8746f54742'
TREE='445bd9d0389227132a4b3b322a3d8afea66d2b18'
SUFFIXES={'.json','.md','.csv','.py','.txt'}
def blob(data):return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def assemble(unit,output):
    cpu=time.process_time();wall=time.monotonic();index=json.loads((unit/'delivery/S0_CONTENT_INDEX.json').read_text());old={r['path']:r for r in index['rows']};oldblobs={r['sha256']:r['git_blob'] for r in old.values()};preserved=[]
    for name,row in old.items():
        data=(unit/name).read_bytes();ok=len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'] and blob(data)==row['git_blob']
        preserved.append(dict(path=name,pass_scoped=ok,git_blob=row['git_blob']))
        if not ok:raise RuntimeError('S0_PATH_CHANGED:'+name)
    selected=[];excluded=[];unique_new={};reused=0;duplicates=0
    for p in sorted(unit.rglob('*')):
        if not p.is_file():continue
        rel=str(p.relative_to(unit));parts=p.relative_to(unit).parts;reason=None
        if rel in {'review/independent_c9_20261024_v1/run_attempt3/MP80_REFERENCE_chi1.5_R80_N2048.csv', 'review/independent_c9_20261024_v1/run_attempt3/MP80_REFERENCE_chi3_R80_N2048.csv'}:reason='full MP80 reference vector; exact identity in review/RAW_VECTOR_INDEX.json and canonical archive'
        elif rel.startswith('delivery/publication_assembly/'):reason='assembly intermediates excluded from public tree'
        elif any(x in parts for x in ['__pycache__','mpl_config','raw','root','external']):reason='cache or full raw/private external intake'
        elif rel.startswith('intake/') and not rel.startswith('intake/freshness_public/'):reason='only explicitly selected freshness summary intake is public'
        elif p.suffix not in SUFFIXES:reason='binary or nonselected text extension; canonical archive carries raw'
        elif any(x in rel.lower() for x in ['download_request','signed_url','transfer_url','upload_url']):reason='transfer mechanics excluded'
        if reason:excluded.append(dict(path=rel,reason=reason));continue
        data=p.read_bytes();text=data.decode('utf-8');urls=re.findall(r'https?://[^\s"<>]+',text)
        if any(re.search(r'[?&](?:X-Amz-|X-Goog-|sig=|token=|se=|sv=|sp=)',url,re.I) for url in urls):
            excluded.append(dict(path=rel,reason='signed or token-bearing transfer URL detected'));continue
        sha=hashlib.sha256(data).hexdigest();gsha=blob(data);entry=dict(path=rel,repository_path='research/cr_n5_ei_energy_20261024/'+rel,bytes=len(data),sha256=sha,git_blob=gsha)
        if rel in old:entry.update(action='PRESERVE_BASE_TREE',transport='existing_base_tree')
        elif sha in oldblobs:entry.update(action='ADD',transport='reuse_existing_blob',reuse_blob=oldblobs[sha]);reused+=1
        elif sha in unique_new:entry.update(action='ADD',transport='reuse_new_content_blob',reuse_local_path=unique_new[sha]);duplicates+=1
        else:entry.update(action='ADD',transport='new_utf8_content');unique_new[sha]=rel
        selected.append(entry)
    result=dict(schema='N5_EI_SCIENCE_PUBLICATION_ASSEMBLY_V1',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),repository='cosmosapjw-quantum/bass_cr',branch='research/cr-n5-ei-energy-20261024',expected_parent_sha=BASE,base_tree_sha=TREE,force=False,status='PREPARED_NOT_PUBLISHED',S0_preserved=preserved,S0_preserved_count=len(preserved),selected=selected,excluded=excluded,selected_count=len(selected),added_count=sum(r['action']=='ADD' for r in selected),reuse_existing_blob_count=reused,reuse_new_content_blob_count=duplicates,new_unique_utf8_blob_count=len(unique_new),pending_evidence='Root final report/claim/DAG and C9 records must exist before final regeneration and explicit science publication GO',publication_gate='No Git writes before root explicit final GO; inspect branch head before expected-SHA update; preserve parallel changes on mismatch',mechanical_process_CPU_s=time.process_time()-cpu,mechanical_wall_s=time.monotonic()-wall,scientific_calls=0)
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x') as f:json.dump(result,f,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps({k:result[k] for k in ['status','S0_preserved_count','selected_count','added_count','reuse_existing_blob_count','reuse_new_content_blob_count','new_unique_utf8_blob_count','mechanical_process_CPU_s','mechanical_wall_s']}));return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--unit',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assemble(a.unit.resolve(),a.output.resolve())
