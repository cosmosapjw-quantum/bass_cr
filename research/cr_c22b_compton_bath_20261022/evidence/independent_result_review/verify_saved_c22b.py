"""Independent C22B saved-array verification, ODE0/RHS0/model imports0.

Reconstruct energy, particle-count EOS, atomic number ledgers and stress norms
directly from verified saved arrays. Never edit original run/analysis files.
"""
from __future__ import annotations
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
import math
import os
from pathlib import Path

for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
            "BLIS_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[key] = "1"
import numpy as np
from scipy.constants import Boltzmann, c, electron_mass, Stefan_Boltzmann

KB_EV = 1.380649e-23/1.602176634e-19
MYR = 365.25*86400*1e6
REGISTRY = [("n", 0, 0., 1.), ("H1",1,1.,1.), ("D",1,2.5e-5,2.5e-5),
            ("T",1,0.,1e-20), ("He3",2,1e-5,1e-5), ("He4",2,.082,.082),
            ("Li7",3,5e-10,5e-10), ("Li6",3,1e-14,1e-14)]
LABELS = ["n" if n=="n" else f"{n}_{q}" for n,z,_,_ in REGISTRY for q in range(z+1)]
SCALES = np.array([s for _,z,_,s in REGISTRY for q in range(z+1)])
CHARGES = np.array([q for _,z,_,_ in REGISTRY for q in range(z+1)])
IONIZATION_ENERGIES = {0:[0.],1:[0.,13.6],2:[0.,24.59,24.59+54.42],
                       3:[0.,5.392,5.392+75.64,5.392+75.64+122.5]}
BINDING = np.array([x for _,z,_,_ in REGISTRY for x in IONIZATION_ENERGIES[z]])
E0 = np.array([10.,20.,40.,60.,100.,150.])


