"""Read frozen TP2D bytes without extracting or approximating query identities."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import stat
import zipfile

import numpy as np

RAW_KEYS = ('S_tp', 'S_pt', 'H_tp', 'H_pt', 'D_tp', 'D_pt')


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass(frozen=True)
class QueryEvidence:
    representative: dict
    record: dict
    arrays: dict[str, np.ndarray]


class ArchiveEvidence:
    def __init__(self, path, contract, representatives):
        self.path = Path(path)
        pin = contract['historical_tp2d_archive']
        data = self.path.read_bytes()
        if len(data) != pin['bytes'] or _sha(data) != pin['sha256']:
            raise ValueError('archive SHA/size mismatch')
        self.z = zipfile.ZipFile(io.BytesIO(data))
        names = self.z.namelist()
        if len(names) != len(set(names)):
            raise ValueError('duplicate ZIP member')
        for member in self.z.infolist():
            name = member.filename
            parts = PurePosixPath(name)
            if (not name or name.startswith('/') or '\\' in name or '..' in parts.parts
                    or stat.S_ISLNK(member.external_attr >> 16)):
                raise ValueError('unsafe ZIP member')
        if self.z.testzip() is not None:
            raise ValueError('archive CRC mismatch')
        if 'MANIFEST.json' not in names:
            raise ValueError('missing MANIFEST.json')
        manifest = json.loads(self.z.read('MANIFEST.json'))
        if set(manifest) != set(names) - {'MANIFEST.json'}:
            raise ValueError('missing or extra manifest entry')
        for name, entry in manifest.items():
            payload = self.z.read(name)
            if len(payload) != entry['bytes'] or _sha(payload) != entry['sha256']:
                raise ValueError('archive member hash/size mismatch: ' + name)
        self.manifest = manifest
        self.contract = contract
        self.representatives = representatives
        queries = representatives.get('queries', [])
        if len(queries) != representatives.get('query_count') or len({q['query_id'] for q in queries}) != len(queries):
            raise ValueError('representative query count/identity mismatch')
        self.basis()
        for query in queries:
            self.query(query)

    def basis(self):
        for name in ('BASIS.json', 'BASIS.npz'):
            if name not in self.manifest:
                raise ValueError('missing BASIS member')
        raw_json = self.z.read('BASIS.json')
        raw_npz = self.z.read('BASIS.npz')
        policy = self.contract.get('basis_policy', {})
        for name, raw, key in (('BASIS.json', raw_json, 'json_sha256'),
                               ('BASIS.npz', raw_npz, 'npz_sha256')):
            if key in policy and _sha(raw) != policy[key]:
                raise ValueError('BASIS byte tamper: ' + name)
        record = json.loads(raw_json)
        with np.load(io.BytesIO(raw_npz), allow_pickle=False) as f:
            arrays = {key: np.array(f[key]) for key in f.files}
        if set(arrays) != {'edges', 'coefficients'}:
            raise ValueError('BASIS payload shape/keys mismatch')
        return {'json_bytes': raw_json, 'npz_bytes': raw_npz, 'record': record, 'npz_arrays': arrays}

    def materialize_basis(self, directory):
        directory = Path(directory)
        if directory.exists():
            raise FileExistsError('basis destination exists')
        basis = self.basis()
        directory.mkdir(parents=True)
        for name, data in (('BASIS.json', basis['json_bytes']), ('BASIS.npz', basis['npz_bytes'])):
            with (directory / name).open('xb') as f:
                f.write(data)
        return directory

    def query(self, representative):
        if representative not in self.representatives['queries']:
            raise ValueError('query outside representative contract')
        qid = representative['query_id']
        prefix = 'runtime_queries/' + qid
        jname, nname = prefix + '.json', prefix + '.npz'
        if jname not in self.manifest or nname not in self.manifest:
            raise ValueError('missing representative query JSON/NPZ')
        raw_json, raw_npz = self.z.read(jname), self.z.read(nname)
        if _sha(raw_json) != representative['json_sha256'] or _sha(raw_npz) != representative['npz_sha256']:
            raise ValueError('representative query JSON/NPZ hash mismatch')
        record = json.loads(raw_json)
        time_hex = representative['time_hex']
        if (record.get('schema') != 'BASS_TP2D_QUALIFIED_RUNTIME_QUERY_V1'
                or record.get('query_id') != qid or record.get('time_hex') != time_hex
                or float.fromhex(time_hex).hex() != time_hex):
            raise ValueError('query time/identity mismatch')
        expected_qid = _sha(json.dumps({'schema': 'BASS_TP2D_RUNTIME_QUERY_V1',
                    'context_id': record['context_id'], 'time_hex': time_hex},
                    sort_keys=True, separators=(',', ':')).encode())
        if expected_qid != qid:
            raise ValueError('query identity mismatch')
        selected = record['qualification']['selected_resolution']
        if selected != representative['selected_resolution']:
            raise ValueError('query selected resolution drift')
        attempts = record['attempts']
        if not attempts or attempts[-1]['resolution'] != selected:
            raise ValueError('query attempt/selected resolution mismatch')
        ladder = self.contract.get('runtime_reference_resolutions')
        if ladder is not None and [x['resolution'] for x in attempts] != ladder[:len(attempts)]:
            raise ValueError('query resolution ladder drift')
        if record.get('payload_sha256') != _sha(raw_npz):
            raise ValueError('query payload receipt hash mismatch')
        with np.load(io.BytesIO(raw_npz), allow_pickle=False) as f:
            arrays = {key: np.array(f[key]) for key in f.files}
        required = {'selected__S', 'selected__H', 'selected__D'}
        for attempt in attempts:
            r = attempt['resolution']
            tag = f"q{r['order']}_h{r['subdivisions']}"
            required.update(f'{tag}__{key}' for key in RAW_KEYS)
        if not required <= set(arrays):
            raise ValueError('missing historical selected/attempted array')
        if any(not np.isfinite(arrays[key]).all() for key in required):
            raise ValueError('nonfinite historical array')
        return QueryEvidence(representative, record, arrays)


def open_evidence(archive_path, contract, representatives):
    return ArchiveEvidence(archive_path, contract, representatives)
