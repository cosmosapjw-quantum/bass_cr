"""Build the private v2 catalog without modifying any v1 row or file.

Document acquisition/identity review is separate. This builder consumes the
review decisions and performs no network access or scientific calculation.
"""
import collections
import csv
import datetime as dt
import hashlib
import json
import mimetypes
from pathlib import Path
import re
import shutil
import sqlite3

BASE = Path(__file__).resolve().parents[1]
LEGACY = BASE / 'v1' if (BASE / 'v1').exists() else BASE.parent / 'v1'
TREE = BASE / 'merged'
OUT = TREE / 'v2'
DATE = '20261001'
DBNAME = 'BASS_CR_SOURCE_DATABASE_' + DATE + '_v2.sqlite'
BIBNAME = 'BASS_CR_REFERENCES_' + DATE + '_v2.bib'
STATUSNAME = 'BASS_CR_FULLTEXT_RECOVERY_STATUS_' + DATE + '.csv'
RELNAME = 'BASS_CR_VERSION_RELATIONS_' + DATE + '.csv'
MANNAME = 'BASS_CR_FULLTEXT_RECOVERY_MANIFEST_' + DATE + '.json'


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def jdump(p, value):
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def writecsv(p, rows, fields):
    with p.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fields, extrasaction='ignore')
        w.writeheader()
        for row in rows:
            w.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v
                        for k, v in row.items() if k in fields})


