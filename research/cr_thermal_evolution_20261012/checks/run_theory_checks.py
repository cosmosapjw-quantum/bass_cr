"""Focused R7 checks: exact conservation examples and one 8-state toy IVP.

This is new theory/receiver validation. It does not rebuild a PHYS02 generator,
repeat saved source/transport checks, or execute an astrophysical history.
"""
from fractions import Fraction as F
from pathlib import Path
import ast
import hashlib
import json
import math
import platform
import sys
import time

import numpy as np
import scipy
from scipy.integrate import solve_ivp, quad
from scipy.constants import e, epsilon_0, m_e, hbar

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from receiver_interface import (
    thermal_transfer_tdot, total_moment_tdot, advance_thermal_packet,
    temperature_error_bound, K_B_SI,
)

def main():
    started = time.perf_counter()
    cases = []
    def record(name, passed, **details):
        cases.append(dict(name=name, passed=bool(passed), **details))
        if not passed:
            raise AssertionError(name)

    k = F(2,3)  # Explicit dimensionless analytical fixture: cv=1.
    birth = total_moment_tdot(7, 5, 3, 2, 8, 2, 8, 0, k_B=k)
    record("active_birth_preserves_thermal_temperature", birth == 0,
           value=str(birth), expected="0")
    transfer = thermal_transfer_tdot(2, 3, 5, 1, k_B=k)
    # Differentiate independent solution T(t)=(6+5t)/(2+t) at t=0.
    record("continuous_packet_matches_rational_solution", transfer == 1,
           value=str(transfer), expected="1")
    adiabatic = thermal_transfer_tdot(2, 3, 0, 0, F(1,2), k_B=k)
    record("adiabatic_T_scales_as_V_minus_two_thirds", adiabatic == -1,
           value=str(adiabatic), expected="-1")
    packet = advance_thermal_packet(2, 6, 1, 5, k_B=k)
    removal = advance_thermal_packet(2, 6, -1, -3, k_B=k)
    record("finite_packet_and_reverse_transfer_conserve_energy",
           packet.count == 3 and packet.energy == 11 and
           packet.temperature == F(11,3) and removal.temperature == 3,
           added_temperature=str(packet.temperature),
           removed_temperature=str(removal.temperature))
    eos_bound = temperature_error_bound(2, 1, 2, 2, k_B=k)
    record("temperature_error_bound_has_exact_saturating_example",
           eos_bound == abs(F(8,2)-F(6,3)) == 2,
           bound=str(eos_bound), actual_error="2")
    rejected = 0
    invalid = [
        lambda: advance_thermal_packet(2,6,-2,0,k_B=k),
        lambda: advance_thermal_packet(2,6,0,-7,k_B=k),
        lambda: total_moment_tdot(2,2,3,0,0,0,0,0,k_B=k),
        lambda: thermal_transfer_tdot(2,float("nan"),0,0,k_B=k),
    ]
    for call in invalid:
        try: call()
        except ValueError: rejected += 1
    record("receiver_rejects_nonphysical_endpoint_or_undefined_heat_capacity",
           rejected == len(invalid), rejected=rejected)

    # A pure moving partition of g(W)=1 on the strip [0.1,0.2] eV.
    lo, hi = F(1,10), F(1,5)
    dn, du = hi-lo, (hi*hi-lo*lo)/2
    record("finite_cutoff_strip_conserves_actual_energy",
           dn == F(1,10) and du == F(3,200) and du != hi*dn,
           transferred_number=str(dn), transferred_energy_eV=str(du),
           mean_energy_eV=str(du/dn))
    # One ionization: parent 20 eV = binding13.6 + daughters6.36+0.04.
    parent, binding, fast, slow = F(20), F(68,5), F(159,25), F(1,25)
    record("subcutoff_daughter_energy_and_number_close",
           parent == binding+fast+slow and -parent+fast+binding+slow == 0
           and slow != lo and (2-1)-1 == 0,
           secondary_count=1, active_count_change=0,
           join_energy_eV=str(slow), cutoff_eV=str(lo))
    K, Pi = [F(1),F(2),F(4)], [F(3),F(5),F(2)]
    work = sum(a*b for a,b in zip(K,Pi))
    mean_work = sum(K)*sum(Pi)/3
    shear_work = sum((a-sum(K)/3)*(b-sum(Pi)/3) for a,b in zip(K,Pi))
    record("anisotropic_pressure_work_keeps_shear",
           work == mean_work+shear_work and shear_work != 0,
           full_work=str(work), isotropic_part=str(mean_work),
           shear_part=str(shear_work))

    # Source-pinned stopping function only; no class/generator/source integrator runs.
    original = ROOT/"inputs/prior_code/causal_cascade.py"
    raw = original.read_bytes()
    mod = ast.parse(raw)
    wanted = [n for n in mod.body if isinstance(n, ast.FunctionDef)
              and n.name in {"checked_energy","stopping_eV_s"}]
    assert len(wanted) == 2
    source_subset = ast.Module(body=wanted, type_ignores=[])
    ne0 = .01*(140.+140.*.248/(4*(1-.248)))
    kap = e*e/(4*math.pi*epsilon_0)
    env = dict(np=np, math=math, CUT=.1, UPPER=900., N_E=ne0,
               EV_J=e, epsilon_0=epsilon_0, m_e=m_e, hbar=hbar, KAPPA=kap)
    exec(compile(source_subset,str(original),"exec"),env)
    energies = np.array([.1,1.,10.,100.,900.])
    speed = np.sqrt(2*energies*e/m_e)
    omega = math.sqrt(ne0*e*e/(epsilon_0*m_e))
    pref = 4*math.pi*kap*kap*ne0/(m_e*speed*e)
    max_rel = 0.
    min_logs = {}
    for cq in [0.,-.5]:
        env["N_E"] = ne0
        base = env["stopping_eV_s"](energies,cq)
        logs = np.minimum(np.log(speed*energies*e/(kap*omega)),
                          np.log(2*energies*e/(hbar*omega))+cq)
        min_logs[str(cq)] = float(min(logs))
        for density in [.2,1.,4.]:
            env["N_E"] = density*ne0
            direct = env["stopping_eV_s"](energies,cq)
            decomposed = density*base-.5*density*math.log(density)*pref
            max_rel = max(max_rel,float(np.max(abs(direct-decomposed)/abs(direct))))
    record("actual_stopping_density_log_decomposition",
           max_rel < 2e-14, max_relative_difference=max_rel,
           energies_eV=energies.tolist(), density_factors=[.2,1.,4.],
           min_Coulomb_log_at_cutoff=min_logs,
           prior_source_sha256=hashlib.sha256(raw).hexdigest(),
           executed_scope="two extracted original functions; 30 coefficient values")

    # Dimensionless energy-bin toy with genuinely noncommuting operators.
    G0 = np.array([[-2.,0.],[1.,-1.]])
    C0 = np.array([[-1.,0.],[1.,-.5]])
    h0, hc = np.array([1.,1.]), np.array([0.,.5])
    commutator = G0@C0-C0@G0
    c_norm = float(max(np.sum(abs(C0),axis=0)+abs(hc)))
    record("toy_passivity_and_noncommutation",
           np.allclose(np.ones(2)@G0+h0,0) and
           np.allclose(np.ones(2)@C0+hc,0) and
           np.any(commutator != 0) and c_norm == 2.,
           commutator=commutator.tolist(), augmented_C0_norm=c_norm)

    # d=e^-t, V=e^t, tau=1-e^-t, Ubar=1.
    # Exact density extension A=dG0 + (td/2) C0 and h=d h0+(td/2)hc.
    # States: actual X1,X2,H,U_th ; reference X1,X2,H,U_th.
    def rhs(t,y):
        d = math.exp(-t)
        A = d*G0+.5*t*d*C0
        h = d*h0+.5*t*d*hc
        ra, rr = float(h@y[:2]), float(d*h0@y[4:6])
        return np.r_[A@y[:2],ra,ra-(2/3)*y[3],
                     d*G0@y[4:6],rr,rr-(2/3)*y[7]]
    grid=np.linspace(0.,1.,65)
    sol=solve_ivp(rhs,(0.,1.),[1,0,0,6,1,0,0,6],
                  method="DOP853",rtol=1e-11,atol=1e-13,
                  t_eval=grid,dense_output=True)
    assert sol.success
    tau=1-np.exp(-grid)
    exact_ref=np.vstack([np.exp(-2*tau),
                         np.exp(-tau)-np.exp(-2*tau),
                         1-np.exp(-tau)])
    ref_error=float(np.max(abs(sol.y[4:7]-exact_ref)))
    total_error=np.sum(abs(sol.y[:2]-sol.y[4:6]),axis=0)+abs(sol.y[2]-sol.y[6])
    cert=1-(grid+1)*np.exp(-grid)
    excess=float(np.max(total_error-cert))
    record("exact_collision_clock_matches_independent_toy_IVP",
           ref_error<1e-9, max_absolute_error=ref_error,
           time_map="tau=1-exp(-t)", nfev=sol.nfev)
    record("noncommuting_Duhamel_certificate_covers_toy_state_and_heat",
           excess<1e-10, largest_error_minus_bound=excess,
           endpoint_error=float(total_error[-1]),
           endpoint_bound=float(cert[-1]),
           scope="65-point numerical diagnostic; theorem supplies continuous bound")

    # T.21 used with its full B_H(s), same expansion and initial state.
    mu=math.exp(2/3)
    thermal_bound=cert[-1]+quad(
        lambda s:(2/3)*math.exp(2*s/3)*(1-(s+1)*math.exp(-s)),0,1,
        epsabs=1e-13,epsrel=1e-13)[0]/mu
    thermal_error=abs(float(sol.y[3,-1]-sol.y[7,-1]))
    temp_error=thermal_error/2  # N=2, cv=1.
    temp_bound=float(temperature_error_bound(float(thermal_bound),0,2,
                                             float(sol.y[7,-1]/2),k_B=k))
    record("deposition_to_expanding_thermal_energy_to_temperature",
           thermal_error<=thermal_bound+1e-10 and temp_error<=temp_bound+1e-10,
           endpoint_thermal_energy_error=thermal_error,
           thermal_energy_bound=float(thermal_bound),
           temperature_error=temp_error, temperature_bound=temp_bound)
    # A relative-volume cumulative heat must not be replaced by int p_h dt.
    proper_integral=quad(lambda t: math.exp(-2*t)*math.exp(-(1-math.exp(-t))),
                         0,1,epsabs=1e-13)[0]
    parcel_heat=1-math.exp(-(1-math.exp(-1)))
    record("proper_rate_integral_and_parcel_heat_have_distinct_volume_basis",
           abs(proper_integral-parcel_heat)>1e-3,
           integral_proper_rate=proper_integral, parcel_heat=parcel_heat)

    csv=np.c_[grid,tau,sol.y[2],sol.y[6],total_error,cert,sol.y[3],sol.y[7]]
    np.savetxt(ROOT/"results/TOY_EVOLUTION.csv",csv,delimiter=",",
               header="time,tau,actual_heat,reference_heat,state_plus_heat_error,certificate,actual_thermal_energy,reference_thermal_energy",
               comments="")
    result=dict(
        unit="CR-THEORY-THERMAL-EVOLUTION-20261012",
        method="exact rational analytic fixtures; source-pinned stopping coefficients; one noncommuting 8-state dimensionless IVP",
        passes=sum(c["passed"] for c in cases), total=len(cases),
        cases=cases,
        runtime=dict(python=platform.python_version(),numpy=np.__version__,
                     scipy=scipy.__version__,elapsed_seconds=time.perf_counter()-started,
                     ivp_method="DOP853",rtol=1e-11,atol=1e-13),
        code_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in [Path(__file__),ROOT/"receiver_interface.py",original]},
        reused_prior_transport_runs=0,new_full_generator_builds=0,
        remote_science_jobs=0)
    (ROOT/"results/THEORY_CHECKS.json").write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({k:result[k] for k in ["unit","passes","total","runtime"]},indent=2))
    return result

if __name__=="__main__":
    main()

