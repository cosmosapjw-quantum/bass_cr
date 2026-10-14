"""Cached scalar heat-delay diagnostics; no operator construction or propagation."""
import argparse
import hashlib
import json
import math
from decimal import Decimal, localcontext
from pathlib import Path

REL = 2e-12
ABS = 2e-14
UNDEFINED = 'UNDEFINED_ZERO_EVENT_PROBABILITY'


def check(name, a, b, scale=1.0):
    raw = a-b
    relative = raw/b if b != 0 else None
    ok = abs(raw) <= ABS*scale + REL*max(abs(a), abs(b))
    if not ok:
        raise ValueError(f'IDENTITY_FAILURE:{name}:{raw}')
    return dict(raw=raw, signed_relative=relative, pass_check=ok)


def event(prob, first, second, T):
    if prob == 0:
        if abs(first/T) > 2e-12 or abs(second/T**2) > 2e-12:
            raise ValueError('INCOMPATIBLE_ZERO_EVENT_MOMENTS')
        return dict(status=UNDEFINED, probability=prob, raw_m1_s=first,
                    raw_m2_s2=second, mean_s=None, second_s2=None, variance_s2=None,
                    std_s=None, issue=UNDEFINED)
    mean, m2 = first/prob, second/prob
    variance = m2-mean*mean
    if first/T < -2e-12 or second/T**2 < -2e-12 or variance < -2e-12*max(T*T,abs(m2),mean*mean):
        raise ValueError('INCOMPATIBLE_EVENT_MOMENTS')
    return dict(status='DEFINED', probability=prob, raw_m1_s=first,
                raw_m2_s2=second, mean_s=mean, second_s2=m2, variance_s2=variance,
                std_s=math.sqrt(variance) if variance >= 0 else None,
                issue='NEGATIVE_VARIANCE_RETAINED' if variance < 0 else None)


def analyze_scalar(H0, p, R, S, mu, m2, T):
    values=(H0,p,R,S,mu,m2,T)
    if any(not math.isfinite(float(x)) for x in values):
        raise ValueError('NONFINITE_INPUT')
    if H0 < 0 or T <= 0:
        raise ValueError('BAD_YIELD_OR_TIME')
    if H0 == 0:
        return dict(status='UNDEFINED_ZERO_YIELD')
    tol=2e-12
    if not (0 <= p <= 1) or R < -tol or S < -tol or S > R+tol or R > p+tol or R*R > p*S+tol:
        raise ValueError('INCOMPATIBLE_CENSORING_MOMENTS')
    e1=T*(p-R); e2=T*T*(p-2*R+S)
    t1=mu-e1; t2=m2-e2
    early=event(p,e1,e2,T); tail=event(1-p,t1,t2,T)
    residual=event(1-p,mu-T*(1-R),m2-2*T*mu+T*T*(1-S),T)
    total=event(1,mu,m2,T)
    if early['status']=='DEFINED' and (early['mean_s'] > T*(1+tol) or early['second_s2'] > T*early['mean_s']+tol*T*T):
        raise ValueError('EARLY_SUPPORT_VIOLATION')
    if tail['status']=='DEFINED' and tail['mean_s'] < T*(1-tol):
        raise ValueError('TAIL_SUPPORT_VIOLATION')
    variance_sum=sum(e['probability']*(e['variance_s2']+(e['mean_s']-mu)**2) for e in (early,tail) if e['status']=='DEFINED')
    checks={'raw_m1':check('raw_m1',e1+t1,mu,T),'raw_m2':check('raw_m2',e2+t2,m2,T*T),'total_variance':check('total_variance',variance_sum,total['variance_s2'],T*T)}
    if tail['status']=='DEFINED':
        checks['residual_mean']=check('residual_mean',residual['mean_s'],tail['mean_s']-T,T)
        checks['residual_second']=check('residual_second',residual['second_s2'],tail['second_s2']-2*T*tail['mean_s']+T*T,T*T)
        checks['residual_variance']=check('residual_variance',residual['variance_s2'],tail['variance_s2'],T*T)
    return dict(status='DEFINED',H0=H0,p=p,R=R,S=S,mu_s=mu,m2_s2=m2,early=early,tail=tail,tail_residual=residual,total=total,checks=checks)