def main():
    assert not TREE.exists(), 'create-only output tree'
    TREE.mkdir()
    shutil.copytree(LEGACY, TREE / 'v1')
    OUT.mkdir()
    for name in ['acquisition', 'supplement', 'footnotes', 'verified_chapter', 'scripts']:
        shutil.copytree(BASE / name, OUT / name,
                        ignore=shutil.ignore_patterns('__pycache__'))
    (OUT / 'evidence').mkdir()
    for name in ['RECOVERY_INVENTORY.json', 'WEB_SEARCH_LEDGER.json', 'IDENTITY_DECISIONS.json',
                 'INDEPENDENT_AUDIT_INITIAL.md', 'INDEPENDENT_AUDIT_CORRECTIONS.json',
                 'JOB3_PINNED_SCRIPT_COMPARISON.json']:
        shutil.copyfile(BASE / 'evidence' / name, OUT / 'evidence' / name)
    shutil.copytree(BASE / 'evidence/pdf_review', OUT / 'evidence/pdf_review')
    for name in ['RESEARCH_RECORD.md', 'public_targets.json', 'supplement_spec.json', 'footnote_spec.json']:
        shutil.copyfile(BASE / name, OUT / name)
    for folder in ['transport', 'transport_supplement', 'transport_footnotes']:
        target = OUT / 'evidence' / (folder.upper() + '_RECEIPT.json')
        original = BASE / folder / 'TRANSPORT_RECEIPT.json'
        if not original.exists():
            original = BASE / 'evidence' / target.name
        shutil.copyfile(original, target)
    certificate = BASE / 'evidence/transport-public.pem'
    if not certificate.exists():
        certificate = BASE / 'scripts/transport-public.pem'
    shutil.copyfile(certificate, OUT / 'scripts/transport-public.pem')
    # The private key and encrypted temporary transport never enter the archive.
    decisions = json.loads((BASE / 'evidence/IDENTITY_DECISIONS.json').read_text())
    selected = {x['source_id']: x for x in decisions if x['fulltext_verified']}
    targets = json.loads((BASE / 'public_targets.json').read_text())
    target_ids = {r['source_id'] for r in targets}
    a1 = json.loads((BASE / 'acquisition/ACQUISITION_RECOVERY.json').read_text())
    a2 = json.loads((BASE / 'supplement/ACQUISITION_SUPPLEMENT.json').read_text())
    a3 = json.loads((BASE / 'footnotes/ACQUISITION_FOOTNOTES.json').read_text())
    attempts = [(batch, x) for batch, obj in [('acquisition', a1), ('supplement', a2), ('footnotes', a3)]
                for x in obj['attempts']]
    legacy_path = TREE / 'v1/02_database/research_sources.sqlite'
    shutil.copyfile(legacy_path, OUT / DBNAME)
    c = sqlite3.connect(OUT / DBNAME)
    c.row_factory = sqlite3.Row
    c.execute('PRAGMA foreign_keys=ON')
    legacy = [dict(r) for r in c.execute('SELECT * FROM sources')]
    source_records = {r['source_id']: json.loads(r['record_json']) for r in legacy}
    c.executescript('''
    CREATE TABLE works(
      work_id TEXT PRIMARY KEY, source_id TEXT UNIQUE NOT NULL REFERENCES sources(source_id),
      title TEXT NOT NULL, authors TEXT, doi TEXT, arxiv TEXT, publication_year INTEGER,
      fulltext_status TEXT NOT NULL, version_class TEXT, fulltext_format TEXT,
      cited_version_id TEXT, selected_version_id TEXT, latest_version TEXT,
      selection_reason TEXT, material_change_status TEXT, manual_access TEXT, notes TEXT);
    CREATE TABLE versions(
      version_id TEXT PRIMARY KEY, work_id TEXT NOT NULL REFERENCES works(work_id),
      title TEXT, authors TEXT, doi TEXT, arxiv TEXT, publication_year INTEGER,
      version_type TEXT NOT NULL, version_label TEXT NOT NULL, identity_status TEXT NOT NULL,
      complete_fulltext INTEGER NOT NULL DEFAULT 0, cited_version INTEGER NOT NULL DEFAULT 0,
      latest_selection_reason TEXT, material_change_status TEXT, notes TEXT);
    CREATE TABLE acquisition_attempts(
      attempt_id INTEGER PRIMARY KEY, legacy_attempt_id INTEGER,
      work_id TEXT REFERENCES works(work_id), batch TEXT NOT NULL, source_url TEXT,
      final_url TEXT, access_route TEXT, kind TEXT, status TEXT, http_status INTEGER,
      failure_class TEXT, failure_subcode TEXT, started_utc TEXT, completed_utc TEXT,
      local_path TEXT, sha256 TEXT, bytes INTEGER, notes TEXT, record_json TEXT NOT NULL);
    CREATE TABLE claims(
      claim_id TEXT PRIMARY KEY, work_id TEXT REFERENCES works(work_id), verbatim TEXT NOT NULL,
      origin TEXT NOT NULL, status TEXT NOT NULL, scientific_validation_performed INTEGER NOT NULL,
      ceiling TEXT NOT NULL);
    CREATE TABLE gaps(
      gap_id TEXT PRIMARY KEY, work_id TEXT REFERENCES works(work_id), status TEXT NOT NULL,
      origin TEXT NOT NULL, description TEXT NOT NULL, manual_access TEXT, record_json TEXT NOT NULL);
    CREATE TABLE code_artifacts(
      artifact_id TEXT PRIMARY KEY, repository TEXT NOT NULL UNIQUE, commit_sha TEXT NOT NULL,
      local_path TEXT NOT NULL, sha256 TEXT NOT NULL, bytes INTEGER NOT NULL,
      license_status TEXT, status TEXT NOT NULL, downloaded_code_executed INTEGER NOT NULL,
      record_json TEXT NOT NULL);
    CREATE TABLE relations(
      relation_id INTEGER PRIMARY KEY, from_work_id TEXT REFERENCES works(work_id),
      to_work_id TEXT REFERENCES works(work_id), from_version_id TEXT REFERENCES versions(version_id),
      to_version_id TEXT REFERENCES versions(version_id), relationship TEXT NOT NULL,
      material_change_status TEXT NOT NULL, evidence TEXT NOT NULL);
    CREATE TABLE provenance(
      provenance_id TEXT PRIMARY KEY, entity_type TEXT NOT NULL, entity_id TEXT NOT NULL,
      source_url TEXT, local_path TEXT, sha256 TEXT, acquired_utc TEXT,
      origin TEXT NOT NULL, notes TEXT, record_json TEXT NOT NULL);
    CREATE VIRTUAL TABLE work_search USING fts5(work_id UNINDEXED,title,authors,doi,fulltext);
    ''')
    fields = {'source_id': 'TEXT', 'work_id': 'TEXT REFERENCES works(work_id)',
              'version_id': 'TEXT REFERENCES versions(version_id)', 'title': 'TEXT',
              'authors': 'TEXT', 'doi': 'TEXT', 'arxiv': 'TEXT', 'publication_year': 'INTEGER',
              'version_type': 'TEXT', 'source_url': 'TEXT', 'final_url': 'TEXT',
              'access_route': 'TEXT', 'local_path': 'TEXT', 'page_count': 'INTEGER',
              'identity_status': 'TEXT', 'license_status': 'TEXT', 'acquired_utc': 'TEXT',
              'supersedes_or_relation': 'TEXT', 'notes': 'TEXT'}
    for name, typ in fields.items():
        c.execute('ALTER TABLE files ADD COLUMN ' + name + ' ' + typ)
    c.execute("UPDATE files SET local_path='v1/'||relative_path")
    relations = []
    workrows = []
    # Every bibliography anchor is a version node even when its full text is missing.
    for r in legacy:
        sid = r['source_id']
        d = source_records[sid]
        old = r['status'] == 'ACQUIRED_PDF_IDENTITY_CHECKED'
        new = selected.get(sid)
        full = old or new is not None
        status = 'LEGACY_FULLTEXT_VERIFIED_REUSED' if old else (
            new['identity_status'] if new else 'FULL_BOOK_NOT_PUBLICLY_ACQUIRED' if sid in
            ['Kato1976', 'Yafaev2000'] else 'NOT_ACQUIRED_FINAL')
        vclass = ('AUTHORITATIVE_PREPRINT' if old and ('arXiv' in (d.get('file_version') or '') or
                   sid == 'HochbruckLubich1997') else 'INSTITUTIONAL_COPY' if old else
                  new['version_class'] if new else 'NOT_ACQUIRED')
        fmt = 'PDF' if old or (new and new.get('signature')) else (
            'HTML_CHAPTER_BUNDLE' if new else None)
        title = (new or {}).get('observed_title') or r['title']
        if sid == 'Enss1979':
            title += ': II. Singular and long-range potentials'
        reason = ('Reuse already acquired pinned v1 file; newest revision not rechecked under hard scope'
                  if old else 'Prefer exact cited published version acquired from institutional/author deposit'
                  if new and fmt == 'PDF' else 'Complete official author-hosted web chapter; publisher PDF unavailable'
                  if new else 'No identity-verified complete full text retrieved; metadata never promoted')
        material = 'NOT_REASSESSED_EXISTING_FILE' if old else ('SAME_CITED_PUBLISHED_VERSION' if new and fmt == 'PDF'
                   else 'NOT_ASSESSED_AGAINST_CITED_PUBLISHER_VERSION' if new else 'NOT_ASSESSABLE_NO_COMPLETE_FULLTEXT')
        pub = [x for batch, x in attempts if x['source_id'] == sid and x['route'] == 'publisher']
        failures = sorted({x.get('failure_class') for batch, x in attempts if x['source_id'] == sid
                           and x.get('failure_class')})
        manual = None if full else (
            'Use institutional Springer ebook access or interlibrary loan for the exact edition; do not treat preview chapters as a book'
            if sid in ['Kato1976', 'Yafaev2000'] else
            'Use an authorized institutional journal subscription or interlibrary loan for DOI ' + r['doi'] +
            '; alternatively request an accepted manuscript from the authors (no request sent)')
        note = 'Original v1 metadata and rows remain in sources; current recovery state is in works.'
        if sid == 'Kato1976':
            note += ' Cited second edition1976; corrected printing1980; DOI-linked Classics1995 reprint; ebook2012. Official21-page front matter confirms1980/1995 relation; it is not a complete book.'
        if sid == 'Yafaev2000':
            note += ' Book LNM1735, first edition2000; ebook2007. Only front matter i–xvi acquired. Same-title ICM1998 article is a different work.'
        if sid == 'KuangLin1996':
            note += ' j189.pdf is a different Montenegro1997 work, rejected. Exact author-list j184 link is dead or returns HTML.'
        if sid == 'Mathias1997':
            note += ' Author PostScript route failed TLS certificate validation; Citeseer404/429. This does not establish absence of a legal public manuscript.'
        if sid == 'Errea1998':
            note += ' HAL metadata/landing timed out and explicit hal-01566050/document returned404; no bypass attempted.'
        if not full:
            note += ' Checked publisher plus independent arXiv title search and DOI-linked metadata/repository routes. Public-copy absence is not proved. Failure classes: ' + ', '.join(failures)
        if old: latest = 'NOT_RECHECKED_V1_SCOPE'
        elif new: latest = new['version_label']
        elif sid == 'Kato1976': latest = '2012 ebook metadata only'
        elif sid == 'Yafaev2000': latest = '2007 ebook metadata only'
        else: latest = 'No alternate complete version retrieved'
        row = dict(work_id=sid, source_id=sid, title=title, authors=r['authors'], doi=r['doi'],
                   arxiv=r['arxiv'], publication_year=r['year'], fulltext_status=status,
                   version_class=vclass, fulltext_format=fmt, cited_version_id=sid + ':cited',
                   selected_version_id=sid + ':available' if full else None,
                   latest_version=latest, selection_reason=reason, material_change_status=material,
                   manual_access=manual, notes=note)
        c.execute('INSERT INTO works VALUES(' + ','.join('?' for _ in row) + ')', tuple(row.values()))
        workrows.append(row)
        citedyear = 1976 if sid == 'Kato1976' else r['year']
        citedlabel = 'Cited second edition1976; exact printing not specified' if sid == 'Kato1976' else 'Cited DOI-linked publisher manifestation'
        citedtype = 'CITED_PUBLISHER_ANCHOR'
        if not r['doi'] and r['arxiv']:
            citedlabel = 'Cited arXiv anchor ' + r['arxiv']
            citedtype = 'CITED_PREPRINT_ANCHOR'
        c.execute('INSERT INTO versions VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                  (sid + ':cited', sid, title, r['authors'], None if sid == 'Kato1976' else r['doi'],
                   r['arxiv'], citedyear, citedtype, citedlabel,
                   'METADATA_ONLY', 0, 1, 'Preserve cited anchor', 'NOT_ASSESSED', note))
        if full:
            label = d.get('file_version') if old else new['version_label']
            vtype = 'AUTHORITATIVE_PREPRINT' if old and vclass == 'AUTHORITATIVE_PREPRINT' else 'INSTITUTIONAL_COPY' if old else new['version_type']
            vid = sid + ':available'
            c.execute('INSERT INTO versions VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                      (vid, sid, title, r['authors'], r['doi'], r['arxiv'], r['year'], vtype, label,
                       ('AUTHORITATIVE_PREPRINT_VERIFIED' if vclass == 'AUTHORITATIVE_PREPRINT' else 'INSTITUTIONAL_COPY_VERIFIED') if old else new['identity_status'], 1, 0, reason, material, note))
            relation = 'PREPRINT_OF' if vclass == 'AUTHORITATIVE_PREPRINT' else 'AUTHOR_WEB_EDITION_OF' if fmt != 'PDF' else 'COPY_OF'
            if not r['doi'] and r['arxiv']:
                relation = 'COPY_OF'
            relations.append(dict(from_work_id=sid, to_work_id=sid, from_version_id=vid,
                                  to_version_id=sid + ':cited', relationship=relation,
                                  material_change_status=material, evidence='v1 identity review reused' if old else new['identity_evidence']))
            if old:
                path = r['relative_path']
                original_attempts = [x for x in d.get('acquisition_attempts',[]) if x.get('sha256') == r['sha256']]
                final_url = next((x.get('final_url') for x in reversed(original_attempts) if x.get('final_url')), None)
                legacy_identity = 'AUTHORITATIVE_PREPRINT_VERIFIED' if vclass == 'AUTHORITATIVE_PREPRINT' else 'INSTITUTIONAL_COPY_VERIFIED'
                c.execute('UPDATE files SET source_id=?,work_id=?,version_id=?,title=?,authors=?,doi=?,arxiv=?,publication_year=?,version_type=?,source_url=?,final_url=?,access_route=?,page_count=?,identity_status=?,license_status=?,supersedes_or_relation=?,notes=? WHERE relative_path=?',
                          (sid,sid,vid,title,r['authors'],r['doi'],r['arxiv'],r['year'],vtype,d.get('original_url'),
                           final_url,'V1_REUSED_WITHOUT_REDOWNLOAD',d.get('page_count'),legacy_identity,
                           d.get('redistribution_permission'),relation,'Inherited v1 identity review; original acquisition UTC not present; not fabricated',path))
        elif sid in target_ids:
            c.execute('INSERT INTO gaps VALUES(?,?,?,?,?,?,?)',
                      ('FULLTEXT_' + sid, sid, status, 'V2_FULLTEXT_RECOVERY', note, manual, json.dumps(row, ensure_ascii=False)))
        for i, text in enumerate(d.get('report_rows_verbatim', [])):
            c.execute('INSERT INTO claims VALUES(?,?,?,?,?,?,?)',
                      (sid + ':report:' + str(i), sid, text, 'V1_REPORT_VERBATIM', 'INHERITED_NOT_REVALIDATED', 0,
                       'Unchanged; source precedent is not a BASS_CR numerical certificate'))
        txtpath = TREE / 'v1/03_extracted_text' / (sid + '.txt')
        txt = txtpath.read_text() if old and txtpath.exists() else ''
        if new and fmt == 'PDF':
            txtpath = OUT / 'evidence/pdf_review' / (sid + '.txt')
            txt = txtpath.read_text()
        elif new:
            txt = '\n'.join(re.sub('<[^>]+>', ' ', (OUT / 'verified_chapter' / ('node%d.html'%n)).read_text()) for n in range(155,190))
        c.execute('INSERT INTO work_search VALUES(?,?,?,?,?)',(sid,title,r['authors'],r['doi'],txt))
    # Partial material is represented separately and never raises a work count.
    for x in decisions:
        if not x['fulltext_verified'] and x['source_id'] in ['Yafaev2000', 'Kato1976']:
            sid = x['source_id'];r = next(y for y in legacy if y['source_id'] == sid)
            c.execute('INSERT INTO versions VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                      (sid + ':frontmatter',sid,r['title'],r['authors'],r['doi'],None,x['publication_year'],x['version_type'],
                       x['version_label'],x['identity_status'],0,0,'Retain legal partial material; complete book not acquired',
                       'INCOMPLETE_CONTENT',x['identity_evidence']))
            relations.append(dict(from_work_id=sid,to_work_id=sid,from_version_id=sid+':frontmatter',
                                  to_version_id=sid+':ebook2012' if sid=='Kato1976' else sid+':ebook2007',relationship='PART_OF',material_change_status='INCOMPLETE_CONTENT',evidence=x['identity_evidence']))
    for sid, label, year, rel, parent in [
        ('Kato1976','Corrected second-edition printing1980',1980,'UPDATED_BY','cited'),
        ('Kato1976','Classics in Mathematics reprint1995',1995,'REPRINT_OF','printing1980'),
        ('Kato1976','DOI-linked ebook published2012; complete text not acquired',2012,'ELECTRONIC_MANIFESTATION_OF','reprint1995'),
        ('Yafaev2000','Ebook published2007; complete text not acquired',2007,'ELECTRONIC_MANIFESTATION_OF','cited')]:
        suffix = 'printing1980' if year == 1980 else 'reprint1995' if year == 1995 else 'ebook' + str(year)
        vid = sid + ':' + suffix; r = next(y for y in legacy if y['source_id'] == sid)
        c.execute('INSERT INTO versions VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                  (vid,sid,r['title'],r['authors'],r['doi'],None,year,'BOOK_MANIFESTATION_METADATA',label,'METADATA_ONLY',0,0,
                   'Official publisher bibliographic metadata; no complete full text', 'NOT_ASSESSED','Manifestations kept separate'))
        fromvid, tovid = (sid + ':' + parent, vid) if rel == 'UPDATED_BY' else (vid, sid + ':' + parent)
        relations.append(dict(from_work_id=sid,to_work_id=sid,from_version_id=fromvid,to_version_id=tovid,
                              relationship=rel,material_change_status='NOT_ASSESSED',evidence='Official Springer catalog dates; Kato1980/1995 relationship is explicit on preserved21-page publisher front matter, pages3 and5'))
    relations.append(dict(from_work_id='LiEtAlErratum2013',to_work_id='LiEtAl2011',from_version_id='LiEtAlErratum2013:available',
                          to_version_id='LiEtAl2011:available',relationship='ERRATUM_OF',material_change_status='CORRECTION_REPORTED_NOT_REPROVED',
                          evidence='Inherited v1 correction identity and both preserved files; no new scientific verification'))
    for rr in relations:
        c.execute('INSERT INTO relations(from_work_id,to_work_id,from_version_id,to_version_id,relationship,material_change_status,evidence) VALUES(?,?,?,?,?,?,?)',tuple(rr.values()))
    # Import old failed/successful attempts without deleting the original table.
    for r in c.execute('SELECT * FROM retrieval_attempts').fetchall():
        d = json.loads(r['record_json'])
        c.execute('INSERT INTO acquisition_attempts(legacy_attempt_id,work_id,batch,source_url,final_url,access_route,kind,status,http_status,local_path,sha256,bytes,notes,record_json) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                  (r['attempt_id'],r['source_id'],r['batch'],r['url'],d.get('final_url'),'V1_INHERITED',d.get('kind'),r['status'],
                   r['http_status'],'v1/'+d['relative_path'] if d.get('relative_path') else None,d.get('sha256'),d.get('bytes'),
                   'Original failure history retained verbatim; missing original UTC not synthesized',r['record_json']))
    for batch, d in attempts:
        subcode = 'LOCAL_WRITE_COLLISION_ALREADY_PRESENT' if d.get('error_type') == 'FileExistsError' else None
        c.execute('INSERT INTO acquisition_attempts(work_id,batch,source_url,final_url,access_route,kind,status,http_status,failure_class,failure_subcode,started_utc,completed_utc,local_path,sha256,bytes,notes,record_json) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                  (d['source_id'],batch,d['requested_url'],d.get('final_url'),d['route'],d['kind'],d['status'],d.get('http_status'),
                   d.get('failure_class'),subcode,d['started_utc'],d.get('completed_utc'),'v2/'+batch+'/'+d['path'] if d.get('path') else None,
                   d.get('sha256'),d.get('bytes'),'Raw FAILED status retained; local duplicate write is not host/network absence' if subcode else None,
                   json.dumps(d,ensure_ascii=False)))
    for g in c.execute('SELECT * FROM report_gaps').fetchall():
        c.execute('INSERT INTO gaps VALUES(?,?,?,?,?,?,?)',(g['gap_id'],None,g['status'],'V1_REPORT_GAP',g['verbatim'],None,json.dumps(dict(g),ensure_ascii=False)))
    ceilings = [
        'Theoretical path from local rho to integrated-tail certificate exists; it has not closed the numerical gate.',
        'Continuous upper majorant rho(z)<=g(z) remains unresolved.',
        'Outer B0 rho~R^-2 samples are empirical evidence, not a theorem.',
        'Raw ||K_TP|| is not a probability-tail error bound.',
        'Finite-window convergence and basis completeness remain separate gates.',
        'B1-B3 are symbolic/preparation only.',
        'capture=false; production=HOLD; all_bound=OPEN; b_grid=NO_GO.']
    for i,text in enumerate(ceilings):
        c.execute('INSERT INTO claims VALUES(?,?,?,?,?,?,?)',('USER_CEILING_'+str(i+1),None,text,'USER_RECOVERY_HANDOFF','PRESERVED_UNCHANGED',0,'Unchanged'))
    for r in c.execute('SELECT * FROM code_snapshots').fetchall():
        f = c.execute('SELECT * FROM files WHERE relative_path=?',(r['archive_path'],)).fetchone()
        d = json.loads(r['record_json'])
        c.execute('INSERT INTO code_artifacts VALUES(?,?,?,?,?,?,?,?,?,?)',
                  (r['repository'],r['repository'],r['commit_sha'],'v1/'+r['archive_path'],f['sha256'],f['bytes'],
                   json.dumps(d.get('license'),ensure_ascii=False),'PINNED_V1_REUSED_NO_REDOWNLOAD',0,r['record_json']))
    # New file records include provenance-only candidates; verification is explicit.
    decision_by_path = {x['local_path']:x for x in decisions}
    raw_by_path = {'v2/'+batch+'/'+x['path']:x for batch,x in attempts if x.get('path')}
    work_by_id = {r['work_id']:r for r in workrows}
    c.commit()
    catalog_paths = sorted(OUT.rglob('*'))
    for file in catalog_paths:
        if not file.is_file() or file.name in [DBNAME,DBNAME+'-journal',DBNAME+'-wal',DBNAME+'-shm']: continue
        path = str(file.relative_to(TREE));d = raw_by_path.get(path,{});decision = decision_by_path.get(path)
        sid = (decision or d).get('source_id');work = work_by_id.get(sid,{})
        rejected = decision and decision['version_type']=='REJECTED_DIFFERENT_WORK'
        vid = (sid+':available' if decision and decision['fulltext_verified'] else
               sid+':frontmatter' if decision and sid in ['Yafaev2000','Kato1976'] else None)
        values = dict(relative_path=path,sha256=digest(file),bytes=file.stat().st_size,mime_type=mimetypes.guess_type(path)[0],
                      source_id=sid,work_id=None if rejected else sid,version_id=vid,title=(decision or {}).get('observed_title') or work.get('title'),
                      authors=work.get('authors') if not rejected else 'Montenegro et al.; not intended target authors',doi=None if rejected else work.get('doi'),
                      arxiv=work.get('arxiv') if not rejected else None,publication_year=(decision or {}).get('observed_year') or work.get('publication_year'),
                      version_type=(decision or {}).get('version_type'),source_url=(decision or {}).get('source_url') or d.get('requested_url'),
                      final_url=(decision or {}).get('final_url') or d.get('final_url'),access_route=(decision or {}).get('access_route') or d.get('route'),
                      local_path=path,page_count=(decision or {}).get('page_count'),identity_status=(decision or {}).get('identity_status') or 'PROVENANCE_OR_METADATA_ONLY',
                      license_status=(decision or {}).get('license_status') or 'Not inferred from public access',acquired_utc=(decision or {}).get('acquired_utc') or d.get('completed_utc'),
                      supersedes_or_relation=(decision or {}).get('relationship'),notes=(decision or {}).get('identity_evidence'))
        keys=list(values);c.execute('INSERT INTO files('+','.join(keys)+') VALUES('+','.join('?' for _ in keys)+')',tuple(values.values()))
    for name,path,notes in [('V1_DB',legacy_path,'Exact byte-identical legacy DB preserved alongside imported tables'),
                            ('IDENTITY_DECISIONS',OUT/'evidence/IDENTITY_DECISIONS.json','Version identity review; no scientific claims tested')]:
        c.execute('INSERT INTO provenance VALUES(?,?,?,?,?,?,?,?,?,?)',
                  (name,'artifact',name,None,str(path.relative_to(TREE)) if path.is_relative_to(TREE) else path.name,
                   digest(path),None,'V2_IMPORT_OR_REVIEW',notes,json.dumps({'bytes':path.stat().st_size,'sha256':digest(path)})))
    c.execute('INSERT INTO provenance VALUES(?,?,?,?,?,?,?,?,?,?)',
              ('V1_ARCHIVE','artifact','V1_ARCHIVE',None,'BASS_CR_LITERATURE_CODE_ARCHIVE_20261001_v1.zip',
               '452451011fa0434a00ea782697043015093d910d7b8924b927281cd31d0fe3ad',None,'V1_RECONCILIATION',
               'Exact original archive bytes/hash verified before import; ZIP is not redundantly embedded in merged tree',json.dumps({'bytes':77109152})))
    c.commit()
    assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    assert not c.execute('PRAGMA foreign_key_check').fetchall()
    assert c.execute('SELECT count(*) FROM works').fetchone()[0]==31
    assert c.execute('SELECT count(*) FROM acquisition_attempts').fetchone()[0]==180+len(attempts)
    assert c.execute('SELECT count(*) FROM retrieval_attempts').fetchone()[0]==180
    c.close()
    # Rebuild bibliography from authoritative legacy metadata with current status.
    def clean(s):
        return str(s).replace('&','\\&').replace('%','\\%').replace('_','\\_')
    entries=[]
    for r in workrows:
        sid=r['source_id'];d=source_records[sid]
        typ='book' if sid in ['Kato1976','Yafaev2000'] else 'incollection' if sid=='TemplatesGHEP' else 'article'
        if not r['doi'] and not d.get('container_title'):
            typ = 'misc'
        auth=' and '.join(x.get('family','')+(', '+x.get('given','') if x.get('given') else '') for x in d.get('authors',[]))
        canonical = 'https://doi.org/'+r['doi'] if r['doi'] else 'https://arxiv.org/abs/'+r['arxiv'] if r['arxiv'] else None
        fields=dict(title=r['title'],author=auth or r['authors'],year=r['publication_year'],doi=r['doi'],url=canonical)
        if typ=='article':
            fields.update({k:d.get(v) for k,v in [('journal','container_title'),('volume','volume'),('number','issue'),('pages','pages')]})
        elif typ=='incollection':
            fields.update(booktitle=d.get('container_title'),publisher=d.get('publisher'),pages=d.get('pages'))
        elif typ=='book':
            fields.update(publisher=d.get('publisher'),edition=2 if sid=='Kato1976' else 1)
        if r['arxiv']: fields.update(eprint=r['arxiv'],archivePrefix='arXiv')
        fields['note']='Recovery status: '+r['fulltext_status']+'. '+r['selection_reason']
        if sid=='Kato1976': fields['note']+='; cited second edition1976; corrected printing1980; 1995 reprint; ebook2012; complete book not acquired'
        if sid=='Yafaev2000': fields['note']+='; LNM1735 book; ebook2007; only front matter acquired; not the ICM1998 article'
        entries.append('@'+typ+'{'+sid+',\n'+',\n'.join('  '+k+' = {'+clean(v)+'}' for k,v in fields.items() if v is not None)+'\n}')
    (OUT/BIBNAME).write_text('\n\n'.join(entries)+'\n')
    statusrows=[]
    for r in workrows:
        if r['source_id'] not in target_ids: continue
        sid=r['source_id'];routes=sorted(set(x['route'] for batch,x in attempts if x['source_id']==sid))
        rr=dict(r,attempt_count=sum(x['source_id']==sid for batch,x in attempts),routes_checked=routes,
                independent_route_minimum_met='publisher' in routes and 'arxiv_title_search' in routes,
                failure_classes=sorted(set(x['failure_class'] for batch,x in attempts if x['source_id']==sid and x.get('failure_class'))),
                acquired_file=selected.get(sid,{}).get('local_path'),source_url=selected.get(sid,{}).get('source_url'))
        statusrows.append(rr)
    writecsv(OUT/STATUSNAME,statusrows,list(statusrows[0]))
    writecsv(OUT/RELNAME,relations,list(relations[0]))
    failed_old=38;failed_new=sum(x['status']=='FAILED' for batch,x in attempts)
    classes=collections.Counter(r['version_class'] for r in workrows if r['fulltext_format'])
    summary=dict(TARGET_WORKS=31,INITIAL_ACQUIRED_PDF_WORKS=13,INITIAL_MISSING_WORKS=18,
                 NEW_VERIFIED_PDF_WORKS=3,NEW_VERIFIED_HTML_CHAPTER_WORKS=1,NEW_DOWNLOADED_CANDIDATE_PDF_FILES=sum(x.get('signature')=='%PDF-' for x in decisions),
                 NEW_PARTIAL_FRONT_MATTER_FILES=2,REJECTED_SOURCE_IDENTITY_CONFLICT_FILES=1,EXACT_PUBLISHER_FULLTEXT=classes['EXACT_PUBLISHER_FULLTEXT'],
                 AUTHORITATIVE_PREPRINT=classes['AUTHORITATIVE_PREPRINT'],ACCEPTED_MANUSCRIPT=0,INSTITUTIONAL_COPY=classes['INSTITUTIONAL_COPY'],
                 VERIFIED_PDF_WORKS_TOTAL=16,FULLTEXT_ACQUIRED_TOTAL=17,IDENTITY_UNRESOLVED_FILES=0,NOT_ACQUIRED=14,
                 FULL_BOOK_NOT_PUBLICLY_ACQUIRED=2,CODE_PROJECTS_PINNED=4,DOCUMENTATION_SOURCES=16,DOCUMENTATION_REGISTER_ROWS=17,
                 FAILED_ATTEMPTS_RETAINED=failed_old+failed_new,LEGACY_ATTEMPTS_RETAINED=180,NEW_ACQUISITION_ATTEMPTS=len(attempts),
                 TOTAL_ACQUISITION_ATTEMPTS=180+len(attempts),LOCAL_REDUNDANT_WRITE_ERRORS_RETAINED=7,scientific_calculations=0,native_authorization_consumption=0,
                 claim_ceilings='UNCHANGED',capture=False,production='HOLD',all_bound='OPEN',b_grid='NO_GO',
                 category_note='Disjoint classes: existing9 authoritative preprints and4 institutional copies are inherited unchanged; new3 exact published PDFs and1 official HTML chapter. Retrieval route for all3 new PDFs is institutional/author deposit.',
                 stopping_rule='Bounded routes checked for all14 unresolved works; blockers and manual access recorded. No universal absence-of-public-copy claim.',
                 generated_utc=dt.datetime.now(dt.timezone.utc).isoformat())
    jdump(OUT/'RECOVERY_SUMMARY.json',summary)
    jdump(OUT/'WORK_STATUS_ALL31.json',workrows)
    jdump(OUT/'FAILED_ACQUISITION_LEDGER.json',[dict(x,batch=batch) for batch,x in attempts if x['status']=='FAILED'])
    hashes={n:{'bytes':(OUT/n).stat().st_size,'sha256':digest(OUT/n)} for n in [DBNAME,BIBNAME,STATUSNAME,RELNAME]}
    report='# BASS_CR full-text recovery v2\n\n'
    report+='검증된 신규 원문은 PDF3편과 공식 저자 Netlib HTML 장1건이다. 기존13 PDF와 고정 코드4개는 재다운로드하지 않고 그대로 재사용했다. 전체31 works 중 usable full text17건(PDF16, HTML1), 미확보14건(책2 포함)이다.\n\n'
    report+='Kato의21쪽·Yafaev의16쪽 front matter와 다른 논문으로 확인된 Kuang1996 후보는 성공 집계에서 제외했다. Netlib은35개 장 페이지, 별도 주석 페이지와 해당 수식 자산을 보존했지만 출판사 PDF와 내용이 정확히 같다는 판정은 하지 않았다.\n\n'
    report+='출판사401/403, HTML 응답, 저장소404, TLS 오류, timeout을 구분했다. 모든 unresolved work에 publisher와 독립 arXiv/저장소 경로를 확인했다. 접근 실패는 공개본 부재의 증명이 아니다. 수동 접근은 해당 DOI의 기관 구독·상호대차·저자 manuscript 요청이며 실제 요청은 보내지 않았다.\n\n'
    report+='## 기존 missing18 최종 상태\n\n| Source ID | 상태 | 형식/메모 |\n|---|---|---|\n'
    for r in statusrows: report+='| '+r['source_id']+' | '+r['fulltext_status']+' | '+str(r['fulltext_format'] or '미확보')+' |\n'
    report+='\n## Version/provenance\n\n신규 PDF3편은 실제 cited journal version을 우선했다. 새 arXiv manuscript를 확보한 항목은 없다. 기존9 preprint의 최신 revision은 hard scope 때문에 재수집하지 않았다. Kato는1976 second edition,1980 corrected printing,1995 reprint,2012 ebook metadata를 분리했고 Yafaev는2000 book과2007 ebook manifestation을 분리했다. Netlib web edition은 revision 번호가 없으므로 official current publicly served copy로 기록하되 material change는 NOT_ASSESSED이다. 기존 Li2011/2013 erratum 관계를 보존했다.\n\n'
    report+='## Counts\n\n```json\n'+json.dumps(summary,ensure_ascii=False,indent=2)+'\n```\n\n## Artifact hashes\n\n```json\n'+json.dumps(hashes,indent=2)+'\n```\n\n'
    report+='v1 원본 파일과 DB·실패180건은 v1/ 아래 그대로 보존한다. 현재 상태는 v2 DB works/files/versions/acquisition_attempts에 있다. legacy sources/retrieval_attempts/code_snapshots는 당시 기록이므로 수정하지 않았다. DB의 local_path는 ZIP root 기준이며 relative_path legacy 값은 원본 기준을 유지한다.\n\n'
    report+='최종 ZIP byte/hash와 provider remote IDs·sizes·revision·R1 tier는 ZIP 생성 후 별도 DELIVERY_RECEIPT에 기록한다. Remote restore 검증은 수행하지 않는다. Local ZIP extraction 검증은 별도 LOCAL_VALIDATION에 기록한다.\n\n'
    report+='scientific calculations=0, native authorization consumption=0, claim ceilings unchanged. capture=false, production=HOLD, all_bound=OPEN, b_grid=NO_GO. 문헌 확보는 과학적 gate closure가 아니다.\n'
    (OUT/'RECOVERY_REPORT_KO.md').write_text(report)
    (TREE/'README_KO.md').write_text('# BASS_CR merged full-text recovery v2\n\nv1/에는 기존224개 archive member의 원본 파일을 모두 그대로 보존했다. v2/에는 새 원문·완전 HTML 장·identity proof·새 DB와 BibTeX·실패 ledger·status/relations·회수 스크립트를 담았다. 시작: v2/RECOVERY_REPORT_KO.md 및 v2/verified_chapter/START_HERE.html.\n\nDB files.local_path는 이 ZIP root 기준이다. Legacy tables는 이전 시점의 authority이며 current state는 works를 사용한다. Manifest의 self-hash와 SHA256SUMS 자체는 순환 참조를 피하기 위해 manifest 대상에서 제외한다. Private transport key와 credentials는 포함하지 않는다. 원문은 개인 연구용 archive이고 공개 재배포 권한을 추정하지 않는다. Remote backup evidence는 별도 DELIVERY_RECEIPT sidecar다.\n\ncapture=false; production=HOLD; all_bound=OPEN; b_grid=NO_GO. Scientific calculations=0; native authorization consumption=0; claim ceilings unchanged.\n')
    manifest_files=[dict(path=str(f.relative_to(TREE)),bytes=f.stat().st_size,sha256=digest(f)) for f in sorted(TREE.rglob('*')) if f.is_file()]
    manifest=dict(summary=summary,artifact_hashes=hashes,new_identity_decisions=decisions,
                  original_v1_archive=dict(bytes=77109152,sha256='452451011fa0434a00ea782697043015093d910d7b8924b927281cd31d0fe3ad'),
                  original_v1_db_sha256=digest(legacy_path),files=manifest_files,
                  exclusions=[MANNAME,'MANIFEST.json','SHA256SUMS'],copyright='Personal research archive; public access does not imply redistribution permission')
    jdump(OUT/MANNAME,manifest)
    manifest_files.append(dict(path='v2/'+MANNAME,bytes=(OUT/MANNAME).stat().st_size,sha256=digest(OUT/MANNAME)))
    jdump(TREE/'MANIFEST.json',dict(files=manifest_files,exclusions=['MANIFEST.json','SHA256SUMS']))
    hashfiles=manifest_files+[dict(path='MANIFEST.json',sha256=digest(TREE/'MANIFEST.json'))]
    (TREE/'SHA256SUMS').write_text(''.join(r['sha256']+'  '+r['path']+'\n' for r in sorted(hashfiles,key=lambda r:r['path'])))
    jdump(BASE/'ARTIFACT_HASHES.json',hashes)
    print(json.dumps(summary,ensure_ascii=False));print(json.dumps(hashes))


if __name__ == '__main__':
    main()
