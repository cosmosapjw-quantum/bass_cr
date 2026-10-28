"""Science jobs; invoke through run_bounded.py so every attempt is charged."""
from dataclasses import replace
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import random
import sys
import time

UNIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIT / "reference"))


def save(path, value):
    import cross_envelope as core
    path.write_text(json.dumps(core.serial(value), indent=2, allow_nan=False) + "\n")


def small(out):
    import cross_envelope as core
    import cross_flow as flow
    import reference_oracle as ref
    rows = []
    cases = list(ref.named_cases())
    rng = random.Random(20261028)
    for j in range(96):
        n = rng.randrange(7)
        cases.append({"id": f"seeded_{j:03d}",
            "weights": tuple(F(rng.randrange(7), rng.randrange(1, 5)) for _ in range(n)),
            "energies": tuple(F(rng.randrange(9), 2) for _ in range(n)),
            "partitions": tuple(rng.randrange(4) for _ in range(n)),
            "cap": F(rng.randrange(15), 2)})
    for c in cases:
        atoms = tuple(flow.Atom(f"a{i}", e, w, b) for i, (w, e, b) in enumerate(
            zip(c["weights"], c["energies"], c["partitions"])))
        bound, witness = core.maximum_cross(atoms, c["cap"])
        oracle = ref.cross_oracle(c["weights"], c["energies"], c["partitions"], c["cap"])
        assert bound.cmax == oracle["cmax"]
        if "expected_cmax" in c:
            assert bound.cmax == c["expected_cmax"], c["id"]
        keys = {a.key: i for i, a in enumerate(atoms)}
        pairs = [(keys[e.electrons[0]], keys[e.electrons[1]], e.coefficient) for e in witness.pairs]
        y = dict(bound.dual)
        assert all(y[atoms[i].key] + y[atoms[j].key] >= 1 for i, j in oracle["edges"])
        # Verify the independently generated flow/mincut dual, not only the threshold dual.
        z = dict(witness.mincut_dual)
        assert all(z[atoms[i].key] + z[atoms[j].key] >= 1 for i, j in oracle["edges"])
        assert sum((a.coefficient * z[a.key] for a in atoms), F(0)) == oracle["cmax"]
        rows.append({"id": c["id"], "n": len(atoms), "edges": len(oracle["edges"]),
            "cmax": bound.cmax, "oracle_gap": F(0), "dual_candidates": oracle["dual_candidates_evaluated"]})
    controls = []
    def reject(name, fn, contains=None):
        try:
            fn()
        except (ValueError, TypeError) as e:
            if contains is not None:
                assert contains in str(e), (name, str(e))
            controls.append({"id": name, "status": "PASS_REJECTED", "reason": str(e)})
        else:
            raise AssertionError("NOT_REJECTED:" + name)
    a = (flow.Atom("a", F(0), F(1), 0), flow.Atom("b", F(0), F(1), 1))
    b, w = core.maximum_cross(a, F(0))
    for field, value in [("energy_eV", -1), ("energy_eV", 0.0), ("coefficient", True),
                         ("coefficient", -1), ("partition", True), ("partition", -1), ("key", "")]:
        reject("domain_" + field + "_" + repr(value),
            lambda field=field, value=value: core.upper_bound((replace(a[0], **{field: value}),), F(0)))
    reject("float_cap", lambda: core.upper_bound(a, 0.0))
    reject("negative_cap", lambda: core.upper_bound(a, -1))
    reject("bool_cap", lambda: core.upper_bound(a, True))
    reject("duplicate_key", lambda: core.upper_bound((a[0], a[0]), 0))
    reject("generator_atoms", lambda: core.upper_bound(iter(a), 0))
    reject("wrong_digest", lambda: core.verify_bound(a, replace(b, atom_digest="0"*64)))
    reject("infeasible_dual", lambda: core.verify_bound(a, replace(b, dual=(("a", F(0)), ("b", F(0))))))
    reject("false_objective", lambda: core.verify_bound(a, replace(b, cmax=b.cmax + 1)))
    reject("missing_pair", lambda: core.verify_primal(a, b, replace(w, pairs=())))
    reject("duplicate_pair", lambda: core.verify_primal(a, b, replace(w, pairs=w.pairs*2)))
    reject("negative_pair", lambda: core.verify_primal(a, b,
        replace(w, pairs=(flow.Event(("a", "b"), F(-1)),))))
    reject("wrong_energy_support", lambda: core.verify_primal(
        (replace(a[0], energy_eV=1), a[1]), b, w))
    reject("nonexact_certificate_objective", lambda: core.verify_bound(a, replace(b, cmax=1.0)))
    save(out / "RESULT.json", {"status": "PASS_EXACT_SMALL_AND_CONTROLS", "case_count": len(rows),
        "named_cases": 20, "seeded_cases": 96, "cases": rows, "controls_count": len(controls),
        "controls": controls, "independent_reference_imports_production": False,
        "all_gaps_exact_zero": True})