def decimal_scalar(H0,p,R,S,mu,m2,T):
    """Independent Decimal80 formula implementation; never calls float oracle."""
    with localcontext() as ctx:
        ctx.prec=80
        h,f,r,s,u,v,t=map(lambda x: Decimal(str(x)),(H0,p,R,S,mu,m2,T))
        out={'H0':h,'p':f,'R':r,'S':s,'mu_s':u,'m2_s2':v}
        if h==0:
            return {'status':'UNDEFINED_ZERO_YIELD'}
        for name,q,a,b in [('early',f,t*(f-r),t*t*(f-2*r+s)),('tail',1-f,u-t*(f-r),v-t*t*(f-2*r+s)),('tail_residual',1-f,u-t*(1-r),v-2*t*u+t*t*(1-s)),('total',Decimal(1),u,v)]:
            e={'probability':q,'raw_m1_s':a,'raw_m2_s2':b}
            if q:
                e.update(mean_s=a/q,second_s2=b/q,variance_s2=b/q-(a/q)**2)
            out[name]=e
        return out


def compare_decimal(fp, dec, T):
    checks={}
    for section in ('early','tail','tail_residual','total'):
        for key,value in dec[section].items():
            if fp[section].get(key) is not None:
                scale=T*T if key.endswith('s2') else T if key.endswith('_s') else 1
                checks[section+'.'+key]=check('decimal.'+section+'.'+key,fp[section][key],float(value),scale)
    return checks


def mixture(columns, selected, T):
    H=sum(c['H0'] for c in columns)
    den={'eventual':H,'early':sum(c['H0']*c['p'] for c in columns),'tail':sum(c['H0']*(1-c['p']) for c in columns),'mean_share':sum(c['H0']*c['mu_s'] for c in columns)}
    weights=[]
    for c in columns:
        numer={'eventual':c['H0'],'early':c['H0']*c['p'],'tail':c['H0']*(1-c['p']),'mean_share':c['H0']*c['mu_s']}
        weights.append({k:{'status':'DEFINED' if den[k] else UNDEFINED,'value':v/den[k] if den[k] else None} for k,v in numer.items()})
    checks={}
    for key in ('p','R','S','mu_s','m2_s2'):
        checks[key]=check('mixture.'+key,sum(c['H0']*c[key]/H for c in columns),selected[key],T*T if key=='m2_s2' else T if key=='mu_s' else 1)
    checks['H0']=check('mixture.H0',H,selected['H0'])
    variance=sum(c['H0']/H*(c['total']['variance_s2']+(c['mu_s']-selected['mu_s'])**2) for c in columns)
    checks['total_variance']=check('birth_total_variance',variance,selected['total']['variance_s2'],T*T)
    for partition in ('early','tail'):
        if selected[partition]['status']=='DEFINED':
            value=sum(weights[i][partition]['value']*(c[partition]['variance_s2']+(c[partition]['mean_s']-selected[partition]['mean_s'])**2) for i,c in enumerate(columns) if c[partition]['status']=='DEFINED')
            checks[partition+'_variance']=check('birth_'+partition+'_variance',value,selected[partition]['variance_s2'],T*T)
    return dict(weights=weights,checks=checks)


def stringify(x):
    if isinstance(x,Decimal): return str(x)
    if isinstance(x,dict): return {k:stringify(v) for k,v in x.items()}
    if isinstance(x,list): return [stringify(v) for v in x]
    return x


