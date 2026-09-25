import os,sys
from pathlib import Path
p=Path(__file__).resolve();root=p.parents[1]
sys.path.insert(0,str(root))
if os.getenv('BASS_UPSTREAM_ROOT'):
    u=Path(os.environ['BASS_UPSTREAM_ROOT'])
    sys.path[:0]=[str(u/'repair'),str(u/'source/research/foundation_rebuild/src'),str(u/'source')]
else:
    fnd=root.parent;repo=fnd.parent.parent
    sys.path[:0]=[str(fnd/'reaudit_20260925/repair'),str(fnd/'src'),str(repo)]
