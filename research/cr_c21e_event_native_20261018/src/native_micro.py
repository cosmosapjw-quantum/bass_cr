"""Bounded persistent bridge; protocol checking is NOT native science validation."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import selectors
import subprocess
import time
import numpy as np
from event_coupler import (MicroRates,DomainError,ProviderFailure,require_state,temperature)

OWNER='6ea2b1b4b3875c9163cafc45efe720afded43fc4'

class NativeMicro:
    kind='NATIVE_ORIGINAL_NONPHOTO_RUST'
    def __init__(self,command:list[str],output:Path,timeout:float=15.,max_calls:int=20000):
        if timeout<=0 or not np.isfinite(timeout) or max_calls<1:raise ValueError('invalid process budget')
        self.command=list(command);self.timeout=timeout;self.max_calls=max_calls;self.calls=0;self.closed=False
        output=Path(output);output.mkdir(parents=True,exist_ok=True)
        self.stderr=(output/'native_stderr.log').open('x')
        self.log=(output/'native_points.jsonl').open('x')
        self.process=None;self.selector=selectors.DefaultSelector();self.buffer=bytearray()
        try:
            self.process=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.stderr,bufsize=0)
            self.selector.register(self.process.stdout,selectors.EVENT_READ)
            hello=self._line()
            if hello!=f'C21E_NONPHOTO_V1\t{OWNER}':raise ProviderFailure('NATIVE_OWNER_HANDSHAKE '+hello)
            exe=Path(command[0])
            (output/'native_process.json').write_text(json.dumps({'owner':OWNER,'command':command,'binary_sha256':hashlib.sha256(exe.read_bytes()).hexdigest() if exe.is_file() else None,'timeout_s':timeout,'max_calls':max_calls},indent=2)+'\n')
        except BaseException:
            self.close();raise

    def _line(self)->str:
        end=time.monotonic()+self.timeout
        while b'\n' not in self.buffer:
            left=end-time.monotonic()
            if left<=0 or not self.selector.select(left):raise ProviderFailure('NATIVE_TIMEOUT')
            block=os.read(self.process.stdout.fileno(),65536)
            if not block:raise ProviderFailure('NATIVE_EOF')
            self.buffer.extend(block)
            if len(self.buffer)>1048576:raise ProviderFailure('NATIVE_OUTPUT_LIMIT')
        line,_,tail=self.buffer.partition(b'\n');self.buffer=bytearray(tail)
        try:return line.decode('ascii')
        except UnicodeDecodeError as e:raise ProviderFailure('NATIVE_NONASCII') from e

    def __call__(self,a,g,nh0,Y)->MicroRates:
        require_state(g,Y)
        if self.closed:raise ProviderFailure('NATIVE_CLOSED')
        if self.calls>=self.max_calls:raise ProviderFailure('NATIVE_CALL_BUDGET')
        if not (np.isfinite([a,nh0,Y]).all() and 0<a<=1 and nh0>0 and Y>=0):raise DomainError('EXPLICIT_FIXTURE_DOMAIN')
        args=[a,nh0,nh0*Y,*g]
        request='EVAL\t'+'\t'.join(format(float(v),'.17e') for v in args)
        self.calls+=1
        start=time.monotonic()
        try:
            self.process.stdin.write((request+'\n').encode('ascii'));self.process.stdin.flush()
            response=self._line()
        except (OSError,ProviderFailure) as e:
            self.log.write(json.dumps({'request':request,'error':str(e),'seconds':time.monotonic()-start})+'\n');self.log.flush()
            self.close();raise ProviderFailure(str(e)) from e
        self.log.write(json.dumps({'request':request,'response':response,'seconds':time.monotonic()-start})+'\n');self.log.flush()
        if response.startswith('ERR\tDOMAIN '):raise DomainError(response)
        if not response.startswith('OK\t'):raise ProviderFailure('NATIVE_PROTOCOL '+response)
        try:v=np.array([float(s) for s in response.split('\t')[1:]])
        except ValueError as e:raise ProviderFailure('NATIVE_FLOAT') from e
        if v.shape!=(23,) or not np.isfinite(v).all():raise ProviderFailure('NATIVE_RESPONSE_SHAPE')
        if not np.allclose(v[:3],[a,nh0/a**3,nh0*Y/a**3],rtol=4e-14,atol=0):raise ProviderFailure('NATIVE_DENSITY_IDENTITY')
        if not np.isclose(v[3],temperature(g,Y),rtol=4e-13,atol=1e-10):raise ProviderFailure('NATIVE_EOS_IDENTITY')
        if not np.all(v[18:]==0):raise ProviderFailure('NATIVE_DOUBLE_PHOTO_OR_GEOMETRY_OWNER')
        rates=MicroRates(v[4:7],v[7],v[8],v[9],v[10],v[11:14],v[14:17],float(v[17]))
        rates.validate(Y)
        return rates

    def close(self):
        if self.closed:return
        self.closed=True
        if self.process is not None:
            try:
                if self.process.poll() is None:
                    self.process.stdin.write(b'QUIT\n');self.process.stdin.flush();self.process.wait(timeout=1)
            except (OSError,subprocess.TimeoutExpired):
                self.process.terminate()
                try:self.process.wait(timeout=1)
                except subprocess.TimeoutExpired:self.process.kill();self.process.wait()
            for stream in (self.process.stdin,self.process.stdout):
                if stream is not None:stream.close()
        self.selector.close();self.log.close();self.stderr.close()
    def __enter__(self):return self
    def __exit__(self,*_):self.close()
