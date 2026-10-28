"""Generate deterministic scoped figures and machine-readable evidence (no native solver run)."""
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from native_budget import PARENT_S as S, PARENT_M as M

root=Path(__file__).resolve().parent
N=F('77906149556394634457/49039857307708443467467104868809893875799651909875269632')
L=F('999870389230360121/3064991081731777716716694054300618367237478244367204352')
R=M-S
vals=[]
for frac in [F(0),F(1,10),F(1,4),F(1,2),F(3,4),F(9,10),F(1),F(11,10),F(3,2)]:
    c=frac*R
    m=min(S+c,M)
    d=(L+m)/2
    vals.append({'c_over_R':str(frac),'c_over_N':str(c/N),'M_over_N':str(m/N),'d_over_N':str(d/N),
                 'cross_used_over_N':str(min(c,R)/N)})

result={
 'unit':'CR_NATIVE_BUDGET_K3_FRONTIER_V1','date':'2026-10-29',
 'repo':'cosmosapjw-quantum/bass_cr',
 'predecessor_pr':119,'predecessor_head':'25bc4d54df0e26ea2adf60ec012bc6b1a25caf95',
 'source_npz_sha256':'1c974c306b50f3deb86df712844f753b4402fb25e5dbc41c9a1de0254bf3ff47',
 'source_atom_digest':'2cfca578701a2355fa6f1f3f1f8a27c211e81b9b488f65cef1e1a89e4dbc7690',
 'source_access': 'WOLFRAM_URLDOWNLOAD_GITHUB_HTTP200_BITEXACT_NPY_PARSE',
 'K_eV':'3','N':str(N),'L':str(L),'S':str(S),'M':str(M),'R':str(R),
 'R_over_N':str(R/N),'dmax_0_over_N':str((L+S)/(2*N)),
 'dmax_R_over_N':str((L+M)/(2*N)),
 'frontier':'M(c)=min(S+c,M); dmax(c)=(L+M(c))/2; C<=c',
 'native_wolfram':{
   'source_atoms':3201,'low':453,'high':2748,'eligible_high_bin2':485,
   'same_bin_pairs':315,'cross_bin_pairs':526,'total_pairs':841,
   'same_cut_high_threshold_eV':'2254790485312799/1125899906842624',
   'full_cut_high_threshold_eV':'6529867615966331/2251799813685248',
   'same_dual_cover_counts':{'high':162,'low':0},
   'full_dual_cover_counts':{'high':452,'low':1},
   'same_primal_dual_exact':True,'full_primal_dual_exact':True,
   'all_3201_atom_marginals_exact':True,'all_841_pair_support_exact':True,
   'wolfram_json_witness_sha256':'f2260f69db5e5ae6b63c339ca1089d0baf9bf0f74328843a658e321e98ccd8ce',
   'wolfram_witness_sha_scope':'Wolfram ExportString of event triples, not Git file hash',
   'different_author_review':'NOT_RUN'
 },
 'python_local':{'runtime':'PYTHON_PASS','version':'3.13.5','numpy':'2.3.5','sympy':'1.14.0',
    'test_methods_passed':10,'independent_full_event_lp_cases':48,
    'synthetic_3201_topology':'PASS','optimized_mode':'PASS',
    'actual_PR116_npz_python_execution':'NOT_RUN_INPUT_NOT_MOUNTED',
    'source_module_sha256':sha256((root/'native_budget.py').read_bytes()).hexdigest(),
    'test_module_sha256':sha256((root/'test_native_budget.py').read_bytes()).hexdigest()},
 'claim':{'theory':'DERIVED','native_wolfram':'NUMERICALLY_CHECKED_SOURCE_PINNED',
    'python_reference':'IMPLEMENTATION_VERIFIED_SYNTHETIC_ONLY',
    'native_python':'NOT_RUN','R6_distinct_author':'NOT_RUN','C9_distinct_author':'NOT_RUN',
    'scientific_gate':'HOLD_PENDING_DISTINCT_AUTHOR_AND_PYTHON_NATIVE',
    'actual_exclusive_kernel':None,'actual_K':None,'physical_native25':False,'L4':False,
    'central_dag':'28/88','central_delta':0},
 'samples':vals
}
(root/'RESULTS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
xs=[float(F(row['c_over_N'])) for row in vals]
ys=[float(F(row['d_over_N'])) for row in vals]
plt.figure(figsize=(8.2,4.8))
plt.plot(xs,ys,marker='o',linewidth=1.8)
plt.axvline(float(R/N),linestyle='--',linewidth=1,label='Exact kink: (M-S)/N')
plt.xlabel(r'Cross-bin budget $c_\times/N$')
plt.ylabel(r'Exact conditional $d_{\max}/N$')
plt.title('PHYS02 He native K=3 eV: exact budget frontier')
plt.grid(alpha=.25)
plt.legend()
plt.tight_layout()
plt.savefig(root/'FIGURE.png',dpi=160)
plt.savefig(root/'FIGURE.svg')
plt.close()
print('R/N',float(R/N),'d0/N',float((L+S)/(2*N)),'dR/N',float((L+M)/(2*N)))
