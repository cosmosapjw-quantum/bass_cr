"""Additive finalized-evidence reuse, not legacy interrupted-run resume.

No native engine is loaded or built. Legacy receipts, IDs, context and NPZ bytes
are immutable. A numerical descriptor indexes only this admitted artifact set;
it does not issue compatibility grants for another engine, host or dataset.
"""
from __future__ import annotations
from dataclasses import dataclass
import copy
import math
from pathlib import Path
from types import MappingProxyType

import numpy as np

from .integrity import (AuditError, canonical, checked_bytes, file_bytes, read_npy,
                        read_zip, sha, strict_json, write_new, write_json_new)

RAW = ('S_tp', 'S_pt', 'H_tp', 'H_pt', 'D_tp', 'D_pt')
FULL = ('S', 'H', 'D')
PIN_PATH = Path(__file__).with_name('INPUT_PINS.json')


@dataclass
class Inputs:
    root: Path
    pins: dict
    payloads: dict[str, bytes]
    documents: dict
    historical: dict[str, bytes]
    source_closure_sha256: str


def load_inputs(repo_root: Path, pins_path: Path = PIN_PATH) -> Inputs:
    root = Path(repo_root).absolute()
    pins = strict_json(Path(pins_path).read_bytes())
    if pins['schema'] != 'BASS_R3_INPUT_PINS_V1':
        raise AuditError('R3_INPUT_SCHEMA', 'unsupported pin schema')
    payloads = {key: file_bytes(root, row['path'], row) for key, row in pins['files'].items()}
    docs = {key: strict_json(value) for key, value in payloads.items()
            if pins['files'][key]['path'].endswith('.json')}
    for rel, row in pins['source_closure'].items():
        file_bytes(root, rel, row)
    closure = sha(canonical(pins['source_closure']))
    f0, rep, summary = docs['f0_closure'], docs['r2_report'], docs['r2_summary']
    if (f0.get('status') != 'F0_DURABLE_CLOSED' or rep.get('status') != 'F1_ENGINE_ADMISSION_PASS'
            or rep.get('first_failure') is not None or rep.get('claim_ceiling') != pins['claim_ceiling']
            or summary.get('persisted') != pins['expected_task_pairs'] or summary.get('failed') != 0):
        raise AuditError('R3_PREDECESSOR_STATE', 'required finalized admission state mismatch')
    # Check publisher's evidence manifest as well as our external pins.
    for row in docs['r2_manifest']['files']:
        file_bytes(root, row['published_path'], row['published'])
    engine, build = docs['engine_identity'], docs['engine_build']
    unsigned = {k: v for k, v in engine.items() if k != 'identity_sha256'}
    if sha(canonical(unsigned)) != engine.get('identity_sha256'):
        raise AuditError('R3_ENGINE_RECEIPT', 'legacy self-digest mismatch')
    for key in ('source_sha256', 'library_sha256', 'machine', 'system', 'argv', 'compiler_version'):
        if engine[key] != build[key]:
            raise AuditError('R3_ENGINE_RECEIPT', key)
    if engine['argv'][1:-3] != docs['f1_contract']['build_policy']['required_flags']:
        raise AuditError('R3_ENGINE_FLAGS', 'not the admitted build argv')
    historical = read_zip(payloads['historical_archive'], max_bytes=256*1024**2, max_members=10000)
    manifest = strict_json(historical['MANIFEST.json'])
    if set(manifest) != set(historical)-{'MANIFEST.json'}:
        raise AuditError('R3_HISTORICAL_MANIFEST', 'coverage mismatch')
    for name, row in manifest.items():
        checked_bytes(historical[name], row, name)
    for name, row in pins['historical_members'].items():
        checked_bytes(historical[name], row, name)
    basis = strict_json(historical['BASIS.json'])
    if basis['matrix_sha256'] != sha(historical['BASIS.npz']):
        raise AuditError('R3_BASIS_IDENTITY', 'basis matrix byte identity mismatch')
    basis_members = read_zip(historical['BASIS.npz'], max_bytes=10*1024**2, max_members=16)
    if set(basis_members) != {k+'.npy' for k in pins['basis_array_metadata']}:
        raise AuditError('R3_BASIS_ARRAYS', 'keys mismatch')
    for key, row in pins['basis_array_metadata'].items():
        read_npy(basis_members[key+'.npy'], shape=tuple(row['shape']), dtype=row['dtype'])
    docs['science_context'] = strict_json(historical['SCIENCE_CONTEXT.json'])
    docs['basis'] = basis
    return Inputs(root, pins, payloads, docs, historical, closure)


