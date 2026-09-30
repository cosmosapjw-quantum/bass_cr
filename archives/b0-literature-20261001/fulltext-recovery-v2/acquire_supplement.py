"""Selective follow-up after document identity/completeness review.

Only KuangLin1996, TemplatesGHEP, Errea1998, and Dollard1964. Never refetch
already acquired Netlib URLs or the three verified PDFs from the first pass.
"""
import concurrent.futures as cf
import hashlib
import json
from pathlib import Path
import re
import time
import urllib.parse
import zipfile
import acquire_missing_fulltexts as a


def main():
    a.ROOT = Path('payload_supplement')
    a.ROOT.mkdir(exist_ok=False)
    a.START = time.monotonic()
    spec = json.loads(Path('supplement_spec.json').read_text())
    known = set(spec['already_acquired_netlib_urls'])
    results = {'scope': ['KuangLin1996', 'TemplatesGHEP', 'Errea1998', 'Dollard1964'],
               'scientific_calculations': 0, 'native_authorization_consumption': 0}
    sid = 'KuangLin1996'
    url = 'https://www.phys.ksu.edu/personal/cdlin/papers/publication95-7.html'
    b, r = a.fetch(sid, url, 'publication_index.html', 'author_publication_index')
    if b:
        s = b.decode('latin-1')
        start = s.lower().find('comprehensive convergence')
        block = s[start:start+1800] if start >= 0 else ''
        links = a.Links(block).links
        found = [(u, t) for u, t in links if 'local' in t.lower()][:1]
        results['kuang_associated_link'] = found
        for u, t in found:
            q = urllib.parse.urljoin(r['final_url'], u)
            if q not in spec['kuang_previous_urls']:
                a.fetch(sid, q, 'author_associated_fulltext.pdf',
                        'author_index_explicit_fulltext', 'pdf')
            else:
                results['kuang_link_already_attempted'] = q
    base = 'https://www.netlib.org/utk/people/JackDongarra/etemplates/'
    sid = 'TemplatesGHEP'
    assets = set(spec['missing_nav_urls'])
    nodes = []
    for n in range(155, 190):
        u = base + 'node%d.html' % n
        if u in known:
            continue
        b, r = a.fetch(sid, u, 'chapter/node%d.html' % n,
                       'official_chapter_missing_subnode')
        if b:
            nodes.append(r)
            for u in a.Links(b.decode('utf-8', 'replace')).images:
                q = urllib.parse.urljoin(base, u)
                if q not in known and q.replace('http://www.netlib.org',
                                               'https://www.netlib.org') not in known:
                    assets.add(q)
    def asset(u):
        parsed = urllib.parse.urlsplit(u)
        if parsed.hostname != 'www.netlib.org':
            return {'status': 'REJECTED', 'url': u}
        u = u.replace('http://www.netlib.org', 'https://www.netlib.org')
        path = 'chapter/' + (('icons/' if '/utk/icons/' in parsed.path else '') +
                             Path(parsed.path).name)
        return a.fetch(sid, u, path, 'official_chapter_missing_asset')[1]
    with cf.ThreadPoolExecutor(max_workers=4) as pool:
        results['new_assets'] = list(pool.map(asset, sorted(assets)))
    results['new_nodes'] = nodes
    a.fetch('Errea1998', 'https://hal.science/hal-01566050/document',
            'hal_document.pdf', 'identified_hal_document', 'pdf')
    b, r = a.fetch('Dollard1964', 'https://inspirehep.net/api/literature/2735287',
                    'inspire.json', 'independent_disciplinary_repository', 'json')
    if b:
        d = json.loads(b).get('metadata', {})
        results['inspire_titles'] = d.get('titles')
        results['inspire_dois'] = d.get('dois')
        match = any(x.get('value', '').lower() == '10.1063/1.1704171'
                    for x in d.get('dois', []))
        if match:
            for i, doc in enumerate(d.get('documents', [])[:2]):
                if doc.get('url') and a.trusted(doc['url']):
                    a.fetch('Dollard1964', doc['url'], 'inspire_fulltext_%d.pdf'%i,
                            'doi_matched_repository_fulltext', 'pdf')
    results['attempts'] = a.ATTEMPTS
    a.save('ACQUISITION_SUPPLEMENT.json', json.dumps(results, indent=2).encode())
    manifest = [{'path': str(q.relative_to(a.ROOT)), 'bytes': q.stat().st_size,
                 'sha256': hashlib.sha256(q.read_bytes()).hexdigest()}
                for q in sorted(a.ROOT.rglob('*')) if q.is_file()]
    a.save('MANIFEST.json', json.dumps(manifest, indent=2).encode())
    with zipfile.ZipFile('recovery_payload.zip', 'x', zipfile.ZIP_DEFLATED) as z:
        for q in sorted(a.ROOT.rglob('*')):
            if q.is_file():
                z.write(q, str(q.relative_to(a.ROOT)))
    print(json.dumps({'supplement_targets': 4, 'attempts': len(a.ATTEMPTS),
                      'new_chapter_nodes': len(nodes), 'identity_verified_pdfs': 0,
                      'scientific_calculations': 0}))


if __name__ == '__main__':
    main()
