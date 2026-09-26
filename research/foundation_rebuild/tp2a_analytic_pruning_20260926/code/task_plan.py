"""Canonical numerical-task keys independent of candidate/reference labels.

Aliasing records shared evidence, never an independent accuracy cross-check.
The effective integration mesh, order, exact time, basis/engine identity and
sector must coincide. No nearby-time interpolation or fuzzy hash matching.
"""
import hashlib,json
import numpy as np

def numerical_key(request,physics_identity):
    order=request['order'];edges=np.asarray(request['integration_edges'],dtype='<f8')
    if type(order) is not int or not 2<=order<=64:raise ValueError('bounded Gauss order required')
    if edges.ndim!=1 or len(edges)<2 or not np.isfinite(edges).all() or np.any(np.diff(edges)<=0):raise ValueError('valid effective mesh required')
    t=float.fromhex(request['time_hex'])
    if not np.isfinite(t):raise ValueError('finite exact time required')
    if request['sector'] not in ('full','even'):raise ValueError('declared sector required')
    obj={'order':order,'edge_sha256':hashlib.sha256(edges.tobytes()).hexdigest(),'time_hex':float(t).hex(),
         'sector':request['sector'],'physics_and_engine_identity':physics_identity,'schema':'BASS_CANONICAL_ANGULAR_TASK_V1'}
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
