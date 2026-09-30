"""Bounded public-source acquisition for the authoritative 18 missing works.

No login, access-control workaround, solver, dependency installation, or
downloaded-code execution. A downloaded candidate is never identity-verified
by this collector; local document review must make that decision.
"""
import argparse
import concurrent.futures as cf
import datetime as dt
import difflib
import gzip
import hashlib
import html
from html.parser import HTMLParser
import io
import json
from pathlib import Path
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile

EXPECTED = {
    'Toshima1999', 'RungeMicha1996', 'Dollard1964', 'Enss1979',
    'Kato1976', 'Stewart2011', 'TemplatesGHEP', 'Stewart1972',
    'Mathias1997', 'BrayStelbovics1992PRL', 'BrayStelbovics1992PRA',
    'Antonio2024', 'Yafaev2000', 'KuangLin1996', 'KuangLin1997',
    'Errea1998', 'DickinsonMcCarroll1983', 'Kunikeev1999',
}
UA = 'BASS-CR-fulltext-recovery/2.0 (public personal research archive)'
ATTEMPTS = []
LOCK = threading.Lock()
ARXIV_LOCK = threading.Lock()
LAST_ARXIV = 0.0
START = 0.0
ROOT = None

DIRECT = {
    'BrayStelbovics1992PRA': [
        'https://researchportal.murdoch.edu.au/view/pdfCoverPage?download=true&filePid=13137046580007891&instCode=61MUN_INST'],
    'BrayStelbovics1992PRL': [
        'https://researchportal.murdoch.edu.au/view/pdfCoverPage?download=true&filePid=13136940910007891&instCode=61MUN_INST'],
    'Mathias1997': [
        'https://citeseerx.ist.psu.edu/document?doi=10.1.1.33.4963&repid=rep1&type=pdf'],
    'KuangLin1996': [
        'https://www.phys.ksu.edu/personal/cdlin/articles/cdl/j189.pdf',
        'https://www.phys.ksu.edu/personal/cdlin/articles/cdl/j184.pdf'],
    'KuangLin1997': [
        'https://www.phys.ksu.edu/personal/cdlin/articles/cdl/j190.pdf'],
}
LANDINGS = {
    'RungeMicha1996': ['https://people.clas.ufl.edu/Micha/publications/'],
    'Dollard1964': ['https://cir.nii.ac.jp/crid/1361418520433153024'],
    'Stewart2011': ['https://www.cs.umd.edu/~stewart/',
                    'https://www.umiacs.umd.edu/~stewart/'],
    'Stewart1972': ['https://www.cs.umd.edu/~stewart/'],
    'Enss1979': ['https://www.iram.rwth-aachen.de/~enss/'],
    'Errea1998': ['https://hal.science/hal-01566050',
                  'https://oskar-bordeaux.fr/handle/20.500.12278/119199'],
    'Kato1976': ['https://link.springer.com/book/10.1007/978-3-642-66282-9',
                 'https://cds.cern.ch/record/101545',
                 'https://cds.cern.ch/record/408827'],
    'Yafaev2000': ['https://link.springer.com/book/10.1007/BFb0105531',
                   'https://cds.cern.ch/record/1691405'],
    'Mathias1997': ['https://www.math.wm.edu/~mathias/',
                    'https://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.33.4963'],
    'BrayStelbovics1992PRA': [
        'https://researchportal.murdoch.edu.au/esploro/outputs/journalArticle/Convergent-close-coupling-calculations-of-electron-hydrogen-scattering/991005541214607891'],
    'BrayStelbovics1992PRL': [
        'https://researchportal.murdoch.edu.au/esploro/outputs/journalArticle/Explicit-demonstration-of-the-convergence-of/991005541211507891'],
}


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def normal(s):
    return re.sub(r'[^a-z0-9]+', '', html.unescape(s).lower())


