"""Dedicated-group supervisor using the approved existing group teardown/packager."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import argparse,json,os,signal,subprocess,time
from static_tail import APPROVAL,request,strict_json,sha,write_new
from supervise_a3 import _exists,_terminate_group,_package

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__,allow_abbrev=False)
    for name in ('proposal','source-pins','inputs','build','out','approved-proposal-sha256'):p.add_argument('--'+name,required=True)
    a=p.parse_args(argv);proposal=strict_json(a.proposal);out=Path(a.out)
    if os.environ.get('ALLOW_NEW_NATIVE_R4P0')!=APPROVAL or sha(a.proposal)!=a.approved_proposal_sha256:
        raise PermissionError('explicit exact proposal approval required before child launch')
    if str(out.resolve())!=proposal['out_path']:raise ValueError('approved output path mismatch')
    request(a.proposal,a.source_pins,a.inputs,a.build,out.with_name(out.name+'_PRELAUNCH'),approved_sha='',preflight_only=True)
    # The parent admission records source/inputs/resources but consumes nothing.
    deadline=min(proposal['deadline_unix'],time.time()+proposal['wall_seconds']);grace=proposal['termination_grace_seconds']
    command=[sys.executable,'-I','-B',str(Path(__file__).with_name('run_tail.py')),
             '--proposal',a.proposal,'--source-pins',a.source_pins,'--inputs',a.inputs,'--build',a.build,'--out',a.out,
             '--approved-proposal-sha256',a.approved_proposal_sha256]
    child=subprocess.Popen(command,start_new_session=True);pgid=child.pid;started=time.time();stop=False
    def handler(signum,frame):
        nonlocal stop
        stop=True
    oldterm=signal.signal(signal.SIGTERM,handler);oldint=signal.signal(signal.SIGINT,handler)
    try:
        while child.poll() is None and not stop and time.time()<deadline and not (out/'FIRST_FAILURE.json').exists():time.sleep(.2)
        timed_out=time.time()>=deadline;failure_seen=(out/'FIRST_FAILURE.json').exists()
        termination={'term_sent':False,'kill_sent':False,'group_exited':True}
        if child.poll() is None or _exists(pgid):termination=_terminate_group(pgid,grace)
        status=child.wait()
        if _exists(pgid):termination=_terminate_group(pgid,grace)
        receipt={'schema':'BASS_R4P0_STATIC_DEDICATED_GROUP_SUPERVISOR_V1','child_pid':child.pid,'process_group':pgid,
                 'started_unix':started,'ended_unix':time.time(),'deadline_unix':deadline,'approved_deadline_unix':proposal['deadline_unix'],
                 'grace_seconds':grace,'deadline_reached':timed_out,'external_stop_requested':stop,
                 'first_failure_seen':failure_seen,'child_exit_status':status,'termination':termination,
                 'descendants_exited':not _exists(pgid),'proposal_sha256':sha(a.proposal)}
        # SIGTERM/deadline may interrupt before the child records a failure.
        if out.is_dir() and not (out/'RETURN_REPORT.json').exists():
            write_new(out/'RETURN_REPORT.json',{'status':'R4P0_B0_STATIC_EXECUTION_INTERRUPTED','candidate_created':False,'deadline_reached':timed_out,'external_stop_requested':stop})
        write_new(out.with_name(out.name+'_SUPERVISOR.json'),receipt)
        archive=_package(out,receipt)
        if archive:write_new(out.with_name(out.name+'_ARCHIVE_RECEIPT.json'),archive)
        return status if not timed_out and not stop and not failure_seen else 124 if timed_out else 2
    finally:
        signal.signal(signal.SIGTERM,oldterm);signal.signal(signal.SIGINT,oldint)

if __name__=='__main__':raise SystemExit(main())
