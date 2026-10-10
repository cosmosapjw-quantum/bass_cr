"""Independent primary-source moment algebra, without importing cascade code."""
from pathlib import Path
import datetime
import hashlib
import json
import time
from fractions import Fraction
import mpmath as mp

ROOT = Path(__file__).resolve().parent
START = time.perf_counter()
mp.mp.dps = 50


def g_h_w(w):
    if not w:
        return mp.mpf(128) / (3 * mp.exp(4))
    s = mp.sqrt(w)
    return (mp.mpf(128)/3 * mp.exp(-4*mp.atan(s)/s)
            / ((1+w)**4 * (-mp.expm1(-2*mp.pi/s))))


def ni_integrand_y(y):
    # w=(1-y)/y; g(w)*|dw/dy|, written independently in y.
    if not y:
        return mp.mpf(0)
    if y == 1:
        return mp.mpf(128)/(3*mp.exp(4))
    k = mp.sqrt(y/(1-y))
    return mp.mpf(128)/3 * y**2 * mp.exp(-4*k*mp.atan(1/k)) / (-mp.expm1(-2*mp.pi*k))


w_knots = [0, 1, 10, 100, 1000, mp.inf]
y_knots = [0, mp.mpf('.001'), mp.mpf('.01'), mp.mpf('.1'), mp.mpf('.5'), 1]
ni_w = mp.quad(g_h_w, w_knots)
q_w = mp.quad(lambda w: 2*g_h_w(w)/(1+w), w_knots)
ni_y = mp.quad(ni_integrand_y, y_knots)
q_y = mp.quad(lambda y: 2*y*ni_integrand_y(y), y_knots)
discrepancies = {'Ni_w_minus_y': str(ni_w-ni_y), 'Q_w_minus_y': str(q_w-q_y)}
checks = {
    'H_Ni_transform': abs(ni_w-ni_y) <= mp.mpf('1e-35'),
    'H_Q_transform': abs(q_w-q_y) <= mp.mpf('1e-35'),
    'H_Ni_table1': abs(ni_w-mp.mpf('.4349958493')) <= mp.mpf('5e-10'),
}
coef = {3: Fraction('8.24012'), 4: Fraction('-10.4769'), 5: Fraction('3.96496'), 6: Fraction('-0.0445976')}
he_ni = sum(c/Fraction(k-1) for k,c in coef.items())
he_q = sum(c/Fraction(k) for k,c in coef.items())  # N=2, so2/N=1.
he_k = 2-he_ni/2
as_mp = lambda f: mp.mpf(f.numerator)/f.denominator
samples = []
for energy in (15,20,25,30,60,100,500,900):
    t = mp.mpf(energy)/mp.mpf('13.6057')
    upper = (t-1)/2
    d = mp.quad(lambda w:g_h_w(w)/(1+w), [0,upper])
    samples.append({'incident_eV':energy,'D_H(t)':str(d),'g_H(0)':str(g_h_w(0)),
                    'g_H((t-1)/2)':str(g_h_w(upper))})

out = {
    'work_unit':'CR-PHYS02C-SOURCE-ALGEBRA',
    'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'contract_sha256':hashlib.sha256((ROOT/'ALGEBRA_CONTRACT.json').read_bytes()).hexdigest(),
    'environment':{'mpmath_version':mp.__version__,'decimal_precision':mp.mp.dps},
    'H': {'Ni':str(ni_w),'Q':str(q_w),'K_BED':str(2-ni_w),
          'threshold_df_dw':str(g_h_w(0)), 'independent_form_values':{'Ni_y':str(ni_y),'Q_y':str(q_y)},
          'comparison_to_source_Table1':{'printed_Ni':'.4349958493','absolute_error':str(ni_w-mp.mpf('.4349958493'))},
          'D_samples':samples},
    'He': {'Ni_exact_rational':str(he_ni),'Ni_decimal':str(as_mp(he_ni)),
           'Q_exact_rational':str(he_q),'Q_decimal':str(as_mp(he_q)),
           'K_BED_exact_rational':str(he_k),'K_BED_decimal':str(as_mp(he_k)),
           'threshold_df_dw':str(as_mp(sum(coef.values()))),
           'K_printed_Muller2009_minus_consistent':str(mp.mpf('1.1860')-as_mp(he_k)),
           'Q_NIST_minus_consistent':str(mp.mpf('.8841')-as_mp(he_q))},
    'checks':checks,'discrepancies':discrepancies,
    'status':'PASS' if all(checks.values()) else 'FAIL',
    'elapsed_s':time.perf_counter()-START,
    'limitations':['No cascade code imported or run.','No empirical accuracy calibration.','Integration equality is numerical, not an interval certificate.']
}
(ROOT/'SOURCE_ALGEBRA_RESULT.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
raise SystemExit(0 if all(checks.values()) else 1)