def trusted(u):
    p = urllib.parse.urlsplit(u)
    h = p.hostname or ''
    if p.scheme not in ('http', 'https') or p.username or p.password:
        return False
    return h.endswith(('.edu', '.edu.au', '.ac.uk', '.ac.jp', '.edu.cn')) or h in {
        'arxiv.org', 'export.arxiv.org', 'api.openalex.org',
        'api.semanticscholar.org', 'api.crossref.org', 'api.hal.science',
        'hal.science', 'cds.cern.ch', 'inspirehep.net', 'www.osti.gov',
        'api.drum.lib.umd.edu', 'journals.aps.org', 'link.aps.org',
        'epubs.siam.org', 'pubs.aip.org', 'link.springer.com',
        'iopscience.iop.org', 'www.sciencedirect.com',
        'www.netlib.org', 'netlib.org', 'cir.nii.ac.jp',
        'www.iram.rwth-aachen.de', 'oskar-bordeaux.fr',
        'repositorio.uam.es', 'espace.curtin.edu.au',
        'ap-st01.ext.exlibrisgroup.com', 'drum.lib.umd.edu',
    }


def save(path, data):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('xb') as f:
        f.write(data)
    return {'path': str(path), 'bytes': len(data),
            'sha256': hashlib.sha256(data).hexdigest()}


def fetch(sid, url, label, route, kind='data', cap=40000000):
    r = {'source_id': sid, 'requested_url': url, 'route': route,
         'kind': kind, 'started_utc': utc(), 'label': label}
    b = None
    try:
        if not trusted(url):
            raise ValueError('not an allowlisted public scholarly route')
        if time.monotonic() - START > 1000:
            raise TimeoutError('bounded acquisition deadline')
        req = urllib.request.Request(url, headers={'User-Agent': UA})
        with urllib.request.urlopen(req, timeout=22) as res:
            r.update(http_status=res.status, final_url=res.url,
                     content_type=res.headers.get('Content-Type'))
            b = res.read(cap + 1)
        if len(b) > cap:
            raise ValueError('response exceeds size limit')
        if kind == 'json':
            json.loads(b)
        if kind == 'pdf' and not b.startswith(b'%PDF-'):
            r['failure_class'] = 'DOWNLOAD_RETURNED_HTML_NOT_PDF'
            raise ValueError('download did not begin with PDF signature')
        if kind == 'ps.gz' and not gzip.decompress(b).startswith(b'%!'):
            r['failure_class'] = 'CORRUPT_DOWNLOAD'
            raise ValueError('not a gzip-compressed PostScript document')
        r.update(save('literature/' + sid + '/' + label, b),
                 status='ACQUIRED', completed_utc=utc())
    except Exception as e:
        b = None
        if isinstance(e, urllib.error.HTTPError):
            r['http_status'] = e.code
        code = r.get('http_status')
        fc = ('RATE_LIMITED' if code == 429 else
              'AUTHENTICATION_REQUIRED' if code == 401 else
              'PUBLISHER_ACCESS_RESTRICTED' if code == 403 and route == 'publisher' else
              'PUBLIC_FULLTEXT_NOT_FOUND' if code == 404 else 'NETWORK_FAILURE')
        r.update(status='FAILED', error_type=type(e).__name__,
                 error=str(e)[:350], completed_utc=utc())
        r.setdefault('failure_class', fc)
    with LOCK:
        r['attempt_id_local'] = len(ATTEMPTS) + 1
        ATTEMPTS.append(r)
    return b, r


class Links(HTMLParser):
    def __init__(self, s):
        super().__init__()
        self.links, self.images, self.meta, self.anchor = [], [], [], None
        self.feed(s)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'a' and a.get('href'):
            self.anchor = [a['href'], '']
        if tag == 'img' and a.get('src'):
            self.images.append(a['src'])
        if tag == 'meta' and a.get('name', '').lower() == 'citation_pdf_url':
            self.meta.append(a.get('content', ''))

    def handle_data(self, s):
        if self.anchor is not None:
            self.anchor[1] += s

    def handle_endtag(self, tag):
        if tag == 'a' and self.anchor:
            self.links.append(tuple(self.anchor))
            self.anchor = None


