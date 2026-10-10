"""BRIDGE13: source-authentic multi-cohort instantaneous FT03 defect chain.
Claims are conditional on inherited directed Decimal/AD primitives and fixed model.
Every new photon is born ONLY on a recorded birth fence. Parent signed error is
carried without resetting; native stage count/energy definitions are not reused
as an instantaneous RHS.
"""
from pathlib import Path
import argparse,json,sys,hashlib,decimal,math
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'source'),str(ROOT/'research')]
import interval_decimal as ia
from interval_decimal import IV,AD,D,UP,DOWN
import cell_model as donor
from certify_cell import exp_action_upper,usum
W0=donor.W0;P0=donor.P0
H=donor.H; NH0=donor.NH0;FHE=donor.FHE;C=donor.C
CUT=donor.CUT;KB=donor.KB;EV=donor.EV;CHI=donor.CHI
DATA=[json.loads(s) for s in (ROOT/'inputs/BRIDGE11_NATIVE.jsonl').read_text().splitlines()]
PARENT=json.loads((ROOT/'inputs/BRIDGE12_CELL_CERTIFICATE.json').read_text())
ENTRIES={k:{r['index']:r for r in DATA if r.get('kind')==k and (k!='point' or r.get('variant')==0)} for k in ('root','point','after')}
# Corner point records are separate diagnostic inputs; never shadow variant=0.
assert all(set(ENTRIES[k])==set(range(32)) for k in ENTRIES)
assert PARENT['time_s']==[ENTRIES['root'][0]['t0'],ENTRIES['root'][0]['t1']]
SCALE_G=[IV(1)]*3+[W0]

def hull(iv,other):
    other=IV(other)
    return IV(min(iv.lo,other.lo),max(iv.hi,other.hi))

def birth_energies():
    births=[D(0)]; eb=[IV(*ENTRIES['root'][0]['pre_energy'][0])]
    for i in range(1,32):
        r=ENTRIES['root'][i]
        if len(r['parent_photons'])>len(births):
            assert len(r['parent_photons'])==len(births)+1
            births.append(D.from_float(r['t0']))
            assert r['pre_energy'][-1][0]==r['pre_energy'][-1][1]==13.7
            eb.append(IV(*r['pre_energy'][-1]))
    assert len(births)==7 and len(eb)==7
    return births,eb
BIRTH,EB=birth_energies()

def gas_photo_rhs(s,z,t0,h,eb):
    n=len(z);nph=n-4
    if nph<1 or len(eb)!=nph:raise ValueError('COHORT_MISMATCH')
    t=t0+h*s
    nh=NH0*(-3*H*t).exp()
    energies=[eb[j]*(-H*(t-IV(BIRTH[j]))).exp() for j in range(nph)]
    x,y,b=z[:3];w=z[3]*W0; photons=[z[4+j]*P0 for j in range(nph)]
    T=donor.temperature(z)
    tv=T.v if isinstance(T,AD) else T
    if tv.lo<D(30000) or tv.hi>D(110000):raise ValueError('T_OUT_OF_FT03_DOMAIN')
    rr0,g,ci0,dr0=donor.coeff(T)
    ne=x+FHE*(y+2*b)
    lower=[1-x,FHE*(1-y-b),FHE*y];upper=[x,FHE*y,FHE*b]
    ci=[nh*ne*lower[j]*ci0[j] for j in range(3)]
    rr=[nh*ne*upper[j]*rr0[j] for j in range(3)]
    dr=[nh*ne*FHE*y*d for d in dr0]
    photo_by=[C*nh*(1-x)*donor.sigma(E)*P for E,P in zip(energies,photons)]
    photo=sum(photo_by)
    rates=[photo+ci[0]-rr[0],ci[1]-rr[1]-sum(dr),ci[2]-rr[2]]
    heat=sum((E-CHI[0])*p for E,p in zip(energies,photo_by))
    kin=sum(q*KB*T*(IV(1.5)+gg)/EV for q,gg in zip(rr,g))
    kindr=sum(d*KB*en/EV for d,en in zip(dr,donor.DRB))
    fw=heat-sum(q*ch for q,ch in zip(ci,CHI))-kin-kindr-2*H*w
    rates=[rates[0],(rates[1]-rates[2])/FHE,rates[2]/FHE,fw]+[-p for p in photo_by]
    scales=SCALE_G+[P0]*nph
    return [a*h/sc for a,sc in zip(rates,scales)], {'T':T,'nh':nh,'E':energies,'photo':photo_by,'heat':heat}

def exact_birth_input(j, root, point):
    # New birth's specified quadrature weight is an interval, not a pulse in prior cells.
    assert j==len(point['p0'])-1
    born=IV(*root['parent_photons'][-1])
    assert born.contains(point['p0'][j])
    return (born-IV(point['p0'][j]))/P0

