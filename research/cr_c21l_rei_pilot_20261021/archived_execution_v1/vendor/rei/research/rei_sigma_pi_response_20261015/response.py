"""Source-bound Einstein-Boltzmann-Vlasov initial Σ / independent π sensitivity.

Constructive answer to the scientific degeneracy question, no synthetic
observational covariance and no claimed complete stellar-gravity closure.
Uses EXACT parent PR145 positive canonical FV source and optional actual frozen
312238-row H/He electron donor in a ONE-WAY Thomson (γ only) lane.
"""
from __future__ import annotations
from concurrent.futures import ProcessPoolExecutor
import hashlib,json,math,sys,time,statistics
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
FV=HERE.parent/"rei_bass_hierarchy_backreaction_20261015"/"canonical_fv_20261015"
PARENT=FV.parent
sys.path.insert(0,str(PARENT))
sys.path.insert(0,str(FV))
from canonical_fv import CanonicalFVSpecies
from run_hierarchy import source_lock,actual_electrons,public_sigma_from_q

FV_SHA="91c1641b851aa9580141d4423e2579ced5f11b95aa716b3fc2cb0137df344cc5"
SOURCE_HEAD="54e29dff5a90c0a785cb6dcfb004403614ca403b"
MASS=30.
FM=.1
BASE=np.array([0.,.2,.2,.5],dtype=float)
DELTA=np.array([.001,.02,.02,.05],dtype=float)
PARAM_NAMES=("signed_q_shear","initial_kappa_gamma","initial_kappa_nu","initial_A_massive")
OBS_NAMES=("signed_s_over_H","b","photon_E2","neutrino_E2","massive_Pi_normalized")
OBS_UNITS=("dimensionless","dimensionless","dimensionless","dimensionless","rhocrit_normalized")
# Scaling is a declared *model sensitivity convention*, not observational errors.
OBS_SCALE=np.array([1e-4,1e-4,0.04,0.04,1e-4])

def check_parent():
    p=FV/"canonical_fv.py"
    return hashlib.sha256(p.read_bytes()).hexdigest()

def one(q,kg,kn,Am,donor=None,n=101,rtol=3e-11,atol=3e-13):
    if not all(np.isfinite([q,kg,kn,Am])):raise ValueError("finite")
    if abs(q)>.04 or not(-.5<=kg<=.5 and -.5<=kn<=.5 and -1<=Am<=2):
        raise ValueError("positive physical source / valid signed shear required")
    src=source_lock()
    Sigma,orient=public_sigma_from_q(q)
    obj=CanonicalFVSpecies(src,2.7255,8,Sigma_ref=Sigma,orientation=orient,
        kappa_gamma=kg,kappa_nu=kn,ne_source=donor,mass_fraction=FM,
        massive_A=Am,mass_over_Tref=MASS,radial_cells=24,angular_cells=12,
        subcell_gauss_order=3)
    sol,diag,elapsed=obj.integrate(n=n,rtol=rtol,atol=atol)
    out=np.stack([np.array([float(d["s"]/d["H"]),float(d["b"]),
                 float(d["E_gamma"][2]),float(d["E_nu"][2]),float(d["Pi_matter_norm"])])
               for d in diag])
    if len(out)!=n or not np.isfinite(out).all():raise ArithmeticError("SCIENTIFIC_OUTPUT")
    hres=max(abs(d["Einstein_H2"]/d["H"]**2-1.) for d in diag)
    Ndiff=max(abs(d["N_gamma"][0]-1) for d in diag)
    Ndiff=max(Ndiff,max(abs(d["N_nu"][0]-1) for d in diag))
    minN=min(d["massive_min_cell_population"] for d in diag)
    if hres>2e-13 or Ndiff>2e-10 or minN<0:
        raise ArithmeticError("SOURCE_CONSTRAINT_NUMBER_POSITIVITY")
    return {"obs":out,"x":np.asarray(sol.t),"physical":{
        "Einstein_H2_constraint_max_relative":hres,
        "particle_number_radiation_max":Ndiff,"min_massive_cell_number":minN,
        "nfev":int(sol.nfev),"wall_s":elapsed,
        "Sigma_end":float(diag[-1]["Sigma"]),
        "initial_rad_pi_gamma":float(diag[0]["Pi_gamma_J_m3"]),
        "initial_rad_pi_nu":float(diag[0]["Pi_nu_J_m3"]),
        "initial_pi_massive":float(diag[0]["Pi_matter_J_m3"]),
        "end_pi_gamma":float(diag[-1]["Pi_gamma_J_m3"]),
        "end_pi_nu":float(diag[-1]["Pi_nu_J_m3"]),
        "end_pi_massive":float(diag[-1]["Pi_matter_J_m3"]),
        "signed_Sigma_ref":math.copysign(Sigma,q) if q else 0.}}