def run(repo, unit):
    contract=unit/'state/SCIENTIFIC_CONTRACT.json'
    if hashlib.sha256(contract.read_bytes()).hexdigest()!='b50c316e91ebea6b1d0e5a43367b1cb31ae8836af328521fb366af9f54e35ccf':
        raise ValueError('CONTRACT_IDENTITY_MISMATCH')
    manifest=json.loads((unit/'inputs/INPUT_IDENTITIES.json').read_text())
    for item in manifest['files'].values():
        data=(repo/item['path']).read_bytes()
        if len(data)!=item['bytes'] or hashlib.sha256(data).hexdigest()!=item['sha256']:
            raise ValueError('INPUT_IDENTITY_MISMATCH:'+item['path'])
    T=1e10; year=31557600; models={}; decimals={}; plots={}
    for model in ('fullBED','legacy'):
        raw=json.loads((repo/manifest['files']['actual_'+model+'_result']['path']).read_text())
        entries=raw['birth_columns']+[raw['selected']]; analyzed=[]; decimal_rows=[]
        for e in entries:
            args=(e['H0'],e['cdf'][-1],e['R'],e['S'],e['mean_lag_s'],e['second_moment_s2'],T)
            fp=analyze_scalar(*args); dec=decimal_scalar(*args)
            fp['decimal80_checks']=compare_decimal(fp,dec,T); analyzed.append(fp); decimal_rows.append(dec)
        models[model]={'birth_columns':analyzed[:2],'selected':analyzed[2],'birth_mixture':mixture(analyzed[:2],analyzed[2],T)}
        # Independent Decimal mixture sums and variance, separate from float mixture.
        with localcontext() as ctx:
            ctx.prec=80
            dcols=decimal_rows[:2]; ds=decimal_rows[2]; dh=sum(x['H0'] for x in dcols)
            dvar=sum(x['H0']/dh*(x['total']['variance_s2']+(x['mu_s']-ds['mu_s'])**2) for x in dcols)
            models[model]['decimal_mixture_variance_check']=check('decimal_mixture_variance',models[model]['selected']['total']['variance_s2'],float(dvar),T*T)
            dweights=[]
            for dc in dcols:
                dw={}
                for key,term in [('eventual',lambda c:c['H0']),('early',lambda c:c['H0']*c['p']),('tail',lambda c:c['H0']*(1-c['p'])),('mean_share',lambda c:c['H0']*c['mu_s'])]:
                    dw[key]=term(dc)/sum(term(c) for c in dcols)
                dweights.append(dw)
            dchecks={}
            for i,dw in enumerate(dweights):
                for key,value in dw.items():
                    dchecks[str(i)+'.'+key]=check('decimal_weight',models[model]['birth_mixture']['weights'][i][key]['value'],float(value))
            for key in ('p','R','S','mu_s','m2_s2'):
                dchecks[key]=check('decimal_mixture.'+key,models[model]['selected'][key],float(sum(c['H0']*c[key]/dh for c in dcols)),T*T if key=='m2_s2' else T if key=='mu_s' else 1)
            models[model]['decimal_mixture_checks']=dchecks
            decimals[model]={'columns':decimal_rows,'birth_total_variance_s2':dvar,'birth_weights':dweights}
        plots[model]={'time_years':[u*T/year for u in raw['sample_u']],'cdf':[e['cdf'] for e in entries], 'density_per_s':[[k/e['H0'] for k in e['kernel_per_s']] for e in entries], 'mean_years':[[a['early']['mean_s']/year,e['current_ramp_ancestry_mean_s']/year,a['mu_s']/year,a['tail_residual']['mean_s']/year] for a,e in zip(analyzed,entries)], 'weights':models[model]['birth_mixture']['weights']}
    difference={}
    for key in ('p','R','S','mu_s','m2_s2'):
        a=models['fullBED']['selected'][key]; b=models['legacy']['selected'][key]
        difference[key]={'raw':a-b,'signed_relative':(a-b)/b if b else None}
    output={'schema':'cr-phys02f-tail-analysis.v1','status':'NUMERICALLY_CHECKED_SAVED9600_SCALARS','T_s':T,'year_s':year,'models':models,'selected_model_difference':difference,'claim_ceiling':['Heat-normalized delay measure, not particle lifetime or fraction of all source energy.','Uncapped and residual moments assume continuation of frozen finite operator; long-time bath validity and mesh convergence unresolved.','No new propagation, interpolation quantiles, or operator construction.'],'routing':{'requested_backend':'gpt-6.1-sol','requested_backend_verification':'NOT_INDEPENDENTLY_VERIFIED','observed_host_label':None,'observed_host_verification':'NOT_INDEPENDENTLY_VERIFIED'}}
    dest=unit/'evidence/analysis'; dest.mkdir(parents=True,exist_ok=True)
    for name,obj in [('NUMERICAL_ARTIFACT.json',output),('DECIMAL80_ORACLE.json',stringify(decimals)),('PLOTTING_DATA.json',plots)]:
        (dest/name).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
    make_plots(unit,plots)
    print(json.dumps({'status':output['status'],'models':{m:{'p':models[m]['selected']['p'],'mean_years':models[m]['selected']['mu_s']/year,'tail_remaining_years':models[m]['selected']['tail_residual']['mean_s']/year} for m in models}},sort_keys=True))


