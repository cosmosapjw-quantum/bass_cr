"""Admission and live guards for C21I's optional successful-RHS cache.

Standard-library imports only: the fresh private H runner must set its thread
environment before it imports NumPy.  This helper never starts a process,
evaluates microphysics, changes provider counters, or stores an RHS value.

The admitted value path is the exact C21F NativeMicro class, optionally inside
the exact private C21H BudgetedNativeMicro class.  The source-reviewed native
owner's EVAL path constructs a fresh point state for every request.  Admission
is source/build provenance, not native-science acceptance or an OS attestation.

File SHA256 is checked at admission.  Each guard enforces an immutable-file
lease (canonical path, device, inode, size, mtime/ctime ns, and mode).  Any
observed file change fails, even if its content would be equivalent.  Call
guard(full_hash=True) before successful return/provider cleanup; the inherited
H runner's post-run source/native checks remain required.  This avoids hashing
the whole native binary on every callback; it is not a per-callback SHA check.
"""
from __future__ import annotations

import ast
import hashlib
import json
import marshal
import math
from pathlib import Path
import stat
import struct
import sys
import time
from types import CodeType, FunctionType, ModuleType

OWNER = "6ea2b1b4b3875c9163cafc45efe720afded43fc4"
NATIVE_KIND = "NATIVE_ORIGINAL_NONPHOTO_RUST"
NATIVE_SOURCE_SHA256 = "ce27acea344604c08159e08d6e703f66a85d51f0729b4e30aa2248a3337ecc27"
BUDGET_SOURCE_SHA256 = "6f344f60d26a0ddb7bb205255cb767fdc230062bf60c56aae1ce58f5ef258f6c"
AUTHORITY_SOURCE_SHA256 = "fb450ad1d00c35e73e99d52c868f2c1a70d1ef71ab1ae83a08ed0e6c0dc00451"
NATIVE_WRAPPER_SHA256 = "3812cf4fec625fdec32e47d737bec8e0306cc538372c5a2cf801d2b0cf590e2d"
EVENT_SOURCE_SHA256 = "24386145f4337b2e01a32219a56ec2446080e4aa4a679a8f956a3eb7ff2ab819"
OWNER_PROOF = {
    "owner_commit": OWNER,
    "review": "C21I source review of fresh-state native_point::evaluate EVAL -> igm_point_rhs",
    "owner_file_git_blobs": {
        "igm_thermal.rs": "0648618d9822e169e9672ac3c556f86595c3b0b6",
        "igm_state.rs": "437365fbe329a10afe292f9dd7eebf549fef804c",
        "igm_rates.rs": "dc3cc028a41ac852d94835372ce13545389d1c3a",
        "hhe_events.rs": "57a63eee1e9d8c4aa2b5ed663dbea15619359f71",
        "lib.rs": "1dfdc11b6af391ceaf5a92713b10b8c89d7db6b1",
    },
    "meaning": "Stored exact-owner source/purity review; no new native execution.",
}
_NATIVE_FIELDS = frozenset(("command", "timeout", "max_calls", "calls", "closed",
                           "stderr", "log", "process", "selector", "buffer"))
_BUDGET_FIELDS = frozenset(("native", "deadline"))
_ABSENT = object()


class NativeCacheAdmissionError(RuntimeError):
    pass


def _fail(reason):
    raise NativeCacheAdmissionError("C21I_NATIVE_CACHE_" + reason)


def _canonical(value):
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"),
                          allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as error:
        raise NativeCacheAdmissionError("C21I_NATIVE_CACHE_JSON_IDENTITY_REQUIRED") from error


def _record(path):
    digest = hashlib.sha256()
    size = 0
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
            size += len(block)
    return {"bytes": size, "sha256": digest.hexdigest()}


def _stat_identity(path):
    st = path.stat()
    if not stat.S_ISREG(st.st_mode):
        _fail("REGULAR_FILE_REQUIRED")
    return (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns, st.st_mode)


