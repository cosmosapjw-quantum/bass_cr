"""Export persisted endpoint results; no endpoint evaluation or physical calls."""
import csv,datetime,hashlib,importlib.util,json,os,pathlib,platform,resource,sys,time
start=time.time();utc=datetime.datetime.now(datetime.timezone.utc).isoformat();base=pathlib.Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('endpoint',base/'src/endpoint_analysis.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
result_path=base/'evidence/endpoint/RESULT.json';before=hashlib.sha256(result_path.read_bytes()).hexdigest();result=json.loads(result_path.read_text())
for name,rows in [('ancestry',result['ancestry_rows']),('selected',result['selected_rows']),('comparisons',result['comparisons'])]:
 with (base/'evidence/endpoint'/(name+'.csv')).open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for row in rows for k in row)));writer.writeheader();writer.writerows({k:json.dumps(v) if isinstance(v,(dict,list)) else v for k,v in row.items()} for row in rows)
module.plot(base,result)
assert hashlib.sha256(result_path.read_bytes()).hexdigest()==before
paths=[base/'src/endpoint_analysis.py',pathlib.Path(__file__),result_path,base/'state/IMPLEMENTATION_AMENDMENT_01.json',*sorted((base/'evidence/figures').glob('*.*')),*sorted((base/'evidence/figures/initial_connected_bounds').glob('*'))]
receipt={'command':[sys.executable,*sys.argv],'cwd':os.getcwd(),'start_utc':utc,'end_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'actual_exit':0,'elapsed_s':time.time()-start,'environment':{'python':sys.version,'platform':platform.platform()},'peak_rss_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'endpoint_evaluation_calls':0,'physical_G_builds':0,'physical_transport_calls':0,'prior_test_suite_reruns':0,'initial_connected_bounds':'SUPERSEDED; original bytes retained','result_sha256_unchanged':before,'hashes':{str(p.relative_to(base)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}
(base/'evidence/endpoint/AMENDMENT_EXPORT_EXIT.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'actual_exit':0,'elapsed_s':receipt['elapsed_s'],'result_sha256':before}))