def targeted(out):
    import cross_envelope as core
    import cross_flow as flow
    atoms = (flow.Atom("a", 0, 5, 0), flow.Atom("b", 0, 1, 1),
        flow.Atom("c", 0, 1, 2))
    b, w = core.maximum_cross(atoms, F(0))
    assert b.cmax == 2
    controls = []
    def check(name, fn):
        try:
            fn()
        except (ValueError, TypeError) as error:
            controls.append({"id": name, "status": "PASS_REJECTED", "reason": str(error)})
        else:
            raise AssertionError(name)
    check("cut_dual_missing", lambda: core.verify_primal(atoms,b,replace(w,mincut_dual=())))
    check("cut_dual_infeasible", lambda: core.verify_primal(atoms,b,replace(w,
        mincut_dual=tuple((a.key,F(0)) for a in atoms))))
    check("cut_dual_wrong_objective", lambda: core.verify_primal(atoms,b,replace(w,
        mincut_dual=tuple((a.key,F(1)) for a in atoms))))
    check("cut_dual_float", lambda: core.verify_primal(atoms,b,replace(w,
        mincut_dual=tuple((key,float(y)) for key,y in w.mincut_dual))))
    check("native_nb_none", lambda: core.consume_native(None,b,w,(0,1),assumption="K",nb_m3=None))
    check("native_nb_wrong", lambda: core.consume_native(None,b,w,(0,1),assumption="K",nb_m3=1))
    check("threshold_false_partition", lambda: core.verify_bound(atoms,replace(b,partition=99)))
    check("threshold_false_energy", lambda: core.verify_bound(atoms,replace(b,e_threshold=1)))
    save(out/"RESULT.json",{"status":"PASS_TARGETED_STATIC_AUDIT_REPAIRS","controls":controls,
        "controls_count":len(controls),"positive_exact_optimum":b.cmax,
        "unchanged_small_116_replayed":False})


def native(out):
    import cross_envelope as core
    import cross_flow as flow
    previous = core.native_module()
    npz = UNIT / "inputs/ATTRIBUTION_ARRAYS.npz"
    source = previous.load_pinned_source(npz)
    atoms = core.native_atoms(source)
    cap_values = [("0", F(0)), ("decimal_0p2", F(1,5)),
        ("twice_binary_ghost", 2*atoms[0].energy_eV),
        ("1", F(1)), ("2", F(2)), ("3", F(3)), ("6", F(6)), ("10", F(10)), ("20", F(20))]
    cert = {"npz_sha256": hashlib.sha256(npz.read_bytes()).hexdigest(),
        "source_atom_digest": source.atom_content_sha256, "atoms": atoms, "cases": []}
    summary = []
    N = sum((a.coefficient for a in atoms), F(0))
    W = F(10**20, 2)
    Hneutral = F(1085,94)*F(99,100)
    assert N*W < Hneutral
    prior = F(0)
    for label, K in cap_values:
        t0 = time.process_time()
        bound = core.upper_bound(atoms, K)
        assert bound.cmax >= prior
        prior = bound.cmax
        witness = consumer = None
        if label in ("0", "3", "20"):
            witness = flow.solve(atoms, K)
            core.verify_primal(atoms, bound, witness)
            consumer = core.consume_native(source, bound, witness, (F(0), F(10**10)),
                assumption="Conditional cross-bin sum cap; actual physical K remains unspecified.")
            assert consumer["cross_duplicate_parent_density"] == W*bound.cmax
            assert consumer["chemical_correction_eV_m3"] == -F(7901,100)*W*bound.cmax
            assert consumer["native_species_correction21"][10] == W*bound.cmax/core.NB
            assert consumer["actual_full_native25"] is None
            if label == "3":
                # Adjacent windows: exact W-additivity and replay refusal with new changed adapter.
                first = core.consume_native(source, bound, witness, (F(0), F(5*10**9)),
                    assumption="Conditional K=3 check.")
                second = core.consume_native(source, bound, witness, (F(5*10**9), F(10**10)),
                    assumption="Conditional K=3 check.", previous_windows=((F(0),F(5*10**9)),))
                assert first["cross_duplicate_parent_density"] + second["cross_duplicate_parent_density"] == W*bound.cmax
                for fn in [
                    lambda: core.consume_native(source, bound, witness, (F(0),F(10**10)), assumption=""),
                    lambda: core.consume_native(source, bound, witness, (F(0),F(10**10)), assumption="K", nb_m3=1),
                    lambda: core.consume_native(source, bound, witness, (F(0),F(10**10)+1), assumption="K"),
                    lambda: core.consume_native(source, bound, witness, (F(0),F(10**10)), assumption="K",
                        previous_windows=((F(0),F(5*10**9)),)),
                ]:
                    try:
                        fn()
                    except ValueError:
                        pass
                    else:
                        raise AssertionError("NATIVE_GUARD_NOT_REJECTED")
        cert["cases"].append({"label": label, "bound": bound, "witness": witness, "consumer": consumer})
        row = {"label": label, "K_eV": K, "cmax": bound.cmax, "cmax_over_N": bound.cmax/N,
            "cmax_density_m3": bound.cmax*W,
            "chemical_correction_min_eV_m3": -F(7901,100)*bound.cmax*W,
            "native_HeI_correction_max": bound.cmax*W/core.NB,
            "primal_constructed": witness is not None, "case_cpu_s": time.process_time()-t0}
        if witness is not None:
            row.update(pairs=len(witness.pairs), network_edges=witness.network_edges,
                dinic_phases=witness.dinic_phases, augmentations=witness.augmentations)
        summary.append(row)
        save(out / "CERTIFICATES.json", cert)
        save(out / "SUMMARY.json", {"status": "RUNNING", "total_coefficient": N,
            "electron_density_m3": N*W, "inventory_ratio_upper": N*W/Hneutral, "cases": summary})
        print(json.dumps(core.serial(row)), flush=True)
    assert summary[1]["cmax"] == summary[2]["cmax"] == 0
    bin_masses = [sum((a.coefficient for a in atoms if a.partition == p), F(0)) for p in range(4)]
    assert summary[-1]["cmax"] == min(N/2,N-max(bin_masses))
    result = {"status": "PASS_EXACT_NATIVE_CROSS_ENVELOPE", "source_atoms": len(atoms),
        "caps_evaluated": len(cap_values), "native_primal_witnesses": 3,
        "native_consumer_calls_accepted": 5, "native_guards_rejected": 4,
        "all_upper_certificates_exact": True, "independent_native_status": "PENDING",
        "inventory_inactive_even_for_all_singles": True, "inventory_ratio_upper": N*W/Hneutral,
        "total_coefficient": N, "electron_density_m3": N*W, "bin_masses": bin_masses,
        "cases": summary, "actual_physical_K": None, "actual_exclusive_kernel": None,
        "physical_activation": False, "source_fit_transport_RR_replays": 0}
    save(out / "SUMMARY.json", result)
    save(out / "RESULT.json", result)


