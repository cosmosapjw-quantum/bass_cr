"""Read-only R4AC review, using local-s recurrences and direct spherical sums.

The review never calls the production interval integrator or native quadrature.
High precision is an independent numerical check, not the certificate itself.
"""
from __future__ import annotations
import argparse,json,math,time
from fractions import Fraction as F
from pathlib import Path
import numpy as np
import mpmath as mp
from runtime_contract import sha,digest,verify_pins,write_json

DPS=120

def mf(q):
    q=F(q);return mp.mpf(q.numerator)/q.denominator

def local_radial(edges,endpoints,bubbles,delta):
    e=[mp.mpf(float(x)) for x in edges];p=[[mp.mpf(float(x)) for x in row] for row in endpoints]
    q=[[[mp.mpf(float(x)) for x in b] for b in row] for row in bubbles]
    R=mp.sqrt(sum(mp.mpf(float(x))**2 for x in delta));nm=len(p)
    out=[[[mp.mpf(0) for _ in range(nm)] for _ in range(nm)] for _ in range(3)]
    for panel in range(len(e)-1):
        a=e[panel];h=e[panel+1]-a;cut=max(mp.mpf(0),min(mp.mpf(1),(R-a)/h))
        polys=[]
        for i in range(nm):
            q0,q1,q2=q[i][panel];left,right=p[i][panel],p[i][panel+1]
            polys.append([left,right-left+q0,q1-q0,q2-q1,-q2])
        products={(i,j):[sum((polys[i][k]*polys[j][n-k] for k in range(5) if 0<=n-k<5),mp.mpf(0)) for n in range(9)] for i in range(nm) for j in range(nm)}
        for lo,hi,inner in ((mp.mpf(0),cut,True),(cut,mp.mpf(1),False)):
            if hi<=lo:continue
            if inner:
                moments={n:(hi**(n+1)-lo**(n+1))/(n+1) for n in range(11)}
                weights=[[sum((math.comb(ell,k)*a**(ell-k)*h**k*moments[n+k] for k in range(ell+1)),mp.mpf(0))*h/R**(ell+1) for n in range(9)] for ell in range(3)]
            else:
                rl,rh=a+h*lo,a+h*hi
                inv={1:[mp.log(rh/rl)/h],2:[(1/rl-1/rh)/h],3:[(1/rl**2-1/rh**2)/(2*h)]}
                for n in range(1,9):
                    inv[1].append(((hi**n-lo**n)/n-a*inv[1][n-1])/h)
                    inv[2].append((inv[1][n-1]-a*inv[2][n-1])/h)
                    inv[3].append((inv[2][n-1]-a*inv[3][n-1])/h)
                weights=[[h*R**ell*inv[ell+1][n] for n in range(9)] for ell in range(3)]
            for ell in range(3):
                for (i,j),coef in products.items():out[ell][i][j]+=sum((coef[n]*weights[ell][n] for n in range(9)),mp.mpf(0))
    return out

def direct_angular(delta):
    # The phi sum removes nonzero Fourier modes through order4; after that
    # the polar integrand is a polynomial of degree<=4, so GL5 is exact in R.
    # Here the rule is evaluated at high precision rather than symbolically.
    R=mp.sqrt(sum(mp.mpf(float(x))**2 for x in delta));d=[mp.mpf(float(x))/R for x in delta]
    nodes,weights=mp.gauss_quadrature(5,'legendre')
    out=[[[mp.mpc(0) for _ in range(4)] for _ in range(4)] for _ in range(3)]
    for k in range(5):
        ct=nodes[k];st=mp.sqrt(1-ct**2)
        for j in range(12):
            phi=2*mp.pi*j/12
            Y=[1/mp.sqrt(4*mp.pi),mp.sqrt(3/(8*mp.pi))*st*mp.exp(-1j*phi),mp.sqrt(3/(4*mp.pi))*ct,-mp.sqrt(3/(8*mp.pi))*st*mp.exp(1j*phi)]
            x=d[0]*st*mp.cos(phi)+d[1]*st*mp.sin(phi)+d[2]*ct
            P=(mp.mpf(1),x,(3*x*x-1)/2);w=weights[k]*2*mp.pi/12
            for ell in range(3):
                for a in range(4):
                    for b in range(4):out[ell][a][b]+=w*mp.conj(Y[a])*Y[b]*P[ell]
    return out

def _inside(value,pair):return mf(F(pair[0]))<=value<=mf(F(pair[1]))

