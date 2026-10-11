import argparse,pathlib,json,hashlib,zipfile,stat,shutil,subprocess,sys
parser=argparse.ArgumentParser();parser.add_argument('archive',type=pathlib.Path);parser.add_argument('destination',type=pathlib.Path);a=parser.parse_args()
if a.destination.exists():raise ValueError('CREATE_ONLY_DESTINATION')
with zipfile.ZipFile(a.archive) as z:
 infos=z.infolist();names=[i.filename for i in infos]
 assert len(names)==len(set(names)) and z.testzip() is None
 for i in infos:
  n=pathlib.PurePosixPath(i.filename);assert not n.is_absolute() and '..' not in n.parts and '\\' not in i.filename and not i.is_dir() and not stat.S_ISLNK(i.external_attr>>16)
 m=json.loads(z.read('RETURN_MANIFEST.json'));assert set(names)==set(m['files'])|{'RETURN_MANIFEST.json'}
 for n,v in m['files'].items():
  b=z.read(n);assert len(b)==v['bytes'] and hashlib.sha256(b).hexdigest()==v['sha256'],n
 a.destination.mkdir();z.extractall(a.destination/'archive_layout')
layout=a.destination/'archive_layout';repo=a.destination/'repository';study=repo/'research/cr_phys02d_20261011'
shutil.copytree(layout/'dependency_payload',repo)
shutil.copytree(layout/'source_unit',study)
shutil.copytree(layout/'actual_run',a.destination/'actual_run')
def verify(root,manifest):
 data=json.loads(manifest.read_text());entries=data.get('files',data.get('entries'))
 if isinstance(entries,list):entries={i['path']:i for i in entries}
 for n,v in entries.items():
  p=(root/n).resolve();assert p.is_relative_to(root.resolve())
  b=p.read_bytes();assert len(b)==v.get('bytes',v.get('size')) and hashlib.sha256(b).hexdigest()==v['sha256'],n
 return len(entries)
unit_count=verify(study,study/'FILE_MANIFEST.json');dep_count=verify(repo,study/'inputs/DEPENDENCY_PAYLOAD_MANIFEST.json')
decision=json.loads((study/'review/INDEPENDENT_DECISION.json').read_text())
for n,v in decision['reviewed_files'].items():
 b=(study/n).read_bytes();assert len(b)==v['bytes'] and hashlib.sha256(b).hexdigest()==v['sha256'],n
r={'archive':str(a.archive),'bytes':a.archive.stat().st_size,'sha256':hashlib.sha256(a.archive.read_bytes()).hexdigest(),'CRC':'PASS','exact_entry_set':'PASS','return_payloads_verified':len(m['files']),'restored_unit_manifest_entries':unit_count,'restored_dependency_entries':dep_count,'restored_independent_review_files':len(decision['reviewed_files']),'restore_destination':str(a.destination),'verification_tier':'R3_LOCAL_RETURN_RESTORE','physical_calls':0}
print(json.dumps(r,indent=2))
