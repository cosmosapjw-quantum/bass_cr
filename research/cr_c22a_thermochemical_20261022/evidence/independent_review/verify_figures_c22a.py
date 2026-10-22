#!/usr/bin/env python3
"""Check final C22A artifacts, raw/CSV binding and shared time-redshift axes.

No science source, solver, model, or RHS is imported.  PNG visual inspection is
an explicitly separate assistant observation documented in the receipt.
"""
from __future__ import annotations
import os
os.environ['MPLBACKEND']='Agg'
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
import argparse,csv,hashlib,io,json,math,sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--project',type=Path,required=True)
parser.add_argument('--analysis',default='analysis_v3')
parser.add_argument('--run-id',default='c22a_finite_uv_bdf_20261022_v1')
parser.add_argument('--out',type=Path,required=True)
args=parser.parse_args()
unit=args.project.resolve()/'research/cr_c22a_thermochemical_20261022'
directory=unit/args.analysis
run=unit/'runs'/args.run_id
def sha(b):return hashlib.sha256(b).hexdigest()
def loadj(p):return json.loads(p.read_bytes())
manifest=loadj(directory/'ARTIFACTS.json')
artifact_records=[]
for row in manifest['files']:
    raw=(directory/row['name']).read_bytes()
    assert len(raw)==row['size_bytes'] and sha(raw)==row['sha256'],row['name']
    artifact_records.append({**row,'verified':True})
assert len(artifact_records)==9
summary=loadj(directory/'SUMMARY.json')
assert summary['status']=='COMPLETE_SAVED_DATA_ANALYSIS'
assert summary['plot_contract']['saved_value_clipping_or_floor']=='NONE'
assert summary['source_identity_sha256']==loadj(run/'SOURCE_IDENTITY.json')['identity_sha256']
histories={}
raw_bindings={}
for name,row in summary['cases'].items():
    raw=(run/'cases'/name/'history.npz').read_bytes()
    assert sha(raw)==row['history_sha256']
    with np.load(io.BytesIO(raw),allow_pickle=False) as z:histories[name]={k:z[k].copy() for k in z.files}
    raw_bindings[name]={'sha256':sha(raw),'size_bytes':len(raw),'same_hashed_bytes_loaded':True}
history_bytes=(directory/'HISTORY.csv').read_bytes()
rows=list(csv.DictReader(io.StringIO(history_bytes.decode())))
assert len(rows)==603
counts={name:0 for name in histories}; numeric_cells=0
for row in rows:
    name=row['name'];i=counts[name];h=histories[name]
    for key,string in row.items():
        if key=='name':continue
        got=float(string)
        if key=='elapsed_Myr':want=h['proper_elapsed_s'][i]/(365.25*86400*1e6)
        elif key.startswith('UV_cohort_'):want=h['UV_photons_per_H'][i,int(key.split('_')[2])-1]
        else:want=h[key][i]
        assert got==float(want),(name,i,key)
        numeric_cells+=1
    counts[name]+=1
assert all(n==201 for n in counts.values())
endpoint_rows=list(csv.DictReader(io.StringIO((directory/'ENDPOINTS.csv').read_text())))
assert len(endpoint_rows)==3
endpoint_cells=0
for row in endpoint_rows:
    h=histories[row['name']]
    for key,string in row.items():
        if key=='name':continue
        if key=='elapsed_Myr':want=h['proper_elapsed_s'][-1]/(365.25*86400*1e6)
        elif key=='redshift':want=h['z'][-1]
        elif key=='UV_photons_per_H_total':want=np.sum(h['UV_photons_per_H'][-1])
        else:want=h[key][-1]
        assert float(string)==float(want),(row['name'],key)
        endpoint_cells+=1

# Reconstruct only the axis helper, not the scientific plot/export pipeline.
sys.dont_write_bytecode=True
sys.path.insert(0,str(unit))
import analyze
analyzer_bytes=(unit/'analyze.py').read_bytes()
def independent_linear_interp(target,x,y):
    i=min(max(int(np.searchsorted(x,target))-1,0),len(x)-2)
    return float(y[i]+(target-x[i])*(y[i+1]-y[i])/(x[i+1]-x[i]))