def review(root,stage,output):
    root,stage,output=Path(root),Path(stage),Path(output)
    if output.exists():raise FileExistsError('review output already exists')
    started=time.monotonic();result=json.loads((stage/'RESULT.json').read_text());done=json.loads((stage/'COMPLETED.json').read_text())
    checks=0
    def check(ok,label):
        nonlocal checks
        checks+=1
        if not ok:raise AssertionError(label)
    check(done['result_sha256']==sha(stage/'RESULT.json'),'result identity')
    context=json.loads((root/'contracts/CONTEXT.json').read_text());verify_pins(root,context['source_pins']);checks+=len(context['source_pins'])
    pins=json.loads((root/'contracts/INPUT_PINS.json').read_text());verify_pins(root,pins);checks+=len(pins)
    entries=sorted((stage/'potentials').iterdir(),key=lambda x:json.loads((x/'CERTIFICATE.json').read_text())['geometry']['actual_z_a0'])
    chosen=[entries[0],next(x for x in entries if json.loads((x/'CERTIFICATE.json').read_text())['geometry']['requested_z_a0']==-32.),entries[-1]]
    with np.load(root/'inputs/CANDIDATE.npz',allow_pickle=False) as z:e,p,q=z['edges'],z['shared_endpoint_values'],z['bubble_coefficients']
    meta=json.loads((root/'inputs/CANDIDATE.json').read_text());lm=[(m['l'],v) for m in meta['modes'] for v in range(-m['l'],m['l']+1)];ix=[i for i,m in enumerate(meta['modes']) for _ in range(2*m['l']+1)]
    amap={(0,0):0,(1,-1):1,(1,0):2,(1,1):3}
    numerics=[];radial_count=0;matrix_count=0;max_imag=mp.mpf(0)
    with mp.workdps(DPS):
        for path in chosen:
            cert=json.loads((path/'CERTIFICATE.json').read_text());delta=np.diff(np.array(cert['geometry']['actual_centers_a0']),axis=0)[0]
            rad=local_radial(e,p,q,delta)
            for ell in range(3):
                for i in range(5):
                    for j in range(5):
                        check(_inside(rad[ell][i][j],cert['radial'][ell][i][j]),'independent radial containment '+path.name);radial_count+=1
            row={'geometry':path.name,'radial_values':75,'matrix_values':162}
            for c,lab in enumerate(('T','P')):
                angular=direct_angular(delta if c==0 else -delta)
                for a,la in enumerate(lm):
                    for b,lb in enumerate(lm):
                        v=-sum((rad[L][ix[a]][ix[b]]*angular[L][amap[la]][amap[lb]] for L in range(3)),mp.mpc(0))
                        check(_inside(mp.re(v),cert['potentials_real'][lab][a][b]),'independent V containment '+path.name);matrix_count+=1
                        check(abs(mp.im(v))<mp.mpf('1e-110'),'plane imaginary cancellation')
                        max_imag=max(max_imag,abs(mp.im(v)))
            numerics.append(row)
        # Recompute all reported error budgets with exact Fraction arithmetic,
        # using squared inequalities instead of producer sqrt/error helpers.
        for path in entries:
            cert=json.loads((path/'CERTIFICATE.json').read_text());comp=json.loads((path/'COMPLETED.json').read_text())
            check(comp['certificate_sha256']==sha(path/'CERTIFICATE.json'),'certificate digest')
            check(comp['potential_npz_sha256']==sha(path/'POTENTIALS.npz'),'potential digest')
            with np.load(path/'POTENTIALS.npz',allow_pickle=False) as z:
                for lab in ('T','P'):
                    vals=z[lab+'__V32'];bounds=cert['checks'][lab];maxq=F(0);sumq=F(0)
                    for i in range(9):
                        for j in range(9):
                            lo,hi=map(F,cert['potentials_real'][lab][i][j]);re,im=F(float(vals[i,j].real)),F(float(vals[i,j].imag))
                            qerr=max(abs(re-lo),abs(re-hi))**2+im*im
                            maxq=max(maxq,qerr);sumq+=qerr
                            check(lo<=hi,'ordered certificate endpoints')
                    check(F(bounds['component_upper_exact'])**2>=maxq,'component squared upper budget')
                    check(F(bounds['frobenius_upper_exact'])**2>=sumq,'Frobenius squared upper budget')
                    check(F(bounds['component_upper_Eh'])>=F(bounds['component_upper_exact']),'upward displayed component')
                    check(F(bounds['frobenius_upper_Eh'])>=F(bounds['frobenius_upper_exact']),'upward displayed norm')
        for d in sorted((stage/'reassembled').iterdir()):
            rec=json.loads((d/'RESULT.json').read_text());parent=root/'inputs/records'/d.name
            check(rec['new_full_sha256']==sha(d/'FULL.npz'),'new full digest');check(rec['parent_full_sha256']==sha(parent/'FULL.npz'),'parent full digest')
            with np.load(d/'FULL.npz',allow_pickle=False) as z,np.load(parent/'FULL.npz',allow_pickle=False) as old:
                for k in old.files:
                    if k not in ('H','T__H','P__H','T__V_other','P__V_other'):check(np.array_equal(old[k],z[k]),'immutable array '+k)
                for k in ('S','H','D'):
                    check(np.array_equal(old[k][:9,9:],z[k][:9,9:]),'cross tp unchanged');check(np.array_equal(old[k][9:,:9],z[k][9:,:9]),'cross pt unchanged')
    check(result['counts']=={'primary_GL32':11,'refinement_GL48':11,'certified_geometry':11,'raw_cross':0,'old_Vother_reruns':0},'bounded counter totals')
    data={'schema':'BASS_R4AC_INDEPENDENT_REVIEW_V1','status':'INDEPENDENT_RECURRENCE_ANGULAR_AND_BUDGET_CHECKS_PASS','checks':checks,'result_sha256':sha(stage/'RESULT.json'),'review_source_sha256':sha(__file__),'review_arithmetic':'120-digit local-s inverse-moment recurrence, independent 5x12 direct spherical rule, exact Fraction bound arithmetic','radial_values_inside_certificates':radial_count,'potential_values_inside_certificates':matrix_count,'selected_geometries':numerics,'max_angular_imaginary_residual':mp.nstr(max_imag,12),'all11_geometry_budget_checks':True,'unchanged_parent_tests_rerun':0,'new_cross_calls':0,'new_native_potential_calls':0,'independent_human_or_agent':False,'high_precision_check_is_not_the_certificate':True,'elapsed_seconds':time.monotonic()-started}
    write_json(output,data);print(json.dumps(data,indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    for k in ('root','stage','output'):ap.add_argument('--'+k,required=True)
    a=ap.parse_args();review(a.root,a.stage,a.output)