def make_plots(unit, data):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    # Reload persisted plotting data: figures consume only the saved JSON.
    data=json.loads((unit/'evidence/analysis/PLOTTING_DATA.json').read_text())
    labels=['Birth 0.1–10 eV','Birth 10–900 eV','Selected sum']; colors=['#2166ac','#b35806','#333333']
    fig,axes=plt.subplots(1,3,figsize=(16,4.7),layout='constrained')
    for i,(label,color) in enumerate(zip(labels,colors)):
        axes[0].plot(data['fullBED']['time_years'],data['fullBED']['cdf'][i],color=color,label=label,marker='o',markersize=3)
    axes[0].plot(data['legacy']['time_years'],data['legacy']['cdf'][2],color='#aa3377',ls='--',label='Legacy selected')
    axes[0].set(xlabel='Delay (years)',ylabel='Cumulative eventual heat fraction',title='CDF on saved times only'); axes[0].legend(fontsize=8)
    categories=['Early conditional','Current ramp ancestry','Uncapped','Tail remaining']
    x=np.arange(4)
    for i,(label,color) in enumerate(zip(labels,colors)):
        axes[1].plot(x,data['fullBED']['mean_years'][i],marker='o',color=color,label=label)
    axes[1].plot(x,data['legacy']['mean_years'][2],marker='x',ls='--',color='#aa3377',label='Legacy selected')
    axes[1].set_yscale('log'); axes[1].set_xticks(x,categories,rotation=25,ha='right'); axes[1].set(ylabel='Mean delay or remaining delay (years)',title='Mean diagnostics (log scale)')
    weightkeys=['eventual','early','tail','mean_share']; low=[data['fullBED']['weights'][0][k]['value'] for k in weightkeys]; high=[data['fullBED']['weights'][1][k]['value'] for k in weightkeys]
    axes[2].bar(x,low,color=colors[0],label=labels[0]); axes[2].bar(x,high,bottom=low,color=colors[1],label=labels[1])
    axes[2].plot(x,[data['legacy']['weights'][0][k]['value'] for k in weightkeys],color='#aa3377',marker='x',ls='none',label='Legacy low-birth fraction')
    axes[2].set_xticks(x,['Eventual heat','Early heat','Tail heat','Mean contribution'],rotation=25,ha='right'); axes[2].set(ylim=(0,1),ylabel='Fraction',title='Source birth mixture'); axes[2].legend(fontsize=8)
    for ax in axes: ax.grid(axis='y',alpha=.2)
    fig.suptitle('Frozen 9600-state heat-delay diagnostics: fullBED and selected legacy comparison',fontsize=13)
    dest=unit/'evidence/figures'; dest.mkdir(parents=True,exist_ok=True)
    for ext in ('png','pdf'): fig.savefig(dest/('TAIL_DIAGNOSTICS.'+ext),dpi=180)
    plt.close(fig)


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--repo',type=Path,required=True); parser.add_argument('--unit',type=Path,required=True)
    args=parser.parse_args(); run(args.repo.resolve(),args.unit.resolve())
