"""Read-only saved endpoint analysis; never constructs a physical operator."""
import argparse,csv,datetime,hashlib,json,math,os,pathlib,platform,resource,sys,time
from decimal import Decimal,localcontext

def age(P,Q,T):
    if not all(math.isfinite(x) for x in (P,Q,T)) or P<0 or Q<0 or T<=0: raise ValueError('invalid P/Q/T')
    if P==0:
        if Q!=0: raise ValueError('nonzero Q with zero P')
        return None
    return T-2*Q/P

def moments(R,S,T):
    if not all(math.isfinite(x) for x in (R,S,T)) or R<0 or S<0 or T<=0: raise ValueError('invalid R/S/T')
    v=S-R*R
    def cond(a,b): return a/abs(b) if b else None
    return dict(R=R,S=S,raw_slacks={'R':R,'1-R':1-R,'S-R2':v,'R-S':R-S},compatibility_within_contract=(R<=1+2e-12 and v>=-2e-12 and S<=R+2e-12),clipped_mean_s=T*(1-R),clipped_second_moment_s2=T*T*(1-2*R+S),clipped_variance_s2=T*T*v,clipped_std_s=T*math.sqrt(v) if v>=0 else None,current_heat_ancestry_mean_s=T*(1-S/R) if R else None,condition_indicators={'mean':cond(1+R,1-R),'age':cond(R+S,R-S),'variance':cond(S+R*R,v)},cdf_T_lower=R*R/S if S else (0 if R==0 else None),cdf_T_upper=1,cdf_bounds={str(u):{'lower':max(0,(S-(1-u)*R)/u),'upper':min(1,((2-u)*R-S)/(1-u))} for u in (.25,.5,.75)})

def endpoint(P,Q,Pinst,T):
    age(P,Q,T)
    if not math.isfinite(Pinst) or Pinst<0: raise ValueError('invalid terminal yield')
    if Pinst==0: return {'status':'UNDEFINED_ZERO_TERMINAL_YIELD','current_heat_ancestry_mean_s':age(P,Q,T)}
    return moments(P/Pinst,2*Q/(T*Pinst),T)

def decimal_oracle(p,q,terminal,T):
    with localcontext() as c:
        c.prec=90;p,q,h,t=map(lambda v:Decimal(str(v)),(p,q,terminal,T));r=p/h;s=2*q/h
        return {k:str(v) for k,v in dict(R=r,S=s,clipped_mean_s=t*(1-r),clipped_second_moment_s2=t*t*(1-2*r+s),clipped_variance_s2=t*t*(s-r*r),clipped_std_s=t*(s-r*r).sqrt() if s>=r*r else Decimal(0),current_heat_ancestry_mean_s=t*(1-s/r),cdf_T_lower=r*r/s).items()}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def relative(a,b): return abs(a-b)/max(abs(a),abs(b)) if a or b else 0

