#!/usr/bin/env python3
"""Native F05 accepted H Case-B SDIRK2 cumulative recombination reaction source.

Original 26-event 46080-cell source, original accepted [0,64],[64,128],
[128,160], unchanged original solver. Not an exact continuum reaction count,
H Lyman-alpha photon source, observed radiation, or new t161 admission.
All raw original physical states are read only and not published.
"""
from __future__ import annotations
import argparse, csv, hashlib, importlib.util, json, math, subprocess, sys, zipfile
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
N=46080
TICKS=131072
PARENT_CR="264ad0c1fd62f7ec799af14f273d9902a24ca6aa"
SOURCE_REI_HEAD="70bb906fcfd6b7c5b0f4c356f44c03ad7164ff00"
REC195_ZIP_SHA="ed08c131cb61b8cb5c5a52a8dadeb4fc7350945eefc5c2e1c1bf12c1a2052657"
SOURCE_TAR_SHA="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
SOURCE_KERNEL_SHA="579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644"
SOURCE_ARRAY_SHA="cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01"
STATE={
  64:("private/first64_original_source.state","aae4607ec1f0eff6669f1c1cb716ec6d6a4af8b789bba14abcd17f1733f83425"),
  128:("private/replayed128_pinned.state","bbb349102194c86fb39a720a6695d9cb5845782b154da3448a433959fcc7f6a6"),
  160:("private/replayed160_pinned.state","74c7cbb784c3a6fe25e53307f678ef23ab87263f56b314fbaa3ef696433d05f6")
}
PROPER_MICROTICK_S=4871848749.16828
CHI_H_EV=13.598434599702
EV_ERG=1.602176634e-12
INTERVALS=((0,64),(64,128),(128,160))
OUTPUT="ORIGINAL_F05_ACCEPTED_H_CASEB_STAGE_3_INTERVALS.csv"
COLUMNS=("start_tick","end_tick","proper_duration_s",
 "source_H_caseB_events_integrated_lower","source_H_caseB_events_integrated_upper",
 "source_H_ion_events_integrated_lower","source_H_ion_events_integrated_upper",
 "gross_H_recomb_chemical_release_lower_erg","gross_H_recomb_chemical_release_upper_erg",
 "conditional_endpoint_min_recomb_events","min_stage_integral_minus_endpoint_lower_events",
 "original_delta_HII_lower","original_delta_HII_upper",
 "quadrature_net_HII_lower","quadrature_net_HII_upper",
 "source_net_HII_interval_overlap","source_net_HII_gap_sum_counts",
 "source_net_HII_gap_over_total_abs_original_delta",
 "source_net_HII_max_gap_over_H_nuclei",
 "global_source_net_HII_interval_overlap",
 "full_vs_twohalf_mid_recomb_difference",
 "all_original_14_ledgers_include_zero","original_source_defect_max","original_public_width_max")
def require(ok,code):
    if not ok:raise ValueError("BASS_CR_ORIGINAL_H_CASEB_"+code)
def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(1048576),b""):h.update(b)
    return h.hexdigest()
def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    require(spec is not None and spec.loader is not None,"ORIGINAL_MODULE_LOAD")
    mod=importlib.util.module_from_spec(spec)
    sys.modules[name]=mod
    spec.loader.exec_module(mod)
    return mod
def sums(a):
    """Higher accumulation precision without claiming directed rounding."""
    return float(np.sum(np.asarray(a,dtype=np.longdouble),dtype=np.longdouble))
def sample_bounds(event,dest,src):
    require(event.flux.lo.shape==event.flux.hi.shape==(N,5,5),"ORIGINAL_26EVENT_SHAPE")
    lo=np.asarray(event.flux.lo[:,dest,src],dtype=np.float64)
    hi=np.asarray(event.flux.hi[:,dest,src],dtype=np.float64)
    require(bool(np.isfinite(lo).all()) and bool(np.isfinite(hi).all()) and
            bool(np.all(lo<=hi)) and bool(np.all(hi>=0.)),"ORIGINAL_REACTION_RATE_CONE")
    # Exact source is nonnegative. Clip only negative outward subnormal rounding.
    require(float(np.min(lo))>=-1e-250,"NEGATIVE_MACRO_REACTION")
    return np.maximum(0.,lo),np.maximum(0.,hi)
def source_quadrature(step,dt,g,dest,src):
    require(step.certified and step.stage_event is not None and step.final_event is not None,
            "SOURCE_STAGE_NOT_CERTIFIED")
    require(dt>0 and math.isfinite(dt) and 0<g<1,"STAGE_CLOCK")
    slo,shi=sample_bounds(step.stage_event,dest,src)
    flo,fhi=sample_bounds(step.final_event,dest,src)
    lower=dt*((1-g)*slo+g*flo)
    upper=dt*((1-g)*shi+g*fhi)
    require(bool(np.all(lower>=0)) and bool(np.all(lower<=upper)) and
            bool(np.isfinite(upper).all()),"SOURCE_QUADRATURE_INTERVAL")
    return lower,upper
