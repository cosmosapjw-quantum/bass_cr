"""Nominal full-coupled arbitrary-birth diagnostics; no source certificate."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from scipy.integrate import solve_ivp
from ft03_point import Model,TEND,H,CT,NH0,TAU_SCALE,W0,CE,CHI,temperature,temperature_gradient,nonphoto_jac

RTOL=2e-11; ATOL=2e-14

def integrate(fun,span,y0,**kw):
    sol=solve_ivp(fun,span,y0,method='DOP853',rtol=kw.pop('rtol',RTOL),atol=kw.pop('atol',ATOL),dense_output=True,**kw)
    if not sol.success:raise RuntimeError(sol.message)
    return sol

@dataclass
class Segment:
    left:float
    right:float
    sol:object
    adj:object=None

class Background:
    def __init__(self,plan):
        self.births=np.r_[0.,np.array(plan['same_births'])/TEND]
        self.weights=np.r_[.05,[plan['same_source_weight_boxes'][str(v)]['weight'] for v in plan['same_births']]]
        self.model=Model(self.births)
        self.segments=[]
        self.n=4+len(self.births)
        y=np.r_[.9,.3,.6,1.,np.zeros(len(self.births)),0.]
        y[4]=self.weights[0]
        edges=np.r_[self.births,1.]
        self.nfev=0
        for i,(a,b) in enumerate(zip(edges[:-1],edges[1:])):
            def rhs(u,z):return np.r_[self.model.rhs(u,z[:self.n]),self.model.goal(u,z[:4])]
            sol=integrate(rhs,(a,b),y,rtol=2e-12,atol=2e-14,max_step=1/16)
            self.nfev+=sol.nfev
            self.segments.append(Segment(a,b,sol))
            y=sol.y[:,-1].copy()
            if i+1<len(self.births):y[4+i+1]+=self.weights[i+1]
        self.final=y
    def evaluate(self,u,side='right'):
        if not 0<=u<=1:raise ValueError('PROBE_TIME_DOMAIN')
        i=np.searchsorted(self.births,u,side=side)-1
        i=max(0,min(int(i),len(self.segments)-1))
        return self.segments[i].sol.sol(u)
    def backward(self):
        lam=np.zeros(self.n);self.adj_nfev=0
        for seg in self.segments[::-1]:
            def rhs(u,l):return -self.model.jac(u,seg.sol.sol(u)[:self.n]).T@l-self.model.goal_vector(u,self.n)
            seg.adj=integrate(rhs,(seg.right,seg.left),lam,max_step=1/16)
            self.adj_nfev+=seg.adj.nfev;lam=seg.adj.y[:,-1]
        return lam
    def probe(self,b,memory=True):
        if not 0<=b<=1:raise ValueError('PROBE_TIME_DOMAIN')
        n=self.n; mod=Model([b]);z=np.zeros(n+7);z[n]=1.
        records=[];evals=0
        for seg in self.segments:
            a=max(b,seg.left)
            if a>=seg.right:continue
            def rhs(u,zz):
                state=seg.sol.sol(u)[:n];dg=zz[:4];qp=zz[4:n]
                en,aa,kap,V,gr=self.model.geometry(u,state[:4])
                ep,ap,kp,vp,_=mod.geometry(u,state[:4]);probe_loss=kp[0]*zz[n]
                J=self.model.jac(u,state,memory=memory)
                dx=J@zz[:n];dx[:4]+=vp[:,0]*probe_loss
                old_loss=kap*qp+state[4:]*(gr@dg)
                old_heat=np.dot(en-CHI[0],old_loss)
                red=H*TEND*np.dot(en,qp)
                np_e=CE@nonphoto_jac(u,state[:4])@dg
                return np.r_[dx,-probe_loss,np.exp(-3*H*TEND*u)*(CE@dg),old_loss.sum(),old_heat,red,np_e,(ep[0]-CHI[0])*probe_loss]
            sol=integrate(rhs,(a,seg.right),z,max_step=1/16)
            evals+=sol.nfev;z=sol.y[:,-1]
            records.append({'u':seg.right,'delta_h':float(z[0]),'photon_retention_sum':float(z[4:n].sum())})
        en,*_=self.model.geometry(1.,self.final[:4])
        count_check=CE@z[:4]+z[n]+z[4:n].sum()-1-z[n+5]
        heat_check=z[n+3]+np.dot(en-CHI[0],z[4:n])+z[n+4]
        return dict(b_u=float(b),b_s=float(b*TEND),memory=memory,K_tau=float(TAU_SCALE*z[n+1]),delta_g=z[:4].tolist(),delta_temperature_K=float(temperature_gradient(self.final[:4])@z[:4]),probe_survival=float(z[n]),retained_existing=z[4:n].tolist(),existing_photo_count=float(z[n+2]),existing_photoheat_eV=float(z[n+3]),existing_extra_redshift_eV=float(z[n+4]),nonphoto_charge=float(z[n+5]),probe_photoheat_eV=float(z[n+6]),charge_identity_residual=float(count_check),old_heat_identity_residual=float(heat_check),nfev=evals,records=records)
    def probe_adjoint(self,b):
        if not 0<=b<=1:raise ValueError('PROBE_TIME_DOMAIN')
        if self.segments[0].adj is None:raise RuntimeError('BACKWARD_NOT_RUN')
        mod=Model([b]);z=np.array([1.,0.]);evals=0
        for seg in self.segments:
            a=max(b,seg.left)
            if a>=seg.right:continue
            def rhs(u,q):
                state=seg.sol.sol(u)[:self.n];_,_,kap,v,_=mod.geometry(u,state[:4])
                direct=kap[0]*q[0]
                return np.array([-direct,direct*np.dot(v[:,0],seg.adj.sol(u)[:4])])
            sol=integrate(rhs,(a,seg.right),z,max_step=1/16)
            z=sol.y[:,-1];evals+=sol.nfev
        return {'b_u':float(b),'K_tau':float(TAU_SCALE*z[1]),'nfev':evals}
    def positive_dose(self,b,dose):
        if not 0<=b<1 or dose<=0:raise ValueError('POSITIVE_DOSE_REQUIRED')
        mod=Model(np.r_[self.births,b]);n=self.n+1
        base=self.evaluate(b);state=np.r_[base[:self.n],dose,base[-1]]
        for seg in self.segments:
            a=max(b,seg.left)
            if a>=seg.right:continue
            def rhs(u,z):return np.r_[mod.rhs(u,z[:n]),mod.goal(u,z[:4])]
            sol=integrate(rhs,(a,seg.right),state,rtol=2e-12,atol=2e-14,max_step=1/32)
            state=sol.y[:,-1].copy()
            # The base evaluation at b uses the right trace, so births at b are not readded.
            if seg.right<1:
                j=int(np.searchsorted(self.births,seg.right))
                if j<len(self.births) and self.births[j]==seg.right:state[4+j]+=self.weights[j]
        return {'b_u':b,'dose':dose,'K_tau_forward_difference':float(TAU_SCALE*(state[-1]-self.final[-1])/dose),'delta_temperature_per_dose':float((temperature(state[:4])-temperature(self.final[:4]))/dose)}
