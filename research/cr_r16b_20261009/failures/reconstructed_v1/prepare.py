"""New full-time FT03 nominal/secant Jacobians and residual panels only."""
import hashlib,json,os,resource,sys,time
from pathlib import Path
from validated import IV,D,UP,DOWN,total,symmetric

PIN_REI='a3971b386edb9dc585b8657ea095ab171159b7881a52a59f574d0ef694538b48'
PIN_R16='b6a537d87e626831073ced6354ac20c13a6dc180f9fa846cef6a1d5b434d45d5'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text())

def context(stage):
    stage=Path(stage);root=stage/'donor/rei_bridge13_20261008'
    if sha(stage/'r15/inputs/REI_XTHREAD_BRIDGE13_20261008.zip')!=PIN_REI:raise ValueError('SOURCE_IDENTITY')
    binding=load(root/'SOURCE_BINDING.json')
    for name,h in binding['immutable_files_sha256'].items():
        if sha(root/name)!=h:raise ValueError('SOURCE_IDENTITY:'+name)
    sys.path[:0]=[str(root/'research'),str(root/'source')];sys.dont_write_bytecode=True
    import chain_defect as ch
    parent=stage/'r15/source/research/cr_xthread_r15_20261008'
    rec=load(parent/'results/run_v1/CELL_RESULTS.json')
    cert=load(root/'results/final_interval/CHAIN_CERTIFICATE.json')
    validate(ch.ENTRIES,cert)
    return ch,rec,parent

def validate(entries,cert):
    if cert['time_s']!=[0,1250000000.] or cert['birth_count']!=6:raise ValueError('CLOCK_CONTRACT')
    births=[]
    for i in range(32):
        r=entries['root'][i];p=entries['point'][i]
        if p['variant']!=0:raise ValueError('VARIANT_IDENTITY')
        if i:
            last=entries['point'][i-1]
            if r['t0']!=entries['root'][i-1]['t1']:raise ValueError('CLOCK_IDENTITY')
            if p['old']+p['p0'][:len(last['p1'])]!=last['gas']+last['p1']:raise ValueError('INTERFACE_IDENTITY')
            if len(p['p0'])>len(last['p1']):
                if len(p['p0'])!=len(last['p1'])+1:raise ValueError('BIRTH_DIMENSION')
                if r['pre_energy'][-1]!=[13.7,13.7] or r['parent_photons'][-1]!=r['birth_box']:raise ValueError('BIRTH_IDENTITY')
                if not r['birth_box'][0]<=p['p0'][-1]<=r['birth_box'][1]:raise ValueError('BIRTH_WEIGHT')
                births.append(i)
    if births!=[4,8,12,16,20,24]:raise ValueError('BIRTH_CLOCK')

def compute_cell(job):
    stage,index,count=job;started=time.monotonic();ch,recs,parent=context(stage)
    pt=ch.ENTRIES['point'][index];root=ch.ENTRIES['root'][index]
    n=4+len(pt['p0']);ch.ia.DIM=n
    scales=ch.SCALE_G+[ch.P0]*(n-4)
    z0=[IV(v)/sc for v,sc in zip(pt['old']+pt['p0'],scales)]
    z1=[IV(v)/sc for v,sc in zip(pt['gas']+pt['p1'],scales)]
    slopes=[b-a for a,b in zip(z0,z1)]
    env=list(map(D,ch.PARENT['all_prefix_error_upper_scaled'] if index==0 else recs[index]['all_prefix_abs_error_scaled']))
    t0=IV(root['t0']);L=IV(root['t1'])-t0
    CT=IV(299792458)*IV(6.6524587e-29)*10**6
    weight=[IV(1),ch.FHE,2*ch.FHE]+[IV(0)]*(n-3)
    panels=[];mine=None
    for k in range(count):
        s=IV(DOWN.divide(D(k),D(count)),UP.divide(D(k+1),D(count)))
        z=[a+s*d for a,d in zip(z0,slopes)]
        nominal,aux=ch.gas_photo_rhs(s,[ch.AD.var(v,j) for j,v in enumerate(z)],t0,L,ch.EB[:n-4])
        secant,_=ch.gas_photo_rhs(s,[ch.AD.var(v+symmetric(e),j) for j,(v,e) in enumerate(zip(z,env))],t0,L,ch.EB[:n-4])
        J=[v.g for v in nominal];K=[v.g for v in secant]
        rr=[d-v.v for d,v in zip(slopes,nominal)]
        q=[total(IV((b-a).mag())*IV(e) for a,b,e in zip(jrow,krow,env)).hi for jrow,krow in zip(J,K)]
        density=ch.NH0*(-3*ch.H*(t0+L*s)).exp()
        g=[CT*density*L*w for w in weight]
        E=min(v.v.lo if hasattr(v,'v') else v.lo for v in aux['E']);mine=E if mine is None else min(mine,E)
        if E<=ch.CUT.hi:raise ValueError('CUTOFF_CROSSING')
        panels.append({'k':k,'s':s.data(),'dt':str(DOWN.divide(D(1),D(count))),
            'Ahat':[[v.data() for v in row] for row in J],
            'secant_minus_nominal_abs_majorant':[[str((b-a).mag()) for a,b in zip(jrow,krow)] for jrow,krow in zip(J,K)],
            'residual':[v.data() for v in rr],'nonlinear_remainder_upper':list(map(str,q)),
            'goal':[v.data() for v in g]})
    event=None
    if index in [4,8,12,16,20,24]:
        delta=(IV(*root['birth_box'])-IV(pt['p0'][-1]))/ch.P0
        event={'clock_s':str(D.from_float(root['t0'])),'dimension_before':n-1,'dimension_after':n,
               'delta':[IV(0).data()]*(n-1)+[delta.data()],
               'shared_noise_label':f'theta_birth_{index//4}',
               'source_weight':IV(*root['birth_box']).data(),'gas_jump':0,'goal_jump':0}
    return {'index':index,'dimension':n,'time_s':[root['t0'],root['t1']],
        'donor_all_prefix_abs_error_scaled':list(map(str,env)),
        'inherited_incoming_error':recs[index]['incoming_error_scaled'],
        'panels':panels,'event_before':event,'minimum_energy_eV':str(mine),
        'new_endpoint_proof':False,'worker_wall_s':time.monotonic()-started,
        'worker_peak_RSS_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
