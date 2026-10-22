#!/usr/bin/env python3
"""Create-only bundle of C22A evidence and its frozen executable dependencies."""
import argparse,hashlib,json,zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
REPO=HERE.parent.parent

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--science-commit',required=True)
    p.add_argument('--publication-head',required=True)
    p.add_argument('--publication-status',default='LOCAL_COMMIT_ONLY_UNPUBLISHED')
    p.add_argument('--git-bundle',type=Path)
    args=p.parse_args()
    source=json.loads((HERE/'evidence/SOURCE_FREEZE.json').read_text())
    paths={p for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc'}
    for record in source['files']:
        path=REPO/record['path'];raw=path.read_bytes()
        if len(raw)!=record['size_bytes'] or hashlib.sha256(raw).hexdigest()!=record['sha256']:
            raise ValueError('SOURCE_CHANGED:'+record['path'])
        paths.add(path)
    records=[]
    with zipfile.ZipFile(args.output,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for path in sorted(paths):
            raw=path.read_bytes();name=str(path.relative_to(REPO))
            records.append({'path':name,'size_bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
            archive.writestr(name,raw)
        if args.git_bundle:
            raw=args.git_bundle.read_bytes();name='publication/C22A_CONTENT.bundle'
            records.append({'path':name,'size_bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
            archive.writestr(name,raw)
        manifest={'schema':'C22A_DELIVERY_MANIFEST_V1','science_commit':args.science_commit,
                  'local_publication_head':args.publication_head,
                  'publication_status':args.publication_status,
                  'execution_source_identity':source['identity_sha256'],'files':records,
                  'old_C21O_raw_included':False,'old_C21O_frozen_execution_dependencies_included':True,
                  'C22A_original_attempts_and_rejected_analysis_versions':'PRESERVED;final analysis_v3 only',
                  'global_error_bound':None}
        archive.writestr('C22A_DELIVERY_MANIFEST.json',json.dumps(manifest,indent=2)+'\n')
        archive.writestr('README_DELIVERY.txt',
          'C22A new thermochemical pilot, not a C21O rerun.\n'
          'Start: research/cr_c22a_thermochemical_20261022/REPORT_KO.md and NEXT_THREAD_HANDOFF_KO.md.\n'
          'Final plots/tables: analysis_v3 and analysis_omissions_v1.\n'
          'Reference FAILED status and rejected v1/v2 analyses remain preserved.\n'
          'Verify expected ZIP SHA256 and C22A_DELIVERY_MANIFEST before extracting into a new directory.\n'
          'Provider ACKs are subsequent records in the separately delivered FINAL_AUTHORITY JSON.\n'
          'No prior C21O 51-trajectory ODE rerun is required. global_error_bound=null.\n')
    raw=args.output.read_bytes()
    print(json.dumps({'path':str(args.output),'size_bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),
                      'payload_files':len(records),'science_commit':args.science_commit,'new_ODE':0}))

if __name__=='__main__':main()
