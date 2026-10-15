"""Execute current compiled original Rust point chemistry with C18 photon input.

Inputs are real AXBI Driver::read_checkpoint cases and the original
owner igm_thermal::igm_point_rhs; no artificial owner point coefficients.
"""
from __future__ import annotations
import argparse,json,subprocess
from pathlib import Path
import numpy as np
from owner_adapter import read_native_export,local_photo_step,EV_ERG

PATHS={
"ZERO":"research/axbi_goal_20261014/runs/flrw/32d11e733155/ZERO",
"SHEAR_PLUS":"research/axbi_goal_20261014/report/full_progress_32d11e733155/snapshot_20261014T083357015083Z/SHEAR_PLUS"
}

def verify(root:Path,folder:Path,bin:Path,dt:float=1e10):
    rows={}
    for case,relative in PATHS.items():
        exported=folder/f"AXBI_{'PLUS' if case=='SHEAR_PLUS' else case}_native.tsv"
        native=read_native_export(exported)
        result=local_photo_step(native,dt)
        arguments=[str(bin),str(root/relative/"config.cfg"),
            str(root/relative/"checkpoint.txt")]
        arguments.extend(format(float(z),'.17g') for z in
                result["photo_gamma_per_absorber_s"]+
                result["photo_heat_erg_per_absorber_s"])
        action=subprocess.run(arguments,capture_output=True,text=True,check=True)
        text=action.stdout
        (folder/f"AXBI_{case}_rust_point_rhs.tsv").write_text(text)
        lines=text.splitlines()
        assert lines[0]=="C18_OWNER_POINT_RHS_V1"
        data={}
        for line in lines[1:]:
            a=line.split("\t")
            data[a[0]]=np.array(list(map(float,a[1:])),float)
        np.testing.assert_allclose(data["PHOTO_EVENT_RATE_CM3_S"],
             native.nH/dt*np.asarray(result["species_photoevents_per_H"]),
             rtol=2e-13,atol=1e-26)
        Q=sum(result["species_heat_eV_per_H"])
        I=sum(result["species_binding_eV_per_H"])
        np.testing.assert_allclose(data["PHOTO_INPUT_ERG_CM3_S"],
             [native.nH/dt*(Q+I)*EV_ERG],rtol=2e-13,atol=1e-35)
        rows[case]={
            "native_photo_input_mode":"real IgmPhotoInput gamma and heat per absorber",
            "photo_gamma_s":data["GAMMA"].tolist(),
            "photo_event_rates_cm3_s":data["PHOTO_EVENT_RATE_CM3_S"].tolist(),
            "photo_input_erg_cm3_s":data["PHOTO_INPUT_ERG_CM3_S"][0],
            "thermal_power_erg_per_H_s":data["THERMAL_POWER_ERG_PER_H_S"][0],
            "fraction_dt_per_s":data["FRACTION_DT_S"].tolist(),
            "owner_native_to_C18_unit_parity":"PASS",
            "proper_dt_s":dt
        }
    output=folder/"OWNER_POINT_RHS_PARITY.json"
    output.write_text(json.dumps(rows,indent=2)+"\n")
    return rows

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--owner",required=True,type=Path)
    p.add_argument("--results",required=True,type=Path)
    p.add_argument("--rust-bin",required=True,type=Path)
    p.add_argument("--dt",type=float,default=1e10)
    a=p.parse_args()
    result=verify(a.owner,a.results,a.rust_bin,a.dt)
    print("RUST_NATIVE_IGM_PHOTO_POINT_PARITY_PASS",list(result))
