"""Quadratic source response from an already verified moment cache.

No CR generator, propagation, physical linear system, or previous evaluator is
imported. Exact rational PSD certificates establish the uniform bounds; plots
only illustrate them.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import platform
import sys
import time
from datetime import datetime, timezone
from decimal import Decimal, localcontext
from fractions import Fraction as F
from pathlib import Path

BASE = Path(__file__).resolve().parent
EXPECTED = '60747f9da89e3596bfeb93a4ec14a1bb58a33bca3a09629fc092f254839f3b7b'
HISTORIES = {
    'constant': (1, 0, 0),
    'linear_rise': (0, 1, 0),
    'convex_rise': (0, 0, 1),
    'concave_rise': (0, 2, -1),
    'quadratic_decline': (1, -2, 1),
    'parabolic_pulse': (0, 4, -4),
}
RISING_VERTICES = ('constant', 'concave_rise', 'convex_rise')


def unpack(x):
    return F(int(x['numerator']), int(x['denominator']))


def packet(x):
    x = F(x)
    with localcontext() as c:
        c.prec = 60
        decimal = str(Decimal(x.numerator) / Decimal(x.denominator))
    return {'numerator': str(x.numerator), 'denominator': str(x.denominator),
            'decimal60': decimal}


def matrix_packet(m):
    return [[packet(x) for x in row] for row in m]


def det(m):
    return m[0][0]*m[1][1] - m[0][1]*m[1][0]


def subscale(a, b, factor):
    return [[a[i][j] - factor*b[i][j] for j in range(2)] for i in range(2)]


def psd_certificate(m):
    assert m[0][1] == m[1][0]
    diagonal = (m[0][0], m[1][1])
    determinant = det(m)
    assert min(diagonal) >= 0 and determinant >= 0
    return {'matrix': matrix_packet(m), 'diagonal_nonnegative': True,
            'determinant': packet(determinant), 'determinant_nonnegative': True}


def outward_percent(value, upper=False, digits=6):
    value = F(100)*value
    scale = 10**digits
    n = -((-value.numerator*scale)//value.denominator) if upper else (value.numerator*scale)//value.denominator
    return f'{Decimal(n)/Decimal(scale):.{digits}f}'


def root_intervals(a, b, c):
    assert a > 0
    discriminant = b*b - 4*a*c
    assert discriminant > 0
    scale = 10**90
    k = math.isqrt(discriminant.numerator*scale*scale//discriminant.denominator)
    lo, hi = F(k, scale), F(k+1, scale)
    assert lo*lo <= discriminant < hi*hi
    intervals = [((-b-hi)/(2*a), (-b-lo)/(2*a)),
                 ((-b+lo)/(2*a), (-b+hi)/(2*a))]
    return intervals, {'a':packet(a), 'b':packet(b), 'c':packet(c),
        'discriminant':packet(discriminant), 'sqrt_lower':packet(lo),
        'sqrt_upper':packet(hi), 'sqrt_bracketing_exact':True}


def witness(af, al, interval):
    rho = sum(interval, F(0))/2
    m = subscale(af, al, rho)
    u, v = -m[0][1], m[0][0]
    if u == 0 and v == 0:
        u, v = -m[1][1], m[1][0]
    peak = max(u*u, (u+v)**2)
    assert peak > 0
    poly = (u*u/peak, 2*u*v/peak, v*v/peak)
    denominator = al[0][0]*poly[0] + 2*al[0][1]*(poly[1]/2) + al[1][1]*poly[2]
    numerator = af[0][0]*poly[0] + af[0][1]*poly[1] + af[1][1]*poly[2]
    ratio = numerator/denominator
    assert denominator > 0
    assert interval[0]-F(1,10**70) <= ratio <= interval[1]+F(1,10**70)
    return {'kind':'squared_linear', 'coefficients_power_basis': [packet(x) for x in poly],
        'source_normalization':'max f(x) on [0,1] = 1; nonnegative polynomial',
        'node_x':packet(-u/v) if v else None,
        'heating_ratio':packet(ratio),
        'role':'Rational approximation to algebraic boundary source; exact boundary uses the exact generalized eigenvalue'}


def main():
    start = time.monotonic()
    started_utc = datetime.now(timezone.utc).isoformat()
    out = BASE/'results'
    if (out/'QUADRATIC_RESPONSE.json').exists():
        raise FileExistsError('Completed result must be reused, not overwritten')
    raw = (BASE/'inputs/CACHED_RESPONSE.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == EXPECTED
    source = json.loads(raw)
    vals, rows = {}, []
    for row in source['rows']:
        h, p, r, s = (unpack(row['moments'][k]) for k in ('H0','p','R','S'))
        assert h > 0 and 0 < s < r < p <= 1 and p*s > r*r
        moments = (p, r, s)
        response = {name:sum((F(c)*m for c,m in zip(poly,moments)),F(0))
                    for name,poly in HISTORIES.items()}
        assert all(x > 0 for x in response.values())
        heat = {name:h*x for name,x in response.items()}
        a = [[h*p,h*r],[h*r,h*s]]
        bubble = h*(r-s)
        assert det(a) > 0 and bubble > 0
        vals[row['model'],row['representation']] = {'h':h,'p':p,'r':r,'s':s,
            'response':response,'heat':heat,'A':a,'B':bubble}
        rows.append({'model':row['model'],'representation':row['representation'],
            'response_over_H0_qstar':{k:packet(x) for k,x in response.items()},
            'heating_coefficient_per_qstar':{k:packet(x) for k,x in heat.items()},
            'A':matrix_packet(a),'det_A':packet(det(a)), 'B':packet(bubble),
            'positive_definite_A':True,'positive_B':True})
    comparison = {}
    for rep in ('selected_record','birth_defined'):
        f,l = vals['fullBED',rep], vals['legacy',rep]
        af,al = f['A'],l['A']
        ratios = {k:f['heat'][k]/l['heat'][k] for k in HISTORIES}
        rising_min = min(RISING_VERTICES, key=ratios.get)
        rising_max = max(RISING_VERTICES, key=ratios.get)
        aa = det(al)
        bb = -(af[0][0]*al[1][1]+af[1][1]*al[0][0]-2*af[0][1]*al[0][1])
        cc = det(af)
        intervals, polynomial = root_intervals(aa,bb,cc)
        auxiliary = f['B']/l['B']
        lower = min(intervals[0][0],auxiliary)
        upper = max(intervals[1][1],auxiliary)
        lower_psd = psd_certificate(subscale(af,al,lower))
        upper_psd = psd_certificate(subscale([[upper*x for x in row] for row in al],af,F(1)))
        assert f['B']-lower*l['B'] >= 0 and upper*l['B']-f['B'] >= 0
        # Exact broad-class inequalities, plus explicitly separated sharp roots.
        comparison[rep] = {
            'named_heating_fullBED_over_legacy_minus1':{k:packet(x-1) for k,x in ratios.items()},
            'rising_class': {'weights':['a','b-a','1-b'],
                'vertices':list(RISING_VERTICES),'minimum_vertex':rising_min,'maximum_vertex':rising_max,
                'ratio_minimum':packet(ratios[rising_min]),'ratio_maximum':packet(ratios[rising_max]),
                'percent_outward_6dp':[outward_percent(ratios[rising_min]-1),outward_percent(ratios[rising_max]-1,True)]},
            'all_nonnegative_quadratics': {
                'definition':'f != 0, degree f <= 2, f(x) >= 0 on [0,1]; f(1) may be zero',
                'generalized_characteristic_polynomial':polynomial,
                'generalized_eigenvalue_intervals':[{'lower':packet(lo),'upper':packet(hi)} for lo,hi in intervals],
                'bubble_ratio':packet(auxiliary),
                'sharp_range_formula':'[min(lambda_minus,B_full/B_legacy), max(lambda_plus,B_full/B_legacy)]',
                'outer_ratio_lower':packet(lower),'outer_ratio_upper':packet(upper),
                'percent_outward_6dp':[outward_percent(lower-1),outward_percent(upper-1,True)],
                'lower_PSD_certificate':lower_psd,'upper_PSD_certificate':upper_psd,
                'bubble_lower_slack':packet(f['B']-lower*l['B']),
                'bubble_upper_slack':packet(upper*l['B']-f['B']),
                'lower_square_witness':witness(af,al,intervals[0]),
                'upper_square_witness':witness(af,al,intervals[1]),
                'bubble_within_eigenvalue_range':intervals[0][1] < auxiliary < intervals[1][0]
            }
        }
    result = {'schema':'cr-m0-quadratic-response.v1','status':'EXACT_RATIONAL_CALCULATION_COMPLETE',
        'input_sha256':EXPECTED,'T_s':source['T_s'],
        'polynomials_power_basis':{k:list(v) for k,v in HISTORIES.items()},
        'normalization':'q=qstar*f(t/T); all displayed named profiles have max f=1; current q(T) can be zero',
        'rows':rows,'comparison':comparison,
        'limits':['Same fixed kernel, bath, spectrum and T as the cache',
                  'Model discrepancy is not error against physical truth',
                  'No arbitrary-history, evolving-bath, cosmic or Bianchi promotion',
                  'No quadratic cumulative heat or post-T heating curve inferred'],
        'representation_policy':'Keep selected_record and birth_defined separate'}
    (out/'QUADRATIC_RESPONSE.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    with (out/'QUADRATIC_RESPONSE.tsv').open('w',newline='') as fp:
        writer = csv.writer(fp,delimiter='\t')
        writer.writerow(['model','representation','source','f_at_T','P_over_H0_qstar','P_per_qstar','model_difference_percent'])
        for row in rows:
            for name,poly in HISTORIES.items():
                delta = comparison[row['representation']]['named_heating_fullBED_over_legacy_minus1'][name]
                writer.writerow([row['model'],row['representation'],name,sum(poly),
                    row['response_over_H0_qstar'][name]['decimal60'],
                    row['heating_coefficient_per_qstar'][name]['decimal60'],
                    packet(100*unpack(delta))['decimal60']])
    arithmetic_wall = time.monotonic()-start

    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes = plt.subplots(2,2,figsize=(13,9),layout='constrained')
    labels = ['Constant','Linear rise','Convex rise','Concave rise','Decline to zero','Parabolic pulse']
    colors = ['#6b7280','#3483bd','#20639b','#49a078','#c27035','#8d5fa8']
    x = np.linspace(0,1,301)
    for (name,poly),label,color in zip(HISTORIES.items(),labels,colors):
        axes[0,0].plot(x,poly[0]+poly[1]*x+poly[2]*x*x,label=label,color=color,lw=1.8)
    axes[0,0].set(xlabel=r'Source time $t/T$',ylabel=r'$q(t)/q_\star$',
                  title='A. Controlled source histories',xlim=(0,1),ylim=(0,1.07))
    axes[0,0].legend(frameon=False,fontsize=8,ncol=2)
    f,l = vals['fullBED','selected_record'],vals['legacy','selected_record']
    values = [100*float(f['response'][name]) for name in HISTORIES]
    bars=axes[0,1].bar(range(6),values,color=colors,width=.7)
    axes[0,1].bar_label(bars,fmt='%.4f',fontsize=8,padding=3)
    axes[0,1].set_xticks(range(6),['Const.','Linear','Convex','Concave','Decline','Pulse'])
    axes[0,1].set(ylabel=r'$\mathcal P_h(T)/(H_0q_\star)$ (%)',ylim=(0,7.4),
                  title='B. Heating at T (fullBED)')
    cmp=comparison['selected_record']
    broad=cmp['all_nonnegative_quadratics']
    n0=float(unpack(broad['lower_square_witness']['node_x']))
    n1=float(unpack(broad['upper_square_witness']['node_x']))
    node=np.linspace(min(0,n0,n1)-.015,max(1,n0,n1)+.015,801)
    ff=float(f['h'])*(float(f['p'])*node**2-2*float(f['r'])*node+float(f['s']))
    ll=float(l['h'])*(float(l['p'])*node**2-2*float(l['r'])*node+float(l['s']))
    axes[1,0].plot(node,100*(ff/ll-1),color='#20639b',lw=2,label=r'$f(x)\propto(x-r)^2$')
    for bound,style,label in [('outer_ratio_lower','--','All nonnegative quadratics: bounds'),('outer_ratio_upper','--',None)]:
        axes[1,0].axhline(100*float(unpack(broad[bound])-1),color='#b14d35',ls=style,lw=1.1,label=label)
    rl=100*float(unpack(cmp['rising_class']['ratio_minimum'])-1)
    ru=100*float(unpack(cmp['rising_class']['ratio_maximum'])-1)
    axes[1,0].axhspan(rl,ru,color='#49a078',alpha=.2,label='Nondecreasing normalized subclass')
    axes[1,0].axhline(0,color='#909090',lw=.6)
    axes[1,0].set(xlabel=r'Position $r$ of source minimum',ylabel='(fullBED / legacy - 1) (%)',
                  title='C. Source shape and model difference')
    axes[1,0].legend(frameon=False,fontsize=8,loc='best')
    grid=np.linspace(0,1,101)
    aa,bb=np.meshgrid(grid,grid)
    def rising_heat(v):
        return float(v['h'])*(aa*float(v['p'])+(bb-aa)*float(2*v['r']-v['s'])+(1-bb)*float(v['s']))
    dd=np.ma.array(100*(rising_heat(f)/rising_heat(l)-1),mask=aa>bb)
    im=axes[1,1].pcolormesh(aa,bb,dd,shading='auto',cmap='viridis',rasterized=True)
    axes[1,1].plot([0,1],[0,1],color='#555555',lw=.8)
    axes[1,1].set(xlabel=r'$a=q(0)/q_\star$',ylabel=r'Bernstein coefficient $b$',
                  title=r'D. Rising family: $0\leq a\leq b\leq1$',xlim=(0,1),ylim=(0,1))
    fig.colorbar(im,ax=axes[1,1],label='Heating difference (%)',shrink=.85)
    for ax in axes.flat:
        ax.spines[['top','right']].set_visible(False)
        ax.grid(alpha=.12)
        ax.set_axisbelow(True)
    fig.suptitle(r'Quadratic source response at $T=10^{10}$ s (316.88 yr)',fontsize=14)
    fig.supxlabel('Fixed bath and spectrum; zero prehistory; selected records.\nExact bounds use rational PSD certificates, not plot sampling. No physical-truth error bound is implied.',fontsize=9)
    fig.savefig(out/'QUADRATIC_RESPONSE.png',dpi=170)
    fig.savefig(out/'QUADRATIC_RESPONSE.pdf')
    plt.close(fig)
    receipt={'schema':'cr-m0-quadratic-execution.v1','started_utc':started_utc,
        'finished_utc':datetime.now(timezone.utc).isoformat(),'python':sys.version,
        'platform':platform.platform(),'actual_postprocessing_invocations':1,
        'arithmetic_wall_s':arithmetic_wall,'in_process_wall_s':time.monotonic()-start,
        'input_sha256':EXPECTED,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'counts':{'record_rows':4,'named_responses':24,'new_named_responses':12,
                  'reused_named_responses':12,'generalized_pencils_2x2':2,'eigenvalue_enclosures':4,
                  'exact_PSD_bound_certificates':4,'old_producer_runs':0,'old_suite_runs':0,
                  'G':0,'CR_linear_solve':0,'pulse_propagation':0,'expm':0,'resolvent':0,'F_retry':0,'NCP':0},
        'outputs':[{'path':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
                   for p in sorted(out.iterdir()) if p.is_file()]}
    (BASE/'evidence/POSTPROCESS_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'arithmetic_wall_s':arithmetic_wall,
        'in_process_wall_s':receipt['in_process_wall_s'],
        'selected_broad_percent_bounds':broad['percent_outward_6dp'],
        'selected_rising_percent_bounds':cmp['rising_class']['percent_outward_6dp'],
        'selected_extremizer_nodes':[n0,n1], 'old_producer_runs':0,'NCP':0}))


if __name__ == '__main__':
    main()
