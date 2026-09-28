"""Fail-closed N384 -> N768 execution admission; no native loading or compilation."""
from __future__ import annotations
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import re
import signal
import subprocess
import sys
import time

ARCHIVE_SHA256 = '630a80208331b7b37c02a77eae7435f6317d07439a4ea34b11885455fe53fa35'
MAX_RAW_ATTEMPTS = 8470  # (768 midpoint accesses + two endpoints) * 11 rules.
THREAD_KEYS = ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS')


def strict_json(path):
    def pairs(rows):
        result = {}
        for key, value in rows:
            if key in result:
                raise ValueError('duplicate JSON key: ' + key)
            result[key] = value
        return result
    def constant(value):
        raise ValueError('nonfinite JSON constant: ' + value)
    def finite_float(text):
        value = float(text)
        if not math.isfinite(value):
            raise ValueError('nonfinite JSON float: ' + text)
        return value
    return json.loads(Path(path).read_text(), object_pairs_hook=pairs, parse_constant=constant, parse_float=finite_float)


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _positive_int(name):
    text = os.environ.get(name, '')
    if not re.fullmatch(r'[1-9][0-9]{0,8}', text):
        raise ValueError('explicit positive integer required: ' + name)
    return int(text)


def check_request(args, repo, head, tree):
    if os.environ.get('ALLOW_NEW_NATIVE_R4C') != 'YES_I_AUTHORIZE_ONE_RUNG':
        raise PermissionError('R4C_NATIVE_NOT_AUTHORIZED')
    if (args.previous_nstep, args.next_nstep) != (384,768):
        raise PermissionError('authorization scope is N384 -> N768 only')
    if args.expected_resume_archive_sha256 != ARCHIVE_SHA256:
        raise PermissionError('authorization does not cover this input archive')
    if not head or not tree or args.expected_commit != head or args.expected_tree != tree:
        raise ValueError('exact expected commit AND tree required for science')
    if not sys.flags.isolated:
        raise ValueError('science requires isolated Python: python -I')
    repo = Path(repo).resolve()
    if Path(args.out).resolve().is_relative_to(repo):
        raise ValueError('science output must be outside source worktree')
    dirty = subprocess.check_output(['git','-C',str(repo),'status','--porcelain','--untracked-files=all'],text=True)
    if dirty:
        raise ValueError('science source worktree is not clean')
    import numpy as np
    import scipy
    if sys.version_info < (3,11) or np.__version__ != '2.3.5' or scipy.__version__ != '1.17.0':
        raise ValueError('prepared Python>=3.11 / NumPy2.3.5 / SciPy1.17.0 required')
    if any(os.environ.get(key) != '1' for key in THREAD_KEYS):
        raise ValueError('all four thread limits must equal 1 before Python starts')
    nonce = os.environ.get('R4C_AUTHORIZATION_ID','')
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{15,95}',nonce):
        raise PermissionError('explicit unique R4C_AUTHORIZATION_ID required')
    return {'schema':'BASS_R4C_EXECUTION_ADMISSION_V1', 'authorization_id':nonce,
            'execution_head':head, 'execution_tree':tree,
            'source_archive_sha256':ARCHIVE_SHA256,'previous_nstep':384,'next_nstep':768,
            'max_wall_seconds':_positive_int('R4C_MAX_WALL_SECONDS'),
            'max_raw_attempts':MAX_RAW_ATTEMPTS,
            'reader_environment':{'python':sys.version,'executable':sys.executable,
                'numpy':np.__version__,'scipy':scipy.__version__,
                'threads':{key:os.environ[key] for key in THREAD_KEYS}},
            'authorization_semantics':'requires explicit user approval; token is not proof of approval',
            'cost_limit_enforced_by_this_code':False}


def check_native_build(directory, contract, source):
    directory=Path(directory).resolve();source=Path(source)
    receipt=directory/'BUILD.json';library=directory/'libmoments.so'
    for p in (receipt,library,source):
        if not p.is_file() or p.is_symlink():
            raise ValueError('native input must be an existing regular non-symlink file: '+str(p))
    rec=strict_json(receipt)
    source_sha=_sha(source);library_sha=_sha(library)
    if (rec.get('schema')!='BASS_ANALYTIC_MOMENTS_BUILD_V1'
        or source_sha!=contract['analytic_source_sha256']
        or library_sha!=contract['analytic_library_sha256']
        or rec.get('source_sha256')!=source_sha or rec.get('library_sha256')!=library_sha):
        raise ValueError('frozen native source/library mismatch BEFORE dlopen')
    if rec.get('machine')!=platform.machine() or rec.get('system')!=platform.system():
        raise ValueError('native architecture mismatch BEFORE dlopen')
    return {'schema':'BASS_R4C_NATIVE_PRELOAD_CHECK_V1','source_sha256':source_sha,
            'library_sha256':library_sha,'build_receipt_sha256':_sha(receipt),
            'native_loaded_by_check':False,'automatic_build_allowed':False}


def consume_authorization(out, admission):
    """Exclusive durable attempt claim, shared by all worktrees of this OS account."""
    nonce=admission['authorization_id']
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{15,95}',nonce):
        raise PermissionError('invalid authorization id')
    root=Path.home()/'.local/state/bass_r4c/authorizations';root.mkdir(parents=True,exist_ok=True)
    path=root/(nonce+'.json')
    record={**admission,'out':str(Path(out).resolve()),'state':'CONSUMED_BEFORE_NATIVE_LOAD',
            'created_unix_seconds':time.time(),'pid':os.getpid()}
    data=(json.dumps(record,indent=2,allow_nan=False)+'\n').encode()
    # Never delete/rewrite this record to retry an interrupted or failed attempt.
    with path.open('xb') as f:
        f.write(data);f.flush();os.fsync(f.fileno())
    fd=os.open(root,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)
    with (Path(out)/'AUTHORIZATION_CONSUMED.json').open('xb') as f:
        f.write(data);f.flush();os.fsync(f.fileno())
    return record


def interrupted(signum, frame):
    if signum == signal.SIGALRM:
        raise TimeoutError('R4C approved wall-clock budget expired')
    raise InterruptedError('R4C interrupted by signal '+str(signum))


class EvaluationLedger:
    """Count attempts BEFORE the evaluator, including interrupted/failed calls."""
    def __init__(self, evaluator, out):
        self.evaluator=evaluator;self.attempts=0;self.out=Path(out)
    def _event(self, value):
        with (self.out/'RAW_EVALUATION_LEDGER.jsonl').open('a') as f:
            f.write(json.dumps(value,allow_nan=False)+'\n');f.flush();os.fsync(f.fileno())
    def __call__(self,t,order,subdivisions):
        if self.attempts >= MAX_RAW_ATTEMPTS:
            raise RuntimeError('R4C raw evaluation attempt budget exhausted')
        self.attempts+=1
        row={'attempt':self.attempts,'time_hex':float(t).hex(),'order':order,'subdivisions':subdivisions}
        self._event(dict(row,event='attempt_started'))
        try: result=self.evaluator(t,order,subdivisions)
        except BaseException as exc:
            self._event(dict(row,event='attempt_failed',exception_type=type(exc).__name__,message=str(exc)))
            raise
        self._event(dict(row,event='attempt_completed'))
        return result
