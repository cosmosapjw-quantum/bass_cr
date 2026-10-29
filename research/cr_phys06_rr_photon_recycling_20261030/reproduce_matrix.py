#!/usr/bin/env python3
"""Small source-pinned independent interface for the H/He 2x2 final matrix."""
import csv, hashlib, importlib.util, io, json, tempfile, zipfile
from pathlib import Path
import numpy as np

PIN='89fd528ede24929cb29b51b1edf55f27ad1ea1f7c0a61f976884ebe657e48cb3'
PARENT='research/cr_phys05_rr_window_ionization_20261030/'
C=299792458.0
T=1e10

def matrix(source_zip):
    blob=Path(source_zip).read_bytes()
    if hashlib.sha256(blob).hexdigest()!=PIN:
        raise ValueError('PR130_SOURCE_SHA256_LOCK_FAIL')
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        assert z.testzip() is None
        entries=json.loads(z.read('SOURCE_MANIFEST.json'))['files']
        assert len(entries)==39
        for e in entries:
            b=z.read(e['path'])
            assert hashlib.sha256(b).hexdigest()==e['sha256'] and len(b)==e['size']
        script=z.read(PARENT+'window_ionization.py')
        old=z.read(PARENT+'sources/PR129_ORIGINAL_SOURCE.zip')
    with tempfile.TemporaryDirectory(prefix='phys06_matrix_') as td:
        root=Path(td);(root/'window_ionization.py').write_bytes(script)
        (root/'parent_source.zip').write_bytes(old)
        spec=importlib.util.spec_from_file_location('original_owner',root/'window_ionization.py')
        module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        atoms,density,params,sigma,reference=module.load_sources(root/'parent_source.zip')
    ages=np.asarray(atoms['time_edges_s'],dtype=float)
    rows=[]
    for source in ('H','He'):
        E=atoms[f'photon_{source}_eV']
        W=atoms[f'capture_{source}_bins_m3']
        a=np.stack([sigma[source][tar]*density[tar] for tar in ('HI','HeI')])
        rate=C*a.sum(axis=0);branch=a/a.sum(axis=0)
        for it,target in enumerate(('HI','HeI')):
            vals=[]
            for latest in (True,False):
                absorb=np.zeros_like(E)
                for j in range(4):
                    s=ages[j+1] if latest else ages[j]
                    absorb+=W[j]*branch[it]*(-np.expm1(-rate*(T-s)))
                vals.append(float(np.sum(absorb,dtype=np.float64)))
            rows.append(dict(source=source,target=target,lower_m3=vals[0],upper_m3=vals[1]))
    return rows

if __name__=='__main__':
    import sys
    if len(sys.argv)!=2:raise SystemExit('Usage: python reproduce_matrix.py ORIGINAL_PR130_SOURCE.zip')
    for row in matrix(sys.argv[1]):print(','.join(map(str,row.values())))
