#!/usr/bin/env python3
"""Create-only exact envelope of frozen G core and late actual F HOLD evidence.

Usage: python assemble_outer.py --spec /ABS/SPEC.json --out-dir /ABS/NEW_OR_EXISTING_OUTPUT
The spec supplies name, science_commit, science_tree, status and files. Each files
entry supplies local_path, bytes, sha256 and origin. Without --out-dir, the spec's
parent directory is used. This helper does not restore or execute either payload.
"""
import argparse
import hashlib
import json
import os
import pathlib
import re
import stat
import sys
import time
import zipfile

SCHEMA = 'cr-phys02g-late-f-hold-envelope.v1'
MANIFEST = 'BUNDLE_MANIFEST.json'
RECEIPT = 'OUTER_ASSEMBLY_RECEIPT.json'


def utc():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


def sha_file(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def safe_name(name):
    if not isinstance(name, str):
        raise ValueError('OUTER_MEMBER_NAME_MUST_BE_STRING')
    p = pathlib.PurePosixPath(name)
    if (not name or '\\' in name or p.is_absolute() or p.as_posix() != name
            or any(part in ('.', '..') for part in p.parts)
            or any(ord(c) < 32 or ord(c) == 127 for c in name)
            or re.match(r'^[A-Za-z]:', name)):
        raise ValueError('UNSAFE_OUTER_MEMBER ' + repr(name))
    return name


def no_symlink_path(path):
    """Check every original lexical component before resolving it."""
    path = pathlib.Path(path)
    if not path.is_absolute() or '..' in path.parts:
        raise ValueError('ABSOLUTE_NONTRAVERSING_LOCAL_PATH_REQUIRED')
    for component in (path, *path.parents):
        if component.is_symlink():
            raise ValueError('SYMLINK_PATH_FORBIDDEN ' + str(component))
    return path


def origin_without_local_paths(origin):
    """Keep root-provided provenance but forbid leaking absolute local paths."""
    if isinstance(origin, str):
        if (pathlib.PurePosixPath(origin).is_absolute()
                or pathlib.PureWindowsPath(origin).is_absolute()
                or re.search(r'(^|\s)(?:/workspace/|/tmp/|/root/|[A-Za-z]:[\\/])', origin)):
            raise ValueError('ABSOLUTE_LOCAL_PATH_IN_ORIGIN')
    elif isinstance(origin, dict):
        for k, value in origin.items():
            if not isinstance(k, str):
                raise ValueError('ORIGIN_KEY_MUST_BE_STRING')
            origin_without_local_paths(k)
            origin_without_local_paths(value)
    elif isinstance(origin, list):
        for value in origin:
            origin_without_local_paths(value)
    elif origin is not None and not isinstance(origin, (bool, int, float)):
        raise ValueError('ORIGIN_NOT_JSON_SERIALIZABLE')
    return origin


def identity(path, info, label):
    if path.stat().st_size != info['bytes'] or sha_file(path) != info['sha256']:
        raise ValueError('INPUT_IDENTITY_MISMATCH ' + label)


def write_json_exclusive(path, value):
    with path.open('x', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())


def assemble(spec_path, output_dir=None):
    start = time.monotonic()
    started_utc = utc()
    spec_path = no_symlink_path(pathlib.Path(spec_path))
    if not spec_path.is_file():
        raise ValueError('SPEC_FILE_REQUIRED')
    spec_raw = spec_path.read_bytes()
    spec = json.loads(spec_raw)
    if set(spec) != {'name', 'science_commit', 'science_tree', 'status', 'files'}:
        raise ValueError('EXACT_SPEC_FIELDS_REQUIRED')
    name = safe_name(spec['name'])
    if pathlib.PurePosixPath(name).name != name or not name.endswith('.zip'):
        raise ValueError('UNIQUE_ZIP_BASENAME_REQUIRED')
    for key in ('science_commit', 'science_tree'):
        if not isinstance(spec[key], str) or not re.fullmatch('[0-9a-f]{40}', spec[key]):
            raise ValueError('EXACT_GIT_ID_REQUIRED ' + key)
    if not isinstance(spec['status'], str) or not spec['status']:
        raise ValueError('ROOT_STATUS_REQUIRED')
    if not isinstance(spec['files'], dict) or not spec['files']:
        raise ValueError('NONEMPTY_EXACT_FILE_MAP_REQUIRED')
    output_dir = no_symlink_path(pathlib.Path(output_dir) if output_dir else spec_path.parent)
    archive = output_dir / name
    receipt_path = output_dir / RECEIPT
    if archive.exists() or archive.is_symlink() or receipt_path.exists() or receipt_path.is_symlink():
        raise FileExistsError('CREATE_ONLY_ARCHIVE_AND_RECEIPT_REQUIRED')
    if output_dir.exists() and not output_dir.is_dir():
        raise ValueError('OUTPUT_DIRECTORY_REQUIRED')

    sources = {}
    files = {}
    for member, info in spec['files'].items():
        safe_name(member)
        if member in (MANIFEST, RECEIPT):
            raise ValueError('RESERVED_OUTER_MEMBER ' + member)
        if not isinstance(info, dict) or set(info) != {'local_path', 'bytes', 'sha256', 'origin'}:
            raise ValueError('EXACT_INPUT_ENTRY_FIELDS_REQUIRED ' + member)
        if isinstance(info['bytes'], bool) or not isinstance(info['bytes'], int) or info['bytes'] < 0:
            raise ValueError('NONNEGATIVE_INTEGER_BYTES_REQUIRED ' + member)
        if not isinstance(info['sha256'], str) or not re.fullmatch('[0-9a-f]{64}', info['sha256']):
            raise ValueError('SHA256_REQUIRED ' + member)
        path = no_symlink_path(pathlib.Path(info['local_path']))
        if not path.is_file() or not stat.S_ISREG(path.stat().st_mode):
            raise ValueError('REGULAR_INPUT_FILE_REQUIRED ' + member)
        if path == archive or path == receipt_path:
            raise ValueError('OUTPUT_CANNOT_BE_INPUT')
        identity(path, info, member)
        sources[member] = path
        files[member] = {'bytes': info['bytes'], 'sha256': info['sha256'],
                         'origin': origin_without_local_paths(info['origin'])}

    manifest = {'schema': SCHEMA, 'name': name,
                'science_commit': spec['science_commit'], 'science_tree': spec['science_tree'],
                'status': spec['status'], 'self_excluded': MANIFEST, 'files': files,
                'payload_policy': 'Frozen G core and original actual F HOLD evidence retained byte-identical',
                'execution': 'Packaging only; no F retry, G frontier execution, restore, plan or numerical rerun'}
    manifest_raw = (json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8')
    output_dir.mkdir(parents=True, exist_ok=True)
    no_symlink_path(output_dir)
    # Exclusive archive creation never overwrites an older successful or failed envelope.
    with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED) as z:
        for member in sorted(sources):
            path = no_symlink_path(sources[member])
            # Pin checks directly before writing limit accidental input changes during assembly.
            identity(path, files[member], member)
            compression = zipfile.ZIP_STORED if member.lower().endswith(('.zip', '.tar.gz', '.tgz')) else zipfile.ZIP_DEFLATED
            z.write(path, arcname=member, compress_type=compression)
        z.writestr(MANIFEST, manifest_raw, compress_type=zipfile.ZIP_DEFLATED)
    with archive.open('rb') as f:
        os.fsync(f.fileno())

    # Exactly one completed-archive pass checks the complete member set and each payload.
    expected = set(files) | {MANIFEST}
    verified = 0
    with zipfile.ZipFile(archive, 'r') as z:
        infos = z.infolist()
        names = [info.filename for info in infos]
        if len(names) != len(set(names)) or set(names) != expected:
            raise ValueError('OUTER_EXACT_ZIP_MEMBERSHIP_MISMATCH')
        for info in infos:
            safe_name(info.filename)
            if info.is_dir() or stat.S_ISLNK(info.external_attr >> 16):
                raise ValueError('OUTER_DIRECTORY_OR_SYMLINK_FORBIDDEN')
            if info.filename == MANIFEST:
                if z.read(info.filename) != manifest_raw:
                    raise ValueError('OUTER_MANIFEST_BYTES_MISMATCH')
                continue
            pin = files[info.filename]
            if info.file_size != pin['bytes']:
                raise ValueError('OUTER_ENTRY_SIZE_MISMATCH ' + info.filename)
            h = hashlib.sha256()
            count = 0
            with z.open(info.filename, 'r') as f:
                for block in iter(lambda: f.read(1024 * 1024), b''):
                    count += len(block)
                    h.update(block)
            if count != pin['bytes'] or h.hexdigest() != pin['sha256']:
                raise ValueError('OUTER_ENTRY_HASH_MISMATCH ' + info.filename)
            verified += 1
    receipt = {'schema': 'cr-phys02g-outer-assembly-receipt.v1', 'status': 'PASS_EXACT_PACKAGING_ONLY',
               'name': name, 'bytes': archive.stat().st_size, 'sha256': sha_file(archive),
               'spec_sha256': hashlib.sha256(spec_raw).hexdigest(),
               'bundle_manifest_sha256': hashlib.sha256(manifest_raw).hexdigest(),
               'science_commit': spec['science_commit'], 'science_tree': spec['science_tree'],
               'root_status': spec['status'], 'payload_files': len(files), 'verified_payload_files': verified,
               'zip_entries': len(expected), 'exact_membership': True,
               'completed_archive_verification_passes': 1,
               'start_utc': started_utc, 'end_utc': utc(), 'elapsed_s': time.monotonic() - start,
               'actual_exit': 0, 'physical_G_calls': 0, 'linear_solve_calls': 0, 'pulse_calls': 0, 'expm_calls': 0,
               'F_retry_authorized': False, 'actual_frontier_execution': False,
               'frozen_core_modified': False, 'source_restore_or_plan_rerun': False}
    write_json_exclusive(receipt_path, receipt)
    return receipt


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--spec', required=True, help='Absolute exact root-provided JSON spec path')
    p.add_argument('--out-dir', help='Absolute output directory; default is spec parent')
    a = p.parse_args()
    print(json.dumps(assemble(a.spec, a.out_dir), ensure_ascii=False, indent=2, allow_nan=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
