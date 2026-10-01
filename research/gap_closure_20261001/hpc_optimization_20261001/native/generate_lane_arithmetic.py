"""Expand the reference complex expression tree into ordered real scalar steps.

Only the marked declarations and lane bodies in moment_kernel_real.f90 change.
Each emitted complex operation is the explicit two-double C++ operation; this
avoids GNU Fortran's scatter lowering of SIMD-private derived-type temporaries.
No algebraic reassociation or common-factor extraction is performed.
"""
from pathlib import Path
import argparse

class Emitter:
    def __init__(self): self.lines=[]; self.count=0
    def step(self,r,i):
        self.count+=1; name=f'w{self.count:03d}'
        self.lines.extend((f'        {name}r={r}',f'        {name}i={i}'))
        return C(self,name+'r',name+'i')

class C:
    def __init__(self,e,r,i):self.e=e;self.r=r;self.i=i
    def __add__(self,b):return self.e.step(f'{self.r}+{b.r}',f'{self.i}+{b.i}')
    def __sub__(self,b):return self.e.step(f'{self.r}-{b.r}',f'{self.i}-{b.i}')
    def __mul__(self,b):
        if isinstance(b,C):return self.e.step(f'{self.r}*{b.r}-{self.i}*{b.i}',f'{self.r}*{b.i}+{self.i}*{b.r}')
        return self.e.step(f'{self.r}*({b})',f'{self.i}*({b})')
    def left(self,a):return self.e.step(f'({a})*{self.r}',f'({a})*{self.i}')

def lane(moving):
    e=Emitter();m=[C(e,f'm({k})%r',f'm({k})%i') for k in range(1,7)]
    imag=C(e,'0.0_c_double','1.0_c_double');pw=C(e,'pw%r','pw%i')
    def bil(t,p):
        return (((m[0]*f'{t}0')*f'{p}0'+m[1]*f'{t}0*{p}1+{t}1*{p}0')+(m[2]*f'{t}1')*f'{p}1')+(m[3]*f'{t}2')*f'{p}2'
    elt=m[0]*'lt0'+m[1]*'lt1';elp=m[0]*'lp0'+m[1]*'lp1'
    f=bil('lt','lp');sv=f.left('at*ap')
    kin=((m[0].left('(at*ap)*qd(l)')+bil('txp','lp').left('at*bp'))+bil('lt','pxt').left('bt*ap'))+f.left('(bt*bp)*xx')
    e.lines.extend(('        b0=lt0*lp0; bc=lt0*lp1+lt1*lp0; bs=lt0*lp2+lt2*lp0',
                    '        bcc=lt1*lp1; bss=lt2*lp2; bcs=lt1*lp2+lt2*lp1'))
    mc=((m[1]*'b0'+m[2]*'bc')+m[4]*'bcc')+m[5]*'bss'
    ms=m[3]*'bs'+m[5]*'bcs'
    def tri(v):return (f.left(v+'(1)')+mc.left(v+'(2)'))+ms.left(v+'(3)')
    hb=kin+(imag*'ap')*(elp.left('at*tr(l,5)')+tri('vpxt').left('bt'))
    if moving:hb=(hb-(imag*'at')*(elt.left('ap*pr(l,6)')+tri('vtxp').left('bp')))+sv.left('vtp')
    dt=(elt.left('(-at*ap)*pr(l,5)')-tri('vpxp').left('at*bp'))-(imag.left('0.5_c_double')*'vp2')*sv
    dc=C(e,'0.0_c_double','0.0_c_double')
    if moving:dc=(elp.left('(-at*ap)*tr(l,6)')-tri('vtxt').left('ap*bt'))+(imag.left('0.5_c_double')*'vt2')*sv
    vals=[sv,hb.left('0.5_c_double')+sv.left('V'),dt,dc]
    for k,val in enumerate(vals,1):
        add=pw*val
        e.lines.extend((f'        acc_r(l,{k})=acc_r(l,{k})+{add.r}',f'        acc_i(l,{k})=acc_i(l,{k})+{add.i}'))
    return e

INPUTS='''        i=ti(l); j=pj(l)
        lt0=tr(l,1)+a*tr(l,2); lt1=rho*tr(l,3); lt2=rho*tr(l,4)
        txp0=apx*tr(l,2); txp1=rho*tr(l,3); txp2=rho*tr(l,4)
        lp0=pr(l,1)+apx*pr(l,2); lp1=rho*pr(l,3); lp2=rho*pr(l,4)
        pxt0=a*pr(l,2); pxt1=rho*pr(l,3); pxt2=rho*pr(l,4)
        ri=2*((u-1)*nt+i)-1; rj=2*((u-1)*np+j)-1
        at=radt(ri); bt=radt(ri+1); ap=radp(rj); bp=radp(rj+1)'''

def blocks():
    static=lane(False);moving=lane(True)
    names=[f'w{k:03d}{part}' for k in range(1,max(static.count,moving.count)+1) for part in ('r','i')]
    declarations='\n'.join('    real(c_double) :: '+','.join(names[k:k+10]) for k in range(0,len(names),10))
    private=['i','j','ri','rj','at','bt','ap','bp','b0','bc','bs','bcc','bss','bcs']
    private += [f'{a}{k}' for a in ('lt','txp','lp','pxt') for k in range(3)]
    private+=names
    omp=['      !$omp simd &']+['      !$omp private('+','.join(private[k:k+10])+') &' for k in range(0,len(private),10)]
    omp[-1]=omp[-1][:-2]
    def loop(e):return '\n'.join(omp)+'\n      do l=1,size\n'+INPUTS+'\n'+'\n'.join(e.lines)+'\n      end do\n      !$omp end simd'
    body='      if (target_static) then\n'+loop(static)+'\n      else\n'+loop(moving)+'\n      end if'
    return declarations,body

def replace_marked(text,tag,content):
    start='! BEGIN GENERATED '+tag;end='! END GENERATED '+tag
    a=text.index(start)+len(start);b=text.index(end,a)
    return text[:a]+'\n'+content+'\n    '+text[b:]

def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args()
    target=Path(__file__).with_name('moment_kernel_real.f90');old=target.read_text();decl,body=blocks()
    new=replace_marked(replace_marked(old,'DECLARATIONS',decl),'ARITHMETIC',body)
    if args.check:
        if new!=old:raise SystemExit('Generated source is stale')
    else:target.write_text(new)
if __name__=='__main__':main()