def count_parent_lower(a,b):
    """Original PR164 endpoint-only bound; comparator, NOT new photon count."""
    require(a[0].shape==a[1].shape==b[0].shape==b[1].shape==(N,5),"STATE_BOX_SHAPE")
    return np.maximum(0.,np.nextafter(a[0][:,1]-b[1][:,1],-np.inf))
def ledger(m,model,step,pop,t0,t1,nh,nhe):
    g=float(m.sdirk.GAMMA)
    led={
       "H_nuclei":(float(np.min(pop.lo[:,0]+pop.lo[:,1]-nh)),
                    float(np.max(pop.hi[:,0]+pop.hi[:,1]-nh))),
       "He_nuclei":(float(np.min(np.sum(pop.lo[:,2:5],axis=1)-nhe)),
                    float(np.max(np.sum(pop.hi[:,2:5],axis=1)-nhe)))
    }
    for label,e,box,ts in (("stage",step.stage_event,pop,t0+g*(t1-t0)),
                           ("final",step.final_event,pop,t1)):
        led[label+"_photon_identity"]=(float(np.min(e.photon_identity.lo)),
                                       float(np.max(e.photon_identity.hi)))
        total=e.resolved_heat+e.unresolved_energy+e.escaped_energy+e.chemical_energy
        led[label+"_total_energy"]=(float(np.min(total.lo)),float(np.max(total.hi)))
        for j,z in enumerate(m.group_photon_residuals(model,box,ts)):
            led[f"{label}_group_{j}_photon"]=(float(np.asarray(z.lo)),float(np.asarray(z.hi)))
    require(len(led)==14 and m.primitive.audit_set_ledgers(led).all_include_zero,
            "ORIGINAL_14_LEDGER_NOT_CLOSED")
    require(not any(e.any_event for e in step.table_events),"ORIGINAL_TABLE_EVENT")
    return True
def local_defect_width(m,full,two,nh,nhe):
    def fields(step):
        p=step.population;l=step.log_temperature
        return {"x_HII":m._I(p.lo[:,1]/nh,p.hi[:,1]/nh),
                "x_HeII":m._I(p.lo[:,3]/nhe,p.hi[:,3]/nhe),
                "x_HeIII":m._I(p.lo[:,4]/nhe,p.hi[:,4]/nhe),
                "log_T":l}
    a=fields(full);b=fields(two)
    errs={k:float(np.max(np.maximum(abs(a[k].lo-b[k].hi),abs(a[k].hi-b[k].lo)))) for k in a}
    widths={k:float(np.max(b[k].hi-b[k].lo)) for k in b}
    require(max(errs.values())<2e-4 and max(widths.values())<2e-3,"ORIGINAL_FROZEN_GATES")
    return max(errs.values()),max(widths.values())
