#!/usr/bin/env python3
"""Original REI F05 MPRK chemical corrector transfers (HI<->HII).

Source-native original accepted 46080 cells, original 3 historical intervals.
NOT actual continuous-time reaction integrals, Ly-alpha, or official t161.
Reads private source immutable via BASS-CR PR165's strict source comparator.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,sys
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/"cr_rei_f05_h_caseb_stage_integral_20261102"
sys.path.insert(0,str(PARENT))
import native_h_caseb as prior

PARENT_HEAD="48fde990177fba08a09e70de20e3218e5303fb36"
OUTPUT="ORIGINAL_F05_MPRK_H_EFFECTIVE_TRANSFER_3_INTERVALS.csv"
INTERVALS=prior.INTERVALS
N=prior.N
COLUMNS=("tick_left","tick_right","dt_seconds","source_cells",
  "MPRK_H_recomb_counts_lo","MPRK_H_recomb_counts_hi",
  "MPRK_H_ion_counts_lo","MPRK_H_ion_counts_hi",
  "MPRK_H_recomb_binding_lo_erg","MPRK_H_recomb_binding_hi_erg",
  "MPRK_recomb_over_PR165_stage_midpoint",
  "PR165_stage_quadrature_recomb_lo","PR165_stage_quadrature_recomb_hi",
  "MPRK_effective_net_HII_vs_exact_accepted_cell_overlap",
  "MPRK_effective_net_HII_disjoint_gap_sum",
  "MPRK_effective_net_HII_global_overlap",
  "unweighted_PR165_stage_HII_overlap",
  "MPRK_native_3maps","MPRK_native_14ledger","original_local_defect_max",
  "original_public_width_max")
def check(ok,label):
    if not ok:raise ValueError("BASS_CR_MPRK_EFFECTIVE_"+label)
def get_ival(m,arr):
    return m._I(np.asarray(arr.lo),np.asarray(arr.hi))
def reconstruct_effective(m,model,base,parent_pop,parent_logt,t0,t1,total_h,total_he,original_result):
    """Reconstruct exact original MPRK predictor (e0/e1) and donor weights.

    The original accepted chemistry corrector is population_step(parent,
    average_flux(e0,e1), pred, dt). Thermal SDIRK eg/ef NOT used.
    """
    dt=float(t1-t0)
    src0=m.event_box(model,parent_pop,m.iv.exp(parent_logt),t0)
    pred=m.population_step(parent_pop,src0.flux,parent_pop,dt,total_h,total_he)
    check(pred.certified,"PREDICTOR_MATRIX_CERTIFICATE")
    parent_E=m.energy_box(parent_pop,m.iv.exp(parent_logt))
    forcing=m.rim.ReducedIntervalModel.forcing_bounds(model,t0,t0)
    ctxp=m.thermal_context(m._I(pred.lower,pred.upper),
                           forcing.volume_cm3,src0.photo_heat,forcing.hubble_s_inv)
    pr=m.thermal_root(ctxp,parent_E,dt,np.zeros_like(parent_logt.lo),1.0,
                      parent_logt.lo-0.02,parent_logt.hi+0.02)
    check(pr.certified,"PREDICTOR_THERMAL_ROOT")
    src1=m.event_box(model,m._I(pred.lower,pred.upper),
                     m.iv.exp(pr.log_temperature),t1)
    fbar=m.average_flux(src0.flux,src1.flux)
    corr=m.population_step(parent_pop,fbar,m._I(pred.lower,pred.upper),
                            dt,total_h,total_he)
    check(corr.certified,"CORRECTOR_MATRIX_CERTIFICATE")
    # Verify reconstructed chemical corrector is the EXACT original map
    # from the independently executed original step object.
    check(np.array_equal(corr.lower,original_result.population.lo)
          and np.array_equal(corr.upper,original_result.population.hi),
          "RECONSTRUCTED_CORRECTOR_BYTE_ARRAY")
    transfer={}
    for name,d,s in (("recomb",0,1),("ion",1,0)):
        fl=m._I(fbar.lo[:,d,s],fbar.hi[:,d,s])
        denom=m._I(pred.lower[:,s],pred.upper[:,s])
        target=m._I(corr.lower[:,s],corr.upper[:,s])
        check(np.all(denom.lo>0) and np.all(target.lo>0) and
              np.all(fl.hi>=0) and np.all(fl.lo>=0),
              "NONNEGATIVE_MPRK_TRANSFER")
        q=(fl*(target/denom))*dt
        lo=np.asarray(q.lo,dtype=np.float64)
        hi=np.asarray(q.hi,dtype=np.float64)
        check(lo.shape==(N,) and hi.shape==(N,) and
              np.all(np.isfinite(hi)) and np.all(hi>=lo) and np.all(lo>=0),
              "MPRK_TRANSFER_BOX")
        transfer[name]=(lo,hi)
    return transfer
def overlap_metrics(i,r,initial,final,nh):
    """Numerical source interval versus source accepted REIADP1 delta."""
    ilo,ihi=i; rlo,rhi=r
    d_lo=final.lo[:,1]-initial.hi[:,1]
    d_hi=final.hi[:,1]-initial.lo[:,1]
    flow_lo=ilo-rhi
    flow_hi=ihi-rlo
    overlap=(flow_lo<=d_hi)&(flow_hi>=d_lo)
    gap=np.maximum(0.,np.maximum(flow_lo-d_hi,d_lo-flow_hi))
    g_dlo=prior.sums(d_lo);g_dhi=prior.sums(d_hi)
    qlo=prior.sums(flow_lo);qhi=prior.sums(flow_hi)
    return {"cell_overlap":int(np.count_nonzero(overlap)),
       "gap_sum":prior.sums(gap),
       "max_gap_per_H_nucleus":float(np.max(gap/nh)),
       "global_overlap":bool(qlo<=g_dhi and qhi>=g_dlo),
       "global_delta_HII":[g_dlo,g_dhi],
       "global_weighted_source_HII":[qlo,qhi]}
def compute(rei,rec_zip,out):
    import subprocess,zipfile
    rei,rec_zip,out=map(lambda x:Path(x).resolve(),(rei,rec_zip,out))
    check(not out.exists(),"OUTPUT_PREEXISTS")
    check(prior.PARENT_CR=="264ad0c1fd62f7ec799af14f273d9902a24ca6aa",
          "SOURCE_PR165_PARENT_LOCK")
    # Preserve exact PR165 source identity even when extracted from a source-free
    # cold archive without .git metadata (requires the immutable parent module).
    check(prior.sha(PARENT/"native_h_caseb.py")==
          "7d73a3ecd47966abdbb254941581b66e92f1914799c05162985243b7d4a91075",
          "IMMUTABLE_PR165_CODE_SHA")
    in_git=subprocess.run(["git","-C",str(HERE),"rev-parse","--is-inside-work-tree"],
                          check=False,capture_output=True,text=True)
    if in_git.returncode==0:
        check(subprocess.run(["git","-C",str(HERE),"merge-base","--is-ancestor",
                              PARENT_HEAD,"HEAD"],check=False).returncode==0,
              "IMMUTABLE_PR165_GIT_ANCESTRY")
    import subprocess,zipfile
    check(subprocess.check_output(["git","-C",str(rei),"rev-parse","HEAD"],
                                  text=True).strip()==prior.SOURCE_REI_HEAD,
          "ORIGINAL_REI_HEAD")
    check(prior.sha(rec_zip)==prior.REC195_ZIP_SHA,"REC195_INPUT_SHA")
    edge=prior.load_module("cr_mprk_original_edge",
                          rei/"research/rei_igm_original26_temperature_edges_20261101/edge_probe.py")
    worker=prior.load_module("cr_mprk_original_worker",rei/edge.REL_STAGE/"analysis/attempt_worker.py")
    worker.jax_guard.install_if_missing()
    check(prior.sha(worker.KERNEL_PATH)==prior.SOURCE_KERNEL_SHA,"KERNEL_SHA")
    m=worker._kernel()
    base,y,logt,nh,nhe=worker._context(m,"LOCAL_NEUTRAL_HAZARD_PRIMARY")
    check(y.shape==(N,5),"SOURCE_SHAPE")
    model=m.rim.ReducedIntervalModel.from_repo(rei)
    src160,src=edge.source_state(rei/edge.REL_STAGE,"LOCAL_NEUTRAL_HAZARD_PRIMARY",worker.state_io)
    check(src["archive_sha256"]==prior.SOURCE_TAR_SHA and
          src["accepted_array_sha256"]==prior.SOURCE_ARRAY_SHA,"SOURCE_ORIGINAL_LOCK")
    native_duration=float(base.forcing.duration_seconds(0))
    check(abs(native_duration/prior.TICKS/prior.PROPER_MICROTICK_S-1.)<2e-14,"CLOCK")
    states={0:(m._I(y,y),m._I(logt,logt))}
    with zipfile.ZipFile(rec_zip) as z:
        check(z.testzip() is None,"ZIP_CRC")
        for tick,(fname,want) in prior.STATE.items():
            raw=z.read(fname)
            check(hashlib.sha256(raw).hexdigest()==want,"ACCEPTED_STATE_SHA")
            a=worker.state_io.decode_state(raw)
            check(a.metadata.get("endpoint_tick")==tick and
                  a.metadata.get("lane")=="LOCAL_NEUTRAL_HAZARD_PRIMARY","STATE_META")
            states[tick]=(m._I(a.population_lower,a.population_upper),
                          m._I(a.log_temperature_lower,a.log_temperature_upper))
    check(np.array_equal(states[160][0].lo,src160.population_lower) and
          np.array_equal(states[160][0].hi,src160.population_upper),
          "LAST_HISTORICAL_STATE")
    records=[]
    for a,b in INTERVALS:
        start,start_T=states[a]
        t0=native_duration*a/prior.TICKS
        t1=native_duration*b/prior.TICKS
        tm=(t0+t1)*0.5
        kw=dict(model=model,base=base,parent_pop=start,
                parent_logt=start_T,total_h=nh,total_he=nhe)
        full=m.run_step(**kw,t0=t0,t1=t1)
        first=m.run_step(**kw,t0=t0,t1=tm)
        check(first.certified,"FIRST_HALF")
        second=m.run_step(model,base,parent_pop=first.population,
               parent_logt=first.log_temperature,t0=tm,t1=t1,
               total_h=nh,total_he=nhe)
        check(all(x.certified for x in (full,first,second)),"ORIGINAL_THREE_MAPS")
        endpoint=states[b]
        check(np.array_equal(second.population.lo,endpoint[0].lo) and
              np.array_equal(second.population.hi,endpoint[0].hi) and
              np.array_equal(second.log_temperature.lo,endpoint[1].lo) and
              np.array_equal(second.log_temperature.hi,endpoint[1].hi),
              "ORIGINAL_ACCEPTED_ENDPOINT_IDENTITY")
        for result,left,right in ((full,t0,t1),(first,t0,tm),(second,tm,t1)):
            prior.ledger(m,model,result,result.population,
                        left,right,nh,nhe)
        err,width=prior.local_defect_width(m,full,second,nh,nhe)
        t1trans=reconstruct_effective(m,model,base,start,start_T,t0,tm,nh,nhe,first)
        t2trans=reconstruct_effective(m,model,base,first.population,
                                first.log_temperature,tm,t1,nh,nhe,second)
        transfer={}
        for k in ("recomb","ion"):
            transfer[k]=(t1trans[k][0]+t2trans[k][0],
                         t1trans[k][1]+t2trans[k][1])
        metric=overlap_metrics(transfer["ion"],transfer["recomb"],
                               start,endpoint[0],nh)
        # The original parent numeric source stage quadrature is a separate
        # comparison and is not by definition the corrector transfer.
        sr1=prior.source_quadrature(first,tm-t0,float(m.sdirk.GAMMA),0,1)
        sr2=prior.source_quadrature(second,t1-tm,float(m.sdirk.GAMMA),0,1)
        stage_lo=prior.sums(sr1[0]+sr2[0])
        stage_hi=prior.sums(sr1[1]+sr2[1])
        rec_lo=prior.sums(transfer["recomb"][0])
        rec_hi=prior.sums(transfer["recomb"][1])
        ion_lo=prior.sums(transfer["ion"][0])
        ion_hi=prior.sums(transfer["ion"][1])
        ratio=((rec_lo+rec_hi)/(stage_lo+stage_hi))
        record={"tick_left":a,"tick_right":b,
          "dt_seconds":t1-t0,"source_cells":N,
          "weighted_MPRK_caseB_recomb_lo":rec_lo,
          "weighted_MPRK_caseB_recomb_hi":rec_hi,
          "weighted_MPRK_H_ion_lo":ion_lo,
          "weighted_MPRK_H_ion_hi":ion_hi,
          "weighted_MPRK_H_gross_binding_lo_erg":rec_lo*prior.CHI_H_EV*prior.EV_ERG,
          "weighted_MPRK_H_gross_binding_hi_erg":rec_hi*prior.CHI_H_EV*prior.EV_ERG,
          "baseline_PR165_stage_recomb_lo":stage_lo,
          "baseline_PR165_stage_recomb_hi":stage_hi,
          "MPRK_to_stage_midpoint_ratio":ratio,
          "accepted_delta_HII_overlap_cells":metric["cell_overlap"],
          "accepted_delta_HII_nonoverlap_gap_sum":metric["gap_sum"],
          "accepted_delta_HII_max_gap_per_H_nucleus":metric["max_gap_per_H_nucleus"],
          "accepted_delta_HII_global_overlap":metric["global_overlap"],
          "source_14_ledgers":"PASS_ON_ALL_THREE_SOURCE_MAPS",
          "original_local_defect_max":err,
          "original_width_max":width}
        records.append(record)
        print(json.dumps({"interval":[a,b],
              "effective_H_caseB_transfer":[rec_lo,rec_hi],
              "effective_H_ion_transfer":[ion_lo,ion_hi],
              "MPRK_HII_conservation_cell_overlap":metric["cell_overlap"],
              "gap_sum":metric["gap_sum"],
              "original_gate":"PASS","DAG":"REI28/88_CR0/3"},sort_keys=True),flush=True)
    out.mkdir(parents=True)
    csvfile=out/OUTPUT
    with csvfile.open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=list(records[0]),lineterminator="\n")
        writer.writeheader();writer.writerows(records)
    total_rec=[math.fsum(r["weighted_MPRK_caseB_recomb_lo"] for r in records),
               math.fsum(r["weighted_MPRK_caseB_recomb_hi"] for r in records)]
    result={"schema":"BASS_CR_REI_F05_NATIVE_MPRK_EFFECTIVE_DISCRETE_TRANSFER_V1",
       "scientific_status":"SOURCE_NATIVE_DISCRETE_MPRK_CHEMICAL_TRANSFER_NOT_CONTINUUM_INTEGRAL",
       "original_source_REI_HEAD":prior.SOURCE_REI_HEAD,
       "original_26event_kernel_SHA256":prior.SOURCE_KERNEL_SHA,
       "original_REC195_source_SHA256":prior.REC195_ZIP_SHA,
       "original_source_TAR_SHA256":prior.SOURCE_TAR_SHA,
       "original_state_sha256_by_tick":{str(k):v[1] for k,v in prior.STATE.items()},
       "original_source_cells":N,
       "original_accepted_ticks":[0,64,128,160],
       "original_tick161":"NOT_ACCEPTED",
       "original_proper_microtick_seconds":native_duration/prior.TICKS,
       "original_MPRK_discrete_transfer_recomb_total":total_rec,
       "original_MPRK_discrete_transfer_recomb_binding_equivalent_erg":[z*prior.CHI_H_EV*prior.EV_ERG for z in total_rec],
       "record_count":len(records),"intervals":records,
       "any_local_source_HII_nonoverlap":any(r["accepted_delta_HII_overlap_cells"]<N for r in records),
       "not_exact_continuum_CaseB_reactions":True,
       "not_hydrogen_Lya_photon_emissivity":True,
       "CR_OFF":True,"NO_REI_MUTATION":True,"PRODUCTION":"HOLD",
       "REI_canonical_DAG":"28/88_DELTA0","REI_working_DAG":"33/88_DELTA0",
       "REI_physical_fast":"4/7_DELTA0","BASS_CR_extension":"0/3_DELTA0",
       "native_subagent":"NOT_RUN","distinct_author_referee":"NOT_RUN",
       "csv_sha256":prior.sha(csvfile)}
    (out/"SCIENCE_RESULT.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    return result
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--rei-repo",type=Path,required=True)
    p.add_argument("--rec195-zip",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    compute(a.rei_repo,a.rec195_zip,a.out)
