"""Read-only independent algebra check. Does not import the producer."""
from pathlib import Path
from fractions import Fraction as F
import json,hashlib
import mpmath as mp
r=Path(__file__).resolve().parents[1]
x=json.loads((r/'evidence/run_v1/CERTIFICATE.json').read_text())
g=json.loads((r/'inputs/BASS_CR_R4AB_GRAM_EXACT.json').read_text())['matrices_exact']
a=json.loads((r/'inputs/ANCHOR_S_ENCLOSURE.json').read_text())
meta=json.loads((r/'inputs/BASS_CR_R4AG_CANDIDATE.json').read_text())
checks=[]
def check(condition, name):
    checks.append({'name':name,'pass':bool(condition)})
    if not condition:raise AssertionError(name)

def q(v):return F(v)
G=[[q(v) for v in row] for row in g['G']]
T=[[q(v) for v in row] for row in g['T']]
ch=[(i,d['l'],m) for i,d in enumerate(meta['modes']) for m in range(-d['l'],d['l']+1)]
S=[[G[i][j] if (l,m)==(ll,mm) else F(0) for j,ll,mm in ch] for i,l,m in ch]
ng=sum(G[i][i] for i,l,m in ch)
qq=sum((1+4*l*(l+1))*T[i][i] for i,l,m in ch)
for i,row in enumerate(S):
    check(q(x['single_centre']['G_lower'])<=row[i]-sum(abs(v) for j,v in enumerate(row) if j!=i),'single centre lower row '+str(i))
    check(q(x['single_centre']['G_upper'])>=row[i]+sum(abs(v) for j,v in enumerate(row) if j!=i),'single centre upper row '+str(i))
check(ng==q(x['single_centre']['norm_trace']),'norm trace')
check(qq==q(x['single_centre']['gradient_trace_upper']),'Hardy angular trace')
v=F(4521571391451241,2251799813685248)
beta=qq/3+v*v*ng/4
check(q(x['motion']['beta_z_derivative_trace'])==beta,'full-multiplet z isotropy')
L=q(x['motion']['cross_z_Lipschitz_upper']);gmax=q(x['single_centre']['G_upper']);gmin=q(x['single_centre']['G_lower'])
check(L*L>=gmax*beta,'Lipschitz root inequality')
sq=F(0);rsq=F(0);msq=F(0)
M=[]
for i,e in enumerate(a['entries']):
    t=[]
    for k in ['re','im']:
        lo=F(int(e[k]['lower_numerator']),2**e[k]['denominator_power2']);hi=F(int(e[k]['upper_numerator']),2**e[k]['denominator_power2'])
        check(lo<=hi,f'anchor endpoint {i} {k}')
        sq+=max(abs(lo),abs(hi))**2;rsq+=((hi-lo)/2)**2;msq+=((hi+lo)/2)**2;t.append((hi+lo)/2)
    M.append(t)
c=q(x['anchor']['C_norm_upper']);eps=q(a['full_cross_radius_upper'])
check(c*c>=sq,'point cross norm squared')
check(eps*eps>=2*rsq,'point radius squared')
eta=q(x['epoch']['phase_error_upper']);delta=q(x['epoch']['delta'])
check(eta==abs(delta)**3/6,'real phase Taylor remainder')
check(q(x['epoch']['q_re'])==1-delta**2/2 and q(x['epoch']['q_im'])==-delta,'phase inverse sign')
Qgrad=2*qq+v*v*ng
Ttime=v*v*beta
check(Qgrad==q(x['motion']['two_centre_gradient_trace_upper']),'complete ETF gradient trace')
check(Ttime==q(x['motion']['projectile_time_derivative_trace_upper']),'complete time trace')
for w in x['windows']:
    h=q(w['halfwidth_a0']);slo=q(w['gram']['lower']);shi=q(w['gram']['upper'])
    check(slo==gmin-c-h*L and slo>0,'uniform Gram lower '+str(h))
    check(shi==gmax+c+h*L,'uniform Gram upper '+str(h))
    check(q(w['gram']['condition_upper'])*slo>=shi,'condition '+str(h))
    H=q(w['operators']['H_operator_upper_Eh']);D=q(w['operators']['D_operator_upper_per_ta'])
    check(H>=Qgrad/2 and (H-Qgrad/2)**2>=16*shi*Qgrad,'Hardy weak H '+str(h))
    check(D*D>=shi*Ttime,'D form '+str(h))
    check(q(w['K_zero_reference_error_operator_upper_Eh'])==H+D,'K triangle '+str(h))
    check(q(w['Sdot_zero_reference_error_operator_upper_per_ta'])==v*L,'Sdot block norm '+str(h))
    check(q(w['S_constant_reference_error_operator_upper'])>=eps+eta*q(x['anchor']['C_mid_full_X_norm_upper'])+h*L,'anchor plus motion tube '+str(h))
check(x['physical_bridge_upper'] is None and x['full_stencil_total_upper']==[None,None],'missing physical gates retained')
check(x['new_cross_integrals']==x['new_radial_integrals']==x['old_calculations_replayed']==0,'zero-integral scope')
# Independent high-precision eigenvalue diagnostic of this new exact anchor
# matrix, not a repeat of a physical scattering or historical eigensolver suite.
mp.mp.dps=70
cv=lambda z:mp.mpf(z.numerator)/z.denominator
A=mp.matrix(18)
for i in range(9):
    for j in range(9):
        A[i,j]=A[9+i,9+j]=cv(S[i][j])
        re,im=M[9*i+j];A[i,9+j]=mp.mpc(cv(re),cv(im));A[9+j,i]=mp.conj(A[i,9+j])
e=mp.eighe(A,eigvals_only=True)
check(e[len(e)-1]>=e[0],'eigenvalue ordering must hold')
check(e[0]>cv(gmin-c),'anchor eigenvalue diagnostic exceeds rigorous lower')
check(e[len(e)-1]<cv(gmax+c),'anchor eigenvalue diagnostic below rigorous upper')
report={'schema':'R4AL_READ_ONLY_REVIEW_V2','status':'PASS','conditions':len(checks),
        'checks':checks,'anchor_eigenvalue_diagnostic':{'digits':70,'min':str(e[0]),'max':str(e[len(e)-1])},
        'certificate_sha256':hashlib.sha256((r/'evidence/run_v1/CERTIFICATE.json').read_bytes()).hexdigest(),
        'new_cross':0,'new_radial':0,'no_import_of_producer':True,
        'limitation':'same-session independent algebra and high-precision diagnostic; no separate human/agent review or formal proof checker'}
(r/'evidence/INDEPENDENT_REVIEW.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='checks'},indent=2))
