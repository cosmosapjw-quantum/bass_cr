"""Strict identity, JSON and create-only primitives for R4AG."""
from __future__ import annotations
import hashlib, json, os, tempfile
from pathlib import Path
from fractions import Fraction as F
ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = '17c0215979675e40db364207ce138c5efb58cb24c22824e418f5abe3cfeb49ef'
M9_SHA = '95df9f4ba47056e7d79a72dd95fb4ad09996cac7f8338122981e45bb80c01daf'
CEILING = {'G02':'UNRESOLVED','production':'HOLD','capture':False,'all_bound':'OPEN','b_grid':'NO_GO'}

class ContractError(ValueError):
    """An identity, scientific scope, or lifecycle contract was violated."""

def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def _pairs(items):
    d={}
    for k,v in items:
        if k in d: raise ContractError('duplicate JSON key: '+k)
        d[k]=v
    return d

def read(path):
    return json.loads(Path(path).read_text(),object_pairs_hook=_pairs,
                      parse_constant=lambda x: (_ for _ in ()).throw(ContractError('nonfinite JSON')))

def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(',',':'),allow_nan=False).encode()

def digest(obj): return hashlib.sha256(canonical(obj)).hexdigest()

def write_new(path,obj):
    path=Path(path)
    with path.open('x') as f:
        json.dump(obj,f,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)
        f.write('\n');f.flush();os.fsync(f.fileno())

def checkpoint(path,obj):
    path=Path(path)
    fd,t=tempfile.mkstemp(prefix=path.name+'.',dir=path.parent)
    try:
        with os.fdopen(fd,'w') as f:
            json.dump(obj,f,sort_keys=True,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
        os.replace(t,path)
    finally:
        if os.path.exists(t):os.unlink(t)

def inside(root,name):
    root=Path(root).resolve();p=(root/name).resolve()
    if not p.is_relative_to(root) or p==root: raise ContractError('path escapes bound root: '+str(name))
    return p

def rational(value):
    if isinstance(value,bool) or isinstance(value,float) or not isinstance(value,(str,int,F)):
        raise ContractError('exact rational string/integer required')
    try:return F(value)
    except (ValueError,ZeroDivisionError) as e:raise ContractError('invalid rational') from e

def verify_lock(root=ROOT):
    lock=read(Path(root)/'SOURCE_INPUT_LOCK.json')
    if lock['schema']!='R4AG_SOURCE_INPUT_LOCK_V1':raise ContractError('lock schema')
    for name,h in lock['pins'].items():
        p=inside(root,name)
        if not p.is_file() or sha(p)!=h:raise ContractError('source/input pin: '+name)
    if sha(Path(root)/'evidence/parents/R4AE_WINDOW_JET.json')!=M9_SHA:raise ContractError('M9 authority')
    return lock
