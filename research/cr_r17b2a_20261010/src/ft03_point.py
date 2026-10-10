"""Fast complex-analytic transcription of pinned FT03 instantaneous equations.

Point/Jacobian numerical backend, NOT interval certification. Source literals
and pre-evaluated binary64 constants agree with selected donor cell_model.py.
Time u=t/TEND, gas thermal coordinate w/W0, photons are counts/H, not /P0.
"""
from __future__ import annotations
import struct
import numpy as np
from response import blocks
TEND=1250000000.0
H=1e-14; NH0=1e-4; FHE=.083; C=29979245800.
KB=1.380649e-16; EV=1.602176634e-12
CHI=np.array([13.598434599702,24.587389011,54.41776])
W0=13.620772387478219
DRA=struct.unpack('<d',struct.pack('<Q',0x3f5f8b1ba9b90acb))[0]
DRB=np.array([struct.unpack('<d',struct.pack('<Q',n))[0] for n in (0x411caf2e364afdee,0x412135e886f9cb6f)])
CT=299792458.*6.6524587e-29*1e6
TAU_SCALE=CT*NH0*TEND
CE=np.array([1.,FHE,2*FHE,0.])

def sigma(E):
    E=np.asarray(E)
    if np.any(E.real<13.6) or np.any(E.real>=24.59):
        raise ValueError('PINNED_SMOOTH_HI_ONLY_SUPPORT_REQUIRED')
    x=E/.4298
    return 5.475e4*(x-1)**2*x**(2.963/2-5.5)*(1+np.sqrt(x/32.88))**(-2.963)*1e-18

def temperature(g):
    D=1+FHE+g[0]+FHE*(g[1]+2*g[2])
    return 2*g[3]*W0*EV/(3*KB*D)

def temperature_gradient(g):
    D=1+FHE+CE@g
    # CE[3]=0; derivative in normalized w coordinate.
    t=temperature(g)
    out=-t/D*CE.copy()
    out[3]=t/g[3]
    return out

def nonphoto(u,g):
    x,y,z,w=g[0],g[1],g[2],g[3]*W0
    temp=temperature(g)
    if not 30000 < temp.real < 110000:
        raise ValueError('FT03_TEMPERATURE_DOMAIN')
    nh=NH0*np.exp(-3*H*TEND*u)
    xe=x+FHE*(y+2*z)
    l=np.array([315614.,570670.,1263030.])/temp
    t=(l/.522)**.470
    rr=(np.array([1.,1.,2.])*1.269e-13*l**1.503/(1+t)**1.923)
    slopes=-1.503+1.923*.470*t/(1+t)
    rr[1]=3e-14*l[1]**.654;slopes[1]=-.654
    ci=(np.array([21.11,32.38,19.95])*temp**-1.5*np.exp(-l/2)*l**np.array([-1.089,-1.146,-1.089])
        /(1+(l/np.array([.354,.416,.553]))**np.array([.874,.987,.735]))**np.array([1.101,1.056,1.275]))
    lows=np.array([1-x,FHE*(1-y-z),FHE*y]);highs=np.array([x,FHE*y,FHE*z])
    ci=nh*xe*lows*ci; rr=nh*xe*highs*rr
    dr=nh*xe*FHE*y*np.array([1.,.3])*DRA*temp**-1.5*np.exp(-DRB/temp)
    net=ci-rr;net[1]-=dr.sum()
    kin=np.sum(rr*KB*temp*(1.5+slopes)/EV)
    fw=-np.sum(ci*CHI)-kin-np.sum(dr*KB*DRB/EV)-2*H*w
    return TEND*np.array([net[0],(net[1]-net[2])/FHE,net[2]/FHE,fw/W0])

def nonphoto_jac(u,g):
    z=np.asarray(g,dtype=complex)
    out=np.empty((4,4))
    for j in range(4):
        x=z.copy();x[j]+=1j*1e-30
        out[:,j]=np.imag(nonphoto(u,x))/1e-30
    return out

class Model:
    def __init__(self,births, energies=None):
        self.births=np.asarray(births,dtype=float)
        self.energies=np.full(len(births),13.7) if energies is None else np.asarray(energies,dtype=float)
        if self.births.ndim!=1 or len(self.energies)!=len(self.births):raise ValueError('COHORT_IDENTITY')
    def geometry(self,u,g):
        en=self.energies*np.exp(-H*TEND*(u-self.births))
        a=TEND*C*NH0*np.exp(-3*H*TEND*u)*sigma(en)
        kap=a*(1-g[0])
        V=np.zeros((4,len(a)));V[0]=1;V[3]=(en-CHI[0])/W0
        grad=np.zeros((len(a),4));grad[:,0]=-a
        return en,a,kap,V,grad
    def rhs(self,u,y):
        g=y[:4];p=y[4:]
        en,a,kap,V,grad=self.geometry(u,g)
        r=kap*p
        return np.r_[nonphoto(u,g)+V@r,-r]
    def jac(self,u,y, memory=True):
        en,a,kap,V,grad=self.geometry(u,y[:4])
        J=blocks(nonphoto_jac(u,y[:4]),y[4:],kap,grad,V)
        if not memory: J[4:,:4]=0
        return J
    @staticmethod
    def goal(u,g):return np.exp(-3*H*TEND*u)*(CE@g)
    @staticmethod
    def goal_vector(u,n):return np.r_[np.exp(-3*H*TEND*u)*CE,np.zeros(n-4)]
