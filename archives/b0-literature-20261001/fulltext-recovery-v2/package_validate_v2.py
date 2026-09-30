"""Create a private merged ZIP and validate a fresh local extraction.

Uses only the existing tree; no downloads, solver runs or remote restore tests.
The output archive is create-only. Manifests exclude their own circular hashes.
"""
import argparse
import collections
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import subprocess
import tempfile
import zipfile


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def validate(tree):
    root_manifest = json.loads((tree / 'MANIFEST.json').read_text())
    physical = {str(p.relative_to(tree)) for p in tree.rglob('*') if p.is_file()}
    expected = {r['path'] for r in root_manifest['files']}
    assert physical == expected | {'MANIFEST.json', 'SHA256SUMS'}, 'file closure'
    assert len(expected) == len(root_manifest['files']), 'duplicate manifest path'
    for r in root_manifest['files']:
        p = tree / r['path']
        assert p.stat().st_size == r['bytes'] and sha(p) == r['sha256'], r['path']
    hashes = {}
    for line in (tree / 'SHA256SUMS').read_text().splitlines():
        value, name = line.split('  ', 1)
        assert sha(tree / name) == value, name
        hashes[name] = value
    assert set(hashes) == physical - {'SHA256SUMS'}, 'SHA256SUMS closure'
    v2 = tree / 'v2'
    recovery = json.loads((v2 / 'BASS_CR_FULLTEXT_RECOVERY_MANIFEST_20261001.json').read_text())
    assert {r['path'] for r in recovery['files']} == physical - {
        'v2/BASS_CR_FULLTEXT_RECOVERY_MANIFEST_20261001.json', 'MANIFEST.json', 'SHA256SUMS'
    }, 'recovery manifest closure'
    for r in recovery['files']:
        p = tree / r['path']
        assert p.stat().st_size == r['bytes'] and sha(p) == r['sha256'], r['path']
    db = v2 / 'BASS_CR_SOURCE_DATABASE_20261001_v2.sqlite'
    c = sqlite3.connect('file:' + str(db) + '?mode=ro', uri=True)
    c.row_factory = sqlite3.Row
    assert c.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
    assert not c.execute('PRAGMA foreign_key_check').fetchall()
    required = ['works', 'files', 'versions', 'acquisition_attempts', 'claims', 'gaps',
                'code_artifacts', 'relations', 'provenance']
    counts = {x: c.execute('SELECT count(*) FROM ' + x).fetchone()[0] for x in required}
    assert counts['works'] == 31 and counts['acquisition_attempts'] == 704
    assert counts['code_artifacts'] == 4 and counts['versions'] == 54
    for r in c.execute('SELECT * FROM files'):
        p = tree / r['local_path']
        assert p.is_file() and p.stat().st_size == r['bytes'] and sha(p) == r['sha256'], r['local_path']
    assert not c.execute("SELECT * FROM files WHERE relative_path LIKE '%-journal' OR relative_path LIKE '%-wal' OR relative_path LIKE '%-shm'").fetchall()
    assert not c.execute('SELECT doi FROM works WHERE doi IS NOT NULL GROUP BY lower(doi) HAVING count(*)>1').fetchall()
    assert not c.execute('SELECT * FROM versions WHERE complete_fulltext=1 AND identity_status NOT IN (\'EXACT_VERSION_VERIFIED\',\'AUTHORITATIVE_PREPRINT_VERIFIED\',\'ACCEPTED_MANUSCRIPT_VERIFIED\',\'INSTITUTIONAL_COPY_VERIFIED\')').fetchall()
    verified_pdf = c.execute("SELECT count(*) FROM files WHERE page_count>0 AND identity_status IN ('EXACT_VERSION_VERIFIED','AUTHORITATIVE_PREPRINT_VERIFIED','ACCEPTED_MANUSCRIPT_VERIFIED','INSTITUTIONAL_COPY_VERIFIED')").fetchone()[0]
    assert verified_pdf == 16
    old = sqlite3.connect('file:' + str(tree / 'v1/02_database/research_sources.sqlite') + '?mode=ro', uri=True)
    legacy = {}
    for table in ['sources', 'source_files', 'code_snapshots', 'retrieval_attempts',
                  'documentation', 'report_gaps', 'cited_urls', 'source_search', 'files']:
        cols = [r[1] for r in old.execute('PRAGMA table_info(' + table + ')')]
        query = 'SELECT ' + ','.join(cols) + ' FROM ' + table + ' ORDER BY ' + cols[0]
        a = old.execute(query).fetchall()
        z = [tuple(x) for x in c.execute(query)]
        if table == 'files':
            z = [tuple(c.execute('SELECT ' + ','.join(cols) + ' FROM files WHERE relative_path=?', (r[0],)).fetchone()) for r in a]
        assert a == z, 'legacy ' + table
        legacy[table] = len(a)
    file_groups = collections.defaultdict(list)
    pdf_groups = collections.defaultdict(list)
    for p in sorted(tree.rglob('*')):
        if not p.is_file():
            continue
        assert 'transport-private' not in p.name and not p.name.endswith(('-journal', '-wal', '-shm'))
        value = sha(p)
        file_groups[value].append(str(p.relative_to(tree)))
        if p.suffix.lower() == '.pdf':
            with p.open('rb') as f:
                assert f.read(5) == b'%PDF-', str(p)
            pdf_groups[value].append(str(p.relative_to(tree)))
        if p.suffix in ['.pem', '.py', '.json', '.md', '.yml']:
            body = p.read_text(errors='replace')
            assert not re.search(r'^-----BEGIN (?:RSA )?PRIVATE KEY-----\r?$', body, re.M)
    assert len(pdf_groups) == 19 and all(len(x) == 1 for x in pdf_groups.values())
    summary = recovery['summary']
    assert summary['FULLTEXT_ACQUIRED_TOTAL'] == 17 and summary['NOT_ACQUIRED'] == 14
    assert summary['scientific_calculations'] == summary['native_authorization_consumption'] == 0
    assert summary['capture'] is False and summary['production'] == 'HOLD'
    assert summary['all_bound'] == 'OPEN' and summary['b_grid'] == 'NO_GO'
    assert not c.execute('SELECT * FROM claims WHERE scientific_validation_performed!=0').fetchall()
    assert not c.execute('SELECT * FROM code_artifacts WHERE downloaded_code_executed!=0').fetchall()
    c.close(); old.close()
    bib = v2 / 'BASS_CR_REFERENCES_20261001_v2.bib'
    with tempfile.TemporaryDirectory(prefix='bass-bib-') as folder:
        q = Path(folder)
        (q / 'check.aux').write_text('\\relax\n\\citation{*}\n\\bibstyle{plain}\n\\bibdata{' + str(bib.with_suffix('')) + '}\n')
        proc = subprocess.run(['bibtex', 'check.aux'], cwd=q, capture_output=True, text=True)
        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert len(re.findall(r'\\bibitem\{', (q / 'check.bbl').read_text())) == 31
    return dict(file_count=len(physical), root_manifest_hashes=len(expected),
                recovery_manifest_hashes=len(recovery['files']), sha256sums_checked=len(hashes),
                database_integrity='ok', foreign_key_check='PASS', database_table_counts=counts,
                database_catalog_all_paths_bytes_hashes='PASS', legacy_table_rows_preserved=legacy,
                physical_pdf_files=19, identity_verified_full_pdf_files=16,
                duplicate_pdf_hash_groups=[], duplicate_all_file_hash_groups=[
                    {'sha256':h, 'paths':ps} for h, ps in file_groups.items() if len(ps)>1],
                doi_version_consistency='PASS', bibtex_parser='BibTeX 0.99d', bibtex_entries=31,
                private_transport_key_absent=True, scientific_calculations=0,
                native_authorization_consumption=0, claim_ceilings='UNCHANGED',
                capture=False, production='HOLD', all_bound='OPEN', b_grid='NO_GO')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tree', type=Path, required=True)
    parser.add_argument('--zip', type=Path, required=True)
    parser.add_argument('--validation', type=Path, required=True)
    parser.add_argument('--original-v1-zip', type=Path, required=True)
    args = parser.parse_args()
    tree = args.tree.resolve()
    args.zip.parent.mkdir(parents=True, exist_ok=True)
    assert not args.zip.exists(), 'ZIP output must be new'
    validate(tree)
    with zipfile.ZipFile(args.zip, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in sorted(tree.rglob('*')):
            if p.is_file():
                z.write(p, str(p.relative_to(tree)))
    with zipfile.ZipFile(args.zip) as z, tempfile.TemporaryDirectory(prefix='bass-local-extract-') as folder:
        assert z.testzip() is None, 'ZIP CRC'
        assert len(z.namelist()) == len(set(z.namelist())), 'duplicate ZIP member'
        assert all(not p.startswith('/') and '..' not in Path(p).parts for p in z.namelist())
        z.extractall(folder)
        extracted = Path(folder)
        result = validate(extracted)
        with zipfile.ZipFile(args.original_v1_zip) as original:
            count = 0
            for name in original.namelist():
                if name.endswith('/'):
                    continue
                assert original.read(name) == (extracted / 'v1' / name).read_bytes(), name
                count += 1
            result['original_v1_members_byte_identical'] = count
        result['zip_crc'] = 'PASS'
        result['fresh_local_extraction'] = 'PASS'
    result['archive'] = dict(name=args.zip.name, bytes=args.zip.stat().st_size, sha256=sha(args.zip))
    result['validation_utc'] = dt.datetime.now(dt.timezone.utc).isoformat()
    result['remote_restore_performed'] = False
    args.validation.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'duplicate_all_file_hash_groups'}, ensure_ascii=False))
    print(json.dumps({'duplicate_all_file_hash_groups_count':len(result['duplicate_all_file_hash_groups'])}))


if __name__ == '__main__':
    main()
