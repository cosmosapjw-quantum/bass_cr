"""Create-only, CPU3, one-thread audit of source data and the finite operator.

No ODE, upstream code execution, cosmological evolution, or physical source
normalization is performed. The spectra below are declared diagnostic inputs.
"""
from __future__ import annotations

import csv
from datetime import datetime, timezone
from decimal import Decimal, localcontext
import hashlib
import json
from math import fsum, isfinite, sqrt
import os
from pathlib import Path
import time

from fs2010_operator import AUTHOR_GRID, CONTRACTED_COLUMNS, FS2010Response, PLSpectrum, affine_product_integral


BASE = Path(__file__).resolve().parent
OUT = BASE / "c23a_fast_electron_source_audit_20261023_v1"


def write_json(name, value):
    with (OUT / name).open("x", encoding="utf-8") as f:
        json.dump(value, f, indent=2, ensure_ascii=False, allow_nan=False)
        f.write("\n")


def reference_gauss(response, spectrum, xi):
    # Independent exact degree-three quadrature; do not call prepare or the
    # Bernstein-product implementation.
    knots = sorted(set(spectrum.energy) | {e for e in response.energy if spectrum.energy[0] < e < spectrum.energy[-1]})
    terms = [[] for _ in range(7)]
    for a, b in zip(knots[:-1], knots[1:]):
        mid, half = (a + b) / 2, (b - a) / 2
        for sign in (-1, 1):
            e = mid + sign * half / sqrt(3)
            q = spectrum.at(e)
            y = response.at(e, xi)
            for k, v in enumerate(y):
                terms[k].append(half * q * v * (e if k < 3 else 1.0))
    return tuple(fsum(v) for v in terms)


