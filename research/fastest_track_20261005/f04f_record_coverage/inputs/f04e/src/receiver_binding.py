"""Read-only F05-to-F04D boundary. Arithmetic is exact on supplied stored values.

A returned reference jet is NOT a derivative of a binary64 program. This module
neither solves nor certifies an ODE, and cannot promote a rejected transaction.
"""
from fractions import Fraction
import math
import struct

MODEL_ID='REI_FT03_HG_RATE_MOMENT_CASE_A_CONTROLLED_V1'
SITE_IDS=('FULL_BE_ENDPOINT','HALF1_BE_ENDPOINT','HALF2_BE_ENDPOINT')
STATE_NAMES=('x_HII','x_HeII','x_HeIII','w_u_over_nH_eV','p0_over_nH','p1_over_nH','p2_over_nH')
EVENT_NAMES=tuple(f'PI_{a}_{g}' for a in range(3) for g in range(3))+tuple(f'CI_{a}' for a in range(3))+tuple(f'RR_{a}' for a in range(3))+('DR_0','DR_1')
NAMES=STATE_NAMES+EVENT_NAMES+('escaped_energy_over_nH_eV',)

def exact(x):
    if isinstance(x,bool):raise ValueError('BOOLEAN_NUMERIC')
    try:q=Fraction(x)
    except (ValueError,TypeError,OverflowError,ZeroDivisionError) as e:raise ValueError('NONFINITE_OR_INVALID_NUMBER') from e
    return q

def binary64_bits(x):
    try:v=float(x)
    except (ValueError,TypeError,OverflowError) as e:raise ValueError('INVALID_BINARY64') from e
    if not math.isfinite(v):raise ValueError('NONFINITE_BINARY64')
    return struct.pack('>d',v).hex()

def vector(x,n,label):
    if not isinstance(x,(list,tuple)) or len(x)!=n:raise ValueError(label+'_SHAPE')
    return [exact(a) for a in x]

def validate_state(x):
    v=vector(x,8,'STATE')
    if min(v)<0 or v[0]>1 or v[1]+v[2]>1:raise ValueError('STATE_DOMAIN')
    return v

def flatten_events(e):
    if not isinstance(e,dict):raise ValueError('EVENTS_TYPE')
    photo=e.get('photo')
    if not isinstance(photo,list) or len(photo)!=3:raise ValueError('PHOTO_SHAPE')
    out=[v for row in photo for v in vector(row,3,'PHOTO')]
    for key,n in [('collision',3),('recombination',3),('dr',2)]:out+=vector(e.get(key),n,key.upper())
    if min(out)<0:raise ValueError('NEGATIVE_EVENT')
    return out

def scales(nh,ev):
    nh,ev=exact(nh),exact(ev)
    if nh<=0 or ev<=0:raise ValueError('UNIT_SCALE_DOMAIN')
    energy=nh*ev
    return [Fraction(1)]*3+[energy]+[nh]*3+[nh]*17+[energy]

def normalize_state(s,nh,ev):
    v=validate_state(s);d=scales(nh,ev)
    return [v[i]/d[i] for i in range(7)]

def record_to_contract(record,nh,ev):
    if not isinstance(record,dict) or record.get('accepted') is not True:raise ValueError('NOT_ACCEPTED')
    if record.get('model_id')!=MODEL_ID:raise ValueError('MODEL_ID')
    t0,h=exact(record.get('t0_s')),exact(record.get('dt_s'))
    if t0<0 or h<=0:raise ValueError('TIME_DOMAIN')
    sites=record.get('sites')
    if not isinstance(sites,list) or len(sites)!=3 or tuple(s.get('id') for s in sites)!=SITE_IDS:raise ValueError('SOURCE_SITE_ORDER')
    if [exact(s.get('step_s')) for s in sites]!=[h,h/2,h/2]:raise ValueError('SOURCE_SITE_TIME')
    old=validate_state(record.get('old_state'));new=validate_state(record.get('state'))
    if new[7]<old[7]:raise ValueError('NEGATIVE_ESCAPE_INCREMENT')
    events=flatten_events(record.get('events'));unit=scales(nh,ev)
    physical=new[:7]+events+[new[7]-old[7]]
    return {'names':NAMES,'physical':physical,'normalized':[v/d for v,d in zip(physical,unit)],
            'initial_normalized':normalize_state(old,nh,ev),'t0_s':t0,'dt_s':h,
            'stage_events':None,'stage_temperatures':None,'native_derivatives':None,
            'accepted_authority':'existing F05 transaction plus external F05 checker, not this adapter'}

