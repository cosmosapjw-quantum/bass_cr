"""Source-derived selected ground channels, finite thermal integrals and total RR."""
import math,re
from decimal import Decimal,localcontext
import numpy as np
from numpy.polynomial.legendre import leggauss

EV=1.602176634e-19; KB=1.380649e-23; H=6.62607015e-34; C_LIGHT=299792458.; ME=9.1093837139e-31
C=8*math.pi/(H**3*C_LIGHT**2)
GL={n:leggauss(n) for n in (64,128)}

class Provider:
    def __init__(self,paths,channels):
        body='\n'.join(x[6:] for x in paths['phfit2'].read_text().splitlines() if x and x[0] not in '*cC')
        rrbody='\n'.join(x[6:] for x in paths['rrfit'].read_text().splitlines() if x and x[0] not in '*cC')
        def data(text,pattern):
            m=re.search(pattern+r'\s*/([^/]+)/',text,re.I)
            if not m:raise ValueError('missing provider row '+pattern)
            return [float(v) for v in m[1].replace('\n','').split(',')]
        self.rows={}
        photo=[list(map(float,x.split())) for x in paths['photo_table'].read_text().splitlines()]
        partial=[list(map(float,x.split())) for x in paths['partial_table'].read_text().splitlines()]
        rrtable=[]
        for line in paths['rr_table'].read_text().splitlines():
            rrtable.append({'label':line[:8].strip(),'Z':int(line[9:11]),'N':int(line[12:14]),'parameters':list(map(float,line[16:].split()))})
        for ch in channels:
            z,n,s=ch['Z'],ch['N'],ch['shell'];name=ch['ion']
            p1=data(body,rf'DATA\s*\(PH1\(I,\s*{z},\s*{n},\s*{s}\),I=1,6\)')
            p2=data(body,rf'DATA\s*\(PH2\(I,\s*{z},\s*{n}\),I=1,7\)')
            rr=data(rrbody,rf'data\(rnew\(i,\s*{z},\s*{n}\),i=1,4\)')
            old=next(r for r in photo if r[:2]==[z,n]);pt=next(r for r in partial if r[:4]==[z,n,s,0])
            assert old[4:]==p2 and pt[4:]==p1 and p1[0]==ch['chi_eV']
            matches=[r for r in rrtable if r['Z']==z and r['N']==n and r['parameters']==rr]
            assert len(matches)==1
            self.rows[name]=dict(ch,PH1=p1,PH2=p2,RR=rr,RR_table_label=matches[0]['label'])
        self.core=data(body,r'DATA\s*\(PH1\(I,\s*3,\s*3,\s*1\),I=1,6\)')
    def sigma(self,name,e,core=False):
        row=self.rows[name];e=np.asarray(e);chi=64.39 if core else row['chi_eV']
        p1=self.core if core else row['PH1'];e0,s0,ya,p,yw,y0,y1=row['PH2']
        x=e/e0-y0;v=np.sqrt(x*x+y1*y1)
        low=s0*((x-1)**2+yw*yw)*v**(p/2-5.5)*(1+np.sqrt(v/ya))**(-p)
        if name=='LiI':
            _,e0,s0,ya,p,yw=p1;t=e/e0
            high=s0*((t-1)**2+yw*yw)*t**(p/2-5.5)*(1+np.sqrt(t/ya))**(-p)
            value=high if core else np.where(e>=64.39,high,low)
        else:value=low
        return np.where(e>=chi,value,0.)
    def sigma_decimal(self,name,e):
        row=self.rows[name]
        with localcontext() as ctx:
            ctx.prec=50;d=lambda v:Decimal(str(v));en=d(e)
            if name=='LiI' and e>=64.39:
                _,e0,s0,ya,p,yw=map(d,row['PH1']);t=en/e0;pol=(t-1)**2+yw*yw
            else:
                e0,s0,ya,p,yw,y0,y1=map(d,row['PH2']);x=en/e0-y0;t=(x*x+y1*y1).sqrt();pol=(x-1)**2+yw*yw
            return float((s0.ln()+pol.ln()+(p/2-d(5.5))*t.ln()-p*(1+(t/ya).sqrt()).ln()).exp())
    def rr(self,name,t):
        a,b,t0,t1=self.rows[name]['RR'];tt=np.sqrt(np.asarray(t)/t0)
        return a/(tt*(1+tt)**(1-b)*(1+np.sqrt(np.asarray(t)/t1))**(1+b))
    def rr_decimal(self,name,t):
        with localcontext() as c:
            c.prec=50;d=lambda v:Decimal(str(v));a,b,t0,t1=map(d,self.rows[name]['RR']);t=d(t);x=(t/t0).sqrt()
            return float(a/(x*((1-b)*(1+x).ln()).exp()*((1+b)*(1+(t/t1).sqrt()).ln()).exp()))
    def intervals(self,name,T,core=False):
        edges=[0.,1.,4.,16.,40.,60.,80.]
        if name=='LiI' and not core:
            edge=(64.39-self.rows[name]['chi_eV'])*EV/(KB*T)
            if 0<edge<80:edges.append(edge)
        return sorted(edges)
    def scaled(self,name,T,Tg,n,core=False):
        chi=(64.39 if core else self.rows[name]['chi_eV'])*EV;kt=KB*T;x0=chi/kt
        nodes,weights=GL[n];a=[];tail=[]
        for lo,hi in zip(self.intervals(name,T,core)[:-1],self.intervals(name,T,core)[1:]):
            t=(lo+hi)/2+(hi-lo)/2*nodes;weight=(hi-lo)/2*weights
            e=(chi+kt*t)/EV;sigma=self.sigma(name,e,core)*1e-22
            base=sigma*(x0+t)**2*np.exp(-t)
            stim=1. if Tg==0 else 1/(-np.expm1(-(chi+kt*t)/(KB*Tg)))
            # All products remain scaled: no exp(+chi/kT) or underflow rate floor.
            vals=np.array([np.sum(weight*base),np.sum(weight*base*stim),np.sum(weight*base*stim*(x0+t)),np.sum(weight*base*stim*t)])
            a.append(vals)
            if hi>60:tail.append(vals)
        return np.sum(a,axis=0),np.sum(tail,axis=0) if tail else np.zeros(4)
    def rate(self,name,Te,Tg=None,n=128,core=False):
        if Tg is None:Tg=Te
        row=self.rows[name];chi=(64.39 if core else row['chi_eV'])*EV;D=row['saha_d']*(2*math.pi*ME*KB*Te/H**2)**1.5
        electron,etail=self.scaled(name,Te,Tg,n,core)
        if Tg>0:
            photon,ptail=(electron,etail) if Tg==Te else self.scaled(name,Tg,Tg,n,core)
            x0=chi/(KB*Tg);logbeta=math.log(C)+3*math.log(KB*Tg)-x0+math.log(photon[1])
            beta=math.exp(logbeta);W=math.exp(logbeta+math.log(KB*Tg)+math.log(photon[2]/photon[1]));K=math.exp(logbeta+math.log(KB*Tg)+math.log(photon[3]/photon[1]))
        else:photon=np.zeros(4);ptail=np.zeros(4);logbeta=None;beta=W=K=0.
        asp=None if core else C*(KB*Te)**3/D*electron[0]*1e6;ast=None if core else C*(KB*Te)**3/D*electron[1]*1e6
        return {'ion':name,'Te_K':Te,'Tgamma_K':Tg,'nodes':n,'beta_s_inverse':beta,'log_beta_s_inverse':logbeta,'beta_underflow':beta==0 and Tg>0,
            'W_abs_J_s':W,'K_primary_J_s':K,'Q_threshold_J_s':chi*beta,'alpha_g_sp_cm3_s':asp,'alpha_g_stim_cm3_s':ast,'alpha_total_RR_cm3_s':None if core else float(self.rr(name,Te)),
            'log_Saha_cm3_inverse':None if core else math.log(D)-chi/(KB*Te)-math.log(1e6),'Saha_cm3_inverse':None if core else math.exp(math.log(D)-chi/(KB*Te)-math.log(1e6)),'total_RR_over_ground_sp':None if core else float(self.rr(name,Te))/asp,'stimulated_enhancement':None if core else ast/asp,
            'scaled_electron':electron.tolist(),'scaled_photon':photon.tolist(),'scaled_electron_tail':etail.tolist(),'scaled_photon_tail':ptail.tolist(),
            'max_sampled_eV':(chi+80*KB*max(Te,Tg))/EV}
