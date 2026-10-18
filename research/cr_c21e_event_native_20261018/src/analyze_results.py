"""Dimensionally explicit analysis of an already executed fixed-fixture matrix."""
from pathlib import Path
import argparse,json,math
import numpy as np
from run_experiment import write_json


def analyze(root:Path):
    root=Path(root)
    summary=json.loads((root/'SUMMARY.json').read_text())
    ref=json.loads((root/'radau.json').read_text())
    fixture=json.loads((root/'fixture.json').read_text())
    gref=np.asarray(ref['gas']);wscale=float(fixture['gas0'][3]);modes={}
    for name in sorted({r['mode'] for r in summary['cases']}):
        rows=[]
        cases=sorted((r for r in summary['cases'] if r['mode']==name),key=lambda r:r['subdivisions_per_event_interval'])
        for r in cases:
            d=np.abs(np.asarray(r['gas'])-gref)
            rows.append({'subdivisions':r['subdivisions_per_event_interval'],
                'fraction_max_abs_error':float(d[:3].max()),'thermal_abs_error_eV_H':float(d[3]),
                'temperature_abs_error_K':abs(r['temperature_K']-ref['temperature_K']),
                'normalized_state_error':float(max(d[:3].max(),d[3]/wscale)),
                'photon_max_abs_error_H':float(np.max(abs(np.asarray(r['photons'])-ref['photons']))),
                'number_defect_H':r['number_defect_H'],'energy_defect_eV_H':r['energy_defect_eV_H'],
                'native_or_manufactured':r['microphysics'],'wall_s':r['wall_s'],'rhs_calls':r['rhs_calls']})
        orders=[]
        for a,b in zip(rows,rows[1:]):
            e1=a['normalized_state_error'];e2=b['normalized_state_error']
            orders.append(math.log(e1/e2)/math.log(b['subdivisions']/a['subdivisions']) if e1>0 and e2>0 else None)
        modes[name]={'rows':rows,'observed_normalized_state_orders':orders}
    result={'schema':'C21E_DIMENSIONAL_REFINEMENT_V1','fixture_sha256':summary['fixture_sha256'],
       'normalization':'fractions use scale=1; thermal energy uses initial w_eV_H, not an untyped max of units',
       'initial_thermal_eV_H':wscale,'modes':modes,
       'scope':'same fixed impulse source/spectrum and microphysical kernel; time refinement only; no global order certificate'}
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('run',type=Path);p.add_argument('--out',type=Path)
    a=p.parse_args();result=analyze(a.run);out=a.out or a.run/'ANALYSIS.json';write_json(out,result)
    print(json.dumps({'analysis':str(out),'modes':{k:v['observed_normalized_state_orders'] for k,v in result['modes'].items()}}))
