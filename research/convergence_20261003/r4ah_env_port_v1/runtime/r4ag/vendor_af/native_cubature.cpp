// R4AF tensor Gaussian evaluator. All scientific arithmetic is outward
// fixed-point GMP integer interval arithmetic, not binary floating point.
#include <gmpxx.h>
#include <array>
#include <vector>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <algorithm>
#include <chrono>
using Z=mpz_class;
static const int BITS=256;
static const Z SCALE=Z(1)<<BITS;
Z floorq(const Z&a,const Z&b){Z q;mpz_fdiv_q(q.get_mpz_t(),a.get_mpz_t(),b.get_mpz_t());return q;}
Z ceilq(const Z&a,const Z&b){Z q;mpz_cdiv_q(q.get_mpz_t(),a.get_mpz_t(),b.get_mpz_t());return q;}
Z absz(const Z&a){return a<0?-a:a;}
struct I {
 Z lo,hi;
 I(long a=0):lo(Z(a)*SCALE),hi(lo){}
 I(const Z&a,const Z&b):lo(a),hi(b){if(a>b)throw std::runtime_error("reversed interval");}
 bool zero()const{return lo==0&&hi==0;}
 I upper()const{Z a=std::max(absz(lo),absz(hi));return I(a,a);}
 I operator-()const{return I(-hi,-lo);}
 I operator+(const I&b)const{return I(lo+b.lo,hi+b.hi);}
 I operator-(const I&b)const{return *this+-b;}
 I operator*(const I&b)const{
  if(zero()||b.zero())return I();
  std::array<Z,4> v={lo*b.lo,lo*b.hi,hi*b.lo,hi*b.hi};
  return I(floorq(*std::min_element(v.begin(),v.end()),SCALE),ceilq(*std::max_element(v.begin(),v.end()),SCALE));
 }
 I operator/(const I&b)const{
  if(b.lo<=0&&b.hi>=0)throw std::runtime_error("interval denominator contains zero");
  if(b.hi<0)return (-*this)/(-b);
  std::array<Z,4> l={floorq(lo*SCALE,b.lo),floorq(lo*SCALE,b.hi),floorq(hi*SCALE,b.lo),floorq(hi*SCALE,b.hi)};
  std::array<Z,4> h={ceilq(lo*SCALE,b.lo),ceilq(lo*SCALE,b.hi),ceilq(hi*SCALE,b.lo),ceilq(hi*SCALE,b.hi)};
  return I(*std::min_element(l.begin(),l.end()),*std::max_element(h.begin(),h.end()));
 }
 I operator*(long b)const{return b>=0?I(lo*b,hi*b):I(hi*b,lo*b);}
 I operator/(long b)const{if(!b)throw std::runtime_error("zero int division");if(b<0)return (-*this)/(-b);return I(floorq(lo,Z(b)),ceilq(hi,Z(b)));}
 I pow(unsigned n)const{I p(1),a=*this;while(n){if(n&1)p=p*a;n>>=1;if(n)a=a*a;}return p;}
 I sqrt()const{if(lo<0)throw std::runtime_error("sqrt negative");Z a,b,aa=lo*SCALE,bb=hi*SCALE;mpz_sqrt(a.get_mpz_t(),aa.get_mpz_t());mpz_sqrt(b.get_mpz_t(),bb.get_mpz_t());if(b*b<bb)++b;return I(a,b);}
};
I operator*(long a,const I&b){return b*a;} I operator+(long a,const I&b){return I(a)+b;} I operator-(long a,const I&b){return I(a)-b;}
I sym(const I&a){I x=a.upper();return I(-x.hi,x.hi);}
I factorial(int n){Z z;mpz_fac_ui(z.get_mpz_t(),n);return I(z*SCALE,z*SCALE);}
I readi(std::istream&s){std::string a,b;if(!(s>>a>>b))throw std::runtime_error("truncated interval input");return I(Z(a),Z(b));}
void dump(std::ostream&o,const I&x){o<<x.lo<<' '<<x.hi<<' ';}
struct C {
 I re,im; C(I a=I(),I b=I()):re(a),im(b){}
 C operator+(const C&b)const{return C(re+b.re,im+b.im);}
 C operator-(const C&b)const{return C(re-b.re,im-b.im);}
 C operator*(const C&b)const{return C(re*b.re-im*b.im,re*b.im+im*b.re);}
 C operator*(const I&b)const{return C(re*b,im*b);}
 C operator/(const I&b)const{return C(re/b,im/b);}
 C conj()const{return C(re,-im);}
};
std::pair<I,I> sincos_i(I x,const I&pi){
 I hp=pi/2;Z mid=(x.lo+x.hi)/2;Z hm=(hp.lo+hp.hi)/2;
 // Any integer range reduction is valid. This choice uses integer rounding.
 Z kk=floorq(mid+hm/2,hm);if(!kk.fits_slong_p())throw std::runtime_error("phase reduction integer overflow");long k=kk.get_si();
 I y=x-hp*k, yy=y*y, bs=y.upper();if(bs.hi>4*SCALE)throw std::runtime_error("phase range reduction bound");
 I st=y,ct(1),ss=y,cc(1);int N=64;
 for(int j=1;j<N;j++){st=-(st*yy)/((2*j)*(2*j+1));ct=-(ct*yy)/((2*j-1)*(2*j));ss=ss+st;cc=cc+ct;}
 I q=bs*bs/((2*N+1)*(2*N+2));I rs=bs.pow(2*N+1)/factorial(2*N+1)/(I(1)-q);I rc=bs.pow(2*N)/factorial(2*N)/(I(1)-q);
 ss=ss+sym(rs);cc=cc+sym(rc);int t=(int)((k%4+4)%4);
 if(t==1){I a=ss;ss=cc;cc=-a;}else if(t==2){ss=-ss;cc=-cc;}else if(t==3){I a=ss;ss=-cc;cc=a;}
 return {ss,cc};
}
std::array<I,3> phi_i(I x){
 if(x.hi>0)throw std::runtime_error("Phi argument positive");I ab=x.upper();if(ab.hi>64*SCALE)throw std::runtime_error("Phi outside registered series domain");
 std::array<I,3> t={I(1),I(1),I(1)/2},s=t;int N=96;
 for(int j=1;j<N;j++)for(int n=0;n<3;n++){t[n]=t[n]*x/(j*(j+n));s[n]=s[n]+t[n];}
 for(int n=0;n<3;n++){I q=ab/((N+1)*(N+1+n));I tail=ab.pow(N)/factorial(N)/factorial(N+n)/(I(1)-q);s[n]=s[n]+sym(tail);}
 return s;
}
using Coeff=std::array<I,5>;
struct Rule {int n;std::vector<I> x,w;};
struct Task {int id,i,j,rule;std::array<std::array<I,2>,3> vtx;I det,uc,hu,wc,hw;};
struct Model {
 I b,z,v,R,offset,rt3,rt32,pi;
 std::array<I,41> edges;
 std::array<std::array<Coeff,40>,5> c;
 std::vector<Rule> rules;std::vector<Task> tasks;
 std::array<int,9> modes={0,1,2,3,3,3,4,4,4};
 std::array<int,9> slots={0,0,0,1,2,3,1,2,3};
 I radial(int a,int e,I r)const{
  I d=edges[e+1]-edges[e],s=(r-edges[e])/d;
  if(a>=3&&e==0){if(!c[a][e][0].zero())throw std::runtime_error("non-removable origin");I f=c[a][e][4];for(int k=3;k>=1;k--)f=f*s+c[a][e][k];return f/d;}
  I f=c[a][e][4];for(int k=3;k>=0;k--)f=f*s+c[a][e][k];return a>=3?f/r:f;
 }
 std::array<std::array<C,3>,4> solids(I a)const{
  I X=a*b/R,Zc=a*z/R,cx=-z/R,cz=b/R;
  return {{{C(I(1)),C(),C()},
           {C(X*rt32),C(cx*rt32),C(I(),rt32)},
           {C(Zc*rt3),C(cz*rt3),C()},
           {C(-(X*rt32)),C(-(cx*rt32)),C(I(),rt32)}}};
 }
 std::array<C,81> eval(const Task&t,I u,I w)const{
  I r0=t.vtx[0][0]+u*((t.vtx[1][0]-t.vtx[0][0])+w*(t.vtx[2][0]-t.vtx[1][0]));
  I r1=t.vtx[0][1]+u*((t.vtx[1][1]-t.vtx[0][1])+w*(t.vtx[2][1]-t.vtx[1][1]));
  I r02=r0*r0,r12=r1*r1,R2=R*R;
  I a=(r02-r12+R2)/(R*2);
  I Q=((r0+r1+R)*(r0+r1-R)*(R+r0-r1)*(R-r0+r1))/(R2*4);
  // Real physical cover proves Q>=0; intersect zeroth scalar enclosure only.
  if(Q.hi<0)throw std::runtime_error("invalid real triangle Q"); if(Q.lo<0)Q.lo=0;
  I k=b*v/R,x=-(k*k*Q)/4;auto f=phi_i(x);
  I B1=k*Q*f[1]/2,B2=k*k*Q*Q*f[2]/4,mc=(Q*f[0]-B2)/2,ms=(Q*f[0]+B2)/2;
  auto left=solids(a),right=solids(a-R);std::array<std::array<C,4>,4> ag;
  for(int i=0;i<4;i++)for(int j=0;j<4;j++){
    C a0=left[i][0].conj(),ac=left[i][1].conj(),as=left[i][2].conj();auto bj=right[j];
    ag[i][j]=(a0*bj[0])*f[0]+(a0*bj[1]+ac*bj[0])*C(I(),B1)+(ac*bj[1])*mc+(as*bj[2])*ms;
  }
  auto sc=sincos_i(z*(r02-r12)*v/(R2*2)+offset,pi);
  C common=C(sc.second,sc.first)*(u*t.det/(R*2));
  std::array<I,5> ra,rb;for(int i=0;i<5;i++){ra[i]=radial(i,t.i,r0);rb[i]=radial(i,t.j,r1);}
  std::array<C,81> ans;
  for(int i=0;i<9;i++)for(int j=0;j<9;j++)ans[i*9+j]=ag[slots[i]][slots[j]]*(common*(ra[modes[i]]*rb[modes[j]]));
  return ans;
 }
 std::array<C,81> integrate(const Task&t)const{
  const auto&r=rules.at(t.rule);std::array<C,81> acc{};
  for(int i=0;i<r.n;i++)for(int j=0;j<r.n;j++){
   auto a=eval(t,t.uc+t.hu*r.x[i],t.wc+t.hw*r.x[j]);I weight=r.w[i]*r.w[j]*t.hu*t.hw;
   for(int k=0;k<81;k++)acc[k]=acc[k]+a[k]*weight;
  }return acc;
 }
};
Model load(std::string path){
 std::ifstream f(path);if(!f)throw std::runtime_error("cannot read model");std::string tag;f>>tag;if(tag!="R4AF_NATIVE_V1")throw std::runtime_error("wrong schema");Model m;
 m.b=readi(f);m.z=readi(f);m.v=readi(f);m.R=readi(f);m.offset=readi(f);m.rt3=readi(f);m.rt32=readi(f);m.pi=readi(f);
 for(auto&e:m.edges)e=readi(f);for(auto&a:m.c)for(auto&e:a)for(auto&c:e)c=readi(f);
 int nr;f>>nr;if(nr<1||nr>16)throw std::runtime_error("rule count");
 for(int i=0;i<nr;i++){Rule r;f>>r.n;if(r.n<1||r.n>128)throw std::runtime_error("rule degree");for(int k=0;k<r.n;k++){r.x.push_back(readi(f));r.w.push_back(readi(f));}m.rules.push_back(r);}
 int nt;f>>nt;if(nt<0||nt>20000)throw std::runtime_error("task count");for(int i=0;i<nt;i++){Task t;f>>t.id>>t.i>>t.j>>t.rule;if(t.i<0||t.i>=40||t.j<0||t.j>=40)throw std::runtime_error("panel index");for(auto&v:t.vtx)for(auto&x:v)x=readi(f);t.det=readi(f);t.uc=readi(f);t.hu=readi(f);t.wc=readi(f);t.hw=readi(f);if(t.det.lo<=0||t.hu.lo<=0||t.hw.lo<=0)throw std::runtime_error("orientation or widths");m.tasks.push_back(t);}if(!f)throw std::runtime_error("truncated task input");return m;
}
int main(int argc,char**argv){
 try{
  if(argc>=2&&std::string(argv[1])=="--arithmetic-fixture"){
   I pi=readi(std::cin);auto sc=sincos_i(I(1),pi);dump(std::cout,sc.first);dump(std::cout,sc.second);for(auto&x:phi_i(I(-2)))dump(std::cout,x);std::cout<<'\n';return 0;
  }
  if(argc>=2&&std::string(argv[1])=="--point-fixture"){
   if(argc!=3)throw std::runtime_error("point fixture input");auto m=load(argv[2]);auto a=m.eval(m.tasks.at(0),I(3)/10,I(2)/5);for(auto&v:a){dump(std::cout,v.re);dump(std::cout,v.im);}std::cout<<'\n';return 0;
  }
  if(argc>=2&&std::string(argv[1])=="--quadrature-fixture"){
   I pi=readi(std::cin);int n;std::cin>>n;std::vector<I>x,w;
   for(int i=0;i<n;i++){x.push_back(readi(std::cin));w.push_back(readi(std::cin));}
   I poly;C phase;
   for(int i=0;i<n;i++)for(int j=0;j<n;j++){
    I u=x[i],v=x[j];poly=poly+u.pow(6)*v.pow(4)*w[i]*w[j];
    auto sc=sincos_i(u*2-v*3,pi);phase=phase+C(sc.second,sc.first)*(w[i]*w[j]);
   }
   dump(std::cout,poly);dump(std::cout,phase.re);dump(std::cout,phase.im);std::cout<<'\n';return 0;
  }
  if(argc!=5)throw std::runtime_error("usage: native MODEL OUTPUT WORKER WORKERS");
  int worker=std::stoi(argv[3]),workers=std::stoi(argv[4]);if(workers<1||worker<0||worker>=workers)throw std::runtime_error("worker partition");
  Model m=load(argv[1]);std::ofstream out(argv[2]);if(!out)throw std::runtime_error("output");int count=0;
  for(const auto&t:m.tasks)if(t.id%workers==worker){auto a=m.integrate(t);out<<"CELL "<<t.id<<' ';for(auto&v:a){dump(out,v.re);dump(out,v.im);}out<<'\n';out.flush();count++;if(count%8==0)std::cerr<<"completed="<<count<<" last="<<t.id<<'\n';}
  out<<"DONE "<<count<<'\n';return 0;
 }catch(const std::exception&e){std::cerr<<"ERROR "<<e.what()<<'\n';return 2;}
}
