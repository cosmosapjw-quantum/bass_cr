"""Read-only free-block/inode admission for create-only C21N run outputs.

An observation is not a filesystem reservation or an enforcement of user quotas.
Use blocks/inodes available to this process, never privileged reserved capacity.
Unknown capacity and read-only/unwritable paths fail closed before run creation.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import time

MIB = 1024**2
GIB = 1024**3


class StorageAdmissionError(RuntimeError):
    def __init__(self, receipt):
        self.receipt = receipt
        super().__init__('STORAGE_PREFLIGHT_BLOCKED:' + ','.join(receipt['reasons']))


def budget_for(remaining_cases, missing_directories=0):
    if (isinstance(remaining_cases, bool) or not isinstance(remaining_cases, int)
            or remaining_cases < 0 or missing_directories < 0):
        raise ValueError('INVALID_REMAINING_STORAGE_TASK_COUNT')
    # Planning allowances, not measured compression/RSS/speedup claims.
    # 40x101 FP64 state plus 128 scalar channels and four 9x101 moment arrays
    # occupies <0.2 MiB before NPZ/JSON overhead. 8 MiB/case allows ample slack.
    # Six current inode consumers: directory + RESERVATION/STARTED/history/
    # RESULT/COMPLETE. Eight includes margin. No plot/backup campaign is budgeted.
    case_bytes, case_inodes = 8 * MIB, 8
    coordinator_bytes, coordinator_inodes = 64 * MIB, 32
    reserve_bytes, reserve_inodes = 2 * GIB, 256
    return {
        'remaining_cases': remaining_cases,
        'case_output_budget_bytes': case_bytes,
        'case_output_budget_inodes': case_inodes,
        'coordinator_output_budget_bytes': coordinator_bytes,
        'coordinator_output_budget_inodes': coordinator_inodes,
        'reserve_bytes': reserve_bytes, 'reserve_inodes': reserve_inodes,
        'missing_directory_inodes': missing_directories,
        'required_available_bytes': reserve_bytes + coordinator_bytes + case_bytes * remaining_cases,
        'required_available_inodes': reserve_inodes + coordinator_inodes + case_inodes * remaining_cases + missing_directories,
        'budget_scope': 'run raw/receipts/coordinator only; exclude later plots and archives',
        'budget_basis': 'conservative analytical allowance; no measured storage improvement claim',
    }


def observe(output, remaining_cases, *, statvfs=None, access=None):
    """Inspect the nearest existing ancestor without creating any path."""
    path = Path(output).resolve()
    probe, missing = path, 0
    while not probe.exists():
        probe = probe.parent
        missing += 1
    receipt = {
        'schema': 'C21N_STORAGE_PREFLIGHT_V1',
        'observed_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'output_path': str(path), 'probed_existing_path': str(probe),
        'budget': budget_for(remaining_cases, missing),
        'statvfs_basis': 'f_bavail * f_frsize (fallback f_bsize), f_favail',
        'reasons': [], 'output_created': False,
        'capacity_reserved': False, 'user_or_project_quota_verified': False,
    }
    if not probe.is_dir():
        receipt['reasons'].append('EXISTING_ANCESTOR_NOT_DIRECTORY')
    try:
        writable = (os.access if access is None else access)(probe, os.W_OK | os.X_OK)
        receipt['writable_searchable_existing_directory'] = bool(writable)
        if not writable:
            receipt['reasons'].append('OUTPUT_ANCESTOR_NOT_WRITABLE')
        v = (os.statvfs if statvfs is None else statvfs)(probe)
        raw = {key: int(getattr(v, key)) for key in
               ('f_bsize', 'f_frsize', 'f_blocks', 'f_bfree', 'f_bavail',
                'f_files', 'f_ffree', 'f_favail', 'f_flag')}
        receipt['statvfs'] = raw
        block_size = raw['f_frsize'] or raw['f_bsize']
        if block_size <= 0 or raw['f_bavail'] < 0 or raw['f_blocks'] <= 0:
            receipt['reasons'].append('AVAILABLE_BLOCKS_UNKNOWN')
        else:
            receipt['available_bytes'] = raw['f_bavail'] * block_size
            if receipt['available_bytes'] < receipt['budget']['required_available_bytes']:
                receipt['reasons'].append('INSUFFICIENT_AVAILABLE_BYTES')
        if raw['f_files'] <= 0 or raw['f_favail'] < 0:
            receipt['reasons'].append('AVAILABLE_INODES_UNKNOWN')
        else:
            receipt['available_inodes'] = raw['f_favail']
            if receipt['available_inodes'] < receipt['budget']['required_available_inodes']:
                receipt['reasons'].append('INSUFFICIENT_AVAILABLE_INODES')
        if raw['f_flag'] & getattr(os, 'ST_RDONLY', 1):
            receipt['reasons'].append('FILESYSTEM_READ_ONLY')
    except (OSError, AttributeError, TypeError, ValueError) as error:
        receipt['reasons'].append('STORAGE_OBSERVATION_UNAVAILABLE')
        receipt['observation_error'] = f'{type(error).__name__}: {error}'
    receipt['status'] = 'PASS_SCOPED' if not receipt['reasons'] else 'BLOCKED'
    return receipt


def require(output, remaining_cases):
    receipt = observe(output, remaining_cases)
    if receipt['status'] != 'PASS_SCOPED':
        raise StorageAdmissionError(receipt)
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--cases', type=int, required=True)
    args = parser.parse_args()
    receipt = observe(args.output, args.cases)
    print(json.dumps(receipt, indent=2, sort_keys=True, allow_nan=False))
    return 0 if receipt['status'] == 'PASS_SCOPED' else 3


if __name__ == '__main__':
    raise SystemExit(main())