def run(base):
    manifest=json.loads((base/'inputs/INPUT_IDENTITIES.json').read_text()); selected=[];ancestry=[];identities={}
    for key in ('legacy_2400_4800','fullBED_2400_4800','paired_9600'):
        ident=manifest['inputs'][key];path=base/ident['path']; assert sha(path)==ident['sha256'];identities[key]=ident;data=json.loads(path.read_text())
        for i,row in enumerate(data['grid_results']):
            model='legacy' if key=='legacy_2400_4800' else row['label'];n=row['nodes'];T=row['final']['time_s'];assert T==1e10
            m=row['metrics_normalized'];p,q,h=(m[x] for x in ('heat_power','heat','terminal_heat_power')); comp=row['final']['components']['selected_total'];P=comp['heat_power_J_m3_s'];Q=comp['heat_J_m3'];prefix=f'grid_results[{i}]'
            if key=='legacy_2400_4800' and n==2400:
                inst=P*h/p;instpath='RECONSTRUCTED: '+prefix+'.final.components.selected_total.heat_power_J_m3_s * '+prefix+'.metrics_normalized.terminal_heat_power / '+prefix+'.metrics_normalized.heat_power'; cross=2*comp['injected_energy_J_m3']/T*h
            else:
                terminal=data['same_operator_terminal'] if key=='legacy_2400_4800' else row['same_operator_terminal'];inst=terminal['terminal_heat_power_at_T_J_m3_s'];instpath=('same_operator_terminal' if key=='legacy_2400_4800' else prefix+'.same_operator_terminal')+'.terminal_heat_power_at_T_J_m3_s';cross=2*comp['injected_energy_J_m3']/T*h
            result=moments(p/h,2*q/h,T);assert result['compatibility_within_contract'];assert relative(inst,cross)<=2e-12
            assert relative(result['R'],P/inst)<=2e-12 and relative(result['S'],2*Q/T/inst)<=2e-12
            dec=decimal_oracle(p,q,h,T);errs={}
            for k,v in dec.items():
                dv=float(v);err=abs(result[k]-dv);errs[k]={'absolute':err,'relative':relative(result[k],dv)};assert err<=2e-14 if k in ('R','S','cdf_T_lower') else relative(result[k],dv)<=2e-12
            result.update(model=model,nodes=n,input_key=key,input_sha256=ident['sha256'],original_field_paths={'P_normalized':prefix+'.metrics_normalized.heat_power','Q_normalized':prefix+'.metrics_normalized.heat','terminal_normalized':prefix+'.metrics_normalized.terminal_heat_power','P_SI':prefix+'.final.components.selected_total.heat_power_J_m3_s','Q_SI':prefix+'.final.components.selected_total.heat_J_m3','Pinst_SI':instpath,'T':prefix+'.final.time_s'},P_SI=P,Q_SI=Q,Pinst_SI=inst,Pinst_crosscheck_SI=cross,Pinst_crosscheck_relative=relative(inst,cross),decimal_90_digit_oracle=dec,float64_Decimal_errors=errs)
            selected.append(result)
            for tag in ('direct_0p1_10','direct_10_900','selected_total'):
                c=row['final']['components'][tag];a=age(c['heat_power_J_m3_s'],c['heat_J_m3'],T);ancestry.append(dict(model=model,nodes=n,birth_tag=tag,current_heat_ancestry_mean_s=a,current_heat_ancestry_mean_year=a/31557600 if a is not None else None,P_SI=c['heat_power_J_m3_s'],Q_SI=c['heat_J_m3'],input_sha256=ident['sha256'],original_field_prefix=prefix+'.final.components.'+tag))
    comparisons=[]
    metrics=['R','S','clipped_mean_s','clipped_variance_s2','clipped_std_s','current_heat_ancestry_mean_s','cdf_T_lower']
    lookup={(r['model'],r['nodes']):r for r in selected}
    for model in ('legacy','fullBED'):
        for a,b in ((2400,4800),(4800,9600)):
            comparisons.append({'kind':'grid','model':model,'from_nodes':a,'to_nodes':b,'interpretation':'mixed grid+runtime empirical; no certification' if b==9600 else 'empirical grid difference; no certification','signed_changes':{k:lookup[model,b][k]-lookup[model,a][k] for k in metrics}})
    for n in (2400,4800,9600):comparisons.append({'kind':'model','nodes':n,'direction':'fullBED minus legacy','signed_changes':{k:lookup['fullBED',n][k]-lookup['legacy',n][k] for k in metrics}})
    return dict(status='PASS_SCOPED_IMPLEMENTATION_CHECKS_PENDING_INDEPENDENT_REVIEW',input_identities=identities,selected_rows=selected,ancestry_rows=ancestry,comparisons=comparisons,uncapped_mean='NOT_IDENTIFIABLE',physical_G_builds=0,physical_transport_calls=0,prior_science_suites_rerun=0,performance_savings='NOT_EVALUATED')

