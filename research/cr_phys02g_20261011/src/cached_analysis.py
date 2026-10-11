"""One-shot frozen cached scalar analysis; no operator, pulse, expm or solve."""
import argparse
import datetime
from decimal import Decimal, localcontext
import hashlib
import json
import math
from pathlib import Path
import platform
import sys
import time
from moment_bounds import bounds, construct_model, envelope, horizon_brackets, comparison, MomentError

ROOT=Path(__file__).resolve().parents[1]
YEAR=31557600
FRACTIONS=(.5,.9,.95,.99,.999)
DIAGNOSTICS=(1000,10000,30000,100000,300000,1000000)
STATUS='IMPLEMENTATION_VERIFIED_CACHED_SCALAR_PENDING_INDEPENDENT_REVIEW'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path,obj):
    with path.open('x') as h:json.dump(obj,h,indent=2,allow_nan=False);h.write('\n')


def decimal_record(r,T):
    """Independent Decimal80 expression evaluation from source decimal tokens."""
    a=r['mu_s'];b=r['m2_s2'];q=Decimal(1)-r['p']
    first=a-T+T*r['R']
    second=b-(T*a)*2+(T*T)-(T*T*r['S'])
    return dict(q=q,mean=a,second=b,variance=b-a*a,
                residual_mean=first/q if q else None,
                residual_second=second/q if q else None,
                residual_variance=second/q-(first/q)**2 if q else None,
                raw_first=first,raw_second=second)


def decimal_pair(a,b,x):
    """Own Decimal formulas, does not call float bounds or convert its moments."""
    variance=b-a*a
    if variance==0:
        v=Decimal(int(x<a));return dict(lower=v,upper=v)
    if x<a:
        gap=a-x
        lower=1/(1+variance/(gap*gap))
    else:lower=Decimal(0)
    if x<=a:upper=Decimal(1)
    elif a*x<b:upper=a/x
    else:
        gap=x-a
        upper=1/(1+gap*gap/variance)
    return dict(lower=lower,upper=upper)


def decimal_envelope(raw,T,t):
    selected=decimal_record(raw['selected'],T)
    rr=[decimal_record(r,T) for r in raw['birth_columns']]
    H=sum(r['H0'] for r in raw['birth_columns'])
    weights=[r['H0']/H for r in raw['birth_columns']]
    def residual(r):
        if not r['q']:return dict(lower=Decimal(0),upper=Decimal(0))
        if t==T:return dict(lower=r['q'],upper=r['q'])
        pair=decimal_pair(r['residual_mean'],r['residual_second'],t-T)
        return {k:r['q']*v for k,v in pair.items()}
    unconditional=decimal_pair(selected['mean'],selected['second'],t)
    pooled=residual(selected)
    parts=[residual(r) for r in rr]
    birth={k:sum(w*p[k] for w,p in zip(weights,parts)) for k in ('lower','upper')}
    intersection=(dict(lower=selected['q'],upper=selected['q']) if t==T else
                  dict(lower=max(unconditional['lower'],pooled['lower'],birth['lower']),
                       upper=min(unconditional['upper'],pooled['upper'],birth['upper'])))
    return dict(unconditional=unconditional,pooled_residual=pooled,
                birth_residual=birth,intersection=intersection)


