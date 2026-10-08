import hashlib
import json
import subprocess
from pathlib import Path

import pytest

from research.foundation_rebuild.ncloud_f1_engine_admission_20260928.runtime.native.cloud_engine import (
    build_engine, verify_engine_identity, verify_source_pins,
)


def contract(source):
    return {'build_policy': {'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
            'required_flags': ['-std=c++17', '-O3', '-fPIC', '-shared', '-ffp-contract=off', '-Wall', '-Wextra', '-Werror'],
            'forbidden_flag_patterns': ['-march=native', '-mtune=native', '-ffast-math', '-Ofast', '-flto'],
            'output_library_name': 'libmoments.so'}}


def fake_compiler(argv, **kwargs):
    if '--version' in argv:
        return subprocess.CompletedProcess(argv, 0, stdout='g++ synthetic 1.0', stderr='')
    Path(argv[argv.index('-o') + 1]).write_bytes(b'synthetic-library')
    return subprocess.CompletedProcess(argv, 0, stdout='', stderr='')


def test_build_records_frozen_flags_and_independent_engine_identity(tmp_path):
    source = tmp_path / 'moment_kernel.cpp'
    source.write_text('synthetic source')
    out = tmp_path / 'new-engine'
    rec = build_engine(source, out, contract(source), run=fake_compiler, compiler='g++')
    assert rec['argv'][1:9] == contract(source)['build_policy']['required_flags']
    assert (out / 'libmoments.so').read_bytes() == b'synthetic-library'
    assert (out / 'ENGINE_BUILD.json').is_file() and (out / 'ENGINE_IDENTITY.json').is_file()
    assert verify_engine_identity(out)['library_sha256'] == hashlib.sha256(b'synthetic-library').hexdigest()


def test_source_sha_mismatch_blocks_compiler(tmp_path):
    source = tmp_path / 'moment_kernel.cpp'
    source.write_text('modified')
    policy = contract(source)
    policy['build_policy']['source_sha256'] = '0' * 64
    with pytest.raises(ValueError, match='source SHA'):
        build_engine(source, tmp_path / 'engine', policy, run=fake_compiler)
    assert not (tmp_path / 'engine').exists()


@pytest.mark.parametrize('flag', ['-march=native', '-mtune=native', '-ffast-math', '-Ofast', '-flto'])
def test_forbidden_compiler_flag_rejected_before_build(tmp_path, flag):
    source = tmp_path / 'moment_kernel.cpp'
    source.write_text('source')
    with pytest.raises(ValueError, match='forbidden'):
        build_engine(source, tmp_path / 'engine', contract(source), run=fake_compiler, extra_flags=(flag,))
    assert not (tmp_path / 'engine').exists()


@pytest.mark.parametrize('mode', ['failure', 'missing-library'])
def test_compiler_failure_or_missing_library_never_emits_identity(tmp_path, mode):
    source = tmp_path / 'moment_kernel.cpp'
    source.write_text('source')
    def runner(argv, **kwargs):
        if '--version' in argv:
            return subprocess.CompletedProcess(argv, 0, 'g++ synthetic', '')
        return subprocess.CompletedProcess(argv, 1 if mode == 'failure' else 0, '', 'compiler error')
    with pytest.raises(RuntimeError, match='compiler|library'):
        build_engine(source, tmp_path / 'engine', contract(source), run=runner)
    assert not (tmp_path / 'engine/ENGINE_IDENTITY.json').exists()


def test_engine_identity_tamper_rejected(tmp_path):
    source = tmp_path / 'moment_kernel.cpp'
    source.write_text('source')
    out = tmp_path / 'engine'
    build_engine(source, out, contract(source), run=fake_compiler)
    identity = json.loads((out / 'ENGINE_IDENTITY.json').read_text())
    identity['library_sha256'] = '0' * 64
    (out / 'ENGINE_IDENTITY.json').write_text(json.dumps(identity))
    with pytest.raises(ValueError, match='identity'):
        verify_engine_identity(out)


def test_source_pin_tamper_rejected(tmp_path):
    file = tmp_path / 'source.txt'
    file.write_text('changed')
    pins = {'additional_pins': [{'path': 'source.txt', 'sha256': hashlib.sha256(b'original').hexdigest()}]}
    with pytest.raises(ValueError, match='source pin'):
        verify_source_pins(tmp_path, pins)


def test_existing_output_is_create_only(tmp_path):
    source = tmp_path / 'moment_kernel.cpp'
    source.write_text('source')
    out = tmp_path / 'engine'
    out.mkdir()
    with pytest.raises(FileExistsError):
        build_engine(source, out, contract(source), run=fake_compiler)


def test_build_passes_wall_timeout_to_compiler(tmp_path):
    source = tmp_path / 'moment_kernel.cpp'
    source.write_text('source')
    limits = []
    def compiler(argv, **kwargs):
        limits.append(kwargs.get('timeout'))
        return fake_compiler(argv, **kwargs)
    build_engine(source, tmp_path / 'engine', contract(source), run=compiler, timeout_seconds=19)
    assert limits == [19, 19]