def plot(base,result):
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(10,4),layout='constrained');colors={'legacy':'#2364aa','fullBED':'#d45b26'}
    for model in colors:
        for tag,ls in [('direct_0p1_10','-'),('direct_10_900','--'),('selected_total',':')]:
            rows=sorted([r for r in result['ancestry_rows'] if r['model']==model and r['birth_tag']==tag],key=lambda r:r['nodes']);axes[0].plot([r['nodes'] for r in rows],[r['current_heat_ancestry_mean_year'] for r in rows],ls,marker='o',color=colors[model],label=f'{model}: {tag}')
        row=next(r for r in result['selected_rows'] if r['model']==model and r['nodes']==9600);x=[.25,.5,.75,1];lo=[row['cdf_bounds'][str(u)]['lower'] for u in x[:-1]]+[row['cdf_T_lower']];hi=[row['cdf_bounds'][str(u)]['upper'] for u in x[:-1]]+[1];offset=-0.008 if model=='legacy' else 0.008; xx=[u+offset for u in x[:-1]]; axes[1].vlines(xx,[100*v for v in lo[:-1]],[100*v for v in hi[:-1]],color=colors[model],linewidth=2,label=model+' interval (offset)'); axes[1].scatter(xx,[100*v for v in lo[:-1]],color=colors[model],marker='_',s=100); axes[1].scatter(xx,[100*v for v in hi[:-1]],color=colors[model],marker='_',s=100); axes[1].text(.03,.97 if model=='legacy' else .90,f'{model}: F(T) in [{100*lo[-1]:.4f}%, 100%]',transform=axes[1].transAxes,va='top',fontsize=8,color=colors[model])
    axes[0].set(xlabel='Grid nodes',ylabel='Current heat ancestry mean (years)',title='Saved ramp endpoints');axes[1].set(xlabel='Pulse lag / T',ylabel='Eventual heat fraction F (%)',ylim=(0,8.2),xlim=(.2,.8),xticks=[.25,.5,.75],title='9600-node discrete pulse CDF bounds')
    for ax in axes:ax.grid(alpha=.2);ax.legend(fontsize=6)
    fig.savefig(base/'evidence/figures/endpoint_summary.png',dpi=200);fig.savefig(base/'evidence/figures/endpoint_summary.pdf');plt.close(fig)
    (base/'evidence/figures/plot_data.json').write_text(json.dumps({'ancestry_rows':result['ancestry_rows'],'selected_9600':[r for r in result['selected_rows'] if r['nodes']==9600]},indent=2)+'\n')

if __name__=='__main__':
    start=time.time();utc=datetime.datetime.now(datetime.timezone.utc).isoformat();base=pathlib.Path(__file__).resolve().parents[1];out=base/'evidence/endpoint';result=run(base);plot(base,result)
    (out/'RESULT.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    for name,rows in [('ancestry',result['ancestry_rows']),('selected',result['selected_rows']),('comparisons',result['comparisons'])]:
        with (out/(name+'.csv')).open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for row in rows for k in row)));w.writeheader();w.writerows({k:json.dumps(v) if isinstance(v,(dict,list)) else v for k,v in row.items()} for row in rows)
    receipt=dict(command=[sys.executable,*sys.argv],cwd=os.getcwd(),start_utc=utc,end_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),exit_code=0,elapsed_s=time.time()-start,environment={'python':sys.version,'platform':platform.platform(),'thread_environment':{k:v for k,v in os.environ.items() if k.endswith('NUM_THREADS')}},resources={'peak_rss_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'affinity':sorted(os.sched_getaffinity(0))},requested_route='contract-preserving lower tier per owner ASTRA_TIER_ROUTING_POLICY.md',actual_host_model_metadata={'model':'GPT-6 Astra Pro per host developer metadata','tier_override':'not exposed; no lower-tier model identity asserted'},performance_savings='NOT_EVALUATED',hashes={str(p.relative_to(base)):sha(p) for p in [pathlib.Path(__file__),base/'tests/test_endpoint_analysis.py',base/'state/SCIENTIFIC_CONTRACT.json',base/'inputs/INPUT_IDENTITIES.json',out/'RESULT.json']})
    (out/'ACTUAL_EXIT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'status':result['status'],'rows':len(result['selected_rows']),'ancestry_rows':len(result['ancestry_rows']),'elapsed_s':receipt['elapsed_s']}))
