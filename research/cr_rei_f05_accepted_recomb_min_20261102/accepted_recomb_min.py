#!/usr/bin/env python3
"""Original REI F05 accepted-history H Case-B minimum recombination event budget.

A necessary lower bound conditional on continuous-model source consistency,
NOT a reconstructed number of actual emitted photons or a t161 acceptance.
Read immutable original private NPZ + REIADP1 state arrays, write only THREE
source-free derived interval records and a science JSON. CR-OFF/production hold.
"""
from __future__ import annotations

import argparse,csv,hashlib,json,math,struct,subprocess
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=Path("/home/cosmosapjw")
PARENT="b5001472fa96ec7ba511e989948d826df3d12ab3"
ORIGINAL_REI="cc1929982948265f6d0b0f699353b3170ccd1792"
REI_BASE=ROOT/"worktrees/rei-f05-v2-versioned-owner-decision-20261101"
REI_RHS=REI_BASE/"stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_R1_VALIDATED_CONTINUOUS_BRANCH_DIFFERENTIAL_INCLUSION_ENCLOSURE_LOCK/analysis/reduced_interval_rhs.py"
RHS_SHA="b1f3d6d6397ff727b756816165652a44eb373055256adf7af2e7ef6304ed9b36"
INIT=ROOT/"worktrees/rec-f05-accepted-trajectory-20261102/research/rec_rei_f05_native_thomson_medium_20261101/source_inputs/ORIGINAL_REI_F05_initial_material_state_z6.npz"
INIT_SHA="7855f8b5c072da7860e5b0404a5548114ef46a8713840d99e4efa1b009905d2d"
REC_RESULT=ROOT/"worktrees/rec-f05-accepted-trajectory-20261102/research/rec_f05_accepted_trajectory_20261102/results/SCIENCE_RESULT.json"
REC_RESULT_SHA="f015ff77dfdc2afc022360880030aa29f06c234cac146105edbbf291fce39429"
STATE_FILES={
 64:ROOT/"archives/rei_f05_owner_original64_rust_20261101/private/FIRST64_CURRENT_RUNTIME_NONAUTHORITATIVE.state",
 128:ROOT/"archives/rec_f05_accepted_trajectory_20261102/run_002_pinned/private/ORIGINAL_REPLAY_TICK000128_NONAUTHORITATIVE.state",
 160:ROOT/"archives/rec_f05_accepted_trajectory_20261102/run_002_pinned/private/ORIGINAL_REPLAY_TICK000160_NONAUTHORITATIVE.state",
}
STATE_SHA={
 64:"aae4607ec1f0eff6669f1c1cb716ec6d6a4af8b789bba14abcd17f1733f83425",
 128:"bbb349102194c86fb39a720a6695d9cb5845782b154da3448a433959fcc7f6a6",
 160:"74c7cbb784c3a6fe25e53307f678ef23ab87263f56b314fbaa3ef696433d05f6",
}
STATE64_BODY_SHA="011f264e01a9634db7766ce15fea136d1416e68c3e5a73725c17cf2bc7d43888"
N=46080
EV_ERG=1.602176634e-12
CHI_H_EV=13.598434599702
DT_REF=4871848749.16828
OUTPUT="REI_F05_ACCEPTED_HISTORY_RECOMB_MIN_3_INTERVALS.csv"
COLUMNS=("tick_start","tick_end","original_proper_duration_s","original_source_cells",
 "certified_net_HII_decline_nodes","certified_net_HII_gain_nodes","source_sign_ambiguous_nodes",
 "min_caseB_recombination_events_conditional","weaker_global_net_HII_decline_lower",
 "min_caseB_gross_binding_release_erg_conditional","minimum_event_fraction_total_original_H",
 "minimum_events_per_proper_second")
def ensure(condition,code):
    if not condition: raise ValueError("BASS_CR_RECOMB_"+code)
