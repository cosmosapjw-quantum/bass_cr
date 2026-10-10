"""Targeted RED assertions for new B2B contract and certificate guards."""
import sys,subprocess,json,argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parent
cases=[('source_corruption','test_contract','ContractTests','test_wrong_bytes',"old=t.load_contract;t.load_contract=lambda **kw:old()"),
('clock_corruption','test_contract','ContractTests','test_wrong_clock',"old=t.load_contract;t.load_contract=lambda **kw:old()"),
('channel_corruption','test_contract','ContractTests','test_wrong_channel',"old=t.load_contract;t.load_contract=lambda **kw:old()"),
('injection_energy_corruption','test_contract','ContractTests','test_corrupt_injection_energy',"old=t.load_contract;t.load_contract=lambda **kw:old()"),
('independent_parameter_falsely_cancelled','test_contract','ContractTests','test_same_box_independent_channels_not_same_physics',"t.channel_jump_orders=lambda *a,**k:dict(J012=[0,0,0],J3=None)"),
('missing_J3_zero_fill','test_peano_gate','PeanoGateTests','test_unreported_third_kink',"t.peano_transfer=lambda e:0"),
('nominal_homotopy','test_peano_gate','PeanoGateTests','test_nominal_only',"t.peano_transfer=lambda e:0"),
('toy_J3_misadopted','test_peano_gate','PeanoGateTests','test_toy_third_jump',"t.peano_transfer=lambda e:0")]
def run(out):
 out.mkdir();rows=[]
 for name,module,cls,test,mutation in cases:
  code=f"import sys,unittest\nsys.path.insert(0,{str(ROOT/'tests')!r})\nimport {module} as t\n{mutation}\nr=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([t.{cls}({test!r})]))\nsys.exit(0 if r.wasSuccessful() else 1)\n"
  cmd=[sys.executable,'-B','-c',code];r=subprocess.run(cmd,text=True,capture_output=True)
  (out/(name+'.py')).write_text(code);(out/(name+'.log')).write_text(r.stdout+r.stderr)
  assert r.returncode==1 and 'FAILED (failures=1)' in r.stderr,(name,r.stderr)
  rows.append(dict(name=name,test=module+'.'+test,command=cmd,exit=r.returncode))
 (out/'RESULT.json').write_text(json.dumps(dict(status='8_TARGETED_RED_MUTANTS_REJECTED',cases=rows),indent=2)+'\n');print('8_TARGETED_RED_MUTANTS_REJECTED')
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--output',type=Path,required=True);x=a.parse_args();run(x.output)
