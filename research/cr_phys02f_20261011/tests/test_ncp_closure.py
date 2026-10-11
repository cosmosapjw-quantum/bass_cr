import unittest,tempfile,pathlib,json,hashlib,sys,io
from unittest.mock import patch
import numpy as np
P=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'ncp'));sys.path.insert(0,str(P/'src'))
import launch_residence as L,run_and_collect as W,residence as R
class ClosureTests(unittest.TestCase):
 def test_absolute_guard_and_partial_counter(self):
  with self.assertRaisesRegex(ValueError,'ABSOLUTE'):W.run_and_collect('relative','also_relative')
  with tempfile.TemporaryDirectory() as t:
   p=pathlib.Path(t);(p/'SOLVE_1_q0_RESERVED.json').write_text('{}')
   c=L.solve_counts(p);self.assertIsNone(c['actual_triangular_solve_calls']);self.assertEqual(c['actual_triangular_solve_calls_bounds'],[0,1])
   (p/'SOLVE_1_q0_COMPLETED.json').write_text('{}');self.assertEqual(L.solve_counts(p)['actual_triangular_solve_calls'],1)
 def test_manifest_real_root_and_READY_admission_fixture(self):
  with tempfile.TemporaryDirectory() as t:
   repo=pathlib.Path(t);study=repo/'research/cr_phys02f_20261011';study.mkdir(parents=True)
   required=['src/residence.py','src/tail_analysis.py','ncp/launch_residence.py','ncp/ops.py','ncp/collect_return.py','ncp/run_and_collect.py'];pins={'state/SCIENTIFIC_CONTRACT.json':L.SCI,'ncp/NCP_EXECUTION_CONTRACT.json':L.NCP,'state/VALIDATION_CONTRACT.json':L.VALIDATION,'inputs/INPUT_IDENTITIES.json':L.INPUT,'inputs/DEPENDENCY_PAYLOAD_MANIFEST.json':L.DEP}
   def write(rel,obj):
    p=study/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj));return p
   dep={}
   for i in range(538):
    p=repo/f'dep{i}';p.write_bytes(b'd');dep[p.name]={'bytes':1,'sha256':L.sha(p)}
   inputs={f'i{i}':{'path':f'dep{i}','bytes':1,'sha256':L.sha(repo/f'dep{i}')} for i in range(17)}
   inputs['prior_resource_adapter']={'path':'research/cr_phys02f_20261011/ncp/ops.py','bytes':2,'sha256':hashlib.sha256(b'{}').hexdigest()}
   write('inputs/INPUT_IDENTITIES.json',{'files':inputs});write('inputs/DEPENDENCY_PAYLOAD_MANIFEST.json',{'files':dep})
   write('state/SCIENTIFIC_CONTRACT.json',{'inherited_gates':{}});write('state/VALIDATION_CONTRACT.json',{});write('state/CONTRACT_IDENTITY.json',pins);write('ncp/NCP_EXECUTION_CONTRACT.json',{'admission':{'review_required_code':required}})
   for rel in required:write(rel,{})
   # restore NCP contract after creating source fixture.
   write('ncp/NCP_EXECUTION_CONTRACT.json',{'admission':{'review_required_code':required}})
   reviewed={rel:{'bytes':(study/rel).stat().st_size,'sha256':L.sha(study/rel)} for rel in required}
   review={'decision':'PASS_SCOPED','independent_of_implementation':True,'independent_of_candidate_design':True,'independent_of_acceptance':True,'reviewer_role':'INDEPENDENT_ASTRA','scientific_contract_sha256':L.SCI,'ncp_contract_sha256':L.NCP,'validation_contract_sha256':L.VALIDATION,'input_manifest_sha256':L.INPUT,'dependency_manifest_sha256':L.DEP,'reviewed_files':reviewed}
   rp=write('review/fixture.json',review)
   write('state/NEXT_DAG.json',{'scientific_contract_sha256':L.SCI,'inherited_gates':{},'tasks':[{'id':L.TASK,'status':'READY','max_G_builds':2,'max_resolvent_blocks':2,'max_triangular_solve_calls':10,'max_pulse_calls':0,'total_wall_s':900,'grid_cells':[3200,6400],'independent_review':{'path':'review/fixture.json','sha256':L.sha(rp)}}]})
   files={p.relative_to(repo).as_posix():{'bytes':p.stat().st_size,'sha256':L.sha(p)} for p in study.rglob('*') if p.is_file()}
   fp=write('FILE_MANIFEST.json',{'schema':'cr-phys02f-file-manifest.v1','path_basis':'repository-root','files':files})
   realsha=L.sha
   def sha(p):
    rel=pathlib.Path(p).relative_to(study).as_posix() if pathlib.Path(p).is_relative_to(study) else None
    return pins[rel] if rel in pins else realsha(p)
   # Fixture pins emulate frozen contract identities; file/dependency/review SHA remains real.
   with patch.object(L,'STUDY',study),patch.object(L,'REPO',repo):
    self.assertEqual(L.frozen_payload()['verification']['verified_entries'],len(files))
    with patch.object(L,'sha',sha):self.assertEqual(L.admission()['dependency_count'],538)
    data=json.loads(fp.read_text());del data['files']['research/cr_phys02f_20261011/src/residence.py'];fp.write_text(json.dumps(data))
    with self.assertRaisesRegex(ValueError,'COVERAGE'):L.frozen_payload()
 def test_wrong_G_no_reservation_no_diagnostic(self):
  current={'G':{'shape':[1,1]},'energy_eV':{},'method_bindings':{'f':{'same_parent_object':True,'qualname':'f'}}};reference={**current,'G':{'shape':[2,2]}}
  calls=[]
  with patch.object(R,'diagnostic',side_effect=lambda **k:calls.append('diagnostic')):
   with self.assertRaisesRegex(R.ResidenceError,'OPERATOR_IDENTITY_MISMATCH'):R.diagnostic_after_parity(current,reference,lambda:calls.append('reserve'))
  self.assertEqual(calls,[])
 def test_pulse_immutable_semantics_and_hash_failures(self):
  with tempfile.TemporaryDirectory() as t:
   root=pathlib.Path(t);E=np.array([1.,10.,900.]);b=np.ones((14,2));b[3:]=0;sources={m:{'energy_eV':E,'source_vectors':b} for m in ('fullBED','legacy')}
   arrays={'sample_u':np.linspace(0.,1.,17),'pulse_states':np.broadcast_to(b,(17,14,2)).copy(),'integrator_states':np.zeros((17,2,2)),'energy_eV':E,'source_vectors':b}
   ids={}
   def save(model):
    p=root/(model+'.npz');np.savez(p,**arrays);ids['actual_'+model+'_pulse']={'path':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    q=root/(model+'_source');q.write_bytes(b'source');ids[model+'_9600_npz']={'path':q.name,'bytes':6,'sha256':hashlib.sha256(b'source').hexdigest()}
   for m in sources:save(m)
   pulse,receipt=R.preflight_pulses(root,ids,sources,n=3)
   with self.assertRaises(ValueError):pulse['fullBED']['energy_eV'].setflags(write=True)
   arrays['pulse_states'][0,0,0]+=1;save('legacy')
   with self.assertRaisesRegex(R.ResidenceError,'PULSE_INITIAL'):R.preflight_pulses(root,ids,sources,n=3)
   (root/'fullBED.npz').write_bytes(b'corrupt')
   with self.assertRaisesRegex(R.ResidenceError,'INPUT_FILE_IDENTITY'):R.preflight_pulses(root,ids,sources,n=3)
if __name__=='__main__':unittest.main()
