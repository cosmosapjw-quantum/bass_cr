"""One-cell outward residual, Picard tube and endpoint comparison proof."""
from pathlib import Path
import argparse,json,math,sys,platform,decimal,hashlib
from fractions import Fraction
import cell_model as m
from cell_model import IV,AD,D
from interval_decimal import UP,NEAR,DOWN

def usum(values):
    s=D(0)
    for x in values:s=UP.add(s,x)
    return s

def exp_action_upper(A,seed,terms=24):
    n=len(A)
    if len(seed)!=n or any(x<0 for x in seed):raise ValueError('NONNEGATIVE_SEED_REQUIRED')
    if all(v==0 for row in A for v in row):
        return list(seed),{'identity_exact':True,'shift':'0','norm_upper':'0','terms':0,'tail_upper':'0'}
    omega=max([D(0)]+[A[i][i].copy_negate() for i in range(n)])
    B=[[UP.add(A[i][j],omega if i==j else D(0)) for j in range(n)] for i in range(n)]
    if any(x<0 for row in B for x in row): raise ValueError('METZLER_REQUIRED')
    q=max(usum(row) for row in B); v=list(seed);acc=list(seed)
    for k in range(1,terms+1):
        v=[UP.divide(usum(UP.multiply(B[i][j],v[j]) for j in range(n)),D(k)) for i in range(n)]
        acc=[UP.add(x,y) for x,y in zip(acc,v)]
    tail=(IV(max(seed))*IV(q).exp()*IV(q)**(terms+1)/math.factorial(terms+1)).hi
    factor=IV(omega.copy_negate()).exp().hi
    return [UP.multiply(factor,UP.add(x,tail)) for x in acc],{'shift':str(omega),'norm_upper':str(q),'terms':terms,'tail_upper':str(tail)}

def contract(bx):
    return (all(v.lo>0 for v in bx) and bx[0].hi<1 and UP.add(bx[1].hi,bx[2].hi)<1)