def sha(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for block in iter(lambda:f.read(1<<20),b""):h.update(block)
    return h.hexdigest()
def source_state(path,tick,expected_hash):
    ensure(sha(path)==expected_hash,"STATE_SHA256")
    data=Path(path).read_bytes()
    ensure(data[:8]==b"REIADP1\x00","STATE_MAGIC")
    (hlen,)=struct.unpack_from("<Q",data,8)
    ensure(30<hlen<10000,"HEADER_LENGTH")
    meta=json.loads(data[16:16+hlen].decode("ascii"))
    ensure(meta["schema"]==1 and meta["byte_order"]=="little" and meta["dtype"]=="float64","STATE_TYPE")
    ensure(meta["array_order"]==["population_lower","population_upper","log_temperature_lower","log_temperature_upper"],"STATE_ORDER")
    ensure(meta["population_shape"]==[N,5] and meta["log_temperature_shape"]==[N],"STATE_SHAPE")
    ensure(meta["metadata"]["endpoint_tick"]==tick and meta["metadata"]["lane"]=="LOCAL_NEUTRAL_HAZARD_PRIMARY","ORIGINAL_LANE_TICK")
    body=data[16+hlen:]
    ensure(len(body)==8*(2*5*N+2*N),"STATE_BODY_BYTE_COUNT")
    if tick==64:ensure(hashlib.sha256(body).hexdigest()==STATE64_BODY_SHA,"STATE64_BODY_SHA")
    # Independently parse raw little-endian f64 body without the original worker.
    a=np.frombuffer(body,dtype="<f8",count=2*N*5).reshape(2,N,5)
    ensure(bool(np.isfinite(a).all()) and bool(np.all(a[0]>0)) and bool(np.all(a[0]<=a[1])),"PHYSICAL_CONE")
    return a[0].copy(),a[1].copy(),meta["metadata"]
def down(value):
    return math.nextafter(float(value),-math.inf)
def lower_envelope(left_lower,right_upper):
    ensure(left_lower.shape==(N,) and right_upper.shape==(N,),"HII_SHAPE")
    difference=np.subtract(left_lower,right_upper)
    # One outward step protects binary64 subtraction for strictly positive
    # differences. A 0-bound is exact for cells with possible gains.
    return np.maximum(0.,np.nextafter(difference,-np.inf))
def exact_nonnegative_sum_down(arr):
    vals=[float(x) for x in arr]
    ensure(all(math.isfinite(x) and x>=0 for x in vals),"SUM_NONNEGATIVE")
    value=math.fsum(vals)
    ensure(value>0,"TRIVIAL_ZERO_SOURCE")
    return down(value)
def run(output):
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    ensure(sha(INIT)==INIT_SHA,"INIT_SHA")
    ensure(sha(REI_RHS)==RHS_SHA,"RHS_SHA")
    ensure(subprocess.check_output(["git","-C",str(REI_BASE),"rev-parse","HEAD"],text=True).strip()==ORIGINAL_REI,"OWNER_HEAD")
    ensure(sha(REC_RESULT)==REC_RESULT_SHA,"REC_ACCEPTED_CLOCK_RESULT_SHA")
    rec=json.loads(REC_RESULT.read_text())
    ensure(rec["physical_epochs"]==[0,64,128,160] and rec["f05_tick161"]=="NOT_ACCEPTED","HISTORICAL_EPOCHS")
    ensure(rec["original_accepted_tick"]=="160/131072" and rec["DAG_REI_canonical"]=="28/88","REC_AUTHORITY")
    for tick,key in ((64,"input_first64_state_sha256"),(128,"replayed_128_state_sha256"),(160,"replayed_160_state_sha256")):
        ensure(rec[key]==STATE_SHA[tick],"REC_REIADP_IDENTITY")
    dt=float(rec["one_tick_duration_seconds"])
    ensure(dt==DT_REF,"NATIVE_PROPER_CLOCK")
    ensure(all(z["all_14_ledgers_include_zero"] for z in rec["original_maps"]),"SOURCE_HISTORY_LEDGER")
    with np.load(INIT,allow_pickle=False) as z:
        init_hi=np.asarray(z["N_HI"],dtype=np.float64).copy()
        init_hii=np.asarray(z["N_HII"],dtype=np.float64).copy()
    ensure(init_hi.shape==(N,) and init_hii.shape==(N,),"INIT_SHAPE")
    ensure(bool(np.isfinite(init_hii).all()) and bool(np.all(init_hii>0)),"INIT_POSITIVE")
    nH=init_hi+init_hii
    ensure(bool(np.all(nH>0)) and bool(np.isfinite(nH).all()),"H_NUCLEI")
    total_h=math.fsum(float(x) for x in nH)
    states={0:(init_hii,init_hii)}
    for tick,path in STATE_FILES.items():
        lo,hi,_=source_state(path,tick,STATE_SHA[tick])
        # HII counts cannot exceed the immutable H-nucleus inventory; verify
        # the original source count interval in the native box.
        ensure(bool(np.all(hi[:,1]<=nH*(1.+1e-10))),"H_ION_CAPACITY")
        ensure(bool(np.all(lo[:,0]+lo[:,1]<=nH*(1.+1e-10))) and
               bool(np.all(hi[:,0]+hi[:,1]>=nH*(1.-1e-10))),"H_NUCLEI_ENCLOSURE")
        states[tick]=(lo[:,1],hi[:,1])
    records=[];all_lower=[];all_HII_LOSS=[];all_energy=[]
    for left,right in ((0,64),(64,128),(128,160)):
        al,au=states[left];bl,bu=states[right]
        lower=lower_envelope(al,bu)
        total_lower=exact_nonnegative_sum_down(lower)
        raw=[down(x) for x in np.subtract(al,bu)]
        weaker=max(0.,down(math.fsum(raw)))
        ensure(total_lower>=weaker*(1.-1e-14),"LOCAL_GE_GLOBAL_LOWER")
        energy=down(down(total_lower*CHI_H_EV)*EV_ERG)
        n_loss=int(np.count_nonzero(al>bu))
        n_gain=int(np.count_nonzero(bl>au))
        ambiguous=N-n_loss-n_gain
        ensure(n_loss+n_gain+ambiguous==N,"SIGN_PARTITION")
        duration=dt*(right-left)
        record={
         "tick_start":left,"tick_end":right,"original_proper_duration_s":duration,
         "original_source_cells":N,"certified_net_HII_decline_nodes":n_loss,
         "certified_net_HII_gain_nodes":n_gain,"source_sign_ambiguous_nodes":ambiguous,
         "min_caseB_recombination_events_conditional":total_lower,
         "weaker_global_net_HII_decline_lower":weaker,
         "min_caseB_gross_binding_release_erg_conditional":energy,
         "minimum_event_fraction_total_original_H":down(total_lower/total_h),
         "minimum_events_per_proper_second":down(total_lower/duration),
        }
        records.append(record);all_lower.append(total_lower);all_energy.append(energy)
    combined=down(math.fsum(all_lower))
    combined_energy=down(math.fsum(all_energy))
    ensure(combined>=0 and combined_energy>=0,"COMBINED_POSITIVE")
    science={
       "schema":"BASS_CR_ORIGINAL_REI_F05_ACCEPTED_HISTORY_MIN_CASEB_RECOMB_V1",
       "result_support":"CONDITIONAL_ON_CONTINUOUS_SOURCE_CONSISTENCY_AND_VALID_ENDPOINT_ENCLOSURES",
       "input_original_NPZ_sha256":INIT_SHA,
       "input_rei_accepted_state_sha256":{str(k):v for k,v in STATE_SHA.items()},
       "input_rec195_accepted_history_science_sha256":REC_RESULT_SHA,
       "source_original_HII_RHS_sha256":RHS_SHA,
       "source_f05_original_tar_sha256":"a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b",
       "source_rei_owner_head":ORIGINAL_REI,
       "original_accepted_ticks":[0,64,128,160],
       "original_t161":"NOT_ACCEPTED",
       "source_cells":N,"native_proper_tick_seconds":dt,
       "min_total_caseB_event_lower_conditional":combined,
       "min_total_H_recomb_binding_release_erg_conditional":combined_energy,
       "total_original_H_nuclei":total_h,
       "intervals":records,
       "no_nonzero_lower_bound_on_actual_Lya_emission":True,
       "no_finite_recomb_upper_from_endpoints":True,
       "actual_26event_time_integrated_reactions":"NOT_MEASURED",
       "original_14ledger_stage_replay":"REUSED_PRIOR_REC195_NOT_RERUN",
       "source_byte_identity":"VERIFIED",
       "independent_referee":"NOT_RUN",
       "native_subagent":"NOT_RUN",
       "REI_central_DAG":"28/88_DELTA0","REI_working_DAG":"33/88_DELTA0",
       "REI_physical_fast":"4/7_DELTA0","BASS_CR_extension":"0/3_DELTA0",
       "CR_OFF":True,"PRODUCTION":"HOLD","NO_REI_MUTATION":True,
       "NO_MERGE":True,"NO_FORCE_PUSH":True,
    }
    csv_path=out/OUTPUT
    with csv_path.open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=COLUMNS,lineterminator="\n")
        writer.writeheader();writer.writerows(records)
    science["output_csv_sha256"]=sha(csv_path)
    js=out/"SCIENCE_RESULT.json"
    js.write_text(json.dumps(science,sort_keys=True,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return science
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",default=HERE,type=Path)
    args=parser.parse_args()
    data=run(args.out)
    print(json.dumps({"output_csv_sha256":data["output_csv_sha256"],"event_lower":data["min_total_caseB_event_lower_conditional"],"intervals":len(data["intervals"])},sort_keys=True))
