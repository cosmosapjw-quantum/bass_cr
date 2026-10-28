"""Source-byte independent native K3 readback and Hall-cut/primal verification.
Does not import production primal algorithm or PR116 consumer/provider modules.
This is one non-blinded, same-author independent-algorithm check, not fresh C9.
"""
import hashlib,io,json,sys
from pathlib import Path
from fractions import Fraction as F
from collections import defaultdict
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
EXPECTED_NPZ='1c974c306b50f3deb86df712844f753b4402fb25e5dbc41c9a1de0254bf3ff47'
EXPECTED_ATOMS='2cfca578701a2355fa6f1f3f1f8a27c211e81b9b488f65cef1e1a89e4dbc7690'
K=F(3)
raw=(ROOT/'inputs/ATTRIBUTION_ARRAYS.npz').read_bytes()
assert hashlib.sha256(raw).hexdigest()==EXPECTED_NPZ
atoms=[]
with np.load(io.BytesIO(raw),allow_pickle=False) as arr:
 e=arr['energy_eV_with_cutoff'];w=arr['identified_A_He_m3_s2']
 assert len(e)==len(w)==3201 and e.dtype==w.dtype==np.dtype('float64')
 for i,(energy,mass) in enumerate(zip(e,w)):
  en=F.from_float(float(energy));ma=F.from_float(float(mass))
  b=0 if i==0 else (1 if en<=1 else (2 if en<=3 else 3))
  key='cutoff_ghost' if i==0 else 'active_%04d'%i
  assert ma>=0
  atoms.append((key,en,ma,b))
serialized=[[key,str(e),str(w),b] for key,e,w,b in atoms]
digest=hashlib.sha256(json.dumps(serialized,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
assert digest==EXPECTED_ATOMS
result=json.loads((ROOT/'runs/NATIVE_K3_RESULT.json').read_text())
assert result['source_sha256']==EXPECTED_NPZ and result['digest']==digest
keys={key:(e,w,b) for key,e,w,b in atoms};used=defaultdict(F)
for high,low,value in result['pair_events']:
 h,wh,bh=keys[high];l,wl,bl=keys[low];v=F(value)
 assert v>0 and bh==bl and 2*h>K and 2*l<=K and h+l<=K
 used[high]+=v;used[low]+=v
assert all(used[key]<=weight for key,_,weight,_ in atoms)
primal=sum((F(v) for _,_,v in result['pair_events']),F(0))
assert primal==F(result['S'])

independent_by_bin={}
for b in sorted(set(a[3] for a in atoms)):
 high=sorted([(e,w) for k,e,w,bb in atoms if bb==b and w>0 and 2*e>K],reverse=True)
 low=sorted([(e,w) for k,e,w,bb in atoms if bb==b and w>0 and 2*e<=K])
 high_total=sum((w for _,w in high),F(0))
 # Truly separate threshold enumerator: recompute each suffix and neighbor independently.
 thresholds=sorted(set(e for e,_ in high))
 gap=max([F(0)]+[sum((w for e,w in high if e>=t),F(0))-
                        sum((w for e,w in low if e+t<=K),F(0)) for t in thresholds])
 dual=high_total-gap
 assert dual==F(result['per_bin'][b]['S'])
 independent_by_bin[b]={'S':str(dual),'deficiency':str(gap),'high_mass':str(high_total),'low_atoms':len(low),'high_atoms':len(high)}
assert sum((F(v['S']) for v in independent_by_bin.values()),F(0))==primal
N=sum((w for _,_,w,_ in atoms),F(0))
L=sum((w for _,e,w,_ in atoms if 2*e<=K),F(0))
M=F('3456415883490050789/12259964326927110866866776217202473468949912977468817408')
D=(L+M)/2
assert N==F(result['N']) and L==F(result['L']) and M==F(result['M']) and D==F(result['D'])
S=primal
assert 0<S<M
# Finite event-outer-bound consequences: C>=2d-L-S, and at d=D: C>=M-S.
report={'status':'PASS_INDEPENDENT_NATIVE_SOURCE_AND_HALL_CUT','source_npz_sha256':EXPECTED_NPZ,
        'atom_digest':digest,'source_atoms':len(atoms),'pair_events':len(result['pair_events']),
        'exact_margin_checks':len(atoms),'exact_support_checks':len(result['pair_events']),
        'S':str(S),'S_over_N':str(S/N),'WS_m3':str(F(10**20,2)*S),
        'M':str(M),'M_over_N':str(M/N),'M_minus_S':str(M-S),
        'min_cross_C_if_d_equals_D':str(M-S),
        'min_cross_C_over_N_if_d_equals_D':str((M-S)/N),
        'max_d_outer_if_C_zero':str((L+S)/2),
        'max_d_over_N_outer_if_C_zero':str((L+S)/(2*N)),
        'by_bin':independent_by_bin,'solver_imports':0,'new_IVPs':0,
        'scope':'NECESSARY_NATIVE_K3_OUTER_BOUND_NOT_EXCLUSIVE_KERNEL',
        'independent_author_C9':'NOT_RUN'}
(ROOT/'runs/INDEPENDENT_NATIVE.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('by_bin',)},indent=2))
