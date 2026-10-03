"""Exact rational interval/ball assembly of the two immutable R8 stencils.

No quadrature, D, historical R8 value, fsum or floating-point reduction is
used. Float JSON endpoints are rejected. Missing nodes do not get zero bounds.
"""
from __future__ import annotations
from fractions import Fraction as F
from math import isqrt, factorial
from common import ROOT,CANDIDATE,M9_SHA,CEILING,ContractError,read,sha,rational

def sqrt_upper(x, bits=256):
    x=rational(x)
    if x<0:raise ContractError('negative square norm')
    if not x:return F(0)
    q=1<<bits;n=isqrt((x.numerator*q*q)//x.denominator)
    if F(n*n,q*q)<x:n+=1
    return F(n,q)

def interval(x):
    if isinstance(x,dict):
        if x.get('denominator_power2')!=256:raise ContractError('unregistered dyadic precision')
        lo=F(int(x['lower_numerator']),1<<256);hi=F(int(x['upper_numerator']),1<<256)
    elif isinstance(x,(list,tuple)) and len(x)==2:lo,hi=map(rational,x)
    else:raise ContractError('interval shape')
    if lo>hi:raise ContractError('reversed interval')
    return lo,hi

def moments(entries):
    if len(entries)!=81:raise ContractError('9x9 ordered channel matrix required')
    center=[];r2=F(0);m2=F(0)
    for e in entries:
        lr,ur=interval(e['re']);li,ui=interval(e['im'])
        a=(lr+ur)/2;b=(li+ui)/2
        center.append((a,b));r2+=((ur-lr)/2)**2+((ui-li)/2)**2;m2+=a*a+b*b
    return center,sqrt_upper(2*r2),sqrt_upper(2*m2)

def phase_midpoint(delta):
    """Enclose exp(-i delta) by a rational center and a scalar modulus ball.

    Sin degree23/cos degree24 at zero; derivative absolute bounds <=1 give
    respective remainders |delta|^24/24! and |delta|^25/25!. No libm assumption.
    """
    delta=rational(delta)
    if abs(delta)>1:raise ContractError('epoch shift outside admitted |delta|<=1')
    s=sum(((-1)**k*delta**(2*k+1)/factorial(2*k+1) for k in range(12)),F(0))
    c=sum(((-1)**k*delta**(2*k)/factorial(2*k) for k in range(13)),F(0))
    es=abs(delta)**24/factorial(24);ec=abs(delta)**25/factorial(25)
    return c,-s,sqrt_upper(ec*ec+es*es)

def transport_center(entries,delta):
    center,rad,norm=moments(entries);a,b,eta=phase_midpoint(delta)
    shifted=[(str(a*x-b*y),str(b*x+a*y)) for x,y in center]
    # Exact phase is unitary: input radius is not multiplied by a rounded norm.
    return shifted,rad,eta*norm

def windows(root=ROOT):
    ans=[]
    for den in (64,128):
        w=read(root/f'evidence/parents/STENCIL_H{den}.json');H=F(1,den);v=F(w['speed_a0_per_ta'])
        if w['candidate']!=CANDIDATE or F(w['atol'])!=F(1,10**12):raise ContractError('frozen window identity/target')
        nodes=[];weights=[]
        for i,a in enumerate((F(-1,2835),F(84,2835),F(-1344,2835),F(4096,2835))):
            h=H/2**i;nodes.extend((-h,h));weights.extend((-a*v/(2*h),a*v/(2*h)))
        if nodes!=list(map(F,w['nodes'])) or weights!=list(map(F,w['weights'])):raise ContractError('frozen weights changed')
        if w['sample_unit']!='1' or w['output_unit']!='ta^-1' or w['norm']!='FROBENIUS_FULL_CROSS':raise ContractError('unit/norm mismatch')
        ans.append(w)
    return ans

def inherited_truncations(root=ROOT):
    if sha(root/'evidence/parents/R4AE_WINDOW_JET.json')!=M9_SHA:raise ContractError('M9 hash mismatch')
    transfer=read(root/'evidence/parents/R4AE_BOUND_TRANSFER.json')
    byid={x['packet']['stencil_id']:x['packet']['truncation'] for x in transfer['windows']}
    ans={}
    for w in windows(root):
        t=byid[w['stencil_id']]
        if t['candidate']!=CANDIDATE or t['unit']!='ta^-1' or t['norm']!='FROBENIUS_FULL_CROSS' or t['bound_type']!='DIRECTED_INTERVAL_BOUND' or M9_SHA not in t['evidence_sha256'] or t['unresolved_assumptions']:
            raise ContractError('truncation authority/type/unit')
        if F(t['domain_a0'][0])>F(w['domain_a0'][0]) or F(t['domain_a0'][1])<F(w['domain_a0'][1]):raise ContractError('truncation domain')
        upper=rational(t['upper'])
        if upper<0:raise ContractError('negative truncation')
        ans[w['stencil_id']]=upper
    return ans

def assemble_packets(registry,packets,*,fixture=False,root=ROOT):
    """Pure arithmetic seam. Filesystem return authentication is in collect.py.

    fixture=True is a test-only result class; it can never emit a physics PASS.
    """
    if registry['candidate']!=CANDIDATE:raise ContractError('registry candidate')
    rows={r['node_id']:r for r in registry['nodes']}
    if len(rows)!=10 or len(registry['nodes'])!=10:raise ContractError('ten unique shifted nodes required')
    received={};audit=[]
    for p in packets:
        key=p['node_id']
        if key not in rows or key in received:raise ContractError('unknown/duplicate node')
        r=rows[key]
        for field,expected in [('candidate',CANDIDATE),('geometry_sha256',r['geometry_sha256']),('unit','1'),('norm','FROBENIUS_FULL_CROSS'),('matrix_shape',[9,9]),('epoch','ACTUAL_STORED'),('bound_type','DIRECTED_INTERVAL_ENCLOSURE')]:
            if p.get(field)!=expected:raise ContractError('packet mismatch: '+field)
        if p.get('fixture',False)!=fixture:raise ContractError('fixture/physical boundary')
        delta=(F(r['v_a0_per_ta'])*F(r['z_a0'])-F(r['v_a0_per_ta'])**2*F(r['time_ta']))/2
        if rational(p['epoch_offset'])!=delta:raise ContractError('epoch value mismatch')
        cent,eps,phase=transport_center(p['entries'],delta)
        received[key]=(cent,eps,phase)
        audit.append({'node_id':key,'epoch_offset':str(delta),'sample_radius':str(eps),'phase_rotation_radius':str(phase),'point_target_met':eps<=F(1,10**16)})
    trunc=inherited_truncations(root);output=[]
    lookup={F(r['offset_a0']):k for k,r in rows.items()}
    for w in windows(root):
        ids=[lookup[F(x)] for x in w['nodes']];missing=[k for k in ids if k not in received]
        state={'stencil_id':w['stencil_id'],'halfwidth_a0':w['halfwidth_a0'],'nodes':ids,'missing_nodes':missing,'truncation_upper':str(trunc[w['stencil_id']]),'total_upper':None,'within_final_target':None,'midpoint':None,'output_unit':'ta^-1','norm':'FROBENIUS_FULL_CROSS','status':'MISSING_SHIFTED_SAMPLES'}
        if not missing:
            center=[(F(0),F(0)) for _ in range(81)];eps=F(0);phase=F(0);point_met=True
            for key,weight in zip(ids,map(F,w['weights'])):
                c,e,p=received[key];center=[(x+weight*F(a),y+weight*F(b)) for (x,y),(a,b) in zip(center,c)]
                eps+=abs(weight)*e;phase+=abs(weight)*p;point_met &= e<=F(1,10**16)
            total=eps+phase+trunc[w['stencil_id']]
            met=point_met and total<=F(w['atol'])
            state.update(midpoint=[[str(x),str(y)] for x,y in center],sample_upper=str(eps),epoch_upper=str(phase),arithmetic_upper='0',arithmetic_method='EXACT_RATIONAL_ENDPOINT_LINEAR_COMBINATION',total_upper=str(total),within_final_target=met,status=('SYNTHETIC_ONLY' if fixture else ('SCOPED_DERIVATIVE_BOUND_PASS' if met else 'TARGET_NOT_MET')),all_point_targets_met=point_met)
        output.append(state)
    return {'schema':'R4AG_STENCIL_ASSEMBLY_V1','fixture':fixture,'windows':output,'per_node':audit,'available_nodes':len(received),'atomic_evaluations':0,'M9_recomputed':False,'D_read':False,'global_ceiling':CEILING.copy(),'physical_source_admission':False,'does_not_certify':['D or D+Ddagger residual','full H','continuous whole trajectory','capture/rate/basis completeness']}
