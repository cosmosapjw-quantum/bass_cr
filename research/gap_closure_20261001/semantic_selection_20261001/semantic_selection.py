"""Semantic finite selected span; does not certify all-bound capture."""
import hashlib
import json
import math
import re

def _identity(row):
    required=('center','l','m','principal_n','positive_rank','kind','energy_Eh','radial_identity')
    if any(k not in row for k in required):raise ValueError('resolved channel identity is incomplete')
    center,l,m=row['center'],row['l'],row['m']
    if any(type(x) is not int for x in (center,l,m)) or center<0 or l<0 or abs(m)>l:raise ValueError('invalid center/angular identity')
    e=row['energy_Eh']
    if isinstance(e,bool) or not isinstance(e,(int,float)) or not math.isfinite(e):raise ValueError('finite resolved energy required')
    if not isinstance(row['radial_identity'],str) or re.fullmatch('[0-9a-f]{64}',row['radial_identity']) is None:raise ValueError('radial SHA256 identity required')
    if row['kind']=='bound':
        if e>=0 or type(row['principal_n']) is not int or row['principal_n']<=l or row['positive_rank'] is not None:raise ValueError('bound kind, energy and quantum identity disagree')
    elif row['kind']=='positive_pseudostate':
        if e<=0 or row['principal_n'] is not None or type(row['positive_rank']) is not int or row['positive_rank']<1:raise ValueError('positive pseudostate identity inconsistent')
    else:raise ValueError('unrecognized physical channel family')
    return (center,l,m,row['principal_n'],row['positive_rank'],row['kind'],row['radial_identity'])

def select_projectile_bound(channels,*,projectile_center):
    """Return positions in the supplied ordering, never copy legacy index fields.

    The caller binds projectile_center from its physical channel convention.
    Positive pseudostates and zero/ambiguous energies cannot enter this span.
    """
    if type(projectile_center) is not int or projectile_center<0:raise ValueError('explicit projectile center required')
    seen=set();selected=[]
    for position,row in enumerate(channels):
        _identity(row)
        # Quantum labels cannot make the same coefficient-backed function new.
        key=(row['center'],row['l'],row['m'],row['radial_identity'])
        if key in seen:raise ValueError('duplicate physical channel identity')
        seen.add(key)
        if row['center']==projectile_center and row['kind']=='bound' and row['energy_Eh']<0:selected.append(position)
    if not selected:raise ValueError('selected projectile negative-energy span is empty')
    return selected

def selection_identity(channels,projectile_center):
    indices=select_projectile_bound(channels,projectile_center=projectile_center)
    identities=sorted((_identity(channels[i]) for i in indices),key=lambda x:json.dumps(x))
    raw=json.dumps({'schema':'BASS_SEMANTIC_BOUND_SELECTION_V1','projectile_center':projectile_center,'channels':identities},sort_keys=True,separators=(',',':')).encode()
    return hashlib.sha256(raw).hexdigest()
