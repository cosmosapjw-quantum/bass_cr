"""Stage-separated build, controls, native, independent and saved-plot jobs."""
from pathlib import Path
from fractions import Fraction as F
import dataclasses
import hashlib
import importlib
import json
import os
import py_compile
import subprocess
import sys

UNIT = Path(__file__).resolve().parents[1]
REPO = UNIT.parents[1]
EXE = UNIT / "bin/integer_flow"
INPUT_PINS = {
    "ATTRIBUTION_ARRAYS.npz": "1c974c306b50f3deb86df712844f753b4402fb25e5dbc41c9a1de0254bf3ff47",
    "PR114_SELECTED_WITNESSES.json": "ae09b3183cbf7f16bb89983fa5f649a65e284b2d4a4042f9d424d0fe5566f8e5",
    "PR115_K20_WITNESS.json": "0cc7d56e82ef3fcab3913f24ed7b69e4e87a123da3727f54afdce960e457c775",
    "PR115_SAVED_BOUNDS.json": "9c9359a570de873ff6a7ad172ae2a95a1b3d3c2552bbbb80e7239c474fbeba01",
}
CONSUMER_SHA = "6b1813ccca95cf3843a217132933db373590b9580d7b1160964468e0351b286d"
W, NB = F(10**20, 2), F(8750, 47)