def arithmetic_checks(raw,model,curve,brackets):
    checks={}
    with localcontext() as context:
        context.prec=80
        T=Decimal(str(model['T']))
        for name,r,fp in [('selected',raw['selected'],model['selected'])]+[
                (f'birth_{i}',r,fp) for i,(r,fp) in enumerate(zip(raw['birth_columns'],model['birth_columns']))]:
            d=decimal_record(r,T)
            pairs=[('q',fp['q'],d['q'],1),('variance',fp['variance_s2'],d['variance'],1e20)]
            if d['q']:
                tail=fp['tail_residual']
                pairs += [(k,tail[fk],d[dk],scale) for k,fk,dk,scale in [
                    ('residual_mean','mean_s','residual_mean',1e10),
                    ('residual_second','second_s2','residual_second',1e20),
                    ('residual_variance','variance_s2','residual_variance',1e20),
                    ('raw_first','raw_m1_s','raw_first',1e10),
                    ('raw_second','raw_m2_s2','raw_second',1e20)]]
            for key,actual,reference,scale in pairs:
                checks[f'{name}.{key}']=comparison(actual,float(reference),scale)
        H=sum(r['H0'] for r in raw['birth_columns'])
        for i,w in enumerate(model['weights']):
            checks[f'birth_weight_{i}']=comparison(w,float(raw['birth_columns'][i]['H0']/H))
        for key,scale in [('H0',float(H)),('p',1),('R',1),('S',1),('mu_s',1e10),('m2_s2',1e20)]:
            mixed=(H if key=='H0' else sum(r['H0']*r[key] for r in raw['birth_columns'])/H)
            checks[f'decimal_mixture.{key}']=comparison(model['selected'][key],float(mixed),scale)
        points=curve+[(e) for b in brackets for e in
                      [envelope(model,b['lower_s']),envelope(model,b['upper_s'])]]
        for i,e in enumerate(points):
            d=decimal_envelope(raw,T,Decimal(str(e['t_s'])))
            for component in d:
                for key in ('lower','upper'):
                    checks[f'point_{i}.{component}.{key}']=comparison(e[component][key],float(d[component][key]))
    if not all(c['pass_check'] for c in checks.values()):
        failures=[k for k,c in checks.items() if not c['pass_check']]
        raise MomentError('DECIMAL80_MISMATCH',repr(failures))
    return dict(precision=80,scope='Recorded scalar decimal strings; arithmetic measurements only, not physical or forward-error certification',
                checks=checks,measurements=len(checks),
                maximum_absolute_normalized=max(abs(c['signed_normalized']) for c in checks.values()),
                maximum_tolerance_fraction=max(abs(c['signed_normalized'])/c['tolerance'] for c in checks.values()))


def invariants(curve):
    checks=[]
    for component in ('unconditional','pooled_residual','birth_residual','intersection'):
        previous=None
        for e in curve:
            l,u=e[component]['lower'],e[component]['upper']
            checks.append(dict(t_s=e['t_s'],component=component,lower=l,upper=u,
                               order_pass=0<=l<=u<=1,
                               lower_increase=None if previous is None else l-previous[0],
                               upper_increase=None if previous is None else u-previous[1],
                               monotonic_pass=previous is None or(l<=previous[0]+2e-14 and u<=previous[1]+2e-14)))
            previous=(l,u)
    for e in curve[1:]:
        checks.append(dict(t_s=e['t_s'],component='intersection_dominance',
            lower_margin=e['intersection']['lower']-max(e[k]['lower'] for k in ('unconditional','pooled_residual','birth_residual')),
            upper_margin=min(e[k]['upper'] for k in ('unconditional','pooled_residual','birth_residual'))-e['intersection']['upper']))
    if any(not c.get('order_pass',True) or not c.get('monotonic_pass',True) or
           c.get('lower_margin',0)<0 or c.get('upper_margin',0)<0 for c in checks):
        raise MomentError('ENVELOPE_INVARIANT_FAILURE','raw curve')
    return dict(status='NUMERICALLY_CHECKED',checks=checks)


