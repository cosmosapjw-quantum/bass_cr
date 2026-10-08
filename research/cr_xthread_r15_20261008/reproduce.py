"""Create-only replay from four archived bytes; never invokes donor science CLIs."""
import argparse,json,os,subprocess,sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
def main():
    a=argparse.ArgumentParser();a.add_argument('--stage',type=Path,required=True)
    a.add_argument('--source-dir',type=Path);a.add_argument('--output',type=Path,required=True)
    a.add_argument('--verify-only',action='store_true');a.add_argument('--independent',action='store_true')
    x=a.parse_args();x.output.mkdir(parents=True,exist_ok=False)
    env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1',R15_INPUT_STAGE=str(x.stage.resolve()))
    receipts=[]
    def run(label,argv):
        with (x.output/(label+'.log')).open('x') as log:
            p=subprocess.run(argv,cwd=HERE,env=env,stdout=log,stderr=subprocess.STDOUT)
        receipts.append({'argv':argv,'exit_code':p.returncode,'log':label+'.log'})
        (x.output/'EXECUTION.json').write_text(json.dumps(receipts,indent=2)+'\n')
        if p.returncode:raise SystemExit(p.returncode)
    manifest=HERE.parent/'ncp_bass_cr_handoff_20261008/INPUTS.json'
    if not x.stage.exists():
        if not x.source_dir:a.error('NEW_STAGE_REQUIRES_SOURCE_DIR')
        run('bootstrap',[sys.executable,str(manifest.parent/'bootstrap_inputs.py'),'--workdir',str(x.stage.resolve()),'--source-dir',str(x.source_dir.resolve()),'--offline','--extract'])
    run('verify_sources',[sys.executable,str(HERE/'verify_sources.py'),'--stage',str(x.stage.resolve()),'--manifest',str(manifest)])
    run('unit',[sys.executable,'-m','unittest','-v','test_goal','test_contract'])
    if not x.verify_only:
        run('interval',[sys.executable,str(HERE/'run_r15.py'),'--stage',str(x.stage.resolve()),'--output',str(x.output.resolve()/'interval')])
        if x.independent:
            run('independent',[sys.executable,str(HERE/'independent_goal.py'),'--stage',str(x.stage.resolve()),'--result',str(x.output.resolve()/'interval'),'--output',str(x.output.resolve()/'INDEPENDENT_GOAL.json')])

if __name__=='__main__':main()
