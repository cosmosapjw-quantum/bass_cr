// Exact s+p angular contraction. Interleaved doubles at C ABI boundary.
// No phi samples, fast-math, matrix projection, or global mutable state.
#include <cmath>
#include <cstddef>
struct C {
 double r,i;
 C(double re=0.,double im=0.):r(re),i(im){}
 double real()const{return r;} double imag()const{return i;}
};
static C operator+(C a,C b){return {a.r+b.r,a.i+b.i};}
static C operator-(C a,C b){return {a.r-b.r,a.i-b.i};}
static C operator*(C a,C b){return {a.r*b.r-a.i*b.i,a.r*b.i+a.i*b.r};}
static C operator*(double a,C b){return {a*b.r,a*b.i};}
static C operator*(C a,double b){return {a.r*b,a.i*b};}
static C conjugate(C a){return {a.r,-a.i};}
static C rd(const double* p,std::size_t i){return C(p[2*i],p[2*i+1]);}
static C bil(const C* t,const C* p,const C* m){
 return m[0]*t[0]*p[0]+m[1]*(t[0]*p[1]+t[1]*p[0])+m[2]*t[1]*p[1]+m[3]*t[2]*p[2];
}
static C tri(const C* t,const C* p,const double* v,const C* m,C f){
 const C b0=t[0]*p[0],bc=t[0]*p[1]+t[1]*p[0],bs=t[0]*p[2]+t[2]*p[0];
 const C bcc=t[1]*p[1],bss=t[2]*p[2],bcs=t[1]*p[2]+t[2]*p[1];
 return v[0]*f+v[1]*(m[1]*b0+m[2]*bc+m[4]*bcc+m[5]*bss)+v[2]*(m[3]*bs+m[5]*bcs);
}
extern "C" int bass_moment_accumulate_v1(std::size_t n,std::size_t nt,std::size_t np,
 const double* geo,const double* radt,const double* radp,const double* qt,const double* qp,
 const double* vel,const double* weights,const double* phase,double R,double Zt,double Zp,double* output) noexcept {
 if(!n||!nt||!np||!geo||!radt||!radp||!qt||!qp||!vel||!weights||!phase||!output)return 1;
 const C I(0.,1.);const std::size_t block=nt*np;
 const double vt2=vel[0]*vel[0]+vel[1]*vel[1]+vel[2]*vel[2];
 const double vp2=vel[3]*vel[3]+vel[4]*vel[4]+vel[5]*vel[5];
 const double vtp=vel[0]*vel[3]+vel[1]*vel[4]+vel[2]*vel[5];
 const bool target_static=(vel[0]==0. && vel[1]==0. && vel[2]==0.);
 for(std::size_t u=0;u<n;++u){
  const double r0=geo[4*u],r1=geo[4*u+1],a=geo[4*u+2],rho=geo[4*u+3];
  const double apx=a-R,xx=(r0*r0+r1*r1-R*R)/2,V=-Zt/r0-Zp/r1;
  const C pw=rd(phase,u);C m[6];for(int k=0;k<6;++k)m[k]=rd(weights,6*u+k);
  const double vpxt[]={vel[3]*a,vel[4]*rho,vel[5]*rho},vpxp[]={vel[3]*apx,vel[4]*rho,vel[5]*rho};
  const double vtxt[]={vel[0]*a,vel[1]*rho,vel[2]*rho},vtxp[]={vel[0]*apx,vel[1]*rho,vel[2]*rho};
  for(std::size_t i=0;i<nt;++i){
   C tq[4];for(int k=0;k<4;++k)tq[k]=conjugate(rd(qt,4*i+k));
   const C lt[]={tq[0]+a*tq[1],rho*tq[2],rho*tq[3]};
   const C txp[]={apx*tq[1],rho*tq[2],rho*tq[3]};
   const double at=radt[2*(u*nt+i)],bt=radt[2*(u*nt+i)+1];
   const C vptq=vel[3]*tq[1]+vel[4]*tq[2]+vel[5]*tq[3];
   const C vttq=vel[0]*tq[1]+vel[1]*tq[2]+vel[2]*tq[3];
   const C elt=m[0]*lt[0]+m[1]*lt[1];
   for(std::size_t j=0;j<np;++j){
    C pq[4];for(int k=0;k<4;++k)pq[k]=rd(qp,4*j+k);
    const C lp[]={pq[0]+apx*pq[1],rho*pq[2],rho*pq[3]};
    const C pxt[]={a*pq[1],rho*pq[2],rho*pq[3]};
    const double ap=radp[2*(u*np+j)],bp=radp[2*(u*np+j)+1];
    const C qdot=tq[1]*pq[1]+tq[2]*pq[2]+tq[3]*pq[3];
    const C vppq=vel[3]*pq[1]+vel[4]*pq[2]+vel[5]*pq[3];
    const C vtpq=vel[0]*pq[1]+vel[1]*pq[2]+vel[2]*pq[3];
    const C elp=m[0]*lp[0]+m[1]*lp[1],f=bil(lt,lp,m),sv=at*ap*f;
    const C kin=at*ap*qdot*m[0]+at*bp*bil(txp,lp,m)+bt*ap*bil(lt,pxt,m)+bt*bp*xx*f;
    C hb=kin+I*ap*(at*vptq*elp+bt*tri(lt,lp,vpxt,m,f));
    if(!target_static) hb=hb-I*at*(ap*vtpq*elt+bp*tri(lt,lp,vtxp,m,f))+vtp*sv;
    const C dTP=-at*ap*vppq*elt-at*bp*tri(lt,lp,vpxp,m,f)-.5*I*vp2*sv;
    const C dPTconj=target_static?C{}:(-at*ap*vttq*elp-ap*bt*tri(lt,lp,vtxt,m,f)+.5*I*vt2*sv);
    const C vals[]={sv,.5*hb+V*sv,dTP,dPTconj};
    for(int k=0;k<4;++k){auto pos=k*block+i*np+j;C add=pw*vals[k];output[2*pos]+=add.real();output[2*pos+1]+=add.imag();}
   }
  }
 }
 return 0;
}

