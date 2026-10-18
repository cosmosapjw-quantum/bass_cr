"""Bounded coordinate study; common fixtures, never infer native validity."""
from pathlib import Path
import argparse,time,traceback
import numpy as np
from run_experiment import make_fixture,run_reference,write_json
from event_coupler import ManufacturedMicro
from native_micro import NativeMicro


def study(out,native=None):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);rows=[]
    for dx,opacity in [(1e-4,1e-3),(1e-4,1.),(1e-3,1.)]:
        f=make_fixture(a0=.09,dx=dx,opacity_scale=opacity)
        case={'fixture_sha256':f.digest,'a0':.09,'dx':dx,'opacity_scale':opacity,'runs':{}}
        for name,coordinate,tol in [('population','population',2e-10),('tau','optical-depth',2e-10),('tau_tight','optical-depth',2e-12)]:
            folder=out/f'dx{dx:g}_opacity{opacity:g}_{name}'
            provider=NativeMicro([str(Path(native).resolve())],folder,15.,20000) if native else ManufacturedMicro()
            start=time.monotonic()
            try:
                result=run_reference(f,provider,coordinates=coordinate,rtol=tol,atol=tol*1e-3)
                case['runs'][name]={'status':'SUCCESS','result':result,'wall_s':time.monotonic()-start}
            except Exception as e:
                case['runs'][name]={'status':'FAILURE','type':type(e).__name__,'error':str(e),'traceback':traceback.format_exc(),'wall_s':time.monotonic()-start}
            finally:
                if native:provider.close()
            write_json(out/f'dx{dx:g}_opacity{opacity:g}_{name}.json',case['runs'][name])
        if all(case['runs'][k]['status']=='SUCCESS' for k in ('tau','tau_tight')):
            a=case['runs']['tau']['result'];b=case['runs']['tau_tight']['result']
            delta=np.abs(np.asarray(a['gas'])-b['gas'])
            case['tolerance_difference']={'max_fraction':float(delta[:3].max()),'thermal_eV_H':float(delta[3]),'temperature_K':abs(a['temperature_K']-b['temperature_K']),
                'max_photon_H':float(np.max(abs(np.asarray(a['photons'])-b['photons'])))}
        rows.append(case)
    result={'schema':'C21F_COORDINATE_STUDY_V1','native_execution':native is not None,'cases':rows,
        'scope':'Fixed three-energy GL2 impulses and identical microphysical kernel; coordinate and solver-tolerance comparison, not native/source/spectral convergence.'}
    write_json(out/'RESULTS.json',result)
    for row in rows:print(row['dx'],row['opacity_scale'],{k:v['status'] for k,v in row['runs'].items()},row.get('tolerance_difference'))
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--native',type=Path)
    a=p.parse_args();study(a.out,a.native)
