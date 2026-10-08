"""Independent Fraction replay of real and imaginary 2x2 rate identities."""
from fractions import Fraction as F
import json

def matrix(rows):return [[F(x) for x in row] for row in rows]
def tr(a):return list(map(list,zip(*a)))
def mul(a,b):return [[sum((x*y for x,y in zip(row,col)),F(0)) for col in zip(*b)] for row in a]
def add(a,b):return [[x+y for x,y in zip(r,s)] for r,s in zip(a,b)]
def scale(c,a):return [[c*x for x in row] for row in a]
def sub(a,b):return add(a,scale(-1,b))
def inv2(a):
    det=a[0][0]*a[1][1]-a[0][1]*a[1][0]
    return scale(1/det,[[a[1][1],-a[0][1]],[-a[1][0],a[0][0]]])

def replay():
    s=matrix([[4,2],[2,5]])
    si=inv2(s)
    j=matrix([[1],[0]])
    x=matrix([[F(1,2)],[0]])
    y=matrix([[-F(1,4)],[F(1,2)]])
    v=matrix([[F(1,2),-F(1,4)],[0,F(1,2)]])
    q=scale(F(1,4),mul(mul(s,j),mul(tr(j),s)))
    assertions=0
    def check(a,b):
        nonlocal assertions
        assert a==b,(a,b)
        assertions+=1
    check(mul(mul(tr(v),s),v),matrix([[1,0],[0,1]]))
    for values in ((1,2,3,4),(0,-3,3,0),(7,0,-2,1),(-5,8,1,-9),(2,2,2,2),(0,0,0,0)):
        d=matrix([values[:2],values[2:]])
        sd=add(d,tr(d))
        a=scale(-1,mul(si,d))
        qd=add(scale(F(1,4),mul(mul(sd,j),mul(tr(j),s))),
               scale(F(1,4),mul(mul(s,j),mul(tr(j),sd))))
        qd=sub(qd,scale(sd[0][0]/16,mul(mul(s,j),mul(tr(j),s))))
        w=add(qd,add(mul(tr(a),q),mul(q,a)))
        e=mul(mul(tr(y),d),x)[0][0]
        wc=matrix([[0,e],[e,0]])
        check(mul(mul(tr(v),w),v),wc)
        check(w,mul(mul(mul(mul(s,v),wc),tr(v)),s))
        check(mul(mul(tr(x),w),x),matrix([[0]]))
        check(mul(mul(tr(y),w),y),matrix([[0]]))
    b=matrix([[2,1],[0,2]])
    for a,g,z in ((2**80,F(1,7),-2**70),(3,2,5),(-4,-3,2),(0,0,0)):
        h=mul(mul(tr(b),matrix([[a,g],[g,z]])),b)
        # W=i*(H S^-1 Q-Q S^-1 H); E=i*Y^T H X.
        wi=sub(mul(mul(h,si),q),mul(mul(q,si),h))
        e=mul(mul(tr(y),h),x)[0][0]
        check(e,F(g))
        check(mul(mul(tr(v),wi),v),matrix([[0,-e],[e,0]]))
    return {'status':'PASS','arithmetic':'fractions.Fraction; no floating-point conversion',
            'exact_assertions':assertions,'real_connection_families':6,'imaginary_hamiltonian_families':4,
            'physical_queries':0,'scope':'finite 2x2 algebraic replay, not arbitrary-dimension proof'}

if __name__=='__main__':print(json.dumps(replay(),indent=2))