CSV_COUNTS={'CONSTANTS':11,'SIGMA0':3,'SIGMA1':3,'SIGMA2':3,'OLD':8,'CONTROL':4,
            'SUM_EVENTS':17,'ESCAPE_INCREMENT':3}
for _stage in ('HALF1','HALF2'):
    CSV_COUNTS.update({_stage+'_STATE':8,_stage+'_EVENTS':17,_stage+'_RHS':7,_stage+'_RATES':17,_stage+'_AUX':4})

def parse_observation(text):
    buckets={k:{} for k in CSV_COUNTS};calls=None
    for line in text.splitlines():
        fields=line.split(',')
        if fields[0]=='BE_CALLS':
            if len(fields)!=2 or calls is not None:raise ValueError('BE_CALLS_FORMAT')
            calls=int(fields[1]);continue
        if len(fields)!=4 or fields[0] not in buckets:raise ValueError('CSV_FIELD')
        tag,index,hexv,decimal=fields
        try:index=int(index);raw=bytes.fromhex(hexv);v=struct.unpack('>d',raw)[0]
        except (ValueError,struct.error) as e:raise ValueError('CSV_BINARY64') from e
        if len(hexv)!=16 or index<0 or index>=CSV_COUNTS[tag] or index in buckets[tag]:raise ValueError('CSV_INDEX_OR_DUPLICATE')
        if not math.isfinite(v):raise ValueError('NONFINITE_BINARY64')
        if binary64_bits(decimal)!=hexv.lower():raise ValueError('DECIMAL_BIT_MISMATCH')
        buckets[tag][index]=v
    if calls!=2:raise ValueError('BE_CALLS_SCOPE')
    if any(len(v)!=CSV_COUNTS[k] for k,v in buckets.items()):raise ValueError('MISSING_FIELDS')
    return {k:[d[i] for i in range(CSV_COUNTS[k])] for k,d in buckets.items()}

def transform_reference_jet(value,gradient,hessian,output_scale,parent_inverse_scales):
    """Exact linear chain rule on stored decimal approximations; no new accuracy claim."""
    n=len(parent_inverse_scales)
    g=vector(gradient,n,'GRADIENT');d=exact(output_scale);s=[exact(x) for x in parent_inverse_scales]
    if d<=0 or min(s)<=0:raise ValueError('JET_SCALE_DOMAIN')
    if not isinstance(hessian,list) or len(hessian)!=n:raise ValueError('HESSIAN_SHAPE')
    H=[vector(row,n,'HESSIAN') for row in hessian]
    return (d*exact(value),[d*g[i]*s[i] for i in range(n)],[[d*H[i][j]*s[i]*s[j] for j in range(n)] for i in range(n)])

def weighted_stage_total(stage_values,stage_weights):
    """Requires actual per-stage values. Aggregate plus unequal weights is insufficient."""
    if stage_values is None:raise ValueError('STAGE_VALUES_UNOBSERVED')
    if len(stage_values)!=len(stage_weights) or not stage_values:raise ValueError('STAGE_WEIGHT_SHAPE')
    return sum((exact(e)*exact(w) for e,w in zip(stage_values,stage_weights)),Fraction(0))
