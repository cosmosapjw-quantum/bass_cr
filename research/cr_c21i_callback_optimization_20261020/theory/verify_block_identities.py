"""Exact rational checks for C21I block/clock/scaling formulas; no ODE run."""
from fractions import Fraction as F
from pathlib import Path
import json
import datetime


def zero(m, n):
    return [[F(0) for _ in range(n)] for _ in range(m)]


def eye(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def add(a, b):
    return [[x + y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def scale(a, c):
    return [[c*x for x in row] for row in a]


def mul(a, b):
    return [[sum((x*y for x, y in zip(row, col)), F(0))
             for col in zip(*b)] for row in a]


def col(v):
    return [[x] for x in v]


def solve(a, b):
    """Exact row-pivoted Gauss elimination, independent of Wolfram LinearSolve."""
    n = len(a)
    q = [list(row) + [v] for row, v in zip(a, b)]
    for j in range(n):
        p = next((i for i in range(j, n) if q[i][j] != 0), None)
        if p is None:
            raise ArithmeticError("singular matrix")
        q[j], q[p] = q[p], q[j]
        pivot = q[j][j]
        q[j] = [x/pivot for x in q[j]]
        for i in range(n):
            if i != j:
                factor = q[i][j]
                q[i] = [x-factor*y for x, y in zip(q[i], q[j])]
    return [row[-1] for row in q]


def flatten(v):
    return [row[0] for row in v]


def build(m, g, ell):
    a = [[F(2*i-j+1, 13) for j in range(g)] for i in range(m)]
    b = [[F(3*i+j-2, 17) for j in range(m)] for i in range(g)]
    c = [[F(-5 if i == j else i-j, 7) for j in range(g)] for i in range(g)]
    p = [[F(i-2*j+3, 19) for j in range(m)] for i in range(ell)]
    q = [[F(i+j-1, 23) for j in range(g)] for i in range(ell)]
    j = [zero(1, m)[0]+a[i]+zero(1, ell)[0] for i in range(m)]
    j += [b[i]+c[i]+zero(1, ell)[0] for i in range(g)]
    j += [p[i]+q[i]+zero(1, ell)[0] for i in range(ell)]
    return a, b, c, p, q, j


def main():
    rows = []
    for m, g, ell in [(3, 2, 3), (3, 4, 2)]:
        a, b, c, p, q, j = build(m, g, ell)
        n = m+g+ell
        v = [F((-1)**i*(i+1), i+3) for i in range(n)]
        jvp = (flatten(mul(a, col(v[m:m+g])))
               + flatten(add(mul(b, col(v[:m])), mul(c, col(v[m:m+g]))))
               + flatten(add(mul(p, col(v[:m])), mul(q, col(v[m:m+g])))))
        assert jvp == flatten(mul(j, col(v)))
        for sigma in [F(0), F(1, 7), F(-1, 9), F(3, 11)]:
            w = add(eye(n), scale(j, -sigma))
            schur = add(add(eye(g), scale(c, -sigma)), scale(mul(b, a), -sigma*sigma))
            rhs_g = add(col(v[m:m+g]), scale(mul(b, col(v[:m])), sigma))
            kg = solve(schur, flatten(rhs_g))
            kt = flatten(add(col(v[:m]), scale(mul(a, col(kg)), sigma)))
            kl = flatten(add(add(col(v[m+g:]), scale(mul(p, col(kt)), sigma)), scale(mul(q, col(kg)), sigma)))
            candidate = kt+kg+kl
            residual = [x-y for x, y in zip(flatten(mul(w, col(candidate))), v)]
            assert not any(residual) and candidate == solve(w, v)
            ft = [F(i+2, 29) for i in range(n)]
            bclock = F(2, 5)
            augmented_j = [[F(0)]*(n+1)]+[[ft[i]]+j[i] for i in range(n)]
            augmented_rhs = [bclock]+v
            augmented_candidate = [bclock]+solve(w, [r+sigma*f*bclock for r, f in zip(v, ft)])
            augmented_residual = [x-y for x, y in zip(flatten(mul(add(eye(n+1), scale(augmented_j, -sigma)), col(augmented_candidate))), augmented_rhs)]
            assert not any(augmented_residual)
            rows.append({"M":m,"G":g,"L":ell,"shift":str(sigma),"schur_residual_zero":True,"full_solution_equal":True,"jvp_equal":True,"clock_residual_zero":True})
    alpha, beta = F(1, 500), F(1, 100)
    scaling = []
    for d, eo, yo, yn in [(F(3, 7),F(-2, 5),F(-4),F(2)),(F(100),F(7),F(0),F(-3)),(F(1, 10000),F(1),F(2),F(3))]:
        physical = d*eo/(alpha*d+beta*max(abs(d*yo),abs(d*yn)))
        scaled = eo/(alpha+beta*max(abs(yo),abs(yn)))
        assert physical == scaled
        scaling.append({"D":str(d),"ratio_equal":True})
    singular_rejected = False
    try:
        solve([[F(0),F(0)],[F(0),F(0)]],[F(1),F(0)])
    except ArithmeticError:
        singular_rejected = True
    assert singular_rejected
    report={"recorded_at_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"classification":"PYTHON_PASS","status":"PASS_SCOPED","scope":"exact rational block/clock/scaling identities; no chemistry or ODE integration; does not establish arbitrary-input numerical conditioning","cases":rows,"scaling_cases":scaling,"singular_matrix_rejected":singular_rejected,"exit_code":0}
    target=Path(__file__).parent/'raw'/'FRACTION_INDEPENDENT_CHECK.json'
    target.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