def numerical_descriptor(inputs: Inputs, engine: dict | None = None) -> dict:
    """Projection of verified provenance, not proof of equivalence for new engines.

    The caller of this low-level pure function owns verification. CLI always uses
    load_inputs first. Source/output paths remain in the legacy receipt, outside
    this descriptor. No field is removed from or rewritten in that receipt.
    """
    d = inputs.documents
    engine = d['engine_identity'] if engine is None else engine
    science = d['science_context']['context']
    contract = science['contract']
    return {
        'schema': 'BASS_R3_NUMERICAL_ARTIFACT_CONTEXT_V1',
        'source_closure_sha256': inputs.source_closure_sha256,
        'historical_archive_sha256': inputs.pins['files']['historical_archive']['sha256'],
        'basis': {'json_sha256': sha(inputs.historical['BASIS.json']),
                  'npz_sha256': sha(inputs.historical['BASIS.npz']),
                  'identity': d['basis']['identity']},
        'model': {'science_context_sha256': sha(inputs.historical['SCIENCE_CONTEXT.json']),
                  'energy_keV_per_u': contract['energy_keV_per_u'], 'b_a0': contract['b_a0'],
                  'z_initial_a0': contract['z_initial_a0'], 'z_final_a0': contract['z_final_a0'],
                  'radial_spec': contract['radial_spec'], 'qualification_sector': 'full'},
        'engine': {'source_sha256': engine['source_sha256'],
                   'library_sha256': engine['library_sha256'],
                   'machine': engine['machine'], 'system': engine['system'],
                   'compiler_version': engine['compiler_version'],
                   'compile_flags': engine['argv'][1:-3]},
        'generation_environment': {'python': d['engine_build']['python'],
                                   'libc': d['engine_build']['libc'],
                                   'numeric': engine['numeric']},
        'quadrature_policy': {key: inputs.pins['files'][key]['sha256'] for key in
                              ('f1_contract', 'representatives', 'r2_contract')},
        'dtype': inputs.pins['expected_dtype'],
        'matrix_shapes': inputs.pins['expected_matrix_shapes'],
        'units': {'time': 'atomic_time_from_original_TP2D_contract',
                  'hbar_in_inherited_atomic_units': 1.0,
                  'physical_equation': 'i*hbar*S*dc/dt=(H-i*hbar*D)c'},
        'reuse_scope': 'READ_ONLY_FINALIZED_ARRAYS_NOT_ENGINE_OR_PRODUCTION_ADMISSION',
    }


def coordinate(time_hex: str, order: int, subdivisions: int) -> tuple:
    try:
        value = float.fromhex(time_hex)
    except (ValueError, TypeError) as exc:
        raise AuditError('R3_TASK_IDENTITY', 'canonical hexadecimal time required') from exc
    if (not isinstance(time_hex, str) or not math.isfinite(value) or value.hex() != time_hex
            or type(order) is not int or type(subdivisions) is not int
            or order <= 0 or subdivisions <= 0):
        raise AuditError('R3_TASK_IDENTITY', 'finite exact time and positive integer q/h required')
    return time_hex, order, subdivisions


def legacy_task_id(context: dict, time_hex: str, order: int, subdivisions: int) -> str:
    coordinate(time_hex, order, subdivisions)
    return sha(canonical({'engine_identity_sha256': context['engine_identity_sha256'],
                          'historical_archive_sha256': context['historical_archive_sha256'],
                          'time_hex': time_hex, 'order': order, 'subdivisions': subdivisions,
                          'sector': 'full'}))


