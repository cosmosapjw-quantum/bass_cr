"""R4AO actual-candidate serializer. The original R4AN guard is unchanged.

This is a separately scoped adapter using the unchanged R4AN native wire format.
The caller must verify the source, input, native and library pins before invoking
this serializer. Raw serialization is not itself scientific admission.
"""
from dyadic import I,SCALE,pi_interval

def serialize(candidate,cell,ctx,entry,samples,binding):
    if candidate.profile!='FINITE_CANDIDATE' or binding.get('profile')!='FINITE_CANDIDATE':
        raise ValueError('finite-candidate admission required')
    expected_context={k:str(getattr(ctx,k)) for k in ('b','z','v','t')}
    if binding.get('candidate')!=candidate.identity or binding.get('cell')!=cell.dump() or binding.get('context')!=expected_context or binding.get('entry')!=list(entry):
        raise ValueError('candidate/cell/entry/epoch binding mismatch')
    if tuple(entry)!=(4,3,1,-1) or cell.kind!='origin_P' or cell.i!=28 or cell.j!=0:
        raise ValueError('registered pilot is origin_P (28,0), mode pair (4,3,+1,-1) only')
    if binding.get('node_limit')!=1024 or len(samples)>1024:
        raise ValueError('single-cell node cap')
    if len(entry)!=4:raise ValueError('four entry indices required')
    a,b,ma,mb=entry
    if any(type(x) is not int for x in entry):raise ValueError('integer entry indices')
    if not(0<=a<len(candidate.ells) and 0<=b<len(candidate.ells)):raise ValueError('mode index')
    if not(-candidate.ells[a]<=ma<=candidate.ells[a] and -candidate.ells[b]<=mb<=candidate.ells[b]):raise ValueError('harmonic m')
    if cell.kind not in ('regular','origin_T','origin_P'):raise ValueError('chart kind')
    if not 1<=len(samples)<=16384:raise ValueError('bounded sample count')
    if not (0<=cell.i<len(candidate.edges)-1 and 0<=cell.j<len(candidate.edges)-1):raise ValueError('panel index')
    if cell.kind=='regular' and (cell.triangle is None or min(cell.i,cell.j)<1):raise ValueError('regular origin cell')
    if cell.kind=='origin_T' and cell.i!=0:raise ValueError('origin_T panel')
    if cell.kind=='origin_P' and cell.j!=0:raise ValueError('origin_P panel')
    out=['R4AN_CELL_V1 256',str(('regular','origin_T','origin_P').index(cell.kind))]
    def put(x):
        q=I(x);out.append(f'{q.lo} {q.hi}')
    for x in (ctx.b,ctx.z,ctx.v,ctx.R,ctx.nu,ctx.t,candidate.edges[1],pi_interval()):put(x)
    for mode,panel,m in ((a,cell.i,ma),(b,cell.j,mb)):
        out.append(f'{candidate.ells[mode]} {m}');lo,hi=candidate.edges[panel:panel+2]
        put(lo);put(hi-lo)
        if len(candidate.coeffs[mode][panel])!=5:raise ValueError('quartic coefficient contract')
        for x in candidate.coeffs[mode][panel]:put(x)
    if cell.kind=='regular':
        for x,y in cell.triangle.vertices:put(x.at(ctx.R));put(y.at(ctx.R))
        put(cell.triangle.det_range(ctx.R))
    else:
        for _ in range(6):put(0)
        put(1)
    out.append(str(len(samples)))
    for u,w,weight in samples:
        u,w,weight=I(u),I(w),I(weight)
        if not (0<=u.lo<=u.hi<=SCALE and 0<=w.lo<=w.hi<=SCALE and weight.lo>=0):raise ValueError('sample domain/weight')
        put(u);put(w);put(weight)
    text='\n'.join(out)+'\n'
    if len(text)>16*1024*1024:raise ValueError('input size cap')
    return text
