"""R3M19 bounded full-H temporal diagnosis in atomic units.

Same periodic Fourier H_h(t)-iW only; this is not a continuum or production
collision test. Frozen source is unchanged. Full exponentials are never
replaced by inner Strang products. CAP is constant in time, spatially varying.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import time
from pathlib import Path

import numpy as np
import scipy
from scipy.integrate import solve_ivp
from scipy.linalg import expm

from cr_repro.r3m11 import ControlledTDLRunner, source_digest
from scripts.r3m17_reference import (FROZEN_SOURCE, _array_sha, dense_fourier_hamiltonian,
                                     stable_phase_metrics, write_new)

MAX_POINTS = 512
MAX_STEPS = 64
MAX_RHS = 20000
MAX_HORIZON = 2.0
CF_A = (3+2*math.sqrt(3))/12
CF_B = (3-2*math.sqrt(3))/12
CF_C1 = .5-math.sqrt(3)/6
CF_C2 = .5+math.sqrt(3)/6


def _finite(value, name):
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"finite {name} required")
    return value


def _positive(value, name):
    value = _finite(value, name)
    if value <= 0:
        raise ValueError(f"positive {name} required")
    return value


def _validate_interval(t0, t1):
    t0,t1 = _finite(t0,"t0"),_finite(t1,"t1")
    if not 0 < t1-t0 <= MAX_HORIZON:
        raise ValueError("ordered interval with horizon <=2 atomic times required")
    return t0,t1


def projectile_integral(rho, z, velocity, t0, t1):
    """Exact integral of -1/sqrt(rho^2+(z-vt)^2), rho strictly positive.

    Equivalent to [asinh((z-vt1)/rho)-asinh((z-vt0)/rho)]/v.
    The 2*atanh identity avoids subtraction and has a stable v -> 0 limit.
    No soft-core or approximation to the Coulomb Hamiltonian is introduced.
    """
    t0,t1 = _validate_interval(t0,t1)
    velocity = _finite(velocity,"velocity")
    rho,z = np.asarray(rho,dtype=float),np.asarray(z,dtype=float)
    if rho.shape != z.shape or not np.isfinite(rho).all() or not np.isfinite(z).all() or np.any(rho <= 0):
        raise ValueError("matching finite arrays and rho>0 required")
    q0,q1 = z-velocity*t0,z-velocity*t1
    rsum = np.hypot(rho,q0)+np.hypot(rho,q1)
    x = -velocity*(t1-t0)/rsum
    if not np.isfinite(x).all() or np.any(abs(x)>=1):
        raise ValueError("integral unresolved at singular/roundoff travel scale")
    ratio = np.divide(np.arctanh(x),x,out=np.ones_like(x),where=x!=0)
    return -2*(t1-t0)*ratio/rsum


def make_model(kinetic, target, rho, z, velocity, W):
    # Gate dimensions before converting a list or constructing any dense copy.
    if not 1 <= len(kinetic) <= MAX_POINTS:
        raise MemoryError("dense model hard limit is 512 points")
    K = np.asarray(kinetic,dtype=complex)
    if K.ndim != 2 or K.shape[0] != K.shape[1] or not np.isfinite(K).all():
        raise ValueError("finite square kinetic matrix required")
    n = K.shape[0]
    if np.linalg.norm(K-K.conj().T) > 64*np.finfo(float).eps*n*max(1,np.linalg.norm(K)):
        raise ValueError("Hermitian kinetic matrix required")
    arrays = [np.asarray(a,dtype=float) for a in (target,rho,z,W)]
    if any(a.shape != (n,) or not np.isfinite(a).all() for a in arrays):
        raise ValueError("finite matching diagonal arrays required")
    target,rho,z,W = arrays
    if np.any(rho<=0):
        raise ValueError("strict rho>0 excludes projectile nuclear grid singularity")
    if np.any(W<0):
        raise ValueError("CAP rate must be nonnegative, no antidamping")
    return dict(K=K,target=target,rho=rho,z=z,velocity=_finite(velocity,"velocity"),W=W)


def generator(model, t):
    t = _finite(t,"time")
    V = model["target"]-1/np.hypot(model["rho"],model["z"]-model["velocity"]*t)
    return -1j*(model["K"]+np.diag(V))-np.diag(model["W"])


def _state_step_args(model, psi, t0, dt):
    t0 = _finite(t0,"time")
    dt = _positive(dt,"dt")
    _validate_interval(t0,t0+dt)
    psi = np.asarray(psi,dtype=complex)
    if psi.shape != (len(model["target"]),) or not np.isfinite(psi).all() or np.vdot(psi,psi).real<=0:
        raise ValueError("finite nonzero state of matching dimension required")
    return psi,t0,dt


def midpoint_step(model, psi, t0, dt):
    psi,t0,dt = _state_step_args(model,psi,t0,dt)
    return expm(dt*generator(model,t0+.5*dt))@psi


def averaged_step(model, psi, t0, dt):
    psi,t0,dt = _state_step_args(model,psi,t0,dt)
    phase = dt*model["target"]+projectile_integral(model["rho"],model["z"],model["velocity"],t0,t0+dt)
    integrated = -1j*(dt*model["K"]+np.diag(phase))-np.diag(dt*model["W"])
    return expm(integrated)@psi


def cf4_step(model, psi, t0, dt):
    """Two full exponentials, Alvermann--Fehske arXiv:1102.5071 Eq.61.

    Rightmost/early action uses a*A1+b*A2; late action b*A1+a*A2.
    a+b=1/2, hence each factor has dissipative -dt*W/2 for constant W.
    """
    psi,t0,dt = _state_step_args(model,psi,t0,dt)
    A1,A2 = generator(model,t0+CF_C1*dt),generator(model,t0+CF_C2*dt)
    early = expm(dt*(CF_A*A1+CF_B*A2))@psi
    return expm(dt*(CF_B*A1+CF_A*A2))@early


def dop853_reference(model, psi, t0, t1, dv, *, rtol=4e-14, atol=4e-16, max_rhs=MAX_RHS):
    t0,t1 = _validate_interval(t0,t1)
    dv = _positive(dv,"dv")
    rtol,atol = _positive(rtol,"rtol"),_positive(atol,"atol")
    if isinstance(max_rhs,bool) or not isinstance(max_rhs,int) or not 1<=max_rhs<=MAX_RHS:
        raise ValueError("RHS budget must be integer <=20000")
    psi,_,_ = _state_step_args(model,psi,t0,t1-t0)
    norm0 = float(np.vdot(psi,psi).real*dv)
    count = 0
    def rhs(t, augmented):
        nonlocal count
        count += 1
        if count>max_rhs:
            raise RuntimeError("DOP853 bounded RHS budget exhausted")
        state = augmented[:-1]
        sampled = model["target"]-1/np.hypot(model["rho"],model["z"]-model["velocity"]*t)
        dst = -1j*(model["K"]@state+sampled*state)-model["W"]*state
        loss = 2*np.sum(model["W"]*abs(state)**2)*dv
        return np.concatenate((dst,np.array([loss],dtype=complex)))
    before = time.perf_counter()
    sol = solve_ivp(rhs,(t0,t1),np.concatenate((psi,[0j])),method="DOP853",
                    rtol=rtol,atol=atol,t_eval=[t1])
    elapsed = time.perf_counter()-before
    if not sol.success or sol.t[-1]!=t1 or not np.isfinite(sol.y).all():
        raise RuntimeError(f"full-H DOP853 failed: {sol.message}")
    final = sol.y[:-1,-1]
    loss = complex(sol.y[-1,-1])
    if abs(loss.imag)>1e-13:
        raise ValueError("CAP ledger integral developed an imaginary component")
    norm1 = float(np.vdot(final,final).real*dv)
    return {"state":final,"norm_initial":norm0,"norm_final":norm1,
            "absorbed_probability":loss.real,"cap_balance_residual":norm1+loss.real-norm0,
            "nfev":sol.nfev,"wall_seconds":elapsed,"rtol":rtol,"atol":atol,
            "max_rhs_budget":max_rhs,"reference_type":"EMPIRICAL_TIGHTENED_DOP853_NOT_CERTIFIED"}


def decompose_vectors(S, E_mid, E_avg, U, dv):
    dv = _positive(dv,"dv")
    arrays = [np.asarray(a,dtype=complex) for a in (S,E_mid,E_avg,U)]
    if any(a.ndim!=1 or a.shape!=arrays[0].shape or not np.isfinite(a).all() for a in arrays):
        raise ValueError("matching finite raw state vectors required")
    S,E_mid,E_avg,U = arrays
    names = ("split","midpoint_quadrature","time_ordering")
    errors = [S-E_mid,E_mid-E_avg,E_avg-U]
    gram = np.array([[np.vdot(a,b)*dv for b in errors] for a in errors])
    total = S-U
    direct = float(np.vdot(total,total).real*dv)
    reconstructed = float(np.sum(gram).real)
    return {
        "semantics":"ACCUMULATED_SAME_INITIAL_SAME_HORIZON_RAW_VECTOR_TELESCOPE",
        "phase_alignment_used_for_decomposition":False,
        "component_norms":{name:float(math.sqrt(gram[i,i].real)) for i,name in enumerate(names)},
        "complex_gram":{f"{a},{b}":[float(gram[i,j].real),float(gram[i,j].imag)] for i,a in enumerate(names) for j,b in enumerate(names)},
        "real_cross_terms_twice":{f"{names[i]},{names[j]}":float(2*gram[i,j].real) for i in range(3) for j in range(i+1,3)},
        "raw_component_vectors":{name:np.column_stack((e.real,e.imag)).tolist() for name,e in zip(names,errors)},
        "total_raw_error_norm":math.sqrt(direct),"direct_squared_norm":direct,
        "reconstructed_squared_norm":reconstructed,"squared_norm_closure_residual":reconstructed-direct,
        "vector_closure_norm":float(np.linalg.norm(sum(errors)-total)*math.sqrt(dv)),
    }


def _budget(shape,spacing,horizon,steps,center,cap_on,b):
    if len(shape)!=3 or any(isinstance(n,(bool,np.bool_)) or not isinstance(n,(int,np.integer)) or n<2 or n%2 for n in shape):
        raise ValueError("three positive even dimensions required")
    if math.prod(shape)>MAX_POINTS:
        raise MemoryError("dense diagnostic hard limit 512 points")
    spacing = _positive(spacing,"spacing")
    horizon = _positive(horizon,"horizon")
    if horizon>MAX_HORIZON:
        raise ValueError("diagnostic horizon budget <=2 required")
    center = _finite(center,"center")
    b = _finite(b,"impact parameter")
    if not isinstance(cap_on,(bool,np.bool_)):
        raise ValueError("cap_on must be Boolean")
    if len(steps)!=3 or any(isinstance(n,bool) or not isinstance(n,(int,np.integer)) or not 1<=n<=MAX_STEPS for n in steps):
        raise ValueError("three integer step counts <=64 required")
    if steps[1]!=2*steps[0] or steps[2]!=2*steps[1]:
        raise ValueError("exact factor-two temporal ladder required")
    return tuple(int(n) for n in shape),spacing,horizon,tuple(int(n) for n in steps),center,b


def run_case(shape=(4,4,4),spacing=.7,horizon=.2,steps=(4,8,16),center=0.,cap_on=False,b=.9):
    shape,spacing,horizon,steps,center,b = _budget(shape,spacing,horizon,steps,center,cap_on,b)
    if source_digest()!=FROZEN_SOURCE:
        raise ValueError("frozen scientific source mismatch")
    t0,t1 = center-horizon/2,center+horizon/2
    from cr_repro.observables import projectile_speed_au
    velocity = projectile_speed_au(100.)
    # Common start/end definitions for every solver and every ladder level.
    limits = [[-n*spacing/2,n*spacing/2] for n in shape]
    cfg = dict(energy_keV_per_u=100.,b=b,backend="numpy",dt=float(np.nextafter(horizon/steps[0],math.inf)),
               grid=dict(zip(("xlim","ylim","zlim"),limits),dx=spacing),z_start=velocity*t0,z_stop=velocity*t1,
               absorber_width=spacing if cap_on else 0.,absorber_power=.125,absorber_reference_dt=.05,
               initial_state="analytic",project_nmax=1,capture_plane=0.)
    first = ControlledTDLRunner(cfg)
    # Runner's computed endpoints and integer scheduling are authoritative.
    t0,t1 = first.t0,first.tf
    duration = t1-t0
    Htarget = dense_fourier_hamiltonian(shape,spacing,np.asarray(first.Vtarget))
    kinetic = Htarget-np.diag(np.asarray(first.Vtarget).ravel())
    _,basis = np.linalg.eigh(Htarget)
    initial = basis[:,0]/math.sqrt(first.dv)
    X,Y,Z = np.meshgrid(*first.spec.axes(),indexing="ij")
    rho = np.hypot(X.ravel()-b,Y.ravel())
    W = -np.log(np.asarray(first.mask).ravel())/cfg["absorber_reference_dt"]
    model = make_model(kinetic,np.asarray(first.Vtarget).ravel(),rho,Z.ravel(),velocity,W)
    references = [dop853_reference(model,initial,t0,t1,first.dv,rtol=r,atol=a) for r,a in ((2e-12,2e-14),(4e-14,4e-16))]
    reference = references[-1]
    U = reference["state"]
    repeat = stable_phase_metrics(references[0]["state"],U,first.dv)
    ladder = []
    for count in steps:
        nominal = float(np.nextafter(duration/count,math.inf))
        local = ControlledTDLRunner(dict(cfg,dt=nominal))
        if local.nstep != count or local.t0!=t0 or local.tf!=t1:
            raise ValueError("integer step scheduling failed to close common horizon")
        dt = local.dt_actual
        states = {name:initial.copy() for name in ("S_mid","E_mid","E_avg","CF4_fullH")}
        norm0 = float(np.vdot(initial,initial).real*first.dv)
        methods = {}
        for name in states:
            start = time.perf_counter()
            state = initial.copy()
            max_increase = 0.
            oldnorm = norm0
            for j in range(count):
                when = t0+j*dt
                if name=="S_mid":
                    state = local.step(state.reshape(shape),when+.5*dt).ravel()
                else:
                    action = {"E_mid":midpoint_step,"E_avg":averaged_step,"CF4_fullH":cf4_step}[name]
                    state = action(model,state,when,dt)
                now = float(np.vdot(state,state).real*first.dv)
                max_increase = max(max_increase,now-oldnorm)
                oldnorm = now
            elapsed = time.perf_counter()-start
            states[name] = state
            metric = stable_phase_metrics(U,state,first.dv)
            methods[name] = {"raw_state_error":metric["unaligned_state_distance"],
                             "ray_error":metric["ray_distance"],"norm_initial":norm0,"norm_final":oldnorm,
                             "norm_error_vs_reference":oldnorm-reference["norm_final"],
                             "maximum_step_norm_increase":max_increase,"wall_seconds":elapsed,
                             "dense_exponential_calls":count*(2 if name=="CF4_fullH" else 1) if name!="S_mid" else 0,
                             "FFT_calls":2*count if name=="S_mid" else 0,"rhs_evaluations":0}
        decomposition = decompose_vectors(states["S_mid"],states["E_mid"],states["E_avg"],U,first.dv)
        ladder.append({"requested_dt":nominal,"actual_dt":dt,"nstep":count,
                       "physical_start_time":t0,"physical_end_time":t1,"same_initial_sha256":_array_sha(initial),
                       "methods":methods,"decomposition":decomposition})
    orders = {}
    for name in ("S_mid","E_mid","E_avg","CF4_fullH"):
        err = [row["methods"][name]["raw_state_error"] for row in ladder]
        orders[name] = [math.log(err[j]/err[j+1])/math.log(ladder[j]["actual_dt"]/ladder[j+1]["actual_dt"])
                        if min(err[j:j+2])>1e-13 else None for j in range(2)]
    finest = min(method["raw_state_error"] for method in ladder[-1]["methods"].values())
    return {
        "scope":"TINY_SAME_PERIODIC_H_h(t)_MINUS_iW_TEMPORAL_ONLY",
        "production_admission":False,"continuum_spatial_validation":False,"production_collision":False,
        "shape":list(shape),"spacing_a0":spacing,"energy_keV_per_u":100.,"b_a0":b,
        "center_time":center,"physical_start_time":t0,"physical_end_time":t1,
        "cap_on":bool(cap_on),"CAP_constant_in_time":True,"CAP_uniform_in_space":bool(np.all(W==W[0])),
        "CAP_reference_dt":.05,"CAP_rate_range_Eh":[float(W.min()),float(W.max())],
        "CAP_mask_sha256":_array_sha(first.mask),"numerical_source_digest":source_digest(),
        "initial_state":"EXACT_DISCRETE_TARGET_GROUND_EIGENSTATE",
        "initial_sha256":_array_sha(initial),"kinetic_sha256":_array_sha(kinetic),"CAP_rate_sha256":_array_sha(W),
        "projectile_minimum_transverse_distance_a0":float(rho.min()),
        "reference":{k:v for k,v in reference.items() if k!="state"},
        "reference_coarse":{k:v for k,v in references[0].items() if k!="state"},
        "reference_repeat_raw_distance":repeat["unaligned_state_distance"],
        "reference_refinement_resolved":bool(repeat["unaligned_state_distance"]<.01*finest),
        "reference_resolution_rule":"tightened_repeat_raw_difference < 0.01 * smallest_finest_method_error; empirical only",
        "observed_orders":orders,"ladder":ladder,
    }


def run_suite(shape=(4,4,4),spacing=.7,horizon=.2,steps=(4,8,16)):
    # Validate all bounded dimensions before constructing the first runner.
    _budget(shape,spacing,horizon,steps,0.,False,.9)
    cases = {}
    for label,center in (("incoming",-.3),("closest",0.),("outgoing",.3)):
        for cap in (False,True):
            name = f"{label}_cap_{'on' if cap else 'off'}"
            cases[name] = run_case(shape,spacing,horizon,steps,center,cap)
    return {
        "schema":"BASS_CR_R3M19_FULLH_TEMPORAL_DIAGNOSTIC_V1","status":"COMPLETE",
        "atomic_units":True,"production_admission":False,"continuum_spatial_validation":False,
        "claim_scope":"BOUNDED_SAME_DISCRETIZATION_TEMPORAL_DECOMPOSITION_ONLY",
        "source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "numerical_source_digest":source_digest(),
        "CF4_coefficients":{"early_weight":CF_A,"late_negative_weight":CF_B,"c1":CF_C1,"c2":CF_C2,
                            "each_exponential_CAP_duration_fraction":CF_A+CF_B},
        "runtime":{"python":platform.python_version(),"numpy":np.__version__,"scipy":scipy.__version__,
                   "platform":platform.platform(),"backend":"CPU_numpy_scipy",
                   "OPENBLAS_NUM_THREADS":os.environ.get("OPENBLAS_NUM_THREADS"),
                   "OMP_NUM_THREADS":os.environ.get("OMP_NUM_THREADS"),"GPU_executed":False},
        "budgets":{"max_points":MAX_POINTS,"max_steps_per_method":MAX_STEPS,"max_rhs_per_oracle":MAX_RHS,
                   "max_horizon":MAX_HORIZON,"estimated_dense_working_bytes":12*16*math.prod(shape)**2},
        "timing_semantics":"SINGLE_CPU_RUN_LOCAL_WORK_PRECISION_ONLY_NOT_GPU_SPEEDUP_EVIDENCE",
        "cases":cases,
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",required=True,type=Path)
    parser.add_argument("--shape",nargs=3,type=int,default=[4,4,4])
    parser.add_argument("--spacing",type=float,default=.7)
    parser.add_argument("--horizon",type=float,default=.2)
    parser.add_argument("--coarse-steps",type=int,default=4)
    args=parser.parse_args()
    if args.out.exists():
        raise FileExistsError(args.out)
    report=run_suite(args.shape,args.spacing,args.horizon,tuple(args.coarse_steps*2**j for j in range(3)))
    write_new(args.out,report)
    print(json.dumps({"status":"COMPLETE","cases":len(report["cases"]),"output":str(args.out),"production_admission":False}))


if __name__=="__main__":
    main()
