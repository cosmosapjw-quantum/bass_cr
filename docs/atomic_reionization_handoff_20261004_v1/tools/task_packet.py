#!/usr/bin/env python3
"""Print one grounded task card; never execute commands or mutate science state."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def select(program,state,thread=None):
 done=set(state.get('completed_task_ids',[]))|set(state.get('activated_decisions',[]))
 known={t['id'] for t in program['tasks']}
 if done-known:raise ValueError('unknown completion IDs: '+','.join(sorted(done-known)))
 candidates=[t for t in program['tasks'] if (thread is None or t['thread']==thread) and not t['optional'] and t['id'] not in done]
 ready=[t for t in candidates if set(t['dependencies'])<=done]
 if ready:return {'status':'READY','task':ready[0],'notice':'Read task acceptance and source identities. Planned commands do not prove execution. This utility executes nothing.'}
 return {'status':'WAITING_OR_FINISHED','waiting':[{'id':t['id'],'unmet':[d for d in t['dependencies'] if d not in done]} for t in candidates]}
def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=['next','show','legacy']);p.add_argument('task_id',nargs='?');p.add_argument('--thread');p.add_argument('--state',type=Path,default=ROOT/'EXECUTION_STATE.json');a=p.parse_args()
 program=json.loads((ROOT/'PROGRAM.json').read_text())
 if a.action=='next':out=select(program,json.loads(a.state.read_text()),a.thread)
 elif a.action=='show':
  matches=[t for t in program['tasks'] if t['id']==a.task_id]
  if not matches:p.error('unknown task id')
  out=matches[0]
 else:
  if a.thread not in ('rei_bianchi','bass_cr','WU088_HH','BASS_HE'):p.error('legacy requires a known --thread')
  target=ROOT/'threads'/a.thread/'LEGACY_LANE.json'
  if not target.exists():p.error('This repository packet does not contain that thread; open its repository or full bundle.')
  out={'status':'RECALL_CONTRACT_ONLY_NO_EXECUTION','legacy':json.loads(target.read_text())}
 print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__':
 try:main()
 except ValueError as e:print(json.dumps({'status':'INVALID_STATE','error':str(e)}),file=sys.stderr);sys.exit(2)