def source_inputs():
    return {"base_parameters":dict(zip(PARAM_NAMES,BASE.tolist())),
            "finite_difference_halfstep":dict(zip(PARAM_NAMES,DELTA.tolist())),
            "units_parameters":{"signed_q_shear":"signed s_ref/H_FLRW(a_ref); historical q adapter, not observable Sigma",
             "initial_kappa_gamma":"dimensionless positive massless gamma P2 occupation multiplier",
             "initial_kappa_nu":"dimensionless positive massless nu P2 occupation multiplier",
             "initial_A_massive":"dimensionless positive initial nonbaryonic Fermi-Dirac angular multiplier"},
            "observable_names":OBS_NAMES,"observable_units":OBS_UNITS,
            "observable_scales":OBS_SCALE.tolist(),
            "initial_physical_Sigma":"sqrt(3)*abs(s)/H, sign separate",
            "source_specific_scopes":{"mass_fraction_nonbaryonic":FM,"mass_over_Tref":MASS,
               "photon_unpolarized":True,"massless_nu_no_Thomson":True,
               "massive_collisionless":True,"full_HHe_feedback":False,
               "emitter_and_recombination_radiation_4momentum_complete":False}}

def compute(donor=None,n=101,scale=1.):
    settings=source_inputs()
    base=one(*BASE,donor=donor,n=n)
    paired=[]
    for k in range(4):
        dp=DELTA[k]*scale
        aa=BASE.copy();bb=BASE.copy()
        aa[k]+=dp;bb[k]-=dp
        plus=one(*aa,donor=donor,n=n)
        minus=one(*bb,donor=donor,n=n)
        derivative=(plus["obs"]-minus["obs"])/(2*dp)
        paired.append({"name":PARAM_NAMES[k],
            "plus":plus["physical"],"minus":minus["physical"],
            "derivative":derivative})
    J=np.stack([p["derivative"] for p in paired],axis=-1)
    # Dimensionless standardized derivative w.r.t explicitly declared
    # physical perturbation scales; NOT posterior/Fisher/observational.
    G=J/OBS_SCALE[None,:,None]*DELTA[None,None,:]
    Jend=J[-1]
    Hend=G[-1]
    s=np.linalg.svd(Hend,compute_uv=False)
    # A convenient null vector should only be built when scalar sensitivity
    # to the massive initial anisotropy is nonzero; check explicitly.
    if abs(Jend[0,3])<1e-10:raise ArithmeticError("UNRESOLVED_DEGENERACY_DIRECTION")
    null=np.array([1.,0.,0.,-Jend[0,0]/Jend[0,3]])
    null_s=float(abs(Jend[0]@null))
    return {"source":settings,
      "x":base["x"],"baseline_observable_history":base["obs"],
      "base_physics":base["physical"],
      "pairs":paired,"Jacobian":J,
      "normalized_Jacobian":G,
      "singular_values_normalized_end":s,
      "condition_number_normalized_end":float(s[0]/s[-1]),
      "rank_normalized_end":int(np.linalg.matrix_rank(Hend,tol=s[0]*1e-8)),
      "scalar_null_example":null,
      "scalar_null_product":null_s,
      "solves_per_lane":9}