def run(rei,rec_zip,out):
    rei,rec_zip,out=map(lambda x:Path(x).resolve(),(rei,rec_zip,out))
    require(subprocess.check_output(["git","-C",str(rei),"rev-parse","HEAD"],text=True).strip()==SOURCE_REI_HEAD,"REI_HEAD_CHANGED")
    require(sha(rec_zip)==REC195_ZIP_SHA,"REC195_ZIP_SHA")
    require(not out.exists(),"REFUSE_OVERWRITE_OUTPUT")
    edge=load_module("cr_hcaseb_original_edge",rei/"research/rei_igm_original26_temperature_edges_20261101/edge_probe.py")
    worker=load_module("cr_hcaseb_original_worker",rei/edge.REL_STAGE/"analysis/attempt_worker.py")
    worker.jax_guard.install_if_missing()
    require(sha(worker.KERNEL_PATH)==SOURCE_KERNEL_SHA,"ORIGINAL_KERNEL_SHA")
    m=worker._kernel()
    base,y,logt,nh,nhe=worker._context(m,"LOCAL_NEUTRAL_HAZARD_PRIMARY")
    require(y.shape==(N,5) and bool(np.all(nh>0)) and bool(np.all(nhe>0)),"SOURCE_ORIGINAL_GRAIN")
    model=m.rim.ReducedIntervalModel.from_repo(rei)
    accepted160,src=edge.source_state(rei/edge.REL_STAGE,"LOCAL_NEUTRAL_HAZARD_PRIMARY",worker.state_io)
    require(src["archive_sha256"]==SOURCE_TAR_SHA and
            src["accepted_array_sha256"]==SOURCE_ARRAY_SHA,"ORIGINAL_SOURCE_LOCK")
    native_duration=float(base.forcing.duration_seconds(0))
    require(abs(native_duration/TICKS/PROPER_MICROTICK_S-1.)<2e-14,"ORIGINAL_PROPER_TIME")
    states={0:(m._I(y,y),m._I(logt,logt))}
    with zipfile.ZipFile(rec_zip) as f:
        require(f.testzip() is None,"SOURCE_ZIP_CRC")
        for tick,(name,wanted) in STATE.items():
            raw=f.read(name)
            require(hashlib.sha256(raw).hexdigest()==wanted,"REIADP1_SOURCE_SHA")
            s=worker.state_io.decode_state(raw)
            require(s.metadata.get("endpoint_tick")==tick and
                    s.metadata.get("lane")=="LOCAL_NEUTRAL_HAZARD_PRIMARY","SOURCE_METADATA")
            states[tick]=(m._I(s.population_lower,s.population_upper),
                          m._I(s.log_temperature_lower,s.log_temperature_upper))
    require(np.array_equal(states[160][0].lo,accepted160.population_lower)
            and np.array_equal(states[160][0].hi,accepted160.population_upper),
            "ACCEPTED_160_SOURCE_DRIFT")
    g=float(m.sdirk.GAMMA)
    require(abs(g-(1-1/math.sqrt(2)))<1e-14,"SOURCE_SDIRK_GAMMA")
    records=[]
    for left,right in INTERVALS:
        pop,lt=states[left]
        t0=native_duration*left/TICKS;t1=native_duration*right/TICKS;mid=(t0+t1)*0.5
        kw=dict(model=model,base=base,parent_pop=pop,parent_logt=lt,total_h=nh,total_he=nhe)
        full=m.run_step(**kw,t0=t0,t1=t1)
        first=m.run_step(**kw,t0=t0,t1=mid)
        require(first.certified,"FIRST_HALF_NOT_CERTIFIED")
        second=m.run_step(model,base,parent_pop=first.population,
            parent_logt=first.log_temperature,t0=mid,t1=t1,total_h=nh,total_he=nhe)
        require(all(s.certified for s in (full,first,second)),"ORIGINAL_THREE_MAPS")
        endpoint=states[right]
        for x,yv in ((second.population.lo,endpoint[0].lo),
                     (second.population.hi,endpoint[0].hi),
                     (second.log_temperature.lo,endpoint[1].lo),
                     (second.log_temperature.hi,endpoint[1].hi)):
            require(np.array_equal(x,yv),"ORIGINAL_ACCEPTED_ENDSTATE_DISAGREEMENT")
        ledger(m,model,full,full.population,t0,t1,nh,nhe)
        ledger(m,model,first,first.population,t0,mid,nh,nhe)
        ledger(m,model,second,second.population,mid,t1,nh,nhe)
        err,width=local_defect_width(m,full,second,nh,nhe)
        dt=t1-t0;h1=mid-t0;h2=t1-mid
        r1=source_quadrature(first,h1,g,0,1)
        r2=source_quadrature(second,h2,g,0,1)
        i1=source_quadrature(first,h1,g,1,0)
        i2=source_quadrature(second,h2,g,1,0)
        rf=source_quadrature(full,dt,g,0,1)
        rlo,rhi=r1[0]+r2[0],r1[1]+r2[1]
        ilo,ihi=i1[0]+i2[0],i1[1]+i2[1]
        require(bool(np.all(rlo<=rhi)) and bool(np.all(ilo<=ihi)),"INTEGRAL_INTERVAL")
        r_min=count_parent_lower((pop.lo,pop.hi),(endpoint[0].lo,endpoint[0].hi))
        ndelta_lo=endpoint[0].lo[:,1]-pop.hi[:,1]
        ndelta_hi=endpoint[0].hi[:,1]-pop.lo[:,1]
        qnet_lo=ilo-rhi;qnet_hi=ihi-rlo
        source_overlap=(qnet_lo<=ndelta_hi)&(qnet_hi>=ndelta_lo)
        source_gap=np.maximum(0.,np.maximum(qnet_lo-ndelta_hi,ndelta_lo-qnet_hi))
        source_gap_rel=source_gap/nh
        net_delta_abs=0.5*(np.abs(ndelta_lo)+np.abs(ndelta_hi))
        aggregate_source_overlap=(sums(qnet_lo)<=sums(ndelta_hi) and
                                  sums(qnet_hi)>=sums(ndelta_lo))
        # This is a direct comparison of discrete stage quadrature vs accepted
        # endpoint values, NOT a presumed theorem about MPRK correctness.
        r= {
          "start_tick":left,"end_tick":right,"proper_duration_s":dt,
          "source_H_caseB_events_integrated_lower":sums(rlo),
          "source_H_caseB_events_integrated_upper":sums(rhi),
          "source_H_ion_events_integrated_lower":sums(ilo),
          "source_H_ion_events_integrated_upper":sums(ihi),
          "gross_H_recomb_chemical_release_lower_erg":sums(rlo)*CHI_H_EV*EV_ERG,
          "gross_H_recomb_chemical_release_upper_erg":sums(rhi)*CHI_H_EV*EV_ERG,
          "conditional_endpoint_min_recomb_events":sums(r_min),
          "min_stage_integral_minus_endpoint_lower_events":sums(rlo-r_min),
          "original_delta_HII_lower":sums(ndelta_lo),
          "original_delta_HII_upper":sums(ndelta_hi),
          "quadrature_net_HII_lower":sums(qnet_lo),
          "quadrature_net_HII_upper":sums(qnet_hi),
          "source_net_HII_interval_overlap":int(np.count_nonzero(source_overlap)),
          "source_net_HII_gap_sum_counts":sums(source_gap),
          "source_net_HII_gap_over_total_abs_original_delta":sums(source_gap)/sums(net_delta_abs),
          "source_net_HII_max_gap_over_H_nuclei":float(np.max(source_gap_rel)),
          "global_source_net_HII_interval_overlap":aggregate_source_overlap,
          "full_vs_twohalf_mid_recomb_difference":sums(0.5*(rf[0]+rf[1])-0.5*(rlo+rhi)),
          "all_original_14_ledgers_include_zero":True,
          "original_source_defect_max":err,"original_public_width_max":width
        }
        records.append(r)
        print(json.dumps({"interval":[left,right],
            "H_CaseB_source_integral":[r["source_H_caseB_events_integrated_lower"],
                                       r["source_H_caseB_events_integrated_upper"]],
            "source_ion_integral":[r["source_H_ion_events_integrated_lower"],
                                    r["source_H_ion_events_integrated_upper"]],
            "conditional_endpoint_min":r["conditional_endpoint_min_recomb_events"],
            "net_HII_source_overlap_cells":r["source_net_HII_interval_overlap"],
            "source_maps":"3/3_CERTIFIED","14_ledgers":"PASS",
            "REI_DAG":"28/88_+0"},sort_keys=True),flush=True)
    out.mkdir(parents=True,exist_ok=True)
    file=out/OUTPUT
    with file.open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=COLUMNS,lineterminator="\n")
        writer.writeheader();writer.writerows(records)
    summary={
      "schema":"BASS_CR_REI_F05_ORIGINAL_ACCEPTED_H_CASEB_NATIVE_STAGE_QUADRATURE_V1",
      "status":"SOURCE_ORIGINAL_ACCEPTED_DISCRETE_STAGE_QUADRATURE_NOT_CONTINUUM_INTEGRAL",
      "source_REI_head":SOURCE_REI_HEAD,"source_REC195_zip_sha256":REC195_ZIP_SHA,
      "source_original_tar_sha256":SOURCE_TAR_SHA,
      "source_original_kernel_sha256":SOURCE_KERNEL_SHA,
      "source_original_accepted160_array_sha256":SOURCE_ARRAY_SHA,
      "state_SHA256_by_tick":{str(i):v[1] for i,v in STATE.items()},
      "source_gamma":g,"source_microtick_seconds":native_duration/TICKS,
      "source_nodes":N,"accepted_intervals":[list(z) for z in INTERVALS],
      "intervals":records,"total_H_caseB_events_quadrature_interval":[
         math.fsum(x["source_H_caseB_events_integrated_lower"] for x in records),
         math.fsum(x["source_H_caseB_events_integrated_upper"] for x in records)],
      "total_gross_H_caseB_binding_release_erg_quadrature_interval":[
         math.fsum(x["gross_H_recomb_chemical_release_lower_erg"] for x in records),
         math.fsum(x["gross_H_recomb_chemical_release_upper_erg"] for x in records)],
      "no_claim_of_exact_continuum_time_integral":True,
      "no_H_Lya_photon_emission_or_escape_inferred":True,
      "no_heat_double_counting":True,
      "original_tick161":"NOT_ACCEPTED",
      "REI_canonical_DAG":"28/88_DELTA0","REI_working_DAG":"33/88_DELTA0",
      "REI_physical_fast_DAG":"4/7_DELTA0","BASS_CR_extension_DAG":"0/3_DELTA0",
      "production":"HOLD","CR_OFF":True,"original_REI_changed":False,
      "native_subagent":"NOT_RUN","distinct_author_referee":"NOT_RUN",
      "output_csv_sha256":sha(file)
    }
    jsonfile=out/"SCIENCE_RESULT.json"
    jsonfile.write_text(json.dumps(summary,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    return summary
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--rei-repo",required=True,type=Path)
    p.add_argument("--rec195-zip",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    run(a.rei_repo,a.rec195_zip,a.out)
