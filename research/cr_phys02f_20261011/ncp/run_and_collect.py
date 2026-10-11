#!/usr/bin/env python3
"""Execute once, always collect, and preserve the actual first failure exit."""
import argparse
import pathlib
import subprocess
import sys
import time
import traceback
import uuid

from collect_return import collect
from launch_residence import STUDY, REPO, utc, write


def run_and_collect(run, out, *, executor=None, collector=None):
    if not pathlib.Path(run).is_absolute() or not pathlib.Path(out).is_absolute():
        raise ValueError('ABSOLUTE_DIRS_REQUIRED')
    run = pathlib.Path(run).resolve()
    out = pathlib.Path(out).resolve()
    if not run.is_absolute() or not out.is_absolute() or run.is_relative_to(REPO) or out.is_relative_to(REPO) or out.exists():
        raise ValueError('FRESH_ABSOLUTE_EXTERNAL_DIRS_REQUIRED')
    if run.exists():
        raise FileExistsError('FRESH_RUN_DIRECTORY_REQUIRED ' + str(run))
    if out.is_relative_to(run):
        raise ValueError('RETURN_OUTPUT_MUST_BE_OUTSIDE_RUN')
    executor = subprocess.run if executor is None else executor
    collector = collect if collector is None else collector
    command = [sys.executable, str(STUDY / 'ncp/launch_residence.py'),
               '--execute', '--run-dir', str(run)]
    start = time.monotonic()
    execution = {'command': command, 'start_utc': utc(), 'execute_calls': 1,
                 'automatic_retry': False}
    collection = {'start_utc': None, 'collection_calls': 0}
    execute_exit = 1
    collect_exit = 1
    try:
        completed = executor(command, check=False)
        execute_exit = completed.returncode
        execution['observed_execute_exit'] = execute_exit
    except Exception:
        execution['exception'] = traceback.format_exc()
        execution['observed_execute_exit'] = None
    finally:
        # If the launcher could not create its directory, preserve that failure
        # in a new directory; this never re-invokes execution.
        run.mkdir(parents=True, exist_ok=True)
        execution.update(actual_exit=execute_exit, end_utc=utc(),
                         elapsed_s=time.monotonic() - start)
        write(run / 'WRAPPER_EXECUTE_EXIT.json', execution)
        collection.update(start_utc=utc(), collection_calls=1)
        try:
            collection['return_archive'] = collector(STUDY, run, out)
            collect_exit = 0
        except Exception:
            collection['exception'] = traceback.format_exc()
        collection.update(actual_exit=collect_exit, end_utc=utc())
        write(run / 'WRAPPER_COLLECTION_EXIT.json', collection)
    # A successful archive never turns a failed numerical execution into exit0.
    actual_exit = execute_exit if execute_exit != 0 else collect_exit
    write(run / 'WRAPPER_ACTUAL_EXIT.json', {
        'actual_exit': actual_exit, 'execute_exit': execute_exit,
        'collection_exit': collect_exit,
        'return_archive': collection.get('return_archive'), 'execute_calls': 1,
        'collection_calls': 1, 'automatic_retry': False,
        'collection_receipt_written_after_archive': True,
        'scientific_status': 'INDEPENDENT_ASTRA_REVIEW_REQUIRED'})
    # Sidecars created after ZIP must form a separately hashed external family.
    if collection.get('return_archive'):
        import shutil
        from ops import sha
        files={}
        archive=pathlib.Path(collection['return_archive']['path'])
        files[archive.name]={'bytes':archive.stat().st_size,'sha256':sha(archive)}
        for name in ('WRAPPER_COLLECTION_EXIT.json','WRAPPER_ACTUAL_EXIT.json','WRAPPER_EXECUTE_EXIT.json','ACTUAL_EXIT.json','RUNTIME.json','stdout.log','stderr.log'):
            p=run/name
            if p.is_file():
                dest=out/name
                with dest.open('xb') as target,p.open('rb') as source:shutil.copyfileobj(source,target)
                files[name]={'bytes':dest.stat().st_size,'sha256':sha(dest)}
        write(out/'RETURN_FAMILY_MANIFEST.json',{'schema':'cr-phys02f-return-family.v1','files':files,'mandatory_external_sidecars':['WRAPPER_COLLECTION_EXIT.json','WRAPPER_ACTUAL_EXIT.json'],'sidecars_are_external_to_archive':True})
    return actual_exit


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-dir',required=True)
    parser.add_argument('--out',required=True)
    args = parser.parse_args()
    return run_and_collect(pathlib.Path(args.run_dir),pathlib.Path(args.out))


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception:
        traceback.print_exc()
        sys.exit(1)
