"""Create-only, frozen-flag native build with a separate current-engine identity."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def _write_new(path, value):
    with Path(path).open('x', encoding='utf-8') as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())


def verify_source_pins(repo_root, pins):
    """Verify the numerical dependency closure without silently repinning it."""
    root = Path(repo_root)
    checked = {}
    rows = list(pins.get('additional_pins', []))
    inherited = pins.get('inherited_dependency_pins')
    if inherited:
        rows.insert(0, inherited)
    for row in rows:
        path = root / row['path']
        if not path.is_file() or _sha(path) != row['sha256']:
            raise ValueError('source pin mismatch: ' + row['path'])
        checked[row['path']] = row['sha256']
    if inherited:
        dependency = json.loads((root / inherited['path']).read_text())
        for row in dependency.get('files', []):
            path = root / row['path']
            if not path.is_file() or _sha(path) != row['sha256']:
                raise ValueError('source pin dependency mismatch: ' + row['path'])
            checked[row['path']] = row['sha256']
    expected_cpp = pins.get('historical_moment_source_sha256')
    if expected_cpp:
        cpp = root / 'research/foundation_rebuild/tp2a_analytic_pruning_20260926/code/moment_kernel.cpp'
        if not cpp.is_file() or _sha(cpp) != expected_cpp:
            raise ValueError('source pin moment source mismatch')
        checked[str(cpp.relative_to(root))] = expected_cpp
    return checked


def _cpu_metadata():
    model, flags = None, []
    try:
        for line in Path('/proc/cpuinfo').read_text().splitlines():
            if line.startswith('model name') and model is None:
                model = line.split(':', 1)[1].strip()
            if line.startswith('flags') and not flags:
                flags = line.split(':', 1)[1].split()
    except OSError:
        pass
    return model, flags


def build_engine(source, out_dir, contract, *, run=None, compiler='g++', extra_flags=(), timeout_seconds=None):
    policy = contract['build_policy']
    source = Path(source).resolve()
    out = Path(out_dir).resolve()
    if out.exists():
        raise FileExistsError('create-only engine output exists')
    if not source.is_file() or _sha(source) != policy['source_sha256']:
        raise ValueError('source SHA mismatch')
    required = ['-std=c++17', '-O3', '-fPIC', '-shared', '-ffp-contract=off',
                '-Wall', '-Wextra', '-Werror']
    if policy['required_flags'] != required:
        raise ValueError('frozen compiler flags mismatch')
    forbidden = ('-march=', '-mtune=', '-ffast-math', '-Ofast', '-flto')
    if any(str(flag).startswith(forbidden) for flag in extra_flags):
        raise ValueError('forbidden compiler flag')
    if extra_flags:
        raise ValueError('extra compiler flags are outside frozen build command')
    if Path(compiler).name != 'g++':
        raise ValueError('frozen compiler family is g++')
    run = run or subprocess.run
    resolved = shutil.which(compiler) if compiler == 'g++' else compiler
    if not resolved:
        raise RuntimeError('compiler unavailable')
    out.mkdir(parents=True)
    lib = out / policy['output_library_name']
    argv = [resolved, *required, str(source), '-o', str(lib)]
    version = run([resolved, '--version'], capture_output=True, text=True, check=False, timeout=timeout_seconds)
    if version.returncode:
        raise RuntimeError('compiler version query failed')
    result = run(argv, capture_output=True, text=True, check=False, timeout=timeout_seconds)
    if result.returncode:
        raise RuntimeError('compiler failed: ' + str(result.stderr)[:1000])
    if not lib.is_file() or lib.stat().st_size == 0:
        raise RuntimeError('library missing or empty after compiler success')
    try:
        import numpy as np
        import scipy
        numeric = {'numpy': np.__version__, 'scipy': scipy.__version__,
                   'blas': np.__config__.CONFIG.get('Build Dependencies', {}).get('blas')}
    except ImportError:
        numeric = {'numpy': None, 'scipy': None, 'blas': None}
    model, flags = _cpu_metadata()
    source_sha, library_sha = _sha(source), _sha(lib)
    compatibility = {'schema': 'BASS_ANALYTIC_MOMENTS_BUILD_V1',
                     'source_sha256': source_sha, 'library_sha256': library_sha,
                     'machine': platform.machine(), 'system': platform.system(),
                     'command': argv, 'compiler_version': version.stdout}
    build = {'schema': 'BASS_NCLOUD_F1_ENGINE_BUILD_V1', 'source_path': str(source),
             'source_sha256': source_sha, 'library_sha256': library_sha,
             'library_bytes': lib.stat().st_size, 'compiler_path': resolved,
             'compiler_version': version.stdout, 'argv': argv,
             'compiler_stdout': result.stdout, 'compiler_stderr': result.stderr,
             'machine': platform.machine(), 'system': platform.system(),
             'cpu_model': model, 'cpu_flags': flags, 'libc': platform.libc_ver(),
             'python': sys.version, **numeric}
    identity = {'schema': 'BASS_NCLOUD_F1_ENGINE_IDENTITY_V1',
                'source_sha256': source_sha, 'library_sha256': library_sha,
                'machine': build['machine'], 'system': build['system'],
                'compiler_path': resolved, 'compiler_version': version.stdout,
                'argv': argv, 'numeric': numeric}
    identity['identity_sha256'] = hashlib.sha256(_canonical(identity)).hexdigest()
    _write_new(out / 'BUILD.json', compatibility)
    _write_new(out / 'ENGINE_BUILD.json', build)
    _write_new(out / 'ENGINE_IDENTITY.json', identity)
    return build


def verify_engine_identity(out_dir):
    out = Path(out_dir)
    identity = json.loads((out / 'ENGINE_IDENTITY.json').read_text())
    build = json.loads((out / 'ENGINE_BUILD.json').read_text())
    compatibility = json.loads((out / 'BUILD.json').read_text())
    digest = identity.pop('identity_sha256', None)
    if digest != hashlib.sha256(_canonical(identity)).hexdigest():
        raise ValueError('engine identity receipt tamper')
    identity['identity_sha256'] = digest
    if (identity['library_sha256'] != _sha(out / 'libmoments.so')
            or identity['library_sha256'] != build['library_sha256']
            or identity['library_sha256'] != compatibility['library_sha256']
            or identity['source_sha256'] != build['source_sha256']
            or identity['machine'] != platform.machine()
            or identity['system'] != platform.system()):
        raise ValueError('engine identity/binary/platform mismatch')
    source = Path(build['source_path'])
    if not source.is_file() or _sha(source) != identity['source_sha256']:
        raise ValueError('engine identity source mismatch')
    return identity