// Cartesian s+p specialization: angular coefficients are real.
static C bil_real(const double* t,const double* p,const C* m){
 return m[0]*t[0]*p[0]+m[1]*(t[0]*p[1]+t[1]*p[0])+m[2]*t[1]*p[1]+m[3]*t[2]*p[2];
}
static C tri_real(const double* t,const double* p,const double* v,const C* m,C f){
 const double b0=t[0]*p[0],bc=t[0]*p[1]+t[1]*p[0],bs=t[0]*p[2]+t[2]*p[0];
 const double bcc=t[1]*p[1],bss=t[2]*p[2],bcs=t[1]*p[2]+t[2]*p[1];
 return v[0]*f+v[1]*(m[1]*b0+m[2]*bc+m[4]*bcc+m[5]*bss)+v[2]*(m[3]*bs+m[5]*bcs);
}
extern "C" int bass_moment_accumulate_real_v1(std::size_t n,std::size_t nt,std::size_t np,
 const double* geo,const double* radt,const double* radp,const double* qt,const double* qp,
 const double* vel,const double* weights,const double* phase,double R,double Zt,double Zp,double* output) noexcept {
 if(!n||!nt||!np||!geo||!radt||!radp||!qt||!qp||!vel||!weights||!phase||!output)return 1;
 const C I(0.,1.);const std::size_t block=nt*np;
 const double vt2=vel[0]*vel[0]+vel[1]*vel[1]+vel[2]*vel[2];
 const double vp2=vel[3]*vel[3]+vel[4]*vel[4]+vel[5]*vel[5];
 const double vtp=vel[0]*vel[3]+vel[1]*vel[4]+vel[2]*vel[5];
 const bool target_static=(vel[0]==0. && vel[1]==0. && vel[2]==0.);
 for(std::size_t u=0;u<n;++u){
  const double r0=geo[4*u],r1=geo[4*u+1],a=geo[4*u+2],rho=geo[4*u+3];
  const double apx=a-R,xx=(r0*r0+r1*r1-R*R)/2,V=-Zt/r0-Zp/r1;
  const C pw=rd(phase,u);C m[6];for(int k=0;k<6;++k)m[k]=rd(weights,6*u+k);
  const double vpxt[]={vel[3]*a,vel[4]*rho,vel[5]*rho},vpxp[]={vel[3]*apx,vel[4]*rho,vel[5]*rho};
  const double vtxt[]={vel[0]*a,vel[1]*rho,vel[2]*rho},vtxp[]={vel[0]*apx,vel[1]*rho,vel[2]*rho};
  for(std::size_t i=0;i<nt;++i){
   double tq[4];for(int k=0;k<4;++k)tq[k]=qt[2*(4*i+k)];
   const double lt[]={tq[0]+a*tq[1],rho*tq[2],rho*tq[3]};
   const double txp[]={apx*tq[1],rho*tq[2],rho*tq[3]};
   const double at=radt[2*(u*nt+i)],bt=radt[2*(u*nt+i)+1];
   const double vptq=vel[3]*tq[1]+vel[4]*tq[2]+vel[5]*tq[3];
   const double vttq=vel[0]*tq[1]+vel[1]*tq[2]+vel[2]*tq[3];
   const C elt=m[0]*lt[0]+m[1]*lt[1];
   for(std::size_t j=0;j<np;++j){
    double pq[4];for(int k=0;k<4;++k)pq[k]=qp[2*(4*j+k)];
    const double lp[]={pq[0]+apx*pq[1],rho*pq[2],rho*pq[3]};
    const double pxt[]={a*pq[1],rho*pq[2],rho*pq[3]};
    const double ap=radp[2*(u*np+j)],bp=radp[2*(u*np+j)+1];
    const double qdot=tq[1]*pq[1]+tq[2]*pq[2]+tq[3]*pq[3];
    const double vppq=vel[3]*pq[1]+vel[4]*pq[2]+vel[5]*pq[3];
    const double vtpq=vel[0]*pq[1]+vel[1]*pq[2]+vel[2]*pq[3];
    const C elp=m[0]*lp[0]+m[1]*lp[1],f=bil_real(lt,lp,m),sv=at*ap*f;
    const C kin=at*ap*qdot*m[0]+at*bp*bil_real(txp,lp,m)+bt*ap*bil_real(lt,pxt,m)+bt*bp*xx*f;
    C hb=kin+I*ap*(at*vptq*elp+bt*tri_real(lt,lp,vpxt,m,f));
    if(!target_static) hb=hb-I*at*(ap*vtpq*elt+bp*tri_real(lt,lp,vtxp,m,f))+vtp*sv;
    const C dTP=-at*ap*vppq*elt-at*bp*tri_real(lt,lp,vpxp,m,f)-.5*I*vp2*sv;
    const C dPTconj=target_static?C{}:(-at*ap*vttq*elp-ap*bt*tri_real(lt,lp,vtxt,m,f)+.5*I*vt2*sv);
    const C vals[]={sv,.5*hb+V*sv,dTP,dPTconj};
    for(int k=0;k<4;++k){auto pos=k*block+i*np+j;C add=pw*vals[k];output[2*pos]+=add.real();output[2*pos+1]+=add.imag();}
   }
  }
 }
 return 0;
}
