"""Observe original AOCC dynamics without changing integral or propagation code."""
import argparse,json,time
from pathlib import Path
import numpy as np
from cr_repro.aocc import OneElectronAOCC
from cr_repro.util import atomic_json,atomic_npy
p=argparse.ArgumentParser();p.add_argument('--config');p.add_argument('--out');a=p.parse_args();out=Path(a.out)
cfg=json.loads(Path(a.config).read_text());obj=OneElectronAOCC(cfg);start=time.monotonic();steps=[0]
atomic_json(out/'basis.json',{'nbasis':obj.nb,'atomic_energies':obj.eps.tolist(),'retained_energies':obj.epsk.tolist(),'config':cfg})
step=obj.unitary_step
atomic_json(out/'progress.json',{'done':0,'status':'initial_generator'})
def observed(G,y,dt):
 z=step(G,y,dt);steps[0]+=1
 if steps[0]==1 or steps[0]%10==0:
  atomic_npy(out/'y_checkpoint.npy',z)
  atomic_json(out/'progress.json',{'done':steps[0],'elapsed_seconds':time.monotonic()-start,'dt_actual':dt,'status':'in_progress','checkpoint_kind':'orthonormal_frame_y; original CLI has no restart loader'})
 return z
obj.unitary_step=observed
r=obj.run();r['config']=cfg;r['wall_seconds']=time.monotonic()-start;atomic_json(out/'result.json',r)
atomic_json(out/'progress.json',{'done':steps[0],'status':'completed'})
print(json.dumps(r,indent=2))
