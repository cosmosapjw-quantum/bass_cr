import json,os,signal,subprocess,sys,time
signal.signal(signal.SIGTERM,signal.SIG_IGN)
child=subprocess.Popen([sys.executable,'-c','import signal,time;signal.signal(signal.SIGTERM,signal.SIG_IGN);time.sleep(30)'],start_new_session=True)
open('/workspace/scratch/da42c813ee8c/bass_cr/research/cr_c21i_callback_optimization_20261020/evidence/paired_pilot_failure_01/raw/test_timeout_cleans_detached_owned_child_and_spares_control/stub_child.json','w').write(json.dumps({'pid':child.pid,'parent':os.getpid()}))
time.sleep(30)
