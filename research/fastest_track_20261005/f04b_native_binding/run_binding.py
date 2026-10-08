#!/usr/bin/env python3
"""One-shot source-pinned observation and read-only exact-real binding."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import shutil
import subprocess
import sys
import time
from bind import analyze, encode

SOURCE_SHA = {
    'hhe_events.rs': 'c100b08e034089c2d67b2102769ccdd51f1d29a2f388d6bb2dfe7984af93b290',
    'microstep.rs': 'e03cc1512cdd2b60735b1ab655c8e6657423c18ee4ad55ca1d30f24ad4974e53',
    'thermal.rs': '6d7be31934bb33a46c0911d28b62e34d22027e08a8a1945c5d7d32bf32f79b8a',
}

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def write(p, value):
    p.write_text(json.dumps(encode(value),indent=2)+'\n')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--reference',type=Path,required=True)
    parser.add_argument('--rustc',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    started=time.perf_counter()
    cpu=min(os.sched_getaffinity(0));os.sched_setaffinity(0,{cpu})
    os.environ.update(PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='1',
        OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
    commands=[]
    def run(argv,name):
        begin=time.perf_counter()
        p=subprocess.run([str(v) for v in argv],capture_output=True,text=True)
        (args.output/(name+'.stdout')).write_text(p.stdout)
        (args.output/(name+'.stderr')).write_text(p.stderr)
        commands.append(dict(argv=[str(v) for v in argv],exit_code=p.returncode,
            wall_seconds=time.perf_counter()-begin))
        write(args.output/'COMMANDS.json',commands)
        if p.returncode:raise RuntimeError(f'{name} exit {p.returncode}')
        return p.stdout
    observation_ran=False
    try:
        manifest=json.loads((args.reference/'MANIFEST_SHA256.json').read_text())
        for name,identity in manifest.items():
            p=args.reference/name
            if p.stat().st_size!=identity['bytes'] or sha(p)!=identity['sha256']:
                raise ValueError('F04A payload mismatch: '+name)
        native=args.output/'native';native.mkdir()
        for name,digest in SOURCE_SHA.items():
            p=args.source/name
            if sha(p)!=digest:raise ValueError('native source mismatch: '+name)
            shutil.copyfile(p,native/name)
        wrapper=Path(__file__).with_name('export_endpoint.rs')
        shutil.copyfile(wrapper,native/'main.rs')
        compiler=run([args.rustc,'-vV'],'rustc_identity')
        inputs=dict(source_sha256=SOURCE_SHA,wrapper_sha256=sha(wrapper),
            analyzer_sha256=sha(Path(__file__).with_name('bind.py')),driver_sha256=sha(__file__),
            compiler_sha256=sha(args.rustc),compiler=compiler,python=platform.python_version(),
            single_cpu=cpu,affinity=sorted(os.sched_getaffinity(0)),
            observed_host_cpu_count=os.cpu_count(),memory_info=Path('/proc/meminfo').read_text(),
            cgroup=Path('/proc/self/cgroup').read_text(),mountinfo=Path('/proc/self/mountinfo').read_text(),
            reference_manifest_sha256=sha(args.reference/'MANIFEST_SHA256.json'),
            inherited_proof_sha256=sha(args.reference/'results/point_dt_1e8.json'))
        write(args.output/'INPUT_LOCK.json',inputs)
        binary=native/'endpoint'
        # Original supplied minimal native probe used -O; preserve this setting.
        run([args.rustc,'--edition=2021','-O',native/'main.rs','-o',binary],'build')
        run(['ldd',binary],'native_libraries')
        observation_ran=True
        text=run([binary],'endpoint_bits')
        result=analyze(text,args.reference)
        write(args.output/'BINDING_RESULT.json',result)
        summary=dict(status=result['status'],endpoint_in_inherited_cube=True,
            residual_inf_display=float(max(map(abs,result['reduced_fraction_residual']))),
            root_distance_inf_display=float(result['root_distance_inf']),
            component_root_distance_display=list(map(float,result['component_root_distance'])),
            exact_seven_scaled_residual_inf_display=float(max(map(abs,result['normalized_direct_seven_residual']))),
            native_reported_residual_display=float(result['native_reported_residual_norm']),
            thermal_B_lower_display=float(result['thermal_numerator_lower']),
            actual_old_u_display=float(result['old'].u),
            old_u_difference_display=float(result['old_u_difference_from_reference']),
            binary_sha256=sha(binary),binary_bytes=binary.stat().st_size,
            native_implicit_calls=1,adaptive_calls=0,retries=0,global_F04_closed=False)
        write(args.output/'SUMMARY.json',summary)
        print(json.dumps(summary,indent=2))
        return 0
    except Exception as exc:
        write(args.output/'FAILURE.json',dict(error=repr(exc),observation_started=observation_ran,
            retries=0,stop_condition='FIRST_FAILURE_STOP'))
        raise
    finally:
        write(args.output/'ATTEMPT.json',dict(attempt_count=1,retries=0,
            observation_started=observation_ran,wall_seconds=time.perf_counter()-started,
            child_peak_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
            peak_scope='compiler and all subprocesses; not endpoint alone'))

if __name__=='__main__':
    sys.dont_write_bytecode=True
    if hasattr(sys,'set_int_max_str_digits'):sys.set_int_max_str_digits(0)
    raise SystemExit(main())
