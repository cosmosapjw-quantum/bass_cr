"""Create-only exact return archive, including failed runs and dependencies."""
import hashlib,json,pathlib,time,uuid,zipfile
from ops import sha,verify,entries
DEP_HASH='248ad97e6417c3ba88bcbbfcb662f6fe65464e63eba6183421770ba06d41a341'

def collect(study,run,out):
    study=pathlib.Path(study).resolve();run=pathlib.Path(run).resolve();out=pathlib.Path(out).resolve()
    if not run.is_dir() or run.is_relative_to(study.parents[1]) or out.is_relative_to(run) or out.is_relative_to(study.parents[1]) or run.is_symlink() or out.is_symlink():raise ValueError('ACTUAL_RUN_REQUIRED_OR_UNSAFE_OUTPUT')
    out.mkdir(parents=True,exist_ok=False);payload={}
    dep=study/'inputs/DEPENDENCY_PAYLOAD_MANIFEST.json'
    if sha(dep)!=DEP_HASH:raise ValueError('DEPENDENCY_MANIFEST_IDENTITY_MISMATCH')
    verify(study.parents[1],dep)
    for rel,item in entries(json.loads(dep.read_text())):payload['dependency_payload/'+rel]=study.parents[1]/rel
    # Full current unit, including theory, tests, endpoint evidence and review.
    # Transient caches and return/run trees are excluded; selected actual run is separate.
    for base,prefix in ((run,'actual_run'),(study,'source_unit')):
        for p in sorted(base.rglob('*')):
            rel=p.relative_to(base)
            if p.is_symlink():raise ValueError('SYMLINK_RETURN_FORBIDDEN')
            if prefix=='source_unit' and (rel.parts[:2] in [('evidence','runs'),('evidence','returns')] or '__pycache__' in rel.parts):continue
            if p.is_file():
                if p.is_symlink():raise ValueError('SYMLINK_RETURN_FORBIDDEN')
                payload[prefix+'/'+rel.as_posix()]=p
    decision=study/'review/INDEPENDENT_DECISION.json'
    if decision.is_file():
        for rel,item in json.loads(decision.read_text()).get('reviewed_files',{}).items():
            p=(study/rel).resolve()
            if not p.is_relative_to(study) or p.is_symlink() or p.stat().st_size!=item['bytes'] or sha(p)!=item['sha256']:raise ValueError('REVIEWED_RETURN_IDENTITY_MISMATCH '+rel)
            payload['source_unit/'+rel]=p
    identities=json.loads((study/'inputs/INPUT_IDENTITIES.json').read_text())['files']
    dependencies={}
    for key,item in identities.items():
        p=(study.parents[1]/item['path']).resolve()
        if not p.is_file() or p.stat().st_size!=item['bytes'] or sha(p)!=item['sha256']:raise ValueError('DEPENDENCY_IDENTITY_MISMATCH '+key)
        name='dependencies/'+key+'/'+p.name;payload[name]=p;dependencies[key]={**item,'archive_path':name}
    from launch_residence import frozen_payload
    frozen=frozen_payload();manifestpath=pathlib.Path(frozen['path']);root=manifestpath.parent
    payload['frozen_payload/'+manifestpath.name]=manifestpath
    for name,p in payload.items():
        if p.is_symlink() or not p.resolve().is_relative_to(study.parents[1]) and not p.resolve().is_relative_to(run):raise ValueError('PAYLOAD_ESCAPE '+name)
    metadata={
        'RESTORE_LAYOUT.json':(json.dumps({'dependency_payload':'overlay repository-relative paths into repository root','source_unit':'overlay into repository/research/cr_phys02f_20261011','actual_run':'preserve separately in a fresh directory','verification':['RETURN_MANIFEST.json exact archive bytes and entry set','restored study FILE_MANIFEST.json','repository-relative inputs/DEPENDENCY_PAYLOAD_MANIFEST.json','hash-bound independent review'],'frozen_payload':'original archive manifest provenance; does not claim every original bundle-root file is included','status':'collection does not create independent scientific approval'},indent=2)+'\n').encode('utf-8'),
        'README_RESTORE.txt':('Verify every RETURN_MANIFEST entry and exact archive entry set first. Restore dependency_payload/ to repository root, then source_unit/ to research/cr_phys02f_20261011. Preserve actual_run/ separately in a fresh directory. Verify restored study FILE_MANIFEST, repository-relative DEPENDENCY_PAYLOAD_MANIFEST, and hash-bound independent review before execution. frozen_payload/ is original manifest provenance, not a claim that all original bundle-root files are included. Never overwrite an earlier actual run.\n').encode('utf-8')}
    files={n:{'bytes':p.stat().st_size,'sha256':sha(p)} for n,p in payload.items()}
    files.update({n:{'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()} for n,raw in metadata.items()})
    manifest={'schema':'cr-phys02f-ncp-return.v1','scientific_status':'INDEPENDENT_ASTRA_REVIEW_REQUIRED','dependencies':dependencies,'files':files}
    dest=out/('CR_PHYS02F_RESIDENCE_RETURN_'+time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'_'+uuid.uuid4().hex+'.zip')
    with zipfile.ZipFile(dest,'x',zipfile.ZIP_DEFLATED) as z:
        for name,p in payload.items():z.write(p,name)
        for name,raw in metadata.items():z.writestr(name,raw)
        z.writestr('RETURN_MANIFEST.json',json.dumps(manifest,indent=2)+'\n')
    return {'path':str(dest),'bytes':dest.stat().st_size,'sha256':sha(dest),'files':len(files)}
