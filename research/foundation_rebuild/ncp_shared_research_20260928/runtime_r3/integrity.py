"""Bounded evidence I/O. Hashes establish identity, not scientific truth."""
from __future__ import annotations
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import stat
import tempfile
import zipfile

import numpy as np


class AuditError(ValueError):
    """A typed fail-closed input, integrity or numerical-diagnostic failure."""
    def __init__(self, code: str, detail: str):
        self.code = code
        super().__init__(f'{code}: {detail}')


def canonical(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def strict_json(data: bytes):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise AuditError('R3_JSON_DUPLICATE', key)
            result[key] = value
        return result
    def invalid(value):
        raise AuditError('R3_JSON_NONFINITE', value)
    try:
        return json.loads(data.decode('utf-8'), object_pairs_hook=pairs, parse_constant=invalid)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise AuditError('R3_JSON_INVALID', str(exc)) from exc


def checked_bytes(data: bytes, expected: dict, label: str) -> bytes:
    if len(data) != expected['bytes'] or sha(data) != expected['sha256']:
        raise AuditError('R3_INPUT_SHA_SIZE', label)
    return data


def safe_name(name: str) -> PurePosixPath:
    p = PurePosixPath(name)
    if (not name or name.startswith('/') or '\\' in name or ':' in name or '\0' in name
            or any(x in ('', '.', '..') for x in name.split('/')) or p.as_posix() != name):
        raise AuditError('R3_ZIP_PATH', 'noncanonical relative member')
    return p


def read_zip(data: bytes, *, max_bytes: int, max_members: int) -> dict[str, bytes]:
    """No extraction and no symlinks. Inspect declared budgets before decompression."""
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            infos = z.infolist()
            if len(infos) > max_members or sum(i.file_size for i in infos) > max_bytes:
                raise AuditError('R3_ZIP_BUDGET', 'member count or uncompressed bytes exceeded')
            names = [i.filename for i in infos]
            if len(names) != len(set(names)):
                raise AuditError('R3_ZIP_DUPLICATE', 'duplicate member names')
            for item in infos:
                safe_name(item.filename)
                mode = item.external_attr >> 16
                kind = stat.S_IFMT(mode)
                if (item.is_dir() or kind not in (0, stat.S_IFREG) or item.flag_bits & 1
                        or item.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED)):
                    raise AuditError('R3_ZIP_TYPE', 'unsupported member type/encryption/compression')
            # ZipFile.read checks the CRC. The output sum cannot exceed inspected limits.
            return {i.filename: z.read(i) for i in infos}
    except (zipfile.BadZipFile, RuntimeError, EOFError) as exc:
        raise AuditError('R3_ZIP_INVALID', str(exc)) from exc


def read_npy(data: bytes, *, shape: tuple[int, ...], dtype: str) -> np.ndarray:
    """Check the NPY header against small exact shapes before NumPy allocates."""
    stream = io.BytesIO(data)
    try:
        version = np.lib.format.read_magic(stream)
        if version == (1, 0):
            actual_shape, order, actual_dtype = np.lib.format.read_array_header_1_0(stream)
        elif version == (2, 0):
            actual_shape, order, actual_dtype = np.lib.format.read_array_header_2_0(stream)
        else:
            raise AuditError('R3_ARRAY_HEADER', 'unsupported NPY version')
        expected = np.dtype(dtype)
        if (tuple(actual_shape) != tuple(shape) or actual_dtype.str != expected.str
                or actual_dtype.hasobject or any(type(v) is not int or v < 0 for v in actual_shape)):
            raise AuditError('R3_ARRAY_METADATA', 'shape/dtype/object-array mismatch')
        count = int(np.prod(shape, dtype=np.int64))
        if len(data)-stream.tell() != count*expected.itemsize:
            raise AuditError('R3_ARRAY_BYTES', 'NPY length disagrees with header')
        value = np.load(io.BytesIO(data), allow_pickle=False)
        if not np.isfinite(value).all():
            raise AuditError('R3_ARRAY_NONFINITE', 'NaN/Inf in stored array')
        # Own read-only snapshot; returning writeable views could invalidate the audit.
        # An immutable bytes owner prevents setflags(write=True) from reopening writes.
        value = np.frombuffer(value.tobytes(order='C'), dtype=expected).reshape(shape)
        return value
    except (ValueError, EOFError) as exc:
        if isinstance(exc, AuditError):
            raise
        raise AuditError('R3_ARRAY_INVALID', str(exc)) from exc


def file_bytes(root: Path, relative: str, expected: dict) -> bytes:
    p = safe_name(relative)
    current = root
    if not root.is_dir() or root.is_symlink():
        raise AuditError('R3_INPUT_ROOT', 'missing or symlinked repository root')
    for part in p.parts:
        current = current / part
        if current.is_symlink():
            raise AuditError('R3_INPUT_SYMLINK', relative)
    if not current.is_file():
        raise AuditError('R3_INPUT_MISSING', relative)
    if current.stat().st_size != expected['bytes']:
        raise AuditError('R3_INPUT_SHA_SIZE', relative)
    return checked_bytes(current.read_bytes(), expected, relative)


def write_new(path: Path, data: bytes) -> None:
    """Create-only atomic publication, fsync payload then directory; no overwrite."""
    path = Path(path)
    if path.exists() or path.is_symlink():
        raise FileExistsError(str(path))
    if not path.parent.is_dir() or path.parent.is_symlink():
        raise AuditError('R3_OUTPUT_PARENT', str(path.parent))
    fd, temp = tempfile.mkstemp(prefix='.partial_r3_', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data); stream.flush(); os.fsync(stream.fileno())
        os.link(temp, path)  # Fails atomically when another writer owns the name.
        dfd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def write_json_new(path: Path, value) -> None:
    write_new(path, (json.dumps(value, indent=2, allow_nan=False)+'\n').encode())
