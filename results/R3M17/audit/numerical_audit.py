from pathlib import Path
import importlib.util,sys,json,math,tempfile
import numpy as np
ROOT=Path('/workspace/scratch/235b855501c6/bass_cr'); sys.path.insert(0,str(ROOT))
def load(name,file):
 s=importlib.util.spec_from_file_location(name,ROOT/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=load('diag','scripts/r3m16_target_only_hdt.py');a=load('ana','scripts/r3m16_analyze.py');p=load('pair','scripts/r3m13_initial_state_pair.py')
out={'source_commit':'7844bc0d8122070b267ee77c75cb2c9447435155','scope':'small CPU diagnostics only; no production collisions','ray_cancellation':[]}
for eps in [1e-5,1e-7,1e-8,1e-9,1e-11,1e-13]:
 x=np.array([1.,0.],complex);y=np.array([math.cos(eps),math.sin(eps)],complex)
 out['ray_cancellation'].append({'eps':eps,'r3m16':m.ray_distance(x,y,1.),'r3m13':p.ray_distance(x,y,1.)['ray_distance'],'exact':2*math.sin(eps/2)})
# Verify wrapper accepts corrupt metadata; original result bytes are read only.
tmp=Path(tempfile.mkdtemp(prefix='matrix-authority-',dir='/workspace/scratch/235b855501c6/audit'))
bad=json.loads((ROOT/'results/R3M16/collisions/B1_result.json').read_text());bad['status']='checkpoint';bad['config']['grid']['dx']=0.125;bad['config']['energy_keV_per_u']=225;bad['config']['_r3m11_source_digest']='MISMATCH';bad['config']['dt']=0.5
badpath=tmp/'invalid_B1.json';badpath.write_text(json.dumps(bad))
try:
 r=a.analyze(ROOT/'results/R3M15/MATRIX_ANALYSIS.json',ROOT/'results/R3M16/collisions/A1_result.json',badpath,ROOT/'results/R3M16/target_only/A.json',ROOT/'results/R3M16/target_only/B.json')
 out['invalid_matrix_authority']={'rejected':False,'input_status':bad['status'],'input_dx':bad['config']['grid']['dx'],'output_row_dx':r['rows']['B1']['dx'],'output_status':r['status'],'output_decision':r['scientific_decision'],'output_source':r['rows']['B1']['source_digest']}
except Exception as e:out['invalid_matrix_authority']={'rejected':True,'exception':str(e)}
from cr_repro.observables import projectile_speed_au
out['grid_phase']=[]
for name in ['A','B','C']:
 cfg=json.loads((ROOT/f'configs/r3m15/{name}.json').read_text());h=cfg['grid']['dx'];v=projectile_speed_au(100);T=(cfg['z_stop']-cfg['z_start'])/v;n=math.ceil(T/cfg['dt']);dt=T/n
 distance=lambda x,lo:abs((x-lo)/h-.5-round((x-lo)/h-.5))
 px=distance(cfg['b'],cfg['grid']['xlim'][0]);py=distance(0,cfg['grid']['ylim'][0]);
 out['grid_phase'].append({'job':name,'h':h,'projectile_nearest_x_over_h':px,'projectile_nearest_y_over_h':py,'projectile_min_transverse_r_over_h':math.hypot(px,py),'nstep':n,'dt_actual':dt,'nucleus_displacement_per_step_over_h':v*dt/h,'steps_per_grid_crossing':h/(v*dt)})
Path('/workspace/scratch/235b855501c6/audit/numerical_audit.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