class CacheArchive:
    """Validated small matrix cache; there is deliberately no native fallback API."""
    def __init__(self, data: bytes, *, context: dict, numerical_identity: dict,
                 sha256: str, byte_count: int, pair_count: int = 297,
                 expected_shapes: dict | None = None):
        checked_bytes(data, {'sha256': sha256, 'bytes': byte_count}, 'cache archive')
        members = read_zip(data, max_bytes=64*1024**2, max_members=10000)
        self._context = copy.deepcopy(context)
        self._identity = copy.deepcopy(numerical_identity)
        self.archive_sha256 = sha256
        self.archive_bytes = byte_count
        self.expected_shapes = expected_shapes or {'raw':[9,9], 'full':[18,18]}
        self._members = members
        self._records = {}
        self._coordinate_map = {}
        self._arrays = {}
        if strict_json(members.get('TASK_CONTEXT.json', b'null')) != context:
            raise AuditError('R3_TASK_CONTEXT', 'archive context mismatch')
        if set(context) != {'engine_identity_sha256','historical_archive_sha256','contract_sha256'}:
            raise AuditError('R3_TASK_CONTEXT', 'unexpected context keys')
        roots = {'TASK_CONTEXT.json', 'PARTIAL_TASK_SUMMARY.json', 'RETURN_REPORT.json'}
        receipt_names = {n for n in members if n.startswith('operator_tasks/') and n.endswith('.json')}
        expected_names = roots | receipt_names | {n[:-5]+'.npz' for n in receipt_names}
        if len(receipt_names) != pair_count or set(members) != expected_names:
            raise AuditError('R3_TASK_PAIR', 'incomplete, extra or missing cache members')
        report = strict_json(members['RETURN_REPORT.json'])
        summary = strict_json(members['PARTIAL_TASK_SUMMARY.json'])
        if (report.get('status') != 'F1_ENGINE_ADMISSION_PASS' or report.get('first_failure') is not None
                or summary.get('status') != 'R2_TASK_PRECOMPUTE_COMPLETE'
                or summary.get('persisted') != pair_count or summary.get('failed') != 0):
            raise AuditError('R3_FINALIZED_EVIDENCE', 'not a complete admitted cache')
        for name in sorted(receipt_names):
            record = strict_json(members[name])
            unsigned = {k:v for k,v in record.items() if k != 'receipt_sha256'}
            if record.get('receipt_sha256') != sha(canonical(unsigned)):
                raise AuditError('R3_TASK_RECEIPT', 'digest mismatch')
            if (record.get('schema') != 'BASS_NCLOUD_F1_R2_OPERATOR_TASK_V1'
                    or record.get('context') != context
                    or record.get('engine_identity_sha256') != context['engine_identity_sha256']
                    or record.get('historical_archive_sha256') != context['historical_archive_sha256']):
                raise AuditError('R3_TASK_CONTEXT', 'receipt/context mismatch')
            key = coordinate(record['time_hex'], record['order'], record['subdivisions'])
            tid = legacy_task_id(context, *key)
            if record.get('task_id') != tid or name != f'operator_tasks/{tid}.json' or record.get('sector') != 'full':
                raise AuditError('R3_TASK_ID', 'receipt coordinates or filename mismatch')
            if key in self._coordinate_map:
                raise AuditError('R3_TASK_ID', 'duplicate numerical coordinates')
            raw = members[name[:-5]+'.npz']
            if sha(raw) != record['payload_sha256'] or len(raw) != record['payload_bytes']:
                raise AuditError('R3_TASK_PAYLOAD', 'digest/size mismatch')
            arrays = self._decode_arrays(raw, record)
            self._records[tid] = record
            self._coordinate_map[key] = tid
            self._arrays[tid] = arrays
        self.audit = {'schema':'BASS_R3_CACHE_AUDIT_V1','task_pairs':pair_count,
                      'array_count':pair_count*9,'invalid_tasks':0,
                      'archive_sha256':sha256,'archive_bytes':byte_count,
                      'original_context':self.context,
                      'original_member_count':len(members), 'new_native_evaluations':0,
                      'mode':'FINALIZED_EVIDENCE_REUSE_NOT_LEGACY_RESUME'}

    def _decode_arrays(self, payload: bytes, record: dict) -> dict:
        names = {f'raw__{key}':('raw',key) for key in RAW}
        names.update({f'full__{key}':('full',key) for key in FULL})
        if set(record['arrays']) != set(names):
            raise AuditError('R3_ARRAY_KEYS','missing/extra recorded arrays')
        members = read_zip(payload,max_bytes=1024**2,max_members=16)
        if set(members) != {n+'.npy' for n in names}:
            raise AuditError('R3_ARRAY_KEYS','missing/extra NPZ arrays')
        output = {'raw':{},'full':{}}
        for name,(group,key) in names.items():
            shape = self.expected_shapes[group]
            if record['arrays'][name] != {'shape':shape,'dtype':'complex128'}:
                raise AuditError('R3_ARRAY_METADATA','unexpected receipt shape/dtype')
            output[group][key] = read_npy(members[name+'.npy'],shape=tuple(shape),dtype='<c16')
        return output

    @classmethod
    def from_inputs(cls, inputs: Inputs):
        d,p = inputs.documents, inputs.pins
        contract_sha = sha((d['r2_contract']['schema']+p['files']['r2_contract']['sha256']
                           +p['files']['f1_contract']['sha256']+p['files']['representatives']['sha256']).encode())
        context = {'engine_identity_sha256':d['engine_identity']['identity_sha256'],
                   'historical_archive_sha256':p['files']['historical_archive']['sha256'],
                   'contract_sha256':contract_sha}
        pin=p['files']['cache_archive']
        cache=cls(inputs.payloads['cache_archive'],context=context,numerical_identity=numerical_descriptor(inputs),
                  sha256=pin['sha256'],byte_count=pin['bytes'],pair_count=p['expected_task_pairs'],
                  expected_shapes=p['expected_matrix_shapes'])
        for name,role in [('RETURN_REPORT.json','r2_report'),('PARTIAL_TASK_SUMMARY.json','r2_summary')]:
            if cache._members[name] != inputs.payloads[role]:
                raise AuditError('R3_EVIDENCE_CROSSCHECK', 'archive and published reports differ')
        times = {q['time_hex'] for q in d['representatives']['queries']}
        for row in d['sentinels']['sentinels']:
            times.update(row[k] for k in ('time_hex','minus_time_hex','plus_time_hex'))
        expected = {(t,x['order'],x['subdivisions']) for t in times
                    for x in d['f1_contract']['runtime_reference_resolutions']}
        if set(cache._coordinate_map) != expected:
            raise AuditError('R3_TASK_COVERAGE','exact representative/sentinel union mismatch')
        return cache

    @property
    def members(self): return MappingProxyType(self._members)
    @property
    def context(self): return copy.deepcopy(self._context)
    @property
    def numerical_identity(self): return copy.deepcopy(self._identity)
    @property
    def records(self): return copy.deepcopy(self._records)

    def evaluate(self,time_hex: str,order: int,subdivisions: int) -> dict:
        key=coordinate(time_hex,order,subdivisions)
        if key not in self._coordinate_map:
            raise AuditError('R3_CACHE_MISS_NO_FALLBACK', repr(key))
        stored=self._arrays[self._coordinate_map[key]]
        return {group:dict(arrays) for group,arrays in stored.items()}

    def import_to(self,destination: Path,*,expected_identity: dict):
        if canonical(expected_identity) != canonical(self._identity):
            raise AuditError('R3_NUMERICAL_CONTEXT_MISMATCH','consumer differs from admitted artifact descriptor')
        root=Path(destination)
        if not root.parent.is_dir() or root.parent.is_symlink():
            raise AuditError('R3_OUTPUT_PARENT','existing nonsymlink parent required')
        root.mkdir(exist_ok=False)
        (root/'operator_tasks').mkdir()
        for name,data in sorted(self._members.items()):
            write_new(root/name,data)
        bridge={'schema':'BASS_R3_IMPORT_BRIDGE_V1',
                'mode':'READ_ONLY_FINALIZED_ARTIFACT_REUSE',
                'source_archive_sha256':self.archive_sha256,
                'original_context':self.context,'numerical_descriptor':self.numerical_identity,
                'numerical_descriptor_sha256':sha(canonical(self._identity)),
                'original_tasks_preserved':len(self._records),
                'original_task_ids':sorted(self._records),
                'member_identities':{n:{'sha256':sha(v),'bytes':len(v)} for n,v in sorted(self._members.items())},
                'execution':{'output_root':str(root.absolute()),'new_engine_built':False,
                             'new_native_evaluations':0},
                'new_engine_compatibility_granted':False,
                'historical_receipts_rewritten':False}
        write_json_new(root/'IMPORT_BRIDGE.json',bridge)
        imported=ImportedCache(self,root,bridge)
        imported.verify_all_members()
        return imported


