#!/usr/bin/env python3
"""Assemble bounded per-repository work into one cross-repository DAG."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ALIASES={
 'REI_SCOPE_LOCK':'REI-F00','REI_PROVIDER_CONTRACT':'REI-F01',
 'REI_DOMAIN_FREEZE':'REI-F07','REI_NONLINEAR_CERTIFIED_SEAM':'REI-F05',
 'REI_BASELINE_EXECUTOR':'REI-F08','REI_BASELINE_HISTORY_ACCEPTED':'REI-F08',
 'REI_ATOMIC_SENSITIVITY_RESULT':'REI-F09'}
DECISIONS=['DECISION_CR_ON_SCOPE','DECISION_REOPEN_LEGACY','EXPLICIT_REOPEN_TRIGGER']
COMPLETED={'HH-F0','HE-P0'}
def write(name,value):
 (ROOT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def check_dag(tasks):
 by={t['id']:t for t in tasks}
 if len(by)!=len(tasks):raise ValueError('duplicate task id')
 for t in tasks:
  for d in t['dependencies']:
   if d not in by:raise ValueError('dangling dependency '+d)
 visiting=set();done=set()
 def visit(n):
  if n in visiting:raise ValueError('cycle at '+n)
  if n in done:return
  visiting.add(n)
  for d in by[n]['dependencies']:visit(d)
  visiting.remove(n);done.add(n)
 for n in by:visit(n)
 return list(by)
def main():
 tasks=[];snapshots={}
 for thread in ['rei_bianchi','bass_cr','WU088_HH','BASS_HE']:
  folder=ROOT/'threads'/thread
  j=json.loads((folder/'TASKS.json').read_text())
  snapshots[thread]=json.loads((folder/'REPO_SNAPSHOT.json').read_text())
  for raw in j['tasks']:
   deps=raw.get('dependencies',raw.get('depends_on',raw.get('deps',[])))+raw.get('external_dependencies',[])
   deps=list(dict.fromkeys(ALIASES.get(x,x) for x in deps))
   taskid=raw['id'];lane=raw.get('lane','legacy' if '-L' in taskid else 'fastest')
   optional=('-L' in taskid or '-M' in taskid)
   if taskid=='CR-F0':deps=list(dict.fromkeys(deps+['REI-F03']))
   if taskid=='REI-F09':deps=list(dict.fromkeys(deps+['HH-F2','HE-F2']))
   if taskid in ('HH-F3','HE-F3'):deps=list(dict.fromkeys([x for x in deps if x not in ('REI-F05','REI-F08')]+['REI-F09']))
   tasks.append({'id':taskid,'thread':thread,'title':raw.get('title',raw.get('name',taskid)),
     'lane':lane,'optional':optional,'state':'completed' if taskid in COMPLETED else ('parked' if optional else 'pending'),
     'source_status':raw.get('status'),'dependencies':deps,'execution_owner': 'rei_bianchi' if taskid=='REI-F09' else thread,
     'source_card':f'threads/{thread}/TASKS.json#{taskid}',
     'read_first':[f'threads/{thread}/CODEX_START_KO.md','common/DECISIONS.json',f'threads/{thread}/PREWORK_KO.md'],
     'working_directory':'repository_root','packet_directory':'docs/atomic_reionization_handoff_20261004_v1',
     'details':raw})
 for d in DECISIONS:tasks.append({'id':d,'thread':'coordinator','title':d,'lane':'explicit_decision','optional':True,'state':'parked','dependencies':[],'execution_owner':'user_or_explicit_research_decision','details':{'rule':'Only activate a documented requested observable/domain or source-conflict trigger; does not block mandatory baseline.'}})
 check_dag(tasks)
 program={'schema':'atomic_reionization.program.v1','date':'2026-10-04','authority':'Current per-thread exact-ref snapshots plus explicit plan decisions; not old deep-research snapshot',
 'source_aliases':ALIASES,'tasks':tasks,'default_lane':'fastest','prework_completed_task_ids':sorted(COMPLETED),
 'single_campaign':{'owner_task':'REI-F09','inputs':['HH-F2','HE-F2'],'output':'runtime_outputs/paired_atomic_sensitivity_v1.json','review_tasks':['HH-F3','HE-F3'],'duplicate_cosmology_execution':False},
 'failure_rules':{'source_drift':'Review changed code/contracts only; docs-only publication does not restart completed science','runtime':'Record environment error; do not relabel physics failure','numeric':'Preserve rejected step and thresholds; repair local map/evaluator','source_conflict':'Keep named alternatives; no silent averaging or legacy restart','physical_domain':'Limit claim or select one provider extension'},
 'claim_ceiling':'PLANNING_AND_PORTABLE_PREWORK_ONLY; runtime admissions are task outputs not package metadata'}
 write('PROGRAM.json',program)
 write('GLOBAL_DAG.json',{k:v for k,v in program.items() if k!='tasks'}|{'nodes':[{k:v for k,v in t.items() if k!='details'} for t in tasks]})
 (ROOT/'TASK_CARDS.jsonl').write_text(''.join(json.dumps(t,ensure_ascii=False,separators=(',',':'))+'\n' for t in tasks))
 write('EXECUTION_STATE.json',{'schema':'task_execution_state.v1','completed_task_ids':sorted(COMPLETED),'activated_decisions':[],'runtime_results':[],
 'note':'Prework completion is scoped; consumer code/atomic scientific gates are not promoted. Later completion requires a RETURN_CONTRACT-conforming evidence receipt.'})
 route={}
 for thread,s in snapshots.items():
  first=next((t['id'] for t in tasks if t['thread']==thread and t['state']=='pending' and not t['optional']),None)
  route[thread]={'repository':'cosmosapjw-quantum/'+thread,'branch':s['branch'],'source_commit':s.get('head_sha',s.get('commit',s.get('head_commit',s.get('head')))),'source_tree':s.get('tree_sha',s.get('tree',s.get('head_tree'))),
  'packet_root':'docs/atomic_reionization_handoff_20261004_v1','start':f'threads/{thread}/CODEX_START_KO.md','first_pending_task':first,
  'inspect_next':f'python3 docs/atomic_reionization_handoff_20261004_v1/tools/task_packet.py next --thread {thread}',
  'legacy':f'threads/{thread}/LEGACY_LANE.json'}
 write('CODEX_ROUTING.json',{'schema':'codex.routing.v1','repositories':route,'initial_policy':'Read one start prompt, common decisions, one ready task only. Do not load all archived sources.'})
 pr=[]
 for t in tasks:
  if t['thread']=='coordinator' or t['state']=='completed':continue
  raw=t['details'];pr.append({'planning_id':'PR-'+t['id'],'repository':'cosmosapjw-quantum/'+t['thread'],'task_id':t['id'],'title':t['title'],'depends_on':t['dependencies'],'state':'PLANNED_NOT_OPENED','delivery':'One independently reviewable task change on selected research branch unless later user instruction changes integration policy','files':raw.get('proposed_paths',raw.get('paths',[])),'acceptance':raw.get('acceptance',[]),'no_auto_merge':True})
 write('PR_PLAN.json',{'schema':'pr_plan.v1','publication_prs':'publication/GITHUB_RECEIPT.json after publication','implementation_prs':pr,'distinction':'Publication PRs contain current packet and inherited branch history; proposed implementation PR units are not fabricated open GitHub PRs.'})
 print(json.dumps({'tasks':len(tasks),'dag_acyclic':True,'initial_completed':sorted(COMPLETED)},indent=2))
if __name__=='__main__':main()
