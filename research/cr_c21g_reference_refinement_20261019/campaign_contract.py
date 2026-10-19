"""C21G immutable input contract and bounded pilot policy (standard library)."""
from __future__ import annotations
import hashlib
import json
import math
import os
from pathlib import Path
import uuid

HERE = Path(__file__).resolve().parent
OWNER = '6ea2b1b4b3875c9163cafc45efe720afded43fc4'
BASELINE_EXECUTION = 'f8359232df8d0dd4fe91fcdabeb6701eb06089ba'
ASSESSMENT_HEAD = 'd780c2c53f869c914add1d5492312d0bc507f976'
NATIVE_BINARY_SHA256 = '1e7265185960cd91c3c589057b3e29d191d83bce95e59d803a399f9eb234ad40'
NATIVE_KIND = 'NATIVE_ORIGINAL_NONPHOTO_RUST'
RAW_NAME = 'C21F_NATIVE_NCP_20261018T1358Z'
DEFAULT_SOURCE = HERE.parent / 'cr_c21e_event_native_20261018'
BIND_EV = (13.598434599702, 24.587389011, 54.41776)
TIERS = (
    {'name': 'L1', 'rtol': 2e-11, 'atol_scale': 2e-14, 'max_step_divisor': 8.0},
    {'name': 'L2', 'rtol': 2e-12, 'atol_scale': 2e-15, 'max_step_divisor': 8.0},
    {'name': 'L3', 'rtol': 2e-13, 'atol_scale': 2e-16, 'max_step_divisor': 8.0},
    {'name': 'L3M', 'rtol': 2e-13, 'atol_scale': 2e-16, 'max_step_divisor': 16.0},
)
PILOT_BUDGETS = {
    'common_ic': {'gas_normalized': 1e-14, 'photon_max_abs_H': 1e-14,
                  'log_survivor_max_abs': 1e-10},
    'native_source': {'gas_normalized': 1e-10, 'photon_max_abs_H': 1e-12,
                      'log_survivor_max_abs': 1e-8},
}
POLICY = {
    'schema': 'C21G_BOUNDED_REFERENCE_REFINEMENT_POLICY_V1',
    'baseline_execution_commit': BASELINE_EXECUTION,
    'assessment_head': ASSESSMENT_HEAD, 'native_owner': OWNER,
    'fixtures': ['common_ic', 'native_source'], 'reference_tiers': TIERS,
    'new_native_subdivisions': [128, 256],
    'new_native_modes': ['FULLMID', 'MIDPHOTO_ENDMICRO'],
    'max_native_calls_per_job': 200000, 'max_reference_rhs_evaluations': 200000,
    'native_call_timeout_s': 15.0, 'wall_timeout_s_per_job': 300.0,
    'max_concurrent_jobs': 1, 'protected_cpu_ids': [55],
    'pilot_agreement_budgets': PILOT_BUDGETS,
    'budget_meaning': 'Predeclared endpoint comparison resolution for this bounded pilot; not a physical acceptance gate or certified error bound.',
    'global_error_bound': None,
    'reference_ready_rule': 'All reference jobs complete; native_source endpoint differences L1-L2, L2-L3 and L3-L3M meet each pilot budget. Mesh-cap inactivity is reported separately.',
    'holds': ['Full48', 'source-age', 'spectral', 'angular', 'Case B',
              'signed Bianchi', 'full EoR', 'standalone Grackle driver parity'],
}

def read_json(path):
    with Path(path).open(encoding='utf-8') as stream:
        return json.load(stream)

def canonical_hash(value):
    data = json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()
    return hashlib.sha256(data).hexdigest()

def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()

