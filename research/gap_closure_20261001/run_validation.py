"""Run only the new, non-native R4Q suites; preserve exact logs and first failure.

This runner does not authorize or launch a physical operator/propagation job.
Use a fresh --out directory outside the source tree for portable-package checks.
"""
from pathlib import Path
import argparse,hashlib,json,os,re,subprocess,sys,time

HERE=Path(__file__).resolve().parent
SUITES=['rho_integration_theorem_20261001','numerical_methods_20261001',
        'semantic_selection_20261001','rank_policy_20261001','asymptotics_20261001',
        'majorant_analytic_20261001','majorant_validated_20261001',
        'independent_propagator_20261001','static_validation_20261001',
        'static_validation_20261001/executor']
def run(out):
    out=Path(out).resolve()
    if out.is_relative_to(HERE):raise ValueError('validation outputs must be outside source')
    out.mkdir(parents=True,exist_ok=False)
    rows=[];first=None
    for suite in SUITES:
        folder=HERE/suite
        if not list(folder.glob('test_*.py')):raise ValueError('missing suite: '+suite)
        command=[sys.executable,'-m','unittest','discover','-s','.','-p','test_*.py','-v']
        env={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1'}
        # Native work is only reachable through separately guarded executor CLIs,
        # not through this explicitly enumerated synthetic/offline suite list.
        started=time.monotonic()
        result=subprocess.run(command,cwd=folder,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        log=suite.replace('/','__')+'.log';(out/log).write_text(result.stdout)
        match=re.search(r'Ran (\d+) tests?',result.stdout);count=int(match.group(1)) if match else None
        skipped=re.search(r'skipped=(\d+)',result.stdout)
        rows.append({'suite':suite,'command':command,'exit_code':result.returncode,'tests':count,'skipped':int(skipped.group(1)) if skipped else 0,'seconds':time.monotonic()-started,'log':log})
        if result.returncode or count is None or skipped:
            first=rows[-1];break
    import numpy,scipy
    data={'schema':'BASS_R4Q_FOCUSED_VALIDATION_V1','status':'PASS' if first is None else 'FAIL','environment':{'python':sys.version,'numpy':numpy.__version__,'scipy':scipy.__version__},'suites':rows,'tests_total':sum(x['tests'] or 0 for x in rows),'skipped_total':sum(x['skipped'] for x in rows),'first_failure':first,'source_files':{str(p.relative_to(HERE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(HERE.rglob('*')) if p.is_file() and '__pycache__' not in p.parts},'scope':'new R4Q non-native suites only; historical suites not repeated','physical_operator_evaluations':0,'physical_transport_runs':0,'native_authorization_consumed':False}
    (out/'VALIDATION.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps({k:data[k] for k in ['status','tests_total','skipped_total','first_failure']}))
    return 0 if first is None else 1
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',required=True);args=parser.parse_args();raise SystemExit(run(args.out))