def independent(out):
    import independent_native
    result = independent_native.evaluate(UNIT/"runs/native_v1/CERTIFICATES.json",
        UNIT/"inputs/ATTRIBUTION_ARRAYS.npz")
    save(out/"RESULT.json", result)


def plot(out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import cross_envelope as core
    r = json.loads((UNIT/"runs/native_v1/SUMMARY.json").read_text())
    indep = json.loads((UNIT/"runs/independent_v1/RESULT.json").read_text())
    rows = [x for x in r["cases"] if x["label"] != "twice_binary_ghost"]
    x = [float(F(v["K_eV"])) for v in rows]
    y = [float(F(v["cmax_over_N"])) for v in rows]
    z = [float(F(v["chemical_correction_min_eV_m3"]))*1e15 for v in rows]
    plt.rcParams.update({"font.family":"DejaVu Sans","font.size":11,
        "axes.spines.top":False,"axes.spines.right":False})
    fig, ax = plt.subplots(1,2,figsize=(11.8,4.7),layout="constrained")
    ax[0].scatter(x,y,s=65,color="#225ea8",zorder=3)
    ax[0].axhline(y[-1],color="#555555",linestyle="--",linewidth=1,label="Unrestricted PR112 bound")
    ax[0].set(xlabel="Conditional pair-energy cap K [eV]",ylabel="Maximum cross-event coefficient / N",
        title="Energy-conditioned cross-bin envelope",ylim=(-.012,.43))
    ax[0].legend(fontsize=9,loc="lower right")
    ax[1].vlines(x,z,0,color="#238b45",linewidth=3,alpha=.7)
    ax[1].scatter(x,z,s=35,color="#006d2c",zorder=3)
    ax[1].axhline(0,color="#555555",linewidth=1)
    ax[1].set(xlabel="Conditional pair-energy cap K [eV]",
        ylabel="Chemical correction interval [10^-15 eV m^-3]",
        title="Union correction: -(I1 + I2) W C")
    for a in ax:
        a.grid(alpha=.2)
    fig.suptitle("BASS CR · fixed PHYS02 He marginal · proper [0, 10^10] s",fontsize=14)
    fig.supxlabel("Exact finite-atom envelopes; displayed samples have no interpolated physical K.\n"
        "Actual joint source and physical K remain unspecified. This is chemical bookkeeping, not heating.",
        fontsize=9)
    fig.savefig(out/"CROSS_ENERGY_ENVELOPE.png",dpi=180)
    fig.savefig(out/"CROSS_ENERGY_ENVELOPE.svg")
    plt.close(fig)
    save(out/"RESULT.json",{"status":"PASS_SAVED_RESULT_PLOT","source_cases":len(rows),
        "science_replays":0,"native_input_sha256":hashlib.sha256((UNIT/"runs/native_v1/SUMMARY.json").read_bytes()).hexdigest(),
        "independent_input_sha256":hashlib.sha256((UNIT/"runs/independent_v1/RESULT.json").read_bytes()).hexdigest(),
        "independent_status":indep["status"],"visual_QA":"PENDING_ROOT_INSPECTION"})


if __name__ == "__main__":
    globals()[sys.argv[1]](Path(sys.argv[2]))
