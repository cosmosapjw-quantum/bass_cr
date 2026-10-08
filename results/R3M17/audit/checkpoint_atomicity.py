from pathlib import Path
import sys,json,tempfile
sys.path.insert(0,'/workspace/scratch/235b855501c6/bass_cr')
from cr_repro import tdl
from cr_repro.r3m11 import ControlledTDLRunner,file_sha
cfg=dict(energy_keV_per_u=100.,b=2.,backend='numpy',grid=dict(xlim=[-2,2],ylim=[-2,2],zlim=[-2,4],dx=1.),dt=.01,z_start=-1.,z_stop=1.,initial_state='analytic',absorber_width=1.,absorber_power=.25,absorber_reference_dt=.05,checkpoint_stride=1,project_nmax=1,capture_plane=1.)
p=Path(tempfile.mkdtemp(prefix='checkpoint-',dir='/workspace/scratch/235b855501c6/audit'))
ControlledTDLRunner(cfg).run(p,max_steps=1)
old=file_sha(p/'state.npy');original=tdl.atomic_json
def fail(path,value):
 if Path(path).name=='state.json':raise KeyboardInterrupt('fault injection after next state.npy replace, before metadata replace')
 return original(path,value)
tdl.atomic_json=fail
try:ControlledTDLRunner(cfg).run(p,max_steps=1)
except KeyboardInterrupt:pass
finally:tdl.atomic_json=original
try:
 ControlledTDLRunner(cfg).run(p,max_steps=1);error=None
except ValueError as e:error=str(e)
r={'old_sealed_state_preserved':file_sha(p/'state.npy')==old,'metadata_done':json.loads((p/'state.json').read_text())['done'],'resume_error':error,'interpretation':'fail-closed corruption detection works, but previous verified checkpoint cannot be restored in-place'}
Path('/workspace/scratch/235b855501c6/audit/checkpoint_atomicity.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
