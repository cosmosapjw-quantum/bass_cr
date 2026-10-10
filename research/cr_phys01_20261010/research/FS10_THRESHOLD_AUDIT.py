"""Read-only interval audit of acquired FS2010 raw tables; no provider changes."""
from pathlib import Path
from decimal import Decimal
import json
import numpy as np
from scipy.optimize import linprog

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / 'vendor/fs10/official/x_int_tables'

def interval(token):
    d = Decimal(token)
    # Printed zero is interpreted as an exact zero channel, not +/-0.5.
    if d == 0:
        return (0., 0.)
    half = Decimal('0.5') * Decimal(10) ** d.as_tuple().exponent
    return float(max(Decimal(0), d-half)), float(d+half)

rows, bounds = [], []
files = []
for p in sorted(BASE.glob('*.dat')):
    tokens = [line.split() for line in p.read_text().splitlines()[3:] if line.strip()]
    a = np.array([[float(t) for t in row] for row in tokens])
    rows.extend(a)
    for row in tokens:
        elo, ehi = interval(row[0]); flo, fhi = interval(row[1])
        ns = [interval(row[k]) for k in (5,6,7)]
        if float(row[1]) > 0:
            bounds.append(([v[0]/ehi for v in ns], [v[1]/elo for v in ns], flo, fhi))
    tests = {}
    for name, chi in {
        'rounded_common': [13.6,24.6,54.4],
        'modern_comparison_not_source_verified': [13.5984,24.5874,54.4178],
        'official_xray_example': [13.58,24.586,54.398],
        'table_inferred_candidate': [13.598,24.586,54.392],
    }.items():
        fi = a[:,5:8] @ np.array(chi) / a[:,0]
        tests[name] = {'thresholds_eV':chi,
            'max_abs_count_derived_fion_minus_table_fion':float(np.max(abs(fi-a[:,1]))),
            'max_abs_count_derived_energy_sum_minus_one':float(np.max(abs(fi+a[:,2]+a[:,3]-1)))}
    files.append({'file':p.name,'raw_energy_closure_max_abs':float(np.max(abs(a[:,1:4].sum(axis=1)-1))), 'threshold_tests':tests})

a = np.array(rows); m = a[:,5:8]/a[:,0,None]; sol=np.linalg.lstsq(m,a[:,1],rcond=None)[0]
aub, bub = [], []
for low, high, flo, fhi in bounds:
    aub.extend([low,[-v for v in high]]);bub.extend([fhi,-flo])
options = {'dual_feasibility_tolerance':1e-9,'primal_feasibility_tolerance':1e-9}
intervals=[]
for k in range(3):
    c=np.zeros(3);c[k]=1
    lo=linprog(c,A_ub=aub,b_ub=bub,bounds=[(10,20),(20,30),(40,70)],method='highs',options=options)
    hi=linprog(-c,A_ub=aub,b_ub=bub,bounds=[(10,20),(20,30),(40,70)],method='highs',options=options)
    intervals.append({'species':['HI','HeI','HeII'][k], 'feasible':bool(lo.success and hi.success),
        'min_eV':float(lo.x[k]) if lo.success else None,'max_eV':float(hi.x[k]) if hi.success else None})

# Diagnose, rather than conceal, inconsistency beyond displayed-digit rounding.
slack_fit=linprog([0,0,0,1],A_ub=[row+[-1.] for row in aub],b_ub=bub,
    bounds=[(10,20),(20,30),(40,70),(0,None)],method='highs',options=options)
slack_report={'feasible':bool(slack_fit.success),
    'minimum_extra_absolute_fion_slack':float(slack_fit.x[3]) if slack_fit.success else None,
    'thresholds_at_minimum_slack_eV':slack_fit.x[:3].tolist() if slack_fit.success else None,
    'meaning':'Extra dimensionless discrepancy required beyond printed-digit uncertainty; not licensed as hidden renormalization.'}

out={'schema':'fs10_threshold_audit_v1','status':'DIAGNOSTIC_NOT_SOURCE_CONSTANT_CERTIFICATION',
    'primary_sources':{'official_tar':'https://cosmicdawn.astro.ucla.edu/elec_interp.tar','paper':'https://arxiv.org/abs/0910.4410'},
    'source_constants':{'xray_interp.c_Eion_eV':[13.58,24.586,54.398],
        'xray_interp.c_photoion_gates_eV':[13.6,24.586,54.4],
        'original_MC_generator_constants':'NOT_IN_RELEASED_ARCHIVE'},
    'least_squares_inference_all_rows_eV':sol.tolist(),
    'least_squares_max_abs_fion_residual':float(np.max(abs(m@sol-a[:,1]))),
    'printed_precision_interval_method':'Per positive token +/- half last printed decimal unit; exact zero channels; interval linear inequalities on fion=sum(n_i*chi_i)/E; positive chi; solver feasibility tolerance 1e-9. Conservative compatibility region, not statistical confidence interval or proof of generator constants.',
    'compatible_threshold_coordinate_intervals':intervals,
    'strict_printed_rounding_status':'INFEASIBLE' if not all(r['feasible'] for r in intervals) else 'FEASIBLE',
    'minimum_extra_slack_diagnostic':slack_report,
    'helium_abundance':{'original_table_generator_YHe':None,'status':'NOT_EXPLICIT_IN_ARCHIVE_OR_INSPECTED_PAPER',
        'xray_example_H_number_weight':.92,'xray_example_He_number_weight':.08,
        'xray_example_He_over_H':.08/.92,'xray_example_implied_mass_fraction_using_mHe_over_mH_4':.32/(.92+.32),
        'warning':'These example spectrum weights do not certify original cascade table abundance. Do not relabel table YHe=.24 or .248.'},
    'file_results':files}
(HERE/'FS10_THRESHOLD_AUDIT.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'least_squares':sol.tolist(),'compatible_intervals':intervals,'xHII_0.01':next(f for f in files if f['file']=='log_xi_-2.0.dat')},indent=2))
