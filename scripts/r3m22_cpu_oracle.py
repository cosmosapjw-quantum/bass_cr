"""Bounded independent dense DOP853 oracle for the opt-in contractive action."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import time

import numpy as np
from scipy.integrate import solve_ivp

from cr_repro.r3m11 import ControlledTDLRunner
from scripts.r3m17_reference import dense_fourier_hamiltonian
from scripts.r3m19_fullh_diagnostic import generator as dense_generator, make_model
from scripts.r3m22_inner_action import BoundedMatrixFreeFullH


def case(shape, cap_on, velocity_sign):
    spacing = .7
    limits = [[-n * spacing / 2, n * spacing / 2] for n in shape]
    cfg = dict(energy_keV_per_u=100., b=.9, backend="numpy", dt=.025,
               grid=dict(zip(("xlim", "ylim", "zlim"), limits), dx=spacing),
               z_start=-2., z_stop=2., initial_state="analytic", project_nmax=1,
               absorber_width=spacing if cap_on else 0., absorber_power=.125,
               absorber_reference_dt=.05, capture_plane=0.)
    runner = ControlledTDLRunner(cfg)
    mf = BoundedMatrixFreeFullH(runner, velocity_override=runner.v * velocity_sign)
    target = np.asarray(runner.Vtarget)
    dense_h = dense_fourier_hamiltonian(shape, spacing, target)
    kinetic = dense_h - np.diag(target.ravel())
    x, y, z = np.meshgrid(*runner.spec.axes(), indexing="ij")
    rho = np.hypot(x-runner.b, y).ravel()
    w = -np.log(np.asarray(runner.mask).ravel())/cfg["absorber_reference_dt"]
    model = make_model(kinetic, target.ravel(), rho, z.ravel(), mf.v, w)
    rng = np.random.default_rng(20260923)
    initial = (rng.normal(size=shape)+1j*rng.normal(size=shape)).astype(np.complex128)
    initial /= math.sqrt(float(np.vdot(initial,initial).real)*runner.dv)
    t0,horizon = -.08,.16

    def ode(max_step):
        count=0
        def rhs(t,state):
            nonlocal count
            count+=1
            if count>20000:
                raise RuntimeError("tiny DOP853 RHS budget exhausted")
            return dense_generator(model,t)@state
        start=time.perf_counter()
        sol=solve_ivp(rhs,(t0,t0+horizon),initial.ravel(),method="DOP853",
                     rtol=4e-14,atol=4e-16,max_step=max_step,t_eval=[t0+horizon])
        if not sol.success or not np.isfinite(sol.y).all():
            raise RuntimeError("independent DOP853 failed")
        return sol.y[:,-1].reshape(shape),dict(rhs=count,wall_seconds=time.perf_counter()-start,max_step=max_step)

    coarse,coarse_info=ode(horizon/16)
    reference,ref_info=ode(horizon/32)
    def dist(a,b):
        return float(np.linalg.norm((a-b).ravel())*math.sqrt(runner.dv))
    def propagate(n,substeps,global_budget):
        state=initial.copy()
        rows=[]
        start=time.perf_counter()
        for j in range(n):
            state,info=mf.cf4_step(state,t0+j*horizon/n,horizon/n,
                                   physical_step_budget=global_budget/n,
                                   action_substeps=substeps,max_basis=16)
            rows.append(info)
        return state,dict(steps=n,action_substeps=substeps,global_budget=global_budget,
                          error_to_ode=dist(state,reference),
                          accumulated_exact_arithmetic_upper_bound=sum(r["accumulated_exact_arithmetic_upper_bound"] for r in rows),
                          max_basis_used=max(a["basis_dimension"] for r in rows for a in r["actions"]),
                          fft_matvecs=sum(r["total_fft_matvec"] for r in rows),
                          wall_seconds=time.perf_counter()-start)
    states={};rows={}
    for n in (4,8,16,32):
        states[str(n)],rows[str(n)]=propagate(n,4,1e-11)
    divided,rows["8_sub8"]=propagate(8,8,1e-11)
    tighter,rows["8_tight"]=propagate(8,4,1e-12)
    distances=dict(reference_repeat=dist(coarse,reference),
                   outer_4_to_8=dist(states["4"],states["8"]),
                   outer_8_to_16=dist(states["8"],states["16"]),
                   outer_16_to_32=dist(states["16"],states["32"]),
                   substep_8_repeat=dist(states["8"],divided),
                   inner_8_repeat=dist(states["8"],tighter))
    threshold=.01*distances["outer_4_to_8"]
    resolved=bool(all(distances[k]<threshold for k in
                      ("reference_repeat","outer_16_to_32","substep_8_repeat","inner_8_repeat")))
    return dict(shape=list(shape),cap_on=cap_on,velocity_sign=velocity_sign,
                source="SAME_PERIODIC_DISCRETE_H_WITH_INDEPENDENT_DENSE_DOP853",
                reference_coarse=coarse_info,reference_fine=ref_info,
                distances=distances,one_percent_threshold=threshold,
                oracle_resolved_at_one_percent=resolved,methods=rows,
                production_admission=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    cases={}
    for name,shape,cap,sign in (("moving64_cap_off",(4,4,4),False,1),
                                ("moving64_cap_on",(4,4,4),True,1),
                                ("reverse64_cap_on",(4,4,4),True,-1),
                                ("rect96_cap_on",(4,4,6),True,1)):
        cases[name]=case(shape,cap,sign)
    result=dict(schema="BASS_CR_R3M22_CPU_ORACLE_V1",cases=cases,
                all_oracle_resolved=all(v["oracle_resolved_at_one_percent"] for v in cases.values()),
                reference_semantics="TINY_DISCRETE_H_ONLY_NO_CONTINUUM_OR_PRODUCTION_ADMISSION")
    with args.out.open("x") as stream:
        json.dump(result,stream,indent=2,sort_keys=True,allow_nan=False);stream.write("\n")
    print(json.dumps({k:v["oracle_resolved_at_one_percent"] for k,v in cases.items()},sort_keys=True))


if __name__=="__main__":
    main()