def serial(x):
    if isinstance(x, F):
        return str(x)
    if dataclasses.is_dataclass(x):
        return serial(dataclasses.asdict(x))
    if isinstance(x, dict):
        return {str(k): serial(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [serial(v) for v in x]
    return x


def write(path, value, compact=False):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(serial(value), indent=None if compact else 2,
                                   separators=(",", ":") if compact else None,
                                   allow_nan=False) + "\n")
    temporary.replace(path)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pin_inputs():
    for name, expected in INPUT_PINS.items():
        if sha(UNIT / "inputs" / name) != expected:
            raise ValueError("INPUT_IDENTITY_MISMATCH:" + name)


def build(out):
    EXE.parent.mkdir(exist_ok=True)
    command = ["g++", "-std=c++17", "-O2", str(UNIT / "implementation/integer_flow.cpp"), "-o", str(EXE)]
    write(out / "BUILD_COMMAND.json", {"argv": command})
    subprocess.run(command, check=True)
    sources = sorted((UNIT / "implementation").glob("*.py")) + sorted((UNIT / "reference").glob("*.py"))
    for path in sources:
        py_compile.compile(str(path), doraise=True)
    return {"status": "PASS_BUILD", "cpp_executable_sha256": sha(EXE), "cpp_executable_bytes": EXE.stat().st_size,
            "python_sources_compiled": len(sources), "compiler": subprocess.check_output(["g++", "--version"], text=True).splitlines()[0],
            "science_claim": "Build and syntax only; implementation controls and native science not yet run"}


def hull(points):
    pts = sorted(set(points))
    if len(pts) <= 1:
        return tuple(pts)
    def cross(o, a, b):
        return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    lo, hi = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(hi) >= 2 and cross(hi[-2], hi[-1], p) <= 0:
            hi.pop()
        hi.append(p)
    return tuple(lo[:-1]+hi[:-1])


def controls(out):
    import joint_region as jr
    import cpp_backend as cb
    sys.path.insert(0, str(UNIT / "reference"))
    oracle = importlib.import_module("exact_oracle")
    checks, cases = [], []
    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        checks.append(name)
    def reject(name, fn):
        try:
            fn()
        except (ValueError, TypeError, OverflowError):
            checks.append(name)
        else:
            raise AssertionError("EXPECTED_REJECTION:"+name)
    fixtures = [
        ("empty", [], F(0)),
        ("zero", [("z", F(0), F(0), 0)], F(0)),
        ("one_low", [("a", F(1,2), F(3), 0)], F(1)),
        ("one_high", [("h", F(2), F(1), 0)], F(1)),
        ("M_zero", [("a", F(1,5), F(2), 0), ("b", F(2,5), F(1), 1)], F(1)),
        ("XM_XD", [("a", F(2,5), F(1), 0), ("h", F(7,5), F(1), 1)], F(2)),
        ("equality", [("a", F(1), F(1), 0), ("h", F(2), F(1), 1)], F(3)),
        ("below_equality", [("a", F(1), F(1), 0), ("h", F(2), F(1), 1)], F(299,100)),
        ("pentagon", [("a", F(1,2), F(3), 0), ("b", F(1), F(1), 1), ("h", F(2), F(1), 2)], F(3)),
        ("repair", [("a", F(7,5), F(3), 0), ("b", F(1,2), F(1), 1), ("c", F(7,5), F(1), 2), ("h", F(2), F(1), 0)], F(3)),
        ("fractional", [("a", F(1,2), F(1,3), 0), ("b", F(1), F(2,5), 1), ("h", F(2), F(1,7), 2)], F(3)),
        ("zero_forbidden", [("a", F(2,5), F(1), 0), ("h", F(7,5), F(0), 0)], F(2)),
    ]
    regions = {}
    for name, rows, cap in fixtures:
        atoms = tuple(jr.Atom(*row) for row in rows)
        region = jr.solve(atoms, cap, cpp_executable=EXE)
        regions[name] = region
        raw = [dict(key=a.key, energy_eV=a.energy_eV, coefficient=a.coefficient, partition=a.partition) for a in atoms]
        independent = oracle.enumerate_projection(raw, cap)
        proposed = hull([(F(0),F(0)), (region.L/2,F(0)), (region.D,region.M), (region.D,region.X), (region.X,region.X)])
        check(name+":hull", set(proposed) == set(map(tuple, independent["hull"])))
        check(name+":D", region.D == independent["dmax"])
        check(name+":X", region.X == independent["cmax"])
        targets = set(proposed)
        for c in {F(0), region.M, region.X, (region.M+region.X)/2}:
            upper = min(region.D,(region.L+c)/2)
            targets.update({(c,c),(upper,c),((c+upper)/2,c)})
        for d, c in sorted(targets):
            measure = jr.mix_at(region,d,c)
            m = jr.metrics(atoms,cap,measure)
            check(name+":target:"+str((d,c)), m["d"]==d and m["C"]==c)
        cases.append({"name":name,"atoms":len(atoms),"K":cap,"D":region.D,"X":region.X,
                      "hull":proposed,"oracle_bases_checked":independent["bases_checked"],"targets":len(targets)})
    region=regions["repair"]
    bad_g={("a","b"):F(1),("a","c"):F(1),("a",):F(1),("h",):F(1)}
    check("repair:initial_HL_zero",jr.metrics(region.atoms,region.K,bad_g)["HL"]==0)
    repaired=jr.assemble(region.atoms,region.K,region.D,region.X,region.vertices["B"],bad_g,cpp_executable=EXE)
    fm=jr.metrics(region.atoms,region.K,repaired.vertices["F"])
    check("repair:common_optimum",fm["d"]==3 and fm["C"]==2 and fm["HL"]==1)
    cases.append({"name":"forced_residual_exchange","metadata":repaired.metadata,"D":F(3),"X":F(2),"HL_before":F(0),"HL_after":fm["HL"]})
    bad=(jr.Atom("a",F(2,5),F(1),0),jr.Atom("h",F(7,5),F(1),0))
    check("same_bin_domain_report",jr.domain_report(bad,F(2))["valid"] is False)
    reject("same_bin_solve_rejected",lambda:jr.solve(bad,F(2),cpp_executable=EXE))
    p=regions["pentagon"]
    reject("coupled_facet_target",lambda:jr.mix_at(p,p.D,F(0)))
    reject("target_cross_exceeds_double",lambda:jr.mix_at(p,F(0),F(1)))
    reject("target_float",lambda:jr.mix_at(p,0.5,F(0)))
    reject("target_bool",lambda:jr.mix_at(p,True,F(0)))
    reject("negative_cap",lambda:jr.domain_report(p.atoms,F(-1)))
    reject("duplicate_atom_key",lambda:jr.domain_report((p.atoms[0],p.atoms[0]),p.K))
    altered=dict(p.vertices["O"]);key=next(iter(altered));altered[key]+=1
    reject("marginal_corruption",lambda:jr.metrics(p.atoms,p.K,altered))
    altered2=dict(p.vertices["O"]);altered2[next(iter(altered2))]=F(-1)
    reject("negative_event",lambda:jr.metrics(p.atoms,p.K,altered2))
    hi=(jr.Atom("u",F(6,5),F(1),0),jr.Atom("v",F(13,10),F(1),1))
    reject("support_corruption",lambda:jr.metrics(hi,F(2),{("u","v"):F(1)}))
    large=(jr.Atom("a",F(0),F(2**64),0),jr.Atom("b",F(0),F(2**64),1))
    large_sol=cb.solve(large,F(0),EXE)
    check("exact_capacity_above_uint64",large_sol.cross_C==2**64 and large_sol.flow_value==2**65)
    huge=(jr.Atom("a",F(0),F(2**126),0),jr.Atom("b",F(0),F(1),1))
    reject("capacity_range_rejection",lambda:cb.solve(huge,F(0),EXE))
    invalid_payload="BASS_CR_INTEGER_FLOW_V1\n2 1 0 1 "+str(2**126)+"\n0 1 1\n"
    cli=subprocess.run([str(EXE)],input=invalid_payload,text=True,capture_output=True)
    check("cpp_parser_overflow_rejection",cli.returncode==3 and "OVERFLOW" in cli.stderr)
    fake=out/"fake_zero_flow_backend.py"
    fake.write_text("#!"+sys.executable+"\nimport sys\nlines=sys.stdin.read().splitlines()\nn,m,s,t,b=lines[1].split()\nprint(lines[0])\nprint(n,m,0,0,0)\nprint('\\n'.join(['0']*int(m)))\n")
    fake.chmod(0o700)
    original_method=cb.cf._Network.max_flow
    try:
        cb.solve(large,F(0),fake)
    except ValueError as exc:
        check("corrupt_backend_mincut_rejected","CPP_RESIDUAL_MINCUT_CERTIFICATE_FAILED" in str(exc))
    else:
        raise AssertionError("CORRUPT_BACKEND_ACCEPTED")
    check("backend_restored_after_failure",cb.cf._Network.max_flow is original_method and cb._PATCH_ACTIVE is False)
    write(out/"CASES.json",cases)
    write(out/"CHECKS.json",checks)
    return {"status":"PASS_EXACT_IMPLEMENTATION_CONTROLS","checks_passed":len(checks),"checks_total":len(checks),
            "oracle_fixture_count":len(fixtures),"oracle_basis_count":sum(c.get("oracle_bases_checked",0) for c in cases),
            "forced_residual_exchange":"PASS","cpp_above_64bit":"PASS","range_guard":"PASS",
            "corrupt_backend_rejected":"PASS","backend_restored_after_failure":"PASS","native_source_execution":False}


def read_measure(records):
    answer={}
    for r in records:
        keys=tuple(sorted(r["electrons"]));value=F(r["coefficient"])
        answer[keys]=answer.get(keys,F(0))+value
    return {k:v for k,v in sorted(answer.items()) if v}


def native(out):
    pin_inputs()
    import joint_region as jr
    sys.path.insert(0,str(REPO/"research/cr_he_energy_cross_20261028/implementation"))
    ce=importlib.import_module("cross_envelope")
    eu=ce.native_module()
    source=eu.load_pinned_source(UNIT/"inputs/ATTRIBUTION_ARRAYS.npz")
    atoms=ce.native_atoms(source)
    if any(type(a) is not jr.Atom for a in atoms):
        raise ValueError("CROSS_ATOM_MODULE_IDENTITY")
    previous=json.loads((UNIT/"inputs/PR114_SELECTED_WITNESSES.json").read_text())
    saved=json.loads((UNIT/"inputs/PR115_SAVED_BOUNDS.json").read_text())
    k20=json.loads((UNIT/"inputs/PR115_K20_WITNESS.json").read_text())
    actual=[(a.key,a.energy_eV,a.coefficient,a.partition) for a in atoms]
    for raw in (previous["native_atoms"],k20["atoms"]):
        old=[(a["key"],F(a["energy_eV"]),F(a["coefficient"]),a["partition"]) for a in raw]
        if old!=actual:
            raise ValueError("SAVED_ACTUAL_ATOM_PAYLOAD_MISMATCH")
    totals={F(c["K_eV"]):c for c in previous["native_cases"]}
    crosses={F(c["bound"]["K_eV"]):c["bound"] for c in saved["cases"]}
    cert={"schema":"CR_HE_JOINT_NATIVE_CERTIFICATES_V1","source_npz_sha256":INPUT_PINS["ATTRIBUTION_ARRAYS.npz"],
          "consumer_sha256":CONSUMER_SHA,"source_atom_digest":source.atom_content_sha256,
          "source_pins":INPUT_PINS,"cases":[],"rejected_cases":[],"W":W,"nb_m3":NB}
    for label in ("1","3","10"):
        report=jr.domain_report(atoms,F(label))
        if report["valid"]:
            raise AssertionError("EXPECTED_NATIVE_DOMAIN_REJECTION:"+label)
        cert["rejected_cases"].append({"label":label,"K":F(label),"domain":report})
    targets=[("0",F(0)),("decimal_0p2",F(1,5)),("twice_binary_ghost",2*atoms[0].energy_eV),
             ("2",F(2)),("6",F(6)),("20",F(20))]
    summaries=[];consumer_calls=0
    for label,cap in targets:
        if not jr.domain_report(atoms,cap)["valid"]:
            raise AssertionError("EXPECTED_NATIVE_ACCEPTED_DOMAIN:"+label)
        old=totals[cap];bound=crosses[cap];D=F(old["dmax"]);X=F(bound["cmax"])
        B=read_measure(old["max_events"])
        G=read_measure(k20["case"]["witness"]["pairs"]+k20["case"]["witness"]["singles"]) if label=="20" else None
        region=jr.assemble(atoms,cap,D,X,B,G,cpp_executable=EXE)
        coords={"O":(F(0),F(0)),"A":(region.L/2,F(0)),"B":(region.D,region.M),
                "F":(region.D,region.X),"G":(region.X,region.X)}
        unique={}
        for name,point in coords.items():
            if point in unique:
                unique[point]["aliases"].append(name)
            else:
                unique[point]={"name":name,"aliases":[name],"measure":region.vertices[name]}
        if len(unique)>1:
            count=len(unique);d=sum((v[0] for v in unique),F(0))/count;c=sum((v[1] for v in unique),F(0))/count
            unique[(d,c)]={"name":"INTERIOR","aliases":["INTERIOR"],"measure":jr.mix_at(region,d,c)}
        witnesses=[]
        for (d,c),row in unique.items():
            measure=row["measure"];met=jr.metrics(atoms,cap,measure)
            if (met["d"],met["C"])!=(d,c):
                raise AssertionError("NATIVE_VERTEX_COORDINATE_MISMATCH")
            events=tuple(eu.Event(f"joint:{label}:{row['name']}:{i:05d}",tuple(keys),weight)
                         for i,(keys,weight) in enumerate(sorted(measure.items())) if weight)
            binding=eu.binding((F(0),F(10**10)),source)
            returns=eu.consume_event_union(eu.claims_by_partition(events,source,binding),source,nb_m3=NB)
            expected_ions=[W*(-region.N+d),W*(region.N-2*d),W*d]
            if list(returns["union"]["ion_density_delta"])!=expected_ions or returns["cross_duplicate_parent_density"]!=W*c:
                raise AssertionError("ORIGINAL_CONSUMER_JOINT_IDENTITY")
            if returns["chemical_correction_eV_m3"]!=-F("79.01")*W*c:
                raise AssertionError("ORIGINAL_CONSUMER_CHEMICAL_IDENTITY")
            consumer_calls+=1
            witnesses.append({"name":row["name"],"aliases":row["aliases"],"d":d,"C":c,
                "events":[{"electrons":keys,"coefficient":weight} for keys,weight in sorted(measure.items()) if weight],
                "consumer":returns})
        case={"label":label,"K":cap,"N":region.N,"L":region.L,"M":region.M,"D":region.D,"X":region.X,
              "witnesses":witnesses,"construction_metadata":region.metadata,
              "certified_optimum_provenance":"Hash-pinned PR114 D/max_events and PR115 X; new witnesses verified in this unit"}
        cert["cases"].append(case)
        summaries.append({k:v for k,v in case.items() if k!="witnesses"})
        summaries[-1].update({"witness_count":len(witnesses),"witness_names":[r["name"] for r in witnesses],
            "normalized":{k:getattr(region,k)/region.N for k in ("L","M","D","X")},
            "normalized_decimal":{k:float(getattr(region,k)/region.N) for k in ("L","M","D","X")}})
        write(out/"CERTIFICATES.json",cert,compact=True)
        write(out/"PARTIAL_RESULT.json",{"status":"PARTIAL_NATIVE_CHECKPOINT","completed_cap_labels":[c["label"] for c in cert["cases"]],"consumer_calls":consumer_calls})
        print(json.dumps({"completed_native_cap":label,"witnesses":len(witnesses),"consumer_calls":consumer_calls}),flush=True)
    summary={"status":"PASS_SCOPED_NATIVE_JOINT_REGION","cases":summaries,"accepted_cap_count":len(summaries),
             "domain_rejections":cert["rejected_cases"],"consumer_calls":consumer_calls,"source_atom_count":len(atoms),
             "new_large_cross_primal_caps":["6"],"native_scalar_optimizer_replays":0,"source_fit_RR_transport_replays":0,
             "source_npz_sha256":cert["source_npz_sha256"],"source_atom_digest":source.atom_content_sha256,
             "certificate_sha256":sha(out/"CERTIFICATES.json"),"physical_activation":False}
    write(out/"SUMMARY.json",summary)
    return summary


def independent(out):
    sys.path.insert(0,str(UNIT/"reference"))
    check=importlib.import_module("independent_native")
    result=check.verify(UNIT/"inputs/ATTRIBUTION_ARRAYS.npz",UNIT/"runs/native_v1/CERTIFICATES.json")
    write(out/"DETAIL.json",result)
    return result


def plot(out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    path=UNIT/"runs/native_v1/SUMMARY.json"
    data=json.loads(path.read_text());chosen={r["label"]:r for r in data["cases"]}
    plt.rcParams.update({"font.size":10,"axes.spines.top":False,"axes.spines.right":False})
    fig,axes=plt.subplots(1,3,figsize=(12,4.5),sharex=True,sharey=True)
    for ax,label in zip(axes,("2","6","20")):
        r=chosen[label];v={k:F(r[k])/F(r["N"]) for k in ("L","M","D","X")}
        pts=hull([(F(0),F(0)),(v["L"]/2,F(0)),(v["D"],v["M"]),(v["D"],v["X"]),(v["X"],v["X"])])
        a=np.array([[float(x),float(y)] for x,y in pts]);closed=np.vstack((a,a[0]))
        ax.fill(a[:,0],a[:,1],color="#b7d9ed",alpha=.85)
        ax.plot(closed[:,0],closed[:,1],color="#164b70",lw=2)
        ax.scatter(a[:,0],a[:,1],color="#164b70",s=20,zorder=3)
        ax.plot([0,.52],[0,.52],color="#999999",ls=":",lw=1)
        ax.set_title(f"Conditional K = {label} eV")
        ax.set_xlabel("Total double-event fraction  d / N")
        ax.set_xlim(-.015,.53);ax.set_ylim(-.015,.53);ax.set_aspect("equal")
        ax.grid(alpha=.18)
        ax.text(.03,.96,f"D / N = {float(v['D']):.9f}\nX / N = {float(v['X']):.9f}",transform=ax.transAxes,va="top",fontsize=9)
    axes[0].set_ylabel("Cross-bin double-event fraction  C / N")
    fig.suptitle("Exact joint He event regions",fontsize=16,y=.98)
    fig.text(.5,.035,"Same pinned source; all allowed low–high pairs are cross-bin. Actual physical K and exclusive kernel remain unspecified.",ha="center",fontsize=8)
    fig.subplots_adjust(left=.065,right=.985,top=.86,bottom=.20,wspace=.16)
    png=out/"joint_regions.png";svg=out/"joint_regions.svg"
    fig.savefig(png,dpi=160);fig.savefig(svg);plt.close(fig)
    return {"status":"PASS_SAVED_RESULT_PLOT","input_summary_sha256":sha(path),"png_sha256":sha(png),"svg_sha256":sha(svg),
            "plots":[str(png.relative_to(UNIT)),str(svg.relative_to(UNIT))],"solver_invocations":0,"float_scope":"Display coordinates only"}


if __name__ == "__main__":
    mode,out=sys.argv[1],Path(sys.argv[2])
    result={"compile":build,"controls":controls,"native":native,"independent":independent,"plot":plot}[mode](out)
    write(out/"RESULT.json",result)
    print(json.dumps(serial({k:v for k,v in result.items() if k!="cases"})),flush=True)