def main():
    start_wall, start_cpu = time.perf_counter(), time.process_time()
    OUT.mkdir(exist_ok=False)
    before = sorted(os.sched_getaffinity(0))
    if 3 not in before:
        raise RuntimeError("assigned CPU3 unavailable")
    os.sched_setaffinity(0, {3})
    write_json("LEASE_START.json", {"owner":"/root/cr_deposition", "pid":os.getpid(), "cpu":3, "affinity_before":before,"native_threads":1,"root_assignment":"CPU3 audit only, no ODE", "UTC":datetime.now(timezone.utc).isoformat()})
    src = BASE / "upstream/x_int_tables"
    response = FS2010Response(src, axis="published_c_axis")
    selected = FS2010Response(src, axis="unambiguous_high_ionization")
    checks = []
    def check(name, condition, **extra):
        record = {"name":name,"result":"PASS" if condition else "FAIL",**extra}
        checks.append(record)
        return condition

    manifest, conflicts, source_sums, lya_residuals = [], [], [], []
    for i, (xi, fname) in enumerate(AUTHOR_GRID):
        file = src / fname
        raw = file.read_bytes()
        h = response.headers[i]
        x_from_H = 1-h[0]
        x_from_He = h[2]
        mismatch = max(abs(xi-x_from_H),abs(xi-x_from_He))
        row = {"file":fname,"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest(),"C_xHII":xi,"header_fHI_fHeI_fHeII_z_T":h,"xHII_from_1_minus_fHI":x_from_H,"header_minus_C_xHeII":x_from_He-xi,"He_fraction_sum_minus_one":h[1]+h[2]-1}
        manifest.append(row)
        if mismatch > 5.1e-7 or abs(h[1]+h[2]-1)>5.1e-7:
            conflicts.append(row)
        for e, v in zip(response.energy, response.rows[i]):
            source_sums.append(fsum(v[:3])-1)
            lya_residuals.append(10.2*v[3]/e-v[2])
    check("all_3612_table_nodes_exact",all(response.at(e,xi)==row for xi,rows in zip(response.ionized_grid,response.rows) for e,row in zip(response.energy,rows)),nodes=14*258)
    convex = []
    max_bary_error = 0.0
    for i in range(len(response.ionized_grid)-1):
        x = (response.ionized_grid[i]+response.ionized_grid[i+1])/2
        for j in range(len(response.energy)-1):
            e=(response.energy[j]+response.energy[j+1])/2
            got=response.at(e,x)
            corners=[response.rows[ii][jj] for ii in [i,i+1] for jj in [j,j+1]]
            for k,g in enumerate(got):
                expected=fsum(v[k] for v in corners)/4
                max_bary_error=max(max_bary_error,abs(g-expected)/max(1.0,abs(expected)))
                convex.append(min(v[k] for v in corners)-1e-12 <= g <= max(v[k] for v in corners)+1e-12)
    check("bilinear_midpoint_and_convex_hull",all(convex) and max_bary_error<3e-14,cells=13*257,max_normalized_barycentric_error=max_bary_error)

    decimal_errors=[]
    with localcontext() as ctx:
        ctx.prec=70
        for a,b,pairs in [(1.0,3.0,((1.0,4.0),(2.0,5.0))), (10.0,10.2,((0.1,0.7),(0.25,0.9),(10.0,10.2))), (100.0,10000.0,((1e-8,3e-11),(0.999,0.01),(100.0,10000.0)))]:
            coef=[Decimal(1)]
            for lo,hi in pairs:
                lo,hi=Decimal(str(lo)),Decimal(str(hi))
                nxt=[Decimal(0)]*(len(coef)+1)
                for j,v in enumerate(coef):
                    nxt[j]+=v*lo;nxt[j+1]+=v*(hi-lo)
                coef=nxt
            expected=(Decimal(str(b))-Decimal(str(a)))*sum(v/Decimal(j+1) for j,v in enumerate(coef))
            got=affine_product_integral(a,b,*pairs)
            decimal_errors.append(abs(got-float(expected))/max(abs(float(expected)),1e-300))
    check("positive_Bernstein_integrals_vs_70digit_monomial",max(decimal_errors)<1e-13,max_relative_error=max(decimal_errors))

    invalid = []
    for e,x in [(9,0.1),(10000,0.1),(100,0),(100,1),(float("nan"),0.1),(100,float("inf"))]:
        try:response.at(e,x);invalid.append(False)
        except ValueError:invalid.append(True)
    for args in [((10,20),(1,-1)),((10,10),(1,1)),((10,float("nan")),(1,1))]:
        try:PLSpectrum(*args);invalid.append(False)
        except ValueError:invalid.append(True)
    try:selected.at(100,0.05);invalid.append(False)
    except ValueError:invalid.append(True)
    try:response.prepare(PLSpectrum((9.0,20.0),(1.0,1.0)));invalid.append(False)
    except ValueError:invalid.append(True)
    try:response.require_physical_coupling(x_HII=.1,x_HeII=.1,x_HeIII=0.,source_He_over_H=None,model_He_over_H=.08,closure_resolved=False);invalid.append(False)
    except ValueError:invalid.append(True)
    try:response.require_physical_coupling(x_HII=.1,x_HeII=.2,x_HeIII=0.,source_He_over_H=.08,model_He_over_H=.08,closure_resolved=True);invalid.append(False)
    except ValueError:invalid.append(True)
    check("fail_closed_invalid_domain_and_gas_contract",all(invalid),cases=len(invalid))

    spectra=[]
    energies=(10.0,10.2,13.6,24.6,54.4,100.0,300.0,1000.0,3000.0,9937.21)
    for power in [0.0,1.5,2.5]:
        s=PLSpectrum(energies,tuple(e**(-power) for e in energies))
        scale=s.injected_energy()
        spectra.append((power,PLSpectrum(energies,tuple(q/scale for q in s.number_rate))))
    records=[];rel_errors=[];source_bound=max(abs(v) for v in source_sums)
    for power,spectrum in spectra:
        prepared=response.prepare(spectrum)
        for xi in (0.0001,0.003,0.01,0.03,0.1,0.3,0.5,0.9,0.999):
            got=prepared.at(xi);ref=reference_gauss(response,spectrum,xi)
            errs=[abs(got[k]-v)/max(abs(v),1e-300) for k,v in zip(CONTRACTED_COLUMNS,ref)]
            rel_errors.extend(errs)
            rec={"diagnostic_PL_power_at_nodes":power,"xi_C_axis":xi,**got,"max_reference_relative_error":max(errs)}
            records.append(rec)
    check("prepared_vs_independent_Gauss2",max(rel_errors)<2e-13,spectra=3,xi_queries_per_spectrum=9,max_relative_error=max(rel_errors))
    check("source_closure_defect_convex_bound",all(abs(r['reported_energy_defect'])<=source_bound*r['injected_kinetic_energy']+1e-14 for r in records),measured_source_bound=source_bound)
    check("nonnegative_contracted_source_channels",all(r[k]>=0 for r in records for k in CONTRACTED_COLUMNS))
    check("source_endpoint_inclusion",response.at(9937.21,0.999)==response.rows[-1][-1])
    check("unambiguous_subgrid_reuses_exact_rows",selected.rows==response.rows[9:] and selected.ionized_grid==response.ionized_grid[9:])

    # Compare current author-table values with four printed 3-keV entries.
    # The paper values are only decimal-rounded reference points, not a full
    # raw-table certification and not an authority to overwrite downloaded data.
    published_heat={0.0001:0.126,0.01:0.319,0.1:0.668,0.9:0.973,0.999:0.979}
    paper_check=[{"xi":x,"paper_Table1_heat_at_3keV":v,"downloaded_table_interpolated_heat_at_3keV":response.at(3000.,x)[1],"difference":response.at(3000.,x)[1]-v} for x,v in published_heat.items()]

    benchmark_spectrum=spectra[1][1]
    prep_start=time.perf_counter();prepared=response.prepare(benchmark_spectrum);prep_wall=time.perf_counter()-prep_start
    xqueries=tuple(.1+i*.8/15 for i in range(16))
    reference_start=time.perf_counter();refs=[reference_gauss(response,benchmark_spectrum,x) for x in xqueries];reference_wall=time.perf_counter()-reference_start
    prepared_start=time.perf_counter();fast=[prepared.at(x) for x in xqueries];prepared_wall=time.perf_counter()-prepared_start
    bench={"scope":"same frozen piecewise-linear number spectrum; 16 ionized-fraction queries; excludes preparation from query ratio", "queries":16,"intervals":prepared.interval_count,"prepare_wall_s":prep_wall,"reference_query_wall_s":reference_wall,"prepared_query_wall_s":prepared_wall,"observed_query_wall_ratio":reference_wall/prepared_wall,"stable_or_end_to_end_speedup":"NOT_ESTABLISHED","asymptotic_operation_reduction":"prepare O(Nxi*Nenergy*Nchannel), then O(Nchannel) per xi query instead of O(Nenergy*Nchannel)"}
    write_json("SOURCE_TABLES_MANIFEST.json",manifest)
    write_json("SOURCE_DEFECTS.json",{"axis_header_conflicts":conflicts,"max_abs_reported_channel_sum_minus_one":source_bound,"channel_sum_minus_one_range":[min(source_sums),max(source_sums)],"max_fheat":max(row[1] for rows in response.rows for row in rows),"max_Lya_fraction_minus_excitation":max(lya_residuals),"paper_table_check":paper_check,"upstream_C_unsafe_reader":"char label[] = \" \"; unbounded fscanf %s exceeds allocation on first header token; not executed", "source_table_He_over_H":None,"normalization":"RAW_VALUES_PRESERVED_NO_CLIP_NO_RENORMALIZE"})
    write_json("SPECTRAL_RESULTS.json",records)
    with (OUT/"SPECTRAL_RESULTS.csv").open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
    write_json("BENCHMARK.json",bench)
    failure_count=sum(c['result']=='FAIL' for c in checks)
    result={"status":"PASS_SCOPED" if failure_count==0 else "FAIL","checks":checks,"failure_count":failure_count,"source_rows":3612,"physical_coupling":"NOT_ADMITTED_SOURCE_CONTRACT_OPEN","global_error_bound":None,"new_ODE":0,"old_ODE_reruns":0,"upstream_code_executed":False,"resources":{"assigned_cpu":3,"actual_affinity":sorted(os.sched_getaffinity(0)),"native_threads":1,"wall_s":time.perf_counter()-start_wall,"cpu_s":time.process_time()-start_cpu},"four_axes":{"EXECUTION":"finite source audit and independent operator checks completed; ODE0","PUBLICATION":"LOCAL_PACKET_FOR_ROOT_INTEGRATION","BACKUP":"PENDING_ROOT_CHECKPOINT","DAG":"R1-R9 source packet, C1-C8 finite operator; source gas/energy closure prevents full 21-population coupling"}}
    write_json("RESULT.json",result)
    write_json("LEASE_COMPLETE.json",{"owner":"/root/cr_deposition","pid":os.getpid(),"cpu":3,"status":"RELEASED","UTC":datetime.now(timezone.utc).isoformat()})
    print(json.dumps({"status":result['status'],"checks":len(checks),"failure_count":failure_count,"resources":result['resources'],"max_reference_relative_error":max(rel_errors),"source_channel_defect":source_bound,"axis_conflicts":len(conflicts),"paper_table_check":paper_check,"benchmark":bench},indent=2))
    if failure_count:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
