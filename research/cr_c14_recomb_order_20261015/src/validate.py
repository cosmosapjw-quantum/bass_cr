"""C14 readout: RR independent reference, stiff source exact Duhamel and owner scope."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy.integrate import quad

from owner_age_bridge import owner_namespace,source_identity
from physical_age import Gas
from rr_order import orders
from exponential_source import (
    absorb_with_source,midpoint_born_source,phi_neg,
    test_matrix_lambda_from_owner,
)


def evaluate(owner:Path):
    ns=owner_namespace(owner)
    rr={}
    for T in (4000.,9000.):
        variants={}
        for mode in ("frozen","midpoint"):
            data=orders(ns,numbers=(8,16,32,64,128),
                        g=Gas(.9,.85,.15,0.,T),ne_method=mode)
            err=np.abs([row["xhi_error"] for row in data["rows"]])
            data["observed_orders_xHI"]=np.log2(err[:-1]/err[1:]).tolist()
            variants[mode]=data
        rr[str(T)]=variants
    E,rates=test_matrix_lambda_from_owner(ns)
    proper=quad(lambda u:1/ns["model"].hubble(np.exp(u),0.),
                np.log(.1),np.log(.11))[0]
    # Manufactured uniform-time source: 0.05 photon/H per total window
    # equally across five representative owner-Verner photon energies.
    source=np.full(len(E),.05/proper/len(E))
    exact=(source*proper)*phi_neg(rates.sum(axis=1)*proper)
    rows=[]
    for N in (16,32,64,128,1024):
        dt=proper/N
        packet=np.zeros(len(E));midpoint=np.zeros(len(E))
        evt=np.zeros((len(E),3))
        for _ in range(N):
            packet,events,_=absorb_with_source(packet,source,rates,dt)
            evt+=events
            midpoint=midpoint_born_source(midpoint,source,rates,dt)
        total_born=source*proper
        assert np.all(packet>=0)
        assert np.max(abs(total_born-(packet+evt.sum(axis=1))))<1e-12
        rows.append({
            "steps":N,
            "tau_per_step":(rates.sum(axis=1)*dt).tolist(),
            "survivor_Duhamel_per_H":packet.tolist(),
            "survivor_midpoint_per_H":midpoint.tolist(),
            "exact_constant_coeff_survivor_per_H":exact.tolist(),
            "Duhamel_max_relative_error":float(np.max(abs(packet-exact)/np.maximum(abs(exact),1e-30))),
            "midpoint_max_relative_error":float(np.max(abs(midpoint-exact)/np.maximum(abs(exact),1e-30))),
            "total_source_per_H":total_born.tolist(),
            "max_photon_ledger_residual":float(np.max(abs(total_born-packet-evt.sum(axis=1))))
        })
    joint_source=Path(__file__).parents[1]/'results/JOINT_ORDER.json'
    joint=json.loads(joint_source.read_text()) if joint_source.is_file() else None
    return {
        "schema":"BASS_CR_C14_RR_AND_DUHAMEL_VALIDATION_V1",
        "physical_scope":"pure RR exact local H/He+fixed gas reference; constant coefficient emitting/absorbing photon cell",
        "owner_sha256":source_identity(owner),
        "owner_igm_rates_sha256":hashlib.sha256(
            (owner/'rust/rei_microphysics/src/igm_rates.rs').read_bytes()).hexdigest(),
        "RR_independent_DOP853":rr,
        "source_toy":{
            "owner_energy_eV":E.tolist(),
            "owner_lambda_s_inverse_by_species":rates.tolist(),
            "proper_total_window_seconds":proper,
            "assumed_emission":"manufactured uniform rate, 0.05 photons/H summed over five energies",
            "positive_exponential_Duhamel":rows
        },
        "full_photorecomb_stress":{"status":"HOLD_GLOBAL_FIRST_ORDER_LIKE",
            "observed":joint,
            "meaning":"C14 time-centered electron density corrects RR-only scheme; photo source injection stiff order remains unresolved",
        },
        "scientific_status":"SCOPED_NUMERICALLY_CHECKED_NOT_PHYSICAL_EOR_ADMISSION"
    }


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--owner',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    v=p.parse_args()
    d=evaluate(v.owner)
    v.out.parent.mkdir(exist_ok=True,parents=True)
    v.out.write_text(json.dumps(d,indent=2)+'\n')
    for T,info in d['RR_independent_DOP853'].items():
        print('T',T,'old_orders',info['frozen']['observed_orders_xHI'],
              'new_orders',info['midpoint']['observed_orders_xHI'])
    print('STIFF_SOURCE_OWNER_ENERGY_eV',d['source_toy']['owner_energy_eV'])
    print('PHOTON_REF_AT_13.61_eV',d['source_toy']['positive_exponential_Duhamel'][-1]['exact_constant_coeff_survivor_per_H'][0])
