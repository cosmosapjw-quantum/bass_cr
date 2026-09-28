"""Research-only probes; no native engine, cloud access or scientific promotion."""
from __future__ import annotations
import json
import math
import sys
import numpy as np
from scipy.linalg import expm


def run():
    out = []
    def record(name, ok, details=None):
        out.append({'check': name, 'passed': bool(ok), 'details': details})
    t, hb = .37, 1.7
    c = np.array([[1+t, 1j*t], [0., 2+t*t]], complex)
    cd = np.array([[1., 1j], [0., 2*t]], complex)
    s = c.conj().T @ c
    sd = cd.conj().T @ c+c.conj().T @ cd
    d = np.array([[t, 1j+t], [2-1j, t*t]])
    h = np.array([[2., t+1j], [t-1j, 3.]])
    ci = np.linalg.inv(c)
    a = -1j/hb*np.linalg.solve(s, h)-np.linalg.solve(s, d)
    g = cd@ci+c@a@ci
    r = sd-d-d.conj().T
    w = ci.conj().T@r@ci
    err = np.linalg.norm(g+g.conj().T-w)
    record('moving_metric_identity', err < 1e-13, float(err))
    h2 = np.array([[11., -4+3j], [-4-3j, -5.]])
    g2 = cd@ci+c@(-1j/hb*np.linalg.solve(s, h2)-np.linalg.solve(s, d))@ci
    err2 = np.linalg.norm(g2+g2.conj().T-w)
    record('Hermitian_H_cancels', err2 < 1e-13, float(err2))
    # Non-Hermitian H contributes i(H†-H)/hbar: it cannot be ignored.
    hn = h.copy(); hn[0,1] += .2
    gn = cd@ci+c@(-1j/hb*np.linalg.solve(s, hn)-np.linalg.solve(s, d))@ci
    wn = ci.conj().T@(r+1j/hb*(hn.conj().T-hn))@ci
    err3 = np.linalg.norm(gn+gn.conj().T-wn)
    record('nonHermitian_H_extra_term', err3 < 1e-13, float(err3))
    actual = np.diag([1., 0.]); reported = np.diag([2., 0.]); dc = reported/2
    record('algebraic_pass_does_not_certify_actual_derivative',
           np.linalg.norm(reported-dc-dc.T)==0 and np.linalg.norm(actual-dc-dc.T)==1)
    k = np.array([[0., 1.], [-1., 0.]])
    e = np.diag([.3, -.2]); duration = .7
    eta = duration*np.linalg.norm(e, 2)
    delta = np.linalg.norm(expm((k+e)*duration)-expm(k*duration), 2)
    record('skew_projection_Duhamel_bound', delta <= math.expm1(eta)+1e-14,
           {'operator_difference': float(delta), 'bound': math.expm1(eta)})
    # E=epsilon I is a commuting example saturating this operator bound.
    eps = .3
    sharp = np.linalg.norm(expm((k+eps*np.eye(2))*duration)-expm(k*duration), 2)
    record('skew_projection_bound_sharp_example', abs(sharp-math.expm1(eps*duration)) < 1e-13)
    ca, pa, cb, pb = 1., .6, 4., .8
    cost_ab = ca+(1-pa)*cb; cost_ba = cb+(1-pb)*ca
    record('early_rejection_order', ca*pb-cb*pa < 0 and cost_ab < cost_ba,
           {'cost_ab':cost_ab,'cost_ba':cost_ba})
    # Actual historical sentinel prefix counts: tails use 2 levels, center uses 8.
    levels = [2]*6+[8]*3+[2]*6
    expected = 15*11+sum(levels)-(2+8+2)
    record('postpass_metric_demand_union', expected == 201 and 27*11 == 297,
           {'prefix_union':expected, 'full_union':297})
    result = {'schema':'NCP_R3_LOCAL_RESEARCH_PROBES_V1', 'checks':out,
              'passed':sum(x['passed'] for x in out), 'failed':sum(not x['passed'] for x in out),
              'cloud_runs':0, 'native_evaluations':0,
              'scope':'synthetic algebra/numerics and derived count only',
              'python':sys.version.split()[0], 'numpy':np.__version__}
    print(json.dumps(result,indent=2,allow_nan=False))
    if result['failed']:
        raise SystemExit(1)

if __name__ == '__main__':
    run()
