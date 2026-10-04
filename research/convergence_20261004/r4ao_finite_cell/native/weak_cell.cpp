// R4AN fixed-geometry weak cell evaluator. All mathematical arithmetic uses
// outward GMP integers / 2^256. No libm, double, strong Laplacian, or full-matrix run.
// R4AM formulas are ported without changing the immutable Python reference.
#include <gmpxx.h>
#include <array>
#include <vector>
#include <string>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <algorithm>
using Z=mpz_class;
static constexpr int BITS=256;
static const Z SCALE=Z(1)<<BITS;
Z fq(const Z&a,const Z&b){Z q;mpz_fdiv_q(q.get_mpz_t(),a.get_mpz_t(),b.get_mpz_t());return q;}
Z cq(const Z&a,const Z&b){Z q;mpz_cdiv_q(q.get_mpz_t(),a.get_mpz_t(),b.get_mpz_t());return q;}
Z az(const Z&a){return a<0?-a:a;}
struct I {
 Z lo,hi;
 I(long a=0):lo(Z(a)*SCALE),hi(lo){}
 I(Z a,Z b):lo(a),hi(b){if(a>b)throw std::runtime_error("reversed interval");}
 bool zero()const{return lo==0&&hi==0;}
 I upper()const{Z x=std::max(az(lo),az(hi));return I(x,x);}
 I operator-()const{return I(-hi,-lo);}
 I operator+(const I&b)const{return I(lo+b.lo,hi+b.hi);}
 I operator-(const I&b)const{return *this+-b;}
 I operator*(const I&b)const{if(zero()||b.zero())return I();std::array<Z,4>x={lo*b.lo,lo*b.hi,hi*b.lo,hi*b.hi};return I(fq(*std::min_element(x.begin(),x.end()),SCALE),cq(*std::max_element(x.begin(),x.end()),SCALE));}
 I operator/(const I&b)const{if(b.lo<=0&&b.hi>=0)throw std::runtime_error("zero divisor interval");if(b.hi<0)return (-*this)/(-b);std::array<Z,4>l={fq(lo*SCALE,b.lo),fq(lo*SCALE,b.hi),fq(hi*SCALE,b.lo),fq(hi*SCALE,b.hi)};std::array<Z,4>h={cq(lo*SCALE,b.lo),cq(lo*SCALE,b.hi),cq(hi*SCALE,b.lo),cq(hi*SCALE,b.hi)};return I(*std::min_element(l.begin(),l.end()),*std::max_element(h.begin(),h.end()));}
 I pow(unsigned n)const{I p(1),x=*this;while(n){if(n&1)p=p*x;n>>=1;if(n)x=x*x;}return p;}
 I sqrt()const{if(lo<0)throw std::runtime_error("negative sqrt");Z a,b,aa=lo*SCALE,bb=hi*SCALE;mpz_sqrt(a.get_mpz_t(),aa.get_mpz_t());mpz_sqrt(b.get_mpz_t(),bb.get_mpz_t());if(b*b<bb)++b;return I(a,b);}
 I midbox()const{return I(fq(lo+hi,Z(2)),cq(lo+hi,Z(2)));}
 I radiusbox()const{return I(fq(hi-lo,Z(2)),cq(hi-lo,Z(2)));}
 I intersect(const I&b)const{return I(std::max(lo,b.lo),std::min(hi,b.hi));}
};
I rational(const Z&a,const Z&b){if(b<=0)throw std::runtime_error("nonpositive denominator");return I(fq(a*SCALE,b),cq(a*SCALE,b));}
I rat(long a,long b){return rational(Z(a),Z(b));}
I square(const I&x){if(x.lo<=0&&x.hi>=0)return I(0,(x.upper()*x.upper()).hi);return x*x;}
I sym(const I&x){I y=x.upper();return I(-y.hi,y.hi);}
Z facz(unsigned n){Z z;mpz_fac_ui(z.get_mpz_t(),n);return z;}
I fact(unsigned n){Z z=facz(n)*SCALE;return I(z,z);}
struct C {
 I re,im;
 C(I a=I(),I b=I()):re(a),im(b){}
 C(long a):re(a),im(){}
 bool zero()const{return re.zero()&&im.zero();}
 C operator-()const{return C(-re,-im);}
 C operator+(const C&b)const{return C(re+b.re,im+b.im);}
 C operator-(const C&b)const{return *this+-b;}
 C operator*(const C&b)const{return C(re*b.re-im*b.im,re*b.im+im*b.re);}
 C operator/(const C&b)const{I d=square(b.re)+square(b.im);if(d.lo<=0)throw std::runtime_error("complex pole");return C((re*b.re+im*b.im)/d,(im*b.re-re*b.im)/d);}
 C pow(unsigned n)const{C p(1),x=*this;while(n){if(n&1)p=p*x;n>>=1;if(n)x=x*x;}return p;}
};
I phi(unsigned n,const I&x){
 if(n>4||x.hi>0)throw std::runtime_error("Phi domain");I bound=sym(rational(Z(1),facz(n)));
 if(x.zero())return rational(Z(1),facz(n));
 if(x.hi-x.lo>SCALE/2)return bound;
 I m=x.midbox(),B=m.upper(),t=rational(Z(1),facz(n)),s=t;const unsigned N=128;
 for(unsigned j=1;j<N;j++){t=t*m/I(static_cast<long>(j*(j+n)));s=s+t;}
 I q=B/I(static_cast<long>((N+1)*(N+1+n)));if(q.hi>=SCALE)throw std::runtime_error("Phi tail ratio");
 I tail=B.pow(N)/fact(N)/fact(N+n)/(I(1)-q);
 return (s+sym(tail)+sym(x.radiusbox()/fact(n+1))).intersect(bound);
}
std::pair<I,I> sincos_i(const I&x,const I&pi){
 if(x.zero())return {I(0),I(1)};
 I lim(-SCALE,SCALE);if(x.hi-x.lo>=2*SCALE)return {lim,lim};
 I c=x.midbox(),hp=pi/I(2);Z num=c.lo+c.hi,den=hp.lo+hp.hi,k=fq(num,den),rem=num-k*den;
 if(2*rem>den||(2*rem==den&&mpz_odd_p(k.get_mpz_t())))++k;
 I ki(k*SCALE,k*SCALE),y=c-ki*hp,y2=y*y,ts=y,tc(1),ss=y,cc(1);const int N=48;
 for(int j=1;j<N;j++){ts=-(ts*y2)/I((2*j)*(2*j+1));tc=-(tc*y2)/I((2*j-1)*(2*j));ss=ss+ts;cc=cc+tc;}
 I B=y.upper(),q=B*B/I((2*N+1)*(2*N+2));if(q.hi>=SCALE)throw std::runtime_error("trig tail ratio");
 ss=ss+sym(B.pow(2*N+1)/fact(2*N+1)/(I(1)-q));cc=cc+sym(B.pow(2*N)/fact(2*N)/(I(1)-q));
 unsigned t=mpz_fdiv_ui(k.get_mpz_t(),4);if(t==1){I a=ss;ss=cc;cc=-a;}else if(t==2){ss=-ss;cc=-cc;}else if(t==3){I a=ss;ss=-cc;cc=a;}
 return {(ss+sym(x.radiusbox())).intersect(lim),(cc+sym(x.radiusbox())).intersect(lim)};
}
long binom(int n,int j){long v=1;for(int k=1;k<=j;k++)v=v*(n-k+1)/k;return v;}
struct Moments {
 I Q,k;std::array<I,5> ph;
 Moments(I q,I kk):Q(q),k(kk){if(Q.lo<0)throw std::runtime_error("Q negative");I x=-(square(k)*Q)/I(4);for(int j=0;j<=4;j++)ph[j]=phi(j,x);}
 C u(int n)const{I out;for(int j=0;j<=n/2;j++){
   I coeff=rational(facz(n),facz(n-2*j)*facz(j));
   out=out+coeff*ph[n-j]*((-k*Q/I(2)).pow(n-2*j))*((-Q/I(4)).pow(j));
 }std::array<C,4>phase={C(1),C(I(),I(-1)),C(-1),C(I(),I(1))};return C(out)*phase[n%4];}
 C get(int a,int b)const{if(a<0||b<0||a+b>4)throw std::runtime_error("angular degree");if(b%2)return C();C out;int s=b/2;for(int j=0;j<=s;j++)out=out+u(a+2*j)*C(((j%2)?-1:1)*binom(s,j))*C(Q.pow(s-j));return out;}
};
struct Term {int a,b;C c;};
struct P {
 std::vector<Term> t;
 P()=default;P(C c){if(!c.zero())t.push_back({0,0,c});}P(I c):P(C(c)){}P(long c):P(C(c)){}
 static P uv(int a,int b){P p;p.t.push_back({a,b,C(1)});return p;}
 void accum(int a,int b,C c){for(auto&x:t)if(x.a==a&&x.b==b){x.c=x.c+c;return;}t.push_back({a,b,c});}
 P clean()const{P p;for(auto x:t)if(!x.c.zero())p.t.push_back(x);return p;}
 P operator+(const P&b)const{P p=*this;for(auto x:b.t)p.accum(x.a,x.b,x.c);return p.clean();}
 P operator-()const{P p;for(auto x:t){x.c=-x.c;p.t.push_back(x);}return p;}
 P operator-(const P&b)const{return *this+-b;}
 P operator*(const P&b)const{P p;for(auto x:t)for(auto y:b.t)p.accum(x.a+y.a,x.b+y.b,x.c*y.c);return p.clean();}
 P operator/(const C&b)const{P p;for(auto x:t){x.c=x.c/b;p.t.push_back(x);}return p.clean();}
 C mean(const Moments&m)const{C s;for(auto x:t)s=s+x.c*m.get(x.a,x.b);return s;}
};
using PV=std::array<P,3>;using CV=std::array<C,3>;
P dot(const PV&a,const PV&b){P p;for(int k=0;k<3;k++)p=p+a[k]*b[k];return p;}
P dot(const CV&a,const PV&b){P p;for(int k=0;k<3;k++)p=p+P(a[k])*b[k];return p;}
struct Field{P f;PV g;};
struct Radial {int ell,m;I lo,delta;std::array<I,5>c;
 std::pair<C,C> eval(C r)const{C s=(r-C(lo))/C(delta),u,du;for(int k=4;k>=0;k--)u=u*s+C(c[k]);for(int k=4;k>=1;k--)du=du*s+C(I(k)*c[k]);return {u,du/C(delta)};}
 std::pair<C,C> first(C r)const{if(!lo.zero()||!c[0].zero())throw std::runtime_error("origin zero trace");C s=r/C(delta),u,du;for(int k=4;k>=1;k--)u=u*s+C(c[k]);for(int k=4;k>=2;k--)du=du*s+C(I(k-1)*c[k]);return {u/C(delta),du/C(delta*delta)};}
};
CV harmonic(int ell,int m,bool conjugated){if(ell==0&&m==0)return {C(),C(),C()};if(ell!=1||m<-1||m>1)throw std::runtime_error("harmonic domain");I a=I(3).sqrt(),b=rat(3,2).sqrt();if(m==0)return {C(),C(),C(a)};return {C(m==-1?b:-b),C(I(),conjugated?b:-b),C()};}
Field regular(const Radial&r,C x,const PV&coords,bool cj){auto c=harmonic(r.ell,r.m,cj);auto ud=r.eval(x);C q=ud.first/x.pow(r.ell+1),qr=ud.second/x.pow(r.ell+1)-C(r.ell+1)*ud.first/x.pow(r.ell+2);P g=r.ell?dot(c,coords):P(1);Field o;o.f=g*P(q);for(int k=0;k<3;k++)o.g[k]=g*coords[k]*P(qr/x)+(r.ell?P(c[k])*P(q):P());return o;}
Field origin(const Radial&r,C x,const PV&n,bool cj){auto c=harmonic(r.ell,r.m,cj);auto f=r.first(x);Field o;if(!r.ell){o.f=P(f.first);for(int k=0;k<3;k++)o.g[k]=n[k]*P(x*f.second);}else{P g=dot(c,n);o.f=g*P(f.first);for(int k=0;k<3;k++)o.g[k]=g*n[k]*P(x*f.second)+(P(c[k])-g*n[k])*P(f.first);}return o;}
struct Model {
 int kind;I b,z,v,R,nu,t,radius,pi,det;std::array<std::array<I,2>,3> vertices;Radial left,right;
 std::array<C,4> eval(I ui,I wi)const{
  if(ui.lo<0||ui.hi>SCALE||wi.lo<0||wi.hi>SCALE)throw std::runtime_error("outside real unit square");
  C u(ui),w(wi),rr(R),ex=C(b)/rr,ez=C(z)/rr;CV e={ex,C(),ez},e1={-ez,C(),ex},e2={C(),C(-1),C()};
  P U=P::uv(1,0),V=P::uv(0,1);PV trans;for(int k=0;k<3;k++)trans[k]=U*P(e1[k])+V*P(e2[k]);
  P s,h,d;C Q,kk,phase,pref;
  if(kind==0){
   C r0=C(vertices[0][0])+u*(C(vertices[1][0])-C(vertices[0][0])+w*(C(vertices[2][0])-C(vertices[1][0])));
   C r1=C(vertices[0][1])+u*(C(vertices[1][1])-C(vertices[0][1])+w*(C(vertices[2][1])-C(vertices[1][1])));
   C A=(r0*r0-r1*r1+rr*rr)/(C(2)*rr);PV xt,xp;for(int k=0;k<3;k++){xt[k]=P(A*e[k])+trans[k];xp[k]=xt[k]-P(rr*e[k]);}
   auto ft=regular(left,r0,xt,true),fp=regular(right,r1,xp,false);P product=ft.f*fp.f;
   h=dot(ft.g,fp.g)/C(2)+ft.g[2]*fp.f*P(C(I(),v/I(2)))-product*P(C(1)/r0+C(1)/r1);
   d=ft.f*fp.g[2]*P(-v)+product*P(C(I(),-nu));s=product;
   pref=r0*r1*u*C(det)/(C(2)*rr);
   Q=((r0+r1+rr)*(r0+r1-rr)*(rr+r0-r1)*(rr-r0+r1))/(C(4)*rr*rr);
   kk=C(v*b)/rr;phase=A*ez*C(v)-C(nu*t);
  }else{
   C r=u*C(radius),eta=w*C(2)-C(1),other=rr+r*eta;
   C aa=-eta+r*(C(1)-eta*eta)/(C(2)*rr);if(kind==2)aa=-aa;
   PV n,local;for(int k=0;k<3;k++){n[k]=P(aa*e[k])+trans[k];local[k]=n[k]*P(r);}
   Field ft,fp;
   if(kind==1){PV xp;for(int k=0;k<3;k++)xp[k]=local[k]-P(rr*e[k]);ft=origin(left,r,n,true);fp=regular(right,other,xp,false);
    h=dot(ft.g,fp.g)*P(r)/C(2)+ft.g[2]*fp.f*P(r*C(I(),v/I(2)));
    d=ft.f*fp.g[2]*P(-v)*P(r*r)+ft.f*fp.f*P((r*r)*C(I(),-nu));
    phase=r*aa*ez*C(v)-C(nu*t);
   }else{PV xt;for(int k=0;k<3;k++)xt[k]=local[k]+P(rr*e[k]);ft=regular(left,other,xt,true);fp=origin(right,r,n,false);
    h=dot(ft.g,fp.g)*P(r)/C(2)+ft.g[2]*fp.f*P((r*r)*C(I(),v/I(2)));
    d=ft.f*fp.g[2]*P(-v)*P(r)+ft.f*fp.f*P((r*r)*C(I(),-nu));
    phase=C(v*z)+r*aa*ez*C(v)-C(nu*t);
   }
   h=h-ft.f*fp.f*P(r+r*r/other);s=ft.f*fp.f*P(r*r);
   pref=other*C(I(2)*radius)/(C(2)*rr);Q=C(1)-aa*aa;kk=C(v*b)*r/rr;
  }
  if(!Q.im.zero()||!kk.im.zero()||!phase.im.zero()||Q.re.hi<0)throw std::runtime_error("not physical real path");
  Moments mm(I(std::max(Z(0),Q.re.lo),Q.re.hi),kk.re);auto sc=sincos_i(phase.re,pi);C factor=C(sc.second,sc.first)*pref;
  P kp=h-d*P(C(I(),I(1)));return {s.mean(mm)*factor,h.mean(mm)*factor,d.mean(mm)*factor,kp.mean(mm)*factor};
 }
};
std::string token(std::istream&f){std::string s;if(!(f>>s)||s.size()>8192)throw std::runtime_error("missing or oversized token");return s;}
I readi(std::istream&f){Z a(token(f)),b(token(f));return I(a,b);}
int readint(std::istream&f,int lo,int hi){auto s=token(f);size_t p;long v=std::stol(s,&p);if(p!=s.size()||v<lo||v>hi)throw std::runtime_error("integer domain");return static_cast<int>(v);}
int main(){try{
 std::string schema=token(std::cin);if(schema!="R4AN_CELL_V1"||readint(std::cin,256,256)!=256)throw std::runtime_error("schema/precision");
 Model m;m.kind=readint(std::cin,0,2);m.b=readi(std::cin);m.z=readi(std::cin);m.v=readi(std::cin);m.R=readi(std::cin);m.nu=readi(std::cin);m.t=readi(std::cin);m.radius=readi(std::cin);m.pi=readi(std::cin);
 if(m.b.lo<0||m.v.lo<0||m.R.lo<=0||m.radius.lo<=0||m.pi.lo<=3*SCALE||m.pi.hi>=4*SCALE)throw std::runtime_error("context domain");
 for(auto*r:{&m.left,&m.right}){r->ell=readint(std::cin,0,1);r->m=readint(std::cin,-r->ell,r->ell);r->lo=readi(std::cin);r->delta=readi(std::cin);for(auto&c:r->c)c=readi(std::cin);if(r->lo.lo<0||r->delta.lo<=0)throw std::runtime_error("radial domain");}
 for(auto&v:m.vertices)for(auto&x:v)x=readi(std::cin);m.det=readi(std::cin);
 if(m.kind==0&&(m.left.lo.lo<=0||m.right.lo.lo<=0||m.det.lo<=0))throw std::runtime_error("regular cell origin/orientation");
 if(m.kind==1&&(!m.left.lo.zero()||!m.left.c[0].zero()))throw std::runtime_error("T origin trace");
 if(m.kind==2&&(!m.right.lo.zero()||!m.right.c[0].zero()))throw std::runtime_error("P origin trace");
 int count=readint(std::cin,1,16384);std::array<C,4> sums{};
 for(int j=0;j<count;j++){I u=readi(std::cin),w=readi(std::cin),weight=readi(std::cin);if(weight.lo<0)throw std::runtime_error("negative integration weight");auto v=m.eval(u,w);for(int k=0;k<4;k++)sums[k]=sums[k]+v[k]*C(weight);}
 std::string extra;if(std::cin>>extra)throw std::runtime_error("trailing input");
 std::cout<<"R4AN_NUMERIC_V1 256 "<<count<<'\n';const char*keys[]={"S_TP","H_TP","D_TP","K_TP"};
 for(int k=0;k<4;k++)std::cout<<keys[k]<<' '<<sums[k].re.lo<<' '<<sums[k].re.hi<<' '<<sums[k].im.lo<<' '<<sums[k].im.hi<<'\n';return 0;
 }catch(const std::exception&e){std::cerr<<"R4AN_REJECT: "<<e.what()<<'\n';return 2;}}
