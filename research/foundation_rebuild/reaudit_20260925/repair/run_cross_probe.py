#!/usr/bin/env python3
"""Bounded static probe only. No collision, source mutation, or automatic retry."""
from pathlib import Path
import sys,json,hashlib,time,argparse
import numpy as np

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
FND=REPO/'research/foundation_rebuild'
sys.path[:0]=[str(HERE),str(FND/'src'),str(REPO)]

from bass_foundations.radial_basis import RadialSpec,atomic_bank
from bass_foundations.two_center import Trajectory,symmetric_channels
from cr_repro.observables import projectile_speed_au
from aligned_cross import cross_blocks

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--order',type=int,required=True)
    p.add_argument('--angular',choices=['bessel','uniform'],default='bessel')
    p.add_argument('--nphi',type=int,default=128)
    p.add_argument('--z',type=float,default=-12.)
    p.add_argument('--out',required=True)
    a=p.parse_args()

    out=Path(a.out)
    out.mkdir(parents=True,exist_ok=False)

    spec=RadialSpec(
        radius=64.,elements=40,degree=4,lmax=1,bound_nmax=2,
        positive_per_l=1,positive_emax=2.,quad_order=12,grading=2.
    )
    bank=atomic_bank(spec)
    ch=symmetric_channels(bank)
    v=projectile_speed_au(100.)
    tr=Trajectory(((0,0,0),(2.,0,0)),((0,0,0),(0,0,v)))

    meta={
        'schema':'REAUDIT_STATIC_CROSS_PROBE_V1',
        'source_commit':'8b7fef411ebca8dcdbfb45de542690c821fd7826',
        'spec':spec.__dict__,
        'channel_identities':[c.record() for c in ch],
        'basis_energy_values':[b.energy for b in bank],
        'order':a.order,'angular':a.angular,'nphi':a.nphi,'z':a.z,
        'python':sys.version,'numpy':np.__version__,
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'kernel_sha256':hashlib.sha256((HERE/'aligned_cross.py').read_bytes()).hexdigest(),
        'production_admission':'HOLD','capture_execution_allowed':False
    }
    with (out/'INTAKE.json').open('x') as f:
        json.dump(meta,f,indent=2)

    tic=time.perf_counter()
    result=cross_blocks(
        tr,ch,bank[0].edges,a.z/v,
        order=a.order,angular=a.angular,nphi=a.nphi
    )
    mats={k:x for k,x in result.items() if isinstance(x,np.ndarray)}
    with (out/'matrices.npz').open('xb') as f:
        np.savez_compressed(f,**mats)

    meta.update(
        status='COMPLETED_STATIC_PROBE',
        seconds=time.perf_counter()-tic,
        metadata=result['metadata'],
        matrix_sha256=hashlib.sha256((out/'matrices.npz').read_bytes()).hexdigest(),
        norms={k:float(np.linalg.norm(x)) for k,x in mats.items()}
    )
    with (out/'RESULT.json').open('x') as f:
        json.dump(meta,f,indent=2)
    print(json.dumps({
        'order':a.order,'seconds':meta['seconds'],
        'metadata':meta['metadata'],'norms':meta['norms']
    },indent=2),flush=True)

if __name__=='__main__':
    main()
