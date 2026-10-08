"""Add verified continuation evidence without rewriting the historical DB tables."""
from pathlib import Path
from collections import Counter
import argparse, hashlib, json, shutil, sqlite3

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def build(baseline, evidence_map, status_file, output, receipt):
    baseline, output, receipt = map(Path, (baseline, output, receipt))
    if output.exists() or receipt.exists():
        raise ValueError('create-only database and receipt required')
    entries = json.loads(Path(evidence_map).read_text())
    statuses = json.loads(Path(status_file).read_text())
    if len({e['evidence_id'] for e in entries}) != len(entries):
        raise ValueError('duplicate evidence ID')
    records = []
    for e in entries:
        p = Path(e['path'])
        if sha(p) != e['sha256']:
            raise ValueError('evidence byte identity changed: '+str(p))
        records.append((e['evidence_id'], e['kind'], e['package_path'], e['sha256'],
                        p.stat().st_size, p.read_text()))
    if len({s['gap_id'] for s in statuses}) != len(statuses):
        raise ValueError('duplicate continuation gap ID')
    with output.open('xb') as dst, baseline.open('rb') as src:
        shutil.copyfileobj(src, dst)
    conn = sqlite3.connect(output)
    conn.execute('PRAGMA foreign_keys=ON')
    with conn:
        conn.execute('CREATE TABLE continuation_evidence (evidence_id TEXT PRIMARY KEY, kind TEXT NOT NULL, package_path TEXT NOT NULL, sha256 TEXT NOT NULL CHECK(length(sha256)=64), bytes INTEGER NOT NULL, record_json TEXT NOT NULL)')
        conn.execute('CREATE TABLE continuation_scientific_status (gap_id TEXT PRIMARY KEY REFERENCES research_gap_status(gap_id), status TEXT NOT NULL, closure_label TEXT NOT NULL, record_json TEXT NOT NULL)')
        conn.executemany('INSERT INTO continuation_evidence VALUES (?,?,?,?,?,?)', records)
        conn.executemany('INSERT INTO continuation_scientific_status VALUES (?,?,?,?)',
            [(s['gap_id'], s['status'], s['closure_label'], json.dumps(s, ensure_ascii=False, sort_keys=True)) for s in statuses])
        conn.execute('CREATE VIEW current_research_gap_status AS SELECT old.database_gap_id, old.gap_id, COALESCE(new.status,old.status) AS status, COALESCE(new.closure_label,old.closure_label) AS closure_label, COALESCE(new.record_json,old.record_json) AS record_json, CASE WHEN new.gap_id IS NULL THEN \'ARCHIVED_V7\' ELSE \'R4V_CONTINUATION\' END AS status_source FROM research_gap_status old LEFT JOIN continuation_scientific_status new USING(gap_id)')
    prior = sqlite3.connect('file:'+str(baseline.resolve())+'?mode=ro', uri=True)
    preserved = []
    for name, schema in prior.execute("SELECT name,sql FROM sqlite_master WHERE type='table'"):
        actual = conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?",(name,)).fetchone()
        if actual != (schema,):
            raise ValueError('historical schema changed: '+name)
        ident = '"'+name.replace('"','""')+'"'
        old = list(prior.execute('SELECT * FROM '+ident))
        if Counter(old) != Counter(conn.execute('SELECT * FROM '+ident)):
            raise ValueError('historical rows changed: '+name)
        preserved.append({'table':name,'rows':len(old),'schema_equal':True,'row_multiset_equal':True})
    integrity = conn.execute('PRAGMA integrity_check').fetchall()
    foreign = conn.execute('PRAGMA foreign_key_check').fetchall()
    if integrity != [('ok',)] or foreign:
        raise ValueError('SQLite integrity or foreign-key validation failed')
    current = [dict(zip(('gap_id','status','closure_label','status_source'),r)) for r in conn.execute('SELECT gap_id,status,closure_label,status_source FROM current_research_gap_status ORDER BY gap_id')]
    prior.close(); conn.close()
    result = {'schema':'BASS_R4V_DB8_VALIDATION_V1','baseline_sha256':sha(baseline),
        'database_sha256':sha(output),'database_bytes':output.stat().st_size,
        'preserved_tables':preserved,'preserved_table_count':len(preserved),
        'preserved_row_count':sum(r['rows'] for r in preserved),
        'new_evidence_rows':len(records),'new_status_rows':len(statuses),
        'effective_status_view':'current_research_gap_status','effective_statuses':current,
        'integrity_check':'ok','foreign_key_violations':0,
        'historical_scientific_claims_rewritten':False,'capture':False,'production_admission':'HOLD'}
    with receipt.open('x') as f:
        json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('baseline','evidence-map','status-file','output','receipt'):
        p.add_argument('--'+name,required=True)
    a=p.parse_args()
    r=build(a.baseline,a.evidence_map,a.status_file,a.output,a.receipt)
    print(json.dumps({k:r[k] for k in ('database_sha256','database_bytes','preserved_table_count','new_evidence_rows','new_status_rows')}))
