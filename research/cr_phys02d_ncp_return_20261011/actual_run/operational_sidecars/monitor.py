import pathlib,json,time,datetime,os
base=pathlib.Path(__file__).parent
run=pathlib.Path((base/'RUN_DIR.txt').read_text())
pid=json.loads((run/'RESERVATION.json').read_text())['coordinator_pid']
with (base/'OWNED_RESOURCE_SAMPLES.jsonl').open('x') as log:
 while True:
  owned=[pid];rows=[]
  for current in owned:
   proc=pathlib.Path('/proc')/str(current)
   try:
    children=(proc/'task'/str(current)/'children').read_text().split()
    owned.extend(int(c) for c in children if int(c) not in owned)
    status=(proc/'status').read_text()
    fields={line.split(':',1)[0]:line.split(':',1)[1].strip() for line in status.splitlines() if line.startswith(('VmRSS:','VmHWM:','Threads:'))}
    rows.append(dict(pid=current,affinity=sorted(os.sched_getaffinity(current)),**fields))
   except (OSError,ProcessLookupError):pass
  terminal=(run/'ACTUAL_EXIT.json').exists()
  log.write(json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),owned_processes=rows,terminal_receipt=terminal,files=sorted(x.name for x in run.iterdir())))+'\n');log.flush()
  if terminal:break
  time.sleep(15)
