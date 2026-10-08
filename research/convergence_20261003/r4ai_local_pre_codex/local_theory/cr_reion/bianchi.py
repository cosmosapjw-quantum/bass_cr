"""Bianchi-I collisionless reference and local exact reservoir bookkeeping.

No general Bianchi background, radiation solver or actual host is replaced.
"""
from fractions import Fraction as F
from .core import ContractError,nonnegative,rational

def bianchi_i_map(momentum, density, a_start, a_end):
    if not all(len(x)==3 for x in (momentum,a_start,a_end)):
        raise ContractError('three spatial axes required')
    a=tuple(map(nonnegative,a_start)); b=tuple(map(nonnegative,a_end))
    if min(a+b)<=0: raise ContractError('positive scale factors required')
    ratio=tuple(x/y for x,y in zip(a,b))
    return tuple(rational(p)*r for p,r in zip(momentum,ratio)),nonnegative(density)*ratio[0]*ratio[1]*ratio[2]

def owner_registry(owners):
    result={}
    for process,owner in owners:
        if not process or not owner: raise ContractError('empty process/owner')
        if process in result: raise ContractError('DOUBLE_PROCESS_OWNER')
        result[process]=owner
    return result