class _FileLease:
    def __init__(self, path, expected_sha256=None):
        self.path = Path(path).absolute()
        try:
            self.resolved = self.path.resolve(strict=True)
            self.identity = _stat_identity(self.path)
            self.record = _record(self.path)
            self.check()
        except OSError as error:
            raise NativeCacheAdmissionError("C21I_NATIVE_CACHE_FILE_UNAVAILABLE") from error
        if expected_sha256 is not None and self.record["sha256"] != expected_sha256:
            _fail("PINNED_SOURCE_OR_BINARY_HASH_MISMATCH")

    def check(self, full_hash=False):
        try:
            if (self.path.resolve(strict=True) != self.resolved
                    or _stat_identity(self.path) != self.identity):
                _fail("IMMUTABLE_FILE_CHANGED " + str(self.path))
            if full_hash and _record(self.path) != self.record:
                _fail("TERMINAL_FILE_HASH_CHANGED " + str(self.path))
            if _stat_identity(self.path) != self.identity:
                _fail("FILE_CHANGED_DURING_CHECK " + str(self.path))
        except OSError as error:
            raise NativeCacheAdmissionError("C21I_NATIVE_CACHE_FILE_UNAVAILABLE") from error


def _code_identity(code):
    return hashlib.sha256(marshal.dumps(code)).hexdigest()


class _ClassBinding:
    """Check exact source-defined methods, including a private module instance."""
    def __init__(self, instance, name, source_hash):
        self.instance, self.cls = instance, type(instance)
        cls = self.cls
        if cls.__name__ != name or cls.__bases__ != (object,):
            _fail("EXACT_PROVIDER_CLASS_REQUIRED")
        init = vars(cls).get("__init__")
        if type(init) is not FunctionType:
            _fail("SOURCE_DEFINED_PROVIDER_REQUIRED")
        self.namespace = init.__globals__
        namespace = self.namespace
        if (namespace.get(name) is not cls or namespace.get("__name__") != cls.__module__
                or "__file__" not in namespace):
            _fail("PROVIDER_MODULE_BINDING")
        self.lease = _FileLease(namespace["__file__"], source_hash)
        raw = self.lease.path.read_bytes()
        module_code = compile(raw, str(self.lease.path), "exec", dont_inherit=True,
                              optimize=sys.flags.optimize)
        class_code = next((c for c in module_code.co_consts
                           if isinstance(c, CodeType) and c.co_name == name), None)
        if class_code is None:
            _fail("SOURCE_CLASS_MISSING")
        expected = {c.co_name: c for c in class_code.co_consts if isinstance(c, CodeType)}
        syntax = next(node for node in ast.parse(raw).body
                      if isinstance(node, ast.ClassDef) and node.name == name)
        definitions = {node.name: node for node in syntax.body
                       if isinstance(node, ast.FunctionDef)}
        self.functions = []
        self.globals = {}
        for method, code in expected.items():
            descriptor = vars(cls).get(method)
            definition = definitions[method]
            is_property = bool(definition.decorator_list)
            if is_property:
                if (len(definition.decorator_list) != 1
                        or not isinstance(definition.decorator_list[0], ast.Name)
                        or definition.decorator_list[0].id != "property"
                        or type(descriptor) is not property
                        or descriptor.fset is not None or descriptor.fdel is not None):
                    _fail("PROVIDER_DESCRIPTOR_CHANGED")
                function = descriptor.fget
            else:
                function = descriptor
            if (type(function) is not FunctionType or function.__globals__ is not namespace
                    or _code_identity(function.__code__) != _code_identity(code)
                    or function.__closure__ is not None):
                _fail("PROVIDER_METHOD_CHANGED")
            defaults = tuple(ast.literal_eval(item) for item in definition.args.defaults)
            if function.__defaults__ != (defaults or None) or function.__kwdefaults__ is not None:
                _fail("PROVIDER_METHOD_DEFAULTS_CHANGED")
            self.functions.append((method, descriptor, function, function.__code__,
                                   function.__defaults__, function.__kwdefaults__))
            for key in function.__code__.co_names:
                if key in namespace:
                    self.globals[key] = namespace[key]
        self.class_items = dict(vars(cls))
        if name == "NativeMicro" and (namespace.get("OWNER") != OWNER or cls.kind != NATIVE_KIND):
            _fail("PROVIDER_OWNER_OR_KIND")
        self.check()

    def check(self):
        if (type(self.instance) is not self.cls
                or self.namespace.get(self.cls.__name__) is not self.cls
                or vars(self.cls).keys() != self.class_items.keys()
                or any(vars(self.cls)[key] is not value
                       for key, value in self.class_items.items())):
            _fail("PROVIDER_CLASS_REPLACED_OR_MUTATED")
        for _, _, function, code, defaults, kwdefaults in self.functions:
            if (function.__code__ is not code or function.__defaults__ != defaults
                    or function.__kwdefaults__ != kwdefaults):
                _fail("PROVIDER_METHOD_MUTATED")
        if any(self.namespace.get(key, _ABSENT) is not value
               for key, value in self.globals.items()):
            _fail("PROVIDER_GLOBAL_BINDING_CHANGED")


