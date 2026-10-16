"""Bounded independent parameter-specific comparison; nothing to do with native NCP."""
from __future__ import annotations
import json
import pathlib
try:
    from .c21d_trilane import compare_grid
except ImportError:
    from c21d_trilane import compare_grid

def run():
    jobs=[(.0125,.0003),(.0125,.001),(.025,.0003),(.025,.001),(.025,.003)]
    output=[]
    for dx,opacity in jobs:
        d=compare_grid((16,32,64),dx=dx,opacity_scale=opacity)
        row={'dx':dx,'opacity_scale':opacity,'reference_numres':d['ref']['photon_mass_res'],
             'reference_energy_res':d['ref']['energy_res'],'lanes':{}}
        for z in d['mathematical_photo_lanes']:
            cases=z['cases']
            row['lanes'][z['mode']]={'errors':[c['state_max_abs_error_vs_radau'] for c in cases],
                'observed_orders':[c['next_error_order'] for c in cases[:-1]],
                'max_number_res':max(abs(c['number_res']) for c in cases),
                'max_energy_res':max(abs(c['energy_res']) for c in cases),
                'max_root_res':max(c['max_root_residual'] for c in cases)}
        output.append(row)
        print(dx,opacity,{mode:(round(v['errors'][-1],11),round(v['observed_orders'][-1],4)) for mode,v in row['lanes'].items()},flush=True)
    return {'schema':'C21D_5_CONDITIONS_3_LANES_PHOTO_ONLY_V1','n':[16,32,64],
            'matrix':output,'claim':'One manufactured full source-age GL2 three-energy FLRW family only; not PR150 native PreparedAbsorption or full Grackle'}
if __name__=='__main__':
    p=pathlib.Path(__file__).resolve().parents[1]/'evidence'/'SCOPED_MATRIX.json'
    v=run();p.write_text(json.dumps(v,indent=2)+'\n')
