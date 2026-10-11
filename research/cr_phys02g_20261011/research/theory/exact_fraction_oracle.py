#!/usr/bin/env python3
"""One-shot exact synthetic oracle for the frozen PHYS02G candidate.

No production implementation or actual E/F numerical input is imported.
Every sharpness witness has at most three atoms; mixed measures have at most six.
Frontier arrays are an algebraic fixture, not a common-G semigroup witness.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys
import traceback

CHECKS: list[dict] = []
MAX_ATOMS = 0


def serial(value):
    if isinstance(value, F):
        return {"numerator": str(value.numerator), "denominator": str(value.denominator), "exact": str(value)}
    if isinstance(value, dict):
        return {str(k): serial(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(v) for v in value]
    return value


def check(name, condition, **details):
    CHECKS.append({"name": name, "pass": bool(condition), **serial(details)})
    if not condition:
        raise AssertionError(name)


def equal(name, got, expected):
    check(name, got == expected, got=got, expected=expected)


def moments(atoms, name):
    global MAX_ATOMS
    MAX_ATOMS = max(MAX_ATOMS, len(atoms))
    check(name + ".finite_support_admitted", len(atoms) <= 8)
    check(name + ".nonnegative", all(x >= 0 and p >= 0 for x, p in atoms))
    equal(name + ".mass", sum((p for _, p in atoms), F(0)), F(1))
    return (sum((p*x for x, p in atoms), F(0)),
            sum((p*x*x for x, p in atoms), F(0)))


def survive(atoms, t):
    return sum((p for x, p in atoms if x > t), F(0))


def bounds(a, b, t):
    if a < 0 or b < 0 or t < 0:
        raise ValueError("negative moment or threshold")
    if a == 0:
        if b != 0:
            raise ValueError("nonnegative mean zero requires second moment zero")
        return F(0), F(0)
    v = b-a*a
    if v < 0:
        raise ValueError("negative variance")
    if v == 0:
        s = F(int(t < a))
        return s, s
    low = (a-t)**2/(v+(a-t)**2) if t < a else F(0)
    if t <= a:
        high = F(1)
    elif t < b/a:
        high = a/t
    else:
        high = v/(v+(t-a)**2)
    return low, high


def lower_poly(a, b, t, x):
    if t >= a:
        return F(0)
    v = b-a*a
    c = a+v/(a-t)
    return 1-((x-c)/(c-t))**2


def upper_poly(a, b, t, x):
    if t <= a:
        return F(1)
    if t < b/a:
        return x/t
    v = b-a*a
    c = a-v/(t-a)
    return ((x-c)/(t-c))**2


def two_point(a, v, low):
    d = a-low
    return [(low, v/(v+d*d)), (a+v/d, d*d/(v+d*d))]


def witness_check(name, atoms, a, b, t):
    got_a, got_b = moments(atoms, name)
    equal(name + ".mean", got_a, a)
    equal(name + ".second", got_b, b)
    s = survive(atoms, t)
    low, high = bounds(a, b, t)
    check(name + ".bounds", low <= s <= high, survival=s, lower=low, upper=high)
    for index, (x, _) in enumerate(atoms):
        indicator = F(int(x > t))
        check(name + f".certificate_at_atom_{index}",
              lower_poly(a,b,t,x) <= indicator <= upper_poly(a,b,t,x),
              x=x, indicator=indicator)
    equal(name + ".lower_certificate_expectation",
          sum((p*lower_poly(a,b,t,x) for x,p in atoms), F(0)), low)
    equal(name + ".upper_certificate_expectation",
          sum((p*upper_poly(a,b,t,x) for x,p in atoms), F(0)), high)
    return s, low, high


def run_witnesses():
    a, b, v = F(2), F(8), F(4)
    for t in [F(0), F(1), F(3,2)]:
        s, low, _ = witness_check("lower_attained_" + str(t), two_point(a,v,t), a,b,t)
        equal("lower_attained_value_" + str(t), s, low)
        s, _, high = witness_check("upper_attained_" + str(t),
                                  two_point(a,v,(a+t)/2), a,b,t)
        equal("upper_attained_value_" + str(t), s, high)
    for t in [F(2), F(3)]:
        previous_upper_gap = previous_lower_gap = None
        for n in [1,4,16,64,256]:
            y, z = t+(b/a-t)/(n+1), b/a+n*a
            py = (a*z-b)/(y*(z-y))
            pz = (b-a*y)/(z*(z-y))
            atoms = [(F(0),1-py-pz),(y,py),(z,pz)]
            s, low, high = witness_check(f"markov_limit_t{t}_n{n}",atoms,a,b,t)
            gap = high-s
            check(f"markov_strict_gap_t{t}_n{n}", gap > 0, gap=gap)
            if previous_upper_gap is not None:
                check(f"markov_approach_t{t}_n{n}", gap < previous_upper_gap)
            previous_upper_gap = gap
            atoms = two_point(a,v,a-a/(n+1))
            s, low, high = witness_check(f"lower_zero_limit_t{t}_n{n}",atoms,a,b,t)
            gap = s-low
            check(f"lower_zero_strict_gap_t{t}_n{n}", gap > 0, gap=gap)
            if previous_lower_gap is not None:
                check(f"lower_zero_approach_t{t}_n{n}", gap < previous_lower_gap)
            previous_lower_gap = gap
    for t in [F(4),F(6)]:
        previous_gap = None
        for n in [1,4,16,64,256]:
            high_atom = t+a/(n+1)
            atoms = two_point(a,v,a-v/(high_atom-a))
            s, low, high = witness_check(f"cantelli_limit_t{t}_n{n}",atoms,a,b,t)
            gap = high-s
            check(f"cantelli_strict_gap_t{t}_n{n}", gap > 0, gap=gap)
            if previous_gap is not None:
                check(f"cantelli_approach_t{t}_n{n}", gap < previous_gap)
            previous_gap = gap
        atoms = [(F(0),1-a*a/b),(b/a,a*a/b)]
        s, low, _ = witness_check("upper_range_zero_lower_"+str(t),atoms,a,b,t)
        equal("upper_range_zero_value_"+str(t),s,low)
    equal("Markov_Cantelli_boundary",a/(b/a),v/(v+(b/a-a)**2))
    equal("strict_threshold_excludes_atom",
          survive([(F(0),F(1,2)),(F(4),F(1,2))],F(4)),F(0))


def run_degenerate():
    for a in [F(0),F(2)]:
        atoms=[(a,F(1))]
        moments(atoms,"deterministic_"+str(a))
        for t in sorted(set([F(0),a/2,a,a+1])):
            low,high=bounds(a,a*a,t)
            equal(f"deterministic_t{t}_a{a}_lower",low,survive(atoms,t))
            equal(f"deterministic_t{t}_a{a}_upper",high,survive(atoms,t))
    for name,args in [
        ("zero_mean_positive_second",(F(0),F(1),F(0))),
        ("negative_variance",(F(2),F(3),F(1))),
        ("negative_mean",(F(-1),F(2),F(1))),
        ("negative_second",(F(1),F(-1),F(1))),
        ("negative_threshold",(F(1),F(2),F(-1)))
    ]:
        caught=False
        try:
            bounds(*args)
        except ValueError:
            caught=True
        check("typed_invalid_"+name,caught)


def censor(atoms,T,name):
    a,b=moments(atoms,name)
    p=sum((prob for x,prob in atoms if x<=T),F(0))
    q=1-p
    R=sum((prob*max(F(0),1-x/T) for x,prob in atoms),F(0))
    S=sum((prob*max(F(0),1-x/T)**2 for x,prob in atoms),F(0))
    r1,r2=a-T*(1-R),b-2*T*a+T*T*(1-S)
    equal(name+".residual_raw_first",r1,
          sum((prob*(x-T) for x,prob in atoms if x>T),F(0)))
    equal(name+".residual_raw_second",r2,
          sum((prob*(x-T)**2 for x,prob in atoms if x>T),F(0)))
    equal(name+".tail_endpoint",survive(atoms,T),q)
    if q==0:
        equal(name+".zero_tail_first",r1,F(0))
        equal(name+".zero_tail_second",r2,F(0))
        return {"a":a,"b":b,"p":p,"q":q,"status":"UNDEFINED_ZERO_TAIL",
                "residual_a":None,"residual_b":None}
    residual=[(x-T,prob/q) for x,prob in atoms if x>T]
    ra,rb=moments(residual,name+".residual_law")
    equal(name+".residual_mean",r1/q,ra)
    equal(name+".residual_second",r2/q,rb)
    equal(name+".positive_support_endpoint",survive(residual,F(0)),F(1))
    return {"a":a,"b":b,"p":p,"q":q,"status":"DEFINED",
            "residual_a":ra,"residual_b":rb}


def residual_bound(row,r):
    if row["q"]==0:
        return F(0),F(0)
    if r==0:
        return row["q"],row["q"]
    low,high=bounds(row["residual_a"],row["residual_b"],r)
    return row["q"]*low,row["q"]*high


def run_censor_mixture():
    T=F(2)
    births=[
        [(F(1),F(1,4)),(F(2),F(1,4)),(F(4),F(1,2))],
        [(F(1,2),F(1,5)),(F(3),F(1,5)),(F(6),F(3,5))]
    ]
    weights=[F(2,5),F(3,5)]
    rows=[censor(atoms,T,"censor_birth_"+str(j)) for j,atoms in enumerate(births)]
    selected=[(x,weights[j]*p) for j,atoms in enumerate(births) for x,p in atoms]
    pooled=censor(selected,T,"censor_selected")
    for key in ["a","b","p","q"]:
        equal("birth_mixture_"+key,
              sum((w*row[key] for w,row in zip(weights,rows)),F(0)),pooled[key])
    for order,key in [(1,"residual_a"),(2,"residual_b")]:
        raw=sum((w*row["q"]*row[key] for w,row in zip(weights,rows)),F(0))
        equal("birth_residual_raw_"+str(order),raw,pooled["q"]*pooled[key])
    q=pooled["q"]
    a,b=pooled["residual_a"],pooled["residual_b"]
    generic=bounds(a,b,F(0))[0]
    check("known_T_endpoint_strictly_improves_generic_lower",q>q*generic,
          q=q,generic=q*generic)
    envelope_rows=[]
    for r in [F(0),F(1,2),F(1),F(2),F(3),F(4),F(5),F(8)]:
        lo_p,hi_p=residual_bound(pooled,r)
        pairs=[residual_bound(row,r) for row in rows]
        lo_b=sum((w*pair[0] for w,pair in zip(weights,pairs)),F(0))
        hi_b=sum((w*pair[1] for w,pair in zip(weights,pairs)),F(0))
        lo_t,hi_t=bounds(pooled["a"],pooled["b"],T+r)
        actual=survive(selected,T+r)
        lo,hi=(q,q) if r==0 else (max(lo_t,lo_p,lo_b),min(hi_t,hi_p,hi_b))
        check("birth_dominates_pool_r"+str(r),lo_b>=lo_p and hi_b<=hi_p,
              lower_birth=lo_b,lower_pool=lo_p,upper_birth=hi_b,upper_pool=hi_p)
        check("censored_intersection_contains_truth_r"+str(r),lo<=actual<=hi,
              lower=lo,actual=actual,upper=hi)
        envelope_rows.append({"residual_t":r,"lower":lo,"upper":hi,"actual":actual})
    for left,right in zip(envelope_rows,envelope_rows[1:]):
        check("censored_monotone_"+str(right["residual_t"]),
              left["lower"]>=right["lower"] and left["upper"]>=right["upper"])
    zero=censor([(T,F(1))],T,"zero_event")
    equal("zero_event_typed",zero["status"],"UNDEFINED_ZERO_TAIL")
    for r in [F(0),F(1)]:
        equal("zero_tail_bounds_"+str(r),residual_bound(zero,r),(F(0),F(0)))
    return {"T":T,"weights":weights,"births":rows,"selected":pooled,"envelopes":envelope_rows}


def run_frontier_algebra():
    laws=[[(F(1),F(1,2)),(F(3),F(1,2))],
          [(F(2),F(3,4)),(F(6),F(1,4))]]
    ab=[moments(law,"frontier_state_"+str(i)) for i,law in enumerate(laws)]
    T0=F(2)
    q0=[F(1,2),F(3,4),F(0)]
    q1=[q0[i]*ab[i][0]/T0 for i in range(2)]+[F(0)]
    q2=[q0[i]*ab[i][1]/(2*T0*T0) for i in range(2)]+[F(0)]
    H0=[F(1),F(2)]
    columns=[[F(1,2),F(1,3),F(2)],[F(1,3),F(2,3),F(0)]]
    birth_weights=[H/sum(H0) for H in H0]
    alphas=[[q0[i]*columns[j][i]/H0[j] for i in range(3)] for j in range(2)]
    selected_alpha=[q0[i]*sum((col[i] for col in columns),F(0))/sum(H0) for i in range(3)]
    for i,(a,b) in enumerate(ab):
        equal("frontier_state_ratio_mean_"+str(i),T0*q1[i]/q0[i],a)
        equal("frontier_state_ratio_second_"+str(i),2*T0*T0*q2[i]/q0[i],b)
    check("frontier_zero_q0_forces_zero_moments",q0[2]==q1[2]==q2[2]==0)
    equal("frontier_zero_heat_skip_count",sum(int(x==0) for x in q0),1)
    for i in range(3):
        equal("selected_alpha_mixture_"+str(i),selected_alpha[i],
              sum((birth_weights[j]*alphas[j][i] for j in range(2)),F(0)))

    def summary(alpha,label):
        mass=sum(alpha,F(0))
        raw1=sum((alpha[i]*ab[i][0] for i in range(2)),F(0))
        raw2=sum((alpha[i]*ab[i][1] for i in range(2)),F(0))
        merged=[(x,alpha[i]*p/mass) for i,law in enumerate(laws) for x,p in law]
        a,b=moments(merged,label)
        equal(label+".weighted_mean",a,raw1/mass)
        equal(label+".weighted_second",b,raw2/mass)
        return {"mass":mass,"a":a,"b":b,"law":merged,"raw1":raw1,"raw2":raw2}

    births=[summary(alpha,"frontier_birth_"+str(j)) for j,alpha in enumerate(alphas)]
    pooled=summary(selected_alpha,"frontier_selected")
    for j,row in enumerate(births):
        for order,(vec,factor,key) in enumerate([
            (q0,F(1),"mass"),(q1,T0,"raw1"),(q2,2*T0*T0,"raw2")]):
            rhs=factor*sum((vec[i]*columns[j][i] for i in range(3)),F(0))/H0[j]
            equal(f"frontier_saved_moment_identity_j{j}_order{order}",row[key],rhs)
    q=pooled["mass"]
    envelope_rows=[]
    for r in [F(0),F(1,2),F(1),F(2),F(3),F(4),F(6),F(10)]:
        if r==0:
            lo_s=hi_s=lo_b=hi_b=lo_p=hi_p=q
        else:
            sb=[bounds(a,b,r) for a,b in ab]
            lo_s=sum((selected_alpha[i]*sb[i][0] for i in range(2)),F(0))
            hi_s=sum((selected_alpha[i]*sb[i][1] for i in range(2)),F(0))
            bb=[bounds(row["a"],row["b"],r) for row in births]
            lo_b=sum((birth_weights[j]*births[j]["mass"]*bb[j][0] for j in range(2)),F(0))
            hi_b=sum((birth_weights[j]*births[j]["mass"]*bb[j][1] for j in range(2)),F(0))
            lo_p0,hi_p0=bounds(pooled["a"],pooled["b"],r)
            lo_p,hi_p=q*lo_p0,q*hi_p0
        actual=q*survive(pooled["law"],r)
        equal("frontier_measure_mixture_r"+str(r),actual,
              sum((selected_alpha[i]*survive(laws[i],r) for i in range(2)),F(0)))
        check("frontier_dominance_r"+str(r),
              lo_s>=lo_b>=lo_p and hi_s<=hi_b<=hi_p,
              frontier=[lo_s,hi_s],birth=[lo_b,hi_b],pooled=[lo_p,hi_p])
        check("frontier_contains_truth_r"+str(r),lo_s<=actual<=hi_s,
              actual=actual,lower=lo_s,upper=hi_s)
        envelope_rows.append({"r":r,"actual":actual,"frontier":[lo_s,hi_s],
                              "birth":[lo_b,hi_b],"pooled":[lo_p,hi_p]})
    return {"fixture_scope":"finite_support_moment_algebra_only_not_common_G_embedding",
            "T0":T0,"q0":q0,"q1":q1,"q2":q2,"H0":H0,"xT_columns":columns,
            "selected_alpha":selected_alpha,"envelopes":envelope_rows}


def run_quantile_endpoints():
    # F(t)=1/2 on [1,3): equality alone cannot make 2 a lower quantile bound.
    atoms=[(F(1),F(1,2)),(F(3),F(1,2))]
    f,t,Q=F(1,2),F(2),F(1)
    c=1-f
    equal("plateau_survival_equals_target",survive(atoms,t),c)
    check("plateau_equality_not_quantile_lower",Q<t,quantile=Q,threshold=t)
    a,b=moments(atoms,"quantile_fixture")
    low,high=bounds(a,b,F(1,2))
    check("strict_survival_lower_implies_quantile_larger",
          low>c and Q>F(1,2),lower=low,c=c)
    low,high=bounds(a,b,F(4))
    check("survival_upper_implies_quantile_upper",
          high<=c and Q<=F(4),upper=high,c=c)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",required=True,type=Path)
    args=parser.parse_args()
    if args.output.exists():
        raise SystemExit("create-only output already exists")
    unit=Path(__file__).resolve().parents[2]
    pins={
        "state/SCIENTIFIC_CONTRACT.json":"517dd569f2e0d0857b37e33a5d90da6475978ab1a43374f3dfbe0323ffb35832",
        "state/VALIDATION_CONTRACT.json":"259d6964154cc190050761db092c9edd5499649867f822003db8afdfa42d9aba",
        "ncp/NCP_EXECUTION_CONTRACT.json":"06a06f865bba44ce93cc3bcf905cf95440de0978e87ee76529d2f440c6065856"
    }
    identity={}
    for rel,expected in pins.items():
        payload=(unit/rel).read_bytes()
        actual=hashlib.sha256(payload).hexdigest()
        if actual!=expected:
            raise SystemExit("frozen contract mismatch: "+rel)
        identity[rel]={"bytes":len(payload),"sha256":actual}
    result={
        "schema":"cr-phys02g-exact-fraction-oracle.v1","status":"RUNNING",
        "role":"candidate_contribution_not_independent_review",
        "source_identity":identity,
        "oracle_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "started_utc":datetime.now(timezone.utc).isoformat(),
        "actual_physical_G":0,"actual_linear_solves":0,"actual_pulse":0,
        "actual_expm":0,"actual_cached_analysis":0
    }
    exit_code=0
    try:
        run_witnesses()
        run_degenerate()
        result["censor_mixture"]=run_censor_mixture()
        result["frontier_algebra"]=run_frontier_algebra()
        run_quantile_endpoints()
        check("max_toy_atoms_within_contract",MAX_ATOMS<=8,max_observed=MAX_ATOMS)
        result["status"]="PASS_EXACT_SYNTHETIC_CANDIDATE_ORACLE"
    except BaseException as exc:
        result["status"]="FAIL_EXACT_SYNTHETIC_CANDIDATE_ORACLE"
        result["exception"]={"type":type(exc).__name__,"message":str(exc)}
        traceback.print_exc(file=sys.stderr)
        exit_code=1
    result["ended_utc"]=datetime.now(timezone.utc).isoformat()
    result["check_count"]=len(CHECKS)
    result["max_atoms_observed"]=MAX_ATOMS
    result["checks"]=CHECKS
    with args.output.open("x",encoding="utf-8") as out:
        json.dump(serial(result),out,ensure_ascii=False,indent=2)
        out.write("\n")
    print(json.dumps({"status":result["status"],"check_count":len(CHECKS),
                      "max_atoms_observed":MAX_ATOMS,"output":str(args.output)},
                     ensure_ascii=False))
    return exit_code


if __name__=="__main__":
    raise SystemExit(main())
