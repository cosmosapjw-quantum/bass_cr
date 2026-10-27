#!/usr/bin/env python3
"""Populate missing local Git blobs only from bytes matching the exact S tree.

This is explicit local object hydration, not a network readback or R3 test.
No source module is imported and no scientific calculation is performed.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--S', required=True)
    parser.add_argument('--receipt', required=True)
    args = parser.parse_args()
    root = Path('/workspace/scratch/865c84d871b7')
    repo = root / 'bass_cr'
    receipt = Path(args.receipt)
    if receipt.exists():
        raise ValueError('create-only hydration receipt required')
    env = {**os.environ, 'GIT_NO_LAZY_FETCH': '1'}

    def git(*command, data=None):
        result = subprocess.run(['git', '-c', 'protocol.allow=never', '-C', str(repo), *command],
                                input=data, capture_output=True, env=env, check=True)
        return result.stdout

    state = json.loads((root / 'parent_ops/pub_state.json').read_bytes())
    if state['head'] != args.S or git('rev-parse', 'HEAD').decode().strip() != args.S:
        raise ValueError('current publication and local HEAD must equal S')
    if len(state['stages']) != 19 or state['stages'][-1]['stage'] != 'C09':
        raise ValueError('actual 19-stage C09 source required')
    published = set(json.loads((root / 'parent_ops/published_paths.json').read_bytes()))
    tree = {}
    for record in git('ls-tree', '-r', '-z', args.S).split(b'\0'):
        if not record:
            continue
        header, name = record.split(b'\t', 1)
        mode, kind, blob = header.decode().split()
        name = name.decode()
        if name.startswith('research/cr_parent_event_native25_20261028/') or name in published:
            if mode not in ('100644', '100755') or kind != 'blob':
                raise ValueError('regular published blob required')
            tree[name] = blob
    rows, pending = [], []
    for name, blob in sorted(tree.items()):
        check = git('cat-file', '--batch-check', data=(blob+'\n').encode()).decode().strip()
        if not check.endswith(' missing'):
            continue
        path = repo / name
        if not path.is_file() or path.is_symlink():
            raise ValueError('explicit network acquisition required for missing local payload: '+name)
        raw = path.read_bytes()
        actual = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        if actual != blob:
            raise ValueError('local bytes do not equal exact S blob: '+name)
        pending.append((name, blob, raw))
    # All prospective bytes are checked before writing any object.
    for name, blob, raw in pending:
        written = git('hash-object', '-w', '--stdin', data=raw).decode().strip()
        if written != blob:
            raise ValueError('content-addressed local write mismatch')
        rows.append({'path': name, 'git_blob_sha1': blob, 'bytes': len(raw),
                     'sha256': hashlib.sha256(raw).hexdigest()})
    result = {'schema': 'CR_PARENT_EVENT_LOCAL_S_BLOB_HYDRATION_V1',
              'unit': 'CR_PHYS02_PARENT_EVENT_NATIVE25_V1', 'S': args.S,
              'published_paths_checked': len(tree), 'local_blobs_populated': len(rows),
              'files': rows, 'network_requests': 0, 'provider_or_Git_raw_R3': False,
              'scientific_execution': False, 'old_science_replays': 0,
              'metadata_CPU_s': None, 'branch_or_ref_mutation': False}
    with receipt.open('x') as handle:
        json.dump(result, handle, indent=2)
        handle.write('\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'files'}))


if __name__ == '__main__':
    main()
