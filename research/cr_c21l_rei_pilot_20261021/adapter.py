"""Exact PR147 source adapter. Full state and original RHS/integrate retained."""
import os
for _k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','BLIS_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):
    os.environ[_k]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
from pathlib import Path
import copy, hashlib, json, math, sys
HERE=Path(__file__).resolve().parent
os.environ.setdefault('MPLCONFIGDIR',str(HERE/'runtime/mplconfig'))
BASE=HERE/'vendor/rei/research/rei_bass_hierarchy_backreaction_20261015'
sys.path.insert(0,str(BASE));sys.path.insert(0,str(BASE/'canonical_fv_20261015'))
import numpy as np
from canonical_fv import CanonicalFVSpecies,CanonicalMomentumFV,FVMoments,G_SI,C_SI
from run_hierarchy import source_lock

S_GRID=[-.04,-.02,-.01,-.005,0.,.005,.01,.02,.04]
P_GRID=[-.001,-.00075,-.0005,-.00025,0.,.00025,.0005,.00075,.001]
SETTINGS={'Tcmb0_K':2.7255,'ellmax':8,'mass_fraction':.1,'massive_A':0.,'mass_over_Tref':30.,'radial_cells':24,'angular_cells':12,'subcell_gauss_order':3,'donor':None,'n':101,'rtol':3e-11,'atol':3e-13}

