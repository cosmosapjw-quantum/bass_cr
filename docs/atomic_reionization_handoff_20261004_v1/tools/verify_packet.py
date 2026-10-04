#!/usr/bin/env python3
import json,hashlib,sys
from pathlib import Path
from build_program import check_dag
from task_packet import select
ROOT=Path(__file__).resolve().parents[1]
def main():
 program=json.loads((ROOT/'PROGRAM.json').read_text());state=json.loads((ROOT/'EXECUTION_STATE.json').read_text())
 check_dag(program['tasks'])
 assert select(program,state,'rei_bianchi')['task']['id']=='REI-F00'
 assert select(program,state,'BASS_HE')['task']['id']=='HE-F1'
 assert select(program,state,'bass_cr')['status']=='WAITING_OR_FINISHED'
 assert select(program,state,'WU088_HH')['status']=='WAITING_OR_FINISHED'
 for broken in [ [{'id':'X','dependencies':['X']}], [{'id':'X','dependencies':['Y']}], [{'id':'X','dependencies':[]},{'id':'X','dependencies':[]}] ]:
  try:check_dag(broken)
  except ValueError:pass
  else:raise AssertionError('invalid DAG accepted')
 try:select(program,{'completed_task_ids':['invented']})
 except ValueError:pass
 else:raise AssertionError('unknown completion accepted')
 by={t['id']:t for t in program['tasks']}
 assert 'HH-F2' in by['REI-F09']['dependencies'] and 'HE-F2' in by['REI-F09']['dependencies']
 assert 'REI-F09' in by['HH-F3']['dependencies'] and 'REI-F09' in by['HE-F3']['dependencies']
 assert all(not x.startswith(('HE-','HH-','CR-L','CR-M')) for x in by['REI-F08']['dependencies'])
 files=0
 manifest=ROOT/'PAYLOAD_MANIFEST.json'
 if manifest.exists():
  for item in json.loads(manifest.read_text())['files']:
   p=ROOT/item['path'];assert p.is_file(),item['path']
   assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'],item['path'];files+=1
 print(json.dumps({'status':'PACKET_LOGIC_AND_AVAILABLE_MANIFEST_PASS','tasks':len(by),'files_checked':files,'scientific_gate_promoted':False},indent=2))
if __name__=='__main__':main()
