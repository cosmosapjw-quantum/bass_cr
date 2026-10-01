"""Exact cross/full binding for the fixed 9 target + 9 projectile model.

assemble_full assigns raw TP/PT blocks without arithmetic. Qualification of
those raw blocks therefore applies only to byte-value-identical full blocks;
no tolerance, projection, or numerical repair is appropriate at this boundary.
"""
from pathlib import Path
import hashlib
import io
import numpy as np
from execution_admission import strict_json


def validate_full_raw_cross(full,raw):
    for name in ('S','H','D'):
        matrix=np.asarray(full[name])
        if matrix.shape!=(18,18) or not np.isfinite(matrix).all():
            raise ValueError('cross binding requires finite18-channel full '+name)
        for suffix,rows,columns in (('tp',slice(0,9),slice(9,18)),
                                    ('pt',slice(9,18),slice(0,9))):
            key=name+'_'+suffix
            cross=np.asarray(raw[key])
            if cross.shape!=(9,9) or not np.isfinite(cross).all():
                raise ValueError('cross binding requires finite9-by9 raw '+key)
            if not np.array_equal(matrix[rows,columns],cross):
                raise ValueError('selected/raw cross binding mismatch: '+key)


def validate_cached_cross_binding(directory,query_id):
    """Check the selected resolution in a committed, hash-bound query pair."""
    directory=Path(directory)
    record=strict_json(directory/(query_id+'.json'))
    payload=(directory/(query_id+'.npz')).read_bytes()
    if hashlib.sha256(payload).hexdigest()!=record.get('payload_sha256'):
        raise ValueError('cross binding payload SHA256 mismatch')
    resolution=record['qualification']['selected_resolution']
    tag=f"q{resolution['order']}_h{resolution['subdivisions']}"
    with np.load(io.BytesIO(payload),allow_pickle=False) as data:
        full={name:np.array(data['selected__'+name]) for name in ('S','H','D')}
        raw={name+'_'+suffix:np.array(data[tag+'__'+name+'_'+suffix])
             for name in ('S','H','D') for suffix in ('tp','pt')}
    validate_full_raw_cross(full,raw)
