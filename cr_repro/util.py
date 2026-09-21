from __future__ import annotations
from pathlib import Path
import hashlib,json,os
import numpy as np

def sha256_bytes(b): return hashlib.sha256(b).hexdigest()
def sha256_file(p): return sha256_bytes(Path(p).read_bytes())
def atomic_json(path,obj):
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
    t=p.with_suffix(p.suffix+'.tmp'); t.write_text(json.dumps(obj,indent=2,sort_keys=True)); os.replace(t,p)
def atomic_npy(path,arr):
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True); t=Path(str(p)+'.tmp')
    with open(t,'wb') as f:
        np.save(f,arr,allow_pickle=False); f.flush(); os.fsync(f.fileno())
    os.replace(t,p)
def config_hash(cfg): return sha256_bytes(json.dumps(cfg,sort_keys=True,separators=(',',':')).encode())