def step_boxes(idx,prev_signed):
    root,pt=(ENTRIES['root'][idx],ENTRIES['point'][idx]);nph=len(pt['p0']);n=4+nph
    ia.DIM=n
    z0=[IV(v)/sc for v,sc in zip(pt['old']+pt['p0'],SCALE_G+[P0]*nph)]
    z1=[IV(v)/sc for v,sc in zip(pt['gas']+pt['p1'],SCALE_G+[P0]*nph)]
    if idx==0:raise ValueError('FIRST_CELL_MUST_USE_INHERITED_PROOF')
    prior=ENTRIES['point'][idx-1]
    e=[]
    for j in range(4):
        e.append(prev_signed[j]+(IV(prior['gas'][j])-IV(pt['old'][j]))/SCALE_G[j])
    for j in range(nph):
        if j<len(prior['p1']):
            e.append(prev_signed[4+j]+(IV(prior['p1'][j])-IV(pt['p0'][j]))/P0)
        else:e.append(exact_birth_input(j,root,pt))
    assert nph in range(1,8) and len(e)==n
    return z0,z1,e

def physics_tube(z0,e,rho_g=D('.003'),ph_rel=D('.08')):
    rad=[rho_g]*4+[UP.multiply(max(D('1e-30'),p.hi),ph_rel) for p in z0[4:]]
    tube=[v+IV(r.copy_negate(),r) for v,r in zip(z0,rad)]
    assert tube[0].lo>0 and tube[0].hi<1 and tube[1].lo>0 and tube[2].lo>0
    assert (tube[1]+tube[2]).hi<1 and all(v.lo>0 for v in tube[3:])
    assert all(ei.lo+z.lo>c.lo and ei.hi+z.hi<c.hi for ei,z,c in zip(e,z0,tube))
    return tube,rad

def cert_step(idx,prev_signed,panels=12,terms=22):
    root=ENTRIES['root'][idx];pt=ENTRIES['point'][idx]
    z0,z1,ein=step_boxes(idx,prev_signed)
    n=len(z0);t0=IV(root['t0']);h=IV(root['t1'])-t0;eb=EB[:n-4]
    # The mathematical target uses exact differences of recorded f64 boundary literals.
    # The native rounded dt is left unchanged in its recorded endpoint.
    assert abs(float(h.lo)-root['dt'])<1e-5
    tube,rad=physics_tube(z0,ein)
    f,aux=gas_photo_rhs(IV(0,1),[AD.var(v,i) for i,v in enumerate(tube)],t0,h,eb)
    J=[v.g for v in f];fmax=[v.v.mag() for v in f]
    ratios=[]
    for i in range(n):
        first=UP.add(ein[i].mag(),fmax[i]);assert first<rad[i],('SELF_MAP_FAIL',idx,i,str(first),str(rad[i]))
        ratios.append(UP.divide(first,rad[i]))
    q=max(UP.divide(usum(UP.multiply(J[i][j].mag(),rad[j]) for j in range(n)),rad[i]) for i in range(n))
    assert q<1,('NOT_CONTRACTION',idx,str(q))
    assert all(a.lo<=v.lo and v.hi<=a.hi for a,v in zip(tube,z1)),('RECONSTRUCTION_OUT_OF_TUBE',idx)
    M=[[J[i][j].hi if i==j else J[i][j].mag() for j in range(n)] for i in range(n)]
    N=[[v.mag() for v in row] for row in J]
    slopes=[b-a for a,b in zip(z0,z1)]
    R=[D(0)]*n;ri=[IV(0) for _ in range(n)];births_here=[]
    for k in range(panels):
        s=IV(DOWN.divide(D(k),D(panels)),UP.divide(D(k+1),D(panels)))
        zz=[a+s*delta for a,delta in zip(z0,slopes)]
        ff,_=gas_photo_rhs(s,zz,t0,h,eb)
        rr=[dy-y for dy,y in zip(slopes,ff)]
        R=[max(u,v.mag()) for u,v in zip(R,rr)]
        ri=[u+v/IV(panels) for u,v in zip(ri,rr)]
    eabs=[ei.mag() for ei in ein]
    aug_M=[row+[v] for row,v in zip(M,R)]+[[D(0)]*(n+1)]
    endpoint,series=exp_action_upper(aug_M,eabs+[D(1)],terms)
    endpoint=endpoint[:n]
    aug_N=[row+[v] for row,v in zip(N,R)]+[[D(0)]*(n+1)]
    env,series_N=exp_action_upper(aug_N,eabs+[D(1)],terms)
    env=env[:n]
    coupling=[usum(UP.multiply(N[i][j],env[j]) for j in range(n)) for i in range(n)]
    signed=[ein[i]-ri[i]+IV(c.copy_negate(),c) for i,c in enumerate(coupling)]
    # Both strict box propagation and signed defect are valid enclosures; intersect them.
    signed=[IV(max(v.lo,endpoint[i].copy_negate()),min(v.hi,endpoint[i])) for i,v in enumerate(signed)]
    assert all(iv.lo<=iv.hi for iv in signed)
    # The exact continuum and endpoint reconstruction lie in the physical tube.
    final=[v+ei for v,ei in zip(z1,signed)]
    assert all(c.lo<=z.lo and z.hi<=c.hi for c,z in zip(tube,final)),('OUTSIDE_TUBE',idx)
    segment=[hull(a,b) for a,b in zip(z1,final)]
    nu=1+FHE+segment[0]+FHE*(segment[1]+2*segment[2]);gradient=[-1/nu,-FHE/nu,-2*FHE/nu,1/segment[3]]
    logerr=sum((g*e for g,e in zip(gradient,signed[:4])),IV(0))
    tnom=donor.temperature(z1)
    dt=tnom*(logerr.exp()-1)
    return {
      'index':idx,'time_s':[root['t0'],root['t1']],'birth':root['birth'],'cohorts':n-4,
      'initial_error_scaled':[v.data() for v in ein],
      'Picard':{'tube_radii_scaled':list(map(str,rad)),'self_map_ratio_max':str(max(ratios)),'weighted_contraction_Q':str(q),'rhs_sup_scaled':list(map(str,fmax)),'physical':True},
      'R_max':list(map(str,R)), 'integrated_residual':[v.data() for v in ri],
      'endpoint_abs_bound_scaled':list(map(str,endpoint)),'endpoint_signed_error_scaled':[v.data() for v in signed],
      'T_native_K':tnom.data(),'T_error_signed_K':dt.data(),
      'lower_energy_eV':min([v.lo for v in aux['E']]).__str__(),
      'matrix_series':series,'positive_envelope_series':series_N},signed

