from pathlib import Path
import json,os,subprocess,sys
import pytest
import run_full_geometry_qualification as runner

HERE=Path(__file__).resolve().parents[1]

def test_help_exposes_only_fixed_execution_controls(tmp_path):
    env=dict(os.environ);env.pop('PYTHONPATH',None)
    p=subprocess.run([sys.executable,'-E',str(HERE/'run_full_geometry_qualification.py'),'--help'],cwd=tmp_path,env=env,text=True,capture_output=True)
    assert p.returncode==0,p.stderr
    for flag in ('--out','--native-build','--workers','--expected-commit','--resume-from'): assert flag in p.stdout
    for forbidden in ('--epsilon','--order','--phase-budget','--capture','--geometry','--tolerance','--gpu'): assert forbidden not in p.stdout


def test_declared_task_specs_cover_candidate_and_frozen_reference_ladder():
    c=json.loads((HERE/'CONTRACT.json').read_text())
    specs=runner.geometry_task_specs(-4.,c)
    assert len(specs)==3*(1+len(c['reference_orders']))
    assert [(x['method'],x.get('reference_order'),x['dz_a0']) for x in specs[:3]]==[
        ('phase24',None,-1e-4),('phase24',None,0.),('phase24',None,1e-4)]
    assert [(x['method'],x.get('reference_order')) for x in specs[3:6]]==[('reference',32)]*3
    assert [(x['method'],x.get('reference_order')) for x in specs[-3:]]==[('reference',64)]*3


def test_sequence_stops_before_submitting_later_geometry_after_first_failure():
    seen=[]
    def fake(z):
        seen.append(z)
        return {'z_a0':z,'failed_screens':(['x'] if z==-2 else [])}
    rows,first=runner.sequence_geometries([-4.,-2.,0.,2.],fake)
    assert seen==[-4.,-2.]
    assert [r['z_a0'] for r in rows]==[-4.,-2.]
    assert first['z_a0']==-2.


def test_sequence_runs_all_when_clean():
    seen=[]
    rows,first=runner.sequence_geometries([-4.,-2.,0.],lambda z:(seen.append(z) or {'z_a0':z,'failed_screens':[]}))
    assert seen==[-4.,-2.,0.] and first is None and len(rows)==3


def test_existing_output_is_rejected_without_mutation(tmp_path):
    before=list(tmp_path.iterdir())
    p=subprocess.run([sys.executable,str(HERE/'run_full_geometry_qualification.py'),'--out',str(tmp_path),'--native-build',str(tmp_path/'x')],text=True,capture_output=True)
    assert p.returncode==2
    assert list(tmp_path.iterdir())==before


def test_reference_policy_runs_candidate_only_after_reference_is_qualified():
    calls=[]
    c={'epsilon_z_a0':1e-4,'reference_orders':[32,40,48],
       'screens':{'connection_relative_max':1e-6,'raw_cross_relative_max':1e-9,
                  'operator_hermiticity_relative_max':1e-11,'metric_min_ratio':1e-8}}
    def ensure(specs):
        calls.append([(s['method'],s.get('reference_order')) for s in specs])
        rows=[]
        for s in specs:
            # q32 fails, q40/q48 pass and converge; candidate passes.
            good = not (s['method']=='reference' and s['reference_order']==32)
            order=s.get('reference_order')
            shift=5e-5 if order==32 else (3e-10 if order==40 else 0.)
            from test_reference_policy import _row
            rows.append(_row(s['method'],order,s['dz_a0'],connection_good=good,cross_shift=shift))
        return rows
    r=runner.execute_geometry_policy(-4.,c,1e-3,ensure)
    assert r['status']=='GEOMETRY_QUALIFIED'
    assert r['qualified_reference_order']==48
    assert calls[0]==[('reference',32)]*3+[('reference',40)]*3
    assert calls[1]==[('reference',48)]*3
    assert calls[2]==[('phase24',None)]*3


def test_reference_exhaustion_never_runs_candidate():
    calls=[]
    c={'epsilon_z_a0':1e-4,'reference_orders':[32,40],
       'screens':{'connection_relative_max':1e-6,'raw_cross_relative_max':1e-9,
                  'operator_hermiticity_relative_max':1e-11,'metric_min_ratio':1e-8}}
    def ensure(specs):
        calls.append([(s['method'],s.get('reference_order')) for s in specs])
        from test_reference_policy import _row
        return [_row('reference',s['reference_order'],s['dz_a0'],connection_good=True,cross_shift=s['reference_order']*1e-4) for s in specs]
    r=runner.execute_geometry_policy(-4.,c,1e-3,ensure)
    assert r['status']=='REFERENCE_CONVERGENCE_UNRESOLVED'
    assert all(call[0][0]=='reference' for call in calls)


def test_sequence_classifies_reference_exhaustion_separately():
    rows,first=runner.sequence_geometries([-4.,-2.],lambda z:{'status':'REFERENCE_CONVERGENCE_UNRESOLVED',
        'z_a0':z,'failed_screens':['reference convergence unresolved']})
    assert len(rows)==1
    assert first['kind']=='reference'
    assert first['z_a0']==-4.