def plot_saved(data_path,figures_dir):
    """Render existing raw plot data; no cached analysis rerun."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    data=json.loads(data_path.read_text())
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.labelsize':11,
                         'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':240})
    colors={'unconditional':'#7a7a7a','pooled_residual':'#0072b2','birth_residual':'#d55e00','intersection':'#242424'}
    labels={'unconditional':'Selected total moments','pooled_residual':'Pooled residual moments',
            'birth_residual':'Birth residual mixture','intersection':'Intersection'}
    fig,axs=plt.subplots(1,2,figsize=(11.8,4.4),sharex=True,sharey=True,layout='constrained')
    for ax,(name,result) in zip(axs,data['models'].items()):
        curve=[r for r in result['curve'] if r['t_s']>data['T_s']]
        x=[r['t_s']/YEAR for r in curve]
        anchor=result['curve'][0]
        ax.scatter([data['T_s']/YEAR],[anchor['intersection']['upper']],color='#242424',s=22,zorder=6)
        ax.annotate('Known tail mass at T',xy=(data['T_s']/YEAR,anchor['intersection']['upper']),
                    xytext=(8,-18),textcoords='offset points',fontsize=8)
        for k in colors:
            low=[r[k]['lower'] for r in curve];high=[r[k]['upper'] for r in curve]
            width=1.8 if k=='intersection' else 1.1
            ax.plot(x,high,color=colors[k],lw=width,label=labels[k])
            ax.plot(x,low,color=colors[k],lw=width,linestyle='--')
        ax.fill_between(x,[r['intersection']['lower'] for r in curve],
                        [r['intersection']['upper'] for r in curve],color='#555555',alpha=.1)
        ax.set(xscale='log',xlabel='Time since birth (years)',title=name,xlim=(data['T_s']/YEAR,1e6),ylim=(0,1))
        ax.grid(True,which='major',color='#dddddd',lw=.5)
    axs[0].set_ylabel('Heat-normalized survival probability')
    axs[1].legend(loc='upper right',frameon=False,fontsize=8)
    fig.suptitle('Two-moment survival envelopes from cached finite-operator moments',fontsize=12)
    fig.savefig(figures_dir/'SURVIVAL_ENVELOPES.pdf');fig.savefig(figures_dir/'SURVIVAL_ENVELOPES.png');plt.close(fig)
    fig,ax=plt.subplots(figsize=(8.2,4.3),layout='constrained')
    for offset,(name,result) in zip((-.13,.13),data['models'].items()):
        color='#0072b2' if name=='fullBED' else '#d55e00'
        for i,b in enumerate(result['brackets']):
            ax.plot([b['lower_s']/YEAR,b['upper_s']/YEAR],[i+offset]*2,color=color,lw=2,
                    marker='|',ms=9,label=name if i==0 else None)
    ax.set(xscale='log',xlabel='Enclosing heat-release horizon (years)',
           yticks=list(range(5)),yticklabels=['50%','90%','95%','99%','99.9%'],ylabel='Cumulative fraction')
    ax.grid(True,axis='x',color='#dddddd',lw=.5);ax.legend(frameon=False)
    ax.set_title('Conservative quantile brackets; no fitted tail or point quantile')
    fig.savefig(figures_dir/'QUANTILE_BRACKETS.pdf');fig.savefig(figures_dir/'QUANTILE_BRACKETS.png');plt.close(fig)
    return dict(matplotlib=matplotlib.__version__,plot_scale='log time, linear probability; no floor or clipping',
                source_plot_data_sha256=sha(data_path),files={p.name:dict(bytes=p.stat().st_size,sha256=sha(p))
                for p in sorted(figures_dir.glob('*')) if p.suffix in ('.png','.pdf')})


def execute():
    start=time.monotonic();utc=datetime.datetime.now(datetime.timezone.utc).isoformat()
    identity=json.loads((ROOT/'state/CONTRACT_IDENTITY.json').read_text())
    for path,pin in identity.items():
        p=ROOT/path
        if p.stat().st_size!=pin['bytes'] or sha(p)!=pin['sha256']:
            raise MomentError('FROZEN_IDENTITY_MISMATCH',path)
    manifest=json.loads((ROOT/'inputs/INPUT_IDENTITIES.json').read_text())
    pin=manifest['local_cached_copy'];source=ROOT/pin['path']
    if source.stat().st_size!=pin['bytes'] or sha(source)!=pin['sha256']:
        raise MomentError('CACHED_INPUT_IDENTITY_MISMATCH',str(source))
    out=ROOT/'evidence/analysis';figures=ROOT/'evidence/figures'
    reservation=out/'CACHED_ANALYSIS_RESERVATION.json'
    write(reservation,dict(start_utc=utc,command=sys.argv,source_sha256=sha(source),
                         physical_G=0,pulse=0,expm=0,linear_solves=0,actual_cached_analysis_run=1))
    raw=json.loads(source.read_text());dec=json.loads(source.read_text(),parse_float=Decimal,parse_int=Decimal)
    T=raw['T_s']
    log_grid=[math.exp(math.log(T)+i*(math.log(1e6*YEAR)-math.log(T))/240) for i in range(241)]
    # Set mathematical logspace endpoints exactly, without changing any bound value.
    log_grid[0]=T;log_grid[-1]=1e6*YEAR
    times=sorted(set(log_grid+[T]+[y*YEAR for y in DIAGNOSTICS]))
    results={}
    for name in ('fullBED','legacy'):
        model=construct_model(raw['models'][name],T)
        curve=[envelope(model,t) for t in times]
        brackets=[horizon_brackets(model,f) for f in FRACTIONS]
        results[name]=dict(model=model,curve=curve,brackets=brackets,
                           decimal80=arithmetic_checks(dec['models'][name],model,curve,brackets),
                           envelope_invariants=invariants(curve))
    artifact=dict(schema='cr-phys02g-cached-analysis.v1',status=STATUS,T_s=T,year_s=YEAR,
        models=results,claim_ceiling=['Recorded scalar two-moment constraints only',
        'No certified forward-error, physical uncertainty, continuum or fixed-bath validity claim',
        'Generic individual bounds sharp; mixture intersection global sharpness not asserted'])
    write(out/'NUMERICAL_ARTIFACT.json',artifact)
    plot=dict(T_s=T,year_s=YEAR,models={name:dict(curve=r['curve'],brackets=r['brackets']) for name,r in results.items()})
    write(figures/'PLOT_DATA.json',plot)
    plotting=plot_saved(figures/'PLOT_DATA.json',figures)
    write(figures/'PLOT_RECEIPT.json',plotting)
    summary=dict(status=STATUS,source_sha256=sha(source),models={name:dict(
        tail_probability=r['model']['selected']['q'],residual_mean_years=r['model']['selected']['tail_residual']['mean_s']/YEAR,
        diagnostics=[e for e in r['curve'] if e['t_s']/YEAR in DIAGNOSTICS],
        quantile_brackets_years=[dict(fraction=b['fraction'],lower=b['lower_s']/YEAR,upper=b['upper_s']/YEAR,
               lower_survival=b['lower_value'],upper_survival=b['upper_value']) for b in r['brackets']],
        decimal80_measurements=r['decimal80']['measurements'],
        decimal80_max_tolerance_fraction=r['decimal80']['maximum_tolerance_fraction']) for name,r in results.items()},
        call_counts=dict(G=0,pulse=0,expm=0,linear_solves=0),curve_points=len(times),
        scientific_review='PENDING_INDEPENDENT_REVIEW',frontier='PREPARED_NOT_EXECUTED')
    write(out/'RESULTS_SUMMARY.json',summary)
    lines=['# Cached scalar moment envelopes','',STATUS,'',
           'Raw FP64 primitives were recomputed; saved residual moments and independent Decimal80 expressions agree within the frozen tolerance. No operator, pulse, expm, or linear solve was called.','',
           'These are conservative two-moment horizon intervals for the recorded finite-operator scalar moments. They are not fitted quantiles, physical uncertainty bands, or certified forward-error bounds. Independent review is pending.','',
           '| Model | Fraction | Lower (years) | Upper (years) |','|---|---:|---:|---:|']
    for name,r in summary['models'].items():
        for b in r['quantile_brackets_years']:lines.append(f"| {name} | {b['fraction']} | {b['lower']:.9g} | {b['upper']:.9g} |")
    with (out/'RESULTS_SUMMARY.md').open('x') as h:h.write('\n'.join(lines)+'\n')
    receipt=dict(status=STATUS,start_utc=utc,end_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        wall_s=time.monotonic()-start,command=sys.argv,actual_exit=0,runtime=dict(python=sys.version,platform=platform.platform()),
        frozen_identities=identity,inputs=dict(path=str(source),bytes=source.stat().st_size,sha256=sha(source)),
        code={str(p.relative_to(ROOT)):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in
              [ROOT/'src/moment_bounds.py',ROOT/'src/cached_analysis.py',ROOT/'tests/test_moment_bounds.py']},
        call_counts=summary['call_counts'],plot=plotting)
    write(out/'EXECUTION_RECEIPT.json',receipt)
    print(json.dumps(summary,indent=2,allow_nan=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--execute',action='store_true')
    parser.add_argument('--plot-only',type=Path)
    args=parser.parse_args()
    if args.plot_only:
        start=time.monotonic();result=plot_saved(args.plot_only,ROOT/'evidence/figures')
        result.update(command=sys.argv,wall_s=time.monotonic()-start,utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
        write(ROOT/'evidence/figures/REPLOT_RECEIPT.json',result)
    elif args.execute:execute()
    else:parser.error('explicit --execute or --plot-only required')
