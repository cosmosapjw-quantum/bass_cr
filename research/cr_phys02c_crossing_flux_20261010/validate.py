import hashlib
import json
import platform
import time
from pathlib import Path
import numpy as np
import scipy
from crossing_flux import K, KERNEL_PATH, boundary, flux, packet_row, slab_flux

ROOT = Path(__file__).resolve().parent


def campaign():
    started = time.monotonic()
    contract = json.loads((ROOT / "CONTRACT.json").read_text())
    assert hashlib.sha256(KERNEL_PATH.read_bytes()).hexdigest() == contract["kernel_sha256"]
    rows, packets = [], []
    for impulse in contract["impulses_eV"]:
        graph = K.make_graph(impulse)
        off = K.make_graph(impulse, enabled=False)
        ids = boundary(graph)
        e = graph.energies_meV[ids] / 1000
        previous, previous_t = np.zeros(len(ids)), 0
        for epoch in contract["epochs_s"]:
            if time.monotonic() - started > 120:
                raise RuntimeError("CAMPAIGN_WALL_BUDGET")
            p = K.sparse_evolve(graph, epoch)
            u, tail, terms = K.uniformize(graph, epoch)
            f, fu = flux(graph, p), flux(graph, u)
            derivative = graph.generator @ p
            loss_n = -float(derivative[graph.active].sum())
            loss_u = -float(derivative[graph.active] @ (graph.energies_meV[graph.active]/1000))
            excitation_rate = float(derivative @ (graph.states @ np.array([10.204,21.218])))
            # Normalize instantaneous identities by outgoing number and energy rates.
            nscale = max(graph.max_rate, np.finfo(float).tiny)
            nerr = abs(loss_n-f.sum())/nscale
            uerr = abs(loss_u-f@e-excitation_rate)/(nscale*impulse)
            parity = max(float(np.abs(f-fu).sum()/nscale), float(np.abs(f-fu)@e/(nscale*impulse)))
            cumulative = p[ids]
            g16 = slab_flux(graph, previous_t, epoch, 16)
            g32 = slab_flux(graph, previous_t, epoch, 32)
            increment = cumulative-previous
            slab_error = max(float(np.abs(g32-increment).sum()),float(np.abs(g32-increment)@e/impulse))
            refinement = max(float(np.abs(g32-g16).sum()),float(np.abs(g32-g16)@e/impulse))
            oracle = None
            if impulse == 1000.001:
                r=K.rates(impulse); total=float(r.sum())
                oracle_f=r*np.exp(-total*epoch)
                oracle_c=r/total*(-np.expm1(-total*epoch))
                oracle=max(float(np.abs(f-oracle_f).sum()/nscale),float(np.abs(cumulative-oracle_c).sum()))
            finite_positive=bool(np.isfinite(p).all() and np.isfinite(f).all() and p.min()>=0 and f.min()>=0)
            bound=bool(np.all((e>978.782)&(e<=1000)))
            off_zero=bool(np.count_nonzero(flux(off,K.sparse_evolve(off,epoch)))==0)
            t0=bool(epoch!=0 or np.count_nonzero(cumulative)==0)
            passed=bool(finite_positive and bound and off_zero and t0 and nerr<=2e-11 and uerr<=2e-11 and parity<=1e-10 and slab_error<=2e-11 and refinement<=2e-11 and (oracle is None or oracle<=1e-10))
            rows.append({"impulse_eV":impulse,"epoch_s":epoch,"states":len(p),"boundary_states":len(ids),"finite_nonnegative":finite_positive,"boundary_energy_bounds":bound,"OFF_zero":off_zero,"t0_zero":t0,"number_flow_error":nerr,"energy_flow_error":uerr,"flux_parity":parity,"slab_increment_error":slab_error,"slab_refinement_error":refinement,"oracle_error":oracle,"uniformization_tail":tail,"PASS":passed})
            packets.append(packet_row(graph,epoch,p))
            previous,previous_t=cumulative,epoch
    identity={"kernel_sha256":contract["kernel_sha256"],"contract_sha256":hashlib.sha256((ROOT/"CONTRACT.json").read_bytes()).hexdigest(),"implementation_sha256":hashlib.sha256((ROOT/"crossing_flux.py").read_bytes()).hexdigest(),"validator_sha256":hashlib.sha256((ROOT/"validate.py").read_bytes()).hexdigest(),"base_commit":contract["base_commit"]}
    return {"status":"PASS_SCOPED_PENDING_REVIEW" if all(r["PASS"] for r in rows) else "FAIL","identity":identity,"wall_s":time.monotonic()-started,"environment":{"python":platform.python_version(),"numpy":np.__version__,"scipy":scipy.__version__},"campaigns":1,"repairs":0,"rows":rows,"packet":{"id":contract["id"],"identity":identity,"clock":"elapsed gas-proper seconds","crossing_energy":"unallocated","HeI_channel":"NIST singlet 2^1P; separate from 23s","rows":packets},"P02B_coupling":"HOLD","global_admission":"HOLD"}


if __name__=="__main__":
    result=campaign()
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if result["status"]=="PASS_SCOPED_PENDING_REVIEW" else 1)
