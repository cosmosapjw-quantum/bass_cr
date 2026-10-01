"""Independent exact-rational spot replay of a subset of symbolic_checks.wls.

Only Python's standard library is required. This is exact arithmetic at six
parameter points, not a symbolic proof for arbitrary matrices or parameters.
Wolfram performs the separately archived parametric symbolic checks.
"""
from fractions import Fraction as F
import json
from pathlib import Path


def mat(rows): return [[F(x) for x in row] for row in rows]
def tr(a): return list(map(list,zip(*a)))
def mul(a,b): return [[sum(x*y for x,y in zip(row,col)) for col in tr(b)] for row in a]
def add(*args): return [[sum(a[i][j] for a in args) for j in range(len(args[0][0]))] for i in range(len(args[0]))]
def neg(a): return [[-v for v in row] for row in a]
def sub(a,b): return add(a,neg(b))
def inv(a):
    n=len(a); a=[row[:]+[F(i==j) for j in range(n)] for i,row in enumerate(a)]
    for k in range(n):
        pivot=next(i for i in range(k,n) if a[i][k])
        a[k],a[pivot]=a[pivot],a[k]
        p=a[k][k]; a[k]=[v/p for v in a[k]]
        for i in range(n):
            if i != k:
                p=a[i][k]; a[i]=[v-p*w for v,w in zip(a[i],a[k])]
    return [row[n:] for row in a]
def det2(a): return a[0][0]*a[1][1]-a[0][1]*a[1][0]
def scale(x,a): return [[x*v for v in row] for row in a]
def zero(a): return all(v==0 for row in a for v in row)


def forms(s,d,sd,j):
    g=mul(mul(tr(j),s),j)
    k=mul(mul(j,inv(g)),tr(j))
    pi=mul(k,s); q=mul(s,pi)
    qd=sub(add(mul(mul(sd,k),s),mul(mul(s,k),sd)),mul(mul(mul(mul(s,k),sd),k),s))
    a=neg(mul(inv(s),d)) # Independent real lane uses H=0.
    w=add(qd,mul(tr(a),q),mul(q,a))
    return a,pi,q,qd,w


def run():
    rows=[]
    for t in (F(-3,2),F(0),F(2,3)):
        b=mat([[1,t],[0,1]]); bd=mat([[0,1],[0,0]])
        s=mul(tr(b),b); d=mul(tr(b),bd); sd=add(d,tr(d)); j=mat([[1],[1]])
        a,pi,q,qd,w=forms(s,d,sd,j)
        g=2+2*t+t*t; gp=2+2*t
        qd_direct=mat([[gp/g**2,1-gp/g**2],[1-gp/g**2,2*t+gp/g**2]])
        for r in (F(2),F(3,4)):
            T=mat([[r,F(1,3)],[0,1/r]])
            co=lambda x: mul(mul(tr(T),x),T)
            ap,pip,qp,qdp,wp=forms(co(s),co(d),co(sd),mul(inv(T),j))
            lm=F(7,5)
            checks={
                'norm_generator_identity':zero(add(sd,mul(tr(a),s),mul(s,a))),
                'Pi_idempotence':zero(sub(mul(pi,pi),pi)),
                'Pi_metric_self_adjoint':zero(sub(mul(tr(pi),s),mul(s,pi))),
                'Q_Hermitian':zero(sub(tr(q),q)),
                'Q_metric_idempotence':zero(sub(mul(mul(q,inv(s)),q),q)),
                'Qdot_direct_derivative':zero(sub(qd,qd_direct)),
                'W_Hermitian':zero(sub(tr(w),w)),
                'A_similarity':zero(sub(ap,mul(mul(inv(T),a),T))),
                'Pi_similarity':zero(sub(pip,mul(mul(inv(T),pi),T))),
                'Q_congruence':zero(sub(qp,co(q))),
                'Qdot_congruence':zero(sub(qdp,co(qd))),
                'W_congruence':zero(sub(wp,co(w))),
                'generalized_characteristic_value':det2(sub(wp,scale(lm,co(s))))/det2(co(s))==det2(sub(w,scale(lm,s)))/det2(s),
            }
            rows.append({'parameters':{'t':str(t),'r':str(r),'s':'1/3','H':'zero'},'checks':checks,'all_passed':all(checks.values())})
    result={'method':'Python standard-library Fraction exact arithmetic',
            'scope':'Six exact parameter substitutions; not universal symbolic proof',
            'cases':rows,'assertions':sum(len(r['checks']) for r in rows),'all_passed':all(r['all_passed'] for r in rows)}
    if not result['all_passed']: raise AssertionError(result)
    return result


if __name__=='__main__':
    result=run()
    Path(__file__).with_name('EXACT_RATIONAL_REPLAY.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'cases':len(result['cases']),'assertions':result['assertions'],'all_passed':result['all_passed']}))