def land(row, url, label):
    sid = row['source_id']
    b, r = fetch(sid, url, label + '.html', 'institutional_landing')
    candidates = []
    if b and b.startswith(b'%PDF-'):
        candidates.append(r)
    elif b:
        p = Links(b.decode('utf-8', 'replace'))
        author_index = any(x in url for x in ('people.clas.ufl.edu', '~mathias/'))
        u = p.meta + [u for u, t in p.links if
                      re.search(r'\.pdf(?:[?#]|$)|pdfCoverPage', u, re.I) and
                      (not author_index or difflib.SequenceMatcher(
                          None, normal(t), normal(row['title'])).ratio() >= .65)]
        for i, q in enumerate(dict.fromkeys(u)):
            if i >= 3:
                break
            q = urllib.parse.urljoin(r['final_url'], html.unescape(q))
            if trusted(q):
                c, rr = fetch(sid, q, label + '_linked_%d.pdf' % i,
                              'institutional_linked_fulltext', 'pdf')
                if c:
                    candidates.append(rr)
        if sid.startswith('Stewart'):
            contents = [u for u, t in p.links if 'contents' in t.lower()][:1]
            for u in contents:
                q = urllib.parse.urljoin(r['final_url'], u)
                c, rr = fetch(sid, q, label + '_contents.html', 'author_contents')
                if c:
                    pp = Links(c.decode('utf-8', 'replace'))
                    needle = 'oblique' if sid == 'Stewart2011' else 'sensitivity'
                    for j, (u, t) in enumerate([(u, t) for u, t in pp.links
                                               if needle in t.lower()][:2]):
                        q = urllib.parse.urljoin(rr['final_url'], u)
                        if trusted(q):
                            cc, rrr = fetch(sid, q, label + '_contents_%d.pdf' % j,
                                            'author_manuscript', 'pdf')
                            if cc:
                                candidates.append(rrr)
    return candidates


def repositories(row):
    sid, doi = row['source_id'], row['doi']
    candidates, records = [], []
    for i, u in enumerate(DIRECT.get(sid, [])):
        b, r = fetch(sid, u, 'identified_%02d.pdf' % i,
                     'identified_institutional_fulltext', 'pdf')
        if b:
            candidates.append(r)
    for i, u in enumerate(LANDINGS.get(sid, [])):
        candidates += land(row, u, 'landing_%02d' % i)
    if sid == 'Mathias1997':
        for i, u in enumerate([
            'https://www.math.wm.edu/~mathias/preprints/ps_zips/1996_002.ps.gz',
            'http://www.math.wm.edu/~mathias/preprints/ps_zips/1996_002.ps.gz']):
            b, r = fetch(sid, u, 'author_%02d.ps.gz' % i,
                         'author_original_postscript', 'ps.gz')
            if b:
                candidates.append(r)
                break
    # Exact DOI endpoints. Metadata-only responses are never full-text success.
    eps = [
        ('openalex', 'https://api.openalex.org/works/https://doi.org/' + doi),
        ('semantic_scholar', 'https://api.semanticscholar.org/graph/v1/paper/DOI:' +
         doi + '?fields=title,authors,year,externalIds,openAccessPdf,url'),
        ('hal', 'https://api.hal.science/search/?' + urllib.parse.urlencode({
            'q': 'doiId_s:"' + doi + '"', 'fl':
            'halId_s,title_s,doiId_s,fileMain_s,files_s,authFullName_s,producedDate_s,licence_s',
            'wt': 'json', 'rows': 5})),
    ]
    for name, u in eps:
        b, rr = fetch(sid, u, name + '.json', name + '_metadata', 'json')
        if not b:
            continue
        d = json.loads(b)
        links = []
        if name == 'openalex' and str(d.get('doi', '')).lower() == ('https://doi.org/' + doi).lower():
            for loc in [d.get('best_oa_location')] + d.get('locations', []):
                if not loc:
                    continue
                if loc.get('is_oa') and loc.get('pdf_url'):
                    links.append((loc['pdf_url'], loc.get('version')))
                elif loc.get('source') and loc['source'].get('type') == 'repository' and loc.get('landing_page_url'):
                    q = loc['landing_page_url']
                    if trusted(q) and q not in LANDINGS.get(sid, []):
                        candidates += land(row, q, name + '_landing_%d' % len(records))
                        records.append(q)
        if name == 'semantic_scholar':
            ext = d.get('externalIds') or {}
            if str(ext.get('DOI', '')).lower() == doi.lower():
                if (d.get('openAccessPdf') or {}).get('url'):
                    links.append((d['openAccessPdf']['url'], 'UNKNOWN'))
                if ext.get('ArXiv'):
                    records.append({'arxiv_id': ext['ArXiv']})
        if name == 'hal':
            for doc in d.get('response', {}).get('docs', []):
                identifiers = doc.get('doiId_s', [])
                if isinstance(identifiers, str):
                    identifiers = [identifiers]
                if doi.lower() not in [str(x).lower() for x in identifiers]:
                    continue
                if doc.get('fileMain_s'):
                    links.append((doc['fileMain_s'], 'HAL_DEPOSIT'))
        for j, (q, version) in enumerate(dict.fromkeys(links)):
            if j >= 3:
                break
            if trusted(q):
                c, rec = fetch(sid, q, name + '_fulltext_%d.pdf' % j,
                               name + '_linked_fulltext', 'pdf')
                rec['metadata_version_label'] = version
                if c:
                    candidates.append(rec)
    # Explicit publisher route, kept separate from all independent alternatives.
    if doi.startswith('10.1103/'):
        journal = 'prl' if 'PhysRevLett.' in doi else 'pra'
        u = 'https://journals.aps.org/' + journal + '/pdf/' + doi
    elif doi.startswith('10.1137/'):
        u = 'https://epubs.siam.org/doi/pdf/' + doi
    elif doi.startswith('10.1007/'):
        u = 'https://link.springer.com/content/pdf/' + doi + '.pdf'
    elif doi.startswith('10.1088/'):
        u = 'https://iopscience.iop.org/article/' + doi + '/pdf'
    elif sid == 'Dollard1964':
        u = 'https://pubs.aip.org/aip/jmp/article-pdf/5/6/729/19136571/729_1_online.pdf'
    else:
        pii = '0003491679902525' if sid == 'Enss1979' else 'S0168583X99000130'
        u = 'https://www.sciencedirect.com/science/article/pii/' + pii + '/pdfft'
    b, rec = fetch(sid, u, 'publisher.pdf', 'publisher', 'pdf')
    if b:
        candidates.append(rec)
    return {'source_id': sid, 'candidate_files': candidates,
            'metadata_discoveries': records, 'identity_status': 'REVIEW_REQUIRED'}


