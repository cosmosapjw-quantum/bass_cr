#!/usr/bin/env python3
"""One bounded local pilot; full operator execution is a separate NCP contract."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import parallel_operator as op
import argparse
import hashlib
import json
import time


def freeze(path):
    E,receipt=op.saved_energy()
    parent,atomic=op.dependencies('legacy')
    anchors=[min(c['adopted_effective_cost_eV'] for c in atomic.excitation if c['species']==s)
             for s in ('HI','HeI')]+[13.6057,24.587,100.,450.]
    columns=sorted({0,3199,3200,9599}|{j for value in anchors for j in
                   (int(op.np.searchsorted(E,value))-1,int(op.np.searchsorted(E,value)))})
    if len(columns)!=16:raise ValueError('SELECTED_COLUMNS_NOT_SIXTEEN')
    plan={'schema':'cr-phys02h-local-pilot-plan.v1','selected_columns':columns,
          'selected_energy_eV':E[columns].tolist(),'anchors_eV':anchors,
          'selection':'ends and split neighbors; brackets of minimum HI/HeI excitation costs, HI/HeI ionization thresholds, 100 and 450 eV',
          'energy_raw_sha256':op.raw_hash(E),'saved_input_preflight':receipt,
          'small_mesh':[80,160],'repetitions':2,'models':['legacy','fullBED'],
          'candidate_workers':[1,2,4],'small_logical_builds':16,'selected_logical_builds':8,
          'maximum_wall_s':240,'sources':op.checked_sources(),'runtime':op.runtime_identity()}
    with Path(path).open('x') as stream:json.dump(plan,stream,indent=2);stream.write('\n')
    print(json.dumps({'frozen_plan':str(path),'columns':columns,'sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest()}))


def run(path,out):
    path=Path(path);plan=json.loads(path.read_text());out=Path(out);out.mkdir(parents=True,exist_ok=True)
    reservation=out/'PILOT_RESERVATION.json'
    with reservation.open('x') as stream:
        json.dump({'plan_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'budget_program_runs':1,
                   'wall_limit_s':240,'small_logical_builds':16,'selected_logical_builds':8},stream,indent=2)
    start=time.perf_counter();rows=[];total_generators=0
    E,receipt=op.saved_energy()
    if op.raw_hash(E)!=plan['energy_raw_sha256'] or plan['sources']!=op.checked_sources():
        raise ValueError('PILOT_PLAN_IDENTITY_CHANGED')
    parent,_=op.dependencies('legacy');smallE=parent.energy_grid(*plan['small_mesh'])
    try:
        for scope,energy,mesh,columns,workers in (
            ('small',smallE,(80,160),None,[1,2,4]),
            ('selected',E,(3200,6400),tuple(plan['selected_columns']),[4])):
            for model in plan['models']:
                for rep in range(2):
                    tag=f'{scope}_{model}_rep{rep+1}'
                    logical=[('serial',0)]+[('parallel',n) for n in workers]
                    reference=None
                    for mode,n in logical:
                        remaining=240-(time.perf_counter()-start)
                        if remaining<=0:raise TimeoutError('PILOT_GLOBAL_WALL_LIMIT')
                        name=tag+'_'+mode+(str(n) if n else '')
                        with (out/(name+'_RESERVATION.json')).open('x') as stream:
                            json.dump({'logical_build':1,'model':model,'scope':scope,'workers':n,
                                       'expected_generator_invocations':n or 1,
                                       'columns':list(range(len(energy))) if columns is None else list(columns)},stream)
                        t=time.perf_counter()
                        if mode=='serial':payload=op.serial_build(model,energy,mesh,columns)
                        else:payload=op.parallel_build(model,energy,mesh,n,columns,timeout_s=min(120,remaining))
                        wall=time.perf_counter()-t
                        total_generators+=n or 1
                        saved=op.persist(payload,out/name)
                        if reference is None:
                            reference=payload;checks={'reference':True}
                        else:
                            checks=op.parity(reference,payload)
                        row={'name':name,'scope':scope,'model':model,'rep':rep+1,'mode':mode,'workers':n,
                             'end_to_end_wall_s':wall,'generator_wall_s_serial':payload.telemetry.get('wall_s') if mode=='serial' else None,
                             'actual_generator_invocations':n or 1,'parity':checks,'telemetry':payload.telemetry,
                             'signed_data_preserved':bool(op.np.any(payload.G.data<0)),
                             'arrays':saved['arrays']}
                        rows.append(row)
                        (out/'PROGRESS.json').write_text(json.dumps({'rows':rows,'actual_generator_invocations':total_generators},indent=2)+'\n')
                        print(json.dumps({'completed':name,'wall_s':wall,'parity':checks}),flush=True)
        result={'schema':'cr-phys02h-parallel-pilot-result.v1','status':'PASS_LOCAL_IMPLEMENTATION_PARITY',
                'plan_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'wall_s':time.perf_counter()-start,
                'logical_small_builds':16,'logical_selected_builds':8,'logical_total':24,
                'actual_generator_invocations':total_generators,
                'actual_original_unrestricted_generators':4,'actual_serial_restricted_generators':4,
                'actual_partial_worker_generators':44,'full9600_complete_builds':0,
                'rows':rows,'runtime':op.runtime_identity(),
                'scope':'Local process spawn CPU/RAM measurement only. Shared arithmetic oracle. No solver, propagation, previous operator adoption, MPI or NCP64 scaling claim.'}
        (out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    except BaseException as exc:
        (out/'FAILURE.json').write_text(json.dumps({'type':type(exc).__name__,'message':str(exc),
            'completed_rows':rows,'actual_completed_generator_invocations':total_generators,
            'wall_s':time.perf_counter()-start},indent=2)+'\n')
        raise


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--freeze');parser.add_argument('--plan');parser.add_argument('--out')
    args=parser.parse_args()
    if args.freeze:freeze(args.freeze)
    elif args.plan and args.out:run(args.plan,args.out)
    else:parser.error('choose --freeze FILE or --plan FILE --out DIRECTORY')
