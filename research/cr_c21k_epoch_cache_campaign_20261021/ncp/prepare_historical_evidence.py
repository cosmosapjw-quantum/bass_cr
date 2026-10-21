"""Create exact receipt-named admission copies from the immutable native archive.

Never extractall, rewrite an old receipt, remove an archive sidecar, execute a
scientific program, or relax the original exact-payload verifier.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import sys
import tarfile

from scheduler import AdmissionError, file_record, read_json, utc, verify_external, write_new

HERE = Path(__file__).resolve().parent
ARCHIVE_PIN = {'bytes': 2568680, 'sha256': '2722e479b6205015a68f1393b8c537d21e63201bb57efd3cf850fe74e4668de3'}
BACKLOG_SHA256 = '3a329a1d593403a4c4d78f8f99eee3b9b521cece02734470738501791669c1eb'
PREFIX = 'C21GHI_NATIVE_EXECUTION_20261020/evidence'


def byte_record(raw):
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def safe_name(name, *, directory=False):
    if not isinstance(name, str) or '\\' in name or '\0' in name:
        raise AdmissionError('UNSAFE_ARCHIVE_OR_PAYLOAD_PATH')
    value = name[:-1] if directory and name.endswith('/') else name
    path = PurePosixPath(value)
    if (not value or path.is_absolute() or any(part in ('', '.', '..') for part in value.split('/'))
        or str(path) != value):
        raise AdmissionError('UNSAFE_ARCHIVE_OR_PAYLOAD_PATH')
    return value


def json_bytes(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise AdmissionError('DUPLICATE_RECEIPT_JSON_KEY')
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=unique,
        parse_constant=lambda value: (_ for _ in ()).throw(AdmissionError('NONFINITE_RECEIPT_JSON')))


def prepare(archive, output):
    archive, output = Path(archive), Path(output)
    if not archive.is_absolute() or not output.is_absolute():
        raise AdmissionError('ABSOLUTE_ARCHIVE_AND_NEW_OUTPUT_REQUIRED')
    if archive.is_symlink():
        raise AdmissionError('REGULAR_ORIGINAL_ARCHIVE_REQUIRED')
    if output.exists() or output.is_symlink():
        raise AdmissionError('CREATE_ONLY_OUTPUT_ALREADY_EXISTS')
    archive = archive.resolve(strict=True)
    output = output.resolve()
    raw = archive.read_bytes()
    if byte_record(raw) != ARCHIVE_PIN:
        raise AdmissionError('ORIGINAL_ARCHIVE_IDENTITY_MISMATCH')
    backlog_path = HERE / 'BACKLOG_INVENTORY.json'
    if file_record(backlog_path)['sha256'] != BACKLOG_SHA256:
        raise AdmissionError('PINNED_BACKLOG_INVENTORY_REQUIRED')
    backlog = read_json(backlog_path)
    nodes = backlog['completed_external_nodes']
    if len(nodes) != 3:
        raise AdmissionError('EXACT_THREE_HISTORICAL_NODES_REQUIRED')
    staged, jobs, excluded = {}, [], []
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as bundle:
        members = {}
        for member in bundle.getmembers():
            name = safe_name(member.name, directory=member.isdir())
            if name in members:
                raise AdmissionError('DUPLICATE_ARCHIVE_MEMBER')
            if not (member.isfile() or member.isdir()):
                raise AdmissionError('ARCHIVE_LINK_OR_SPECIAL_MEMBER_FORBIDDEN')
            members[name] = member

        def take(name, expected=None):
            item = members.get(name)
            if item is None or not item.isfile():
                raise AdmissionError('REQUIRED_ARCHIVE_FILE_MISSING')
            value = bundle.extractfile(item).read()
            if len(value) != item.size or (expected is not None and byte_record(value) != expected):
                raise AdmissionError('ARCHIVE_NAMED_PAYLOAD_IDENTITY_MISMATCH')
            return value

        for node in nodes:
            directory = safe_name(node['original_return_directory_name'])
            if '/' in directory:
                raise AdmissionError('HISTORICAL_JOB_DIRECTORY_MUST_BE_ONE_COMPONENT')
            prefix = PREFIX + '/' + directory + '/'
            pin = {key: node['receipt'][key] for key in ('bytes', 'sha256')}
            receipt_raw = take(prefix + 'JOB_RECEIPT.json', pin)
            receipt = json_bytes(receipt_raw)
            if (receipt.get('execution') != 'COMPLETE' or receipt.get('command') != 'native'
                or receipt.get('native_exit_code') != 0 or not isinstance(receipt.get('payload_files'), dict)):
                raise AdmissionError('HISTORICAL_COMPLETE_NATIVE_RECEIPT_REQUIRED')
            names = {'JOB_RECEIPT.json'}
            staged[directory + '/JOB_RECEIPT.json'] = receipt_raw
            for payload, expected in receipt['payload_files'].items():
                payload = safe_name(payload)
                if payload == 'JOB_RECEIPT.json':
                    raise AdmissionError('RECEIPT_CANNOT_SELF_LIST_AS_PAYLOAD')
                names.add(payload)
                staged[directory + '/' + payload] = take(prefix + payload, expected)
            extra = []
            for name, member in members.items():
                if member.isfile() and name.startswith(prefix) and name[len(prefix):] not in names:
                    relative = name[len(prefix):]
                    # This immutable archive is known to contain exactly this
                    # one unlisted execution-wrapper sidecar per returned job.
                    if relative != 'runner_exit_code.txt':
                        raise AdmissionError('UNEXPECTED_UNLISTED_HISTORICAL_JOB_FILE')
                    extra.append({'archive_member': name, **byte_record(take(name))})
            if len(extra) != 1:
                raise AdmissionError('EXPECTED_ORIGINAL_WRAPPER_SIDECAR_NOT_FOUND')
            excluded.extend(extra)
            jobs.append({'job_id': node['job_id'], 'directory': directory,
                'receipt': pin, 'payload_file_count': len(receipt['payload_files']),
                'strict_payload_verification': 'PENDING'})

    # All pinned source bytes and archive paths are checked before any output.
    output.mkdir(parents=True, exist_ok=False)
    for name, value in sorted(staged.items()):
        path = output.joinpath(*PurePosixPath(name).parts)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('xb') as stream:
            stream.write(value)
    for job in jobs:
        verify_external({'receipt_file': str(output / job['directory'] / 'JOB_RECEIPT.json'),
            'receipt_record': job['receipt'], 'success': [
                {'path': 'execution', 'equals': 'COMPLETE'},
                {'path': 'command', 'equals': 'native'},
                {'path': 'native_exit_code', 'equals': 0}]})
        job['strict_payload_verification'] = 'PASS_UNCHANGED_SCHEDULER_VERIFIER'
    if file_record(archive) != ARCHIVE_PIN:
        raise AdmissionError('ORIGINAL_ARCHIVE_CHANGED_DURING_STAGING')
    receipt = {'schema': 'C21K_HISTORICAL_EVIDENCE_STAGING_V1', 'status': 'COMPLETE',
        'created_at_utc': utc(), 'original_archive': {'name': archive.name, **ARCHIVE_PIN},
        'backlog_inventory': file_record(backlog_path), 'helper': file_record(Path(__file__)),
        'jobs': jobs, 'staged_file_count': len(staged), 'staged_bytes': sum(map(len, staged.values())),
        'excluded_from_admission_copy_preserved_in_original_archive': excluded,
        'preservation': 'Original archive and all sidecars remain byte-identical. Original receipts and every named payload are copied verbatim; no receipt rewrite or verifier relaxation.',
        'binding': 'native_return_evidence must be this new output root. STAGING_RECEIPT.json stays outside the three per-job directories.',
        'current_fd_parent_context_admission': 'SEPARATE_UNCHANGED_ORIGINAL_RUNNER_GUARD',
        'native_execution': 'NOT_RUN', 'global_error_bound': None}
    write_new(output / 'STAGING_RECEIPT.json', receipt)
    return receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = prepare(args.archive, args.out)
    except (OSError, ValueError, KeyError, tarfile.TarError, AdmissionError) as exc:
        print(json.dumps({'status': 'BLOCKED_HISTORICAL_STAGING', 'error': type(exc).__name__ + ': ' + str(exc),
            'native_execution': 'NOT_RUN', 'global_error_bound': None}), file=sys.stderr)
        return 2
    print(json.dumps({'status': result['status'], 'jobs': len(result['jobs']),
        'payload_files': sum(job['payload_file_count'] for job in result['jobs']),
        'staged_files_including_receipts': result['staged_file_count'],
        'original_sidecars_preserved': len(result['excluded_from_admission_copy_preserved_in_original_archive']),
        'strict_payload_verification': 'PASS', 'native_execution': 'NOT_RUN', 'global_error_bound': None}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