def arxiv(row):
    global LAST_ARXIV
    sid, title, doi = row['source_id'], row['title'], row['doi']
    term = re.sub(r'[^A-Za-z0-9 -]+', ' ', title)
    q = 'ti:"' + term + '"'
    url = 'https://export.arxiv.org/api/query?' + urllib.parse.urlencode({
        'search_query': q, 'start': 0, 'max_results': 5,
        'sortBy': 'lastUpdatedDate', 'sortOrder': 'descending'})
    with ARXIV_LOCK:
        delay = max(0.0, 3.1 - (time.monotonic() - LAST_ARXIV))
        if delay:
            time.sleep(delay)
        b, rr = fetch(sid, url, 'arxiv_title_query.xml', 'arxiv_title_search')
        LAST_ARXIV = time.monotonic()
    out = {'source_id': sid, 'query': q, 'entries': [], 'candidate_files': []}
    if b:
        try:
            ns = {'a': 'http://www.w3.org/2005/Atom', 'x': 'http://arxiv.org/schemas/atom'}
            tree = ET.fromstring(b)
            for e in tree.findall('a:entry', ns):
                tt = e.findtext('a:title', '', ns)
                dd = e.findtext('x:doi', '', ns)
                ident = e.findtext('a:id', '', ns).split('/abs/')[-1]
                ratio = difflib.SequenceMatcher(None, normal(tt), normal(title)).ratio()
                record = {'title': tt, 'doi': dd, 'arxiv': ident,
                          'updated': e.findtext('a:updated', '', ns),
                          'authors': [x.findtext('a:name', '', ns) for x in e.findall('a:author', ns)],
                          'title_similarity': ratio, 'selected': dd.lower() == doi.lower() or ratio >= .93}
                out['entries'].append(record)
                if record['selected'] and re.fullmatch(r'(?:[a-z-]+/)?\d+(?:\.\d+)?(?:v\d+)?', ident):
                    c, r = fetch(sid, 'https://arxiv.org/pdf/' + ident,
                                 'arxiv_' + ident.replace('/', '_') + '.pdf',
                                 'arxiv_latest_returned_version', 'pdf')
                    if c:
                        out['candidate_files'].append(r)
        except ET.ParseError:
            out['metadata_status'] = 'ARXIV_RESPONSE_NOT_ATOM'
    return out