def digest(data):
    return hashlib.sha256(json.dumps(data,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def verify_source():
    manifest=json.loads((HERE/'SOURCE_MANIFEST.json').read_text())
    for r in manifest['files']:
        p=HERE/'vendor/rei'/r['path']
        if p.stat().st_size!=r['size'] or hashlib.sha256(p.read_bytes()).hexdigest()!=r['sha256']:
            raise RuntimeError('IMMUTABLE_SOURCE_BYTE_MISMATCH:'+r['path'])
    return manifest

class ExactReuseMomentum(CanonicalMomentumFV):
    """Only eliminate identical subexpressions; expression/reduction order retained."""
    def moments(self,eta,b):
        if not all(map(math.isfinite,(eta,b))) or eta<0 or abs(b)>1:
            raise ValueError('finite positive cosmological time and Bianchi chart')
        r=math.exp(-eta)
        rq2=(r*self._q)**2
        qp2=rq2*math.exp(2*b)*self._one_minus_mu2
        qz2=rq2*math.exp(-4*b)*self._mu2
        E=np.sqrt(self.mass*self.mass+qp2+qz2)
        coeff=(r**3)/self.reference_energy_norm
        weighted=coeff*self._numbers
        rho=float(np.sum(weighted*E))
        pp=float(np.sum(weighted*(qp2/(2*E))))
        pa=float(np.sum(weighted*(qz2/E)))
        return FVMoments(rho,pp,pa,float(self._number_sum*r**3),self._min_cell)

def make_template(optimized=True):
    obj=CanonicalFVSpecies(source_lock(),2.7255,8,Sigma_ref=0.,orientation=0,
        kappa_gamma=0.,kappa_nu=0.,ne_source=None,mass_fraction=.1,
        massive_A=0.,mass_over_Tref=30.,radial_cells=24,angular_cells=12,subcell_gauss_order=3)
    for arr in (obj.energy_matrix,obj.number_matrix,obj.thomson):arr.flags.writeable=False
    if optimized:
        m=copy.copy(obj.momentum);m.__class__=ExactReuseMomentum
        m._one_minus_mu2=1-m._mu2;m._one_minus_mu2.flags.writeable=False
        m._min_cell=float(np.min(m._cell_numbers));obj.momentum=m
    return obj

def normalized(d):
    p=sum(float(d[k]) for k in ('Pi_gamma_J_m3','Pi_nu_J_m3','Pi_matter_J_m3'))
    S=math.sqrt(6)*float(d['s'])/float(d['H'])
    P=(8*math.pi*G_SI/C_SI**2)*math.sqrt(6)*p/float(d['H'])**2
    return {'S':S,'P':P,'Sigma_F':abs(S),'Pi_F':abs(P),'Sigma_half':abs(S)/math.sqrt(2),'Pi_half':abs(P)/math.sqrt(2),'p_total_J_m3':p}

def map_case(template,S0,P0):
    if not all(map(math.isfinite,(S0,P0))) or abs(S0)>=math.sqrt(6):raise ValueError('invalid target')
    obj=copy.copy(template)
    obj.Sigma_ref=abs(S0)/math.sqrt(2);obj.orientation=int(np.sign(S0));obj._nfev=0
    obj.k_gamma=obj.k_nu=0.
    z=normalized(obj.fields(0.,obj.initial_state()))
    obj.k_gamma=obj.k_nu=.5
    h=normalized(obj.fields(0.,obj.initial_state()))
    slope=2*(h['P']-z['P'])
    if not math.isfinite(slope) or slope==0:raise ArithmeticError('nonfinite/zero mapping slope')
    k=(P0-z['P'])/slope
    if not math.isfinite(k) or abs(k)>.5:raise ValueError('mapped k outside positive source domain')
    obj.k_gamma=obj.k_nu=k
    actual=normalized(obj.fields(0.,obj.initial_state()))
    if max(abs(actual['S']-S0),abs(actual['P']-P0))>2e-13:raise ArithmeticError('initial mapping discrepancy')
    return obj,{'requested_S0':S0,'requested_P0':P0,'source_Sigma_ref':obj.Sigma_ref,'orientation':obj.orientation,'q':S0/math.sqrt(6-S0*S0),'k_gamma':k,'k_nu':k,'actual':actual,'P_k0':z['P'],'P_khalf':h['P']}

def solve_case(template,S0,P0):
    obj,mapping=map_case(template,S0,P0)
    sol,diag,seconds=obj.integrate(n=101,rtol=3e-11,atol=3e-13)
    hist={'eta':sol.t,'Y':sol.y,'proper_elapsed_s':sol.y[0]/obj.source.href}
    scalar_keys=[k for k,v in diag[0].items() if isinstance(v,(float,int,np.floating,np.integer))]
    for k in scalar_keys:hist[k]=np.array([d[k] for d in diag],dtype=np.float64)
    for k in ('E_gamma','N_gamma','E_nu','N_nu'):hist[k]=np.stack([d[k] for d in diag])
    norms=[normalized(d) for d in diag]
    for k in norms[0]:hist[k]=np.array([d[k] for d in norms],dtype=np.float64)
    if sol.y.dtype!=np.float64 or sol.y.shape!=(40,101) or not all(np.isfinite(a).all() for a in hist.values()):raise ArithmeticError('full FP64 state/history invalid')
    hres=max(abs(d['Einstein_H2']/d['H']**2-1) for d in diag)
    nres=max(max(abs(d['N_gamma'][0]-1),abs(d['N_nu'][0]-1)) for d in diag)
    mincell=min(d['massive_min_cell_population'] for d in diag)
    conserved=max(abs(hist['massive_physical_number_norm']*np.exp(3*sol.t)/obj.momentum.total_cell_number-1))
    if hres>2e-13 or nres>2e-10 or mincell<0:raise ArithmeticError('SOURCE_CONSTRAINT_NUMBER_POSITIVITY')
    receipt={'mapping':mapping,'nfev':int(sol.nfev),'solver_wall_s':seconds,'state_shape':list(sol.y.shape),'dtype':str(sol.y.dtype),'diagnostics':{'Einstein_H2_constraint_max_relative':hres,'radiation_number_max_abs':nres,'min_massive_cell_number':mincell,'massive_comoving_number_max_relative':float(conserved),'max_initial_mapping_error':max(abs(norms[0]['S']-S0),abs(norms[0]['P']-P0))},'endpoint':{**norms[-1],'a':float(diag[-1]['a']),'H':float(diag[-1]['H']),'b':float(diag[-1]['b']),**{k:float(diag[-1][k]) for k in ('Pi_gamma_J_m3','Pi_nu_J_m3','Pi_matter_J_m3')}},'global_error_bound':None}
    return receipt,hist