def sha(raw): return hashlib.sha256(raw).hexdigest()
def canonical(data): return json.dumps(data,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
def readjson(path): return json.loads(Path(path).read_bytes())
def readnpz(raw):
    with np.load(io.BytesIO(raw), allow_pickle=False) as n:
        return {k:n[k] for k in n.files}


def near(actual, expected, key, rtol=2e-13, atol=1e-30):
    actual,expected=np.asarray(actual),np.asarray(expected)
    if actual.shape!=expected.shape or not np.allclose(actual,expected,rtol=rtol,atol=atol,equal_nan=False):
        raise AssertionError("DERIVED_FIELD_MISMATCH:"+key)
    return float(np.max(abs(actual-expected)))


def audit_mesh(h, raw_eta, raw_Y, gates):
    eta,Y=h["eta"],h["Y"]
    assert np.array_equal(eta,raw_eta) and np.array_equal(Y,raw_Y)
    n=len(eta);assert Y.shape==(75,n) and np.all(np.diff(eta)>0)
    assert h["atomic_state_labels"].tolist()==LABELS
    assert np.all(Y[[40,45,46]]==0.)
    for key,values in h.items():
        if key=="cancellation_fraction":continue
        if values.dtype.kind in "fci":assert np.isfinite(values).all(),key
    x=Y[40:61];ab=SCALES[:,None]*x
    near(h["atomic_scaled"],x,"atomic_scaled",0,0)
    near(h["atomic_abundance_per_Href"],ab,"atomic_abundance",0,0)
    xe=CHARGES@ab;ntot=ab.sum(axis=0)+xe
    T=Y[67]/(1.5*KB_EV*ntot)
    near(h["temperature_K"],T,"temperature")
    near(h["n_e_cm3"],h["nH_ref_cm3"]*xe,"electron_density")
    energies=E0[None,:]*np.exp(-eta[:,None])
    near(h["UV_cohort_energies_eV"],energies,"redshifting_energy")
    near(h["UV_photons_per_H"],Y[61:67].T,"UV_counts",0,0)
    near(h["thermal_energy_eV_per_H"],Y[67],"thermal",0,0)
    chemical=BINDING@ab;uv=np.sum(energies*Y[61:67].T,axis=1)
    near(h["ionization_energy_eV_per_H"],chemical,"chemical")
    near(h["UV_energy_eV_per_H"],uv,"UV_energy")
    total=Y[67]+chemical+uv+Y[68]+Y[69]+Y[70]+Y[74]
    total_difference=near(h["energy_total_eV_per_H"],total,"energy_total",2e-13,1e-14)
    energy_residual=(total-total[0])/abs(total[0])
    energy_max=float(np.max(abs(energy_residual)))
    photon_scale=max(float(Y[61:67,0].sum()),1.)
    charge=(xe+Y[71]-Y[72]-xe[0])/photon_scale
    photon=(Y[61:67].sum(axis=0)+Y[72]-Y[61:67,0].sum())/photon_scale
    near(h["charge_photon_relative_residual"],charge,"charge",0,3e-15)
    near(h["photon_number_relative_residual"],photon,"photon_count",0,3e-15)
    nuclei={};offset=0;fractions={}
    for name,z,initial,scale in REGISTRY:
        current=ab[offset:offset+z+1].sum(axis=0)
        if initial==0:
            assert np.all(current==0);residual=0.
        else:
            residual=float(np.max(abs(current/initial-1)))
            fractions[name]=ab[offset:offset+z+1]/initial
        nuclei[name]=residual;offset+=z+1
    isotopes={a+"/"+b:float(np.max(abs(fractions[a]-fractions[b])))
              for a,b in (("H1","D"),("He3","He4"),("Li6","Li7"))}
    assert max(isotopes.values())<1e-9
    tg=2.7255/h["a"]
    near(h["prescribed_CMB_temperature_K"],tg,"bath_T",0,0)
    rate=(4*6.6524587051e-29*(4*Stefan_Boltzmann/c)*tg**4*Boltzmann*xe
          *(tg-T)/(electron_mass*c)/1.602176634e-19)
    near(h["Compton_gas_rate_eV_per_H_s"],rate,"Compton_rate",3e-13,1e-30)
    near(h["Compton_gas_per_eta"],rate/h["H"],"Compton_eta",3e-13,1e-30)
    theta=Boltzmann*np.maximum(T,tg)/(electron_mass*c*c)
    near(h["Compton_nonrelativistic_parameter"],theta,"theta")
    stress_error=0.
    kt=8*math.pi*6.6743e-11/(299792458.**2)
    near(h["p_r_J_m3"],h["p_gamma_J_m3"]+h["p_nu_J_m3"],"signed_p_r",0,0)
    near(h["p_tot_J_m3"],h["p_m_J_m3"]+h["p_r_J_m3"],"signed_p_total",0,0)
    for sector in ("m","gamma","nu","r","tot"):
        p=h["p_"+sector+"_J_m3"]
        tensor=np.stack((-p,-p,2*p),axis=0)
        normalized=np.sqrt(np.sum(tensor*tensor,axis=0))*kt/(h["H"]**2)
        stress_error=max(stress_error,near(h["Pi_"+sector+"_F"],normalized,"Frobenius_"+sector))
        near(h["signed_Pi_"+sector+"_F"],math.sqrt(6)*p*kt/h["H"]**2,"signed_"+sector)
        near(h["Pi_"+sector+"_half"],normalized/math.sqrt(2),"half_"+sector)
    near(h["signed_Sigma_F"],math.sqrt(6)*h["s"]/h["H"],"signed_shear")
    near(h["Sigma_F"],abs(h["signed_Sigma_F"]),"shear_norm",0,0)
    den=abs(h["p_m_J_m3"])+abs(h["p_r_J_m3"]);defined=den!=0
    assert np.array_equal(h["cancellation_fraction_defined"],defined)
    assert np.array_equal(np.isfinite(h["cancellation_fraction"]),defined)
    assert np.all(np.isnan(h["cancellation_fraction"][~defined]))
    cancellation=1-abs(h["p_tot_J_m3"][defined])/den[defined]
    if np.any(defined):near(h["cancellation_fraction"][defined],cancellation,"cancellation",0,0)
    minimum_population=float(x.min());minimum_uv=float(Y[61:67].min())
    checks={"energy":energy_max<=gates["energy_relative_saved_and_accepted_max_abs"],
        "nucleus":max(nuclei.values())<=gates["nucleus_max_relative_residual"],
        "charge":float(np.max(abs(charge)))<=gates["charge_and_photon_absolute_normalized"],
        "photon":float(np.max(abs(photon)))<=gates["charge_and_photon_absolute_normalized"],
        "population":minimum_population>=gates["minimum_scaled_population"],
        "UV":minimum_uv>=gates["minimum_UV_count_per_H"],"n_T_exact_zero":True,
        "T_domain":bool(np.all((T>=3)&(T<=1e9))),"nonrelativistic":float(theta.max())<=.01}
    assert all(checks.values()),checks
    return {"status":"PASS_SCOPED","mesh_points":n,"checks":checks,
        "energy_relative_max_abs_independent":energy_max,"energy_field_max_abs_difference":total_difference,
        "nucleus_relative_residuals":nuclei,"charge_max_abs":float(np.max(abs(charge))),
        "photon_number_max_abs":float(np.max(abs(photon))),"minimum_population_scaled":minimum_population,
        "minimum_UV_per_H":minimum_uv,"negative_UV_count":int(np.sum(Y[61:67]<0)),
        "temperature_min_K":float(T.min()),"temperature_max_K":float(T.max()),
        "theta_max":float(theta.max()),"zero_inventory_max_abs":0.,"isotope_fraction_max_differences":isotopes,
        "Frobenius_vs_physical_tensor_max_abs":stress_error,"undefined_cancellation_count":int((~defined).sum()),
        "bath_final_eV_per_H":float(Y[74,-1]),"bath_min_eV_per_H":float(Y[74].min()),
        "trace_H2_fraction_max":float(np.max(h["omitted_trace_energy_H2_fraction"])),
        "strict_positivity":"NOT_CLAIMED; raw tolerated negative values retained"}


def main():
    ap=argparse.ArgumentParser();ap.add_argument("--unit",type=Path,required=True)
    ap.add_argument("--analysis",type=Path,required=True);ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args();unit=args.unit.resolve();analysis=args.analysis.resolve();repo=unit.parent.parent
    contract=readjson(unit/"CONTRACT.json");gates=contract["preregistered_gates"]
    frozen=readjson(unit/"evidence/SOURCE_FREEZE.json");sources=[]
    for row in frozen["files"]:
        raw=(repo/row["path"]).read_bytes();assert sha(raw)==row["sha256"] and len(raw)==row["size_bytes"]
        sources.append(row)
    artifacts=readjson(analysis/"ARTIFACTS.json");artifact_rows=[]
    for row in artifacts["files"]:
        raw=(analysis/row["name"]).read_bytes();assert sha(raw)==row["sha256"] and len(raw)==row["size_bytes"],row["name"]
        artifact_rows.append(row)
    summary=readjson(analysis/"SUMMARY.json")
    assert summary["analyzer_sha256"]==sha((unit/"analyze.py").read_bytes())
    observations={};data={};segments=0;branch_predicates=0;resources={}
    for role in ("nominal","reference"):
        run=Path(summary["runs"][role]["path"])
        source=readjson(run/"SOURCE_IDENTITY.json");assert source==frozen
        payload=dict(source);sid=payload.pop("identity_sha256");assert sha(canonical(payload))==sid
        inputs=readjson(run/"INPUT.json");input_sha=sha(canonical(inputs));runtime=readjson(run/"RUNTIME.json")
        assert runtime["input_sha256"]==input_sha and runtime["source_identity_sha256"]==sid
        assert set(runtime["thread_environment"].values())=={"1"}
        registered=contract["new_cosmological_runs"][role]
        for key in ("method","rtol","atol"):assert inputs[key]==registered[key]
        assert inputs["cases"]==(registered["cases"] if role=="nominal" else [registered["case"]])
        resource=readjson(run/"RESOURCE.json");adm=resource["admission"]
        assert 55 not in adm["selected_worker_cpus"] and adm["coordinator_cpu"] not in adm["selected_worker_cpus"]
        assert adm["workers"]<=2 and adm["numerical_threads_per_worker"]==1
        resources[role]={"coordinator_cpu":adm["coordinator_cpu"],"worker_cpus":adm["selected_worker_cpus"],
                         "lease_scope":resource["lease_observation"]["discovery"]["scope"],"exclusive_reservation":False}
        for case in inputs["cases"]:
            name=case["name"];folder=run/"cases"/name
            complete=readjson(folder/"COMPLETE.json");receipt_raw=(folder/"RECEIPT.json").read_bytes();receipt=json.loads(receipt_raw)
            raw=(folder/"history.npz").read_bytes();h=readnpz(raw)
            assert complete["status"]=="COMPLETED_SCOPED"
            assert complete["history_sha256"]==receipt["history_sha256"]==sha(raw)
            assert complete["receipt_sha256"]==sha(receipt_raw)
            for obj in (complete,receipt):
                assert obj["input_sha256"]==input_sha and obj["source_identity_sha256"]==sid
            assert receipt["case"]==case and receipt["model_metadata_sha256"]==sha((folder/"MODEL.json").read_bytes())
            assert receipt["state_size"]==75 and receipt["solver_state_size"]==72 and len(h["eta"])==201
            started=readjson(folder/"STARTED.json");assert len(started["affinity"])==1 and started["affinity"][0] in adm["selected_worker_cpus"]
            for segment in receipt["segments"]:
                assert segment["success"];segments+=1
                for side in ("left","right"):
                    check=segment["endpoint_branch_checks"][side]
                    assert check["expected_sides"]==check["actual_sides"]
                    assert 1<=check["ulp_steps"]<=256
                    branch_predicates+=np.asarray(check["actual_sides"]).size
            accepted_raw=(analysis/(role+"_"+name+"_ACCEPTED.npz")).read_bytes();ha=readnpz(accepted_raw)
            saved=audit_mesh(h,h["eta"],h["Y"],gates)
            accepted=audit_mesh(ha,h["accepted_eta"],h["accepted_Y"],gates)
            observations[role+":"+name]={"raw_sha256":sha(raw),"raw_bytes":len(raw),
                "accepted_derived_sha256":sha(accepted_raw),"saved":saved,"accepted":accepted}
            data[(role,name)]=h
    assert segments==72 and branch_predicates==6048
    nn=data[("nominal","finite_uv_compton_lrs")];rr=data[("reference","finite_uv_compton_lrs")]
    assert np.array_equal(nn["eta"],rr["eta"])
    comparisons={}
    for key in gates["reference_fields"]:
        peak=float(np.max(abs(rr[key])))
        scales=np.full_like(rr[key],max(peak,1e-30)) if key=="bath_energy_received_eV_per_H" else np.maximum(abs(rr[key]),max(1e-8*peak,1e-30))
        maximum=float(np.max(abs(nn[key]-rr[key])/scales))
        assert maximum<=gates["reference_scaled_max_difference"]
        assert maximum==summary["tighter_reference"]["finite_uv_compton_lrs"][key]["max_scaled_difference"]
        comparisons[key]={"max_scaled_difference":maximum,"gate":gates["reference_scaled_max_difference"],"pass":True}
    with (analysis/"HISTORY.csv").open(newline="") as f:csvrows=list(csv.DictReader(f))
    assert len(csvrows)==804;positions={key:0 for key in data};numeric_cells=0
    for row in csvrows:
        key=(row["role"],row["name"]);h=data[key];i=positions[key];positions[key]+=1
        for field,value in row.items():
            if field in ("role","name"):continue
            expected=h["proper_elapsed_s"][i]/MYR if field=="elapsed_Myr" else h[field][i]
            assert float(value)==float(expected),(key,i,field);numeric_cells+=1
    assert set(positions.values())=={201}
    with (analysis/"ENDPOINTS.csv").open(newline="") as f:endrows=list(csv.DictReader(f))
    assert len(endrows)==4
    for row in endrows:
        h=data[(row["role"],row["name"])]
        for field,value in row.items():
            if field in ("role","name"):continue
            expected=h["proper_elapsed_s"][-1]/MYR if field=="elapsed_Myr" else h[field][-1]
            assert float(value)==float(expected)
    prior=unit/"analysis_v1";unchanged={}
    if analysis!=prior:
        for row in artifact_rows:
            name=row["name"]
            if (prior/name).is_file():unchanged[name]=sha((prior/name).read_bytes())==row["sha256"]
    for row in sources:assert sha((repo/row["path"]).read_bytes())==row["sha256"]
    report={"schema":"C22B_INDEPENDENT_SAVED_DATA_REVIEW_V1","status":"PASS_SCOPED",
        "utc":datetime.now(timezone.utc).isoformat(),"analysis_path":str(analysis),
        "execution_source_identity_sha256":frozen["identity_sha256"],"frozen_file_count":len(sources),
        "source_unchanged":True,"ODE_calls":0,"RHS_calls":0,"science_model_imports":0,
        "new_completed_cases_reviewed":4,"successful_segments":segments,"endpoint_branch_predicates":int(branch_predicates),
        "resource_observations":resources,"runs_and_meshes":observations,"reference_comparison":comparisons,
        "CSV":{"rows":len(csvrows),"numeric_cells_exact_float_roundtrip":numeric_cells,
               "endpoint_rows":len(endrows),"HISTORY_sha256":sha((analysis/"HISTORY.csv").read_bytes())},
        "verified_artifacts":artifact_rows,"byte_identity_to_rejected_v1":unchanged,
        "figure_disposition":"v1 reference negative-time-axis rejected; final v2 visual review recorded separately",
        "limits":["finite saved and accepted meshes only","tolerated negative numerical residuals retained",
                  "one LRS solver comparison","prescribed external thermostat and atomic omissions remain conditional",
                  "no physical full-closure or global-error-bound claim"],"global_error_bound":None}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    with args.out.open("x") as f:json.dump(report,f,indent=2,allow_nan=False);f.write("\n")
    print(json.dumps({"status":report["status"],"out":str(args.out),"cases":4,"segments":segments,
        "accepted_points":{k:v["accepted"]["mesh_points"] for k,v in observations.items()},
        "max_energy_relative":max(v[mesh]["energy_relative_max_abs_independent"] for v in observations.values() for mesh in ("saved","accepted")),
        "max_reference_scaled":max(v["max_scaled_difference"] for v in comparisons.values()),"CSV_rows":len(csvrows),
        "byte_identity":unchanged}))


if __name__=="__main__":main()
