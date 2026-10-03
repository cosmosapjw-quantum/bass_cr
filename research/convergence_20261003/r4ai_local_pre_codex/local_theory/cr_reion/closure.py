"""Conditional finite-observable chains and nonstationary-phase bounds.

These functions certify arithmetic given explicitly supplied mathematical
premises. They neither verify continuous input envelopes nor admit physics.
"""
from __future__ import annotations
from .core import ContractError, nonnegative

def compose_chain(edges,*,quantity:str,unit:str,target):
    """Sum adjacent deterministic comparison links, without RSS or double count.

    `left` and `right` are identities for exact comparison objects. Every link
    compares the same quantity/unit. Evidence IDs are recorded, not externally
    authenticated by this pure helper. Missing bounds force upper=None.
    """
    if not isinstance(edges,list) or not edges or not quantity or not unit:
        raise ContractError('nonempty ordered comparison chain required')
    tol=nonnegative(target)
    if tol==0:raise ContractError('positive predeclared target required')
    seen=set();links=[];total=nonnegative(0);missing=[]
    keys={'left','right','quantity','unit','upper','bound_type','evidence_sha256'}
    previous=None
    for i,e in enumerate(edges):
        if not isinstance(e,dict) or set(e)!=keys:raise ContractError('edge schema')
        a,b=e['left'],e['right']
        if not isinstance(a,str) or not a or not isinstance(b,str) or not b or a==b:
            raise ContractError('distinct exact object identities required')
        if i==0:seen.add(a)
        if previous is not None and previous!=a:raise ContractError('NONADJACENT_COMPARISON_OBJECTS')
        if b in seen:raise ContractError('CYCLE_OR_DOUBLE_COUNTED_LINK')
        seen.add(b);previous=b
        if e['quantity']!=quantity or e['unit']!=unit:raise ContractError('INCOMPATIBLE_OBSERVABLE_OR_UNIT')
        if e['bound_type']!='DETERMINISTIC_CONDITIONAL':raise ContractError('UNSUPPORTED_BOUND_TYPE')
        ev=e['evidence_sha256']
        if not isinstance(ev,list) or not ev or any(not isinstance(h,str) or len(h)!=64 or any(c not in '0123456789abcdef' for c in h) for h in ev):
            raise ContractError('nonempty evidence hash list required')
        if e['upper'] is None:missing.append(i)
        else:total+=nonnegative(e['upper'])
        links.append(dict(e))
    return {'schema':'CR_COMMON_OBSERVABLE_CHAIN_V1','quantity':quantity,'unit':unit,
            'status':'MISSING_BOUNDS' if missing else 'CONDITIONAL_ARITHMETIC_COMPLETE',
            'upper':None if missing else str(total),'known_partial_sum':str(total),
            'within_target':None if missing else total<=tol,'target':str(tol),
            'missing_links':missing,'links':links,'physical_admission':False,
            'premises_authenticated':False,'assembly':'DETERMINISTIC_TRIANGLE_NOT_RSS'}

def oscillatory_integral_bound(a_left,a_right,duration,a_sup,aprime_sup,phi2_sup,omega_lower):
    r"""Bound ||int A exp(i phi) dt|| for C1 matrix A and real C2 phase.

    Requires |phi'|>=omega_lower>0 continuously and the supplied amplitude /
    derivative bounds in the SAME submultiplicative norm. All propagator,
    projector and time-dependent-frame derivatives belong in A'. The returned
    number is conditional; instantaneous gaps/samples do not prove its premises.
    """
    al,ar,dt,a,ap,p2,w=map(nonnegative,(a_left,a_right,duration,a_sup,aprime_sup,phi2_sup,omega_lower))
    if w==0:raise ContractError('NO_NONSTATIONARY_PHASE_GAP')
    if a<max(al,ar):raise ContractError('amplitude supremum does not cover endpoints')
    if dt==0:return nonnegative(0)
    return (al+ar)/w+dt*(ap/w+a*p2/w**2)
