"""Independent witness consumer: no calls to native_budget.certify/greedy/hall_cut."""
import hashlib,json
from fractions import Fraction as F
from pathlib import Path
import numpy as np
p=Path(__file__).parent
raw=(p/'ATTRIBUTION_ARRAYS.npz').read_bytes()
assert hashlib.sha256(raw).hexdigest()=='1c974c306b50f3deb86df712844f753b4402fb25e5dbc41c9a1de0254bf3ff47'
with np.load(p/'ATTRIBUTION_ARRAYS.npz',allow_pickle=False) as src:
 e=src['energy_eV_with_cutoff'];w=src['identified_A_He_m3_s2']
a={}
for i in range(len(e)):
 E=F.from_float(float(e[i]));W=F.from_float(float(w[i]));b=0 if i==0 else 1 if E<=1 else 2 if E<=3 else 3
 key='cutoff_ghost' if i==0 else f'active_{i:04d}'
 a[key]=(E,W,b)
assert len(a)==3201
K=F(3)
H={k:v for k,v in a.items() if 2*v[0]>K};L={k:v for k,v in a.items() if 2*v[0]<=K}
witness=json.loads((p/'NATIVE_WITNESS_COMPACT.json').read_text())
used={k:F(0) for k in a}
for group in ['same_pairs','cross_pairs']:
 for h,l,vs in witness[group]:
  E1,W1,b1=a[h];E2,W2,b2=a[l];v=F(vs)
  assert h in H and l in L and E1+E2<=K and v>0
  assert (b1==b2)==(group=='same_pairs')
  used[h]+=v;used[l]+=v
assert all(used[k]<=a[k][1] for k in a)
S=sum((F(v) for _,_,v in witness['same_pairs']),F(0))
R=sum((F(v) for _,_,v in witness['cross_pairs']),F(0))
assert S==F(witness['S']) and R==F(witness['R']) and S+R==F(witness['M'])
N=sum((v[1] for v in a.values()),F(0));low_mass=sum((v[1] for v in L.values()),F(0))
assert N==F(witness['N']) and low_mass==F(witness['L'])
for key,lam,target in [('same_dual_price_one',1,S),('full_dual_price_one',0,S+R)]:
 prices=set(witness[key]);obj=sum((a[k][1] for k in prices),F(0))
 assert obj==target
 checked=0
 for h,(eh,wh,bh) in H.items():
  for l,(el,wl,bl) in L.items():
   if eh+el<=K:
    assert int(h in prices)+int(l in prices)+lam*int(bh!=bl)>=1
    checked+=1
 print(key,'dual_obj=',target,'eligible_edges_checked=',checked)
print('INDEPENDENT_COMPACT_WITNESS_PASS atoms',len(a),'pairs',len(witness['same_pairs'])+len(witness['cross_pairs']),'S',S,'R',R)
