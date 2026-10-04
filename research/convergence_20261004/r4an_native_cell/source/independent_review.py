"""Read-only review. No producer imports, compiler, native, or atomic calls.
Exact fixture integral checks plus high precision Cartesian angular quadrature.
The latter is numerical validation, not a new rigorous enclosure proof.
"""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json
import mpmath as mp
import sympy as sp
ROOT=Path(__file__).resolve().parents[1]
checks=[]
def check(name,ok):
    checks.append({'name':name,'pass':bool(ok)})
    if not ok:raise AssertionError(name)
def as_mp(q):
    f=F(q);return mp.mpf(f.numerator)/f.denominator

def direct(rec,N):
    b,z,v,t=map(as_mp,[rec[k] for k in ('b','z','v','t')]);R=mp.sqrt(b*b+z*z);u,w=as_mp(rec['u']),as_mp(rec['w']);e=[b/R,0,z/R];e1=[-z/R,0,b/R];e2=[0,-1,0]
    if rec['chart']=='regular':
        pts=rec['regular_vertices'];r0=pts[0][0]+u*(pts[1][0]-pts[0][0]+w*(pts[2][0]-pts[1][0]));r1=pts[0][1]+u*(pts[1][1]-pts[0][1]+w*(pts[2][1]-pts[1][1]));jac=u*r0*r1/R
    else:
        radius=as_mp(rec['first_radius']);r=radius*u;other=R+r*(2*w-1)
        r0,r1=(r,other) if rec['chart']=='origin_T' else (other,r)
        jac=2*radius*r*r*other/R
    A=(r0*r0-r1*r1+R*R)/(2*R);rho=mp.sqrt(r0*r0-A*A)
    def field(x,l,m,conj):
        r=mp.sqrt(sum(y*y for y in x));scale=mp.mpf(1) if l==0 else mp.mpf(2)/3
        f=scale*(1-r/8)**2;fp=-scale*(1-r/8)/4
        if l==0:return f,[fp*y/r for y in x]
        c=[mp.mpc(0) for _ in range(3)]
        if m==0:c[2]=mp.sqrt(3)
        else:c[0]=(1 if m==-1 else -1)*mp.sqrt(mp.mpf(3)/2);c[1]=-mp.j*mp.sqrt(mp.mpf(3)/2)
        if conj:c=[mp.conj(y) for y in c]
        n=[y/r for y in x];g=sum(a*b for a,b in zip(c,n))
        return f*g,[(fp-f/r)*g*n[k]+(f/r)*c[k] for k in range(3)]
    ell0,ell1,m0,m1=rec['entry'];acc=[mp.mpc(0) for _ in range(4)]
    for j in range(N):
        theta=2*mp.pi*j/N
        xt=[A*e[k]+rho*(mp.cos(theta)*e1[k]+mp.sin(theta)*e2[k]) for k in range(3)];xp=[xt[k]-R*e[k] for k in range(3)]
        ft,gt=field(xt,ell0,m0,True);fp,gp=field(xp,ell1,m1,False)
        s=ft*fp;h=sum(a*b for a,b in zip(gt,gp))/2+mp.j*v*gt[2]*fp/2-(1/r0+1/r1)*s;d=-v*ft*gp[2]-mp.j*v*v*s/2
        phase=mp.exp(mp.j*(v*xt[2]-v*v*t/2))
        for k,x in enumerate([s,h,d,h-mp.j*d]):acc[k]+=x*phase
    return [x*jac/(2*N) for x in acc]

def main():
    output=ROOT/'evidence/INDEPENDENT_REVIEW.json'
    if output.exists():raise FileExistsError('read-only review evidence already exists')
    pilot=json.loads((ROOT/'evidence/PILOT_v1/RESULT.json').read_text())
    # Independent exact 2-D integrals for normalized constant s fields.
    u,w=sp.symbols('u w');r0=1*0+2+u;r1=4+u*w
    integ=lambda x:sp.integrate(x,(u,0,1),(w,0,1))
    s_exact=F(str(integ(r0*r1*u/10)));h_exact=F(str(integ(-(r0+r1)*u/10)))
    aa=F(1,8);targets={'regular':(s_exact,h_exact),'origin_T':(aa**3/3,-aa**2/2-aa**3/15),'origin_P':(aa**3/3,-aa**2/2-aa**3/15)}
    for case in pilot['fixtures']:
        expected=dict(zip(['S_TP','H_TP','D_TP','K_TP'],[targets[case['chart']][0],targets[case['chart']][1],F(0),targets[case['chart']][1]]))
        for k,v in case['values'].items():
            for part,q in [('real',expected[k]),('imag',F(0))]:
                d=v['enclosure'][part];lo=F(int(d['lower_numerator']),1<<d['denominator_power2']);hi=F(int(d['upper_numerator']),1<<d['denominator_power2'])
                check(case['chart']+'/'+k+'/'+part,lo<=q<=hi)
        check(case['chart']+'/radius',F(case['radius_l1_upper'])<=F(1,10**16))
    extra=json.loads((ROOT/'evidence/CARTESIAN_CASES.json').read_text());details=[]
    with mp.workdps(80):
        for j,rec in enumerate(extra['records']):
            a=direct(rec,128);b=direct(rec,256);maxdiff=mp.mpf(0)
            for k,x,y in zip(['S_TP','H_TP','D_TP','K_TP'],a,b):
                check(f'Cartesian{j}/{k}/quadrature_agreement',abs(x-y)<mp.mpf('1e-65'))
                vals=rec['values'][k];mid=[]
                for part in ['real','imag']:
                    d=vals[part];mid.append(mp.mpf(int(d['lower_numerator'])+int(d['upper_numerator']))/mp.power(2,d['denominator_power2']+1))
                diff=abs(mp.mpc(*mid)-y);maxdiff=max(maxdiff,diff)
                check(f'Cartesian{j}/{k}/native_match',diff<mp.mpf('1e-60'))
            details.append({'chart':rec['chart'],'entry':rec['entry'],'max_abs_difference':mp.nstr(maxdiff,30)})
    result={'status':'PASS','check_count':len(checks),'checks':checks,'native_or_atomic_calls':0,'producer_imports':False,'proof_assistant':False,'independent_human_or_agent':False,'exact_analytic_fixture_integrals':{'regular_S':str(s_exact),'regular_H':str(h_exact)},'numerical_cartesian_checks':details,'numerical_oracle_is_not_interval_proof':True}
    output.write_text(json.dumps(result,indent=2));print(json.dumps({k:result[k] for k in ['status','check_count','numerical_cartesian_checks']}))
if __name__=='__main__':main()
