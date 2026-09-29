from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import time
import zipfile


HERE=Path(__file__).resolve().parents[1]


def test_deadline_terminates_only_dedicated_synthetic_group(tmp_path):
    receipt=tmp_path/'receipt.json'
    env={**os.environ,'ALLOW_NEW_NATIVE_R4F':'YES_I_AUTHORIZE_MIGRATION'}
    command=[sys.executable,'-I','-B',str(HERE/'supervise.py'),
             '--deadline-unix',str(time.time()+1),
             '--grace-seconds','1','--receipt',str(receipt),
             '--out',str(tmp_path/'synthetic_out'),'--',
             '/bin/sh','-c','sleep 20 & wait']
    completed=subprocess.run(command,env=env,timeout=6,capture_output=True,text=True)
    record=json.loads(receipt.read_text())
    assert completed.returncode==124
    assert record['deadline_reached'] is True
    assert record['termination']['term_sent'] is True
    assert record['descendants_exited'] is True


def test_supervisor_packages_only_existing_child_bytes(tmp_path):
    out=tmp_path/'result'
    receipt=tmp_path/'supervisor.json'
    env={**os.environ,'ALLOW_NEW_NATIVE_R4F':'YES_I_AUTHORIZE_MIGRATION'}
    child=[sys.executable,'-c',
           'from pathlib import Path; import sys; p=Path(sys.argv[1]); p.mkdir(); (p/"partial.txt").write_text("bytes")',
           str(out)]
    command=[sys.executable,'-I','-B',str(HERE/'supervise.py'),
             '--deadline-unix',str(time.time()+10),
             '--grace-seconds','1','--receipt',str(receipt),
             '--out',str(out),'--',*child]
    completed=subprocess.run(command,env=env,timeout=5,capture_output=True,text=True)
    assert completed.returncode==0
    with zipfile.ZipFile(tmp_path/'result_RETURN.zip') as z:
        assert z.read('partial.txt')==b'bytes'
        assert 'SUPERVISOR_RECEIPT.json' in z.namelist()
        assert 'RETURN_REPORT.json' not in z.namelist()
