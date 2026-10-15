"""Read-only single-b AOCC basis geometry and projector diagnostic."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
from cr_repro.aocc import OneElectronAOCC

def diagnose(config: dict, times: list[float]) -> dict:
    a = OneElectronAOCC(config)
    groups = []
    for g in a.groups:
        neg = np.asarray(g["eps"])[np.asarray(g["eps"]) < 0]
        groups.append({"name": g["name"], "states": int(len(g["eps"])),
                       "negative_count": int(len(neg)),
                       "lowest_energy_Eh": float(g["eps"][0])})
    observations = []
    for t in times:
        O, H, D = a.matrix(t)
        Sh = (O + O.conj().T) * 0.5
        lam = np.linalg.eigvalsh(Sh)
        t_idx = [i for i, (center, j) in enumerate(a.basis)
                 if center == "T" and a.eps[j] < 0]
        p_idx = [i for i, (center, j) in enumerate(a.basis)
                 if center == "P" and a.eps[j] < 0]
        # Orthogonal projectors onto separate subspaces need not sum to identity.
        # Singular values of whitened cross overlap quantify their nonorthogonality.
        ST = Sh[np.ix_(t_idx,t_idx)]
        SP = Sh[np.ix_(p_idx,p_idx)]
        TP = Sh[np.ix_(t_idx,p_idx)]
        def invsqrt(S):
            vals,U = np.linalg.eigh(S)
            return (U * (1 / np.sqrt(vals))) @ U.conj().T
        sv = np.linalg.svd(invsqrt(ST) @ TP @ invsqrt(SP),compute_uv=False) if t_idx and p_idx else []
        h=1e-4
        Op=a.matrix(t+h)[0]; Om=a.matrix(t-h)[0]
        dotO=(Op-Om)/(2*h)
        identity_defect=float(np.linalg.norm(dotO-D-D.conj().T)/max(np.linalg.norm(dotO),1e-30))
        observations.append({
            "t_au": float(t),
            "overlap_min_eigenvalue":float(lam[0]),
            "overlap_max_eigenvalue":float(lam[-1]),
            "overlap_condition":float(lam[-1]/lam[0]) if lam[0]>0 else None,
            "max_target_projectile_bound_subspace_overlap":float(max(sv)) if len(sv) else 0.,
            "overlap_hermiticity_defect":float(np.linalg.norm(O-O.conj().T)/max(np.linalg.norm(O),1e-30)),
            "hamiltonian_hermiticity_defect":float(np.linalg.norm(H-H.conj().T)/max(np.linalg.norm(H),1e-30)),
            "moving_basis_identity_defect":identity_defect
        })
    return {"energy_keV_per_u":config["energy_keV_per_u"], "b_a0":config["b"],
            "basis_dimension":a.nb,"retained_atomic_states":len(a.keep),
            "negative_energy_count":int(np.count_nonzero(a.epsk<0)),
            "groups":groups,"geometry":observations}

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("configs",nargs="+")
    parser.add_argument("--output",default=None)
    args=parser.parse_args()
    records=[]
    for path in args.configs:
        cfg=json.loads(Path(path).read_text())
        a=OneElectronAOCC(cfg)
        records.append({"source":str(path),"diagnosis":diagnose(cfg,[a.t0,0.,a.tf])})
    encoded=json.dumps({"schema":"BASS_CR_AOCC_GEOMETRY_V1","records":records},indent=2,allow_nan=False)
    if args.output:Path(args.output).write_text(encoded+"\n")
    print(encoded)
