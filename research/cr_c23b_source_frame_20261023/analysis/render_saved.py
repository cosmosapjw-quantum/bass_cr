"""Publication figures from existing CSV/JSON only. No source/ODE evaluation."""
from __future__ import annotations
import argparse
import csv
from datetime import datetime,timezone
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parent
UNIT=ROOT.parent
THREAD_KEYS=('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','BLIS_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS')
for k in THREAD_KEYS:os.environ[k]='1'

def write(path,value):
    with path.open('x') as f:json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')

def digest(path):
    b=path.read_bytes();return {'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}

def render(run):
    os.sched_setaffinity(0,{3});t0,c0=time.perf_counter(),time.process_time()
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter,FixedLocator,LogLocator
    pins=json.loads((ROOT/'INPUT_PINS.json').read_text())
    for name,pin in pins['files'].items():
        if digest(UNIT/name)!=pin:raise RuntimeError('SAVED_INPUT_CHANGED:'+name)
    source=UNIT/'source_providers/runs/c23b_pw19_spectral_source_20261023_v1'
    boost=UNIT/'implementation/runs/c23b_boost_and_source_20261023_v2'
    for p in [source/'SUMMARY.json',boost/'SUMMARY.json']:
        if json.loads(p.read_text())['status']!='PASS_SCOPED':raise RuntimeError('INPUT_NOT_COMPLETED_PASS')
    with (source/'photoelectron_atoms.csv').open() as f:
        saved=[r for r in csv.DictReader(f) if float(r['redshift'])==2.479]
    cases={r['channel']:r for r in json.loads((source/'CASES.json').read_text()) if r['redshift']==2.479}
    partitions=json.loads((boost/'PARTITIONS.json').read_text())
    config=json.loads((boost/'INPUT.json').read_text())
    species=('HI','HeI','HeII');labels={'HI':'H I','HeI':'He I','HeII':'He II'}
    colors={'HI':'#0072B2','HeI':'#D55E00','HeII':'#7A5195'}
    minimum=min(float(r['kinetic_eV']) for r in saved);maximum=max(float(r['kinetic_eV']) for r in saved)
    edges=np.logspace(math.floor(math.log10(minimum)),math.ceil(math.log10(maximum)),65)
    histogram=[];bins=[];max_rebin_rel=0.
    for channel in species:
        group=[r for r in saved if r['channel']==channel]
        energies=np.array([float(r['kinetic_eV']) for r in group]);weights=np.array([float(r['number_weight_per_target_s']) for r in group])
        energy_bins,_=np.histogram(energies,bins=edges,weights=energies*weights)
        density=energy_bins/np.diff(np.log(edges))
        total=math.fsum(float(k)*float(w) for k,w in zip(energies,weights))
        max_rebin_rel=max(max_rebin_rel,abs(math.fsum(map(float,energy_bins))-total)/total)
        histogram.append((channel,density))
        for i,value in enumerate(density):bins.append({'channel':channel,'K_lo_eV':float(edges[i]),'K_hi_eV':float(edges[i+1]),'kinetic_eV_per_target_s':float(energy_bins[i]),'kinetic_eV_per_target_s_per_lnK':float(value)})
    with (run/'source_histogram_bins.csv').open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(bins[0]));w.writeheader();w.writerows(bins)
    fractions=[]
    for channel in species:
        case=cases[channel];result=case['result']
        fractions.append({'channel':channel,'redshift':2.479,'mean_K_eV':result['kinetic_eV_per_target_s']/result['number_per_target_s'],
            'below_FS_fraction':result['bins'][0]['kinetic_fraction_of_finite_atomic_source'],
            'in_FS_fraction':result['bins'][1]['kinetic_fraction_of_finite_atomic_source'],
            'above_FS_fraction':result['bins'][2]['kinetic_fraction_of_finite_atomic_source']})
    write(run/'SOURCE_FRACTIONS.json',fractions)
    coverage=[]
    for p in partitions:
        if p['identity'].startswith(('tritium_','neutron_')):
            m=p['moments'];coverage.append({'identity':p['identity'],'u':p['boost_u'],
                'covered_kinetic_fraction':m['covered'][1]/m['all'][1],
                'covered_number':m['covered'][0],'total_kinetic_eV_per_event':m['all'][1]})
    with (run/'boost_coverage.csv').open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(coverage[0]));w.writeheader();w.writerows(coverage)
    outputs=[];figure_extents=[]
    def save(fig,name,width):
        fig.canvas.draw()
        # Record figure-coordinate text extents for residual clipping review.
        renderer=fig.canvas.get_renderer();boxes=[]
        for artist in fig.findobj(matplotlib.text.Text):
            if artist.get_visible() and artist.get_text():
                bounds=artist.get_window_extent(renderer).transformed(fig.transFigure.inverted())
                boxes.append({'text':artist.get_text(),'bbox':[bounds.x0,bounds.y0,bounds.x1,bounds.y1],'font_pt':artist.get_fontsize()})
        figure_extents.append({'figure':name,'width_mm':width,'texts':boxes})
        for ext in ('png','pdf'):
            path=run/(name+'.'+ext)
            if path.exists():raise RuntimeError('CREATE_ONLY_OUTPUT_EXISTS')
            fig.savefig(path,dpi=300,facecolor='white',metadata={'Creator':'BASS_CR C23B saved-output analyzer'})
            outputs.append({'file':path.name,**digest(path),'width_mm':width})
        plt.close(fig)
    for width in (180,90):
        narrow=width==90;font=8.5 if narrow else 9.0
        plt.rcParams.update({'font.family':'DejaVu Sans','font.size':font,'axes.labelsize':font,'axes.titlesize':font+0.5,
            'xtick.labelsize':font-0.2,'ytick.labelsize':font-0.2,'legend.fontsize':font-0.2,'axes.linewidth':.7,
            'pdf.fonttype':42,'ps.fonttype':42,'savefig.bbox':None})
        height=145 if narrow else 135
        fig=plt.figure(figsize=(width/25.4,height/25.4))
        def box(x,y,w,h):return [x/width,y/height,w/width,h/height]
        def note(x,y,s,**kw):return fig.text(x/width,y/height,s,**kw)
        ax=fig.add_axes(box(22,63,64,62) if narrow else box(25,72,150,44))
        note(width/2,height-6,'PW19 primary electron supply',ha='center',fontsize=font+1)
        note(width/2,height-12,'z = 2.479 · saved positive quadrature',ha='center',fontsize=font)
        for channel,density in histogram:
            ax.stairs(np.where(density>0,density,np.nan),edges,baseline=None,label=labels[channel],color=colors[channel],linewidth=1.4)
        ax.axvspan(10,9937.21,color='#008D7F',alpha=.08,zorder=-2)
        ax.axvline(10,color='#555555',ls='--',lw=.7);ax.axvline(9937.21,color='#555555',ls='--',lw=.7)
        ax.set_xscale('log');ax.set_yscale('log');ax.set_xlim(edges[0],edges[-1]);ax.set_ylim(1e-24,2e-11)
        ax.set_xlabel(r'Electron kinetic energy $K$ [eV]')
        ax.set_ylabel('Energy per ln K\n[eV target$^{-1}$ s$^{-1}$]')
        ax.xaxis.set_major_locator(FixedLocator([1e-3,1e-1,10,1e3,1e5]));ax.yaxis.set_major_locator(FixedLocator([1e-24,1e-21,1e-18,1e-15,1e-12]))
        ax.grid(True,which='major',color='#DDDDDD',lw=.5);ax.legend(loc='upper right',ncol=3 if not narrow else 1,frameon=True,facecolor='white',edgecolor='none',framealpha=1.0,handlelength=1.7,columnspacing=.9)
        ax.text(.01,.98,'(a)',transform=ax.transAxes,ha='left',va='top',fontweight='bold')
        below=np.array([r['below_FS_fraction'] for r in fractions]);inside=np.array([r['in_FS_fraction'] for r in fractions]);above=np.array([r['above_FS_fraction'] for r in fractions]);y=np.arange(3)
        if narrow:
            note(8,44,'(b) Kinetic-energy fractions of finite source',fontsize=font)
            axtable=fig.add_axes(box(7,17,79,22));axtable.axis('off')
            rows=[[labels[c],f'{below[i]:.6f}',f'{inside[i]:.6f}',f'{above[i]:.2e}'] for i,c in enumerate(species)]
            table=axtable.table(cellText=rows,colLabels=['Target','Below 10 eV','FS band','Above FS'],
                colWidths=[.15,.28,.28,.29],cellLoc='center',loc='center',bbox=[0,0,1,1])
            table.auto_set_font_size(False);table.set_fontsize(8.0)
            for (r,c),cell in table.get_celld().items():
                cell.set_edgecolor('#D2D2D2');cell.set_linewidth(.35)
                if r==0:cell.set_facecolor('#EAF1F4')
            note(width/2,11,'FS band: 10–9937.21 eV.',ha='center',fontsize=8.0)
            note(width/2,6,'Photon fit support ≤ 50 keV.',ha='center',fontsize=8.0)
            note(width/2,2,'Deposition closure remains open.',ha='center',fontsize=8.0)
        else:
            axbar=fig.add_axes(box(25,29,110,20));axtail=fig.add_axes(box(142,29,33,20))
            axbar.barh(y,below,color='#E69F00',height=.55,label='Below 10 eV',edgecolor='white',linewidth=.3)
            axbar.barh(y,inside,left=below,color='#56B4E9',height=.55,label='10–9937.21 eV',edgecolor='white',linewidth=.3)
            axbar.barh(y,above,left=below+inside,color='#777777',height=.55)
            for i in range(3):
                axbar.text(below[i]/2,i,f'{100*below[i]:.1f}%',ha='center',va='center',fontsize=font-.4)
                axbar.text(below[i]+inside[i]/2,i,f'{100*inside[i]:.1f}%',ha='center',va='center',fontsize=font-.4)
            axbar.set_yticks(y,[labels[c] for c in species]);axbar.set_ylim(2.5,-.7);axbar.set_xlim(0,1)
            axbar.set_xticks([0,.5,1]);axbar.set_xlabel('Kinetic-energy fraction')
            note(25,55,'(b) Finite energy-domain partition',fontsize=font)
            for spine in ['top','right']:axbar.spines[spine].set_visible(False)
            handles_,labels_=axbar.get_legend_handles_labels()
            fig.legend(handles_,labels_,loc='center',bbox_to_anchor=(80/width,10/height),ncol=2,frameon=False,handlelength=1.3,columnspacing=1.0)
            axtail.set_xlim(0,1);axtail.set_ylim(2.5,-.7);axtail.axis('off')
            note(158.5,53,'Above FS fraction',ha='center',fontsize=font-.1)
            for i,fraction in enumerate(above):axtail.text(.5,i,f'{fraction:.2e}',ha='center',va='center',fontsize=font-.3)
            note(width/2,3,'Photon fit support ≤ 50 keV; deposition closure remains open.',ha='center',fontsize=font-.6)
        save(fig,f'primary_electron_source_{width}mm',width)
        # Same saved discrete u samples; display positions are categorical and
        # labelled explicitly, with no interpolated curve or new evaluations.
        height=167 if narrow else 110
        fig=plt.figure(figsize=(width/25.4,height/25.4))
        axes=[fig.add_axes(box(20,93,67,31)),fig.add_axes(box(20,28,67,31))] if narrow else [fig.add_axes(box(21,35,64,42)),fig.add_axes(box(113,35,62,42))]
        note(width/2,height-6,'Rest-moment witnesses under a boost',ha='center',fontsize=font+1)
        if narrow:
            note(width/2,155,'Diagnostic measures',ha='center',fontsize=font-.2)
            note(width/2,150,'Not evaluated beta spectra',ha='center',fontsize=font-.2)
        else:note(width/2,98,'Diagnostic measures · not evaluated beta spectra',ha='center',fontsize=font-.2)
        ugrid=config['boost_u_grid'];ticks=['0',r'$10^{-12}$',r'$10^{-6}$',r'$10^{-3}$','0.05','0.2','1','10'];xs=np.arange(len(ugrid))
        for ax,parent,panel in zip(axes,['tritium','neutron'],['(a)','(b)']):
            for ending,color,marker,label,offset in [('mean_line_diagnostic','#0072B2','o','Mean-energy line',-.09),('endpoints_diagnostic','#D55E00','s','Endpoint mixture',.09)]:
                selected={x['u']:x['covered_kinetic_fraction'] for x in coverage if x['identity']==parent+'_'+ending}
                yy=[selected[u] for u in ugrid]
                ax.scatter(xs+offset,yy,color=color,marker=marker,s=25 if narrow else 27,label=label,zorder=3,linewidths=.7,facecolors='none' if marker=='s' else color)
            ax.set_xticks(xs,ticks,rotation=45 if narrow else 40,ha='right');ax.set_xlim(-.5,7.5)
            ax.set_ylabel('Covered kinetic-energy fraction')
            if parent=='tritium':
                ax.set_ylim(-.055,1.07);ax.set_yticks([0,.25,.5,.75,1]);ax.set_title(panel+' Tritium moment witnesses\nmean 5.690 keV; Q = 18.590 keV',loc='left',fontsize=font)
            else:
                ax.set_yscale('symlog',linthresh=1e-6,linscale=.5);ax.set_ylim(-2e-7,2.5e-3);ax.set_yticks([0,1e-5,1e-4,1e-3]);ax.set_yticklabels(['0',r'$10^{-5}$',r'$10^{-4}$',r'$10^{-3}$']);ax.set_title(panel+' Neutron moment witnesses\nmean 301.370 keV; Q = 782.347 keV',loc='left',fontsize=font)
            ax.grid(True,axis='y',which='major',color='#D8D8D8',lw=.6)
        handles,labels_=axes[0].get_legend_handles_labels();fig.legend(handles,labels_,loc='center',bbox_to_anchor=(.52,(140 if narrow else 91)/height),ncol=2,frameon=False,columnspacing=.7 if narrow else 1.3,handletextpad=.4,fontsize=8.0 if narrow else font-.2)
        note(width/2,14 if narrow else 19,r'Saved boost samples $u=\gamma\beta$',ha='center',fontsize=font)
        note(width/2,8 if narrow else 10,'Coverage: 10–9937.21 eV in the bath frame.',ha='center',fontsize=8.0 if narrow else font-.2)
        note(width/2,3 if narrow else 5,'Discrete u; horizontal offsets are visual only.',ha='center',fontsize=8.0 if narrow else font-.6)
        save(fig,f'boost_finite_energy_coverage_{width}mm',width)
    write(run/'TEXT_EXTENTS.json',figure_extents)
    write(run/'OUTPUTS.json',outputs)
    summary={'run_id':run.name,'status':'RENDERED_AWAITING_VISUAL_REVIEW','input_files':pins['files'],'new_physics_execution':0,'source_provider_calls':0,'ODE':0,'historical_reruns':0,
        'saved_source_atoms_consumed':len(saved),'saved_witness_partitions_consumed':len(coverage),'histogram_bins_per_channel':len(edges)-1,
        'histogram_energy_sum_relative_max':max_rebin_rel,'figure_variants':4,'PNG':4,'PDF':4,'native_threads':1,'worker_cpu':3,'coordinator_cpu':6,
        'worker_wall_s':time.perf_counter()-t0,'worker_cpu_s':time.process_time()-c0,'peak_RSS_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'global_error_bound':None,'interpolation_accuracy_claim':False,'finished_utc':datetime.now(timezone.utc).isoformat()}
    write(run/'SUMMARY.json',summary);print(json.dumps(summary,ensure_ascii=False))
    return 0

def dispatch(run_id):
    if not run_id or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789_-' for c in run_id):raise ValueError('FRESH_SAFE_RUN_ID_REQUIRED')
    from resource_control import observe_resources
    observed=observe_resources();run=ROOT/'runs'/run_id;run.mkdir(parents=True,exist_ok=False);write(run/'RESOURCE_OBSERVED.json',observed)
    spare,mem=observed.get('cpu_quota_spare_cores'),observed.get('memory_available_bytes')
    if not {3,6}.issubset(os.sched_getaffinity(0)) or spare is None or mem is None or not observed.get('memory_observation_complete') or spare<1.2 or mem<768*1024**2:raise RuntimeError('RESOURCE_NOT_ADMITTED')
    leases=Path('/tmp/rei-bianchi-cooperative-leases');leases.mkdir(exist_ok=True);mine=leases/(run_id+'.json')
    with (leases/'leases.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);seen=[]
        for p in leases.glob('*.json'):
            doc=json.loads(p.read_text());entries=doc.get('leases',[doc])
            if not isinstance(entries,list):raise RuntimeError('UNKNOWN_LEASE')
            for item in entries:
                if not isinstance(item,dict) or not isinstance(item.get('cpus'),list) or any(type(c) is not int for c in item['cpus']):raise RuntimeError('UNKNOWN_CPU_LEASE')
                if {3,6}&set(item['cpus']):raise RuntimeError('CPU_LEASE_CONFLICT')
            seen.append({'file':str(p),**digest(p)})
        lease={'schema':'C21_CPU_LEASES_V1','leases':[{'owner':run_id,'cpus':[3,6],'pid':os.getpid()}]};write(mine,lease);write(run/'LEASE.json',dict(lease,other_leases=seen,protected_cpu55=True,native_threads=1))
    try:
        os.sched_setaffinity(0,{6});write(run/'ANALYZER_IDENTITY.json',{'files':{n:digest(ROOT/n) for n in ['render_saved.py','resource_control.py','INPUT_PINS.json']}})
        proc=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--worker',str(run)],capture_output=True,text=True,timeout=60,env=os.environ.copy())
        with (run/'STDOUT.txt').open('x') as f:f.write(proc.stdout)
        with (run/'STDERR.txt').open('x') as f:f.write(proc.stderr)
        write(run/'DISPATCH_COMPLETE.json',{'returncode':proc.returncode,'timeout_s':60});print(proc.stdout)
        if proc.returncode:print(proc.stderr,file=sys.stderr)
        return proc.returncode
    finally:
        with (leases/'leases.lock').open('a+') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            if mine.exists() and json.loads(mine.read_text())==lease:mine.unlink()
        write(run/'LEASE_RELEASED.json',{'owner':run_id,'utc':datetime.now(timezone.utc).isoformat()})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--run-id');p.add_argument('--worker',type=Path);args=p.parse_args()
    sys.exit(render(args.worker) if args.worker else dispatch(args.run_id))