def _positive_timeout(value):
    if (type(value) not in (int, float) or not math.isfinite(value)
            or not 0 < value <= 15.0):
        _fail("TIMEOUT_OUTSIDE_ORIGINAL_BUDGET")


def admit_native_cache(provider, native_provenance, fixture_identity, source_identity):
    """Return ``(owned_json_contract, guard)`` for the exact known native path.

    ``native_provenance`` is the actual C21G verify_native_binary return; it is
    reverified here with source-pinned authority bytes.  Fixture/source identity
    are nonempty JSON mappings owned and verified by the runner (include the
    full fixture digest/context and H+I runtime closure).  Mutation is rejected.

    Use only for vectorized_exact.  vectorized needs no purity admission.
    ``guard()`` does not consume a call; ``guard(full_hash=True)`` also rehashes
    immutable files.  ``guard(current_provider=...)`` can assert an outer
    runner's provider binding.  Guard calls never reset/extend budgets.

    Native calls == max_calls is allowed: the Nth actual successful call and
    an exact successful cache hit remain valid.  The original __call__ blocks
    any N+1 miss.  Calls above the cap or decreasing counters are rejected.
    Bare NativeMicro relies on run_optimized_reference's one-job deadline;
    a BudgetedNativeMicro deadline is additionally immutable and checked here.
    """
    identities = (native_provenance, fixture_identity, source_identity)
    if any(type(item) is not dict or not item for item in identities):
        _fail("EXPLICIT_PROVENANCE_FIXTURE_SOURCE_REQUIRED")
    identity_bytes = tuple(_canonical(item) for item in identities)
    wrapper = None
    if type(provider).__name__ == "BudgetedNativeMicro":
        wrapper = _ClassBinding(provider, "BudgetedNativeMicro", BUDGET_SOURCE_SHA256)
        if vars(provider).keys() != _BUDGET_FIELDS:
            _fail("BUDGET_WRAPPER_CONFIGURATION")
        native = provider.native
        deadline = provider.deadline
        if type(deadline) not in (int, float) or not math.isfinite(deadline):
            _fail("FINITE_ORIGINAL_DEADLINE_REQUIRED")
        deadline_bits = struct.pack("<d", deadline)
    else:
        native, deadline, deadline_bits = provider, None, None
    native_binding = _ClassBinding(native, "NativeMicro", NATIVE_SOURCE_SHA256)
    source_dir = native_binding.lease.path.parent.parent
    authority_path = source_dir.parent / "cr_c21g_reference_refinement_20261019/campaign_contract.py"
    authority_lease = _FileLease(authority_path, AUTHORITY_SOURCE_SHA256)
    wrapper_lease = _FileLease(source_dir / "native/native_point.rs", NATIVE_WRAPPER_SHA256)
    event_lease = _FileLease(source_dir / "src/event_coupler.py", EVENT_SOURCE_SHA256)
    if wrapper is not None and wrapper.lease.path.parent.parent != source_dir.parent:
        _fail("PROVIDER_UNITS_DO_NOT_SHARE_RESEARCH_CONTEXT")
    authority = ModuleType("_c21i_native_cache_source_authority")
    authority.__file__ = str(authority_path)
    exec(compile(authority_path.read_bytes(), str(authority_path), "exec"), authority.__dict__)
    try:
        verified = authority.verify_native_binary(native_provenance["path"], source_dir,
                                                   native_provenance.get("build_directory"))
    except (KeyError, ValueError, OSError) as error:
        raise NativeCacheAdmissionError("C21I_NATIVE_CACHE_NATIVE_PROVENANCE_FAILED") from error
    if verified != native_provenance or verified.get("owner") != OWNER:
        _fail("NATIVE_PROVENANCE_MISMATCH")
    binary_path = str(Path(verified["path"]).resolve(strict=True))
    if type(native.command) is not list or native.command != [binary_path]:
        _fail("EXACT_SINGLE_BINARY_COMMAND_REQUIRED")
    max_calls = native.max_calls
    if type(max_calls) is not int or not 1 <= max_calls <= 200000:
        _fail("ORIGINAL_CALL_CAP_REQUIRED")
    command = tuple(native.command)
    process = native.process
    if process is None or type(getattr(process, "pid", None)) is not int or process.pid <= 0:
        _fail("LIVE_PROCESS_ID_REQUIRED")
    pid, process_type = process.pid, type(process)
    poll_method = getattr(process_type, "poll", None)
    if not callable(poll_method) or "poll" in vars(process):
        _fail("PROCESS_POLL_BINDING")
    if type(process.args) is not list or process.args != list(command):
        _fail("PROCESS_COMMAND_MISMATCH")
    streams = (native.log, native.stderr, process.stdin, process.stdout)
    if any(stream is None or getattr(stream, "closed", True) for stream in streams):
        _fail("PROVIDER_STREAM_CLOSED")
    if Path(native.log.name).resolve().parent != Path(native.stderr.name).resolve().parent:
        _fail("PROVIDER_LOG_CONTEXT")
    process_receipt_path = Path(native.log.name).resolve().parent / "native_process.json"
    try:
        process_receipt = json.loads(process_receipt_path.read_bytes())
    except (OSError, ValueError) as error:
        raise NativeCacheAdmissionError("C21I_NATIVE_CACHE_PROCESS_RECEIPT_REQUIRED") from error
    if (process_receipt.get("owner") != OWNER
            or process_receipt.get("command") != list(command)
            or process_receipt.get("binary_sha256") != verified["sha256"]
            or process_receipt.get("max_calls") != max_calls):
        _fail("PROCESS_RECEIPT_MISMATCH")
    _positive_timeout(process_receipt.get("timeout_s"))
    selector, selector_type = native.selector, type(native.selector)
    selector_select = getattr(selector_type, "select", None)
    selector_close = getattr(selector_type, "close", None)
    if not callable(selector_select) or not callable(selector_close):
        _fail("SELECTOR_INTERFACE")
    leases = [native_binding.lease, authority_lease, wrapper_lease, event_lease,
              _FileLease(binary_path, verified["sha256"]), _FileLease(process_receipt_path)]
    if wrapper is not None:
        leases.append(wrapper.lease)
    if verified["status"] == "RECORDED_PINNED_OWNER_BUILD":
        build = Path(verified["build_directory"])
        leases.extend(_FileLease(build / name) for name in
                      ("owner_commit.txt", "build_exit.txt", "input_sha256.txt", "owner_source.tar"))
    last_calls = native.calls
    provider_kind = provider.kind
    contract = {
        "schema": "C21I_DETERMINISTIC_PROVIDER_ADMISSION_V1",
        "deterministic_successful_rhs": True,
        "provider_kind": provider_kind,
        "provider_identity": {
            "native_class": "NativeMicro", "wrapper_class": "BudgetedNativeMicro" if wrapper else None,
            "native_provenance": json.loads(identity_bytes[0]),
            "configuration": {"command": list(command), "max_calls": max_calls,
                              "deadline_bits": deadline_bits.hex() if deadline_bits else None},
            "process_pid": pid, "instance_ids": {"provider": id(provider), "native": id(native),
                                                 "process": id(process)},
            "fixture_identity": json.loads(identity_bytes[1]),
            "source_identity": json.loads(identity_bytes[2]),
            "verified_files": {str(lease.path): lease.record for lease in leases},
            "owner_purity_proof": OWNER_PROOF,
        },
        "admitted_by": "Exact source-defined provider classes, reverified C21G native build/owner, immutable cell/job context and live guard",
        "budget_policy": "Nth actual success and exact successful hits at calls==max_calls allowed; original NativeMicro rejects N+1 miss; no reset or deadline extension",
        "mutable_operational_fields": ["calls (monotone actual attempts)", "timeout (finite 0<timeout<=15s)", "buffer (original protocol-owned bytearray)"],
        "file_guard_policy": "Admission SHA256 + per-guard immutable metadata/path lease + terminal full_hash=True and inherited runner postchecks",
        "success_values_only": True, "global_error_bound": None,
    }
    contract = json.loads(_canonical(contract))
    contract_bytes = _canonical(contract)

    def guard(*, full_hash=False, current_provider=provider):
        nonlocal last_calls
        if current_provider is not provider:
            _fail("OUTER_PROVIDER_REPLACED")
        native_binding.check()
        if wrapper is not None:
            wrapper.check()
            if (vars(provider).keys() != _BUDGET_FIELDS or provider.native is not native
                    or type(provider.deadline) not in (int, float)
                    or struct.pack("<d", provider.deadline) != deadline_bits):
                _fail("INNER_PROVIDER_OR_DEADLINE_CHANGED")
            if time.monotonic() >= deadline:
                _fail("NATIVE_JOB_WALL_BUDGET")
        if vars(native).keys() != _NATIVE_FIELDS or native.kind != provider_kind:
            _fail("NATIVE_CONFIGURATION_CHANGED")
        if type(native.command) is not list or tuple(native.command) != command or native.max_calls != max_calls:
            _fail("COMMAND_OR_CALL_CAP_CHANGED")
        if type(native.max_calls) is not int or type(native.calls) is not int:
            _fail("INTEGER_CALL_COUNTER_REQUIRED")
        if native.calls < 0 or native.calls < last_calls or native.calls > max_calls:
            _fail("ACTUAL_CALL_COUNTER_OR_CAP")
        last_calls = native.calls
        _positive_timeout(native.timeout)
        if native.closed is not False:
            _fail("PROVIDER_CLOSED")
        if (native.process is not process or type(process) is not process_type or process.pid != pid
                or type(process.args) is not list or tuple(process.args) != command
                or getattr(process_type, "poll", None) is not poll_method or "poll" in vars(process)):
            _fail("PROCESS_REPLACED_OR_CHANGED")
        if process.poll() is not None:
            _fail("PROVIDER_EXITED")
        if (any(current is not original for current, original in
                zip((native.log, native.stderr, process.stdin, process.stdout), streams))
                or any(getattr(stream, "closed", True) for stream in streams)):
            _fail("PROVIDER_STREAM_REPLACED_OR_CLOSED")
        if (native.selector is not selector or type(selector) is not selector_type
                or getattr(selector_type, "select", None) is not selector_select
                or getattr(selector_type, "close", None) is not selector_close
                or type(native.buffer) is not bytearray or len(native.buffer) > 1048576):
            _fail("PROTOCOL_CONFIGURATION_CHANGED")
        if (tuple(_canonical(item) for item in identities) != identity_bytes
                or _canonical(contract) != contract_bytes):
            _fail("IMMUTABLE_CONTEXT_CHANGED")
        for lease in leases:
            lease.check(full_hash=full_hash)
        if wrapper is not None and time.monotonic() >= deadline:
            _fail("NATIVE_JOB_WALL_BUDGET")

    guard(full_hash=True)
    return contract, guard
