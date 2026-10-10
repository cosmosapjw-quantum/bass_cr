"""Focused negative tests must FAIL when their guard/feedback is removed.
Each mutant runs in a fresh process and is retained with exact command/exit.
The production source is never edited by this harness.
"""
import sys,json,subprocess,argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parent
CASES=[
 ('wrong_source_bytes','test_backend','test_source_bytes',"original=t.load_pins; t.load_pins=lambda **kw:original()"),
 ('wrong_clock','test_backend','test_clock',"original=t.load_pins; t.load_pins=lambda **kw:original()"),
 ('lost_mass_mismatch','test_backend','test_mass_mismatch',"original=t.load_pins; t.load_pins=lambda **kw:dict(original(**kw),mass_mismatch=0)"),
 ('incorrect_local_global','test_backend','test_local_global',"t.local_derivatives=lambda v,h,total:v"),
 ('unreported_kink','test_backend','test_unreported_kink',"t.require_proof=lambda e:None"),
 ('nominal_only_homotopy','test_backend','test_nominal_only',"t.require_proof=lambda e:None"),
 ('frozen_gas_replacement','test_backend','test_frozen_gas',"t.require_proof=lambda e:None"),
 ('lost_survival_memory','test_backend','test_memory_feedback',"t.memory_response=lambda p,m:t.I(0)"),
 ('lost_companion_feedback','test_functional','test_companion_current_response_participates',"original=t.tangent_functional; t.tangent_functional=lambda *a:original(*a[:-1],lambda f:(t.I(0),t.I(0)))")]
def run(out):
 out.mkdir();rows=[]
 for name,module,method,mutant in CASES:
  cls='FunctionalTests' if module=='test_functional' else 'BackendTests'
  code=f"import sys,unittest\nsys.path.insert(0,{str(ROOT/'tests')!r})\nimport {module} as t\n{mutant}\nsuite=unittest.TestSuite([t.{cls}({method!r})])\nr=unittest.TextTestRunner(verbosity=2).run(suite)\nsys.exit(0 if r.wasSuccessful() else 1)\n"
  cmd=[sys.executable,'-B','-c',code];r=subprocess.run(cmd,text=True,capture_output=True)
  (out/(name+'.py')).write_text(code);(out/(name+'.log')).write_text(r.stdout+r.stderr)
  assert r.returncode==1 and 'FAILED (failures=1)' in r.stderr,(name,r.returncode,r.stderr)
  rows.append(dict(name=name,exit=r.returncode,expected='focused assertion failure',test=module+'.'+cls+'.'+method,command=cmd))
 (out/'RESULT.json').write_text(json.dumps(dict(status='ALL_9_MUTANTS_REJECTED',cases=rows),indent=2)+'\n');print('ALL_9_MUTANTS_REJECTED')
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--output',type=Path,required=True);x=a.parse_args();run(x.output)
