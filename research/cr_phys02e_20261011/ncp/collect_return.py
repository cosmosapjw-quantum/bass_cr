"""Create-only exact return archive, including failed runs and dependencies."""
import hashlib,json,pathlib,time,uuid,zipfile
from ops import sha,verify,entries

def collect(study,run,out):
    study=pathlib.Path(study).resolve();run=pathlib.Path(run).resolve();out=pathlib.Path(out).resolve()
    if not run.is_dir() or out.is_relative_to(run):raise ValueError('ACTUAL_RUN_REQUIRED_OR_UNSAFE_OUTPUT')
    out.mkdir(parents=True,exist_ok=True);payload={}
    dep=study/'inputs/DEPENDENCY_PAYLOAD_MANIFEST.json'
    if sha(dep)!='e04ea95cf8cfc7aef26292c9bd8ed9fb538980f9912d9c04cf97172d8496208e':raise ValueError('DEPENDENCY_MANIFEST_IDENTITY_MISMATCH')
    verify(study.parents[1],dep)
    for rel,item in entries(json.loads(dep.read_text())):payload['dependency_payload/'+rel]=study.parents[1]/rel
    # Full current unit, including theory, tests, endpoint evidence and review.
    # Transient caches and return/run trees are excluded; selected actual run is separate.
    for base,prefix in ((run,'actual_run'),(study,'source_unit')):
        for p in sorted(base.rglob('*')):
            rel=p.relative_to(base)
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
    identities=json.loads((study/'inputs/INPUT_IDENTITIES.json').read_text())['inputs']
    dependencies={}
    for key,item in identities.items():
        p=(study/item['path']).resolve()
        if not p.is_file() or p.stat().st_size!=item['bytes'] or sha(p)!=item['sha256']:raise ValueError('DEPENDENCY_IDENTITY_MISMATCH '+key)
        name='dependencies/'+key+'/'+p.name;payload[name]=p;dependencies[key]={**item,'archive_path':name}
    root=next((x for x in (study,*study.parents) if (x/'BUNDLE_MANIFEST.json').is_file()),None)
    name='BUNDLE_MANIFEST.json'
    if root is None:
        root=next((x for x in (study,study.parents[1]) if (x/'FILE_MANIFEST.json').is_file()),None);name='FILE_MANIFEST.json'
    if root is None:raise ValueError('FROZEN_RETURN_MANIFEST_MISSING')
    manifestpath=root/name;verify(root,manifestpath);payload['frozen_payload/'+name]=manifestpath
    for rel,item in entries(json.loads(manifestpath.read_text())):
        p=(root/rel).resolve()
        if p.is_relative_to(study):payload['source_unit/'+p.relative_to(study).as_posix()]=p
    metadata={
        'RESTORE_LAYOUT.json':(json.dumps({'dependency_payload':'overlay repository-relative paths into repository root','source_unit':'overlay into repository/research/cr_phys02e_20261011','actual_run':'preserve separately in a fresh directory','verification':['RETURN_MANIFEST.json exact archive bytes and entry set','restored study FILE_MANIFEST.json','repository-relative inputs/DEPENDENCY_PAYLOAD_MANIFEST.json','hash-bound independent review'],'frozen_payload':'original archive manifest provenance; does not claim every original bundle-root file is included','status':'collection does not create independent scientific approval'},indent=2)+'\n').encode('utf-8'),
        'README_RESTORE.txt':('Verify every RETURN_MANIFEST entry and exact archive entry set first. Restore dependency_payload/ to repository root, then source_unit/ to research/cr_phys02e_20261011. Preserve actual_run/ separately in a fresh directory. Verify restored study FILE_MANIFEST, repository-relative DEPENDENCY_PAYLOAD_MANIFEST, and hash-bound independent review before execution. frozen_payload/ is original manifest provenance, not a claim that all original bundle-root files are included. Never overwrite an earlier actual run.\n').encode('utf-8')}
    files={n:{'bytes':p.stat().st_size,'sha256':sha(p)} for n,p in payload.items()}
    files.update({n:{'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()} for n,raw in metadata.items()})
    manifest={'schema':'cr-phys02e-ncp-return.v1','scientific_status':'INDEPENDENT_ASTRA_REVIEW_REQUIRED','dependencies':dependencies,'files':files}
    dest=out/('CR_PHYS02E_PULSE_RETURN_'+time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'_'+uuid.uuid4().hex+'.zip')
    with zipfile.ZipFile(dest,'x',zipfile.ZIP_DEFLATED) as z:
        for name,p in payload.items():z.write(p,name)
        for name,raw in metadata.items():z.writestr(name,raw)
        z.writestr('RETURN_MANIFEST.json',json.dumps(manifest,indent=2)+'\n')
    return {'path':str(dest),'bytes':dest.stat().st_size,'sha256':sha(dest),'files':len(files)}
