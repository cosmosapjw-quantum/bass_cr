#!/usr/bin/env python3
"""One bounded whole-file HTTPS GET from a connector-issued URL. No science."""
import datetime, hashlib, json, os, pathlib, resource, signal, sys, time, urllib.error, urllib.parse, urllib.request

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def main():
    request=json.load(sys.stdin)
    destination=pathlib.Path(request["destination"])
    receipt_path=pathlib.Path(request["receipt_path"])
    if not destination.is_absolute() or not receipt_path.is_absolute():
        raise ValueError("absolute output paths required")
    if destination.exists() or receipt_path.exists():
        raise FileExistsError("create-only output already exists")
    parsed=urllib.parse.urlsplit(request["download_url"])
    if parsed.scheme!="https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("connector-issued HTTPS URL required")
    expected_bytes=int(request["expected_bytes"])
    if expected_bytes<0:raise ValueError("nonnegative byte count required")
    destination.parent.mkdir(parents=True,exist_ok=True)
    receipt_path.parent.mkdir(parents=True,exist_ok=True)
    started=now(); t=time.monotonic(); c=time.process_time()
    affinity_before=sorted(os.sched_getaffinity(0))
    if 0 in affinity_before:os.sched_setaffinity(0,{0})
    resource.setrlimit(resource.RLIMIT_CPU,(10,10))
    resource.setrlimit(resource.RLIMIT_AS,(256*1024*1024,256*1024*1024))
    def timeout(_sig,_frame):raise TimeoutError("whole GET deadline")
    signal.signal(signal.SIGALRM,timeout);signal.alarm(60)
    count=0;digest=hashlib.sha256();status="FAIL";error_type=None;http_status=None;final_host=None
    try:
        # urllib's ordinary runtime proxy handling is used unchanged.
        # No HEAD, Range, automatic retry, custom authentication or proxy bypass.
        with destination.open("xb") as target:
            call=urllib.request.Request(request["download_url"],method="GET")
            with urllib.request.urlopen(call,timeout=30) as response:
                http_status=response.status
                final_host=urllib.parse.urlsplit(response.geturl()).hostname
                if http_status!=200:raise ValueError("complete HTTP200 required")
                while True:
                    block=response.read(1024*1024)
                    if not block:break
                    target.write(block);digest.update(block);count+=len(block)
                    if count>expected_bytes:raise ValueError("download exceeds canonical bytes")
        if count!=expected_bytes or digest.hexdigest()!=request["expected_sha256"]:
            raise ValueError("download identity differs from canonical")
        status="PASS_BYTES_DOWNLOADED"
    except Exception as error:
        error_type=type(error).__name__
        if isinstance(error,urllib.error.HTTPError):http_status=error.code
    finally:signal.alarm(0)
    receipt={"schema":"N5_SINGLE_FULL_GET_RECEIPT_V1","started_utc":started,"finished_utc":now(),"provider":request["provider"],"source_file_id":request["source_file_id"],"source_name":request["source_name"],"destination":str(destination),"status":status,"HTTP_status":http_status,"final_host":final_host,"error_type":error_type,"bytes":count,"sha256":digest.hexdigest(),"expected_bytes":expected_bytes,"expected_sha256":request["expected_sha256"],"size_match":count==expected_bytes,"sha256_match":digest.hexdigest()==request["expected_sha256"],"logical_GET_attempts":1,"HEAD_calls":0,"Range_calls":0,"automatic_retries":0,"HTTP_redirects":"urllib default; logical download may follow provider redirect","proxy_policy":"Runtime default urllib handling; no bypass or credentials logged","whole_wall_deadline_seconds":60,"socket_timeout_seconds":30,"affinity_before":affinity_before,"affinity_during":sorted(os.sched_getaffinity(0)),"process_CPU_s":time.process_time()-c,"wall_s":time.monotonic()-t,"peak_RSS_KiB":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,"science_executions":0,"ZIP_integrity_verification":"SEPARATE_CANONICAL_HELPER_REQUIRED","signed_URL_persisted_in_receipt":False}
    with receipt_path.open("x") as output:json.dump(receipt,output,indent=2)
    print(json.dumps(receipt,indent=2))
    return 0 if status=="PASS_BYTES_DOWNLOADED" else 1
if __name__=="__main__":sys.exit(main())