axis_rows=[]
for name,h in histories.items():
    t=h['proper_elapsed_s']/(365.25*86400*1e6);z=h['z']
    assert np.all(np.diff(t)>0) and np.all(np.diff(z)<0)
    fig,ax=plt.subplots(figsize=(7,3));analyze.axes_time_redshift(ax,h)
    sec=fig.axes[-1];fig.canvas.draw()
    assert ax.get_xscale()==sec.get_xscale()=='symlog'
    assert ax.xaxis.get_transform().linthresh==sec.xaxis.get_transform().linthresh==1e-5
    marks=[int(t.get_text()) for t in sec.get_xticklabels()]
    assert marks==[20,10,2]
    loc=sec.get_xticks();records=[]
    for mark,actual in zip(marks,loc):
        expected=independent_linear_interp(mark,z[::-1],t[::-1])
        assert math.isclose(float(actual),expected,rel_tol=2e-15,abs_tol=2e-12)
        bottom_x=float(ax.transData.transform((expected,0))[0])
        top_x=float(sec.transData.transform((actual,0))[0])
        delta=abs(bottom_x-top_x)
        assert delta<1e-7
        records.append({'redshift':mark,'time_Myr_from_raw':expected,
                        'time_Myr_used_by_top_axis':float(actual),
                        'top_bottom_display_pixel_difference':delta})
    axis_rows.append({'case':name,'scale':'shared_symlog','linthresh_Myr':1e-5,
                      'z_ticks':records,'same_case_mapping':True})
    plt.close(fig)
report={
 'schema':'C22A_FINAL_FIGURE_AND_CSV_REVIEW_V1',
 'analysis':args.analysis,'decision':'PASS_SCOPED_FINAL_V3_ONLY',
 'execution':{'ODE':0,'RHS':0,'scientific_model_imports':0,'axis_helper_figures':3},
 'analyzer_sha256':sha(analyzer_bytes),
 'artifacts':artifact_records,'raw_bindings':raw_bindings,
 'CSV':{'history_rows':len(rows),'case_rows':counts,'numeric_cells_exact_float_roundtrip':numeric_cells,
        'history_bytes':len(history_bytes),'history_sha256':sha(history_bytes),
        'endpoint_rows':len(endpoint_rows),'endpoint_numeric_cells_exact_float_roundtrip':endpoint_cells,
        'clipping_or_flooring':'NONE'},
 'axes':axis_rows,
 'visual_review':{'method':'Assistant inspected the three actual analysis_v3 PNGs through view_image before this check',
                  'figures':['THERMOCHEMISTRY_finite_uv_lrs.png','THERMOCHEMISTRY_finite_uv_flrw.png','THERMOCHEMISTRY_dark_expansion.png'],
                  'result':'PASS_SCOPED',
                  'observations':['Temperature/electron peaks and late decline match saved-data magnitudes.',
                                  'The three selected redshift labels use actual per-case time coordinates and the same symlog transform.',
                                  'Residual zero and small signed negative populations/photon values remain visible; no floor is used.',
                                  'Cumulative RR export and expansion work are separately labeled.',
                                  'Number-residual exponent is in the y-axis label, avoiding the former redshift-20 offset overlap.',
                                  'Titles, labels and legends remain readable; no material overlap in the final inspected PNGs.'],
                  'limits':'PNG visual review only; PDFs are byte/hash checked, not separately rendered. Dark no-UV photon wiggles are numerical residuals near 1e-31, not a detected photon source.'},
 'rejected_versions':{'analysis_v1':'REJECTED; parent-recorded axis mismatch and truncated CSV/manifest mismatch, root cause unresolved',
                      'analysis_v2':'REJECTED_VISUAL_LAYOUT; final approval is only analysis_v3'},
 'stage':{'EXECUTION':'NO_ODE_FINAL_ARTIFACT_REVIEW_COMPLETE','PUBLICATION':'PARENT_OWNED','BACKUP':'PARENT_OWNED',
          'DAG':'Final analysis_v3 figures/CSV pass scoped; original failed reference and physics OPEN states unchanged'},
 'global_error_bound':None,
 'check_script_sha256':sha(Path(__file__).read_bytes())}
with args.out.open('x') as f:json.dump(report,f,indent=2,allow_nan=False);f.write('\n')
print(json.dumps({'decision':report['decision'],'CSV':report['CSV'],'axes':axis_rows,'output':str(args.out)},indent=2))