def certify(out,panels=64):
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    # Fixed a priori physical tube, not inferred from the numerical reference.
    rho=D('.001'); tube=[v+IV(rho.copy_negate(),rho) for v in m.Z0]
    assert contract(tube)
    ff,aux=m.rhs(IV(0,1),[AD.var(v,i) for i,v in enumerate(tube)])
    J=[v.g for v in ff]; Q=max(usum(x.mag() for x in row) for row in J)
    F=max(v.v.mag() for v in ff)
    init=[(a-b).mag() for a,b in zip(m.INITIAL_FAMILY,m.Z0)]
    assert all(x==0 for x in init),'THIS_CERTIFICATE_STARTS_AT_ORIGINAL_POINT_GAS_COUNT'
    assert UP.add(max(init),F)<rho and Q<1
    assert all(c.lo<=v.lo and v.hi<=c.hi for c,v in zip(tube,m.Z1))
    M=[[J[i][j].hi if i==j else J[i][j].mag() for j in range(5)] for i in range(5)]
    N=[[x.mag() for x in row] for row in J]
    L=max(UP.add(row[i].hi,usum(x.mag() for j,x in enumerate(row) if j!=i)) for i,row in enumerate(J))
    R=[D(0)]*5; slices=[];ri=[IV(0) for _ in range(5)]; slopes=[b-a for a,b in zip(m.Z0,m.Z1)]
    for k in range(panels):
        s=IV(DOWN.divide(D(k),D(panels)),UP.divide(D(k+1),D(panels)))
        fh,aa=m.rhs(s,m.reconstruction(s))
        r=[d-f for d,f in zip(slopes,fh)]
        R=[max(a,v.mag()) for a,v in zip(R,r)]
        ri=[a+v/IV(panels) for a,v in zip(ri,r)]
        slices.append({'s':s.data(),'residual':[v.data() for v in r]})
    A=[row+[r] for row,r in zip(M,R)]+[[D(0)]*6]
    bound,series=exp_action_upper(A,init+[D(1)])
    b=bound[:5]
    # Nonnegative Jacobian norm majorant is monotone and bounds all prefix errors.
    AN=[row+[r] for row,r in zip(N,R)]+[[D(0)]*6]
    envelope,envseries=exp_action_upper(AN,init+[D(1)])
    envelope=envelope[:5]
    coupling=[usum(UP.multiply(N[i][j],envelope[j]) for j in range(5)) for i in range(5)]
    signed=[-r+IV(c.copy_negate(),c) for r,c in zip(ri,coupling)]
    signed=[IV(max(v.lo,bv.copy_negate()),min(v.hi,bv)) for v,bv in zip(signed,b)]
    at_endpoint=[m.Z1[i]+IV(b[i].copy_negate(),b[i]) for i in range(5)]
    assert all(t.lo<=z.lo and z.hi<=t.hi for t,z in zip(tube,at_endpoint))
    nu=1+m.FHE+at_endpoint[0]+m.FHE*(at_endpoint[1]+2*at_endpoint[2])
    grad=[-1/nu,-m.FHE/nu,-2*m.FHE/nu,1/at_endpoint[3]]
    logerr=sum((g*v for g,v in zip(grad,signed[:4])),IV(0))
    Tnom=m.temperature(m.Z1)
    Terr=Tnom*(logerr.exp()-1)
    logabs=usum(UP.multiply(g.mag(),e) for g,e in zip(grad,b[:4]))
    Tabs=(IV(Tnom.hi)*(IV(logabs).exp()-1)).hi
    # Conservative matched-parameter comparison with the inherited discrete family.
    discrete_offset=[a-b for a,b in zip(m.DISCRETE_BOX,m.Z1)]
    matched=[a-b for a,b in zip(signed,discrete_offset)]
    Tdisc=m.temperature(m.DISCRETE_BOX)
    matched_T=Terr-(Tdisc-Tnom)
    geometry=m.geometry(IV(0,1))
    data={
      'task':'REI-XTHREAD-BRIDGE12-20261008',
      'status':'FIRST_CONTINUOUS_COHORT_CELL_ENDPOINT_ERROR_ENCLOSED_CONDITIONAL',
      'time_s':m.CELL['time_s'],'dimension':5,'time_panels':panels,
      'variables':['xHII','xHeII','xHeIII','w/w0','P/P0'],
      'target':'instantaneous FT03 HHe + ONE cohort, nH(t), E(t); fixed birth plan, no birth in this cell',
      'initial_energy_family_eV':m.EB.data(),'initial_gas_and_count_error':list(map(str,init)),
      'native_frozen_stage_density':m.CELL['fixed_stage_density'],
      'continuous_density_and_energy_range':m.serialize(geometry),
      'picard':{'radius':str(rho),'rhs_norm_upper':str(F),'contraction_Q':str(Q),'physical_tube':m.serialize(tube),'temperature_K':aux['T'].v.data(),'invariant_physical_subset':True,'self_map':True,'unique_solution':True},
      'lognorm_upper_normalized':str(L),'jacobian':m.serialize(J),'metzler_upper':m.serialize(M),
      'whole_cell_residual_abs_upper':list(map(str,R)),
      'integrated_signed_defect':m.serialize(ri),
      'endpoint_error_upper_scaled':list(map(str,b)),
      'endpoint_error_upper_physical':[str(UP.multiply(v,a.hi)) for v,a in zip(b,m.SCALE)],
      'all_prefix_error_upper_scaled':list(map(str,envelope)),
      'signed_error_continuum_minus_native_point_scaled':m.serialize(signed),
      'signed_error_continuum_minus_native_point_physical':m.serialize([v*s for v,s in zip(signed,m.SCALE)]),
      'duhamel_coupling_remainder_upper_scaled':list(map(str,coupling)),
      'T_native_exact_readout':Tnom.data(),'T_error_abs_upper_K':str(Tabs),
      'T_error_signed_interval_K':Terr.data(),
      'matched_continuum_minus_discrete_family_scaled':m.serialize(matched),
      'matched_temperature_error_interval_K':matched_T.data(),
      'matrix_series':series,'monotone_envelope_series':envseries,
      'no_source_birth':True,'no_cutoff_crossing':geometry[1].lo>m.CUT.hi,
      'arithmetic_trust':'unmodified inherited Decimal60 directed basic ops; correctly-rounded exp/ln expanded by one representable neighbor; new AD/RHS assembly and comparison proof',
      'independent_second_interval_rhs':False,'proof_assistant':False,
      'parent_science_replayed':False,'native_runs':0,'new_IVP_used_as_proof_input':False,
      'not_claimed':['whole_macro','later_cells','fixed-grid transport limit','continuous_source quadrature','uniform cumulative escape/work','canonical_restart','Bianchi','physical atomic-fit accuracy'],
      'environment':{'python':sys.version,'libmpdec':decimal.__libmpdec_version__,'platform':platform.platform()},
      'input_sha256':hashlib.sha256((m.ROOT/'inputs/NEXT_CELL_INPUT.json').read_bytes()).hexdigest()}
    (out/'CELL_CERTIFICATE.json').write_text(json.dumps(data,indent=2)+'\n')
    (out/'RESIDUAL_SLICES.json').write_text(json.dumps(slices,indent=2)+'\n')
    print(json.dumps({k:data[k] for k in ['status','picard','lognorm_upper_normalized','endpoint_error_upper_physical','T_error_abs_upper_K','T_error_signed_interval_K','matched_temperature_error_interval_K']},indent=2))
    return data
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--panels',type=int,default=64);a=p.parse_args()
    if not 1<=a.panels<=512:p.error('1..512 proof panels required')
    certify(a.output,a.panels)
