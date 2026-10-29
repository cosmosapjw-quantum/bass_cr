// Exact conditional HL min-cost flow via energy-ordered prefix-segment DAG.
// Input is pre-certified integer-scaled marginals and admissible prefix counts,
// with zero/one birth-bin cost. No physics/rate normalization is inferred.
#include <bits/stdc++.h>
using namespace std; using I=__int128_t; using U=__uint128_t;
string out(I v){if(!v)return "0";bool neg=v<0;U x=neg?U(-(v+1))+1:U(v);string s;while(x){s+=char('0'+x%10);x/=10;}if(neg)s+='-';reverse(s.begin(),s.end());return s;}
I getI(const string&s){if(s.empty())throw runtime_error("EMPTY_INTEGER");bool neg=s[0]=='-';if(neg&&s.size()==1)throw runtime_error("BAD_INTEGER");I x=0, bound=(I(1)<<124);for(size_t i=neg;i<s.size();i++){if(!isdigit((unsigned char)s[i]))throw runtime_error("NONINTEGER");int k=s[i]-'0';if(x>(bound-k)/10)throw runtime_error("INPUT_OVERFLOW");x=10*x+k;}return neg?-x:x;}
struct Edge{int u,v,cost;I cap;};
struct Down{int id,child;};
struct Solver{
 int H,L,B,s,t,V; I total=0,inf=0,m=0,C=0,budget=0;
 vector<I> hh,ll;vector<int> hb,lb;
 vector<Edge>e;vector<vector<int>>adj;vector<long long>potential;
 vector<vector<int>> down;vector<vector<pair<int,int>>> attached;vector<int>segmentOrder;
 vector<int> roots;vector<int>leafSink;vector<vector<int>>members;vector<vector<int>>cuts;
 long long steps=0,pops=0,relaxations=0,dualRelax=0;long long logicalEdges=0;
 Solver(int h,int l,int b,vector<I>hi,vector<I>lo,vector<int>highbin,vector<int>lowbin,vector<vector<int>>pref):H(h),L(l),B(b),s(0),t(h+l+1),V(t+1),hh(move(hi)),ll(move(lo)),hb(move(highbin)),lb(move(lowbin)),adj(V),potential(V),down(V),attached(h),roots(b,-1),leafSink(l,-1),members(b),cuts(move(pref)){
   for(I x:hh){if(x<0)throw runtime_error("NEGATIVE_CAPACITY");total+=x;}
   for(I x:ll){if(x<0)throw runtime_error("NEGATIVE_CAPACITY");total+=x;}
   if(total >=(I(1)<<106))throw runtime_error("CAPACITY_OVERFLOW");
   inf=total+1;
   for(int i=0;i<H;i++)add(s,1+i,hh[i],0);
   for(int j=0;j<L;j++){if(lb[j]<0||lb[j]>=B)throw runtime_error("INVALID_BIN");members[lb[j]].push_back(j);leafSink[j]=add(1+H+j,t,ll[j],0);}
   for(int i=0;i<H;i++)if(hb[i]<0||hb[i]>=B)throw runtime_error("INVALID_BIN");
   for(int b0=0;b0<B;b0++)if(!members[b0].empty())roots[b0]=makeTree(members[b0],0,(int)members[b0].size());
   for(int i=0;i<H;i++)for(int b0=0;b0<B;b0++){
       int k=cuts[i][b0];if(k<0||k>(int)members[b0].size())throw runtime_error("INVALID_PREFIX");logicalEdges+=k;
       if(k>0)connectPrefix(i,b0,roots[b0],0,(int)members[b0].size(),k);
   }
 }
 int node(){int id=V++;adj.push_back({});potential.push_back(0);down.push_back({});return id;}
 int add(int u,int v,I cap,int cost){int id=(int)e.size();e.push_back({u,v,cost,cap});e.push_back({v,u,-cost,0});adj[u].push_back(id);adj[v].push_back(id+1);return id;}
 // Every nonleaf segment node is created AFTER its descendants. This gives a reverse ID topological order.
 int makeTree(const vector<int>&low,int a,int b){if(b-a==1)return 1+H+low[a];int md=(a+b)/2,lc=makeTree(low,a,md),rc=makeTree(low,md,b);int id=node();down[id].push_back(add(id,lc,inf,0));down[id].push_back(add(id,rc,inf,0));segmentOrder.push_back(id);return id;}
 void connectPrefix(int h,int b0,int id,int a,int b,int k){if(k<=a)return;if(b<=k){int eid=add(1+h,id,inf,hb[h]==b0?0:1);attached[h].push_back({eid,id});return;}int md=(a+b)/2;if(id<=t)throw runtime_error("INTERNAL_SEGMENT_EXPECTED");connectPrefix(h,b0,e[down[id][0]].v,a,md,k);connectPrefix(h,b0,e[down[id][1]].v,md,b,k);}
 bool shortest(vector<int>&prev,long long&k){const long long BIG=LLONG_MAX/8;vector<long long>d(V,BIG);prev.assign(V,-1);priority_queue<pair<long long,int>,vector<pair<long long,int>>,greater<pair<long long,int>>>pq;d[s]=0;pq.push({0,s});while(!pq.empty()){auto [dv,u]=pq.top();pq.pop();pops++;if(dv!=d[u])continue;for(int idx:adj[u]){auto a=e[idx];if(a.cap<=0)continue;long long rc=(long long)a.cost+potential[u]-potential[a.v];if(rc<0)throw runtime_error("NEGATIVE_REDUCED_COST");if(dv>BIG-rc)throw runtime_error("DISTANCE_OVERFLOW");if(dv+rc<d[a.v]){d[a.v]=dv+rc;prev[a.v]=idx;pq.push({d[a.v],a.v});relaxations++;}}}if(d[t]==BIG)return false;for(int u=0;u<V;u++)if(d[u]!=BIG)potential[u]+=d[u];k=potential[t]-potential[s];if(k<0)throw runtime_error("NEGATIVE_MARGINAL_COST");return true;}
 vector<int> reconstruct(const vector<int>&prev){vector<int>path;vector<char>seen(V);int u=t;while(u!=s){if(seen[u]||prev[u]<0)throw runtime_error("BROKEN_PATH");seen[u]=1;int idx=prev[u];path.push_back(idx);u=e[idx].u;}return path;}
 pair<vector<long long>,vector<long long>> dual(int k){vector<long long>d(V,0);deque<int>q;vector<char>inq(V,1);vector<int> depth(V);for(int u=0;u<V;u++)q.push_back(u);
   auto update=[&](int u,int v,long long cost){long long nv=d[u]+cost;if(nv>=d[v])return;d[v]=nv;dualRelax++;depth[v]=depth[u]+1;if(depth[v]>=V)throw runtime_error("DUAL_NEGATIVE_CYCLE");if(!inq[v]){inq[v]=1;q.push_back(v);}};
   while(!q.empty()){int u=q.front();q.pop_front();inq[u]=0;for(int j:adj[u])if(e[j].cap>0)update(u,e[j].v,e[j].cost);if(u==t)update(t,s,-k);if(u==s&&m>0)update(s,t,k);}
   vector<long long>ph(H),pl(L);for(int h=0;h<H;h++)ph[h]=max(0LL,d[1+h]-d[s]);for(int l=0;l<L;l++)pl[l]=max(0LL,d[t]-d[1+H+l]);
   I obj=budget;for(int h=0;h<H;h++)obj+=hh[h]*ph[h];for(int l=0;l<L;l++)obj+=ll[l]*pl[l];if(obj!=I(k)*m+(budget-C))throw runtime_error("DUAL_OBJECTIVE_MISMATCH");return {ph,pl};}
 pair<vector<long long>,vector<long long>> terminal(){vector<char>seen(V);deque<int>q;seen[s]=1;q.push_back(s);while(!q.empty()){int u=q.front();q.pop_front();for(int j:adj[u])if(e[j].cap>0&&!seen[e[j].v]){seen[e[j].v]=1;q.push_back(e[j].v);}}if(seen[t])throw runtime_error("NOT_MAX_FLOW");vector<long long>ph(H),pl(L);for(int h=0;h<H;h++)ph[h]=!seen[1+h];for(int l=0;l<L;l++)pl[l]=seen[1+H+l];I obj=0;for(int h=0;h<H;h++)obj+=hh[h]*ph[h];for(int l=0;l<L;l++)obj+=ll[l]*pl[l];if(obj!=m)throw runtime_error("MAXFLOW_DUAL_OBJECTIVE_MISMATCH");return {ph,pl};}
 void emit(int query,I b,I frac,I denom,const vector<int>&path,int k){budget=b;auto dp=k?dual(k):terminal();vector<I>adjflow(e.size()/2);for(int id:path){int fwd=id/2;adjflow[fwd]+=id%2?-frac:frac;}
   auto flow=[&](int j)->I{return e[j^1].cap*denom+adjflow[j/2];};
   vector<vector<pair<int,I>>>label(V);I emitted=0,cross=0;map<pair<int,int>,I>pairs;
   for(int h=0;h<H;h++)for(auto [j,child]:attached[h]){I f=flow(j);if(f<0)throw runtime_error("NEGATIVE_HL_ATTACH");if(f>0)label[child].push_back({h,f});}
   // Segments are created postorder: reverse processing propagates labels downward.
   for(auto it=segmentOrder.rbegin();it!=segmentOrder.rend();++it){int node=*it;vector<I>remain;for(int j:down[node]){I f=flow(j);if(f<0)throw runtime_error("NEGATIVE_SEGMENT_FLOW");remain.push_back(f);}for(auto [h,w]:label[node]){for(size_t j=0;j<remain.size()&&w>0;j++){I x=min(w,remain[j]);if(x>0){label[e[down[node][j]].v].push_back({h,x});remain[j]-=x;w-=x;}}if(w)throw runtime_error("SEGMENT_LABEL_OVERFLOW");}for(I v:remain)if(v)throw runtime_error("SEGMENT_FLOW_ORPHAN");label[node].clear();}
   for(int l=0;l<L;l++){I capUsed=0;for(auto [h,w]:label[1+H+l]){if(w<=0)throw runtime_error("NEGATIVE_LEAF_LABEL");pairs[{h,l}]+=w;capUsed+=w;emitted+=w;if(hb[h]!=lb[l])cross+=w;}if(capUsed!=flow(findLeafSink(l)))throw runtime_error("LEAF_SINK_MISMATCH");}
   I expected=m*denom+frac, expcost=C*denom+I(k)*frac;
   if(emitted!=expected||cross!=expcost)throw runtime_error("EMITTED_MASS_OR_COST_MISMATCH");
   cout<<"QUERY "<<query<<"\nM "<<out(expected)<<" "<<out(denom)<<"\nC "<<out(cross)<<" "<<out(denom)<<"\nBUDGET "<<out(b)<<"\nLOW "<<out(totalLow())<<"\nLAMBDA "<<(k?1:0)<<" "<<(k?k:1)<<"\nPRICE_DENOM "<<(k?k:1)<<"\n";
   for(int h=0;h<H;h++)cout<<"PH "<<h<<" "<<dp.first[h]<<"\n";
   for(int l=0;l<L;l++)cout<<"PL "<<l<<" "<<dp.second[l]<<"\n";
   for(auto&[key,w]:pairs)cout<<"FLOW "<<key.first<<" "<<key.second<<" "<<out(w)<<" "<<out(denom)<<"\n";
   cout<<"STATS "<<steps<<" "<<pops<<" "<<relaxations<<" "<<dualRelax<<" "<<logicalEdges<<" "<<e.size()/2<<" "<<V<<"\nEND\n";
 }
 I totalLow()const {I sum=0;for(I x:ll)sum+=x;return sum;}
 int findLeafSink(int l)const{return leafSink[l];}
 void run(vector<I>query){if(query.empty()||query.size()>128)throw runtime_error("BAD_QUERY_COUNT");vector<pair<I,int>>ord;for(int i=0;i<(int)query.size();i++){if(query[i]<0)throw runtime_error("NEGATIVE_BUDGET");ord.push_back({query[i],i});}stable_sort(ord.begin(),ord.end());size_t pos=0;long long previous=-1;
   for(int iteration=0;iteration<2000000;iteration++){vector<int>prev;long long k;if(!shortest(prev,k)){for(;pos<ord.size();pos++)emit(ord[pos].second,ord[pos].first,0,1,{},0);return;}if(k<previous)throw runtime_error("NONCONVEX_MARGINAL_CURVE");previous=k;auto p=reconstruct(prev);I d=inf;for(int j:p)d=min(d,e[j].cap);if(d<=0)throw runtime_error("BAD_BOTTLENECK");if(k){I end=C+I(k)*d;while(pos<ord.size()&&ord[pos].first<=end){I b=ord[pos].first;if(b<C)throw runtime_error("BAD_QUERY_ORDER");emit(ord[pos].second,b,b-C,k,p,(int)k);pos++;}if(pos==ord.size())return;}
      for(int j:p){e[j].cap-=d;e[j^1].cap+=d;}m+=d;C+=I(k)*d;steps++;
   }throw runtime_error("AUGMENTATION_GUARD");}
};
int main(){ios::sync_with_stdio(false);cin.tie(nullptr);try{
 int H,L,B,Q;if(!(cin>>H>>L>>B>>Q)||H<0||L<0||B<1||B>100||H>20000||L>20000||Q<=0||Q>128)throw runtime_error("HEADER");
 string s;vector<I>budgets(Q),hh(H),ll(L);for(I&x:budgets){cin>>s;x=getI(s);}for(I&x:hh){cin>>s;x=getI(s);}for(I&x:ll){cin>>s;x=getI(s);}vector<int>hb(H),lb(L);for(int&v:hb)cin>>v;for(int&v:lb)cin>>v;vector<vector<int>>cuts(H,vector<int>(B));for(auto&v:cuts)for(int&x:v)cin>>x;
 Solver z(H,L,B,hh,ll,hb,lb,cuts);z.run(budgets);return 0;
 }catch(const exception&e){cerr<<"ERROR "<<e.what()<<'\n';return 2;}}
