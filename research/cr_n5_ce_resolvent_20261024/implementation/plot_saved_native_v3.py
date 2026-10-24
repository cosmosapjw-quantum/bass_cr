"""Saved JSON only: no providers, matrix construction or scientific solve."""
import argparse,csv,hashlib,json,time
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def writej(p,obj):
    with p.open('x') as f:json.dump(obj,f,indent=2,allow_nan=False);f.write('\n')
def run(unit,out):
    start=time.process_time();v3=unit/'runs/n5_ce_resolvent_native_knot_primary_20261024_v3';v2=unit/'runs/n5_ce_resolvent_recovery_primary_20261024_v2'
    files=[v3/'SOURCE_WEIGHTED_RESULTS.json',v3/'FINITE_COMPARISONS.json',v3/'MATRIX_CASES.json',v2/'FINITE_COMPARISONS.json'];inputs=[{'path':str(p.relative_to(unit)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
    rows=json.loads(files[0].read_text());comp=json.loads(files[1].read_text());cases=json.loads(files[2].read_text());oldcomp=json.loads(files[3].read_text());finest=[r for r in rows if r['N']==2048 and r['R']==80]
    metrics={'all_matrix_local_checks_PASS':all(r['pass'] for r in cases),'all_source_local_checks_PASS':all(r['local_pass'] for r in rows),'all_comparison_gates_PASS':all(r['pass'] for r in comp),'max_linear_scaled_residual':max(r['checks']['linear_scaled_residual'] for r in cases),'max_partition_abs_defect':max(r['checks']['partition_max_abs'] for r in cases),'max_generator_scaled_defect':max(r['generator_scaled_defect'] for r in cases),'max_grid_probability_relative_change':max(r['relative_2048_1024']['P_active'] for r in comp if r['type']=='grid'),'max_grid_event_energy_relative_change':max(r['relative_2048_1024']['conditional_incoming_eV'] for r in comp if r['type']=='grid'),'max_grid_event_time_relative_change':max(r['relative_2048_1024']['conditional_event_time_s'] for r in comp if r['type']=='grid'),'max_boundary_relative_probability_change':max(r['relative_R40_R80'] for r in comp if r['type']=='boundary'),'minimum_native_spacing_eV':min(r['minimum_spacing_eV'] for r in cases)}
    writej(out/'NUMERIC_EXTRACTION.json',{'source':'saved outputs only','input_pins':inputs,'metrics':metrics,'R80_N2048_rows':finest,'scope':'Conditional finite-state result; no continuum/global certificate, physical error band or thermal assimilation.'})
    tab=[]
    for r in finest:
        for ch in ['2S','2P','sum']:tab.append({'z':r['z'],'chi':r['chi'],'channel':ch,**r['values'][ch]})
    with (out/'FINEST_RESULTS.csv').open('x',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(tab[0]));writer.writeheader();writer.writerows(tab)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
    fig,axes=plt.subplots(1,2,figsize=(12.8,5.2),gridspec_kw={'width_ratios':[1.1,1.]});ax,bx=axes
    x=list(range(len(finest)));s=[r['values']['2S']['P_active']*1e5 for r in finest];p=[r['values']['2P']['P_active']*1e5 for r in finest]
    ax.bar(x,s,color='#287d8e',width=.65,label='1s → 2s');ax.bar(x,p,bottom=s,color='#db9343',width=.65,label='1s → 2p')
    ax.set_xticks(x,[f"{r['z']}\nχ={r['chi']:g}" for r in finest]);ax.set_xlabel('Source redshift and first-entry cutoff');ax.set_ylabel('Active-source first-CE probability × 10⁵');ax.set_title('(a) Channel-resolved first-event probabilities',loc='left',pad=13);ax.legend(frameon=False,loc='upper left');ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True)
    groups=[(chi,ch) for chi in [1.5,3.] for ch in ['2S','2P','sum']]
    def worst(data,chi,ch):return 100*max(r['relative_2048_1024']['P_active'] for r in data if r['type']=='grid' and r['chi']==chi and r['channel']==ch)
    point=[worst(oldcomp,chi,ch) for chi,ch in groups];native=[worst(comp,chi,ch) for chi,ch in groups];xx=list(range(6))
    bx.bar([k-.18 for k in xx],point,width=.34,color='#aab5bc',label='Original point grid (v2)');bx.bar([k+.18 for k in xx],native,width=.34,color='#345e9a',label='Native-knot union (v3)')
    bx.axhline(.5,color='#b34848',ls='--',lw=1.3,label='Frozen 0.5% criterion');bx.set_xticks(xx,[f'{ch}\nχ={chi:g}' for chi,ch in groups]);bx.set_ylabel('2048 vs 1024 relative probability change (%)');bx.set_title('(b) Saved finite-grid comparisons',loc='left',pad=13);bx.legend(frameon=False,fontsize=8.5,loc='upper right');bx.set_ylim(0,max(point)*1.25);bx.grid(axis='y',alpha=.18);bx.set_axisbelow(True)
    fig.suptitle('H I first excitation before EE first entry — native-source-knot finite chain',fontsize=13,y=.97)
    fig.text(.5,.025,'T = 10,000 K; nₑ = 0.14 cm⁻³; n₁ₛ = 0.9 cm⁻³; R80 primary. Finite comparisons are not continuum or physical error certificates.',ha='center',fontsize=9,color='#444444')
    fig.subplots_adjust(left=.075,right=.985,top=.83,bottom=.18,wspace=.28)
    fig.savefig(out/'CE_NATIVE_KNOT_DIAGNOSTIC.png',dpi=180);fig.savefig(out/'CE_NATIVE_KNOT_DIAGNOSTIC.svg');plt.close(fig)
    writej(out/'PLOT_RECEIPT.json',{'status':'PASS','saved_outputs_only':True,'new_ODE':0,'new_provider_evaluation':0,'new_matrix':0,'new_solve':0,'input_pins':inputs,'plot_process_cpu_after_import_s':time.process_time()-start,'scope':'Import CPU is included only by enclosing process receipt, not this internal timer.'})
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--unit',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();run(a.unit,a.output)
