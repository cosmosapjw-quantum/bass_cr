// Source-independent exact integral-scaled bipartite budget min-cost flow.
// Scientific domain: finite fractional conditional HL event allocation, no physical rates.
// Input integer capacities and ONE integer cross-bin budget, all in the same exact scale.
// Output exact scaled rational primal witness and vertex/constraint LP dual.
#include <bits/stdc++.h>
using namespace std;
using I=__int128_t;
using U=__uint128_t;
string str(I x){ if(x==0)return "0"; bool neg=x<0; U y=neg?U(-(x+1))+1:U(x); string s;while(y){s.push_back(char('0'+y%10));y/=10;}if(neg)s.push_back('-');reverse(s.begin(),s.end());return s;}
I parse(const string &s){if(s.empty())throw runtime_error("EMPTY_INTEGER");bool neg=s[0]=='-';I v=0;for(size_t i=neg;i<s.size();i++){if(!isdigit((unsigned char)s[i]))throw runtime_error("NONINTEGER");int d=s[i]-'0';if(v>( (I(1)<<125)-d)/10)throw runtime_error("INPUT_128_OVERFLOW");v=v*10+d;}return neg?-v:v;}
struct Edge{int u,v, cost; I cap;};
struct Original{int hi,lo,id,cost;};
struct Solver{
 int H,L,V,s,t;vector<I> ch,cl;I budget,INF,totalLow=0,m=0,C=0;
 vector<Edge> e;vector<vector<int>> adj;vector<Original> original;vector<int> originalOfArc;
 vector<long long> pot;long long augments=0,pops=0,relax=0,spfa_relax=0;
 Solver(int h,int l,vector<I> hh,vector<I> ll,I b):H(h),L(l),V(h+l+2),s(0),t(V-1),ch(move(hh)),cl(move(ll)),budget(b),adj(V),pot(V,0){I sum=0;for(auto v:ch){if(v<0)throw runtime_error("NEGATIVE_CAPACITY");sum+=v;}for(auto v:cl){if(v<0)throw runtime_error("NEGATIVE_CAPACITY");totalLow+=v;}if(sum+totalLow >= (I(1)<<106))throw runtime_error("CAPACITY_128_SAFETY_LIMIT");
 INF=sum+totalLow+1;for(int i=0;i<H;i++)add(s,1+i,ch[i],0);for(int i=0;i<L;i++)add(1+H+i,t,cl[i],0);}
 int add(int u,int v,I cap,int cost){int id=e.size();e.push_back({u,v,cost,cap});e.push_back({v,u,-cost,0});adj[u].push_back(id);adj[v].push_back(id+1);originalOfArc.push_back(-1);originalOfArc.push_back(-1);return id;}
 void addHL(int h,int l,int cost){if(h<0||h>=H||l<0||l>=L||!(cost==0||cost==1))throw runtime_error("BAD_EDGE");int id=add(1+h,1+H+l,INF,cost);int index=original.size();original.push_back({h,l,id,cost});originalOfArc[id]=index;originalOfArc[id+1]=index;}
 bool shortest(vector<int>&prev,long long &k){
  const long long INFD=LLONG_MAX/8;vector<long long>d(V,INFD);prev.assign(V,-1);
  priority_queue<pair<long long,int>,vector<pair<long long,int>>,greater<pair<long long,int>>>pq;d[s]=0;pq.push({0,s});
  while(!pq.empty()){
   auto [du,u]=pq.top();pq.pop();pops++;if(du!=d[u])continue;
   for(int id:adj[u]){const auto &a=e[id];if(a.cap<=0)continue;
    long long rc=static_cast<long long>(a.cost)+pot[u]-pot[a.v];if(rc<0)throw runtime_error("NEGATIVE_REDUCED_COST");
    if(du>INFD-rc)throw runtime_error("DISTANCE_OVERFLOW");
    if(du+rc<d[a.v]){d[a.v]=du+rc;prev[a.v]=id;pq.push({d[a.v],a.v});relax++;}
   }
  }
  if(d[t]==INFD)return false;
  for(int u=0;u<V;u++)if(d[u]!=INFD)pot[u]+=d[u];
  k=pot[t]-pot[s];if(k<0)throw runtime_error("NEGATIVE_MARGINAL_COST");return true;
 }
 vector<int> path(const vector<int>&prev){vector<int> path;int u=t;vector<bool>seen(V,false);while(u!=s){if(seen[u]||prev[u]<0)throw runtime_error("BROKEN_PATH");seen[u]=true;int id=prev[u];path.push_back(id);u=e[id].u;}return path;}
 // Given a cost-minimal flow and k equal to the next marginal cost, derive integer
 // dual prices via global residual circulation potentials with t->s cost -k.
 // This is a certificate construction, not a numerical LP tolerance check.
 pair<vector<long long>,vector<long long>> dual(int k){
  vector<long long>d(V,0);deque<int>q;vector<bool>inq(V,true);vector<int> depth(V,0);for(int u=0;u<V;u++)q.push_back(u);
  auto relax_edge=[&](int u,int v,int cost){
    long long vnew=d[u]+cost;if(vnew>=d[v])return;
    d[v]=vnew;spfa_relax++;depth[v]=depth[u]+1;
    if(depth[v]>=V)throw runtime_error("DUAL_NEGATIVE_CYCLE");
    if(!inq[v]){q.push_back(v);inq[v]=true;}
  };
  // Residual edge t->s has unbounded forward capacity and reverse has capacity m.
  while(!q.empty()){
   int u=q.front();q.pop_front();inq[u]=false;
   for(int id:adj[u])if(e[id].cap>0)relax_edge(u,e[id].v,e[id].cost);
   if(u==t)relax_edge(t,s,-k);
   if(u==s && m>0)relax_edge(s,t,k);
  }
  vector<long long>ph(H),pl(L);
  for(int h=0;h<H;h++)ph[h]=max(0LL,d[1+h]-d[s]);
  for(int l=0;l<L;l++)pl[l]=max(0LL,d[t]-d[1+H+l]);
  for(const auto &a:original)if(ph[a.hi]+pl[a.lo]+a.cost<k)throw runtime_error("DUAL_EDGE_UNCOVERED");
  I objective=budget;for(int h=0;h<H;h++)objective+=ch[h]*ph[h];for(int l=0;l<L;l++)objective+=cl[l]*pl[l];
  // For within a segment, optimum is m+(budget-C)/k.
  if(objective!=I(k)*m+(budget-C))throw runtime_error("DUAL_OBJECTIVE_MISMATCH");
  return {ph,pl};
 }
 pair<vector<long long>,vector<long long>> terminalDual(){
  vector<bool>seen(V);deque<int>q;seen[s]=true;q.push_back(s);
  while(!q.empty()){int u=q.front();q.pop_front();for(int id:adj[u])if(e[id].cap>0&&!seen[e[id].v]){seen[e[id].v]=true;q.push_back(e[id].v);}}
  if(seen[t])throw runtime_error("NOT_MAX_FLOW");
  vector<long long>ph(H),pl(L);for(int h=0;h<H;h++)ph[h]=!seen[1+h];for(int l=0;l<L;l++)pl[l]=seen[1+H+l];
  for(const auto&a:original)if(ph[a.hi]+pl[a.lo]<1)throw runtime_error("MAXFLOW_DUAL_EDGE_UNCOVERED");
  I obj=0;for(int h=0;h<H;h++)obj+=ch[h]*ph[h];for(int l=0;l<L;l++)obj+=cl[l]*pl[l];if(obj!=m)throw runtime_error("MAXFLOW_DUAL_OBJECTIVE_MISMATCH");return {ph,pl};
 }
 void output(const string&state,I fractional,I denom,const vector<int>&p,int k){
  // scaled event mass = (m*denom+fractional)/denom; fractional = unused budget.
  auto prices=(k==0)?terminalDual():dual(k);
  I numerator=m*denom+fractional;
  vector<I>adjust(original.size());for(int id:p){int j=originalOfArc[id];if(j!=-1)adjust[j]+= (id%2==0?fractional:-fractional);}
  cout<<"STATUS "<<state<<"\n";
  cout<<"M "<<str(numerator)<<" "<<str(denom)<<"\n";
  cout<<"C "<<str(C*denom+I(k?fractional*k:0))<<" "<<str(denom)<<"\n";
  cout<<"BUDGET "<<str(budget)<<"\n";
  cout<<"LOW "<<str(totalLow)<<"\n";
  cout<<"LAMBDA "<<(k?1:0)<<" "<<(k?k:1)<<"\n";
  cout<<"PRICE_DENOM "<<(k?k:1)<<"\n";
  for(int h=0;h<H;h++)cout<<"PH "<<h<<" "<<prices.first[h]<<"\n";
  for(int l=0;l<L;l++)cout<<"PL "<<l<<" "<<prices.second[l]<<"\n";
  I checkm=0,checkC=0;
  for(size_t j=0;j<original.size();j++){
   const auto &a=original[j];I x=e[a.id^1].cap*denom+adjust[j];
   if(x<0)throw runtime_error("NEGATIVE_PRIMAL");
   if(x){cout<<"FLOW "<<a.hi<<" "<<a.lo<<" "<<str(x)<<" "<<str(denom)<<"\n";checkm+=x;checkC+=a.cost*x;}
  }
  if(checkm!=numerator||checkC!=C*denom+I(k?fractional*k:0))throw runtime_error("PRIMAL_SUM_MISMATCH");
  cout<<"STATS "<<augments<<" "<<pops<<" "<<relax<<" "<<spfa_relax<<" "<<original.size()<<"\nEND\n";
 }
 void solve(){
  long long previous=-1;
  for(long long step=0;step<2000000;step++){
   vector<int>prev;long long k; if(!shortest(prev,k)){output("SATURATED",0,1,{},0);return;}
   if(k<previous)throw runtime_error("NONCONVEX_MARGINAL_CURVE");
   previous=k;
   vector<int>p=path(prev);I delta=INF;
   for(int id:p)delta=min(delta,e[id].cap);
   if(delta<=0)throw runtime_error("NONPOSITIVE_AUGMENT");
   if(k>0&&C+I(k)*delta>budget){output("PARTIAL",budget-C,I(k),p,int(k));return;}
   for(int id:p){e[id].cap-=delta;e[id^1].cap+=delta;}
   m+=delta;C+=I(k)*delta;augments++;
  }
  throw runtime_error("AUGMENTATION_GUARD");
 }
};
int main(){ios::sync_with_stdio(false);cin.tie(nullptr);try{
 string a,b,x;int h,l,E; if(!(cin>>h>>l>>E>>x))throw runtime_error("BAD_HEADER");
 if(h<0||l<0||E<0||h>20000||l>20000||E>4000000)throw runtime_error("BAD_DIMENSIONS");
 I budget=parse(x);if(budget<0)throw runtime_error("NEGATIVE_BUDGET");vector<I>hi(h),lo(l);
 for(int i=0;i<h;i++){cin>>x;hi[i]=parse(x);}for(int j=0;j<l;j++){cin>>x;lo[j]=parse(x);}
 Solver z(h,l,hi,lo,budget);set<pair<int,int>> duplicate;
 for(int i=0;i<E;i++){int u,v,k;if(!(cin>>u>>v>>k))throw runtime_error("BAD_EDGE_INPUT");if(!duplicate.insert({u,v}).second)throw runtime_error("DUPLICATE_EDGE");z.addHL(u,v,k);}z.solve();return 0;
 }catch(const exception &er){cerr<<"ERROR "<<er.what()<<"\n";return 2;}}
