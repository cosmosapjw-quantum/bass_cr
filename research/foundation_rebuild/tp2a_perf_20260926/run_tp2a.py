#!/usr/bin/env python3
"""Fixed TP2A geometry scan, bounded CPU workers, durable per-node checkpoints.

No propagation, capture, GPU, automatic install, retry or tolerance tuning.
--resume-from salvages valid completed nodes into a NEW output directory.
"""
from __future__ import annotations
import os
# Set before NumPy/SciPy import and before spawning children: no nested BLAS pool.
for _k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[_k]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import argparse,concurrent.futures as cf,json,multiprocessing as mp,queue,subprocess,time,traceback,zipfile
import paths
from paths import HERE,REPO
from runtime import sha,digest,write_json,atomic_file,save_bank,load_bank,restore_nodes,worker_init,worker_geometry


def resource_limits():
    affinity=set(os.sched_getaffinity(0)) if hasattr(os,'sched_getaffinity') else set(range(os.cpu_count() or 1))
    effective=len(affinity);quota=None
    try:
        q,p=Path('/sys/fs/cgroup/cpu.max').read_text().split()
        if q!='max':quota=max(1,int(q)//int(p));effective=min(effective,quota)
    except (OSError,ValueError):pass
    physical=set()
    for c in affinity:
        d=Path(f'/sys/devices/system/cpu/cpu{c}/topology')
        try:physical.add(((d/'physical_package_id').read_text().strip(),(d/'core_id').read_text().strip()))
        except OSError:pass
    avail=None
    try:
        for l in Path('/proc/meminfo').read_text().splitlines():
            if l.startswith('MemAvailable:'):avail=int(l.split()[1])*1024
        lim=Path('/sys/fs/cgroup/memory.max').read_text().strip()
        if lim!='max':avail=min(avail,int(lim)-int(Path('/sys/fs/cgroup/memory.current').read_text()))
    except (OSError,TypeError,ValueError):pass
    reserve=8*1024**3 if avail and avail>24*1024**3 else 512*1024**2
    memworkers=max(1,int((avail-reserve)//(512*1024**2))) if avail else 1
    max_workers=max(1,min(effective,memworkers))
    default=max(1,min(8,max(1,(len(physical) or effective)-2),max_workers))
    return {'affinity_cpu_count':len(affinity),'physical_cores_in_affinity':len(physical) or None,
            'cgroup_cpu_quota':quota,'available_memory_bytes':avail,'reserve_bytes':reserve,
            'max_safe_workers':max_workers,'default_workers':default,'per_worker_blas_threads':1}


def verify_sources():
    rec=json.loads((HERE/'SOURCE_MANIFEST.json').read_text());expected=rec['files']
    for rel,value in expected.items():
        if sha(HERE/rel)!=value:raise ValueError('package source identity mismatch: '+rel)
    pins=json.loads((HERE/'DEPENDENCY_PINS.json').read_text())
    for row in pins['files']:
        if sha(REPO/row['path'])!=row['sha256']:raise ValueError('upstream source identity mismatch: '+row['path'])
    return {'manifest_sha256':sha(HERE/'SOURCE_MANIFEST.json'),'dependency_pins_sha256':sha(HERE/'DEPENDENCY_PINS.json')}


def run_new_tests(out,backend):
    import xml.etree.ElementTree as ET
    command=[sys.executable,'-m','pytest','-q','-p','no:cacheprovider',str(HERE/'tests'),'--junitxml='+str(out/'tests.xml')]
    if backend=='numpy':command+=['--ignore='+str(HERE/'tests/test_native.py')]
    env=dict(os.environ,PYTEST_DISABLE_PLUGIN_AUTOLOAD='1')
    with (out/'tests.stdout').open('x') as so,(out/'tests.stderr').open('x') as se:
        p=subprocess.run(command,stdout=so,stderr=se,env=env,timeout=180)
    counts={k:0 for k in ('tests','failures','errors','skipped')}
    if (out/'tests.xml').exists():
        for suite in ET.parse(out/'tests.xml').getroot().iter('testsuite'):
            for k in counts:counts[k]+=int(suite.attrib.get(k,0))
    r={'command':command,'returncode':p.returncode,'counts':counts,'native_tests_excluded':backend=='numpy'}
    write_json(out/'TEST_RECEIPT.json',r)
    if p.returncode or not counts['tests'] or counts['failures'] or counts['errors'] or counts['skipped']:
        raise RuntimeError('new optimization tests failed; no scan started')
    return r


def scan(config,bank,context_id,out,workers,native_dir,emit):
    ctx=mp.get_context('spawn');events=ctx.Queue();cancel=ctx.Event();result=[]
    todo=iter(config['z_samples_a0']);pending={};first=None
    pool=cf.ProcessPoolExecutor(max_workers=workers,mp_context=ctx,initializer=worker_init,
            initargs=(config,bank,context_id,str(out),events,cancel,native_dir))
    def submit_one():
        try:z=next(todo)
        except StopIteration:return False
        pending[pool.submit(worker_geometry,z)]=z;return True
    try:
        for _ in range(workers):submit_one()
        last=time.monotonic()
        while pending:
            done,_=cf.wait(pending,timeout=.2,return_when=cf.FIRST_COMPLETED)
            while True:
                try:emit(**events.get_nowait())
                except queue.Empty:break
            if time.monotonic()-last>=5:
                emit(event='heartbeat',running_or_finishing_geometries=sorted(pending.values()),completed=len(result));last=time.monotonic()
            for f in sorted(done,key=lambda f:pending[f]):
                z=pending.pop(f)
                try:
                    row=f.result();result.append(row)
                    if row['failed_screens'] and first is None:
                        first={'kind':'numerical','z_a0':z,'failed_screens':row['failed_screens']};cancel.set()
                except BaseException as e:
                    if first is None:first={'kind':'execution','z_a0':z,'type':type(e).__name__,'message':str(e)};cancel.set()
                if first is None:submit_one()
            if first:
                for f in tuple(pending):
                    if f.cancel():pending.pop(f)
        return sorted(result,key=lambda r:r['z_a0']),first
    except BaseException:
        cancel.set()
        for f in pending:f.cancel()
        raise
    finally:
        pool.shutdown(wait=True,cancel_futures=True)
        events.close();events.join_thread()


def finish(out,report):
    write_json(out/'RETURN_REPORT.json',report)
    files={str(p.relative_to(out)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(out.rglob('*')) if p.is_file() and not p.name.startswith('.partial_')}
    write_json(out/'MANIFEST.json',files)
    archive=out.with_name(out.name+'_RETURN.zip')
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(out.rglob('*')):
            if p.is_file() and not p.name.startswith('.partial_'):z.write(p,str(p.relative_to(out)))
    print(json.dumps({'status':report['status'],'report':str(out/'RETURN_REPORT.json'),'archive':str(archive),'capture_execution_allowed':False}),flush=True)


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out',required=True);ap.add_argument('--expected-commit');ap.add_argument('--workers',type=int)
    ap.add_argument('--backend',choices=('numpy','native'),default='numpy');ap.add_argument('--native-build')
    ap.add_argument('--resume-from',help='explicitly reuse verified complete nodes from a prior run in a fresh output')
    args=ap.parse_args(argv);out=Path(args.out).resolve()
    if out.exists() or out.with_name(out.name+'_RETURN.zip').exists():ap.error('output exists; nothing overwritten')
    out.mkdir(parents=True);started=time.monotonic();report={'schema':'BASS_TP2A_RETURN_V1','status':'IN_PROGRESS',
        'scope':'13_GEOMETRY_STATIC_METRIC_CONNECTION_SCAN_ONLY','capture_execution_allowed':False,
        'production_admission':'HOLD','all_bound':'OPEN','b_grid':'NO_GO','original_capture_gap_resolved':False,
        'gpu_run':False,'propagation_run':False,'completed_geometry':[]};phase='preflight';rc=0
    def emit(**row):
        row={'elapsed_seconds':time.monotonic()-started,**row}
        with (out/'PROGRESS.jsonl').open('a') as f:f.write(json.dumps(row)+'\n');f.flush();os.fsync(f.fileno())
        print(json.dumps(row),flush=True)
    emit(event='run_start',out=str(out))
    try:
        pins=verify_sources()
        try:
            head=subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True,stderr=subprocess.DEVNULL).strip()
            tree=subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD^{tree}'],text=True,stderr=subprocess.DEVNULL).strip()
        except (OSError,subprocess.CalledProcessError):head=tree=None
        if args.expected_commit and head!=args.expected_commit:raise ValueError('execution commit mismatch')
        from bass_foundations.radial_basis import RadialSpec,atomic_bank
        from cr_repro.observables import projectile_speed_au
        import numpy,scipy,platform
        config=json.loads((HERE/'CONTRACT.json').read_text());config['speed']=projectile_speed_au(config['energy_keV_per_u'])
        limits=resource_limits();workers=args.workers if args.workers is not None else limits['default_workers']
        if workers<1 or workers>limits['max_safe_workers']:raise ValueError('workers exceeds detected CPU/memory safety budget: '+str(limits))
        native=None;native_dir=None
        if args.backend=='native':
            if not args.native_build:raise ValueError('--backend native requires explicit --native-build directory')
            from native_ring import NativeRing
            native_dir=str(Path(args.native_build).resolve());native=NativeRing(native_dir).receipt
        elif args.native_build:raise ValueError('--native-build is only valid with --backend native')
        if args.resume_from:
            origin=Path(args.resume_from).resolve();bank,brec=load_bank(origin)
            for name in ('BASIS.json','BASIS.npz'):
                atomic_file(out/name,lambda f,name=name:f.write((origin/name).read_bytes()))
            bank_id=brec['identity']
        else:
            bank=atomic_bank(RadialSpec(**config['radial_spec']));brec=save_bank(out,bank);bank_id=brec['identity']
        context={'config':config,'basis_identity':bank_id,'sources':pins,'backend':args.backend,
                 'native_binary_sha256':native['library_sha256'] if native else None}
        if args.resume_from:
            previous=json.loads((Path(args.resume_from)/'INTAKE.json').read_text())
            if previous['context']!=context:raise ValueError('resume context differs; no automatic cache migration')
        context_id=digest(context);restored=restore_nodes(args.resume_from,out,context_id) if args.resume_from else 0
        report.update(execution_head=head,execution_tree=tree,source_layout='repository' if head else 'recovered_pinned_dependencies',
            workers=workers,backend=args.backend,restored_nodes=restored,resources=limits,
            environment={'python':sys.version,'numpy':numpy.__version__,'scipy':scipy.__version__,'machine':platform.machine()},native_build=native)
        write_json(out/'INTAKE.json',{'context':context,'context_id':context_id,'report':report})
        phase='new_tests';emit(event='tests_start');report['new_tests']=run_new_tests(out,args.backend);emit(event='tests_complete',counts=report['new_tests']['counts'])
        phase='geometry_scan';emit(event='scan_start',workers=workers,backend=args.backend,geometry_count=len(config['z_samples_a0']),restored_nodes=restored)
        rows,first=scan(config,bank,context_id,out,workers,native_dir,emit);report['completed_geometry']=rows
        if first:
            report['first_failure']=first;report['status']='NUMERICAL_SCREEN_FAILED' if first['kind']=='numerical' else 'EXECUTION_FAILED';rc=2 if first['kind']=='numerical' else 3
        elif len(rows)!=len(config['z_samples_a0']):raise RuntimeError('missing declared geometry results')
        else:report['status']='TP2A_OPERATOR_GEOMETRY_SCAN_PASS'
    except BaseException as e:
        rc=130 if isinstance(e,KeyboardInterrupt) else 3
        report['status']='INTERRUPTED' if rc==130 else ('IDENTITY_OR_INPUT_BLOCKED' if isinstance(e,(ValueError,FileNotFoundError)) else 'EXECUTION_OR_ENVIRONMENT_BLOCKED')
        report['first_failure']={'phase':phase,'type':type(e).__name__,'message':str(e)}
        (out/'failure.traceback.txt').write_text(traceback.format_exc())
    report['wall_seconds']=time.monotonic()-started
    report['continuous_trajectory_error_bound']=False;report['capture_admitted']=False
    finish(out,report);return rc
if __name__=='__main__':raise SystemExit(main())