class ImportedCache:
    """Reader bound to one original admitted cache; verifies bytes on each lookup."""
    def __init__(self, source: CacheArchive, root: Path, bridge: dict):
        self.source, self.root, self.bridge = source, root, copy.deepcopy(bridge)

    @property
    def numerical_identity(self):return self.source.numerical_identity

    def verify_all_members(self):
        for name,data in self.source.members.items():
            self._read_exact(name,data)
        current=strict_json((self.root/'IMPORT_BRIDGE.json').read_bytes())
        if current!=self.bridge:
            raise AuditError('R3_IMPORTED_BRIDGE','changed import receipt')

    def _read_exact(self,name: str,expected: bytes) -> bytes:
        try:
            return file_bytes(self.root,name,{'sha256':sha(expected),'bytes':len(expected)})
        except (AuditError,OSError) as exc:
            raise AuditError('R3_IMPORTED_BYTES',name) from exc

    def evaluate(self,time_hex: str,order: int,subdivisions: int) -> dict:
        key=coordinate(time_hex,order,subdivisions)
        if key not in self.source._coordinate_map:
            raise AuditError('R3_CACHE_MISS_NO_FALLBACK',repr(key))
        tid=self.source._coordinate_map[key]
        self._read_exact(f'operator_tasks/{tid}.json',self.source.members[f'operator_tasks/{tid}.json'])
        name=f'operator_tasks/{tid}.npz'
        payload=self._read_exact(name,self.source.members[name])
        return self.source._decode_arrays(payload,self.source._records[tid])
