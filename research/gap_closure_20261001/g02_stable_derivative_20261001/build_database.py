"""Create DBv9 by preserving all DBv8 tables and adding one G02 research step."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build(baseline, evidence_map, status_file, output, receipt):
    baseline, output, receipt = map(Path, (baseline, output, receipt))
    if output.exists() or receipt.exists():
        raise ValueError('create-only DB and receipt required')
    if sha(baseline) != '29cb9f002be65c48e4b002771b4f3649ddbc947ec626b805e381a0bfaf154ba2':
        raise ValueError('DBv8 baseline identity mismatch')
    evidence=json.loads(Path(evidence_map).read_text())
    status=json.loads(Path(status_file).read_text())
    if status['gap_id']!='G02' or status['status']!='UNRESOLVED':
        raise ValueError('this update is confined to G02 without gate promotion')
    records=[]
    for e in evidence:
        p=Path(e['path'])
        if sha(p)!=e['sha256']:
            raise ValueError('evidence identity mismatch')
        records.append((e['evidence_id'],e['kind'],e['package_path'],e['sha256'],p.stat().st_size,p.read_text()))
    with output.open('xb') as dst, baseline.open('rb') as src:
        shutil.copyfileobj(src,dst)
    conn=sqlite3.connect(output)
    conn.execute('PRAGMA foreign_keys=ON')
    old_view=conn.execute("SELECT sql FROM sqlite_master WHERE type='view' AND name='current_research_gap_status'").fetchone()[0]
    with conn:
        conn.execute('CREATE TABLE derivative_research_evidence (evidence_id TEXT PRIMARY KEY, kind TEXT NOT NULL, package_path TEXT NOT NULL, sha256 TEXT NOT NULL, bytes INTEGER NOT NULL, record_json TEXT NOT NULL)')
        conn.executemany('INSERT INTO derivative_research_evidence VALUES (?,?,?,?,?,?)',records)
        conn.execute('CREATE TABLE derivative_research_status (gap_id TEXT PRIMARY KEY REFERENCES research_gap_status(gap_id), status TEXT NOT NULL, closure_label TEXT NOT NULL, record_json TEXT NOT NULL)')
        conn.execute('INSERT INTO derivative_research_status VALUES (?,?,?,?)',(status['gap_id'],status['status'],status['closure_label'],json.dumps(status,ensure_ascii=False,sort_keys=True)))
        conn.execute(old_view.replace('CREATE VIEW current_research_gap_status AS','CREATE VIEW current_research_gap_status_v8 AS',1))
        conn.execute('DROP VIEW current_research_gap_status')
        conn.execute('CREATE VIEW current_research_gap_status AS SELECT old.database_gap_id,old.gap_id,COALESCE(new.status,old.status) AS status,COALESCE(new.closure_label,old.closure_label) AS closure_label,COALESCE(new.record_json,old.record_json) AS record_json,CASE WHEN new.gap_id IS NULL THEN old.status_source ELSE \'R4W_G02_DERIVATIVE_RESEARCH\' END AS status_source FROM current_research_gap_status_v8 old LEFT JOIN derivative_research_status new USING(gap_id)')
    prior=sqlite3.connect('file:'+str(baseline.resolve())+'?mode=ro',uri=True)
    preserved=[]
    for name,schema in prior.execute("SELECT name,sql FROM sqlite_master WHERE type='table'"):
        if conn.execute("SELECT sql FROM sqlite_master WHERE name=?",(name,)).fetchone()!=(schema,):
            raise ValueError('historical schema changed: '+name)
        ident='"'+name.replace('"','""')+'"'
        old=list(prior.execute('SELECT * FROM '+ident))
        if Counter(old)!=Counter(conn.execute('SELECT * FROM '+ident)):
            raise ValueError('historical rows changed: '+name)
        preserved.append({'table':name,'rows':len(old),'schema_equal':True,'row_multiset_equal':True})
    if conn.execute('PRAGMA integrity_check').fetchall()!=[('ok',)] or conn.execute('PRAGMA foreign_key_check').fetchall():
        raise ValueError('DB integrity/foreign key failure')
    current=conn.execute('SELECT gap_id,status,closure_label,status_source FROM current_research_gap_status ORDER BY gap_id').fetchall()
    historical=prior.execute('SELECT * FROM current_research_gap_status ORDER BY gap_id').fetchall()
    if conn.execute('SELECT * FROM current_research_gap_status_v8 ORDER BY gap_id').fetchall()!=historical:
        raise ValueError('v8 view was not preserved')
    prior.close();conn.close()
    result={'schema':'BASS_R4W_DB9_VALIDATION_V1','baseline_sha256':sha(baseline),'database_sha256':sha(output),'database_bytes':output.stat().st_size,'preserved_tables':preserved,'preserved_table_count':len(preserved),'preserved_row_count':sum(x['rows'] for x in preserved),'new_evidence_rows':len(records),'new_status_rows':1,'integrity_check':'ok','foreign_key_violations':0,'previous_effective_view_preserved_as':'current_research_gap_status_v8','effective_status_view':'current_research_gap_status','effective_statuses':current,'production_admission':'HOLD','capture':False}
    with receipt.open('x') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('baseline','evidence-map','status-file','output','receipt'):
        p.add_argument('--'+name,required=True)
    a=p.parse_args();r=build(a.baseline,a.evidence_map,a.status_file,a.output,a.receipt)
    print(json.dumps({k:r[k] for k in ('database_sha256','database_bytes','preserved_table_count','new_evidence_rows')}))