def concise(c):
    b=c["base_physics"];J=c["Jacobian"][-1];G=c["normalized_Jacobian"][-1]
    return {"baseline_Sigma_end":b["Sigma_end"],"baseline_s_over_H":c["baseline_observable_history"][-1,0],
      "J_final_S":J[0].tolist(),
      "J_final_b":J[1].tolist(),
      "J_final_Egamma2":J[2].tolist(),"J_final_Enu2":J[3].tolist(),
      "J_final_massive_pi":J[4].tolist(),
      "SVD":c["singular_values_normalized_end"].tolist(),
      "rank":c["rank_normalized_end"],
      "condition":c["condition_number_normalized_end"],
      "null_example":c["scalar_null_example"].tolist(),
      "scalar_null_residual":c["scalar_null_product"]}

def run(owner:Path,output:Path):
    if output.exists():raise FileExistsError(output)
    if check_parent()!=FV_SHA:raise RuntimeError("EXACT_PARENT_CANONICAL_SOURCE_SHA_CHANGED")
    start=time.perf_counter()
    obj={}
    # Genuinely distinct study lanes: missing Thomson/actual frozen HHe electrons.
    for name,donor in [("collisionless_gamma_nu",None),("actual_zero_HHe_oneway_thomson",actual_electrons(owner)[0])]:
        coarse=compute(donor,101,1.)
        fine=compute(donor,101,.5)
        j=coarse["Jacobian"]
        jf=fine["Jacobian"]
        norm=abs(j-jf)
        metrics={"max_diff_abs":float(norm.max()),
             "max_row_normalized":float(np.max(norm/(np.max(np.abs(jf),axis=(0,2))[None,:,None]+1e-15))),
             "signed_s_endpoint_response_error":float(np.max(abs(j[-1,0]-jf[-1,0])/(abs(jf[-1,0])+1e-15))),
             "baseline_bytewise_repeat_possible":True}
        obj[name]={"coarse":coarse,"fine":fine,"derivative_consistency":metrics}
    elapsed=time.perf_counter()-start
    # Fail closed on unexpectedly unstable physical derivatives, without
    # widening tolerances solely to get all numbers.
    for name,v in obj.items():
        if v["derivative_consistency"]["signed_s_endpoint_response_error"]>0.015:
            raise ArithmeticError("FINITE_DIFFERENCE_RESPONSE_UNCONVERGED:"+name)
    from hashlib import sha256
    receipt={
      "schema":"rei.bass.sigma_pi.init_response.source_scoped.v1",
      "parent_REI_PR145_sha":SOURCE_HEAD,
      "parent_canonical_src_sha":FV_SHA,
      "actual_HHe_donor_type":"unmodified source ZERO 312238 row original, only one-way gamma Thomson",
      "source_scope":"Einstein LRS Bianchi I gamma+nu energy/number L8, collisionless positive canonical massive, optional one-way native HHe electrons",
      "observables":"signed shear s/H, metric b, gamma/nu E2 quadrupoles, massive pi dimensionless",
      "sensitivity_interpretation":"local numerical derivative, no physical covariance, no observational Fisher posterior",
      "degeneracy":"scalar final shear S has 3-dim local kernel for four IC controls; multi-channel finite toy observables may resolve some directions",
      "numeric_accuracy":"two centered step sizes; empirical finite differences not interval-certified derivatives",
      "external_stellar_source_closed":False,"actual_photoionizing_opacity_pi":False,
      "scalar_inputs":source_inputs(),
      "elapsed_wall_seconds":elapsed,
      "cases":{k:{
          "source_physics":v["coarse"]["base_physics"],
          "coarse":concise(v["coarse"]),
          "fine":concise(v["fine"]),
          "finite_difference_consistency":v["derivative_consistency"],
          "x":v["coarse"]["x"].tolist(),
          "baseline_observables":v["coarse"]["baseline_observable_history"].tolist(),
          "derivatives_full":v["coarse"]["Jacobian"].tolist(),
          "derivatives_half_step":v["fine"]["Jacobian"].tolist()}
        for k,v in obj.items()}}
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps({"status":"COMPLETED_SOURCE_BOUND_RESPONSE",
        "wall_seconds":elapsed,
        "cases":{k:{"coarse":concise(v["coarse"]),"derivative_stability":v["derivative_consistency"]}
                 for k,v in obj.items()}},indent=2))
    return receipt

if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--owner",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    run(args.owner,args.output)
