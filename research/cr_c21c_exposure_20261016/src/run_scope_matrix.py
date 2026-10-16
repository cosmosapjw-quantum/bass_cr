"""Bounded C8 sensitivity: independent source-age Radau vs retained exact-pair solver."""
from __future__ import annotations
import argparse,json,pathlib,math
from compare_c21b import compare


def run():
    p=argparse.ArgumentParser()
    p.add_argument('--out',type=pathlib.Path,required=True)
    a=p.parse_args()
    results=[]
    for dx in (.0125,.025):
        for fac in (1e-4,1e-3,3e-3):
            data=compare((4,8,16,32,64),dx=dx,opacity_scale=fac)
            seq=data['sequence']
            err=[v['state_difference_inf'] for v in seq]
            order=[math.log(err[i]/err[i+1],2) for i in range(len(err)-1)]
            results.append(dict(dx_ln_a=dx,opacity_scale=fac,steps=[4,8,16,32,64],
              max_state_abs_errors=err,adjacent_orders=order,
              max_number_residual=max(abs(v['number_residual']) for v in seq),
              max_energy_residual_ev_per_H=max(abs(v['energy_residual_ev_H']) for v in seq),
              reference_events=data['reference']['photon_events_H'],
              endpoint_condition=data['reference']['endpoint_condition'],
              reference_energy_residual_ev_per_H=data['reference']['energy_residual_ev_H']))
    result=dict(schema='C21C_REAL_VERNER_MANUFACTURED_THREE_SOURCE_NINE_AGE_PHASE_MATRIX_V1',
      note='Original Verner fit+MD14 birth CLOCK but manufactured three energy source shape; no RR/CI/DR/CMB; no native execution',
      data=results)
    a.out.parent.mkdir(exist_ok=True,parents=True)
    a.out.write_text(json.dumps(result,indent=2)+'\n')
    for r in results:
        print('dx',r['dx_ln_a'],'fac',r['opacity_scale'],
           'order(last)',round(r['adjacent_orders'][-1],5),
           'err64',format(r['max_state_abs_errors'][-1],'.4e'),
           'maxE',format(r['max_energy_residual_ev_per_H'],'.4e'))

if __name__=='__main__':run()