def calc(out,panels=12,terms=22):
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    first=[IV(*s) for s in PARENT['signed_error_continuum_minus_native_point_scaled']]
    assert len(first)==5 and first[0].lo>0 and first[3].hi<0
    last=first;steps=[]
    for i in range(1,32):
        record,last=cert_step(i,last,panels,terms)
        steps.append(record)
        print(f"CERT {i}/31 n={record['cohorts']} Q={float(record['Picard']['weighted_contraction_Q']):.4g} HII={list(map(float,last[0].data()))} T={list(map(float,record['T_error_signed_K']))}",flush=True)
    root=ENTRIES['root'][31];p=ENTRIES['point'][31]
    nominal=[IV(v)/sc for v,sc in zip(p['gas']+p['p1'],SCALE_G+[P0]*len(p['p1']))]
    full=[a+v for a,v in zip(nominal,last)]
    disc=[IV(*q)/sc for q,sc in zip(root['carry_gas']+root['carry_photons'],SCALE_G+[P0]*len(p['p1']))]
    matched=[c-(b-a) for c,a,b in zip(last,nominal,disc)]
    Tpoint=donor.temperature(nominal);Tc=donor.temperature(full);Td=donor.temperature(disc)
    # subtract intervals; conservative, may lose correlations
    outcome={
        'task':'REI-XTHREAD-BRIDGE13-20261008','status':'CONDITIONAL_PIECEWISE_CONTINUOUS_FIRST_MACRO_ERROR_ENCLOSED',
        'source_native_SHA256':hashlib.sha256((ROOT/'inputs/BRIDGE11_NATIVE.jsonl').read_bytes()).hexdigest(),
        'inherited_first_certificate_SHA256':hashlib.sha256((ROOT/'inputs/BRIDGE12_CELL_CERTIFICATE.json').read_bytes()).hexdigest(),
        'source_geometry':'prescribed FLRW','time_s':[0,1250000000.],'native_cells':32,'inherited_cells':1,'new_cells':31,
        'birth_count':len(BIRTH)-1,'birth_times_s':list(map(str,BIRTH)),
        'dimension_final':len(last),'residual_time_panels_per_new_cell':panels,
        'inherited_first_cell_signed_error_scaled':PARENT['signed_error_continuum_minus_native_point_scaled'],
        'final_continuum_minus_nominal_scaled':[v.data() for v in last],
        'final_continuum_minus_discrete_family_scaled':[v.data() for v in matched],
        'T_native_K':Tpoint.data(),'T_continuum_interval_K':Tc.data(),
        'T_continuum_minus_native_K':(Tc-Tpoint).data(),
        'T_continuum_minus_discrete_family_K':(Tc-Td).data(),
        'all_picard_and_contraction_checks_passed':True,
        'new_IVP_reference':None,'uniform_number_energy_ledger':False,'continuous_source_accuracy':None,'continuous_tau':None,
        'physical_admission':'HOLD',
        'not_certified':['physical atomic fit','Bianchi directional transport','continuous source quadrature','canonical restart','uniform escape/work ledger','original paired_trial','full 1e13s history'],
    }
    (out/'CHAIN_CERTIFICATE.json').write_text(json.dumps(outcome,indent=2)+'\n')
    (out/'CELL_EVIDENCE.json').write_text(json.dumps(steps,indent=2)+'\n')
    print('FINAL',json.dumps({k:outcome[k] for k in ['status','new_cells','final_continuum_minus_nominal_scaled','T_continuum_minus_native_K','T_continuum_minus_discrete_family_K']},indent=2))
    return outcome
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--output',required=True);a.add_argument('--panels',type=int,default=12);a.add_argument('--terms',type=int,default=22);args=a.parse_args()
    calc(args.output,args.panels,args.terms)