def netlib_chapter():
    sid = 'TemplatesGHEP'
    base = 'https://www.netlib.org/utk/people/JackDongarra/etemplates/'
    b, r = fetch(sid, base + 'index.html', 'chapter/index.html', 'official_author_book_index')
    out = {'source_id': sid, 'format': 'OFFICIAL_CHAPTER_HTML', 'node_paths': [],
           'assets': [], 'complete': False, 'identity_status': 'REVIEW_REQUIRED'}
    if not b:
        return out
    links = Links(b.decode('utf-8', 'replace')).links
    target = [i for i, (u, t) in enumerate(links) if normal(t) == normal('Generalized Hermitian Eigenvalue Problems')]
    if not target:
        return out
    i = target[0]
    next_i = next((j for j in range(i + 1, len(links))
                   if normal(links[j][1]) == normal('Singular Value Decomposition')), None)
    if next_i is None:
        return out
    selected = links[i:next_i]
    nodes = list(dict.fromkeys(u for u, t in selected if re.fullmatch(r'node\d+\.html', u)))
    out['toc_selection'] = selected
    assets = set()
    for u in nodes:
        c, rr = fetch(sid, base + u, 'chapter/' + u, 'official_complete_chapter_node')
        if not c:
            continue
        out['node_paths'].append(rr)
        assets.update(Links(c.decode('utf-8', 'replace')).images)
    safe_assets = [u for u in sorted(assets) if not urllib.parse.urlsplit(u).netloc
                   and '..' not in Path(u).parts and not u.startswith('/')][:500]
    def asset(u):
        return fetch(sid, base + u, 'chapter/' + u, 'official_chapter_asset')[1]
    with cf.ThreadPoolExecutor(max_workers=4) as pool:
        out['assets'] = list(pool.map(asset, safe_assets))
    out['complete'] = (len(out['node_paths']) == len(nodes) and len(safe_assets) == len(assets)
                       and all(x['status'] == 'ACQUIRED' for x in out['assets']))
    out['expected_nodes'] = nodes
    out['expected_assets'] = len(assets)
    return out


def main():
    global ROOT, START
    p = argparse.ArgumentParser()
    p.add_argument('--targets', required=True)
    p.add_argument('--output', required=True)
    p.add_argument('--check-only', action='store_true')
    a = p.parse_args()
    rows = json.loads(Path(a.targets).read_text())
    assert len(rows) == 18 and {x['source_id'] for x in rows} == EXPECTED
    assert all(x['doi'] for x in rows)
    if a.check_only:
        print(json.dumps({'targets': 18, 'already_acquired_requested': 0,
                          'scientific_calculations': 0, 'native_authorization_consumption': 0}))
        return
    ROOT, START = Path(a.output), time.monotonic()
    ROOT.mkdir(exist_ok=False)
    with cf.ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(repositories, rows))
    arxiv_results = [arxiv(r) for r in rows]
    chapter = netlib_chapter()
    summary = {'targets': 18, 'results': results, 'arxiv_results': arxiv_results,
               'official_chapter': chapter, 'attempts': ATTEMPTS,
               'scientific_calculations': 0, 'downloaded_code_execution': 0,
               'native_authorization_consumption': 0, 'elapsed_seconds': time.monotonic() - START}
    save('ACQUISITION_RECOVERY.json', json.dumps(summary, ensure_ascii=False, indent=2).encode())
    manifest = [{'path': str(q.relative_to(ROOT)), 'bytes': q.stat().st_size,
                 'sha256': hashlib.sha256(q.read_bytes()).hexdigest()}
                for q in sorted(ROOT.rglob('*')) if q.is_file()]
    save('MANIFEST.json', json.dumps(manifest, indent=2).encode())
    with zipfile.ZipFile('recovery_payload.zip', 'x', zipfile.ZIP_DEFLATED) as z:
        for q in sorted(ROOT.rglob('*')):
            if q.is_file():
                z.write(q, str(q.relative_to(ROOT)))
    print(json.dumps({'targets': 18, 'candidate_pdfs': sum(x['kind'] == 'pdf' and x['status'] == 'ACQUIRED' for x in ATTEMPTS),
                      'attempts': len(ATTEMPTS), 'identity_verified_pdfs': 0,
                      'chapter_nodes': len(chapter['node_paths']), 'scientific_calculations': 0}))


if __name__ == '__main__':
    main()