def write_new_json(path, value):
    """Atomically publish a new file; an existing path is never replaced."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.' + uuid.uuid4().hex + '.partial')
    try:
        with temporary.open('x', encoding='utf-8') as stream:
            json.dump(value, stream, indent=2, allow_nan=False)
            stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
        os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)

def file_record(path):
    path = Path(path)
    return {'bytes': path.stat().st_size, 'sha256': sha256(path)}

def fixture_scales(fixture):
    """Fixed dimensional scales. Positive energy scales follow from w0>0."""
    q, amounts, birth = (fixture[key] for key in ('q', 'amounts', 'birth'))
    gas = fixture['gas0']; helium = fixture['Y']; count = len(q)
    if not (len(amounts) == len(birth) == count and len(gas) == 4):
        raise ValueError('FIXTURE_SCALE_SHAPE')
    values = [*q, *amounts, *birth, *gas, helium]
    if not all(math.isfinite(x) for x in values):
        raise ValueError('FIXTURE_SCALE_NONFINITE')
    if gas[3] <= 0 or helium < 0 or any(a < 0 for a in amounts):
        raise ValueError('FIXTURE_SCALE_DOMAIN')
    binding = (BIND_EV[0], helium * BIND_EV[1], helium * (BIND_EV[1] + BIND_EV[2]))
    energy = gas[3] + math.fsum(b * g for b, g in zip(binding, gas[:3]))
    energy += math.fsum(a * qi * math.exp(-xb) for a, qi, xb in zip(amounts, q, birth))
    if not math.isfinite(energy) or energy <= 0:
        raise ValueError('FIXTURE_ENERGY_SCALE_DOMAIN')
    scales = [1.0] * (count + 19)
    scales[count + 3] = gas[3]
    for offset in (14, 15, 16, 17, 18):
        scales[count + offset] = energy
    return {'values': scales, 'thermal_eV_H': gas[3], 'energy_eV_H': energy,
            'definition': 'tau/fraction:1; number ledger:1 per H; thermal:w0; energy ledger:w0+initial binding+all fixed birth photon energy',
            'state_order': 'tau[M],gas[4],photo[3],ci[3],rr[3],dr,escape,cmb,photon_work,gas_work,heat',
            'state_floor_applied': False}

def reference_controls(fixture, tier):
    scales = fixture_scales(fixture)
    return {'rtol': tier['rtol'],
            'atol': [tier['atol_scale'] * x for x in scales['values']],
            'max_step_divisor': tier['max_step_divisor'],
            'max_evaluations': POLICY['max_reference_rhs_evaluations'],
            'scale_contract': scales}

def verify_files(root, records):
    root = Path(root).resolve()
    verified = {}
    for relative, expected in records.items():
        rel = Path(relative)
        if rel.is_absolute() or '..' in rel.parts:
            raise ValueError('MANIFEST_PATH_DOMAIN')
        path = root / rel
        if not path.is_file():
            raise ValueError('PINNED_FILE_MISSING ' + str(path))
        actual = file_record(path)
        if actual != {'bytes': expected['bytes'], 'sha256': expected['sha256']}:
            raise ValueError('PINNED_FILE_MISMATCH ' + str(path))
        verified[relative] = actual
    return verified

def verify_inputs(source_dir, baseline_dir, manifest_path=None):
    manifest = read_json(manifest_path or HERE / 'EXECUTION_MANIFEST.json')
    source = verify_files(source_dir, manifest['c21f_runtime_files'])
    baseline = verify_files(baseline_dir, manifest['baseline_files'])
    code = verify_files(HERE, manifest['c21g_runtime_files'])
    if manifest['policy_sha256'] != canonical_hash(POLICY):
        raise ValueError('PILOT_POLICY_MISMATCH')
    fixture_records = {}
    for name in POLICY['fixtures']:
        f = read_json(Path(baseline_dir) / name / 'fixture.json')
        digest = canonical_hash(f)
        reference = read_json(Path(baseline_dir) / name / 'radau.json')
        summary = read_json(Path(baseline_dir) / name / 'SUMMARY.json')
        if reference['fixture_sha256'] != digest or summary['fixture_sha256'] != digest:
            raise ValueError('BASELINE_FIXTURE_BINDING ' + name)
        if reference['microphysics'] != NATIVE_KIND or summary['microphysics'] != NATIVE_KIND:
            raise ValueError('BASELINE_NATIVE_KIND ' + name)
        if len(summary['cases']) != 12:
            raise ValueError('BASELINE_CASE_COUNT ' + name)
        fixture_records[name] = {'sha256': digest, 'cohorts': len(f['q']),
                                 'scales': fixture_scales(f)}
    return {'schema': 'C21G_VERIFIED_INPUTS_V1', 'manifest_path': str(Path(manifest_path or HERE / 'EXECUTION_MANIFEST.json').resolve()),
            'manifest_sha256': sha256(manifest_path or HERE / 'EXECUTION_MANIFEST.json'),
            'policy_sha256': canonical_hash(POLICY), 'c21f_runtime_files': source,
            'c21g_runtime_files': code, 'baseline_files': baseline,
            'fixtures': fixture_records, 'global_error_bound': None}

def verify_native_binary(binary, source_dir, build_dir=None):
    binary = Path(binary).resolve()
    record = file_record(binary)
    if record['sha256'] == NATIVE_BINARY_SHA256:
        return {'path': str(binary), **record, 'status': 'PR82_VERIFIED_BINARY_HASH_REUSED', 'owner': OWNER}
    if build_dir is None:
        raise ValueError('NEW_BINARY_REQUIRES_RECORDED_BUILD_DIRECTORY')
    build = Path(build_dir).resolve()
    if binary != build / 'native_point':
        raise ValueError('BUILD_BINARY_PATH_MISMATCH')
    if (build / 'owner_commit.txt').read_text().strip() != OWNER:
        raise ValueError('BUILD_OWNER_MISMATCH')
    if (build / 'build_exit.txt').read_text().strip() != 'exit_code=0':
        raise ValueError('BUILD_NOT_COMPLETED')
    rows = {}
    for line in (build / 'input_sha256.txt').read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        rows[Path(name.lstrip('*')).name] = digest
    wrapper_hash = sha256(Path(source_dir) / 'native/native_point.rs')
    if rows.get('native_point') != record['sha256'] or rows.get('native_point.rs') != wrapper_hash:
        raise ValueError('BUILD_INPUT_OR_BINARY_HASH_MISMATCH')
    archive = file_record(build / 'owner_source.tar')
    if rows.get('owner_source.tar') != archive['sha256']:
        raise ValueError('BUILD_OWNER_ARCHIVE_HASH_MISMATCH')
    return {'path': str(binary), **record, 'owner': OWNER,
            'status': 'RECORDED_PINNED_OWNER_BUILD', 'owner_source_archive': archive,
            'native_wrapper_sha256': wrapper_hash, 'build_directory': str(build),
            'meaning': 'Build-script provenance and actual hashes; not a claim of bit-reproducible toolchains.'}
