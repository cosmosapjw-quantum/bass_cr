from __future__ import annotations
from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class GridSpec:
    xlim: tuple[float,float]; ylim: tuple[float,float]; zlim: tuple[float,float]; dx: float
    @staticmethod
    def from_dict(d):
        return GridSpec(tuple(map(float,d['xlim'])),tuple(map(float,d['ylim'])),tuple(map(float,d['zlim'])),float(d['dx']))
    def shape(self):
        out=[]
        for lohi in [self.xlim,self.ylim,self.zlim]:
            L=lohi[1]-lohi[0]; n=round(L/self.dx)
            if abs(n*self.dx-L)>1e-9: raise ValueError('box lengths must be integer multiples of dx for cell-centered grid')
            out.append(int(n))
        return tuple(out)
    def axes(self,xp=np):
        axes=[]
        for (lo,hi),n in zip([self.xlim,self.ylim,self.zlim],self.shape()):
            axes.append(xp.asarray(lo+(np.arange(n)+0.5)*self.dx))
        return tuple(axes)
    @property
    def dv(self): return self.dx**3

def k2_grid(spec:GridSpec,xp):
    nx,ny,nz=spec.shape(); dx=spec.dx
    kx=2*xp.pi*xp.fft.fftfreq(nx,d=dx); ky=2*xp.pi*xp.fft.fftfreq(ny,d=dx); kz=2*xp.pi*xp.fft.fftfreq(nz,d=dx)
    return kx[:,None,None]**2+ky[None,:,None]**2+kz[None,None,:]**2

def absorber_mask(spec:GridSpec,xp,width=4.0,power=0.125):
    if width<=0: return xp.ones(spec.shape(),dtype=float)
    axes=spec.axes(xp); masks=[]
    for a,(lo,hi) in zip(axes,[spec.xlim,spec.ylim,spec.zlim]):
        d=xp.minimum(a-lo,hi-a)
        u=xp.clip(d/width,0,1)
        m=xp.where(u<1,xp.sin(0.5*xp.pi*u)**power,1.0)
        masks.append(m)
    return masks[0][:,None,None]*masks[1][None,:,None]*masks[2][None,None,:]
