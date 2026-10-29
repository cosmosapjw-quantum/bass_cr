"""Independent Decimal80 consumer: represented-binary64 source atoms, no production import."""
import argparse,zipfile,hashlib,json,io,csv
from pathlib import Path
from decimal import Decimal, localcontext
import numpy as np
BASE='research/cr_low_birth_causal_rr_20261027/runs/primary_v1/'
SRCSHA='5392bc1bf159d0b23d7530a541f894e201231c3df874d6c547474b7517654c58'
NPZSHA='2c3624e4ca6d087436f79360497e75b0c84fb2c8ea6b83bb855a9a0cd0005c1d'
EVJ=Decimal('1.602176634e-19')

def main(src,out):
    raw=Path(src).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==SRCSHA
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
       srcnpz=z.read(BASE+'ARRAYS.npz'); old=json.loads(z.read(BASE+'RESULT.json'))
    assert hashlib.sha256(srcnpz).hexdigest()==NPZSHA
    with np.load(io.BytesIO(srcnpz),allow_pickle=False) as ar:
        en=ar['E_eV']
        C={ch:ar[f'capture_{ch}_bins_m3'] for ch in ('H','He')}
        photons={ch:ar[f'photon_{ch}_energy_eV'] for ch in ('H','He')}
    result={'method':'Decimal80 direct original atomic weighted sums, without primary implementation imports',
            'source_SHA256':SRCSHA,'data':[]}
    with localcontext() as ctx:
        ctx.prec=80
        allN=Decimal(0);allU=Decimal(0)
        for ch in ('H','He'):
            for j in range(4):
                ww=C[ch][j]
                N=sum((Decimal.from_float(float(x)) for x in ww), Decimal(0))
                Uev=sum((Decimal.from_float(float(w))*Decimal.from_float(float(e))
                       for w,e in zip(ww,photons[ch])),Decimal(0))
                oldc=old['observation_bins'][j]['channels'][ch]
                oldN=Decimal.from_float(float(oldc['capture_number_m3']))
                oldU=Decimal.from_float(float(oldc['retained_photon_energy_eV_m3']))
                def rerr(a,b):return abs((a-b)/a) if a!=0 else abs(a-b)
                Nerr=rerr(N,oldN);Uerr=rerr(Uev,oldU)
                assert Nerr<Decimal('3e-12') and Uerr<Decimal('3e-12')
                result['data'].append({'channel':ch,'bin':j+1,'N_Decimal':str(N),
                    'UeV_Decimal':str(Uev),'UJ_Decimal':str(Uev*EVJ),
                    'N_relative_error_to_old_original':str(Nerr),
                    'U_relative_error_to_old_original':str(Uerr)})
                allN+=N;allU+=Uev*EVJ
        result['N_total_Decimal']=str(allN);result['U_J_total_Decimal']=str(allU)
    Path(out).write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print('independent_decimal8/8 PASS',str(result['N_total_Decimal']),str(result['U_J_total_Decimal']))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--out',required=True)
    q=p.parse_args();main(q.source,q.out)
