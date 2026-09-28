#!/usr/bin/env python3
"""One cache-only audit, with no native import, compile, subprocess or pool API."""
from __future__ import annotations
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import sys
import time

# Direct-file and python -m entrypoints are both supported without importing old runtimes.
if __package__ in (None,''):
    sys.path.insert(0,str(Path(__file__).resolve().parents[4]))
    from research.foundation_rebuild.ncp_shared_research_20260928.runtime_r3 import cache_bridge as cb
    from research.foundation_rebuild.ncp_shared_research_20260928.runtime_r3 import metric_diagnostics as md
    from research.foundation_rebuild.ncp_shared_research_20260928.runtime_r3.integrity import AuditError,sha,strict_json,file_bytes,write_json_new
else:
    from . import cache_bridge as cb, metric_diagnostics as md
    from .integrity import AuditError,sha,strict_json,file_bytes,write_json_new


def verify_code():
    root=Path(__file__).resolve().parent
    manifest=strict_json((root/'CODE_MANIFEST.json').read_bytes())
    for path,row in manifest['files'].items():
        file_bytes(root,path,row)
    return {'manifest_sha256':sha((root/'CODE_MANIFEST.json').read_bytes()),
            'file_count':len(manifest['files']),'checked':True}


def reader_environment():
    import numpy, scipy
    pins = strict_json(cb.PIN_PATH.read_bytes())['reader_environment']
    if sys.version_info < (3, 11) or numpy.__version__ != pins['numpy'] or scipy.__version__ != pins['scipy']:
        raise AuditError('R3_READER_ENVIRONMENT', 'Python >=3.11 and exact NumPy/SciPy pins required; no automatic install')
    return {'python':sys.version,'numpy':numpy.__version__,'scipy':scipy.__version__,
            'host_kind':'UNVERIFIED_LOCAL_EXECUTION_HOST','native_engine_loaded':False,
            'purpose':'portable archived-array reader and small matrix diagnostics',
            'thread_env':{k:os.environ.get(k) for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS')}}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[4])
    parser.add_argument('--out',required=True,type=Path,help='new output directory; parent must exist')
    args=parser.parse_args(argv)
    out=args.out.absolute()
    if out.exists() or out.is_symlink() or not out.parent.is_dir() or out.parent.is_symlink():
        print('R3_OUTPUT_COLLISION_OR_PARENT: output not created',file=sys.stderr)
        return 3
    out.mkdir(exist_ok=False)
    start=time.monotonic();phase='code_identity'
    report={'schema':'BASS_R3_CACHE_AUDIT_RETURN_V1','status':'R3_BLOCKED',
            'created_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
            'first_failure':None,'completed_phases':[],
            'new_native_evaluations':0,'new_engine_builds':0,'new_cloud_scientific_runs':0,
            'capture_execution_allowed':False,'production_admission':'HOLD','all_bound':'OPEN','b_grid':'NO_GO',
            'original_capture_gap_resolved':False,'continuous_global_supremum_bound':False,
            'review_type':'IMPLEMENTATION_SELF_CHECK_NOT_INDEPENDENT_REVIEW'}
    rc=3
    try:
        report['code_identity']=verify_code();report['completed_phases'].append(phase)
        phase='reader_environment';env=reader_environment()
        write_json_new(out/'READER_ENVIRONMENT.json',env)
        report['reader_environment']=env;report['completed_phases'].append(phase)
        phase='input_identity';inputs=cb.load_inputs(args.repo_root)
        report['input_pins_sha256']=sha(cb.PIN_PATH.read_bytes())
        report['admitted_r2_status']=inputs.documents['r2_report']['status']
        report['generation_environment']=inputs.documents['generation_environment']
        report['completed_phases'].append(phase)
        phase='cache_validation';cache=cb.CacheArchive.from_inputs(inputs)
        report['cache']=cache.audit
        write_json_new(out/'CACHE_AUDIT.json',cache.audit)
        report['completed_phases'].append(phase)
        phase='fresh_output_import';imported=cache.import_to(out/'imported_cache',expected_identity=cache.numerical_identity)
        write_json_new(out/'IMPORT_BRIDGE.json',imported.bridge)
        report['numerical_descriptor_sha256']=sha(cb.canonical(cache.numerical_identity))
        report['completed_phases'].append(phase)
        phase='stored_metric_diagnostics'
        diagnostics=md.from_cache(imported,inputs.documents['sentinels'],inputs.documents['f1_contract'])
        write_json_new(out/'METRIC_DIAGNOSTICS.json',diagnostics)
        report['metric_summary']={'sentinels':len(diagnostics['sentinels']),
                                  'max_relative_residual':max(r['relative_residual'] for r in diagnostics['sentinels']),
                                  'max_whitened_connection_rate_per_atomic_time':max(r['whitened_connection_spectral_norm'] for r in diagnostics['sentinels']),
                                  'continuous_bound':'NOT_CERTIFIED','integrated_eta':'NOT_CERTIFIED'}
        report['completed_phases'].append(phase)
        report['status']='R3_CACHE_REUSE_AND_METRIC_AUDIT_COMPLETE';rc=0
    except (Exception,KeyboardInterrupt) as exc:
        report['first_failure']={'phase':phase,'type':type(exc).__name__,
                                 'code':getattr(exc,'code','R3_RUNTIME_ERROR'),'message':str(exc)}
    finally:
        report['elapsed_seconds']=time.monotonic()-start
        write_json_new(out/'R3_RETURN.json',report)
        entries={}
        for path in sorted(out.rglob('*')):
            if path.is_file():
                data=path.read_bytes();entries[path.relative_to(out).as_posix()]={'bytes':len(data),'sha256':sha(data)}
        write_json_new(out/'OUTPUT_MANIFEST.json',{'schema':'BASS_R3_OUTPUT_MANIFEST_V1','files':entries,'self_excluded':True})
    print(json.dumps({'status':report['status'],'out':str(out),'new_native_evaluations':0}))
    return rc

if __name__=='__main__':
    raise SystemExit(main())
